# 🛍️ Agent 01: Product Query & Shopping Assistant

An intelligent, enterprise-grade Product Query AI Agent with **ChromaDB Persistent Memory**, **LangGraph Session Checkpointing**, and **Multi-Tool Plugins**.

---

## 🌟 Key Features

- ⚡ **Groq & Google Gemini Support**: Ultra-fast tool-calling inference with automatic rate-limit fallbacks.
- 🧠 **ChromaDB Long-Term Memory**: Stores customer setup, owned hardware, and budget limits across sessions on disk (`./data/chroma_db`).
- 🛡️ **Anti-Hallucination Grounding**: Fact-checks and grounds specifications against verified documentation in ChromaDB.
- 🔌 **5 Modular Work Plugins**:
  - `CatalogPlugin`: Product lookups and real-time inventory count.
  - `RAGSupportPlugin`: User manuals, setup guides, and troubleshooting steps.
  - `FinancePlugin`: Currency conversions (EUR, GBP, INR, JPY, CAD) & tax calculation.
  - `InvoicePlugin`: Official downloadable PDF invoices via `fpdf2`.
  - `MemoryPlugin`: Persistent memory storage and retrieval.
- 💾 **Session Thread Persistence**: Retains multi-turn conversation context via LangGraph checkpointer.

---

## 🚀 How to Run

### 1. Configure Environment
Copy `.env.example` to `.env` inside this folder or repository root:
```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Launch Streamlit Web UI
```powershell
$env:PYTHONPATH="src"
uv run streamlit run src/agentic_ai/app.py
```

### 3. Run in Python / Jupyter Notebook
Open **`product_query_agent_advanced.ipynb`** or run in Python:
```python
import sys
sys.path.insert(0, "src")

from agentic_ai.core import HighLevelAgent

agent = HighLevelAgent()

# Ask grounded questions
print(agent.ask("what is the price of wireless headphones."))
print(agent.ask("How do I enable dual external monitors on MacBook Air M3?"))
```
