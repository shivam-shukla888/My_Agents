"""
Base Connector interface for Agentic AI system.
Provides consistent lifecycle, status inspection, and error handling for external connectors.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseConnector(ABC):
    """
    Abstract base class for all data and service connectors.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Initialize the connection to the underlying resource."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Gracefully release or close the connection."""
        pass

    @property
    def is_connected(self) -> bool:
        """Return True if the connector is ready to process queries."""
        return self._is_connected

    def get_status(self) -> Dict[str, Any]:
        """Return diagnostic status information about this connector."""
        return {
            "name": self.name,
            "description": self.description,
            "connected": self.is_connected,
        }
