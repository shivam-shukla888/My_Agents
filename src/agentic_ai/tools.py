"""
Custom LangChain Tools for the Product Query Agent.
Equips the agent with catalog search, detailed spec retrieval, product comparison,
inventory & shipping checks, and discount lookups.
"""

import json
from typing import List, Optional
from langchain_core.tools import tool
from agentic_ai.products_data import PRODUCTS, DISCOUNTS


@tool
def search_products(query: str = "", category: Optional[str] = None, max_price: Optional[float] = None) -> str:
    """
    Search products in the catalog using keywords, category filter, or a maximum price budget.

    Args:
        query: Keywords to search for in product title, brand, or description (e.g. 'laptop', 'OLED', 'titanium', 'Sony').
        category: Optional category filter (e.g. 'Laptops', 'Smartphones', 'Audio', 'Monitors', 'Smartwatches').
        max_price: Optional maximum budget/price in USD (e.g. 1000.0).

    Returns:
        A JSON string summary of matching products with their ID, name, brand, price, rating, and stock.
    """
    q = query.strip().lower() if query else ""
    cat = category.strip().lower() if category else None

    results = []
    for prod in PRODUCTS:
        # Category filter
        if cat and cat not in prod["category"].lower():
            continue

        # Price filter
        if max_price is not None and prod["price"] > float(max_price):
            continue

        # Keyword match
        if q:
            matchable_text = f"{prod['name']} {prod['brand']} {prod['category']} {prod['description']} {' '.join(str(v) for v in prod['specs'].values())}".lower()
            if q not in matchable_text:
                # Check individual words
                words = [w for w in q.split() if len(w) > 2]
                if not any(w in matchable_text for w in words):
                    continue

        results.append({
            "id": prod["id"],
            "name": prod["name"],
            "brand": prod["brand"],
            "category": prod["category"],
            "price": f"${prod['price']:.2f}",
            "rating": f"{prod['rating']}/5 ({prod['reviews_count']} reviews)",
            "stock": f"{prod['stock']} units available",
            "highlight": prod["description"][:120] + "...",
        })

    if not results:
        return json.dumps({
            "status": "not_found",
            "message": f"No products found matching query='{query}', category='{category}', max_price='{max_price}'."
        }, indent=2)

    return json.dumps({
        "status": "success",
        "total_results": len(results),
        "products": results
    }, indent=2)


@tool
def get_product_details(product_name_or_id: str) -> str:
    """
    Retrieve full technical specifications, pricing, warranty, rating, and description for a specific product.

    Args:
        product_name_or_id: The ID (e.g., 'PROD-101') or name (e.g., 'MacBook Air M3', 'Galaxy S25 Ultra') of the product.

    Returns:
        JSON string containing comprehensive product details.
    """
    target = product_name_or_id.strip().lower()
    
    matched_product = None
    for prod in PRODUCTS:
        if prod["id"].lower() == target or target in prod["name"].lower():
            matched_product = prod
            break

    if not matched_product:
        # Fuzzy fallback
        for prod in PRODUCTS:
            if any(w in prod["name"].lower() for w in target.split() if len(w) > 3):
                matched_product = prod
                break

    if not matched_product:
        return json.dumps({
            "status": "not_found",
            "message": f"No product found matching '{product_name_or_id}'. Try search_products to see available items."
        }, indent=2)

    return json.dumps({
        "status": "success",
        "product": matched_product
    }, indent=2)


