"""
Finance & Pricing Calculations Plugin.
High-efficiency multi-currency conversions and checkout tax calculations in a single tool call.
"""

import json
from typing import List, Optional, Union
from langchain_core.tools import BaseTool, tool

from agentic_ai.plugins.registry import BasePlugin
from agentic_ai.connectors.api_connector import RESTAPIConnector
from agentic_ai.products_data import DISCOUNTS


class FinancePlugin(BasePlugin):
    """
    Plugin for multi-currency conversions, pricing breakdowns, tax calculations, and discounts.
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
        def convert_currency_and_tax(
            amount_usd: float,
            target_currencies: Optional[str] = "EUR,GBP,INR",
            tax_rate_percent: Optional[float] = 8.5,
            state_code: Optional[str] = None,
        ) -> str:
            """
            Convert a USD price into one or multiple foreign currencies (e.g. 'EUR, GBP, INR, JPY')
            and calculate sales tax in a single deterministic operation.

            Args:
                amount_usd: Base price in USD (e.g. 399.99).
                target_currencies: Comma-separated currency codes (e.g. 'EUR,GBP,INR' or 'EUR').
                tax_rate_percent: Optional tax rate percentage (default 8.5%).
                state_code: Optional US state code for automatic tax rate lookup (e.g. 'CA', 'NY').

            Returns:
                JSON string with conversions for all requested currencies, tax breakdown, and totals.
            """
            tax_rate = tax_rate_percent if tax_rate_percent is not None else 8.5
            if state_code:
                tax_info = api.calculate_sales_tax(subtotal=amount_usd, state_code=state_code)
                tax_usd = tax_info["tax_usd"]
                tax_rate = tax_info["tax_rate_percent"]
            else:
                tax_usd = round(amount_usd * (tax_rate / 100.0), 2)

            total_usd = round(amount_usd + tax_usd, 2)

            # Parse target currencies
            curr_list = [c.strip().upper() for c in target_currencies.split(",") if c.strip()] if target_currencies else ["EUR", "GBP", "INR"]
            
            conversions = {}
            for c in curr_list:
                res = api.convert_currency(amount_usd=total_usd, target_currency=c)
                if res.get("status") == "success":
                    conversions[c] = {
                        "converted_total": res["converted_amount"],
                        "exchange_rate": res["exchange_rate"],
                        "formatted": res["formatted"],
                    }

            return json.dumps({
                "status": "success",
                "subtotal_usd": amount_usd,
                "tax_rate": f"{tax_rate}%",
                "tax_usd": tax_usd,
                "total_usd": total_usd,
                "multi_currency_totals": conversions,
            })

        @tool
        def lookup_promotional_discounts(category_or_product: Optional[str] = None) -> str:
            """
            Look up active promo discount codes and coupons (e.g. TECHSAVINGS10, SUMMERSALE15).
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

            return json.dumps({
                "status": "success",
                "active_coupons": matched or DISCOUNTS[:2]
            })

        return [convert_currency_and_tax, lookup_promotional_discounts]
