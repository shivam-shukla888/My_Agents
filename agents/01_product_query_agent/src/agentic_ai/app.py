"""
Enterprise Streamlit Web Application for High-Level Agentic AI.
Features:
- Pluggable Connectors & Modular Work Plugins
- ChromaDB Persistent Long-Term Memory
- Anti-Hallucination Ground-Truth Verification
- Conversation Thread Persistence (Checkpointer)
- Multi-LLM Provider Switching (Groq & Gemini)
- PDF Invoice Generation & Downloads
"""

import os
import sys
from pathlib import Path

# Add src to python path
current_file = Path(__file__).resolve()
src_dir = current_file.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv

from agentic_ai.core import HighLevelAgent, get_llm
from agentic_ai.plugins import PluginRegistry, CatalogPlugin, RAGSupportPlugin, FinancePlugin, InvoicePlugin, MemoryPlugin
from agentic_ai.connectors import DatabaseConnector, VectorRAGConnector, RESTAPIConnector, PDFConnector, ChromaMemoryConnector
from agentic_ai.products_data import PRODUCTS, DISCOUNTS
from agentic_ai.connectors.vector_connector import MANUAL_DOCUMENTS

# Load environment variables
load_dotenv(current_file.parent / ".env")
load_dotenv(src_dir.parent / ".env")

