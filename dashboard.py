import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import models

# Set page config for maximum width
st.set_page_config(page_title="Enterprise AI Automation Finance OS", layout="wide", initial_sidebar_state="collapsed")

# Ultra-Premium Light Mode Theme (Consulting / Board Deck feel)
st.markdown("""
<style>
    /* Global background */
    .stApp {
        background-color: #F8FAFC; /* Light slate background */
        font-family: 'Inter', 'SF Pro Display', sans-serif;
        color: #0F172A;
    }
    
    /* Elegant metric cards */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        text-align: left;
        position: relative;
        overflow: hidden;
    }
    
    /* Subtle blue accent bar on top of cards */
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
    }

    .metric-value {
        font-size: 38px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 12px;
        font-feature-settings: "tnum"; /* tabular numbers */
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Clean headers */
    h1 {
        font-weight: 700 !important;
        color: #0F172A !important;
        font-size: 2.2rem !important;
        margin-bottom: 0.2rem !important;
        letter-spacing: -0.5px;
    }
    .subtitle {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Section headers */
    .section-title {
        font-size: 14px;
        color: #1E293B;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        margin-bottom: 20px;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 8px;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Data Loading
try:
    summary = models.get_executive_summary()
    cohorts = models.get_cohort_economics()
    verticals = models.get_automation_performance_by_vertical()
    trends = models.get_monthly_trend()
    sankey_data = models.get_sankey_data()
    heatmap_data = models.get_cohort_retention_heatmap()
except Exception as e:
    st.error(f"Data Connectivity Error. System Halted. ({str(e)})")
    st.stop()

# Header Section
st.markdown("<h1>Enterprise AI Automation Finance OS</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Platform Unit Economics & Workflow Resolution Telemetry</p>', unsafe_allow_html=True)

# 1. Executive Key Performance Indicators
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active Deployments</div>
        <div class="metric-value">{int(summary['total_clients']):,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Annualized Return (ARR)</div>
        <div class="metric-value">${summary['total_arr'] / 1000000:.1f}M</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Net Operational Savings</div>
        <div class="metric-value" style="color: #059669;">${summary['total_savings_generated'] / 1000000:.1f}M</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Global AI Resolution</div>
        <div class="metric-value" style="color: #2563EB;">{summary['blended_automation_rate'] * 100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)


# Common chart layout settings for Light Mode
layout_args = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#475569', family='Inter, sans-serif'),
    title_font=dict(size=14, color='#0F172A', family='Inter, sans-serif'),
    margin=dict(t=50, l=10, r=10, b=10),
    xaxis=dict(showgrid=False, zeroline=False, linecolor='#E2E8F0', tickcolor='#E2E8F0'),
    yaxis=dict(showgrid=True, gridcolor='#F1F5F9', zeroline=False, linecolor='#E2E8F0', tickcolor='#E2E8F0'),
)

st.markdown('<div class="section-title">Workflow Resolution Architecture</div>', unsafe_allow_html=True)

# 2. Advanced Topology: Sankey Flow
# Create labels for Sankey
nodes = list(pd.concat([sankey_data['source'], sankey_data['target']]).unique())
node_indices = {node: i for i, node in enumerate(nodes)}

source_indices = [node_indices[src] for src in sankey_data['source']]
target_indices = [node_indices[tgt] for tgt in sankey_data['target']]
values = sankey_data['value']

fig_sankey = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 20,
      thickness = 15,
      line = dict(color = "#E2E8F0", width = 0.5),
      label = nodes,
      color = ["#1E3A8A", "#6366F1", "#10B981", "#3B82F6", "#F43F5E"] # Strong, executive primary colors
    ),
    link = dict(
      source = source_indices,
      target = target_indices,
      value = values,
      color = "rgba(203, 213, 225, 0.4)" # Subtle gray links
  ))])

fig_sankey.update_layout(**layout_args, title_text="End-to-End Workflow Transformation Volume", height=400)
st.plotly_chart(fig_sankey, use_container_width=True, config={'displayModeBar': False})

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Velocity & Retention Intelligence</div>', unsafe_allow_html=True)


# 3. Dual Intelligence: Heatmap & Line
col_a, col_b = st.columns([1.2, 1])

with col_a:
    # Heatmap of Handle Rate by Cohort
    heatmap_pivot = heatmap_data.pivot(index="cohort_month", columns="active_month", values="handle_rate")
    
    fig_heat = px.imshow(
        heatmap_pivot,
        labels=dict(x="Active Month", y="Cohort Vintage", color="Resolution Rate"),
        title="AI Resolution Maturity by Contract Vintage",
        color_continuous_scale="Blues" # Clean corporate blue scale
    )
    
    # Custom layout
    fig_heat.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#475569', family='Inter, sans-serif'),
        title_font=dict(size=14, color='#0F172A', family='Inter, sans-serif'),
        margin=dict(t=50, l=10, r=10, b=10),
        coloraxis_colorbar=dict(title="", tickformat=".0%", thicknessmode="pixels", thickness=10)
    )
    # Remove gridlines for heatmap
    fig_heat.update_xaxes(showgrid=False, linecolor='rgba(0,0,0,0)')
    fig_heat.update_yaxes(showgrid=False, linecolor='rgba(0,0,0,0)')
    
    st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})

with col_b:
    # Value Generation Evolution
    fig_area = px.area(
        trends, x="month", y="monthly_savings", color="vertical",
        title="Compounding Operational Savings ($)",
        color_discrete_sequence=['rgba(30, 58, 138, 0.8)', 'rgba(99, 102, 241, 0.8)'] # Deep Blues
    )
    fig_area.update_layout(**layout_args, legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Cohort Investment Recovery (CAC)</div>', unsafe_allow_html=True)

# 4. Bubble Scatter for CAC Payback
cohorts_filtered = cohorts.dropna(subset=['cac_payback_months_gross']).copy()
cohorts_filtered = cohorts_filtered[cohorts_filtered['cohort_month'] >= '2023-01']

fig_c = px.scatter(
    cohorts_filtered, x="cohort_month", y="cac_payback_months_gross",
    color="vertical", size="cohort_arr",
    labels={"cac_payback_months_gross": "Gross Payback (Months)", "cohort_month": ""},
    color_discrete_sequence=['#1E3A8A', '#6366F1']
)
fig_c.update_layout(**layout_args, title="Investment Recovery Velocity vs Deployment Scale", showlegend=True, height=350)
fig_c.update_traces(marker=dict(line=dict(width=1, color='#FFFFFF')))
st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})

# Subtle status line Footer
st.markdown("""
<br>
<div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #94A3B8; text-transform: uppercase; border-top: 1px dashed #E2E8F0; padding-top: 10px;">
    SYSTEM LOG: DATA SYNCHRONIZED | KERNEL ACTIVE | AI TELEMETRY CONNECTED
</div>
""", unsafe_allow_html=True)
