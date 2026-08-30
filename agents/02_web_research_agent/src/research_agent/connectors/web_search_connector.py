"""
Web Search & Market Intelligence Connector for Agent 02.
Provides search over tech publications, reviews, benchmarks, and competitor retail pricing.
"""

from typing import Any, Dict, List, Optional
import json

COMPETITOR_DATABASE = {
    "macbook air m3": [
        {"retailer": "Amazon", "price": 1049.00, "in_stock": True, "shipping": "Free Next-Day", "condition": "New"},
        {"retailer": "Best Buy", "price": 1099.00, "in_stock": True, "shipping": "Free 2-Day", "condition": "New (Includes AppleCare 3mo promo)"},
        {"retailer": "B&H Photo", "price": 1029.00, "in_stock": True, "shipping": "Free Standard", "condition": "New (No sales tax with Payboo card)"},
    ],
    "iphone 16 pro": [
        {"retailer": "Amazon", "price": 999.00, "in_stock": True, "shipping": "Free 2-Day", "condition": "New Unlocked"},
        {"retailer": "Best Buy", "price": 999.00, "in_stock": True, "shipping": "Same Day Pickup", "condition": "New (Carrier activation required)"},
        {"retailer": "Verizon", "price": 999.00, "in_stock": True, "shipping": "Free", "condition": "New ($830 trade-in promo)"},
    ],
    "samsung galaxy s25 ultra": [
        {"retailer": "Amazon", "price": 1199.00, "in_stock": True, "shipping": "Free 2-Day", "condition": "New (Includes $100 Amazon Gift Card promo)"},
        {"retailer": "Best Buy", "price": 1199.00, "in_stock": True, "shipping": "Free Next-Day", "condition": "New"},
        {"retailer": "Samsung Direct", "price": 1199.00, "in_stock": True, "shipping": "Free Express", "condition": "New (Double storage promo)"},
    ],
    "sony wh-1000xm5": [
        {"retailer": "Amazon", "price": 328.00, "in_stock": True, "shipping": "Free Next-Day", "condition": "New (Limited Deal)"},
        {"retailer": "Best Buy", "price": 348.00, "in_stock": True, "shipping": "Same Day Pickup", "condition": "New"},
        {"retailer": "Walmart", "price": 319.00, "in_stock": True, "shipping": "Free 2-Day", "condition": "New (Marketplace seller)"},
    ],
    "dell ultrasharp 27 4k": [
        {"retailer": "Amazon", "price": 539.00, "in_stock": True, "shipping": "Free 2-Day", "condition": "New"},
        {"retailer": "B&H Photo", "price": 549.00, "in_stock": True, "shipping": "Free Next-Day", "condition": "New"},
        {"retailer": "Dell Direct", "price": 549.00, "in_stock": True, "shipping": "Free Expedited", "condition": "New (3-yr Advanced Exchange)"},
    ],
}

TECH_ARTICLES = [
    {
        "url": "https://theverge.com/reviews/macbook-air-m3-review",
        "title": "Apple MacBook Air M3 Review: The Default Laptop for Almost Everyone",
        "author": "The Verge Tech Team",
        "summary": "The M3 MacBook Air delivers incredible single-core speed, silent fanless thermal design, and remarkable 18-hour battery longevity. Key upgrade is dual external monitor support with lid closed. Verdict: 9/10.",
        "tags": ["laptop", "apple", "m3", "review"]
    },
    {
        "url": "https://rtings.com/headphones/reviews/sony/wh-1000xm5-wireless",
        "title": "Sony WH-1000XM5 Wireless Headphones: In-Depth Lab Test & ANC Ranking",
        "author": "RTINGS Labs",
        "summary": "Industry-leading active noise cancellation (score 8.9/10). Sound profile is warm and punchy. Exceptional microphone clarity in noisy environments. 30 hours battery life measured in testing.",
        "tags": ["audio", "sony", "headphones", "anc", "review"]
    },
    {
        "url": "https://tomshardware.com/monitors/dell-u2723qe-review",
        "title": "Dell UltraSharp 27 4K USB-C Hub Monitor (U2723QE) Review: IPS Black Tested",
        "author": "Tom's Hardware Display Team",
        "summary": "The first monitor with LG IPS Black technology delivering true 2000:1 contrast ratio. Built-in 90W USB-C power delivery effortlessly powers MacBooks and laptops. Outstanding color accuracy (98% DCI-P3).",
        "tags": ["monitor", "dell", "4k", "ips-black", "review"]
    },
]


class WebSearchConnector:
    """
    Search and market intelligence connector for Agent 02.
    """

    def __init__(self):
        self._is_connected = True

    def search_articles(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search tech publications and review articles."""
        q = query.lower()
        results = []
        for art in TECH_ARTICLES:
            text = f"{art['title']} {art['summary']} {' '.join(art['tags'])}".lower()
            if any(term in text for term in q.split() if len(term) > 2):
                results.append(art)
        if not results:
            results = TECH_ARTICLES[:max_results]
        return results[:max_results]

    def get_competitor_prices(self, product_name: str) -> Dict[str, Any]:
        """Fetch competitor retail listings and deals."""
        p_name = product_name.lower().strip()
        matched_key = None
        for k in COMPETITOR_DATABASE:
            if k in p_name or p_name in k or any(w in k for w in p_name.split() if len(w) > 3):
                matched_key = k
                break

        if not matched_key:
            return {
                "status": "not_found",
                "message": f"No competitor pricing feeds found for '{product_name}'.",
                "available_tracked_products": list(COMPETITOR_DATABASE.keys()),
            }

        listings = COMPETITOR_DATABASE[matched_key]
        prices = [item["price"] for item in listings]
        return {
            "status": "success",
            "product": matched_key.title(),
            "lowest_market_price": min(prices),
            "average_market_price": round(sum(prices) / len(prices), 2),
            "listings": listings,
        }
