# BoardPrep AI: Governed Finance Text-to-SQL Copilot
*A Data & Strategy Portfolio Project for Enterprise SaaS Operations*

---

## Executive Summary
Most finance teams spend significant cycles manually translating business questions into SQL, creating bottlenecks and metric inconsistency across departments. 

For a fast-scaling AI platform—operating across housing and healthcare verticals with immense board-facing pressure—answering operational questions quickly and accurately is a competitive advantage.

**BoardPrep AI** is a finance-safe Text-to-SQL assistant built on curated datasets, governed metric definitions, and semantic query guardrails. It demonstrates how a Finance Data Analyst can build automated, trustworthy reporting workflows that scale.

**Core Impact Statement:**
> *Built a governed Finance Text-to-SQL copilot translating executive questions into trusted SQL and reusable reporting workflows, reducing ad hoc analysis time while preserving metric consistency across housing and healthcare.*

---

## The Problem
"Chat with your database" applications often fail in finance environments because they hallucinate metric definitions (e.g., calculating ARR inconsistently across different prompts, or failing to understand the difference between 'Healthcare' and 'Housing' vertical logic). 

When a VP of Finance asks a question, the data *must* be correctly joined, filtered, and aggregated according to canonical accounting definitions.

## The Solution: A Governed Semantic Layer
Instead of pointing an LLM at a raw event log, I built a rigid dimensional model acting as a semantic bridge. 

### 1. The Finance Data Architecture
I engineered a highly structured SQLite backend mimicking a production Snowflake/dbt environment:
- **`dim_customer`**: Governs cohort acquisition months and vertical segmentation.
- **`dim_date`**: Forces explicit time-series aggregation.
- **`fct_revenue`**: The single source of truth for MRR, Expansion, and Contraction.
- **`fct_support_cost`**: A detailed granular log of AI interaction attempts and human escalation costs (a crucial operating metric for the business).

### 2. The Copilot Engine & Guardrails
The application uses a semantic configuration (`metrics.yaml`) to enforce math. If the user asks for "ARR", the system does not guess; it is forced to apply the rule: `SUM(fct_revenue.mrr) * 12`. 

Furthermore, every output is paired with a **plain-English narrative explanation** of exactly which metric definitions were applied, ensuring absolute transparency and auditability for finance stakeholders.

---

## Demonstration
The interactive Streamlit interface (**Hex Magic / ChatGPT style**) allows an executive to ask complex questions and receive immediate, governed SQL, interactive charts, and data tables.

### Example Prompts Supported:

**1. Cross-Vertical Revenue:**
> *"What was net new ARR from healthcare customers this quarter?"*

**2. Forecast Variance:**
> *"Compare actual vs budget for healthcare revenue by month and call out the largest drivers of variance."*

**3. Hidden Exception Costs:**
> *"Which enterprise housing accounts had the highest expansion revenue last quarter but are also trending above average on support cost?"*

**4. Cohort Velocity:**
> *"Show cohorts signed in the last 12 months and their 90-day expansion performance."*

---

## Why This Matters for an Enterprise Data Strategy
The hard part of modern data analytics is not SQL generation; it is establishing trust. 

By building **BoardPrep AI**, I’ve demonstrated the exact skill set required for a Senior Finance Data Analyst:
1. Building rigorous finance datasets.
2. Governing core metrics (ARR, NRR, Cost to Serve).
3. Automating executive deliverables.
4. Distilling complex workflow data into clear financial stories for leadership.
