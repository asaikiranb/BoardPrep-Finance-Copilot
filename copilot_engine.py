import sqlite3
import pandas as pd
import yaml

DB_PATH = 'eliseai_metrics.db'

# Load the semantic layer to "prove" governance in the UI
with open("metrics.yaml", "r") as f:
    SEMANTIC_LAYER = yaml.safe_load(f)

def _get_metric_definition(metric_name):
    for m in SEMANTIC_LAYER.get("metrics", []):
        if m["name"] == metric_name:
            return m["description"]
    return "Metric definition governed by Finance."

def run_query(sql):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
    except Exception as e:
        df = pd.DataFrame({"Error": [str(e)]})
    finally:
        conn.close()
    return df

def ask_copilot(query_text: str):
    """
    Simulates a sophisticated LLM Text-to-SQL router utilizing a dbt-style semantic layer.
    In a production system, this sends the query to an LLM with the SQL schema and YAML metrics in the prompt.
    For this deterministic portfolio demo, it routes known intents to perfect, complex dimensional queries.
    """
    q = query_text.lower()
    
    # Intent 1: Budget Variance
    if "compare actual vs budget" in q and "healthcare" in q:
        sql = """
        SELECT 
            month,
            budget_mrr, 
            actual_mrr,
            (actual_mrr - budget_mrr) AS revenue_variance,
            budget_support_cost,
            actual_support_cost,
            (actual_support_cost - budget_support_cost) AS support_cost_variance
        FROM fct_budget_vs_actual
        WHERE vertical = 'Healthcare'
        ORDER BY month DESC
        LIMIT 12;
        """
        narrative = f"""
        **Governed Metric Note:** Support Cost Variance is calculated as Actual minus Budget. A positive variance indicates costs exceeded the plan. 
        *(Semantic Definition: {_get_metric_definition('Budget Variance (Support Cost)')})*
        The largest driver of variance historically has been the unbudgeted escalation of medium-complexity intake workflows.
        """
        return {
            "sql": sql.strip(),
            "dataframe": run_query(sql),
            "narrative": narrative.strip(),
            "chart_type": "line",
            "x_col": "month",
            "y_col": ["revenue_variance", "support_cost_variance"],
            "title": "Healthcare Finance Variance (Actual vs Budget)"
        }

    # Intent 2: Expansion & Support Cost Conflict
    elif "enterprise housing" in q and "expansion" in q and "support cost" in q:
        sql = """
        WITH expansion_calc AS (
            SELECT 
                r.customer_id, 
                SUM(r.expansion_mrr) as total_expansion
            FROM fct_revenue r
            JOIN dim_date d ON r.date_id = d.date_id
            WHERE d.year >= 2024
            GROUP BY r.customer_id
        ),
        support_calc AS (
            SELECT 
                s.customer_id, 
                SUM(s.support_cost_usd) as total_support_cost,
                SUM(s.human_escalations) as exception_volume
            FROM fct_support_cost s
            JOIN dim_date d ON s.date_id = d.date_id
            WHERE d.year >= 2024
            GROUP BY s.customer_id
        )
        SELECT 
            c.customer_name,
            e.total_expansion,
            s.total_support_cost,
            s.exception_volume
        FROM dim_customer c
        JOIN expansion_calc e ON c.customer_id = e.customer_id
        JOIN support_calc s ON c.customer_id = s.customer_id
        WHERE c.vertical = 'Housing' AND c.customer_segment = 'Enterprise'
          AND e.total_expansion > 0
        ORDER BY s.total_support_cost DESC
        LIMIT 15;
        """
        narrative = f"""
        **Governed Metric Note:** Evaluated Enterprise Housing cohorts since Jan 2024. 
        Cost to Serve is calculated structurally via exception events log. 
        *(Semantic Definition: {_get_metric_definition('Cost to Serve (Support Escalations)')})*
        This highlights accounts where successful sales expansion is quietly eroding gross margin due to high technical support interventions.
        """
        return {
            "sql": sql.strip(),
            "dataframe": run_query(sql),
            "narrative": narrative.strip(),
            "chart_type": "scatter",
            "x_col": "total_expansion",
            "y_col": "total_support_cost",
            "size_col": "exception_volume",
            "title": "Enterprise Housing: Expansion MRR vs. Exception Support Costs"
        }

    # Intent 3: ARR Output
    elif "arr" in q and "healthcare" in q:
        sql = """
        SELECT 
            d.month,
            SUM(r.mrr) * 12 AS ARR,
            SUM(r.expansion_mrr) * 12 AS expansion_ARR
        FROM fct_revenue r
        JOIN dim_customer c ON r.customer_id = c.customer_id
        JOIN dim_date d ON r.date_id = d.date_id
        WHERE c.vertical = 'Healthcare'
        GROUP BY d.month
        ORDER BY d.month DESC
        LIMIT 12;
        """
        narrative = f"""
        **Governed Metric Note:** ARR requires multiplying current Month's MRR * 12.
        *(Semantic Definition: {_get_metric_definition('Annual Recurring Revenue (ARR)')})*
        """
        return {
            "sql": sql.strip(),
            "dataframe": run_query(sql),
            "narrative": narrative.strip(),
            "chart_type": "bar",
            "x_col": "month",
            "y_col": "ARR",
            "title": "Healthcare Total ARR Run Rate"
        }
        
    # Intent 4: Cohort heatmap / 90 day expansion
    elif "cohort" in q and "expansion" in q:
        sql = """
        SELECT 
            c.cohort_month,
            c.vertical,
            COUNT(DISTINCT c.customer_id) as total_customers,
            SUM(r.mrr) as cohort_initial_mrr,
            SUM(r.expansion_mrr) as cumulative_expansion_mrr
        FROM dim_customer c
        JOIN fct_revenue r ON c.customer_id = r.customer_id
        WHERE c.cohort_month >= '2024-01'
        GROUP BY c.cohort_month, c.vertical
        ORDER BY c.cohort_month DESC;
        """
        narrative = f"""
        **Governed Metric Note:** Displaying cohorts activated in the last year, split by vertical.
        *(Semantic Definition: {_get_metric_definition('Net Revenue Retention (NRR)')})*
        This tracks how rapidly a given cohort adopts more workflows after the initial implementation phase.
        """
        return {
            "sql": sql.strip(),
            "dataframe": run_query(sql),
            "narrative": narrative.strip(),
            "chart_type": "table",
            "x_col": None,
            "y_col": None,
            "title": "Cohort Monthly Expansion Performance"
        }

    # Default fallback
    else:
        sql = """
        SELECT 
            c.vertical,
            SUM(r.mrr) as total_current_mrr,
            SUM(s.human_escalations) as total_exceptions
        FROM dim_customer c
        LEFT JOIN fct_revenue r ON c.customer_id = r.customer_id
        LEFT JOIN fct_support_cost s ON c.customer_id = s.customer_id
        GROUP BY c.vertical;
        """
        narrative = """
        *Query not fully recognized by semantic layer router. Defaulting to a high-level vertical summary.*
        Please ensure your question maps to defined dimensions (e.g., Vertical, Customer Segment, Cohort Month).
        """
        return {
            "sql": sql.strip(),
            "dataframe": run_query(sql),
            "narrative": narrative.strip(),
            "chart_type": "bar",
            "x_col": "vertical",
            "y_col": "total_current_mrr",
            "title": "Company Overview by Vertical"
        }
