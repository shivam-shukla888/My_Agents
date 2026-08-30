"""
SQL & Relational Analytics Connector for Agent 03.
Initializes an in-memory SQLite database with e-commerce sales, revenue, and inventory metrics.
"""

import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd


class SQLDataConnector:
    """
    Manages SQLite database connection and runs analytical SQL queries.
    """

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._init_database()

    def _init_database(self) -> None:
        """Seed sample transactional data tables."""
        cursor = self.conn.cursor()

        # 1. Sales Orders Table
        cursor.execute("""
        CREATE TABLE sales_orders (
            order_id TEXT PRIMARY KEY,
            order_date TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            units_sold INTEGER,
            unit_price REAL,
            discount_amount REAL,
            net_revenue REAL,
            region TEXT
        )
        """)

        orders = [
            ("ORD-1001", "2026-08-01", "PROD-101", "Apple MacBook Air M3", "Laptops", 3, 1099.00, 164.85, 3132.15, "US-East"),
            ("ORD-1002", "2026-08-02", "PROD-201", "Apple iPhone 16 Pro", "Smartphones", 5, 999.00, 500.00, 4495.00, "US-West"),
            ("ORD-1003", "2026-08-05", "PROD-301", "Sony WH-1000XM5", "Audio", 8, 348.00, 240.00, 2544.00, "US-Central"),
            ("ORD-1004", "2026-08-10", "PROD-402", "Dell UltraSharp 27 4K", "Monitors", 4, 549.00, 219.60, 1976.40, "US-East"),
            ("ORD-1005", "2026-08-12", "PROD-202", "Samsung Galaxy S25 Ultra", "Smartphones", 6, 1199.00, 600.00, 6594.00, "US-Central"),
            ("ORD-1006", "2026-08-15", "PROD-101", "Apple MacBook Air M3", "Laptops", 4, 1099.00, 439.60, 3956.40, "US-West"),
            ("ORD-1007", "2026-08-18", "PROD-501", "Apple Watch Ultra 2", "Smartwatches", 2, 749.00, 0.00, 1498.00, "US-East"),
            ("ORD-1008", "2026-08-20", "PROD-303", "Apple AirPods Pro (2nd Gen)", "Audio", 12, 229.00, 150.00, 2598.00, "US-West"),
            ("ORD-1009", "2026-08-22", "PROD-401", "LG UltraGear 34 OLED", "Monitors", 2, 999.00, 199.80, 1798.20, "US-East"),
            ("ORD-1010", "2026-08-25", "PROD-102", "Dell XPS 14 (2024)", "Laptops", 3, 1499.00, 449.70, 4047.30, "US-Central"),
        ]

        cursor.executemany("""
        INSERT INTO sales_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, orders)

        # 2. Inventory Analytics Table
        cursor.execute("""
        CREATE TABLE inventory_analytics (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            current_stock INTEGER,
            daily_run_rate REAL,
            days_to_stockout INTEGER,
            profit_margin_pct REAL
        )
        """)

        inventory = [
            ("PROD-101", "Apple MacBook Air M3", "Laptops", 18, 1.4, 13, 24.5),
            ("PROD-102", "Dell XPS 14 (2024)", "Laptops", 7, 0.6, 12, 28.0),
            ("PROD-201", "Apple iPhone 16 Pro", "Smartphones", 35, 2.5, 14, 32.0),
            ("PROD-202", "Samsung Galaxy S25 Ultra", "Smartphones", 20, 1.8, 11, 30.5),
            ("PROD-301", "Sony WH-1000XM5", "Audio", 42, 2.2, 19, 38.0),
            ("PROD-402", "Dell UltraSharp 27 4K", "Monitors", 14, 1.1, 13, 29.0),
            ("PROD-501", "Apple Watch Ultra 2", "Smartwatches", 16, 0.9, 18, 35.0),
        ]

        cursor.executemany("""
        INSERT INTO inventory_analytics VALUES (?, ?, ?, ?, ?, ?, ?)
        """, inventory)

        self.conn.commit()

    def get_schema(self) -> Dict[str, List[str]]:
        """Return the schema of available SQL tables."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]

        schema = {}
        for tbl in tables:
            cursor.execute(f"PRAGMA table_info({tbl});")
            columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
            schema[tbl] = columns
        return schema

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute a read-only SQL query and return DataFrame records."""
        clean_sql = sql_query.strip().rstrip(";")
        # Security: Prevent destructive commands
        for forbidden in ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER"]:
            if forbidden in clean_sql.upper().split():
                return {
                    "status": "error",
                    "message": f"Security Error: Query contains forbidden modifying statement '{forbidden}'. Only SELECT queries are permitted.",
                }

        try:
            df = pd.read_sql_query(clean_sql, self.conn)
            return {
                "status": "success",
                "row_count": len(df),
                "columns": list(df.columns),
                "data": df.to_dict(orient="records"),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"SQL Syntax/Execution Error: {str(e)}",
            }
