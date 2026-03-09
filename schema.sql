-- BoardPrep AI / EliseAI Finance Dimensional Model
-- Designed for governed executive reporting via Text-to-SQL

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    vertical TEXT NOT NULL, -- 'Housing' or 'Healthcare'
    customer_segment TEXT NOT NULL, -- 'Enterprise', 'Mid-Market'
    cohort_month TEXT NOT NULL, -- YYYY-MM
    industry TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id TEXT PRIMARY KEY, -- YYYY-MM-DD
    month TEXT NOT NULL,      -- YYYY-MM
    quarter TEXT NOT NULL,    -- YYYY-QQ
    year INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_workflow_type (
    workflow_id TEXT PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    vertical TEXT NOT NULL,
    complexity_tier TEXT NOT NULL -- 'Low', 'Medium', 'High'
);

CREATE TABLE IF NOT EXISTS fct_revenue (
    record_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    date_id TEXT NOT NULL,
    mrr REAL NOT NULL,
    expansion_mrr REAL NOT NULL,
    contraction_mrr REAL NOT NULL,
    one_time_implementation_fee REAL NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id)
);

CREATE TABLE IF NOT EXISTS fct_support_cost (
    record_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    date_id TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    total_ai_interactions INTEGER NOT NULL,
    human_escalations INTEGER NOT NULL,
    -- Examples of specific exception strings for the copilot to analyze
    primary_exception_reason TEXT NOT NULL, 
    support_labor_minutes REAL NOT NULL,
    support_cost_usd REAL NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY(workflow_id) REFERENCES dim_workflow_type(workflow_id)
);

CREATE TABLE IF NOT EXISTS fct_budget_vs_actual (
    record_id TEXT PRIMARY KEY,
    vertical TEXT NOT NULL,
    month TEXT NOT NULL, -- YYYY-MM
    budget_mrr REAL NOT NULL,
    actual_mrr REAL NOT NULL,
    budget_support_cost REAL NOT NULL,
    actual_support_cost REAL NOT NULL
);

-- Optimize for common copilot aggregation patterns
CREATE INDEX IF NOT EXISTS idx_fct_rev_cust ON fct_revenue(customer_id);
CREATE INDEX IF NOT EXISTS idx_fct_rev_date ON fct_revenue(date_id);
CREATE INDEX IF NOT EXISTS idx_fct_supp_cust ON fct_support_cost(customer_id);
CREATE INDEX IF NOT EXISTS idx_fct_supp_date ON fct_support_cost(date_id);
