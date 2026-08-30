"""
🌐 Multi-Agent Collaborative Network & Evals Studio
World-Class AI Dashboard with Real 3D Visual Assets, Glassmorphism & Inter-Agent Intelligence.
"""

import os
import sys
import time
from pathlib import Path

# Add paths
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

# Page Configuration
st.set_page_config(
    page_title="My Agents: Autonomous Multi-Agent Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End CSS with Google Fonts & Glassmorphism
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4, .hero-title {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(21, 29, 46, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }

    /* Agent Cards */
    .agent-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .agent-box:hover {
        border-color: #6366F1;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.25);
    }
    
    /* Glowing Hero Badge */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 9999px;
        color: #818CF8;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .live-pulse {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10B981;
    }

    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.15;
    }
    
    /* Metric Pill */
    .metric-pill {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .metric-val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'Outfit', sans-serif;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

vault = SecureWorkspaceVault()

# Initialize Cached Multi-Agent Network
@st.cache_resource
def load_orchestrator(provider: str, model: str):
    return MultiAgentNetwork(provider=provider, model_name=model)

# -------------------------------------------------------------
# SIDEBAR CONTROL CENTER
# -------------------------------------------------------------
with st.sidebar:
    st.image("assets/agent_evals.jpg", caption="AI Agent Orchestrator", width=120)
    st.markdown("### 🎛️ Agent Command Hub")
    
    selected_mode = st.radio(
        "Operating Workspace",
        [
            "🌐 Multi-Agent Collaborative Mesh",
            "🛍️ Agent 01: Shopping & Catalog",
            "🔍 Agent 02: Deep Web Intelligence",
            "📊 Agent 03: SQL & Financial Analytics",
            "🧪 3-Pillar Evaluation Benchmark",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("### ⚡ Engine & Model Setup")
    
    provider_opt = st.selectbox("LLM Provider", ["Primary / Low Latency (Ultra Fast)", "Groq LPU Direct", "Google Gemini"])
    if "Primary" in provider_opt:
        prov = "primary"
        model_id = "gpt-4o-mini"
    elif "Groq" in provider_opt:
        prov = "groq"
        model_id = st.selectbox("Groq Model", ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"])
    else:
        prov = "google"
        model_id = "gemini-2.5-flash"

    st.markdown("---")
    st.markdown("### 📁 Shared Workspace Vault")
    vault_files = vault.list_shared_files()
    if vault_files:
        for vf in vault_files:
            st.markdown(f"📄 `{vf['filename']}` ({vf['size_bytes']} B)")
    else:
        st.info("Vault is ready for new reports.")

network = load_orchestrator(prov, model_id)

# -------------------------------------------------------------
# HERO HEADER SECTION WITH 3D ASSETS
# -------------------------------------------------------------
st.markdown("""
<div class="hero-badge">
    <span class="live-pulse"></span> Production Multi-Agent Ecosystem v2.0
</div>
""", unsafe_allow_html=True)

col_hero_text, col_hero_banner = st.columns([1.2, 1.8])

with col_hero_text:
    st.markdown('<div class="gradient-text">Autonomous Multi-Agent AI Studio</div>', unsafe_allow_html=True)
    st.markdown("""
    A unified network of domain-specialized AI agents cooperating over an **Inter-Agent Communication Bus**, 
    grounded with **ChromaDB Long-Term Memory**, and verified by a **3-Pillar Evaluation Suite**.
    """)
    
    # 3-Pillar Highlights
    st.markdown("""
    - ⚡ **Sub-Second Execution**: Ultra-low latency primary engine with automatic Groq LPU fallbacks.
    - 🛡️ **Anti-Hallucination Grounding**: Fact-checked against indexed ChromaDB documentation.
    - 🤝 **Live Inter-Agent Delegation**: Synchronous task handoffs between shopping, web research, and data analytics.
    """)

with col_hero_banner:
    st.image("assets/hero_banner.jpg", width="stretch")

st.markdown("---")

# -------------------------------------------------------------
# 3D AGENT GRID CARDS
# -------------------------------------------------------------
st.markdown("### 🤖 Deployed AI Agents & Systems")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.image("assets/agent_01_product.jpg", width="stretch")
    st.markdown("#### 🛍️ Agent 01: Products")
    st.caption("ChromaDB Memory, Catalog Specs, PDF Invoices & FX Pricing.")

with c2:
    st.image("assets/agent_02_research.jpg", width="stretch")
    st.markdown("#### 🔍 Agent 02: Research")
    st.caption("Competitor Live Prices (Amazon, Best Buy, B&H), Reviews & Synthesis.")

with c3:
    st.image("assets/agent_03_analyst.jpg", width="stretch")
    st.markdown("#### 📊 Agent 03: Data Analyst")
    st.caption("SQL Transactions, Revenue Charts, Margin Analysis & Stockout Forecasts.")

with c4:
    st.image("assets/agent_evals.jpg", width="stretch")
    st.markdown("#### 🧪 Evals Suite")
    st.caption("3 Pillars: Functional Accuracy, Latency/Cost & Safety/PII Scanners.")

st.markdown("---")

# -------------------------------------------------------------
# WORKSPACE 1: COLLABORATIVE MULTI-AGENT MESH
# -------------------------------------------------------------
if "Collaborative" in selected_mode:
    st.markdown("## 🌐 Multi-Agent Collaborative Mesh")
    st.markdown("Watch all 3 agents communicate, share context, and generate an executive intelligence report.")

    st.markdown("#### 💡 Quick Strategic Scenarios")
    p1, p2, p3 = st.columns(3)
    with p1:
        if st.button("💻 Apple MacBook Air M3 Analysis", width="stretch"):
            st.session_state.collab_input = "Evaluate Apple MacBook Air M3: catalog inventory, external competitor prices, and sales performance."
    with p2:
        if st.button("📱 Flagship Smartphone Face-off", width="stretch"):
            st.session_state.collab_input = "Compare iPhone 16 Pro and Galaxy S25 Ultra: store stock, external carrier deals, and category revenue share."
    with p3:
        if st.button("🖥️ Dell UltraSharp 27 4K Monitor", width="stretch"):
            st.session_state.collab_input = "Analyze Dell UltraSharp 27 4K: specs & power delivery, market retail prices, and days to stockout."

    user_goal = st.text_input("Or define a custom multi-agent business goal:", placeholder="e.g. Find best wireless headphones, research competitor prices, and plot sales revenue...")
    goal_to_run = getattr(st.session_state, "collab_input", None) or user_goal
    st.session_state.collab_input = None

    if st.button("🚀 Launch Collaborative Multi-Agent Execution", type="primary", width="stretch") and goal_to_run:
        st.markdown(f"### 🎯 Active Mission: *{goal_to_run}*")
        
        with st.status("🤖 Coordinating Autonomous Agents...", expanded=True) as status:
            st.write("🛍️ **Agent 01** inspecting product specifications & ChromaDB inventory...")
            collab_result = network.run_collaborative_workflow(goal_to_run)
            status.update(label="✅ Multi-Agent Collaboration Complete!", state="complete", expanded=False)

        # 3 Agent Output Tabs
        t1, t2, t3, t4 = st.tabs([
            "🛍️ 1. Catalog & Ground Truth (Agent 01)",
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
                width="stretch"
            )

# -------------------------------------------------------------
# WORKSPACE 2: AGENT 01 (PRODUCTS & SHOPPING)
# -------------------------------------------------------------
elif "01" in selected_mode:
    st.markdown("## 🛍️ Agent 01: Product Query & Shopping Assistant")
    col_img, col_chat = st.columns([1, 3])
    with col_img:
        st.image("assets/agent_01_product.jpg", width="stretch")
        st.markdown("**Tools:** `get_product`, `search_catalog`, `query_user_manuals`, `convert_currency_price`, `generate_customer_invoice_pdf`")
    
    with col_chat:
        q1 = st.text_input("Ask Agent 01:", value="What 4K monitors do you have in stock under $600 with 90W USB-C charging?")
        if st.button("Send Inquiry to Agent 01", type="primary"):
            with st.spinner("Agent 01 is searching catalog & ChromaDB memory..."):
                t0 = time.time()
                ans = network.agent_01.ask(q1)
                t_elapsed = round(time.time() - t0, 2)
                st.success(f"Response generated in {t_elapsed}s")
                st.markdown(ans)

# -------------------------------------------------------------
# WORKSPACE 3: AGENT 02 (WEB RESEARCH & COMPETITOR INTEL)
# -------------------------------------------------------------
elif "02" in selected_mode:
    st.markdown("## 🔍 Agent 02: Autonomous Web Research Agent")
    col_img, col_chat = st.columns([1, 3])
    with col_img:
        st.image("assets/agent_02_research.jpg", width="stretch")
        st.markdown("**Tools:** `search_tech_web`, `compare_competitor_retail_prices`, `scrape_webpage`, `save_research_brief_to_shared_vault`")
    
    with col_chat:
        q2 = st.text_input("Ask Agent 02:", value="Find competitor prices for Sony WH-1000XM5 and identify the best deal.")
        if st.button("Send Inquiry to Agent 02", type="primary"):
            with st.spinner("Agent 02 is scanning live web prices & tech reviews..."):
                t0 = time.time()
                ans = network.agent_02.ask(q2)
                t_elapsed = round(time.time() - t0, 2)
                st.success(f"Market search completed in {t_elapsed}s")
                st.markdown(ans)

# -------------------------------------------------------------
# WORKSPACE 4: AGENT 03 (SQL & TABULAR ANALYST)
# -------------------------------------------------------------
elif "03" in selected_mode:
    st.markdown("## 📊 Agent 03: SQL & Tabular Data Analyst Agent")
    col_img, col_chat = st.columns([1, 3])
    with col_img:
        st.image("assets/agent_03_analyst.jpg", width="stretch")
        st.markdown("**Tools:** `get_database_schema`, `run_sql_query`, `generate_category_revenue_chart`, `check_stockout_risks`")
    
    with col_chat:
        q3 = st.text_input("Ask Agent 03:", value="Calculate total revenue and sales volume across all categories and show a chart.")
        if st.button("Send Inquiry to Agent 03", type="primary"):
            with st.spinner("Agent 03 is formulating SQL & computing analytics..."):
                t0 = time.time()
                ans = network.agent_03.ask(q3)
                t_elapsed = round(time.time() - t0, 2)
                st.success(f"SQL execution completed in {t_elapsed}s")
                st.markdown(ans)

# -------------------------------------------------------------
# WORKSPACE 5: 3-PILLAR EVALUATION BENCHMARK
# -------------------------------------------------------------
elif "Evaluation" in selected_mode:
    st.markdown("## 🧪 3-Pillar Agent Evaluation Studio")
    st.markdown("Automated evaluation measuring **Functional Accuracy**, **Latency & Cost**, and **Safety/PII Compliance**.")

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

            # Deep Pillar Breakdown
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
