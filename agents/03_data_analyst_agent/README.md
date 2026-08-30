# 📊 Agent 03: SQL & Tabular Data Analyst Agent

An autonomous Data Analyst agent that runs **read-only SQL queries**, calculates **revenue metrics**, computes **inventory stockout forecasting**, and generates **visual markdown charts**.

---

## 🌟 Key Features

- 🗄️ **Safe SQL Engine**: In-memory SQLite relational database populated with sales orders, customer transactions, and inventory turnover.
- 📊 **Visual Chart Generator**: Horizontal ASCII/Markdown bar charts and statistical aggregations.
- ⚠️ **Stockout Risk Predictor**: Identifies high-velocity inventory items at risk of running out within 14 days.
- 🔐 **Shared Vault Publishing**: Writes CSVs and markdown analysis briefs to `shared/workspace/`.
- 🤝 **Inter-Agent Collaboration**: Can consult Agent 01 (Product Catalog) and Agent 02 (Web Research).

---

## 🚀 Quick Start

### Run Streamlit App
```powershell
$env:PYTHONPATH="src;agents/03_data_analyst_agent/src;shared"
uv run streamlit run agents/03_data_analyst_agent/app.py
```

### Python API
```python
from analyst_agent.core.agent import DataAnalystAgent

agent = DataAnalystAgent()

# Category Revenue Query
print(agent.ask("What is our total net revenue and sales volume by product category?"))

# Stockout Risk Forecast
print(agent.ask("Which products are at risk of stockout within the next 14 days?"))
```