@tool
def compare_products(product_names_or_ids: str) -> str:
    """
    Compare 2 or more products side-by-side on price, specs, ratings, and features.

    Args:
        product_names_or_ids: Comma-separated list or names of products to compare (e.g. 'iPhone 16 Pro, Samsung Galaxy S25 Ultra').

    Returns:
        JSON string containing structured side-by-side comparison.
    """
    names = [n.strip() for n in product_names_or_ids.split(",") if n.strip()]
    if len(names) < 2:
        return json.dumps({
            "status": "error",
            "message": "Please provide at least 2 product names or IDs separated by commas to compare."
        }, indent=2)

    compared = []
    for item in names:
        target = item.lower()
        matched = None
        for prod in PRODUCTS:
            if prod["id"].lower() == target or target in prod["name"].lower() or any(w in prod["name"].lower() for w in target.split() if len(w) > 3):
                matched = prod
                break
        if matched:
            compared.append({
                "id": matched["id"],
                "name": matched["name"],
                "brand": matched["brand"],
                "price": f"${matched['price']:.2f}",
                "rating": f"{matched['rating']}/5 ({matched['reviews_count']} reviews)",
                "specs": matched["specs"],
                "warranty": matched["warranty"],
                "stock": f"{matched['stock']} units",
            })
        else:
            compared.append({
                "query": item,
                "status": "not_found"
            })

    return json.dumps({
        "status": "success",
        "comparison_count": len(compared),
        "products": compared
    }, indent=2)


@tool
def check_inventory_and_delivery(product_name_or_id: str, postal_code: Optional[str] = None) -> str:
    """
    Check real-time stock availability, warehouse location, and estimated delivery dates for a product.

    Args:
        product_name_or_id: Product ID or name to check inventory for.
        postal_code: Optional destination ZIP/postal code to calculate delivery timing and fees.

    Returns:
        JSON string with stock status, warehouse origin, estimated transit time, and shipping cost.
    """
    target = product_name_or_id.strip().lower()
    matched = None
    for prod in PRODUCTS:
        if prod["id"].lower() == target or target in prod["name"].lower():
            matched = prod
            break

    if not matched:
        return json.dumps({
            "status": "not_found",
            "message": f"Product '{product_name_or_id}' was not found in our catalog."
        }, indent=2)

    stock_status = "In Stock" if matched["stock"] > 5 else ("Low Stock" if matched["stock"] > 0 else "Out of Stock")
    
    # Calculate delivery estimate
    base_days = matched.get("estimated_shipping_days", 2)
    shipping_cost = 0.00 if matched["price"] > 100 else 9.99

    return json.dumps({
        "status": "success",
        "product_id": matched["id"],
        "product_name": matched["name"],
        "stock_count": matched["stock"],
        "stock_status": stock_status,
        "warehouse": matched.get("warehouse_location", "Primary Warehouse"),
        "destination_zip": postal_code or "Standard US Delivery",
        "estimated_delivery_days": f"{base_days} business days",
        "shipping_fee": f"${shipping_cost:.2f}" if shipping_cost > 0 else "FREE Standard Shipping",
        "express_shipping_available": True,
    }, indent=2)


@tool
def get_active_discounts(category_or_product: Optional[str] = None) -> str:
    """
    Retrieve active promotional discounts, coupon codes, and special trade-in offers.

    Args:
        category_or_product: Optional category (e.g. 'Laptops', 'Audio') or product name to filter applicable deals.

    Returns:
        JSON string listing valid coupon codes, discounts, and minimum spend requirements.
    """
    cat = category_or_product.strip().lower() if category_or_product else None
    valid_deals = []

    for deal in DISCOUNTS:
        if cat:
            categories_match = any(c.lower() in cat or cat in c.lower() for c in deal["valid_categories"])
            if not categories_match and cat not in deal["description"].lower():
                continue
        valid_deals.append(deal)

    if not valid_deals:
        return json.dumps({
            "status": "success",
            "message": f"No specific deals found for '{category_or_product}', but you can use general storewide coupons.",
            "available_deals": DISCOUNTS
        }, indent=2)

    return json.dumps({
        "status": "success",
        "total_active_coupons": len(valid_deals),
        "coupons": valid_deals
    }, indent=2)


# List of all available product query tools
PRODUCT_TOOLS = [
    search_products,
    get_product_details,
    compare_products,
    check_inventory_and_delivery,
    get_active_discounts,
]
