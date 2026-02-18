"""Tests for analytics persistence integration."""

from datetime import datetime
from pathlib import Path

from kerygma_strategy.analytics import AnalyticsCollector, EngagementMetric
from kerygma_strategy.persistence import JsonStore


class TestAnalyticsPersistence:
    def test_collector_with_store(self, tmp_path):
        path = tmp_path / "analytics.json"
        store = JsonStore(path)
        collector = AnalyticsCollector(store=store)
        collector.record(EngagementMetric(
            channel_id="mastodon", content_id="c1",
            timestamp=datetime(2026, 2, 15), impressions=100, clicks=10,
        ))
        collector.flush()
        assert path.exists()

        # Reload from disk
        store2 = JsonStore(path)
        collector2 = AnalyticsCollector(store=store2)
        assert collector2.total_records == 1
        assert collector2.get_by_channel("mastodon")[0].impressions == 100

    def test_from_dict(self):
        data = {
            "metrics": [
                {
                    "channel_id": "discord",
                    "content_id": "c1",
                    "timestamp": "2026-02-15T00:00:00",
                    "impressions": 200,
                    "clicks": 20,
                    "shares": 5,
                    "replies": 3,
                }
            ]
        }
        collector = AnalyticsCollector.from_dict(data)
        assert collector.total_records == 1
        assert collector.get_by_channel("discord")[0].clicks == 20

    def test_without_store_no_crash(self):
        collector = AnalyticsCollector()
        collector.record(EngagementMetric(
            channel_id="ch1", content_id="c1",
            timestamp=datetime(2026, 1, 1), impressions=50,
        ))
        assert collector.total_records == 1
