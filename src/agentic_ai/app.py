"""
🌐 My Agents: Premium Autonomous AI SaaS Workspace
Clean, high-performance production UI with Progressive Execution, ChromaDB Grounding,
Persistent Memory, and Integrated Tool Workspaces.
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add source directory to Python path
current_file = Path(__file__).resolve()
src_dir = current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
root_dir = src_dir.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from dotenv import load_dotenv

from agentic_ai.core import HighLevelAgent, get_llm
from agentic_ai.plugins import (
    PluginRegistry,
    CatalogPlugin,
    RAGSupportPlugin,
    FinancePlugin,
    InvoicePlugin,
    MemoryPlugin,
)
from agentic_ai.connectors import (
    DatabaseConnector,
    VectorRAGConnector,
    RESTAPIConnector,
    PDFConnector,
    ChromaMemoryConnector,
)
from agentic_ai.products_data import PRODUCTS, DISCOUNTS

# Load environment configurations
load_dotenv(current_file.parent / ".env")
load_dotenv(src_dir / ".env")
load_dotenv(root_dir / ".env")

# -------------------------------------------------------------
# PAGE SETUP & PREMIUM DESIGN SYSTEM
# -------------------------------------------------------------
st.set_page_config(
    page_title="My Agents: Autonomous Product Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End SaaS Styling (Linear / Vercel / Perplexity aesthetic)
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

    /* Global Streamlit App Overrides */
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
        padding: 12px 18px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .top-bar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .top-bar-badge {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
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

    /* Message Bubbles */
    .user-msg-container {
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 14px;
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .assistant-msg-container {
        background: transparent;
        border: 1px solid transparent;
        padding: 4px 6px 16px 6px;
        margin-bottom: 16px;
        color: var(--text-primary);
        line-height: 1.6;
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

    /* Empty State Suggestion Cards */
    .suggestion-box {
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        height: 100%;
    }
    .suggestion-box:hover {
        border-color: var(--accent-primary);
        background: var(--bg-elevated);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .suggestion-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .suggestion-desc {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    /* Memory Card */
    .memory-item {
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# GLOBAL CACHED CONNECTORS & AGENT FACTORY
# -------------------------------------------------------------
@st.cache_resource
def initialize_cached_connectors():
    """Cache persistent connectors across all reruns."""
    db = DatabaseConnector()
    rag = VectorRAGConnector()
    api = RESTAPIConnector()
    pdf = PDFConnector()
    chroma = ChromaMemoryConnector()
    for c in [db, rag, api, pdf, chroma]:
        c.connect()
    return db, rag, api, pdf, chroma

db_conn, rag_conn, api_conn, pdf_conn, chroma_conn = initialize_cached_connectors()


@st.cache_resource
def get_cached_agent(
    provider_name: str,
    model_id: str,
    temp: float,
    cat_on: bool,
    rag_on: bool,
    fin_on: bool,
    inv_on: bool,
    mem_on: bool,
):
    """
    Cache compiled LangGraph agent instance to avoid expensive graph reconstruction on every rerun.
    """
    registry = PluginRegistry()
    registry.register(CatalogPlugin(db_connector=db_conn, enabled=cat_on))
    registry.register(RAGSupportPlugin(vector_connector=rag_conn, enabled=rag_on))
    registry.register(FinancePlugin(api_connector=api_conn, enabled=fin_on))
    registry.register(InvoicePlugin(pdf_connector=pdf_conn, db_connector=db_conn, enabled=inv_on))
    registry.register(MemoryPlugin(chroma_connector=chroma_conn, enabled=mem_on))

    llm = get_llm(provider=provider_name, model_name=model_id, temperature=temp)
    agent = HighLevelAgent(
        llm=llm,
        registry=registry,
        chroma_conn=chroma_conn,
    )
    return agent


# -------------------------------------------------------------
# SESSION STATE MANAGEMENT
# -------------------------------------------------------------
if "messages_display" not in st.session_state:
    st.session_state.messages_display = []
if "active_view" not in st.session_state:
    st.session_state.active_view = "💬 Chat Workspace"
if "last_telemetry" not in st.session_state:
    st.session_state.last_telemetry = None
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# -------------------------------------------------------------
# SIDEBAR NAVIGATION & CONFIGURATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ **My Agents**")
    st.caption("Grounded Autonomous Agent Workspace")

    if st.button("➕ New Conversation", width="stretch", type="primary"):
        st.session_state.messages_display = []
        st.session_state.last_telemetry = None
        st.rerun()

    st.markdown("---")
    st.markdown("##### 🧭 Workspace Navigation")
    nav_view = st.radio(
        "Navigation",
        [
            "💬 Chat Workspace",
            "🧠 Memory Explorer",
            "🛡️ Grounding Lab",
            "📦 Product Catalog",
            "📄 Invoice Document Hub",
        ],
        label_visibility="collapsed",
    )
    st.session_state.active_view = nav_view

    st.markdown("---")
    with st.expander("👤 User Identity & Session", expanded=True):
        user_id = st.text_input("User ID", value="alex_smith", help="ChromaDB stores user memory facts under this identifier")
        thread_id = st.text_input("Thread ID", value="session_main", help="LangGraph checkpointer tracks conversation context")

    with st.expander("⚙️ Model & Engine Setup", expanded=False):
        provider_radio = st.radio("Provider", ["Primary (Ultra Fast)", "Groq LPU Direct", "Google Gemini"])
        if "Primary" in provider_radio:
            active_prov = "primary"
            active_model = "gpt-4o-mini"
        elif "Groq" in provider_radio:
            active_prov = "groq"
            active_model = st.selectbox("Groq Model", ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"])
        else:
            active_prov = "google"
            active_model = st.selectbox("Gemini Model", ["gemini-2.5-flash", "gemini-1.5-flash"])

        temp_val = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05, help="0.0 for deterministic tool execution")

    with st.expander("🧩 Capabilities & Plugins", expanded=False):
        en_catalog = st.toggle("📦 Product Catalog", value=True)
        en_rag = st.toggle("📚 User Manuals RAG", value=True)
        en_finance = st.toggle("💱 Multi-Currency & Tax", value=True)
        en_invoice = st.toggle("📄 PDF Invoicing", value=True)
        en_memory = st.toggle("🧠 ChromaDB Memory", value=True)

    st.markdown("---")
    if st.button("🗑️ Reset Active Thread", width="stretch"):
        st.session_state.messages_display = []
        st.session_state.last_telemetry = None
        st.success(f"Thread '{thread_id}' cleared.")
        st.rerun()

# Build or retrieve cached agent
agent_instance = get_cached_agent(
    provider_name=active_prov,
    model_id=active_model,
    temp=temp_val,
    cat_on=en_catalog,
    rag_on=en_rag,
    fin_on=en_finance,
    inv_on=en_invoice,
    mem_on=en_memory,
)

# -------------------------------------------------------------
# TOP BAR HEADER
# -------------------------------------------------------------
telemetry_html = ""
if st.session_state.last_telemetry:
    t = st.session_state.last_telemetry
    telemetry_html = f"""<span class="telemetry-badge">⏱️ {t.get('total_seconds', 0)}s | {t.get('tool_count', 0)} tools | mem: {t.get('memory_retrieval_ms', 0)}ms</span>"""

st.markdown(f"""
<div class="top-bar">
    <div class="top-bar-title">
        <span>🛍️</span> Product & Shopping Intelligence Agent
    </div>
    <div style="display: flex; gap: 8px; align-items: center;">
        <span class="top-bar-badge"><span class="pulse-dot"></span> ChromaDB Grounded</span>
        {telemetry_html}
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================
# VIEW 1: CHAT WORKSPACE (PRIMARY)
# =============================================================
if st.session_state.active_view == "💬 Chat Workspace":

    # Empty State with Production Suggestions
    if not st.session_state.messages_display:
        st.markdown("### 💬 **What can I help you accomplish today?**")
        st.markdown(f"Active User: `{user_id}` • Conversation Thread: `{thread_id}`")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            if st.button("💾 **Save User Preference**\n\nRemember laptop ownership & 4K monitor budget.", width="stretch"):
                st.session_state.pending_prompt = f"Remember that I own an Apple MacBook Air M3 and strictly need a 4K monitor under $600 with 90W USB-C charging."
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🧾 **Generate PDF Invoice**\n\nCreate official order invoice with coupon discount.", width="stretch"):
                st.session_state.pending_prompt = f"Generate an official order invoice PDF for customer {user_id} purchasing 1 Dell UltraSharp 27 with code TECHSAVINGS10."

        with col_s2:
            if st.button("🎯 **Recall & Recommend**\n\nRecommend a monitor tailored to saved preferences.", width="stretch"):
                st.session_state.pending_prompt = "Based on my owned laptop and saved budget, which monitor do you recommend?"
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💱 **Multi-Currency Pricing**\n\nConvert headphone prices to EUR, GBP, INR with tax.", width="stretch"):
                st.session_state.pending_prompt = "Convert the price of Sony WH-1000XM5 headphones into EUR, GBP, and INR with 8.5% sales tax."

        with col_s3:
            if st.button("🛡️ **Grounded Spec Check**\n\nVerify charging wattage & warranty with ChromaDB.", width="stretch"):
                st.session_state.pending_prompt = "Verify the exact charging wattage, contrast ratio, and warranty of the Dell UltraSharp 27 4K monitor using verified ground-truth."
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📚 **RAG Manual Troubleshooting**\n\nCheck MacBook dual monitor clamshell setup.", width="stretch"):
                st.session_state.pending_prompt = "How do I configure dual external monitors on MacBook Air M3 according to the official manual?"

        st.markdown("---")

    # Render Conversation Messages
    for msg in st.session_state.messages_display:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="⚡"):
                # Render tool summary chips
                if msg.get("tool_calls"):
                    chips_html = '<div style="margin-bottom: 8px;">'
                    for tc in msg["tool_calls"]:
                        name = tc.get("name", "Tool")
                        clean_name = name.replace("_", " ").title()
                        chips_html += f'<span class="tool-chip">✓ {clean_name}</span>'
                    chips_html += '</div>'
                    st.markdown(chips_html, unsafe_allow_html=True)
                
                st.markdown(msg["content"])
                
                # Expandable technical inspect
                if msg.get("tool_calls"):
                    with st.expander(f"⚙️ Execution Trace ({len(msg['tool_calls'])} tools)", expanded=False):
                        for tc in msg["tool_calls"]:
                            st.markdown(f"**Tool:** `{tc.get('name')}`")
                            st.json(tc.get("args"))

    # Chat Input Box
    user_typed = st.chat_input("Ask a grounded product question, recall saved preferences, or generate invoices...")
    prompt_to_execute = st.session_state.pending_prompt or user_typed
    st.session_state.pending_prompt = None

    if prompt_to_execute:
        st.session_state.messages_display.append({
            "role": "user",
            "content": prompt_to_execute,
            "tool_calls": [],
        })
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_to_execute)

        with st.chat_message("assistant", avatar="⚡"):
            # Staged Progressive Execution Status
            with st.status("⚡ Agent is processing...", expanded=True) as status_box:
                st.write("🔍 **Recalling user context** from ChromaDB persistent memory...")
                t_start = time.perf_counter()
                
                # Execute agent query
                res = agent_instance.invoke_with_trace(
                    query=prompt_to_execute,
                    user_id=user_id,
                    thread_id=thread_id,
                )
                
                st.write("🛡️ **Verifying specifications & executing tools**...")
                time.sleep(0.1)  # smooth visual transition
                status_box.update(label="✅ Response Generated", state="complete", expanded=False)

            answer = res.get("output", "No response generated.")
            tool_calls = res.get("tool_calls", [])
            telemetry = res.get("telemetry", {})

            # Store telemetry
            st.session_state.last_telemetry = telemetry

            # Render tool summary chips
            if tool_calls:
                chips_html = '<div style="margin-bottom: 8px;">'
                for tc in tool_calls:
                    name = tc.get("name", "Tool")
                    clean_name = name.replace("_", " ").title()
                    chips_html += f'<span class="tool-chip">✓ {clean_name}</span>'
                chips_html += '</div>'
                st.markdown(chips_html, unsafe_allow_html=True)

            st.markdown(answer)

            if tool_calls:
                with st.expander(f"⚙️ Execution Trace ({len(tool_calls)} tools)", expanded=False):
                    for tc in tool_calls:
                        st.markdown(f"**Tool:** `{tc.get('name')}`")
                        st.json(tc.get("args"))

            st.session_state.messages_display.append({
                "role": "assistant",
                "content": answer,
                "tool_calls": tool_calls,
                "telemetry": telemetry,
            })
            st.rerun()


