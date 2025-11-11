"""Storage utilities for GEO Crystal MVP (JSON file storage)."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from config.config import settings
from src.utils.logger import logger


class JSONStorage:
    """JSON file-based storage for MVP."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize JSON storage.

        Args:
            storage_dir: Directory to store JSON files. Uses default from config if None.
        """
        self.storage_dir = storage_dir or settings.DATA_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized JSON storage at {self.storage_dir}")

    def save_audit(self, audit_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """
        Save audit data to JSON file.

        Args:
            audit_data: Dictionary containing audit data
            filename: Optional filename. If None, generates from URL and timestamp.

        Returns:
            Path to saved file
        """
        if filename is None:
            url = audit_data.get("url", "unknown")
            # Sanitize URL for filename
            safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_{safe_url}_{timestamp}.json"

        filepath = self.storage_dir / filename

        # Convert datetime objects to ISO format strings
        serializable_data = self._make_serializable(audit_data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved audit data to {filepath}")
        return filepath

    def load_audit(self, filename: str) -> Dict[str, Any]:
        """
        Load audit data from JSON file.

        Args:
            filename: Name of the file to load

        Returns:
            Dictionary containing audit data

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = self.storage_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Audit file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Loaded audit data from {filepath}")
        return data

    def list_audits(self) -> list[str]:
        """
        List all audit files.

        Returns:
            List of audit filenames
        """
        audit_files = [
            f.name
            for f in self.storage_dir.glob("audit_*.json")
            if f.is_file()
        ]
        return sorted(audit_files, reverse=True)  # Most recent first

    def save_transformation(
        self,
        transformation_data: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> Path:
        """
        Save transformation data to JSON file.

        Args:
            transformation_data: Dictionary containing transformation data
            filename: Optional filename. If None, generates from timestamp.

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transformation_{timestamp}.json"

        filepath = self.storage_dir / filename

        serializable_data = self._make_serializable(transformation_data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved transformation data to {filepath}")
        return filepath

    def _make_serializable(self, data: Any) -> Any:
        """
        Convert data to JSON-serializable format.

        Args:
            data: Data to convert

        Returns:
            JSON-serializable data
        """
        if isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, Path):
            return str(data)
        elif hasattr(data, "model_dump"):  # Pydantic models
            return data.model_dump()
        else:
            return data

