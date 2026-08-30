"""
SQL & Tabular Analytics Plugin for Agent 03.
"""

import json
from typing import List, Optional
from langchain_core.tools import BaseTool, tool

from analyst_agent.connectors.sql_connector import SQLDataConnector
from analyst_agent.connectors.chart_connector import ChartEngineConnector
from shared.security import SecureWorkspaceVault


class AnalyticsPlugin:
    """
    Plugin providing tools for SQL queries, revenue visualization, stockout risk checks, and dataset export.
    """

    def __init__(
        self,
        sql_conn: Optional[SQLDataConnector] = None,
        chart_conn: Optional[ChartEngineConnector] = None,
        vault: Optional[SecureWorkspaceVault] = None,
    ):
        self.sql = sql_conn or SQLDataConnector()
        self.chart = chart_conn or ChartEngineConnector()
        self.vault = vault or SecureWorkspaceVault()

    def get_tools(self) -> List[BaseTool]:
        sql_c = self.sql
        chart_c = self.chart
        vault_c = self.vault

        @tool
        def get_database_schema() -> str:
            """
            Inspect the schema and columns of the analytics database (tables: 'sales_orders', 'inventory_analytics').

            Returns:
                JSON string with tables and column types.
            """
            schema = sql_c.get_schema()
            return json.dumps({"status": "success", "tables": schema}, indent=2)

        @tool
        def run_sql_query(sql_query: str) -> str:
            """
            Execute a read-only SQL query against transactional sales orders and inventory analytics.
            Examples:
            - 'SELECT category, SUM(net_revenue) as total_rev FROM sales_orders GROUP BY category ORDER BY total_rev DESC'
            - 'SELECT product_name, units_sold, net_revenue FROM sales_orders WHERE region = "US-East"'

            Args:
                sql_query: The SQL SELECT query string.

            Returns:
                JSON string with query results.
            """
            res = sql_c.execute_query(sql_query)
            return json.dumps(res, indent=2)

        @tool
        def generate_category_revenue_chart() -> str:
            """
            Generate a visual bar chart comparing net revenue across product categories.

            Returns:
                Markdown formatted visual bar chart.
            """
            res = sql_c.execute_query("""
                SELECT category, SUM(net_revenue) as total_rev, SUM(units_sold) as total_units
                FROM sales_orders
                GROUP BY category
                ORDER BY total_rev DESC
            """)
            if res["status"] != "success" or not res["data"]:
                return "Could not compute category revenue."

            chart_md = chart_c.generate_bar_chart(
                title="Revenue by Category (August 2026)",
                data_points=res["data"],
                label_key="category",
                value_key="total_rev",
                unit="$",
            )
            return chart_md

        @tool
        def check_stockout_risks() -> str:
            """
            Identify products with high turnover rates and impending stockout risks within 14 days.

            Returns:
                JSON string listing critical inventory items.
            """
            res = sql_c.execute_query("""
                SELECT product_name, category, current_stock, daily_run_rate, days_to_stockout, profit_margin_pct
                FROM inventory_analytics
                WHERE days_to_stockout <= 14
                ORDER BY days_to_stockout ASC
            """)
            return json.dumps(res, indent=2)

        @tool
        def save_data_insights_to_vault(filename: str, report_content: str) -> str:
            """
            Save an analytics report, CSV summary, or forecast into the shared workspace.

            Args:
                filename: Filename (e.g. 'august_sales_performance.md', 'inventory_forecast.csv').
                report_content: Text/CSV/Markdown content.

            Returns:
                Confirmation with file path.
            """
            res = vault_c.write_file(
                filename=filename,
                content=report_content,
                author_agent="03_data_analyst_agent",
            )
            return f"Data analysis report saved: {res['filename']} in shared vault ({res['size_bytes']} bytes)."

        return [
            get_database_schema,
            run_sql_query,
            generate_category_revenue_chart,
            check_stockout_risks,
            save_data_insights_to_vault,
        ]
