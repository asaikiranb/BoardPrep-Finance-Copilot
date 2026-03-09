import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import yaml

DB_PATH = 'eliseai_metrics.db'
NUM_CLIENTS = 120
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime.now()
DAYS = (END_DATE - START_DATE).days

def generate_dim_date():
    dates = []
    curr = START_DATE
    while curr <= END_DATE:
        dates.append({
            'date_id': curr.strftime('%Y-%m-%d'),
            'month': curr.strftime('%Y-%m'),
            'quarter': f"{curr.year}-Q{(curr.month-1)//3 + 1}",
            'year': curr.year
        })
        curr += timedelta(days=1)
    return pd.DataFrame(dates)

def generate_dim_workflow_type():
    workflows = [
        {'workflow_id': 'wf_h1', 'workflow_name': 'Maintenance Request (Standard)', 'vertical': 'Housing', 'complexity_tier': 'Low'},
        {'workflow_id': 'wf_h2', 'workflow_name': 'Leasing Inquiry & Tour Scheduling', 'vertical': 'Housing', 'complexity_tier': 'Medium'},
        {'workflow_id': 'wf_h3', 'workflow_name': 'Emergency Maintenance Triage', 'vertical': 'Housing', 'complexity_tier': 'High'},
        {'workflow_id': 'wf_m1', 'workflow_name': 'Patient Intake & Registration', 'vertical': 'Healthcare', 'complexity_tier': 'Medium'},
        {'workflow_id': 'wf_m2', 'workflow_name': 'Post-Scheduling Clinical Clarification', 'vertical': 'Healthcare', 'complexity_tier': 'High'},
        {'workflow_id': 'wf_m3', 'workflow_name': 'Basic Appointment Reminder', 'vertical': 'Healthcare', 'complexity_tier': 'Low'},
    ]
    return pd.DataFrame(workflows)

def generate_dim_customer():
    np.random.seed(42)
    clients = []
    
    for i in range(NUM_CLIENTS):
        vertical = np.random.choice(['Housing', 'Healthcare'], p=[0.7, 0.3]) # EliseAI has strong housing presence
        segment = np.random.choice(['Enterprise', 'Mid-Market'], p=[0.25, 0.75])
        cohort_month = (START_DATE + timedelta(days=np.random.randint(0, DAYS))).strftime('%Y-%m')
        
        clients.append({
            'customer_id': f"cust_{uuid.uuid4().hex[:8]}",
            'customer_name': f"{vertical} {segment} Partner {i}",
            'vertical': vertical,
            'customer_segment': segment,
            'cohort_month': cohort_month,
            'industry': vertical
        })
    return pd.DataFrame(clients)

def generate_fct_revenue(dim_customer, dim_date):
    revenue_records = []
    months = sorted(dim_date['month'].unique())
    
    for _, client in dim_customer.iterrows():
        cohort_idx = months.index(client['cohort_month']) if client['cohort_month'] in months else len(months)
        
        # Base MRR
        base_mrr = np.random.normal(15000, 5000) if client['customer_segment'] == 'Enterprise' else np.random.normal(3000, 1000)
        current_mrr = base_mrr
        
        for m_idx in range(cohort_idx, len(months)):
            month_str = months[m_idx]
            
            # Find the first valid date_id for this month to use as the record timestamp
            valid_dates = dim_date[dim_date['month'] == month_str]['date_id'].values
            date_id = valid_dates[0] if len(valid_dates) > 0 else f"{month_str}-01"

            expansion = 0.0
            contraction = 0.0
            one_time_fee = 0.0
            
            # Implementation fee in month 1
            if m_idx == cohort_idx:
                one_time_fee = current_mrr * 2.5
                
            # Random expansion events (e.g. buying more units/workflows)
            elif np.random.random() < 0.05: 
                expansion = current_mrr * np.random.uniform(0.1, 0.3)
                current_mrr += expansion
                
            # Churn/Contraction risk
            elif np.random.random() < 0.02:
                contraction = current_mrr * np.random.uniform(-0.5, -0.1)
                current_mrr += contraction
                
            revenue_records.append({
                'record_id': f"rev_{uuid.uuid4().hex[:12]}",
                'customer_id': client['customer_id'],
                'date_id': date_id,
                'mrr': current_mrr,
                'expansion_mrr': expansion,
                'contraction_mrr': contraction,
                'one_time_implementation_fee': one_time_fee
            })
            
            # Stop tracking if churned fully
            if current_mrr <= 0: break
            
    return pd.DataFrame(revenue_records)

