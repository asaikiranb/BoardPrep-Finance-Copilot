import sqlite3
import pandas as pd

DB_PATH = 'eliseai_metrics.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_executive_summary():
    """Returns high-level KPI summary across the entire platform."""
    query = """
    SELECT 
        COUNT(DISTINCT c.client_id) as total_clients,
        SUM(c.arr) as total_arr,
        SUM(m.total_automation_savings) as total_savings_generated,
        SUM(m.ai_handled_events) * 1.0 / SUM(m.total_events) as blended_automation_rate
    FROM clients c
    JOIN metrics_daily m ON c.client_id = m.client_id
    WHERE c.status = 'Active'
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn).iloc[0]

def get_cohort_economics():
    """Calculates ROI and CAC metrics by cohort month and vertical."""
    query = """
    WITH cohort_base AS (
        SELECT 
            c.cohort_month,
            c.vertical,
            COUNT(DISTINCT c.client_id) as num_clients,
            SUM(c.implementation_cost) as total_cac,
            SUM(c.arr) as cohort_arr
        FROM clients c
        GROUP BY c.cohort_month, c.vertical
    ),
    cohort_savings AS (
        SELECT 
            c.cohort_month,
            c.vertical,
            SUM(m.total_automation_savings) as cohort_automation_savings
        FROM clients c
        JOIN metrics_daily m ON c.client_id = m.client_id
        GROUP BY c.cohort_month, c.vertical
    )
    SELECT 
        b.cohort_month,
        b.vertical,
        b.num_clients,
        b.total_cac,
        b.cohort_arr,
        s.cohort_automation_savings,
        (b.total_cac / NULLIF(b.cohort_arr, 0)) * 12 as cac_payback_months_gross,
        s.cohort_automation_savings / b.num_clients as avg_savings_per_client
    FROM cohort_base b
    LEFT JOIN cohort_savings s USING (cohort_month, vertical)
    ORDER BY b.cohort_month, b.vertical
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def get_automation_performance_by_vertical():
    """Compares the AI automation rates and volume between verticals."""
    query = """
    SELECT 
        c.vertical,
        SUM(m.total_events) as total_workflow_events,
        SUM(m.ai_handled_events) as ai_handled_events,
        SUM(m.total_events) - SUM(m.ai_handled_events) as human_handled_events,
        SUM(m.ai_handled_events) * 1.0 / SUM(m.total_events) as ai_handle_rate,
        SUM(m.total_automation_savings) as total_customer_savings,
        SUM(m.total_fallback_cost) as total_human_cost
    FROM clients c
    JOIN metrics_daily m ON c.client_id = m.client_id
    GROUP BY c.vertical
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def get_monthly_trend():
    """Returns monthly usage and savings trends for charting."""
    query = """
    SELECT 
        strftime('%Y-%m', m.date) as month,
        c.vertical,
        SUM(m.total_events) as total_events,
        SUM(m.ai_handled_events) * 1.0 / SUM(m.total_events) as automation_rate,
        SUM(m.total_automation_savings) as monthly_savings
    FROM metrics_daily m
    JOIN clients c ON m.client_id = c.client_id
    GROUP BY 1, 2
    ORDER BY 1, 2
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def get_sankey_data():
    """Returns data formatted for a Sankey volume flow diagram."""
    query = """
    SELECT 
        c.vertical as source,
        'Total Workflows' as target,
        SUM(m.total_events) as value
    FROM clients c
    JOIN metrics_daily m ON c.client_id = m.client_id
    GROUP BY c.vertical
    
    UNION ALL
    
    SELECT 
        'Total Workflows' as source,
        'AI Resolved' as target,
        SUM(m.ai_handled_events) as value
    FROM metrics_daily m
    
    UNION ALL
    
    SELECT 
        'Total Workflows' as source,
        'Human Fallback' as target,
        SUM(m.total_events - m.ai_handled_events) as value
    FROM metrics_daily m
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def get_cohort_retention_heatmap():
    """Calculates AI Handle Rate over time by Cohort Month"""
    query = """
    SELECT 
        c.cohort_month,
        strftime('%Y-%m', m.date) as active_month,
        SUM(m.ai_handled_events) * 1.0 / SUM(m.total_events) as handle_rate
    FROM clients c
    JOIN metrics_daily m ON c.client_id = m.client_id
    GROUP BY c.cohort_month, active_month
    HAVING active_month >= '2023-01' AND c.cohort_month >= '2023-01'
    ORDER BY c.cohort_month DESC, active_month ASC
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)
