# Portfolio Case Study: EliseAI Automation Return on Investment (ROI) & Unit Economics Platform

## 1. Executive Summary

As EliseAI continues its hyper-growth trajectory, expanding both its Housing and Healthcare verticals, measuring the financial impact of our AI automation becomes mission-critical. This project outlines an analytical platform designed to provide the Finance team—and executive leadership—with clear, defensible data on client ROI, unit economics, and cohort scaling.

**The core problem solved:** Turning raw, high-volume workflow interactions (AI handling maintenance requests, leasing inquiries, healthcare scheduling) into direct financial metrics (Cost Savings, Fallback Costs, CAC Payback). 

---

## 2. Business Context & Strategic Need

EliseAI's valuation and growth (e.g., recent Series E) hinge on demonstrating high *efficiency (automation rates)* and *value delivery (customer cost savings)*. For the Finance team, having an analytical layer that can accurately quantify these metrics enables:
- **Pricing Strategy Optimization:** Aligning contract pricing with actual value delivered to enterprise clients.
- **Resource Allocation:** Understanding if the Healthcare vertical (higher margin, lower volume) needs more engineering focus compared to Housing (high volume, scaled automation).
- **Executive & Board Reporting:** Moving beyond generic SaaS metrics into deep ROI statements that fuel Series F readiness.

---

## 3. Data Architecture & Governance

The foundation of this reporting stack requires strict data modeling. Rather than writing ad-hoc queries, I designed a scalable SQLite schema simulation:

### Core Tables
1. **`clients`**: Tracks the client lifecycle, ARR, implementation cost (CAC), and vertical affiliation.
2. **`workflow_events`**: The granular, event-level telemetry of every AI interaction, tracking if it was fully automated or handed off to a human, and attributing a specific dollar value to that action.
3. **`metrics_daily`**: A pre-computed aggregation layer specifically designed to support fast dashboard rendering without re-querying billions of rows of event data.

### Synthetic Data Generation
To demonstrate this capability securely, I built a Python-based synthetic data generator (`generate_data.py`). It simulates 24 months of operational history across 100 enterprise clients, accurately capturing the nuanced differences between Real Estate (high volume, established AI success) and Healthcare (emerging complexity, higher implementation cost).

---

## 4. Modeling & The "Hex-Native" Dashboard Experience

Using Python (pandas) and Streamlit, I built an interactive analytical application (`dashboard.py`) that operates similarly to a Hex or Sigma workbook. The modeling layer (`models.py`) handles complex SQL joins to calculate:

- **Cohort CAC Payback Velocity:** How quickly we recoup the initial setup cost of a customer through their automation savings and monthly platform fees.
- **Vertical Profitability:** Contrasting the high-volume nature of housing against the high-stakes, higher-value nature of healthcare administration.
- **Forecasting Sensitivity Model:** An interactive tool allowing Finance leadership to answer: *"If our engineering team improves the AI handle rate by 5% next quarter, what is the downstream impact on customer ROI?"*

---

## 5. Potential Next Steps

If deployed within EliseAI's actual workflow:
1. **dbt Integration:** The SQL models defined here would be orchestrated via dbt, ensuring automated testing (e.g., ensuring `automation_savings` is never negative) and version control.
2. **Real-time Streaming:** Moving from daily batched metrics to real-time event ingestion (e.g., Kafka -> Snowflake) for immediate workflow monitoring.
3. **Predictive Churn Modeling:** Using the drop in automation rate as an early warning indicator for client churn risk.
