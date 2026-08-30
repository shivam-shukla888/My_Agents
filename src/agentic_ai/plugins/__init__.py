"""
Plugins and Tool Registry Layer for Agentic AI.
"""

from agentic_ai.plugins.registry import BasePlugin, PluginRegistry
from agentic_ai.plugins.catalog_plugin import CatalogPlugin
from agentic_ai.plugins.rag_support_plugin import RAGSupportPlugin
from agentic_ai.plugins.pricing_plugin import FinancePlugin
from agentic_ai.plugins.invoice_plugin import InvoicePlugin
from agentic_ai.plugins.memory_plugin import MemoryPlugin

__all__ = [
    "BasePlugin",
    "PluginRegistry",
    "CatalogPlugin",
    "RAGSupportPlugin",
    "FinancePlugin",
    "InvoicePlugin",
    "MemoryPlugin",
]
