"""
🌐 My Agents: Enterprise Multi-Agent AI Studio
World-Class SaaS UI with Progressive Execution, Real 3D Assets, Inter-Agent Mesh,
ChromaDB Persistent Memory & 3-Pillar Evals Benchmark.
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add source directories to Python path
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
from agentic_ai.connectors import DatabaseConnector, ChromaMemoryConnector

load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "src" / "agentic_ai" / ".env")

# -------------------------------------------------------------
# PAGE CONFIGURATION & DESIGN SYSTEM
# -------------------------------------------------------------
st.set_page_config(
    page_title="My Agents: Autonomous AI Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
    /* CSS Variables Design Tokens */
    :root {
        --bg-primary: #0B0F14;
        --bg-secondary: #111720;
        --bg-elevated: #151C26;
        --border-subtle: #222C38;
        --border-hover: #334155;
        --text-primary: #F5F7FA;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --accent-primary: #7C5CFF;
        --accent-hover: #8B70FF;
        --accent-glow: rgba(124, 92, 255, 0.15);
        --success: #22C55E;
        --warning: #F59E0B;
        --error: #EF4444;
    }

    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Top Bar Header */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 20px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .top-bar-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .top-bar-badge {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        background: rgba(34, 197, 94, 0.12);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .telemetry-badge {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 9999px;
        background: rgba(124, 92, 255, 0.12);
        color: #A78BFA;
        border: 1px solid rgba(124, 92, 255, 0.3);
        font-family: 'JetBrains Mono', monospace;
    }
    .pulse-dot {
        width: 6px;
        height: 6px;
        background: #22C55E;
        border-radius: 50%;
        box-shadow: 0 0 8px #22C55E;
    }

    /* Tool Call Chips */
    .tool-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 10px;
        background: rgba(124, 92, 255, 0.08);
        border: 1px solid rgba(124, 92, 255, 0.25);
        border-radius: 8px;
        color: #C4B5FD;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
</style>
""", unsafe_allow_html=True)

vault = SecureWorkspaceVault()

# -------------------------------------------------------------
# GLOBAL CACHED NETWORK INSTANCE
# -------------------------------------------------------------
@st.cache_resource
def get_cached_multi_agent_network(prov_name: str, model_name: str):
    return MultiAgentNetwork(provider=prov_name, model_name=model_name)

# Session State
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = None
if "pending_goal" not in st.session_state:
    st.session_state.pending_goal = None

