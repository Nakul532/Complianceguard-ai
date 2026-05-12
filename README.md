# 🛡️ ComplianceGuard AI

**Real-Time AML Transaction Monitoring Dashboard**
Built by Nakul Shriman Karthikeyan · Fintech Analyst

### 🌐 [**→ LIVE DEMO**](https://complianceguard-ai-7cylmhunfwt49pjzyfqp5h.streamlit.app)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://complianceguard-ai-7cylmhunfwt49pjzyfqp5h.streamlit.app)

---

## 🎯 Overview

ComplianceGuard AI is an end-to-end Anti-Money Laundering (AML) transaction monitoring system designed for BSA Analysts at US banks and fintech companies. It analyzes 49,937 synthetic transactions, applies 12 suspicious-pattern detectors, computes explainable risk scores, and auto-generates draft Suspicious Activity Reports (SARs).

**Try it live:** https://complianceguard-ai-7cylmhunfwt49pjzyfqp5h.streamlit.app

---

## 📊 What It Detects

| Metric | Value |
|---|---|
| Transactions analyzed | 49,937 |
| Customers monitored | 5,000 |
| AML rules applied | 12 |
| Flagged transactions | 6,952 (13.92%) |
| Total at risk | $14.98M |
| High-risk SAR cases | 26 |

## ✨ Features

- **12 AML Pattern Detectors**: Structuring, Smurfing, Rapid-Fire Transfers, Round-Amount Wires, OFAC Sanctions Hits, High-Risk Jurisdiction Flows, High-Risk MCC, Velocity Anomalies, Layering/Pass-Through, Dormancy Bursts, Large Cash (CTR), Round-Trip TBML
- **Explainable Risk Scoring (0-100)**: Five-factor decomposition with regulatory citations
- **Interactive Dashboard**: Transaction monitoring, pattern analytics, case investigation
- **Auto-Generated SAR Drafts**: Pre-populated narratives ready for BSA Officer review per 31 CFR 1020.320
- **Regulatory Mapping**: Every rule cites BSA, FinCEN, FATF, or OFAC guidance

## 🛠️ Tech Stack

Python · Streamlit · Pandas · NumPy · Plotly · scikit-learn · Faker

## 🚀 Run Locally

\`\`\`bash
git clone https://github.com/Nakul532/Complianceguard-ai.git
cd Complianceguard-ai
pip install -r requirements.txt
streamlit run app.py
\`\`\`

## 👤 About the Builder

**Nakul Shriman Karthikeyan**
M.S. Engineering Management, Northeastern University · Fintech Analyst · IEEE Published

🔗 [LinkedIn](https://linkedin.com/in/shriman-nakul) · [Portfolio](https://nakul532.github.io)

## ⚖️ Disclaimer

All data synthetically generated. Customer names, transactions, and sanctions list entries are fictional and not representative of real persons or entities.
