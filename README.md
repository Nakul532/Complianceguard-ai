# 🛡️ ComplianceGuard AI

**Real-Time AML Transaction Monitoring Dashboard**
Built by Nakul Shriman Karthikeyan · Fintech Analyst

[![Deploy on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 🎯 Overview

ComplianceGuard AI is an end-to-end Anti-Money Laundering (AML) transaction monitoring system designed for BSA Analysts at US banks and fintech companies. It analyzes 50,000+ synthetic transactions, applies 12 suspicious-pattern detectors, computes explainable risk scores, and auto-generates draft Suspicious Activity Reports (SARs).

**Live Demo:** _(deploy URL after Streamlit Cloud setup)_

---

## ✨ Features

- **12 AML Pattern Detectors**: Structuring, Smurfing, Rapid-Fire Transfers, Round-Amount Wires, OFAC Sanctions Hits, High-Risk Jurisdiction Flows, High-Risk MCC, Velocity Anomalies, Layering/Pass-Through, Dormancy Bursts, Large Cash (CTR), Round-Trip TBML
- **Explainable Risk Scoring (0-100)**: Five-factor decomposition — rule severity, multi-rule bonus, amount, customer history, sanctions status
- **Interactive Dashboard**: KPI hero, filterable flagged-transactions table, pattern analytics, case investigation
- **Auto-Generated SAR Drafts**: Pre-populated narrative ready for BSA Officer review per 31 CFR 1020.320
- **Regulatory References**: Every triggered rule maps to BSA, FinCEN, FATF, or OFAC guidance

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Data Processing | Pandas, NumPy |
| ML / Statistics | scikit-learn (extendable) |
| Visualization | Plotly |
| Synthetic Data | Faker |

---

## 🚀 Running Locally

```bash
# 1. Clone or download this folder
cd aml-monitor

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

Open your browser to `http://localhost:8501`

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this folder to a GitHub repo
2. Go to https://share.streamlit.io
3. Connect your GitHub
4. Select this repo → `app.py`
5. Deploy. Live URL in ~2 minutes.

---

## 📊 The 12 AML Rules Explained

| # | Rule | Regulatory Reference |
|---|---|---|
| 1 | Structuring (CTR Avoidance) | BSA 31 CFR 1010.314 |
| 2 | Rapid-Fire Transfers | FinCEN SAR Guidance Sec. 5.2 |
| 3 | Round-Amount Wires | BSA 31 CFR 1020.320 |
| 4 | OFAC Sanctions List Match | OFAC 31 CFR 501.603 |
| 5 | High-Risk Jurisdiction | FATF Recommendation 19 |
| 6 | High-Risk MCC | FFIEC BSA/AML Manual |
| 7 | Velocity Anomaly | FinCEN Advisory FIN-2014-A005 |
| 8 | Smurfing | BSA 31 CFR 1010.314 |
| 9 | Layering / Pass-Through | FATF Recommendation 10 |
| 10 | Dormancy Then Burst | FFIEC BSA/AML Manual |
| 11 | Large Transaction (CTR) | BSA 31 CFR 1010.311 |
| 12 | Round-Trip TBML | FinCEN Advisory FIN-2014-A005 |

---

## 🎯 Why This Matters

BSA Analysts at US banks process 100K+ transactions daily looking for suspicious patterns. The current state of the art is rule-based systems that:

1. Generate too many false positives → analyst fatigue
2. Lack explainability → SAR narratives are slow to draft
3. Don't surface multi-rule cases → real laundering schemes slip through

ComplianceGuard AI addresses all three by combining rules + explainable scoring + auto-narrative generation.

---

## 👤 About the Builder

**Nakul Shriman Karthikeyan**
Fintech Analyst | SQL + Payments + Risk + Compliance | IEEE Published

- M.S. Engineering Management, Northeastern University (May 2025, GPA 3.52)
- B.Tech Electronics & Telecommunication Engineering, NMIMS University
- IEEE 2024 Publication: ML Algorithms for Disease Prediction (5 models, 4,200+ patient dataset)

🔗 [LinkedIn](https://linkedin.com/in/shriman-nakul) · [Portfolio](https://nakul532.github.io)

---

## ⚖️ Disclaimer

All data in this project is synthetically generated. Customer names, transactions, and sanctions list entries are fictional and not representative of real persons or entities. This project is a demonstration of AML detection methodology, not a production compliance tool.
