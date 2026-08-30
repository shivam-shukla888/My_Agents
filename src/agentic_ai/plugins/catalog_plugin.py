"""
Catalog & Product Data Plugin.
Wraps DatabaseConnector to provide product querying, stock inspection, and detailed spec tools.
"""

import json
from typing import List, Optional
from langchain_core.tools import BaseTool, tool

from agentic_ai.plugins.registry import BasePlugin
from agentic_ai.connectors.db_connector import DatabaseConnector


class CatalogPlugin(BasePlugin):
    """
    Plugin for product catalog lookups, technical specifications, and inventory checks.
    """

    def __init__(self, db_connector: Optional[DatabaseConnector] = None, enabled: bool = True):
        super().__init__(
            name="CatalogPlugin",
            description="Enables querying the structured product catalog, tech specs, and stock levels.",
            enabled=enabled,
        )
        self.db = db_connector or DatabaseConnector()
        self.db.connect()

    def get_tools(self) -> List[BaseTool]:
        db = self.db

        @tool
        def get_product(product_name_or_id: str) -> str:
            """
            Retrieve full product information, price, specs, rating, and stock for a given product name or ID.
            (e.g., 'MacBook Air M3', 'iPhone 16 Pro', 'Sony WH-1000XM5', 'wireless headphones', 'PROD-101').

            Args:
                product_name_or_id: The title, brand, category, or ID of the product.

            Returns:
                JSON string with product details, specs, price, and stock.
            """
            product = db.get_product_by_id_or_name(product_name_or_id)
            if not product:
                # Try fallback query
                results = db.query_products(category=product_name_or_id)
                if results:
                    return json.dumps({
                        "status": "multiple_found",
                        "count": len(results),
                        "products": results[:3]
                    }, indent=2)
                return json.dumps({
                    "status": "not_found",
                    "message": f"Product '{product_name_or_id}' was not found in catalog."
                }, indent=2)

            return json.dumps({
                "status": "success",
                "product": product
            }, indent=2)

        @tool
        def search_catalog(
            query: str = "",
            category: Optional[str] = None,
            max_price: Optional[float] = None,
            min_rating: Optional[float] = None,
        ) -> str:
            """
            Filter products by category, maximum price budget, and minimum customer rating.

            Args:
                query: Optional search keyword.
                category: Category filter ('Laptops', 'Smartphones', 'Audio', 'Monitors', 'Smartwatches').
                max_price: Maximum price threshold in USD.
                min_rating: Minimum review rating (1.0 - 5.0).

            Returns:
                JSON list of matching products.
            """
            results = db.query_products(
                category=category,
                max_price=max_price,
                min_rating=min_rating,
                in_stock_only=False,
            )
            return json.dumps({
                "status": "success",
                "count": len(results),
                "products": results
            }, indent=2)

        @tool
        def check_warehouse_stock(product_name_or_id: str) -> str:
            """
            Check real-time warehouse inventory quantity, fulfillment center location, and transit days.

            Args:
                product_name_or_id: Product ID or title to check.

            Returns:
                JSON string with stock status and warehouse origin.
            """
            status = db.get_inventory_status(product_name_or_id)
            if not status:
                return json.dumps({"status": "not_found", "message": f"Product '{product_name_or_id}' not found."})
            return json.dumps({"status": "success", "inventory": status}, indent=2)

        return [get_product, search_catalog, check_warehouse_stock]
