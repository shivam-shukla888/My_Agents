"""
Agentic AI Package - High-Level Architecture with Connectors, Plugins & Tools.
"""

from agentic_ai.core.agent import HighLevelAgent
from agentic_ai.core.config import get_llm
from agentic_ai.plugins.registry import PluginRegistry, BasePlugin
from agentic_ai.plugins.catalog_plugin import CatalogPlugin
from agentic_ai.plugins.rag_support_plugin import RAGSupportPlugin
from agentic_ai.plugins.pricing_plugin import FinancePlugin
from agentic_ai.plugins.invoice_plugin import InvoicePlugin

from agentic_ai.connectors.base import BaseConnector
from agentic_ai.connectors.db_connector import DatabaseConnector
from agentic_ai.connectors.vector_connector import VectorRAGConnector
from agentic_ai.connectors.api_connector import RESTAPIConnector
from agentic_ai.connectors.pdf_connector import PDFConnector

from agentic_ai.product_query_agent import create_product_agent, run_product_query
from agentic_ai.tools import PRODUCT_TOOLS
from agentic_ai.products_data import PRODUCTS, DISCOUNTS

__all__ = [
    # High-level Agent & Config
    "HighLevelAgent",
    "get_llm",
    # Plugins & Registry
    "PluginRegistry",
    "BasePlugin",
    "CatalogPlugin",
    "RAGSupportPlugin",
    "FinancePlugin",
    "InvoicePlugin",
    # Connectors
    "BaseConnector",
    "DatabaseConnector",
    "VectorRAGConnector",
    "RESTAPIConnector",
    "PDFConnector",
    # Legacy / direct helpers
    "create_product_agent",
    "run_product_query",
    "PRODUCT_TOOLS",
    "PRODUCTS",
    "DISCOUNTS",
]
