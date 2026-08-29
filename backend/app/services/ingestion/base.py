"""Base connector - docs 09_DATA_PIPELINE Source Connector contract."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import datetime, timezone
import uuid


class BaseConnector(ABC):
    """Provider-agnostic connector. Each dataset implements this."""

    def __init__(self, source_id: str, name: str, provider: str):
        self.source_id = source_id
        self.name = name
        self.provider = provider

    @abstractmethod
    async def fetch(self, **params) -> List[Dict[str, Any]]:
        """Retrieve raw records from external source. Must handle auth/pagination/retries."""
        ...

    @abstractmethod
    def validate_source(self) -> bool:
        """Check source availability."""
        ...

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return source metadata: coverage, resolution, update_frequency."""
        ...

    def transform(self, raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optional: normalize raw -> canonical. Default passthrough."""
        return raw

    def provenance(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider": self.provider,
            "dataset": self.name,
            "ingestion_time": datetime.now(timezone.utc).isoformat(),
            "processing_version": "1.0",
        }