# =============================================================
# VIEW 2: MEMORY EXPLORER
# =============================================================
elif st.session_state.active_view == "🧠 Memory Explorer":
    st.markdown("### 🧠 **ChromaDB Long-Term Memory Explorer**")
    st.caption(f"Persisted facts stored for user `{user_id}` on disk in `./data/chroma_db`.")

    with st.container(border=True):
        st.markdown("##### ➕ Add Preference to Memory Store")
        c_in, c_btn = st.columns([4, 1])
        with c_in:
            manual_pref = st.text_input("Fact / Preference", placeholder="e.g. User prefers midnight color and requires 90W USB-C charging.", label_visibility="collapsed")
        with c_btn:
            if st.button("Save Memory", width="stretch", type="primary"):
                if manual_pref:
                    chroma_conn.save_user_memory(user_id=user_id, memory_fact=manual_pref)
                    st.success("Preference persisted to ChromaDB!")
                    st.rerun()

    st.markdown("##### Active User Memories")
    user_memories = chroma_conn.recall_user_memories(user_id=user_id, n_results=10)
    if user_memories:
        for idx, m in enumerate(user_memories):
            st.markdown(f"""
            <div class="memory-item">
                <div style="font-weight: 700; color: #F5F7FA; margin-bottom: 4px;">Memory #{idx+1}</div>
                <div style="color: #CBD5E1; font-size: 0.9rem; margin-bottom: 6px;">{m['memory']}</div>
                <div style="font-size: 0.75rem; color: #64748B;">🏷️ Category: <code>{m['category']}</code> • 🕒 {m.get('created_at', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"No stored memories for `{user_id}` yet. Talk to the assistant in chat to save facts automatically!")


# =============================================================
# VIEW 3: GROUNDING LAB
# =============================================================
elif st.session_state.active_view == "🛡️ Grounding Lab":
    st.markdown("### 🛡️ **ChromaDB Anti-Hallucination Grounding Lab**")
    st.caption(f"Search across **{chroma_conn.kb_collection.count()} verified technical documents** used for strict grounding.")

    search_claim = st.text_input("Verify Technical Specification or Search Ground Truth", value="Dell UltraSharp 27 4K IPS Black 90W USB-C")
    if search_claim:
        results = chroma_conn.verify_ground_truth(search_claim, n_results=4)
        for idx, r in enumerate(results):
            with st.container(border=True):
                dist = r.get("relevance_distance", 0.0)
                meta = r.get("metadata", {})
                st.markdown(f"##### 📄 {meta.get('name', meta.get('title', 'Verified Source'))} • `Distance: {dist}`")
                st.markdown(f"**Type:** `{meta.get('type')}`")
                st.code(r["content"], language="text")


# =============================================================
# VIEW 4: PRODUCT CATALOG
# =============================================================
elif st.session_state.active_view == "📦 Product Catalog":
    st.markdown("### 📦 **Verified Product Catalog**")
    st.caption("Real-time inventory database queried by the Catalog Plugin.")

    cat_filter = st.selectbox("Filter Category", ["All Categories", "Laptops", "Monitors", "Audio", "Smartphones", "Smartwatches"])
    df = db_conn.products_df
    if cat_filter != "All Categories":
        df = df[df["category"] == cat_filter]

    st.dataframe(
        df,
        width="stretch",
        column_config={
            "price_usd": st.column_config.NumberColumn("Price (USD)", format="$%.2f"),
            "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
            "in_stock": st.column_config.CheckboxColumn("In Stock"),
        },
    )


# =============================================================
# VIEW 5: INVOICE DOCUMENT HUB
# =============================================================
elif st.session_state.active_view == "📄 Invoice Document Hub":
    st.markdown("### 📄 **Invoice Document Center**")
    st.caption("Official customer PDF invoices generated with `fpdf2`.")

    inv_dir = Path("invoices")
    if inv_dir.exists():
        pdf_list = sorted(list(inv_dir.glob("*.pdf")), reverse=True)
        if pdf_list:
            for pf in pdf_list:
                with st.container(border=True):
                    c_info, c_dl = st.columns([3, 1])
                    with c_info:
                        st.markdown(f"📄 **{pf.name}**")
                        st.caption(f"Size: {pf.stat().st_size} bytes • Generated via PDFConnector")
                    with c_dl:
                        with open(pf, "rb") as f:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=f.read(),
                                file_name=pf.name,
                                mime="application/pdf",
                                width="stretch",
                            )
        else:
            st.info("No invoices created yet. Ask the assistant in chat to generate an invoice!")
    else:
        st.info("Invoices will appear here once generated.")
