"""Provider contracts for future media-generation adapters.

No external provider is implemented here yet. Keep secrets out of source control.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

@dataclass(frozen=True)
class AssetResult:
    asset_path: Path
    provider: str
    model: str
    media_type: str
    duration_seconds: float | None = None
    license_note: str = "Unspecified; review before publication"

class MediaProvider(Protocol):
    def generate(self, *, prompt: str, output_path: Path) -> AssetResult:
        """Generate one asset and return its metadata."""
        ...

class ProviderNotConfigured(RuntimeError):
    """Raised when a requested provider has not been configured."""
