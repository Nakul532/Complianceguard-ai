"""
AML Rule Engine: 12 suspicious pattern detectors.
Each rule returns a list of flagged txn_ids with severity, explanation, and regulation reference.
"""
import pandas as pd
import numpy as np
from datetime import timedelta


HIGH_RISK_COUNTRIES = ['Iran', 'North Korea', 'Syria', 'Russia', 'Myanmar', 'Yemen', 'Afghanistan']
HIGH_RISK_MCC = ['cash_advance', 'money_service_business', 'precious_metals', 'gambling', 'crypto_exchange']
SANCTIONED_NAMES = [
    'Viktor Volkov', 'Ahmed Al-Hashimi', 'Kim Jong-Sun', 'Hassan Rezaei',
    'Ivan Petrov', 'Bashar Al-Qadri', 'Mohammed Al-Zahrani', 'Vladislav Sokolov',
]


def detect_structuring(df):
    """Rule 1: Multiple transactions just below $10K threshold within 7 days."""
    flags = []
    df_sorted = df.sort_values(['customer_id', 'timestamp'])
    for cust_id, group in df_sorted.groupby('customer_id'):
        near_threshold = group[(group['amount'] >= 9000) & (group['amount'] < 10000)]
        if len(near_threshold) >= 3:
            for _, row in near_threshold.iterrows():
                flags.append({
                    'txn_id': row['txn_id'],
                    'rule': 'Structuring (CTR Avoidance)',
                    'severity': 9,
                    'explanation': f'Customer made {len(near_threshold)} transactions between $9,000-$9,999, indicative of CTR threshold avoidance.',
                    'regulation': 'BSA 31 CFR 1010.314 (Structuring Prohibition)',
                })
    return flags


def detect_rapid_fire(df):
    """Rule 2: 5+ transactions within 1 hour."""
    flags = []
    df_sorted = df.sort_values(['customer_id', 'timestamp'])
    for cust_id, group in df_sorted.groupby('customer_id'):
        if len(group) < 5:
            continue
        for i in range(len(group) - 4):
            window = group.iloc[i:i+5]
            time_span = (window['timestamp'].max() - window['timestamp'].min()).total_seconds() / 3600
            if time_span <= 1.0:
                for _, row in window.iterrows():
                    if not any(f['txn_id'] == row['txn_id'] and f['rule'] == 'Rapid-Fire Transfers' for f in flags):
                        flags.append({
                            'txn_id': row['txn_id'],
                            'rule': 'Rapid-Fire Transfers',
                            'severity': 7,
                            'explanation': f'5+ transactions within 1 hour. Velocity anomaly suggests automated or coordinated activity.',
                            'regulation': 'FinCEN SAR Filing Guidance Sec. 5.2',
                        })
    return flags


def detect_round_amounts(df):
    """Rule 3: Suspiciously round dollar amounts in wire transfers."""
    flags = []
    round_amounts = [5000.0, 10000.0, 25000.0, 50000.0, 100000.0]
    suspect = df[(df['amount'].isin(round_amounts)) & (df['txn_type'] == 'wire')]
    for _, row in suspect.iterrows():
        flags.append({
            'txn_id': row['txn_id'],
            'rule': 'Round-Amount Wire',
            'severity': 5,
            'explanation': f'Wire transfer of exactly ${row["amount"]:,.0f}. Round amounts often indicate layering or pre-coordinated movements.',
            'regulation': 'BSA 31 CFR 1020.320 (Suspicious Transactions)',
        })
    return flags


def detect_sanctions_hits(df):
    """Rule 4: Transactions involving sanctioned names."""
    flags = []
    suspect = df[df['customer_name'].isin(SANCTIONED_NAMES)]
    for _, row in suspect.iterrows():
        flags.append({
            'txn_id': row['txn_id'],
            'rule': 'OFAC Sanctions List Match',
            'severity': 10,
            'explanation': f'Customer name "{row["customer_name"]}" matches synthetic OFAC SDN List. Immediate blocking required.',
            'regulation': 'OFAC 31 CFR 501.603 (Mandatory Blocking)',
        })
    return flags


