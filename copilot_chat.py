import streamlit as st
import pandas as pd
import plotly.express as px
import time
import copilot_engine

# Set page config
st.set_page_config(page_title="BoardPrep AI: Finance Copilot", layout="wide", initial_sidebar_state="expanded")

# Clean, Hex-like Light Mode
st.markdown("""
<style>
    .stApp {
        background-color: #FAFAFA;
        font-family: 'Inter', sans-serif;
        color: #111827;
    }
    
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding-bottom: 100px;
    }
    
    .bot-message {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .user-message {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 16px 24px;
        margin-bottom: 24px;
        font-weight: 500;
        text-align: right;
        margin-left: auto;
        width: fit-content;
        max-width: 80%;
    }
    
    .sql-block {
        background-color: #1F2937;
        color: #F8FAFC;
        padding: 16px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        overflow-x: auto;
        margin: 16px 0;
    }
    
    .narrative-block {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        margin-top: 16px;
        font-size: 14px;
        color: #1E3A8A;
    }
    
    /* Hide top bar */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# (Sidebar removed per user request)

st.markdown("<h2 style='text-align: center; color: #111827; font-weight: 700; margin-bottom: 40px;'>Enterprise Executive Finance Copilot</h2>", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Welcome message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Welcome to BoardPrep AI. I am securely connected to the enterprise dimensional finance models. What would you like to analyze today?",
        "type": "text"
    })

# Formatter helper
def render_message(msg):
    if msg["role"] == "user":
        st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='bot-message'>", unsafe_allow_html=True)
        if msg["type"] == "text":
            st.markdown(msg["content"])
        elif msg["type"] == "analysis":
            # 1. SQL Block
            st.markdown("##### Approved Query")
            st.markdown(f"<div class='sql-block'>{msg['sql']}</div>", unsafe_allow_html=True)
            
            # 2. Chart / Data
            st.markdown(f"##### {msg['title']}")
            df = msg['dataframe']
            
            if msg['chart_type'] == 'line':
                fig = px.line(df, x=msg['x_col'], y=msg['y_col'])
                st.plotly_chart(fig, use_container_width=True)
            elif msg['chart_type'] == 'bar':
                fig = px.bar(df, x=msg['x_col'], y=msg['y_col'])
                st.plotly_chart(fig, use_container_width=True)
            elif msg['chart_type'] == 'scatter':
                fig = px.scatter(df, x=msg['x_col'], y=msg['y_col'], size=msg['size_col'], hover_name='customer_name')
                st.plotly_chart(fig, use_container_width=True)
            elif msg['chart_type'] == 'table':
                st.dataframe(df, use_container_width=True)
            
            # 3. Narrative & Governance
            st.markdown(f"<div class='narrative-block'>{msg['narrative']}</div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

# Layout container
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    render_message(msg)

# Suggested Prompts Row
if len(st.session_state.messages) == 1:
    st.markdown("##### Try asking:")
    c1, c2 = st.columns(2)
    c1.button("Compare actual vs budget for healthcare revenue by month and call out the largest drivers of variance.", key="p1", on_click=lambda: st.session_state.update(prompt="Compare actual vs budget for healthcare revenue by month and call out the largest drivers of variance."))
    c2.button("Which enterprise housing accounts had the highest expansion revenue last quarter but are also trending above average on support cost?", key="p2", on_click=lambda: st.session_state.update(prompt="Which enterprise housing accounts had the highest expansion revenue last quarter but are also trending above average on support cost?"))
    c1.button("What was net new ARR from healthcare customers this quarter?", key="p3", on_click=lambda: st.session_state.update(prompt="What was net new ARR from healthcare customers this quarter?"))
    c2.button("Show cohorts signed in the last 12 months and their 90-day expansion performance.", key="p4", on_click=lambda: st.session_state.update(prompt="Show cohorts signed in the last 12 months and their 90-day expansion performance."))

st.markdown("</div>", unsafe_allow_html=True)

# Chat Input
user_input = st.chat_input("Ask a finance question...")

# Also handle button clicks injecting into prompt
if "prompt" in st.session_state and st.session_state.prompt:
    user_input = st.session_state.prompt
    st.session_state.prompt = None

if user_input:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun() # Refresh to show user bubble immediately

# 2. Generate Assistant Reply (Only triggered if last message was from user)
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    
    with st.spinner("Translating intent, applying semantic layer metadata, generating secure SQL..."):
        time.sleep(1.5) # Fake LLM latency for demo feel
        
        response_data = copilot_engine.ask_copilot(user_query)
        
        # Append analysis result
        st.session_state.messages.append({
            "role": "assistant",
            "type": "analysis",
            "sql": response_data["sql"],
            "dataframe": response_data["dataframe"],
            "narrative": response_data["narrative"],
            "chart_type": response_data["chart_type"],
            "x_col": response_data["x_col"],
            "y_col": response_data["y_col"],
            "size_col": response_data.get("size_col"),
            "title": response_data["title"]
        })
        
        st.rerun()
