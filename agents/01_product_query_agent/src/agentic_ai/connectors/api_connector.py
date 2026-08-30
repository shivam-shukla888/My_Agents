"""
REST API & External Services Connector.
Provides currency exchange conversions, live carrier shipping quotes, and regional sales tax calculation.
"""

from typing import Any, Dict, Optional
from agentic_ai.connectors.base import BaseConnector

# Standard exchange rates relative to USD (base)
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "INR": 86.50,
    "CAD": 1.38,
    "JPY": 154.20,
    "AUD": 1.55,
}

# Regional Sales Tax percentages
STATE_TAX_RATES = {
    "CA": 0.0925,  # California
    "NY": 0.08875, # New York
    "TX": 0.0825,  # Texas
    "FL": 0.0700,  # Florida
    "IL": 0.0875,  # Illinois
    "DEFAULT": 0.075,
}


class RESTAPIConnector(BaseConnector):
    """
    Connector for external REST services (Currency exchange, Shipping carrier calculation, Tax calculator).
    """

    def __init__(self, name: str = "RESTAPIConnector"):
        super().__init__(
            name=name,
            description="Connector for external web APIs, currency rates, carrier shipping quotes, and tax estimation."
        )

    def connect(self) -> bool:
        self._is_connected = True
        return True

    def disconnect(self) -> None:
        self._is_connected = False

    def convert_currency(self, amount_usd: float, target_currency: str) -> Dict[str, Any]:
        """Convert a USD amount into a target currency."""
        curr = target_currency.upper().strip()
        rate = EXCHANGE_RATES.get(curr)

        if not rate:
            supported = list(EXCHANGE_RATES.keys())
            return {
                "status": "error",
                "message": f"Currency '{curr}' is not supported. Supported currencies: {', '.join(supported)}",
            }

        converted_amount = round(amount_usd * rate, 2)
        return {
            "status": "success",
            "base_currency": "USD",
            "amount_usd": amount_usd,
            "target_currency": curr,
            "exchange_rate": rate,
            "converted_amount": converted_amount,
            "formatted": f"{converted_amount:,.2f} {curr}",
        }

    def calculate_shipping_rates(
        self,
        weight_kg: float,
        destination_zip: str,
        urgency: str = "standard"
    ) -> Dict[str, Any]:
        """Calculate carrier options and rates for a given weight and destination."""
        urg = urgency.lower()
        if "express" in urg or "overnight" in urg:
            carrier = "FedEx Priority Overnight"
            days = 1
            rate = max(19.99, round(weight_kg * 12.5, 2))
        elif "two_day" in urg or "2-day" in urg or "fast" in urg:
            carrier = "UPS 2nd Day Air"
            days = 2
            rate = max(12.99, round(weight_kg * 7.5, 2))
        else:
            carrier = "USPS Ground Advantage"
            days = 3
            rate = 0.00 if weight_kg < 5.0 else max(7.99, round(weight_kg * 3.5, 2))

        return {
            "carrier": carrier,
            "destination_zip": destination_zip,
            "estimated_days": days,
            "shipping_cost_usd": rate,
            "is_free": rate == 0.00,
        }

    def calculate_sales_tax(self, subtotal: float, state_code: Optional[str] = None) -> Dict[str, Any]:
        """Calculate state sales tax."""
        state = (state_code or "DEFAULT").upper().strip()
        rate = STATE_TAX_RATES.get(state, STATE_TAX_RATES["DEFAULT"])
        tax_amount = round(subtotal * rate, 2)
        total = round(subtotal + tax_amount, 2)

        return {
            "state": state,
            "tax_rate_percent": round(rate * 100, 2),
            "subtotal_usd": subtotal,
            "tax_usd": tax_amount,
            "total_usd": total,
        }
