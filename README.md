<<<<<<< HEAD
# My_Agents
=======
# 🤖 My Agents - Multi-Agent AI Collection

Welcome to **My Agents**! A modular monorepo collection of production-ready, domain-specialized Agentic AI applications built with **LangChain**, **Groq**, **Google Gemini**, **ChromaDB**, and **Streamlit**.

---

## 📂 Repository Structure

Each agent is organized in its own isolated directory under `agents/` with dedicated tools, connectors, prompts, notebooks, and user interfaces:

```
My_Agents/
├── README.md                              # Main Hub & Documentation (You are here)
├── pyproject.toml                         # Shared dependencies & environment
├── .gitignore                             # Excludes secrets, API keys, and cache
├── .env.example                           # Global API keys template
│
└── agents/
    │
    ├── 01_product_query_agent/            # 🛍️ Agent 1: Product Query & Shopping Assistant
    │   ├── README.md                      # Agent 1 Documentation
    │   ├── .env.example                   # Local environment template
    │   ├── product_query_agent_advanced.ipynb # Interactive demo notebook
    │   ├── product_query_agent_demo.ipynb # Getting started notebook
    │   └── src/
    │       └── agentic_ai/
    │           ├── core/                  # HighLevelAgent orchestrator & multi-LLM config
    │           ├── connectors/            # DB, ChromaDB, REST API, PDF Engine
    │           ├── plugins/               # Catalog, Manuals RAG, Finance, Invoice, Memory
    │           ├── products_data.py       # Verified catalog dataset & discounts
    │           └── app.py                 # Interactive Streamlit Web UI
    │
    ├── 02_web_research_agent/             # 🔍 Agent 2: Autonomous Web Research (Coming Soon)
    │   └── README.md
    │
    └── 03_data_analyst_agent/             # 📊 Agent 3: SQL & Data Analyst Agent (Coming Soon)
        └── README.md
```

---

## 🌟 Available Agents

| # | Agent Name | Domain / Work | Key Tech | Link |
|---|---|---|---|---|
| **01** | **Product Query & Shopping Assistant** | E-Commerce, ChromaDB Long-Term Memory, Anti-Hallucination Grounding, PDF Invoices | LangChain, Groq, ChromaDB, fpdf2, Streamlit | [Explore Agent 01](./agents/01_product_query_agent/) |
| **02** | **Web Research Agent** | Deep multi-step internet research & synthesis | LangGraph, Tavily, Groq | [Explore Agent 02](./agents/02_web_research_agent/) |
| **03** | **SQL & Data Analyst Agent** | Text-to-SQL, tabular data analysis, charts | SQL Agent, Pandas, Plotly | [Explore Agent 03](./agents/03_data_analyst_agent/) |

---

## 🚀 How to Add a New Agent to this Repository

Adding a new agent is super simple:

1. Create a new folder under `agents/` (e.g. `agents/04_customer_support_agent/`).
2. Add your agent code, custom tools, notebooks, and UI.
3. Add a dedicated `README.md` inside your agent folder.
4. Link your new agent in the table above!

---

## 🛠️ Global Quick Start

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/shivam-shukla888/My_Agents.git
cd My_Agents
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your API keys (`GROQ_API_KEY`, `GOOGLE_API_KEY`).

### 3. Run Agent 01 (Product Query Assistant)
```powershell
$env:PYTHONPATH="agents/01_product_query_agent/src"
uv run streamlit run agents/01_product_query_agent/src/agentic_ai/app.py
```
>>>>>>> c563f95 (feat: Add Multi-Agent repository architecture with Agent 01 Product Query Assistant)
