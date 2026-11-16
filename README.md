# 🛡️ ComplianceGuard AI

> **This project now lives on in [SafeSpend](https://safespend-nakul.vercel.app).** Code: [Nakul532/safespend](https://github.com/Nakul532/safespend).
> ComplianceGuard's AML rule engine was rebuilt inside SafeSpend to monitor payments made by AI agents.
> - The rules (structuring, velocity, rapid-fire, round amounts, dormancy, fan-in) run alongside new agent-specific ones (look-alike merchants, new-merchant bursts, team structuring), and an AI investigator drafts case notes whose every cited transaction is checked by code.
> - The rules are measured on IBM's public synthetic AML benchmark (HI-Small) at fixed daily alert budgets, next to a simple amount-threshold baseline.
> - Play the AML analyst yourself in **Analyst shift**: three minutes, 15 of 60 alerts.
>
> The figures below (49,937 transactions, $14.98M flagged, 6,948 → 26 cases) come from this project's own generated data, not real bank data. This repository is kept as the original prototype and is no longer maintained.

---


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