def generate_fct_support_cost(dim_customer, dim_date, dim_workflow):
    support_records = []
    # Using specific dates instead of pure monthly grouping to mimic a true transactional fact table
    # For speed of generation in portfolio, we'll generate at the weekly grain but assign to a date_id
    
    # EliseAI Specific Exception Archetypes
    exceptions_h = ['Resident Context Unclear', 'Complex Multi-Issue Maintenance', 'Awkward Leasing Handoff', 'Third-Party Vendor Escalation', 'System Timeout']
    exceptions_m = ['Incomplete Patient Intake', 'Post-Scheduling Clarification Loop', 'Insurance Verification Failure', 'Clinical Urgency Escalation']
    
    for _, client in dim_customer.iterrows():
        vertical = client['vertical']
        workflows = dim_workflow[dim_workflow['vertical'] == vertical]
        
        cohort_date = datetime.strptime(client['cohort_month'], "%Y-%m")
        curr = cohort_date
        
        while curr <= END_DATE:
            # Skip some days to be realistic, simulating weekly batch checks
            curr += timedelta(days=7)
            if curr > END_DATE: break
                
            date_id = curr.strftime('%Y-%m-%d')
            
            for _, wf in workflows.iterrows():
                # Base volume
                base_ai_volume = np.random.randint(50, 500) if client['customer_segment'] == 'Enterprise' else np.random.randint(10, 100)
                
                # Escalation logic based on complexity
                if wf['complexity_tier'] == 'High':
                    escalation_rate = np.random.uniform(0.15, 0.35)
                    cost_per_minute = 1.50 # Specialized support
                elif wf['complexity_tier'] == 'Medium':
                    escalation_rate = np.random.uniform(0.08, 0.20)
                    cost_per_minute = 1.00
                else:
                    escalation_rate = np.random.uniform(0.02, 0.08)
                    cost_per_minute = 0.50
                    
                escalations = int(base_ai_volume * escalation_rate)
                
                if escalations > 0:
                    exception_reason = np.random.choice(exceptions_h if vertical == 'Housing' else exceptions_m)
                    
                    # Specific penalties
                    if exception_reason in ['Incomplete Patient Intake', 'Awkward Leasing Handoff']:
                        labor_minutes = escalations * np.random.uniform(15, 25) # Messy cleanups take longer
                    else:
                        labor_minutes = escalations * np.random.uniform(5, 12)
                        
                    support_records.append({
                        'record_id': f"sup_{uuid.uuid4().hex[:12]}",
                        'customer_id': client['customer_id'],
                        'date_id': date_id,
                        'workflow_id': wf['workflow_id'],
                        'total_ai_interactions': base_ai_volume,
                        'human_escalations': escalations,
                        'primary_exception_reason': exception_reason,
                        'support_labor_minutes': labor_minutes,
                        'support_cost_usd': labor_minutes * cost_per_minute
                    })

    return pd.DataFrame(support_records)

def build_budget_vs_actual(fct_rev, fct_support, dim_date, dim_cust):
    # Generates a macro-level budget table for the copilot to query
    fct_rev['month'] = fct_rev['date_id'].str[:7]
    merged = pd.merge(fct_rev, dim_cust, on='customer_id')
    actual_rev = merged.groupby(['month', 'vertical'])['mrr'].sum().reset_index()
    
    fct_support['month'] = fct_support['date_id'].str[:7]
    merged_sup = pd.merge(fct_support, dim_cust, on='customer_id')
    actual_sup = merged_sup.groupby(['month', 'vertical'])['support_cost_usd'].sum().reset_index()
    
    budget = pd.merge(actual_rev, actual_sup, on=['month', 'vertical'], how='left').fillna(0)
    
    budget_records = []
    for _, row in budget.iterrows():
        # Inject budget variance
        # Assume hitting revenue plan usually, but support costs constantly blow past budget
        b_rev = row['mrr'] * np.random.uniform(0.95, 1.05)
        b_sup = row['support_cost_usd'] * np.random.uniform(0.60, 0.85) # Consistently underbudgeted support costs!
        
        budget_records.append({
            'record_id': f"bva_{uuid.uuid4().hex[:8]}",
            'vertical': row['vertical'],
            'month': row['month'],
            'budget_mrr': b_rev,
            'actual_mrr': row['mrr'],
            'budget_support_cost': b_sup,
            'actual_support_cost': row['support_cost_usd']
        })
        
    return pd.DataFrame(budget_records)
    

def main():
    print("Initializing BoardPrep AI Governed Semantic Backend...")
    
    d_date = generate_dim_date()
    d_wf = generate_dim_workflow_type()
    d_cust = generate_dim_customer()
    print(f"Generated Dimensions: {len(d_cust)} customers")
    
    f_rev = generate_fct_revenue(d_cust, d_date)
    f_sup = generate_fct_support_cost(d_cust, d_date, d_wf)
    print(f"Generated Facts: {len(f_rev)} revenue, {len(f_sup)} support events")
    
    f_bva = build_budget_vs_actual(f_rev.copy(), f_sup.copy(), d_date, d_cust)
    
    print("Writing to eliseai_metrics.db...")
    conn = sqlite3.connect(DB_PATH)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
        
    d_date.to_sql('dim_date', conn, if_exists='replace', index=False)
    d_wf.to_sql('dim_workflow_type', conn, if_exists='replace', index=False)
    d_cust.to_sql('dim_customer', conn, if_exists='replace', index=False)
    f_rev.to_sql('fct_revenue', conn, if_exists='replace', index=False)
    f_sup.to_sql('fct_support_cost', conn, if_exists='replace', index=False)
    f_bva.to_sql('fct_budget_vs_actual', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    print("Database ready for Text-to-SQL copilot.")

if __name__ == '__main__':
    main()
