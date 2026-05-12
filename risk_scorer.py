import pandas as pd
import numpy as np

def compute_risk_scores(transactions_df, flags_df, customers_df):
    if len(flags_df) == 0:
        flags_agg = pd.DataFrame(columns=['txn_id', 'rule_count', 'max_severity', 'sum_severity', 'rules_triggered'])
    else:
        flags_agg = flags_df.groupby('txn_id').agg(
            rule_count=('rule', 'count'),
            max_severity=('severity', 'max'),
            sum_severity=('severity', 'sum'),
            rules_triggered=('rule', lambda x: list(x)),
        ).reset_index()
    df = transactions_df.merge(flags_agg, on='txn_id', how='left')
    df['rule_count'] = df['rule_count'].fillna(0)
    df['max_severity'] = df['max_severity'].fillna(0)
    df['sum_severity'] = df['sum_severity'].fillna(0)
    df['rules_triggered'] = df['rules_triggered'].apply(lambda x: x if isinstance(x, list) else [])
    df = df.merge(customers_df[['customer_id', 'risk_tier', 'is_sanctioned']], on='customer_id', how='left')
    df['rule_score'] = (df['max_severity'] * 3).clip(0, 30)
    df['multi_rule_bonus'] = ((df['rule_count'] - 1).clip(lower=0) * 2).clip(0, 8)
    df['amount_score'] = ((np.log1p(df['amount']) - 5) * 1.5).clip(0, 8)
    df['customer_history_score'] = ((df['rule_count'] > 0) & (df['risk_tier'] == 'high')).astype(int) * 4
    df['sanctioned_score'] = ((df['rule_count'] > 0) & df['is_sanctioned'].fillna(False)).astype(int) * 15
    df['risk_score'] = (df['rule_score'] + df['multi_rule_bonus'] + df['amount_score'] + df['customer_history_score'] + df['sanctioned_score']).clip(0, 100)
    df['risk_tier_label'] = pd.cut(df['risk_score'], bins=[-1, 30, 60, 100], labels=['cleared', 'review', 'high-risk'])
    return df

def generate_sar_narrative(txn_row, related_txns):
    rules = txn_row.get('rules_triggered', [])
    narrative = f"SUSPICIOUS ACTIVITY REPORT - DRAFT\n\nSubject: {txn_row['customer_name']} ({txn_row['customer_id']})\nDate: {txn_row['timestamp']}\nAmount: ${txn_row['amount']:,.2f}\nRoute: {txn_row['sender_country']} -> {txn_row['receiver_country']}\n\nTriggered Rules:\n"
    for rule in rules:
        narrative += f"  - {rule}\n"
    narrative += f"\nRisk Score: {txn_row['risk_score']:.1f}/100\nFiled by: Nakul Shriman Karthikeyan, Fintech Analyst\n"
    return narrative
