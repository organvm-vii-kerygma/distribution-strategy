"""Channels module for managing distribution channel configurations.

Defines channel types, formatting rules, and delivery mechanisms
for each distribution platform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ChannelConfig:
    """Configuration for a single distribution channel."""
    channel_id: str
    name: str
    platform: str
    endpoint: str
    max_length: int = 0
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def format_content(self, title: str, body: str, url: str) -> str:
        parts = [title]
        if body:
            remaining = self.max_length - len(title) - len(url) - 10 if self.max_length else len(body)
            parts.append(body[:remaining])
        parts.append(url)
        text = "\n\n".join(parts)
        if self.max_length and len(text) > self.max_length:
            return text[:self.max_length - 3] + "..."
        return text


class ChannelRegistry:
    """Registry of all configured distribution channels."""

    def __init__(self) -> None:
        self._channels: dict[str, ChannelConfig] = {}

    def register(self, config: ChannelConfig) -> None:
        if config.channel_id in self._channels:
            raise ValueError(f"Channel '{config.channel_id}' already registered")
        self._channels[config.channel_id] = config

    def get(self, channel_id: str) -> ChannelConfig:
        return self._channels[channel_id]

    def get_enabled(self) -> list[ChannelConfig]:
        return [c for c in self._channels.values() if c.enabled]

    def get_by_platform(self, platform: str) -> list[ChannelConfig]:
        return [c for c in self._channels.values() if c.platform == platform]

    def disable(self, channel_id: str) -> None:
        self._channels[channel_id].enabled = False

    def enable(self, channel_id: str) -> None:
        self._channels[channel_id].enabled = True

    @classmethod
    def from_yaml(cls, path: Path) -> ChannelRegistry:
        """Load channel registry from a YAML file."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        reg = cls()
        for ch_data in data.get("channels", []):
            reg.register(ChannelConfig(
                channel_id=ch_data["channel_id"],
                name=ch_data.get("name", ch_data["channel_id"]),
                platform=ch_data["platform"],
                endpoint=ch_data.get("endpoint", ""),
                max_length=ch_data.get("max_length", 0),
                enabled=ch_data.get("enabled", True),
                metadata=ch_data.get("metadata", {}),
            ))
        return reg

    def to_yaml(self, path: Path) -> None:
        """Save channel registry to a YAML file."""
        channels = []
        for ch in self._channels.values():
            channels.append({
                "channel_id": ch.channel_id,
                "name": ch.name,
                "platform": ch.platform,
                "endpoint": ch.endpoint,
                "max_length": ch.max_length,
                "enabled": ch.enabled,
                "metadata": ch.metadata,
            })
        path.write_text(
            yaml.dump({"channels": channels}, default_flow_style=False),
            encoding="utf-8",
        )

    @property
    def total_channels(self) -> int:
        return len(self._channels)
