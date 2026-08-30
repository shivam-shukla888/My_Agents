"""
ChromaDB Persistent Vector & Long-Term Memory Connector.
Provides:
1. Ground-truth knowledge collection to strictly ground model responses and reduce hallucinations.
2. Persistent user memory collection to remember customer preferences, past orders, and owned devices.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from agentic_ai.connectors.base import BaseConnector
from agentic_ai.products_data import PRODUCTS, DISCOUNTS
from agentic_ai.connectors.vector_connector import MANUAL_DOCUMENTS


class ChromaMemoryConnector(BaseConnector):
    """
    Persistent ChromaDB connector managing both Ground-Truth Knowledge and User Long-Term Memories.
    """

    def __init__(
        self,
        persist_dir: str = "data/chroma_db",
        name: str = "ChromaMemoryConnector"
    ):
        super().__init__(
            name=name,
            description="Persistent ChromaDB storage for anti-hallucination ground-truth knowledge and cross-session user memory."
        )
        self.persist_dir = Path(persist_dir)
        self.client: Optional[chromadb.PersistentClient] = None
        self.kb_collection: Optional[Any] = None
        self.memory_collection: Optional[Any] = None

    def connect(self) -> bool:
        """Initialize persistent ChromaDB client and collections."""
        try:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )

            # 1. Ground-Truth Knowledge Base Collection (for reducing hallucinations)
            self.kb_collection = self.client.get_or_create_collection(
                name="product_ground_truth",
                metadata={"description": "Verified ground-truth product specifications and manuals"}
            )

            # 2. Long-Term User Memory Collection (for cross-session preferences)
            self.memory_collection = self.client.get_or_create_collection(
                name="user_long_term_memories",
                metadata={"description": "Persistent customer preferences, owned devices, and history"}
            )

            # Populate knowledge base if collection is empty
            if self.kb_collection.count() == 0:
                self._seed_ground_truth_kb()

            self._is_connected = True
            return True
        except Exception as e:
            self._is_connected = False
            raise RuntimeError(f"Failed to connect ChromaMemoryConnector: {e}")

    def disconnect(self) -> None:
        self.client = None
        self.kb_collection = None
        self.memory_collection = None
        self._is_connected = False

    def _seed_ground_truth_kb(self) -> None:
        """Seed verified product facts and manual docs into ChromaDB."""
        docs = []
        metadatas = []
        ids = []

        # Ingest structured product ground truth
        for prod in PRODUCTS:
            spec_str = ", ".join(f"{k}: {v}" for k, v in prod["specs"].items())
            doc_text = (
                f"PRODUCT FACT SHEET: {prod['name']} ({prod['id']})\n"
                f"Brand: {prod['brand']} | Category: {prod['category']}\n"
                f"Official Price: ${prod['price']:.2f} USD\n"
                f"Rating: {prod['rating']}/5 based on {prod['reviews_count']} reviews\n"
                f"Warehouse Stock: {prod['stock']} units ({prod.get('warehouse_location', 'Primary')})\n"
                f"Specifications: {spec_str}\n"
                f"Warranty: {prod['warranty']}\n"
                f"Description: {prod['description']}"
            )
            docs.append(doc_text)
            metadatas.append({
                "type": "product_spec",
                "product_id": prod["id"],
                "name": prod["name"],
                "category": prod["category"],
                "price": float(prod["price"]),
            })
            ids.append(f"kb_prod_{prod['id']}")

        # Ingest official user manuals & troubleshooting guides
        for manual in MANUAL_DOCUMENTS:
            doc_text = (
                f"OFFICIAL MANUAL / GUIDE: {manual['title']}\n"
                f"Product ID: {manual['product_id']} | Category: {manual['category']}\n"
                f"Content: {manual['content']}"
            )
            docs.append(doc_text)
            metadatas.append({
                "type": "manual_guide",
                "product_id": manual["product_id"],
                "title": manual["title"],
                "category": manual["category"],
            })
            ids.append(f"kb_manual_{manual['id']}")

        self.kb_collection.add(
            documents=docs,
            metadatas=metadatas,
            ids=ids,
        )

    # -------------------------------------------------------------
    # Anti-Hallucination Grounding Methods
    # -------------------------------------------------------------
    def verify_ground_truth(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve verified facts from ChromaDB to ground claims and eliminate hallucinations.
        """
        if not self.is_connected or self.kb_collection is None:
            self.connect()

        results = self.kb_collection.query(
            query_texts=[query],
            n_results=min(n_results, self.kb_collection.count())
        )

        formatted = []
        if results and results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                dist = results["distances"][0][i] if results.get("distances") else 0.0
                formatted.append({
                    "content": doc,
                    "metadata": meta,
                    "relevance_distance": round(dist, 4),
                })
        return formatted

    # -------------------------------------------------------------
    # Long-Term User Memory Methods
    # -------------------------------------------------------------
    def save_user_memory(self, user_id: str, memory_fact: str, category: str = "preference") -> Dict[str, Any]:
        """
        Persist a piece of knowledge about a specific user across sessions.
        (e.g., 'User owns a 2023 MacBook Air and prefers OLED monitors under $1000').
        """
        if not self.is_connected or self.memory_collection is None:
            self.connect()

        timestamp = datetime.now().isoformat()
        memory_id = f"mem_{user_id}_{int(datetime.now().timestamp() * 1000)}"

        self.memory_collection.add(
            documents=[memory_fact],
            metadatas=[{
                "user_id": user_id,
                "category": category,
                "created_at": timestamp,
            }],
            ids=[memory_id]
        )

        return {
            "status": "success",
            "memory_id": memory_id,
            "user_id": user_id,
            "saved_fact": memory_fact,
            "timestamp": timestamp,
        }

    def recall_user_memories(self, user_id: str, query: str = "", n_results: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieve relevant long-term memories and preferences for a user from ChromaDB.
        """
        if not self.is_connected or self.memory_collection is None:
            self.connect()

        if self.memory_collection.count() == 0:
            return []

        # If query is provided, semantic search filtered by user_id
        if query:
            results = self.memory_collection.query(
                query_texts=[query],
                where={"user_id": user_id},
                n_results=n_results,
            )
            formatted = []
            if results and results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i]
                    formatted.append({
                        "memory": doc,
                        "category": meta.get("category", "preference"),
                        "created_at": meta.get("created_at"),
                    })
            return formatted
        else:
            # Return all stored memories for this user
            all_records = self.memory_collection.get(
                where={"user_id": user_id},
                limit=n_results,
            )
            formatted = []
            if all_records and all_records.get("documents"):
                for i, doc in enumerate(all_records["documents"]):
                    meta = all_records["metadatas"][i] if all_records.get("metadatas") else {}
                    formatted.append({
                        "memory": doc,
                        "category": meta.get("category", "preference"),
                        "created_at": meta.get("created_at"),
                    })
            return formatted

    def get_all_stored_memories(self) -> List[Dict[str, Any]]:
        """Retrieve diagnostic list of all stored user memories across all users."""
        if not self.is_connected or self.memory_collection is None:
            self.connect()

        records = self.memory_collection.get()
        items = []
        if records and records.get("documents"):
            for i, doc in enumerate(records["documents"]):
                meta = records["metadatas"][i] if records.get("metadatas") else {}
                mid = records["ids"][i]
                items.append({
                    "id": mid,
                    "memory": doc,
                    "user_id": meta.get("user_id", "anonymous"),
                    "created_at": meta.get("created_at", "N/A"),
                })
        return items
