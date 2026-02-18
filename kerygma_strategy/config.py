"""Configuration loader for distribution-strategy.

Loads YAML config with analytics store path, calendar path,
and channel registry path.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class StrategyConfig:
    """Configuration for distribution strategy components."""
    analytics_store_path: str = "analytics.json"
    calendar_path: str = ""
    channels_path: str = ""
    reports_directory: str = "reports"


def load_config(path: Path | None = None) -> StrategyConfig:
    """Load strategy configuration from YAML."""
    if not path or not path.exists():
        return StrategyConfig()

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return StrategyConfig()

    return StrategyConfig(
        analytics_store_path=data.get("analytics_store_path", "analytics.json"),
        calendar_path=data.get("calendar_path", ""),
        channels_path=data.get("channels_path", ""),
        reports_directory=data.get("reports_directory", "reports"),
    )