# Page Configuration
st.set_page_config(
    page_title="Agentic AI: Memory & ChromaDB",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .badge-grounded {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .memory-card {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages_display" not in st.session_state:
    st.session_state.messages_display = [
        {
            "role": "assistant",
            "content": "👋 Welcome to the **Agentic AI System with ChromaDB & Persistent Memory**!\n\nI retain long-term user preferences across sessions and ground all answers using verified ChromaDB documents to prevent hallucinations.",
            "tool_calls": [],
        }
    ]
if "selected_query" not in st.session_state:
    st.session_state.selected_query = None

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ Orchestrator Setup")

    # User & Thread Persistence Controls
    st.subheader("👤 User Identity & Thread Session")
    user_id = st.text_input("Customer ID / Username", value="alex_smith", help="ChromaDB stores preferences under this user ID")
    thread_id = st.text_input("Conversation Thread ID", value="thread_session_1", help="LangGraph checkpointer maintains thread history")

    st.markdown("---")
    # LLM Provider & Model Selection
    provider = st.radio("LLM Provider", ["Groq (Fast)", "Google Gemini"], horizontal=True)
    
    if "Groq" in provider:
        selected_provider = "groq"
        model_choice = st.selectbox(
            "Model",
            options=["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"],
            index=0
        )
    else:
        selected_provider = "google"
        model_choice = st.selectbox(
            "Model",
            options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            index=0
        )

    temperature = st.slider("Temperature (0.0 = Strictest Grounding)", 0.0, 1.0, 0.0, 0.05)

    st.markdown("---")
    st.subheader("🧩 Work Plugins")
    enable_catalog = st.checkbox("📦 Catalog & Inventory Plugin", value=True)
    enable_rag = st.checkbox("📚 User Manuals RAG Plugin", value=True)
    enable_finance = st.checkbox("💱 Finance & Currency Plugin", value=True)
    enable_invoice = st.checkbox("📄 PDF Invoice Plugin", value=True)
    enable_memory = st.checkbox("🧠 ChromaDB Memory & Grounding Plugin", value=True)

    st.markdown("---")
    if st.button("🗑️ Clear Active Thread History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages_display = [
            {
                "role": "assistant",
                "content": f"👋 Thread `{thread_id}` reset! How can I assist you today, **{user_id}**?",
                "tool_calls": [],
            }
        ]
        st.rerun()


# Initialize Connectors
@st.cache_resource
def get_connectors():
    db = DatabaseConnector()
    rag = VectorRAGConnector()
    api = RESTAPIConnector()
    pdf = PDFConnector()
    chroma = ChromaMemoryConnector()
    for c in [db, rag, api, pdf, chroma]:
        c.connect()
    return db, rag, api, pdf, chroma

db_conn, rag_conn, api_conn, pdf_conn, chroma_conn = get_connectors()

def build_agent():
    registry = PluginRegistry()
    registry.register(CatalogPlugin(db_connector=db_conn, enabled=enable_catalog))
    registry.register(RAGSupportPlugin(vector_connector=rag_conn, enabled=enable_rag))
    registry.register(FinancePlugin(api_connector=api_conn, enabled=enable_finance))
    registry.register(InvoicePlugin(pdf_connector=pdf_conn, db_connector=db_conn, enabled=enable_invoice))
    registry.register(MemoryPlugin(chroma_connector=chroma_conn, enabled=enable_memory))
    
    llm = get_llm(provider=selected_provider, model_name=model_choice, temperature=temperature)
    agent = HighLevelAgent(llm=llm, registry=registry)
    agent.chroma_conn = chroma_conn
    return agent


# Main Tabs
tab_chat, tab_memory, tab_grounding, tab_catalog, tab_invoices = st.tabs([
    "💬 Assistant with Persistent Memory",
    "🧠 ChromaDB User Memories",
    "🛡️ Anti-Hallucination Grounding",
    "📦 Product Catalog",
    "📄 Invoices & Downloads"
])

# ================= TAB 1: Assistant =================
with tab_chat:
    col_hdr, col_badge = st.columns([3, 1])
    with col_hdr:
        st.markdown('<div class="main-header">🧠 Persistent Memory & Grounded Agent</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-header">Active User: <strong>{user_id}</strong> | Thread: <strong>{thread_id}</strong></div>', unsafe_allow_html=True)
    with col_badge:
        st.markdown('<br><span class="badge-grounded">🛡️ ChromaDB Grounding: ON</span>', unsafe_allow_html=True)

    # Quick suggestion buttons
    st.markdown("**💡 Quick Multi-Turn Actions:**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("💾 Save User Preference", use_container_width=True):
            st.session_state.selected_query = f"Remember that I own an Apple MacBook Air M3 and strictly need a 4K monitor under $600 with 90W USB-C charging."
    with c2:
        if st.button("🎯 Recall & Recommend", use_container_width=True):
            st.session_state.selected_query = "Based on my owned laptop and saved budget, which monitor do you recommend?"
    with c3:
        if st.button("🛡️ Grounded Spec Verification", use_container_width=True):
            st.session_state.selected_query = "Verify the exact charging wattage, contrast ratio, and warranty of the Dell UltraSharp 27 4K monitor using verified ground-truth."
    with c4:
        if st.button("🧾 Generate Invoice", use_container_width=True):
            st.session_state.selected_query = f"Generate an official order invoice PDF for customer {user_id} purchasing 1 Dell UltraSharp 27 with code TECHSAVINGS10."

    st.markdown("---")

    # Render Chat History
    for msg in st.session_state.messages_display:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if msg.get("tool_calls"):
                with st.expander(f"🔍 Tools Triggered ({len(msg['tool_calls'])})", expanded=False):
                    for tc in msg["tool_calls"]:
                        st.markdown(f"**Tool:** `{tc.get('name')}`")
                        st.json(tc.get("args"))

    # Chat Input
    user_input = st.chat_input("Ask a grounded product question or save customer preferences...")
    query_to_run = st.session_state.selected_query or user_input
    st.session_state.selected_query = None

    if query_to_run:
        st.session_state.messages_display.append({"role": "user", "content": query_to_run, "tool_calls": []})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query_to_run)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 Recalling user memories & verifying facts from ChromaDB..."):
                try:
                    agent = build_agent()
                    res = agent.invoke_with_trace(
                        question=query_to_run,
                        user_id=user_id,
                        thread_id=thread_id,
                    )
                    answer = res.get("output", "No response generated.")
                    tool_calls = res.get("tool_calls", [])

                    st.markdown(answer)

                    if tool_calls:
                        with st.expander(f"🔍 Tools Triggered ({len(tool_calls)})", expanded=False):
                            for tc in tool_calls:
                                st.markdown(f"**Tool:** `{tc.get('name')}`")
                                st.json(tc.get("args"))

                    st.session_state.messages_display.append({
                        "role": "assistant",
                        "content": answer,
                        "tool_calls": tool_calls,
                    })

                except Exception as err:
                    err_text = f"❌ **Error:** {err}"
                    st.error(err_text)
                    st.session_state.messages_display.append({
                        "role": "assistant",
                        "content": err_text,
                        "tool_calls": [],
                    })


# ================= TAB 2: ChromaDB Memories =================
with tab_memory:
    st.header(f"🧠 Long-Term Memories for '{user_id}' in ChromaDB")
    st.write("These user facts are stored persistently on disk in `./data/chroma_db` and recalled across conversation sessions.")
    
    # Manual Add Memory Box
    with st.expander("➕ Manually Add User Preference / Fact to ChromaDB"):
        new_fact = st.text_input("New Fact/Preference", placeholder="e.g. User prefers silver color and requires ANC headphones.")
        if st.button("Save to ChromaDB"):
            if new_fact:
                chroma_conn.save_user_memory(user_id=user_id, memory_fact=new_fact)
                st.success("Saved memory to persistent ChromaDB!")
                st.rerun()

    user_memories = chroma_conn.recall_user_memories(user_id=user_id, n_results=10)
    if user_memories:
        for idx, m in enumerate(user_memories):
            st.markdown(f"""
            <div class="memory-card">
                <strong>Memory #{idx+1}:</strong> {m['memory']}<br>
                <span style="font-size:0.75rem; color:#64748B;">Category: {m['category']} | Timestamp: {m.get('created_at', 'N/A')}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"No long-term memories stored yet for user '{user_id}'. You can tell the assistant in chat or add one above!")

    st.markdown("---")
    st.subheader("All Users in Memory Store")
    all_mems = chroma_conn.get_all_stored_memories()
    if all_mems:
        st.dataframe(all_mems, use_container_width=True)


# ================= TAB 3: Grounding Store =================
with tab_grounding:
    st.header("🛡️ ChromaDB Anti-Hallucination Ground-Truth Store")
    st.write(f"Contains **{chroma_conn.kb_collection.count()} verified documents** (hardware specs, warranties, compatibility notes, and user guides).")
    
    search_claim = st.text_input("Verify Claim / Search Ground Truth", value="Dell UltraSharp 27 4K IPS Black 90W USB-C")
    if search_claim:
        results = chroma_conn.verify_ground_truth(search_claim, n_results=3)
        for r in results:
            with st.expander(f"📄 Source: {r['metadata'].get('name', r['metadata'].get('title', 'Document'))} (Distance: {r['relevance_distance']})"):
                st.markdown(f"**Type:** `{r['metadata'].get('type')}`")
                st.text(r["content"])


# ================= TAB 4: Catalog =================
with tab_catalog:
    st.header("📦 Product Catalog")
    st.dataframe(db_conn.products_df, use_container_width=True)


# ================= TAB 5: Invoices =================
with tab_invoices:
    st.header("📄 Downloadable Invoices (PDFConnector)")
    invoice_dir = Path("invoices")
    if invoice_dir.exists():
        pdf_files = list(invoice_dir.glob("*.pdf"))
        if pdf_files:
            for pf in sorted(pdf_files, reverse=True):
                with open(pf, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download {pf.name}",
                        data=f.read(),
                        file_name=pf.name,
                        mime="application/pdf",
                    )
        else:
            st.info("No invoices created yet.")
    else:
        st.info("Invoices will appear here once generated.")