# -------------------------------------------------------------
# SIDEBAR CONTROL CENTER
# -------------------------------------------------------------
with st.sidebar:
    st.image("assets/agent_evals.jpg", caption="My Agents Studio", width=120)
    st.markdown("### ⚡ **My Agents Studio**")
    st.caption("Autonomous Multi-Agent Workspace")

    if st.button("➕ New Session", width="stretch", type="primary"):
        st.session_state.chat_messages = []
        st.session_state.last_metrics = None
        st.rerun()

    st.markdown("---")
    st.markdown("##### 🧭 Workspaces & Agents")
    active_workspace = st.radio(
        "Workspace Selection",
        [
            "🌐 Multi-Agent Collaborative Mesh",
            "🛍️ Agent 01: Shopping & Catalog",
            "🔍 Agent 02: Deep Web Intelligence",
            "📊 Agent 03: SQL Data Analytics",
            "🧪 3-Pillar Evals Benchmark",
            "📁 Shared Vault Explorer",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    with st.expander("⚙️ LLM Engine & Routing", expanded=False):
        prov_select = st.radio("Provider", ["Primary (Ultra Fast)", "Groq LPU Direct", "Google Gemini"])
        if "Primary" in prov_select:
            sel_prov = "primary"
            sel_model = "gpt-4o-mini"
        elif "Groq" in prov_select:
            sel_prov = "groq"
            sel_model = st.selectbox("Groq Model", ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"])
        else:
            sel_prov = "google"
            sel_model = st.selectbox("Gemini Model", ["gemini-2.5-flash", "gemini-1.5-flash"])

    st.markdown("---")
    if st.button("🗑️ Clear Session Context", width="stretch"):
        st.session_state.chat_messages = []
        st.session_state.last_metrics = None
        st.success("Session reset.")
        st.rerun()

# Load Cached Orchestrator
network = get_cached_multi_agent_network(sel_prov, sel_model)

# Top Bar Header
metrics_html = ""
if st.session_state.last_metrics:
    m = st.session_state.last_metrics
    metrics_html = f"""<span class="telemetry-badge">⏱️ {m.get('latency', '0.0')}s | {m.get('tools', 0)} tools | Engine: {sel_prov.title()}</span>"""

st.markdown(f"""
<div class="top-bar">
    <div class="top-bar-title">
        <span>🤖</span> {active_workspace}
    </div>
    <div style="display: flex; gap: 8px; align-items: center;">
        <span class="top-bar-badge"><span class="pulse-dot"></span> System Online</span>
        {metrics_html}
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================
# WORKSPACE 1: MULTI-AGENT COLLABORATIVE MESH
# =============================================================
if "Collaborative" in active_workspace:
    st.markdown("### 🌐 **Autonomous Multi-Agent Team Execution**")
    st.caption("Agent 01 (Products), Agent 02 (Web Research), and Agent 03 (SQL Analytics) collaborate synchronously over the shared communication bus.")

    # 3D Agent Summary Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.image("assets/agent_01_product.jpg", width="stretch")
        st.markdown("##### 🛍️ Agent 01: Product Catalog")
        st.caption("Catalog specs, inventory stock, ChromaDB memory, and PDF invoices.")
    with c2:
        st.image("assets/agent_02_research.jpg", width="stretch")
        st.markdown("##### 🔍 Agent 02: Web Research")
        st.caption("Live competitor prices (Amazon, Best Buy, B&H), reviews & briefs.")
    with c3:
        st.image("assets/agent_03_analyst.jpg", width="stretch")
        st.markdown("##### 📊 Agent 03: SQL Analytics")
        st.caption("Transactional SQL queries, category revenue & stockout forecasts.")

    st.markdown("---")
    st.markdown("##### 💡 Strategic Collaborative Objectives")
    s1, s2, s3 = st.columns(3)
    with s1:
        if st.button("💻 **Apple MacBook Air M3 Strategy**\n\nEvaluate catalog stock, competitor pricing & sales.", width="stretch"):
            st.session_state.pending_goal = "Evaluate Apple MacBook Air M3: catalog inventory, external competitor prices, and sales performance."
    with s2:
        if st.button("📱 **Smartphone Market Face-off**\n\nCompare iPhone 16 Pro and Galaxy S25 Ultra deals.", width="stretch"):
            st.session_state.pending_goal = "Compare iPhone 16 Pro and Galaxy S25 Ultra: store stock, external carrier deals, and category revenue share."
    with s3:
        if st.button("🖥️ **Dell 4K Monitor Stockout Health**\n\nAnalyze Dell UltraSharp 27 specs, retail prices & stockout.", width="stretch"):
            st.session_state.pending_goal = "Analyze Dell UltraSharp 27 4K: specs & power delivery, market retail prices, and days to stockout."

    user_mission = st.text_input("Or input a custom collaborative mission:", placeholder="e.g. Find best wireless headphones, research competitor deals online, and analyze sales revenue...")
    goal_to_run = st.session_state.pending_goal or user_mission
    st.session_state.pending_goal = None

    if st.button("🚀 Launch Multi-Agent Execution", type="primary", width="stretch") and goal_to_run:
        st.markdown(f"#### 🎯 Goal: *{goal_to_run}*")
        t0 = time.perf_counter()
        
        with st.status("🤖 Orchestrating Multi-Agent Team...", expanded=True) as status_box:
            st.write("🛍️ **Agent 01** inspecting catalog specifications & ChromaDB inventory...")
            collab_result = network.run_collaborative_workflow(goal_to_run)
            status_box.update(label="✅ Multi-Agent Collaboration Complete!", state="complete", expanded=False)

        t_elapsed = round(time.perf_counter() - t0, 2)
        st.session_state.last_metrics = {"latency": t_elapsed, "tools": 3}

        # Render 3 Agent Steps
        t1, t2, t3, t4 = st.tabs([
            "🛍️ 1. Catalog & Specs (Agent 01)",
            "🔍 2. Market Intelligence (Agent 02)",
            "📊 3. Sales Analytics (Agent 03)",
            "📑 Shared Vault Executive Brief"
        ])

        with t1:
            st.markdown(collab_result["steps"][0]["output"])
        with t2:
            st.markdown(collab_result["steps"][1]["output"])
        with t3:
            st.markdown(collab_result["steps"][2]["output"])
        with t4:
            st.markdown(collab_result["final_summary"])
            st.download_button(
                label="⬇️ Download Executive Brief (Markdown)",
                data=collab_result["final_summary"],
                file_name="collaborative_executive_brief.md",
                mime="text/markdown",
                width="stretch",
            )


# =============================================================
# WORKSPACE 2: AGENT 01 (PRODUCTS & CHAT)
# =============================================================
elif "01" in active_workspace:
    st.markdown("### 🛍️ **Agent 01: Product Query & Shopping Assistant**")
    st.caption("Equipped with ChromaDB long-term memory, grounding verification, catalog lookups, and PDF invoices.")

    q1 = st.text_input("Ask Agent 01:", value="What 4K monitors do you have in stock under $600 with 90W USB-C charging?")
    if st.button("Send Inquiry to Agent 01", type="primary"):
        with st.status("⚡ Agent 01 is reasoning...", expanded=True) as status:
            t0 = time.perf_counter()
            ans = network.agent_01.ask(q1)
            t_elapsed = round(time.perf_counter() - t0, 2)
            status.update(label=f"✅ Response Generated in {t_elapsed}s", state="complete", expanded=False)
            st.session_state.last_metrics = {"latency": t_elapsed, "tools": 1}
        st.markdown(ans)


# =============================================================
# WORKSPACE 3: AGENT 02 (WEB RESEARCH)
# =============================================================
elif "02" in active_workspace:
    st.markdown("### 🔍 **Agent 02: Autonomous Web Research Agent**")
    st.caption("Live competitor price-matching (Amazon, Best Buy, B&H, Walmart), tech reviews, and research briefs.")

    q2 = st.text_input("Ask Agent 02:", value="Find competitor prices for Sony WH-1000XM5 and identify the best retail deal.")
    if st.button("Send Inquiry to Agent 02", type="primary"):
        with st.status("🔍 Agent 02 scanning web sources...", expanded=True) as status:
            t0 = time.perf_counter()
            ans = network.agent_02.ask(q2)
            t_elapsed = round(time.perf_counter() - t0, 2)
            status.update(label=f"✅ Research Completed in {t_elapsed}s", state="complete", expanded=False)
            st.session_state.last_metrics = {"latency": t_elapsed, "tools": 1}
        st.markdown(ans)


# =============================================================
# WORKSPACE 4: AGENT 03 (SQL ANALYST)
# =============================================================
elif "03" in active_workspace:
    st.markdown("### 📊 **Agent 03: SQL & Tabular Data Analyst Agent**")
    st.caption("Read-only safe SQL queries, transactional sales performance, category revenue charts, and stockout forecasting.")

    q3 = st.text_input("Ask Agent 03:", value="Calculate total revenue and sales volume across all categories and show a visual chart.")
    if st.button("Send Inquiry to Agent 03", type="primary"):
        with st.status("📊 Formulating SQL & computing analytics...", expanded=True) as status:
            t0 = time.perf_counter()
            ans = network.agent_03.ask(q3)
            t_elapsed = round(time.perf_counter() - t0, 2)
            status.update(label=f"✅ SQL Analytics Completed in {t_elapsed}s", state="complete", expanded=False)
            st.session_state.last_metrics = {"latency": t_elapsed, "tools": 1}
        st.markdown(ans)


# =============================================================
# WORKSPACE 5: 3-PILLAR EVALS BENCHMARK
# =============================================================
elif "Evals" in active_workspace:
    st.markdown("### 🧪 **3-Pillar Agent Evaluation Studio**")
    st.caption("Automated evaluation measuring **Functional Accuracy**, **Latency & Cost**, and **Safety/PII Compliance**.")

    eval_runner = EvaluationRunner(network=network)
    tab_single, tab_golden = st.tabs(["🎯 Live Single Interaction Eval", "📈 Golden Benchmark Suite"])

    with tab_single:
        st.subheader("Interactive 3-Pillar Test")
        c_t1, c_t2 = st.columns([1, 2])
        with c_t1:
            target_agent_id = st.selectbox("Target Agent", ["01_product_query_agent", "02_web_research_agent", "03_data_analyst_agent"])
        with c_t2:
            test_prompt = st.text_input("Query", value="What is the price and display size of the Apple MacBook Air M3?")
            expected_gt = st.text_input("Ground Truth", value="Apple MacBook Air M3 costs $1099.00 with 13.6-inch Liquid Retina display.")

        if st.button("🔬 Run 3-Pillar Evaluation", type="primary", width="stretch"):
            with st.spinner("Running Functional, Cost, and Safety evaluation algorithms..."):
                scorecard = eval_runner.evaluate_single_interaction(
                    agent_id=target_agent_id,
                    question=test_prompt,
                    ground_truth=expected_gt,
                )

            # Scorecard KPIs
            st.markdown("### 🏆 Evaluation Scorecard")
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Overall Grade", scorecard["overall_grade"])
            with k2:
                st.metric("1. Functional Accuracy", f"{scorecard['pillar_1_functional']['score_pct']}%")
            with k3:
                st.metric("2. Latency & Tokens", f"{scorecard['pillar_2_cost_and_latency']['latency_seconds']}s", f"{scorecard['pillar_2_cost_and_latency']['total_tokens']} tokens")
            with k4:
                st.metric("3. Safety Compliance", f"{scorecard['pillar_3_safety']['score_pct']}%")

            st.markdown("---")
            st.subheader("Agent Response Output")
            st.markdown(scorecard["response"])

            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.markdown("#### 1. Functional Breakdown")
                st.json(scorecard["pillar_1_functional"])
            with col_p2:
                st.markdown("#### 2. Cost & Latency Metrics")
                st.json(scorecard["pillar_2_cost_and_latency"])
            with col_p3:
                st.markdown("#### 3. Safety & PII Scan")
                st.json(scorecard["pillar_3_safety"])

    with tab_golden:
        st.subheader("Standard Golden Benchmark Suite (7 Curated Scenarios)")
        st.write("Tests accuracy across catalog specs, competitor retail prices, SQL queries, and adversarial prompt injections.")

        if st.button("🚀 Execute Golden Benchmark Suite", width="stretch"):
            with st.spinner("Executing benchmark across all test cases..."):
                bench_report = eval_runner.run_full_benchmark()

            st.markdown(bench_report["summary_markdown"])

            with st.expander("🔍 Test Case Execution Trace"):
                for tcr in bench_report["test_results"]:
                    st.markdown(f"**[{tcr['test_case_id']}]** Grade: `{tcr['overall_grade']}` | Functional: `{tcr['pillar_1_functional']['score_pct']}%` | Safety: `{tcr['pillar_3_safety']['score_pct']}%` | Latency: `{tcr['pillar_2_cost_and_latency']['latency_seconds']}s`")
                    st.write(f"*Q:* {tcr['question']}")
                    st.write(f"*A:* {tcr['response'][:250]}...")
                    st.markdown("---")


# =============================================================
# WORKSPACE 6: SHARED VAULT EXPLORER
# =============================================================
elif "Vault" in active_workspace:
    st.markdown("### 📁 **Secure Workspace Vault Explorer**")
    st.caption("Sandboxed file vault (`shared/workspace/`) where agents exchange generated reports, datasets, and invoices.")

    v_files = vault.list_shared_files()
    if v_files:
        for vf in v_files:
            with st.container(border=True):
                c_fn, c_act = st.columns([3, 1])
                with c_fn:
                    st.markdown(f"📄 **{vf['filename']}**")
                    st.caption(f"Size: {vf['size_bytes']} bytes • Modified: {vf['modified_at']}")
                with c_act:
                    f_data = vault.read_file(vf['filename'], reader_agent="UI_User")
                    if f_data["status"] == "success":
                        st.download_button(
                            label="⬇️ Download",
                            data=f_data["content"],
                            file_name=vf['filename'],
                            mime="text/markdown",
                            width="stretch",
                            key=f"dl_{vf['filename']}"
                        )
    else:
        st.info("Vault is currently empty. Run a multi-agent collaborative task to generate executive briefs!")
