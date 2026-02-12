"""Analytics module for tracking distribution performance.

Collects and aggregates engagement metrics across channels,
providing insights for optimizing distribution strategy.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EngagementMetric:
    channel_id: str
    content_id: str
    timestamp: datetime
    impressions: int = 0
    clicks: int = 0
    shares: int = 0
    replies: int = 0

    @property
    def engagement_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return (self.clicks + self.shares + self.replies) / self.impressions

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "content_id": self.content_id,
            "timestamp": self.timestamp.isoformat(),
            "impressions": self.impressions,
            "clicks": self.clicks,
            "shares": self.shares,
            "replies": self.replies,
            "engagement_rate": round(self.engagement_rate, 4),
        }


class AnalyticsCollector:
    """Collects and aggregates distribution performance metrics."""

    def __init__(self) -> None:
        self._metrics: list[EngagementMetric] = []

    def record(self, metric: EngagementMetric) -> None:
        self._metrics.append(metric)

    def get_by_channel(self, channel_id: str) -> list[EngagementMetric]:
        return [m for m in self._metrics if m.channel_id == channel_id]

    def get_by_content(self, content_id: str) -> list[EngagementMetric]:
        return [m for m in self._metrics if m.content_id == content_id]

    def aggregate_by_channel(self) -> dict[str, dict[str, int]]:
        agg: dict[str, dict[str, int]] = {}
        for m in self._metrics:
            if m.channel_id not in agg:
                agg[m.channel_id] = {"impressions": 0, "clicks": 0, "shares": 0, "replies": 0}
            agg[m.channel_id]["impressions"] += m.impressions
            agg[m.channel_id]["clicks"] += m.clicks
            agg[m.channel_id]["shares"] += m.shares
            agg[m.channel_id]["replies"] += m.replies
        return agg

    def top_content(self, limit: int = 5) -> list[tuple[str, float]]:
        content_rates: dict[str, list[float]] = {}
        for m in self._metrics:
            content_rates.setdefault(m.content_id, []).append(m.engagement_rate)
        averages = [(cid, sum(rates) / len(rates)) for cid, rates in content_rates.items()]
        return sorted(averages, key=lambda x: x[1], reverse=True)[:limit]

    @property
    def total_records(self) -> int:
        return len(self._metrics)
