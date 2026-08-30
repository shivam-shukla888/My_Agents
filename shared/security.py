"""
Secure Workspace & File Vault for Multi-Agent Environment.
Enables agents to safely exchange generated reports, CSV datasets, and PDF invoices
with strict path validation, sandbox boundaries, and anti-traversal security.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class SecureWorkspaceVault:
    """
    Sandboxed file vault for multi-agent file exchange.
    Enforces security by keeping all file operations strictly inside the designated sandbox.
    """

    def __init__(self, sandbox_dir: str = "shared/workspace"):
        self.sandbox_dir = Path(sandbox_dir).resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, filename: str) -> Path:
        """Sanitize filename and ensure it cannot escape the sandbox boundary."""
        clean_name = os.path.basename(filename.strip().replace("\\", "/"))
        safe_path = (self.sandbox_dir / clean_name).resolve()
        if not str(safe_path).startswith(str(self.sandbox_dir)):
            raise PermissionError(f"Security Violation: Attempted directory traversal with '{filename}'.")
        return safe_path

    def write_file(
        self,
        filename: str,
        content: str,
        author_agent: str,
        file_type: str = "text/markdown",
    ) -> Dict[str, Any]:
        """Safely write a file to the shared workspace."""
        safe_path = self._resolve_safe_path(filename)
        safe_path.write_text(content, encoding="utf-8")

        return {
            "status": "success",
            "filename": safe_path.name,
            "path": str(safe_path),
            "size_bytes": safe_path.stat().st_size,
            "author_agent": author_agent,
            "file_type": file_type,
            "created_at": datetime.now().isoformat(),
        }

    def read_file(self, filename: str, reader_agent: str) -> Dict[str, Any]:
        """Safely read a file from the shared workspace."""
        safe_path = self._resolve_safe_path(filename)
        if not safe_path.exists():
            return {
                "status": "not_found",
                "message": f"File '{filename}' does not exist in the shared workspace.",
            }

        content = safe_path.read_text(encoding="utf-8")
        return {
            "status": "success",
            "filename": safe_path.name,
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
            "reader_agent": reader_agent,
        }

    def list_shared_files(self) -> List[Dict[str, Any]]:
        """List all files currently accessible in the shared vault."""
        files = []
        for p in self.sandbox_dir.glob("*"):
            if p.is_file():
                files.append({
                    "filename": p.name,
                    "size_bytes": p.stat().st_size,
                    "modified_at": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                })
        return files
