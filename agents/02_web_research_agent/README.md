# 🔍 Agent 02: Autonomous Web Research Agent

An autonomous web research and market intelligence agent with **Competitor Price Tracking**, **Review Synthesis**, and **Shared Vault Publishing**.

---

## 🌟 Key Features

- 🌐 **Web Search & Article Parsing**: Searches tech publications, benchmark reports, and review sites.
- 🏷️ **Competitor Price Tracking**: Compares live retail listings from Amazon, Best Buy, B&H Photo, and Walmart.
- 📝 **Executive Brief Generator**: Synthesizes multi-source research into clean, structured Markdown reports.
- 🔐 **Shared Vault Publishing**: Writes files to `shared/workspace/` with directory-traversal protection.
- 🤝 **Inter-Agent Collaboration**: Can consult Agent 01 (Product Catalog) and Agent 03 (Data Analyst).

---

## 🚀 Quick Start

### Run Streamlit App
```powershell
$env:PYTHONPATH="src;agents/02_web_research_agent/src;shared"
uv run streamlit run agents/02_web_research_agent/app.py
```

### Python API
```python
from research_agent.core.agent import WebResearchAgent

agent = WebResearchAgent()

# Competitor Price-Matching
print(agent.ask("Find competitor retail prices for the Apple MacBook Air M3."))

# Lab Reviews Synthesis
print(agent.ask("Search and summarize lab test rankings for the Sony WH-1000XM5."))
```