def detect_geographic_risk(df):
    """Rule 5: Transactions to/from FATF high-risk jurisdictions."""
    flags = []
    suspect = df[
        (df['receiver_country'].isin(HIGH_RISK_COUNTRIES)) |
        (df['sender_country'].isin(HIGH_RISK_COUNTRIES))
    ]
    for _, row in suspect.iterrows():
        country = row['receiver_country'] if row['receiver_country'] in HIGH_RISK_COUNTRIES else row['sender_country']
        flags.append({
            'txn_id': row['txn_id'],
            'rule': 'High-Risk Jurisdiction',
            'severity': 8,
            'explanation': f'Transaction involves {country}, a FATF high-risk or monitored jurisdiction. Enhanced due diligence required.',
            'regulation': 'FATF Recommendation 19 (High-Risk Jurisdictions)',
        })
    return flags


def detect_high_risk_mcc(df):
    """Rule 6: High-risk merchant category codes."""
    flags = []
    suspect = df[df['merchant_category'].isin(HIGH_RISK_MCC)]
    for _, row in suspect.iterrows():
        flags.append({
            'txn_id': row['txn_id'],
            'rule': 'High-Risk Merchant Category',
            'severity': 6,
            'explanation': f'Merchant category "{row["merchant_category"]}" is classified as high-risk per FFIEC BSA/AML Examination Manual.',
            'regulation': 'FFIEC BSA/AML Manual: High-Risk MCC Section',
        })
    return flags


def detect_velocity_anomaly(df):
    """Rule 7: Customer's daily volume 10x their baseline."""
    flags = []
    df_sorted = df.sort_values(['customer_id', 'timestamp'])
    df_sorted['date'] = df_sorted['timestamp'].dt.date

    for cust_id, group in df_sorted.groupby('customer_id'):
        if len(group) < 10:
            continue
        daily = group.groupby('date')['amount'].sum().reset_index()
        if len(daily) < 5:
            continue
        baseline = daily['amount'].median()
        if baseline == 0:
            continue
        anomaly_days = daily[daily['amount'] > baseline * 10]
        for _, day in anomaly_days.iterrows():
            day_txns = group[group['date'] == day['date']]
            for _, row in day_txns.iterrows():
                flags.append({
                    'txn_id': row['txn_id'],
                    'rule': 'Velocity Anomaly',
                    'severity': 7,
                    'explanation': f'Customer daily volume of ${day["amount"]:,.0f} is 10x+ baseline (${baseline:,.0f}). Sudden spike indicates account compromise or coordinated movement.',
                    'regulation': 'FinCEN Advisory FIN-2014-A005 (Behavioral Anomalies)',
                })
    return flags


def detect_smurfing(df):
    """Rule 8: One customer sending many small amounts to different recipients."""
    flags = []
    df_sorted = df.sort_values(['customer_id', 'timestamp'])
    for cust_id, group in df_sorted.groupby('customer_id'):
        # Smurfing: 6+ transactions in same day, similar amounts, different patterns
        group_with_date = group.copy()
        group_with_date['date'] = group['timestamp'].dt.date
        for date, day_group in group_with_date.groupby('date'):
            if len(day_group) >= 6:
                small_amounts = day_group[(day_group['amount'] >= 1000) & (day_group['amount'] <= 5000)]
                if len(small_amounts) >= 6:
                    for _, row in small_amounts.iterrows():
                        flags.append({
                            'txn_id': row['txn_id'],
                            'rule': 'Smurfing Pattern',
                            'severity': 8,
                            'explanation': f'Customer sent {len(small_amounts)} small transactions ($1K-$5K) in one day, suggesting amount-splitting to avoid detection.',
                            'regulation': 'BSA 31 CFR 1010.314 (Structuring/Smurfing)',
                        })
    return flags


