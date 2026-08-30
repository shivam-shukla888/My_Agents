"""
Invoice & PDF Generation Plugin.
Wraps PDFConnector to generate formal order invoices, quotations, and receipts.
"""

import json
from typing import List, Optional
from langchain_core.tools import BaseTool, tool

from agentic_ai.plugins.registry import BasePlugin
from agentic_ai.connectors.pdf_connector import PDFConnector
from agentic_ai.connectors.db_connector import DatabaseConnector


class InvoicePlugin(BasePlugin):
    """
    Plugin for automated PDF invoice generation and purchase receipts using fpdf2.
    """

    def __init__(
        self,
        pdf_connector: Optional[PDFConnector] = None,
        db_connector: Optional[DatabaseConnector] = None,
        enabled: bool = True
    ):
        super().__init__(
            name="InvoicePlugin",
            description="Generates official PDF order invoices and purchase quotations using fpdf2.",
            enabled=enabled,
        )
        self.pdf = pdf_connector or PDFConnector()
        self.db = db_connector or DatabaseConnector()
        self.pdf.connect()
        self.db.connect()

    def get_tools(self) -> List[BaseTool]:
        pdf_conn = self.pdf
        db_conn = self.db

        @tool
        def generate_customer_invoice_pdf(
            customer_name: str,
            product_name_or_id: str,
            quantity: int = 1,
            discount_code: Optional[str] = None,
        ) -> str:
            """
            Generate an official downloadable PDF invoice for an order.

            Args:
                customer_name: Full name of the customer (e.g. 'John Doe').
                product_name_or_id: Product ID or title being ordered.
                quantity: Number of units (default 1).
                discount_code: Optional promo code to apply (e.g. 'SUMMERSALE15', 'TECHSAVINGS10').

            Returns:
                JSON string with invoice number, file path, and grand total.
            """
            product = db_conn.get_product_by_id_or_name(product_name_or_id)
            unit_price = product.get("price", 999.0) if product else 999.0
            prod_name = product.get("name", product_name_or_id) if product else product_name_or_id

            subtotal = unit_price * quantity
            discount_amt = 0.0

            if discount_code:
                code_upper = discount_code.upper()
                if "15" in code_upper:
                    discount_amt = round(subtotal * 0.15, 2)
                elif "10" in code_upper:
                    discount_amt = round(subtotal * 0.10, 2)
                elif "100" in code_upper:
                    discount_amt = 100.00
                elif "30" in code_upper:
                    discount_amt = 30.00

            items = [
                {
                    "name": prod_name,
                    "qty": quantity,
                    "price": unit_price,
                }
            ]

            result = pdf_conn.generate_invoice_pdf(
                customer_name=customer_name,
                items=items,
                discount_code=discount_code,
                discount_amount=discount_amt,
                shipping_cost=0.0,
                tax_amount=round((subtotal - discount_amt) * 0.075, 2),
            )

            return json.dumps(result, indent=2)

        return [generate_customer_invoice_pdf]
