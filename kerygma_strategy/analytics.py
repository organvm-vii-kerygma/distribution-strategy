"""Analytics module for tracking distribution performance.

Collects and aggregates engagement metrics across channels,
providing insights for optimizing distribution strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kerygma_strategy.persistence import JsonStore


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

    def __init__(self, store: JsonStore | None = None, persist_every: int = 50) -> None:
        self._metrics: list[EngagementMetric] = []
        self._store = store
        self._persist_every = persist_every
        self._unsaved_count = 0
        if store:
            self._load_from_store()

    def _load_from_store(self) -> None:
        """Load metrics from persistent store."""
        if not self._store:
            return
        raw = self._store.get("metrics", [])
        for item in raw:
            self._metrics.append(EngagementMetric(
                channel_id=item["channel_id"],
                content_id=item["content_id"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                impressions=item.get("impressions", 0),
                clicks=item.get("clicks", 0),
                shares=item.get("shares", 0),
                replies=item.get("replies", 0),
            ))

    def _persist(self) -> None:
        """Save metrics to persistent store."""
        if not self._store:
            return
        self._store.set("metrics", [m.to_dict() for m in self._metrics])
        self._store.save()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalyticsCollector:
        """Deserialize from a dict (e.g., loaded from JSON)."""
        collector = cls()
        for item in data.get("metrics", []):
            collector._metrics.append(EngagementMetric(
                channel_id=item["channel_id"],
                content_id=item["content_id"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                impressions=item.get("impressions", 0),
                clicks=item.get("clicks", 0),
                shares=item.get("shares", 0),
                replies=item.get("replies", 0),
            ))
        return collector

    def record(self, metric: EngagementMetric) -> None:
        self._metrics.append(metric)
        self._unsaved_count += 1
        if self._unsaved_count >= self._persist_every:
            self.flush()

    def flush(self) -> None:
        """Force-persist any unsaved metrics to disk."""
        if self._unsaved_count > 0:
            self._persist()
            self._unsaved_count = 0

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
    def all_metrics(self) -> list[EngagementMetric]:
        """Public read-only access to the full metrics list."""
        return list(self._metrics)

    @property
    def total_records(self) -> int:
        return len(self._metrics)