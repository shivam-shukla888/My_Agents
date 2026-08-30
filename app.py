"""
Unified Multi-Agent Dashboard for My Agents Ecosystem.
Features:
- Collaborative Multi-Agent Team Execution (Agent 1, Agent 2, Agent 3)
- Individual Agent Workspaces
- 🧪 Agent Evaluation Suite (Functional Eval, Cost Eval, Safety Eval)
- Inter-Agent Communication Bus & Secure Shared Vault
"""

import os
import sys
from pathlib import Path

# Add source paths
root_dir = Path(__file__).resolve().parent
for p in [
    str(root_dir),
    str(root_dir / "src"),
    str(root_dir / "agents" / "01_product_query_agent" / "src"),
    str(root_dir / "agents" / "02_web_research_agent" / "src"),
    str(root_dir / "agents" / "03_data_analyst_agent" / "src"),
    str(root_dir / "shared"),
    str(root_dir / "evals"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
from dotenv import load_dotenv

from shared.orchestrator import MultiAgentNetwork
from shared.security import SecureWorkspaceVault
from evals.runner import EvaluationRunner
from evals.benchmark_dataset import BENCHMARK_TEST_SUITE

load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "src" / "agentic_ai" / ".env")

st.set_page_config(
    page_title="My Agents: Multi-Agent Network & Evals",
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
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

vault = SecureWorkspaceVault()

# Sidebar: Mode Selector & Setup
with st.sidebar:
    st.title("🤖 Multi-Agent Hub")
    
    mode = st.radio(
        "Select Operating Mode",
        [
            "🌐 Collaborative Team Mode (All 3 Agents)",
            "🛍️ Agent 01: Product Query Assistant",
            "🔍 Agent 02: Web Research Agent",
            "📊 Agent 03: SQL Data Analyst Agent",
            "🧪 Agent Evals Suite (3 Pillars)",
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


# -------------------------------------------------------------
# MODE 1: Collaborative Multi-Agent Network
# -------------------------------------------------------------
if "Collaborative" in mode:
    st.markdown('<div class="network-header">🌐 Collaborative Multi-Agent Network</div>', unsafe_allow_html=True)
    st.markdown("Watch **Agent 01 (Products)**, **Agent 02 (Web Research)**, and **Agent 03 (Data Analytics)** cooperate in real-time to solve complex business goals.")

    # Preset scenarios
    st.markdown("**💡 Quick Collaborative Scenarios:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💻 Laptop Market Analysis", use_container_width=True):
            st.session_state.collab_goal = "Evaluate the Apple MacBook Air M3: catalog inventory, competitor retail pricing, and regional sales turnover."
    with c2:
        if st.button("📱 Smartphone Face-off", use_container_width=True):
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

# -------------------------------------------------------------
# MODE 2: Agent 01
# -------------------------------------------------------------
elif "01" in mode:
    st.title("🛍️ Agent 01: Product Query & Shopping Assistant")
    st.markdown("ChromaDB persistent memory, catalog lookups, multi-currency conversions, and PDF invoice creation.")
    agent_01 = network.agent_01
    q1 = st.text_input("Ask Agent 01:", value="What laptops do you have under $1200, and what discounts apply?")
    if st.button("Submit to Agent 01"):
        with st.spinner("Agent 01 is thinking..."):
            ans = agent_01.ask(q1)
            st.markdown(ans)

# -------------------------------------------------------------
# MODE 3: Agent 02
# -------------------------------------------------------------
elif "02" in mode:
    st.title("🔍 Agent 02: Autonomous Web Research Agent")
    st.markdown("Competitor retail price tracking (Amazon, Best Buy, B&H), review synthesis, and market research briefs.")
    agent_02 = network.agent_02
    q2 = st.text_input("Ask Agent 02:", value="Find competitor prices for the Apple MacBook Air M3 and identify the best retail deal.")
    if st.button("Submit to Agent 02"):
        with st.spinner("Agent 02 is researching the web..."):
            ans = agent_02.ask(q2)
            st.markdown(ans)

# -------------------------------------------------------------
# MODE 4: Agent 03
# -------------------------------------------------------------
elif "03" in mode:
    st.title("📊 Agent 03: SQL & Tabular Data Analyst Agent")
    st.markdown("SQL transactional queries, category revenue charts, and stockout forecasting.")
    agent_03 = network.agent_03
    q3 = st.text_input("Ask Agent 03:", value="Calculate total revenue and sales volume by category, and check stockout risks.")
    if st.button("Submit to Agent 03"):
        with st.spinner("Agent 03 is formulating SQL & computing analytics..."):
            ans = agent_03.ask(q3)
            st.markdown(ans)

# -------------------------------------------------------------
# MODE 5: 🧪 AGENT EVALS SUITE (3 PILLARS)
# -------------------------------------------------------------
elif "Evals" in mode:
    st.title("🧪 Agentic AI Evaluation Suite (3 Pillars)")
    st.markdown("Automated evaluation across **Functional Correctness & Faithfulness**, **Cost & Latency**, and **Safety & PII Defense**.")

    eval_runner = EvaluationRunner(network=network)

    eval_tab1, eval_tab2 = st.tabs(["🎯 Live Single Query Eval", "📈 Batch Benchmark Suite"])

    with eval_tab1:
        st.subheader("Live 3-Pillar Evaluation on Any Query")
        col_a1, col_a2 = st.columns([1, 2])
        with col_a1:
            target_agent = st.selectbox(
                "Target Agent",
                ["01_product_query_agent", "02_web_research_agent", "03_data_analyst_agent"]
            )
        with col_a2:
            test_q = st.text_input(
                "Test Query",
                value="What are the specs and price for the Apple MacBook Air M3 and what discounts can I use?"
            )
            gt_text = st.text_input(
                "Ground Truth (Optional)",
                value="Apple MacBook Air M3 costs $1099.00 USD with 16GB memory, 512GB SSD, 18-hour battery, and coupons TECHSAVINGS10 or SUMMERSALE15."
            )

        if st.button("🔬 Run 3-Pillar Evaluation", type="primary"):
            with st.spinner("Running Functional, Cost, and Safety Evaluations..."):
                eval_report = eval_runner.evaluate_single_interaction(
                    agent_id=target_agent,
                    question=test_q,
                    ground_truth=gt_text,
                    model_name=model_choice,
                )

            # Scorecard Header
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Overall Grade", eval_report["overall_grade"])
            with m2:
                st.metric("1. Functional Score", f"{eval_report['pillar_1_functional']['score_pct']}%")
            with m3:
                st.metric("2. Latency & Tokens", f"{eval_report['pillar_2_cost_and_latency']['latency_seconds']}s", f"{eval_report['pillar_2_cost_and_latency']['total_tokens']} tokens")
            with m4:
                st.metric("3. Safety Score", f"{eval_report['pillar_3_safety']['score_pct']}%")

            st.markdown("---")
            st.subheader("Agent Response")
            st.markdown(eval_report["response"])

            # 3 Pillar Details
            p1, p2, p3 = st.columns(3)
            with p1:
                st.markdown("### 1. Functional Eval")
                st.json(eval_report["pillar_1_functional"])
            with p2:
                st.markdown("### 2. Cost & Performance Eval")
                st.json(eval_report["pillar_2_cost_and_latency"])
            with p3:
                st.markdown("### 3. Safety & Robustness Eval")
                st.json(eval_report["pillar_3_safety"])

    with eval_tab2:
        st.subheader("Run Standard Golden Benchmark Suite (7 Curated Test Cases)")
        st.write(f"Test cases include catalog lookups, RAG manual retrieval, competitor pricing, SQL analytics, and adversarial jailbreak/PII attacks.")

        if st.button("🚀 Run All Benchmark Test Cases"):
            with st.spinner("Executing full golden benchmark suite..."):
                bench_res = eval_runner.run_full_benchmark()

            st.markdown(bench_res["summary_markdown"])

            with st.expander("🔍 Detailed Test Case Results"):
                for res in bench_res["test_results"]:
                    st.markdown(f"**[{res['test_case_id']}] {res['category']}** | Grade: `{res['overall_grade']}` | Func: `{res['pillar_1_functional']['score_pct']}%` | Safety: `{res['pillar_3_safety']['score_pct']}%` | Latency: `{res['pillar_2_cost_and_latency']['latency_seconds']}s`")
                    st.write(f"*Q:* {res['question']}")
                    st.write(f"*A:* {res['response'][:200]}...")
                    st.markdown("---")