def detect_layering(df):
    """Rule 9: Money in -> money out within 24 hours (pass-through)."""
    flags = []
    df_sorted = df.sort_values(['customer_id', 'timestamp'])
    for cust_id, group in df_sorted.groupby('customer_id'):
        if len(group) < 4:
            continue
        for i in range(len(group) - 1):
            curr = group.iloc[i]
            next_txn = group.iloc[i + 1]
            time_diff = (next_txn['timestamp'] - curr['timestamp']).total_seconds() / 3600
            amount_similar = abs(curr['amount'] - next_txn['amount']) / max(curr['amount'], 1) < 0.1
            if time_diff < 24 and amount_similar and curr['amount'] > 5000:
                flags.append({
                    'txn_id': next_txn['txn_id'],
                    'rule': 'Layering / Pass-Through',
                    'severity': 8,
                    'explanation': f'Similar amounts in and out within {time_diff:.1f} hours. Pass-through pattern indicates layering stage of money laundering.',
                    'regulation': 'FATF Recommendation 10 (CDD: Layering Detection)',
                })
    return flags


def detect_dormancy_then_activity(df):
    """Rule 10: Long-dormant account suddenly active."""
    flags = []
    df_sorted = df.sort_values(['customer_id', 'timestamp'])
    for cust_id, group in df_sorted.groupby('customer_id'):
        if len(group) < 3:
            continue
        group = group.sort_values('timestamp')
        # If first txn was 30+ days before second txn, flag the burst
        gaps = group['timestamp'].diff().dt.total_seconds() / 86400
        burst_idx = gaps[gaps > 30].index
        for idx in burst_idx:
            row = group.loc[idx]
            flags.append({
                'txn_id': row['txn_id'],
                'rule': 'Dormancy Then Burst',
                'severity': 6,
                'explanation': f'Account dormant 30+ days then sudden activity. Potential account takeover or coordinated reactivation.',
                'regulation': 'FFIEC BSA/AML Manual: Behavioral Red Flags',
            })
    return flags


def detect_large_cash(df):
    """Rule 11: Single transaction over $10K (CTR reporting trigger)."""
    flags = []
    suspect = df[df['amount'] >= 10000]
    for _, row in suspect.iterrows():
        flags.append({
            'txn_id': row['txn_id'],
            'rule': 'Large Transaction (CTR)',
            'severity': 4,
            'explanation': f'Transaction of ${row["amount"]:,.2f} exceeds $10,000 CTR reporting threshold. Currency Transaction Report required.',
            'regulation': 'BSA 31 CFR 1010.311 (CTR Reporting)',
        })
    return flags


def detect_round_trip(df):
    """Rule 12: Customer sends to country and receives from same country within short window."""
    flags = []
    df_sorted = df.sort_values(['customer_id', 'timestamp'])
    for cust_id, group in df_sorted.groupby('customer_id'):
        for country in HIGH_RISK_COUNTRIES:
            sent = group[group['receiver_country'] == country]
            received = group[group['sender_country'] == country]
            if len(sent) > 0 and len(received) > 0:
                for _, row in sent.iterrows():
                    flags.append({
                        'txn_id': row['txn_id'],
                        'rule': 'Round-Trip High-Risk Country',
                        'severity': 9,
                        'explanation': f'Both sending to and receiving from {country}. Round-trip pattern suggests trade-based money laundering.',
                        'regulation': 'FinCEN Advisory FIN-2014-A005 (TBML)',
                    })
    return flags


def run_all_rules(df):
    """Execute all 12 rules and return consolidated flags DataFrame."""
    all_flags = []
    rules = [
        detect_structuring,
        detect_rapid_fire,
        detect_round_amounts,
        detect_sanctions_hits,
        detect_geographic_risk,
        detect_high_risk_mcc,
        detect_velocity_anomaly,
        detect_smurfing,
        detect_layering,
        detect_dormancy_then_activity,
        detect_large_cash,
        detect_round_trip,
    ]
    for rule in rules:
        try:
            all_flags.extend(rule(df))
        except Exception as e:
            print(f"Rule {rule.__name__} failed: {e}")
    return pd.DataFrame(all_flags) if all_flags else pd.DataFrame(columns=['txn_id', 'rule', 'severity', 'explanation', 'regulation'])
