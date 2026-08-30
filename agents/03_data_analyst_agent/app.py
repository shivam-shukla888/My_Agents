"""
Streamlit Web UI for Agent 03: SQL & Tabular Data Analyst Agent.
"""

import sys
from pathlib import Path

# Add paths
root_dir = Path(__file__).resolve().parent.parent.parent
src_dir = Path(__file__).resolve().parent / "src"
for p in [str(root_dir / "src"), str(src_dir), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
from analyst_agent.core.agent import DataAnalystAgent
from analyst_agent.connectors.sql_connector import SQLDataConnector
from shared.security import SecureWorkspaceVault

st.set_page_config(page_title="Agent 03: SQL Data Analyst", page_icon="📊", layout="wide")

st.title("📊 Agent 03: SQL & Tabular Data Analyst Agent")
st.markdown("Automated SQL generation, revenue analytics, stockout risk prediction, and visual chart reporting.")

sql_conn = SQLDataConnector()
vault = SecureWorkspaceVault()

if "analyst_chat" not in st.session_state:
    st.session_state.analyst_chat = []

# Quick Actions
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📈 Category Revenue Breakdown", use_container_width=True):
        st.session_state.user_query = "Calculate net revenue and units sold by category, and show a visual chart."
with c2:
    if st.button("⚠️ Check Stockout Risks", use_container_width=True):
        st.session_state.user_query = "Which products have the highest inventory turnover and are at risk of stockout within 14 days?"
with c3:
    if st.button("💾 Export Sales Summary to Vault", use_container_width=True):
        st.session_state.user_query = "Run a regional sales performance query and save the report to the shared vault."

for msg in st.session_state.analyst_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask a data question, request a SQL query, or check sales metrics...")
q = getattr(st.session_state, "user_query", None) or user_input
st.session_state.user_query = None

if q:
    st.session_state.analyst_chat.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        with st.spinner("📊 Agent 03 is formulating SQL & computing analytics..."):
            agent = DataAnalystAgent()
            res = agent.invoke_with_trace(q)
            st.markdown(res["output"])
            st.session_state.analyst_chat.append({"role": "assistant", "content": res["output"]})

# Sidebar Schema Inspector
with st.sidebar:
    st.header("🗄️ SQL Database Schema")
    schema = sql_conn.get_schema()
    for tbl, cols in schema.items():
        with st.expander(f"Table: `{tbl}`"):
            for c in cols:
                st.code(c, language="text")
    
    st.markdown("---")
    st.header("📁 Shared Vault Files")
    files = vault.list_shared_files()
    if files:
        for f in files:
            st.markdown(f"📄 **{f['filename']}** ({f['size_bytes']} bytes)")
    else:
        st.info("Vault is empty.")
