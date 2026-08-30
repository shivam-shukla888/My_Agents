"""
Finance & Pricing Calculations Plugin.
Wraps RESTAPIConnector to provide currency conversions, tax estimation, and promotional discounts.
"""

import json
from typing import List, Optional
from langchain_core.tools import BaseTool, tool

from agentic_ai.plugins.registry import BasePlugin
from agentic_ai.connectors.api_connector import RESTAPIConnector
from agentic_ai.products_data import DISCOUNTS


class FinancePlugin(BasePlugin):
    """
    Plugin for currency conversions, multi-region pricing, tax calculation, and discounts.
    """

    def __init__(self, api_connector: Optional[RESTAPIConnector] = None, enabled: bool = True):
        super().__init__(
            name="FinancePlugin",
            description="Provides real-time currency conversions (EUR, GBP, INR, JPY, CAD), sales tax, and discount lookups.",
            enabled=enabled,
        )
        self.api = api_connector or RESTAPIConnector()
        self.api.connect()

    def get_tools(self) -> List[BaseTool]:
        api = self.api

        @tool
        def convert_currency_price(amount_usd: float, target_currency: str) -> str:
            """
            Convert a USD price into foreign currencies such as EUR, GBP, INR, CAD, JPY, or AUD.

            Args:
                amount_usd: The price in USD to convert (e.g. 1099.00).
                target_currency: Target 3-letter currency code (e.g. 'EUR', 'GBP', 'INR', 'JPY', 'CAD', 'AUD').

            Returns:
                JSON string with exchange rate and converted amount.
            """
            result = api.convert_currency(amount_usd=amount_usd, target_currency=target_currency)
            return json.dumps(result, indent=2)

        @tool
        def calculate_checkout_totals(
            subtotal_usd: float,
            state_code: Optional[str] = None,
            destination_zip: Optional[str] = "90210",
            shipping_urgency: str = "standard",
        ) -> str:
            """
            Calculate estimated sales tax, carrier shipping fees, and final grand total for checkout.

            Args:
                subtotal_usd: Subtotal price in USD.
                state_code: 2-letter US state code for sales tax (e.g. 'CA', 'NY', 'TX', 'FL', 'IL').
                destination_zip: Destination ZIP code.
                shipping_urgency: 'standard', 'two_day', or 'express'.

            Returns:
                JSON string with subtotal, tax, shipping, and grand total.
            """
            tax_info = api.calculate_sales_tax(subtotal=subtotal_usd, state_code=state_code)
            shipping_info = api.calculate_shipping_rates(
                weight_kg=2.0,
                destination_zip=destination_zip or "90210",
                urgency=shipping_urgency
            )

            shipping_cost = shipping_info["shipping_cost_usd"]
            tax_cost = tax_info["tax_usd"]
            grand_total = round(subtotal_usd + tax_cost + shipping_cost, 2)

            return json.dumps({
                "subtotal_usd": subtotal_usd,
                "state": tax_info["state"],
                "sales_tax_usd": tax_cost,
                "tax_rate": f"{tax_info['tax_rate_percent']}%",
                "carrier": shipping_info["carrier"],
                "estimated_delivery_days": shipping_info["estimated_days"],
                "shipping_fee_usd": shipping_cost,
                "grand_total_usd": grand_total,
            }, indent=2)

        @tool
        def lookup_promotional_discounts(category_or_product: Optional[str] = None) -> str:
            """
            Look up active promotional discount coupon codes and rebates.

            Args:
                category_or_product: Optional category or product name to filter applicable deals.

            Returns:
                JSON string with valid coupons and minimum spend.
            """
            cat = category_or_product.lower().strip() if category_or_product else None
            matched = []
            for d in DISCOUNTS:
                if cat:
                    if any(c.lower() in cat or cat in c.lower() for c in d["valid_categories"]):
                        matched.append(d)
                    elif cat in d["description"].lower():
                        matched.append(d)
                else:
                    matched.append(d)

            if not matched:
                matched = DISCOUNTS

            return json.dumps({
                "status": "success",
                "active_coupons": matched
            }, indent=2)

        return [convert_currency_price, calculate_checkout_totals, lookup_promotional_discounts]
