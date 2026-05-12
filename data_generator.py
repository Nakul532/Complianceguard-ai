"""
Synthetic transaction data generator for AML monitoring.
Generates realistic transactions with injected suspicious patterns.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# High-risk countries (FATF, OFAC sanctioned + monitoring)
HIGH_RISK_COUNTRIES = ['Iran', 'North Korea', 'Syria', 'Russia', 'Myanmar', 'Yemen', 'Afghanistan']
NORMAL_COUNTRIES = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Japan', 'India', 'Australia',
                    'Singapore', 'UAE', 'Netherlands', 'Brazil', 'Mexico', 'Spain', 'Italy']

# Suspicious OFAC-style names (synthetic)
SANCTIONED_NAMES = [
    'Viktor Volkov', 'Ahmed Al-Hashimi', 'Kim Jong-Sun', 'Hassan Rezaei',
    'Ivan Petrov', 'Bashar Al-Qadri', 'Mohammed Al-Zahrani', 'Vladislav Sokolov',
]

TXN_TYPES = ['wire', 'ACH', 'zelle', 'check', 'card']
MCC_NORMAL = ['retail', 'restaurant', 'grocery', 'gas', 'utilities', 'subscription']
MCC_HIGH_RISK = ['cash_advance', 'money_service_business', 'precious_metals', 'gambling', 'crypto_exchange']


def generate_customer_pool(n_customers=5000):
    """Generate customer pool with risk profiles."""
    customers = []
    for i in range(n_customers):
        is_sanctioned = i < 50  # First 50 are on sanctions list
        is_high_risk = i < 500   # First 500 are high-risk
        customers.append({
            'customer_id': f'CUST{i:06d}',
            'customer_name': random.choice(SANCTIONED_NAMES) if is_sanctioned else fake.name(),
            'risk_tier': 'high' if is_high_risk else 'normal',
            'is_sanctioned': is_sanctioned,
            'home_country': random.choice(HIGH_RISK_COUNTRIES if is_high_risk else NORMAL_COUNTRIES),
            'account_open_date': fake.date_between(start_date='-5y', end_date='-30d'),
        })
    return pd.DataFrame(customers)


def generate_normal_transaction(customer, base_time):
    """Generate a normal-looking transaction."""
    return {
        'timestamp': base_time + timedelta(minutes=random.randint(0, 1440)),
        'customer_id': customer['customer_id'],
        'customer_name': customer['customer_name'],
        'amount': round(np.random.lognormal(mean=4.5, sigma=1.2), 2),
        'sender_country': customer['home_country'],
        'receiver_country': random.choice(NORMAL_COUNTRIES),
        'txn_type': random.choice(TXN_TYPES),
        'merchant_category': random.choice(MCC_NORMAL),
        'injected_pattern': None,
    }


def inject_structuring(customer, base_time):
    """Multiple transactions just below $10K threshold."""
    txns = []
    n = random.randint(3, 6)
    for i in range(n):
        txns.append({
            'timestamp': base_time + timedelta(hours=i*2),
            'customer_id': customer['customer_id'],
            'customer_name': customer['customer_name'],
            'amount': round(random.uniform(9000, 9999), 2),
            'sender_country': customer['home_country'],
            'receiver_country': random.choice(NORMAL_COUNTRIES),
            'txn_type': 'wire',
            'merchant_category': random.choice(MCC_NORMAL),
            'injected_pattern': 'structuring',
        })
    return txns


def inject_rapid_fire(customer, base_time):
    """5+ transactions in 1 hour."""
    txns = []
    n = random.randint(5, 10)
    for i in range(n):
        txns.append({
            'timestamp': base_time + timedelta(minutes=i*8),
            'customer_id': customer['customer_id'],
            'customer_name': customer['customer_name'],
            'amount': round(random.uniform(500, 3000), 2),
            'sender_country': customer['home_country'],
            'receiver_country': random.choice(NORMAL_COUNTRIES),
            'txn_type': random.choice(['zelle', 'ACH']),
            'merchant_category': random.choice(MCC_NORMAL),
            'injected_pattern': 'rapid_fire',
        })
    return txns


def inject_round_amount(customer, base_time):
    """Round dollar amounts."""
    return [{
        'timestamp': base_time,
        'customer_id': customer['customer_id'],
        'customer_name': customer['customer_name'],
        'amount': random.choice([5000.0, 10000.0, 25000.0, 50000.0, 100000.0]),
        'sender_country': customer['home_country'],
        'receiver_country': random.choice(NORMAL_COUNTRIES),
        'txn_type': 'wire',
        'merchant_category': random.choice(MCC_NORMAL),
        'injected_pattern': 'round_amount',
    }]


def inject_sanctions_hit(customer, base_time):
    """Transaction involving sanctioned country."""
    return [{
        'timestamp': base_time,
        'customer_id': customer['customer_id'],
        'customer_name': customer['customer_name'],
        'amount': round(random.uniform(5000, 75000), 2),
        'sender_country': customer['home_country'],
        'receiver_country': random.choice(HIGH_RISK_COUNTRIES),
        'txn_type': 'wire',
        'merchant_category': random.choice(MCC_HIGH_RISK),
        'injected_pattern': 'sanctions_geo',
    }]


def inject_velocity_anomaly(customer, base_time):
    """Sudden large volume from previously dormant account."""
    txns = []
    for i in range(random.randint(8, 15)):
        txns.append({
            'timestamp': base_time + timedelta(hours=i),
            'customer_id': customer['customer_id'],
            'customer_name': customer['customer_name'],
            'amount': round(random.uniform(8000, 25000), 2),
            'sender_country': customer['home_country'],
            'receiver_country': random.choice(NORMAL_COUNTRIES + HIGH_RISK_COUNTRIES),
            'txn_type': random.choice(TXN_TYPES),
            'merchant_category': random.choice(MCC_NORMAL + MCC_HIGH_RISK),
            'injected_pattern': 'velocity_anomaly',
        })
    return txns


def inject_high_risk_mcc(customer, base_time):
    """Cash advance / crypto / gambling spike."""
    return [{
        'timestamp': base_time,
        'customer_id': customer['customer_id'],
        'customer_name': customer['customer_name'],
        'amount': round(random.uniform(2000, 30000), 2),
        'sender_country': customer['home_country'],
        'receiver_country': random.choice(NORMAL_COUNTRIES),
        'txn_type': random.choice(['wire', 'card']),
        'merchant_category': random.choice(MCC_HIGH_RISK),
        'injected_pattern': 'high_risk_mcc',
    }]


def inject_smurfing(customer, base_time):
    """Large amount split across many accounts (one customer sends to many)."""
    txns = []
    n = random.randint(6, 12)
    for i in range(n):
        txns.append({
            'timestamp': base_time + timedelta(minutes=i*15),
            'customer_id': customer['customer_id'],
            'customer_name': customer['customer_name'],
            'amount': round(random.uniform(1500, 4500), 2),
            'sender_country': customer['home_country'],
            'receiver_country': random.choice(NORMAL_COUNTRIES),
            'txn_type': 'zelle',
            'merchant_category': random.choice(MCC_NORMAL),
            'injected_pattern': 'smurfing',
        })
    return txns


def generate_transactions(n_total=100000, fraud_rate=0.02):
    """Generate transaction dataset with injected AML patterns."""
    customers = generate_customer_pool(5000)

    transactions = []
    base_date = datetime(2026, 4, 1)

    # Normal transactions
    n_normal = int(n_total * (1 - fraud_rate))
    for _ in range(n_normal):
        customer = customers.sample(1).iloc[0]
        base_time = base_date + timedelta(days=random.randint(0, 35))
        transactions.append(generate_normal_transaction(customer, base_time))

    # Inject suspicious patterns
    pattern_funcs = [
        inject_structuring,
        inject_rapid_fire,
        inject_round_amount,
        inject_sanctions_hit,
        inject_velocity_anomaly,
        inject_high_risk_mcc,
        inject_smurfing,
    ]

    n_suspicious_events = int((n_total * fraud_rate) / 5)  # average 5 txns per event
    for _ in range(n_suspicious_events):
        # Pick a customer with bias toward high-risk
        if random.random() < 0.4:
            customer = customers[customers['risk_tier'] == 'high'].sample(1).iloc[0]
        else:
            customer = customers.sample(1).iloc[0]
        base_time = base_date + timedelta(days=random.randint(0, 35))
        pattern_func = random.choice(pattern_funcs)
        transactions.extend(pattern_func(customer, base_time))

    df = pd.DataFrame(transactions)
    df['txn_id'] = [f'TXN{i:08d}' for i in range(len(df))]
    df = df[['txn_id', 'timestamp', 'customer_id', 'customer_name', 'amount',
             'sender_country', 'receiver_country', 'txn_type', 'merchant_category',
             'injected_pattern']]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df, customers


if __name__ == '__main__':
    print("Generating 100K transactions...")
    df, customers = generate_transactions(100000, fraud_rate=0.02)
    print(f"Generated {len(df)} transactions across {customers['customer_id'].nunique()} customers")
    print(f"Suspicious patterns injected: {(df['injected_pattern'].notna()).sum()}")
    df.to_csv('transactions.csv', index=False)
    customers.to_csv('customers.csv', index=False)
    print("Saved to transactions.csv and customers.csv")
