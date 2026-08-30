"""
Unified Multi-Agent Dashboard for My Agents Ecosystem.
Orchestrates Agent 01, Agent 02, and Agent 03 with Inter-Agent Communication Bus & Secure Shared Vault.
"""

import os
import sys
from pathlib import Path

# Add src directories to sys.path
root_dir = Path(__file__).resolve().parent
for p in [
    str(root_dir),
    str(root_dir / "src"),
    str(root_dir / "agents" / "01_product_query_agent" / "src"),
    str(root_dir / "agents" / "02_web_research_agent" / "src"),
    str(root_dir / "agents" / "03_data_analyst_agent" / "src"),
    str(root_dir / "shared"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
from dotenv import load_dotenv

from shared.orchestrator import MultiAgentNetwork
from shared.security import SecureWorkspaceVault

load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "src" / "agentic_ai" / ".env")

st.set_page_config(
    page_title="My Agents: Collaborative Multi-Agent Network",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .network-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .agent-pill-1 { background: #EFF6FF; color: #1D4ED8; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.8rem; }
    .agent-pill-2 { background: #F5F3FF; color: #6D28D9; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.8rem; }
    .agent-pill-3 { background: #ECFDF5; color: #047857; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

vault = SecureWorkspaceVault()

# Sidebar: Environment & Mode Selector
with st.sidebar:
    st.title("🤖 Multi-Agent Hub")
    
    mode = st.radio(
        "Select Operating Mode",
        [
            "🌐 Collaborative Team Mode (All 3 Agents)",
            "🛍️ Agent 01: Product Query Assistant",
            "🔍 Agent 02: Web Research Agent",
            "📊 Agent 03: SQL Data Analyst Agent",
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("⚙️ Multi-Model Setup")
    provider = st.selectbox("LLM Provider", ["Groq (Fast)", "Google Gemini"])
    selected_provider = "groq" if "Groq" in provider else "google"
    
    if selected_provider == "groq":
        model_choice = st.selectbox("Model", ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"], index=0)
    else:
        model_choice = st.selectbox("Model", ["gemini-2.5-flash", "gemini-1.5-flash"], index=0)

    st.markdown("---")
    st.subheader("📁 Secure File Vault")
    files = vault.list_shared_files()
    if files:
        for f in files:
            st.markdown(f"📄 **{f['filename']}** ({f['size_bytes']} bytes)")
    else:
        st.info("No shared files yet.")


@st.cache_resource
def get_network(prov: str, model: str):
    return MultiAgentNetwork(provider=prov, model_name=model)

network = get_network(selected_provider, model_choice)

# Main UI Routing based on Mode
if "Collaborative" in mode:
    st.markdown('<div class="network-header">🌐 Collaborative Multi-Agent Network</div>', unsafe_allow_html=True)
    st.markdown("Watch **Agent 01 (Products)**, **Agent 02 (Web Research)**, and **Agent 03 (Data Analytics)** cooperate in real-time to solve complex business goals.")

    st.markdown("""
    <div style="display:flex; gap:10px; margin-bottom:15px;">
        <span class="agent-pill-1">🛍️ Agent 01: Specs & Stock</span>
        <span class="agent-pill-2">🔍 Agent 02: Competitor Prices</span>
        <span class="agent-pill-3">📊 Agent 03: Sales & Forecasting</span>
    </div>
    """, unsafe_allow_html=True)

    # Preset scenarios
    st.markdown("**💡 Quick Collaborative Scenarios:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💻 High-End Laptop Market Analysis", use_container_width=True):
            st.session_state.collab_goal = "Evaluate the Apple MacBook Air M3: catalog inventory, competitor retail pricing, and regional sales turnover."
    with c2:
        if st.button("📱 Flagship Smartphone Face-off", use_container_width=True):
            st.session_state.collab_goal = "Compare iPhone 16 Pro and Galaxy S25 Ultra: store stock, external carrier deals, and category revenue share."
    with c3:
        if st.button("🖥️ 4K Monitor Stockout Strategy", use_container_width=True):
            st.session_state.collab_goal = "Analyze Dell UltraSharp 27 4K: specs & power delivery, market retail prices, and days to stockout."

    user_goal = st.text_input("Or enter custom collaborative goal:", placeholder="e.g. Find best wireless headphones, research competitor prices, and plot sales revenue...")
    goal_to_run = getattr(st.session_state, "collab_goal", None) or user_goal
    st.session_state.collab_goal = None

    if st.button("🚀 Run Multi-Agent Team Execution", type="primary") and goal_to_run:
        st.markdown(f"### 🎯 Goal: *{goal_to_run}*")
        
        with st.status("🤖 Orchestrating Agents...", expanded=True) as status:
            st.write("🛍️ **Agent 01** inspecting product specifications & ChromaDB inventory...")
            res = network.run_collaborative_workflow(goal_to_run)
            status.update(label="✅ Multi-Agent Collaboration Complete!", state="complete", expanded=False)

        # Render 3 Agent Steps
        t1, t2, t3, t4 = st.tabs([
            "🛍️ Agent 01: Specs & Stock",
            "🔍 Agent 02: Market Pricing",
            "📊 Agent 03: Sales Analytics",
            "📑 Full Executive Report & Download"
        ])

        with t1:
            st.subheader("🛍️ Agent 01: Catalog & Ground-Truth Specifications")
            st.markdown(res["steps"][0]["output"])

        with t2:
            st.subheader("🔍 Agent 02: Competitor Retail Prices & Review Synthesis")
            st.markdown(res["steps"][1]["output"])

        with t3:
            st.subheader("📊 Agent 03: Sales Revenue & Inventory Health")
            st.markdown(res["steps"][2]["output"])

        with t4:
            st.subheader("📑 Shared Vault Executive Brief")
            st.markdown(res["final_summary"])
            st.download_button(
                label="⬇️ Download Executive Brief (Markdown)",
                data=res["final_summary"],
                file_name="collaborative_executive_brief.md",
                mime="text/markdown",
            )

elif "01" in mode:
    st.title("🛍️ Agent 01: Product Query & Shopping Assistant")
    st.markdown("ChromaDB persistent memory, catalog lookups, multi-currency conversions, and PDF invoice creation.")
    
    agent_01 = network.agent_01
    q1 = st.text_input("Ask Agent 01:", value="What laptops do you have under $1200, and what discounts apply?")
    if st.button("Submit to Agent 01"):
        with st.spinner("Agent 01 is thinking..."):
            ans = agent_01.ask(q1)
            st.markdown(ans)

elif "02" in mode:
    st.title("🔍 Agent 02: Autonomous Web Research Agent")
    st.markdown("Competitor retail price tracking (Amazon, Best Buy, B&H), review synthesis, and market research briefs.")
    
    agent_02 = network.agent_02
    q2 = st.text_input("Ask Agent 02:", value="Find competitor prices for the Apple MacBook Air M3 and identify the best retail deal.")
    if st.button("Submit to Agent 02"):
        with st.spinner("Agent 02 is researching the web..."):
            ans = agent_02.ask(q2)
            st.markdown(ans)

elif "03" in mode:
    st.title("📊 Agent 03: SQL & Tabular Data Analyst Agent")
    st.markdown("SQL transactional queries, category revenue charts, and stockout forecasting.")
    
    agent_03 = network.agent_03
    q3 = st.text_input("Ask Agent 03:", value="Calculate total revenue and sales volume by category, and check stockout risks.")
    if st.button("Submit to Agent 03"):
        with st.spinner("Agent 03 is formulating SQL & computing analytics..."):
            ans = agent_03.ask(q3)
            st.markdown(ans)
