"""
Database & Tabular Data Connector.
Provides structured SQL-like query operations over product catalogs, orders, and inventory tables.
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from agentic_ai.connectors.base import BaseConnector
from agentic_ai.products_data import PRODUCTS, DISCOUNTS


class DatabaseConnector(BaseConnector):
    """
    Connector for structured tabular and SQL data queries using Pandas DataFrames.
    """

    def __init__(self, name: str = "DatabaseConnector"):
        super().__init__(
            name=name,
            description="Connector for relational/tabular product catalogs, inventory, and orders."
        )
        self.products_df: Optional[pd.DataFrame] = None
        self.discounts_df: Optional[pd.DataFrame] = None

    def connect(self) -> bool:
        """Load tabular data into memory."""
        try:
            # Flatten specs and nested attributes into searchable DataFrame columns
            flattened = []
            for p in PRODUCTS:
                row = dict(p)
                specs = row.pop("specs", {})
                for k, v in specs.items():
                    row[f"spec_{k}"] = str(v)
                flattened.append(row)

            self.products_df = pd.DataFrame(flattened)
            self.discounts_df = pd.DataFrame(DISCOUNTS)
            self._is_connected = True
            return True
        except Exception as e:
            self._is_connected = False
            raise RuntimeError(f"Failed to initialize DatabaseConnector: {e}")

    def disconnect(self) -> None:
        self.products_df = None
        self.discounts_df = None
        self._is_connected = False

    def query_products(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Query products table using structured filters."""
        if not self.is_connected or self.products_df is None:
            self.connect()

        df = self.products_df.copy()

        if category:
            df = df[df["category"].str.contains(category, case=False, na=False)]
        if brand:
            df = df[df["brand"].str.contains(brand, case=False, na=False)]
        if max_price is not None:
            df = df[df["price"] <= float(max_price)]
        if min_rating is not None:
            df = df[df["rating"] >= float(min_rating)]
        if in_stock_only:
            df = df[df["stock"] > 0]

        # Convert back to clean records
        return df.to_dict(orient="records")

    def get_product_by_id_or_name(self, query: str) -> Optional[Dict[str, Any]]:
        """Find exact or close product record by ID or title."""
        if not self.is_connected:
            self.connect()

        q = query.strip().lower()
        for p in PRODUCTS:
            if p["id"].lower() == q or q in p["name"].lower():
                return p

        # Keyword match
        for p in PRODUCTS:
            if any(word in p["name"].lower() for word in q.split() if len(word) > 3):
                return p
        return None

    def get_inventory_status(self, product_id_or_name: str) -> Optional[Dict[str, Any]]:
        """Query real-time stock levels and warehouse distribution."""
        product = self.get_product_by_id_or_name(product_id_or_name)
        if not product:
            return None

        stock = product.get("stock", 0)
        return {
            "id": product["id"],
            "name": product["name"],
            "stock": stock,
            "status": "In Stock" if stock > 5 else ("Low Stock" if stock > 0 else "Out of Stock"),
            "warehouse": product.get("warehouse_location", "Primary Central Facility"),
            "transit_days": product.get("estimated_shipping_days", 2),
        }
