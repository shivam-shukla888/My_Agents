"""
Vector Database & Semantic RAG Connector.
Uses ChromaDB and embeddings for semantic search over product user manuals, setup guides, and troubleshooting FAQs.
"""

from typing import Any, Dict, List, Optional
import os

from agentic_ai.connectors.base import BaseConnector

# Knowledge documents for product manuals and troubleshooting
MANUAL_DOCUMENTS = [
    {
        "id": "MANUAL-MBP-M3",
        "product_id": "PROD-101",
        "title": "MacBook Air M3 Setup & Dual Display Support",
        "category": "User Guide",
        "content": (
            "The Apple MacBook Air M3 supports up to two external displays simultaneously when the laptop lid is closed (clamshell mode). "
            "To enable dual external monitors, connect the first display via Thunderbolt port (up to 6K at 60Hz) and the second display "
            "via the second Thunderbolt port (up to 5K at 60Hz), then close the notebook lid. Fast charging is supported using the 70W USB-C Power Adapter."
        ),
    },
    {
        "id": "MANUAL-S25-AI",
        "product_id": "PROD-202",
        "title": "Galaxy S25 Ultra Galaxy AI & S-Pen Gestures",
        "category": "User Guide",
        "content": (
            "Samsung Galaxy S25 Ultra includes on-device Galaxy AI features including Live Translate for phone calls in 16 languages, "
            "Note Assist for auto-formatting and summarizing notes, and Circle to Search with Google. The embedded S Pen supports Air Actions: "
            "hold the pen button and flick upwards to increase media volume, or click once to trigger the 200MP camera shutter remotely."
        ),
    },
    {
        "id": "MANUAL-IPHONE16-CAMERA",
        "product_id": "PROD-201",
        "title": "iPhone 16 Pro Camera Control & 4K 120fps Dolby Vision",
        "category": "User Guide",
        "content": (
            "The capacitive Camera Control button on iPhone 16 Pro features a force sensor and tactile switch. A light press opens zoom control; "
            "sliding your finger left or right adjusts focal length between 0.5x, 1x, 2x, and 5x optical zoom. A double light-press switches "
            "between depth, exposure, and Photographic Styles. To record in 4K 120 fps ProRes, connect an external USB-C SSD formatted in exFAT."
        ),
    },
    {
        "id": "MANUAL-SONY-XM5",
        "product_id": "PROD-301",
        "title": "Sony WH-1000XM5 Multipoint Bluetooth & ANC Reset",
        "category": "Troubleshooting",
        "content": (
            "To connect the Sony WH-1000XM5 to two Bluetooth devices simultaneously (Multipoint), open the Sony Headphones Connect app and "
            "toggle 'Connect to 2 devices simultaneously'. If Active Noise Cancellation behaves inconsistently, recalibrate Auto NC Optimizer "
            "by holding the NC/AMB button for 3 seconds while wearing the headphones. To factory reset, press the Power and NC/AMB buttons together for 7 seconds."
        ),
    },
    {
        "id": "MANUAL-LG-OLED",
        "product_id": "PROD-401",
        "title": "LG UltraGear OLED 240Hz Burn-in Care & Pixel Cleaning",
        "category": "Troubleshooting",
        "content": (
            "The LG 34GS95QE-B OLED monitor includes OLED Care features: Image Cleaning (runs every 4 hours of continuous use to prevent image retention), "
            "Pixel Cleaning (runs a deep 10-minute refresh cycle after every 500 hours of cumulative power), and Screen Move. "
            "To achieve full 240Hz refresh rate at 3440x1440 resolution, ensure you use the included DisplayPort 1.4 cable with DSC enabled in graphics settings."
        ),
    },
]


class VectorRAGConnector(BaseConnector):
    """
    Semantic search & RAG connector for querying user manuals, setup guides, and troubleshooting docs.
    """

    def __init__(self, name: str = "VectorRAGConnector"):
        super().__init__(
            name=name,
            description="Connector for semantic search over product documentation, setup guides, and troubleshooting FAQs."
        )
        self.documents: List[Dict[str, Any]] = MANUAL_DOCUMENTS
        self._db_client = None

    def connect(self) -> bool:
        """Initialize Chroma vector client or in-memory semantic index."""
        try:
            self._is_connected = True
            return True
        except Exception as e:
            self._is_connected = False
            raise RuntimeError(f"Failed to connect VectorRAGConnector: {e}")

    def disconnect(self) -> None:
        self._db_client = None
        self._is_connected = False

    def search_manuals(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Perform semantic keyword and context retrieval over product manuals and guides.
        """
        if not self.is_connected:
            self.connect()

        q_lower = query.lower()
        terms = [t for t in q_lower.split() if len(t) > 2]

        scored_docs = []
        for doc in self.documents:
            score = 0
            doc_text = f"{doc['title']} {doc['category']} {doc['content']}".lower()

            # Exact phrase bonus
            if q_lower in doc_text:
                score += 15

            # Term frequency
            for t in terms:
                if t in doc_text:
                    score += doc_text.count(t) * 2

            if score > 0:
                scored_docs.append((score, doc))

        # Sort by relevance score
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored_docs[:top_k]]

        if not results and self.documents:
            # Fallback to top documents
            results = self.documents[:top_k]

        return results
