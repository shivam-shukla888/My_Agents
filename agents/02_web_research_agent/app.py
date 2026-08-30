"""
Streamlit Web UI for Agent 02: Autonomous Web Research Agent.
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
from research_agent.core.agent import WebResearchAgent
from shared.security import SecureWorkspaceVault

st.set_page_config(page_title="Agent 02: Web Research Agent", page_icon="🔍", layout="wide")

st.title("🔍 Agent 02: Autonomous Web Research Agent")
st.markdown("Deep web intelligence, competitor price-matching analysis, review synthesis, and report generation.")

vault = SecureWorkspaceVault()

if "research_chat" not in st.session_state:
    st.session_state.research_chat = []

# Quick Actions
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📊 MacBook M3 Competitor Prices", use_container_width=True):
        st.session_state.user_query = "Find all competitor retail prices for the Apple MacBook Air M3 and identify the cheapest option."
with c2:
    if st.button("🎧 Sony XM5 Reviews & ANC Rating", use_container_width=True):
        st.session_state.user_query = "Search and synthesize lab reviews and ANC rankings for the Sony WH-1000XM5 headphones."
with c3:
    if st.button("📝 Generate & Save Market Brief", use_container_width=True):
        st.session_state.user_query = "Generate an executive market research brief comparing the iPhone 16 Pro and Galaxy S25 Ultra retail pricing, and save it to the shared vault."

for msg in st.session_state.research_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Enter a research topic, product for competitor pricing, or review search...")
q = getattr(st.session_state, "user_query", None) or user_input
st.session_state.user_query = None

if q:
    st.session_state.research_chat.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Agent 02 is searching the web and analyzing market data..."):
            agent = WebResearchAgent()
            res = agent.invoke_with_trace(q)
            st.markdown(res["output"])
            st.session_state.research_chat.append({"role": "assistant", "content": res["output"]})

# Vault Viewer in Sidebar
with st.sidebar:
    st.header("📁 Shared Vault Files")
    files = vault.list_shared_files()
    if files:
        for f in files:
            st.markdown(f"📄 **{f['filename']}** ({f['size_bytes']} bytes)")
    else:
        st.info("Vault is empty. Ask the agent to save a report!")
