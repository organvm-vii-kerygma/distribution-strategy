"""Tests for the analytics module."""

from datetime import datetime

from kerygma_strategy.analytics import AnalyticsCollector, EngagementMetric


def test_record_and_retrieve():
    collector = AnalyticsCollector()
    m = EngagementMetric(channel_id="ch1", content_id="c1", timestamp=datetime(2026, 1, 1), impressions=100, clicks=10)
    collector.record(m)
    assert collector.total_records == 1


def test_get_by_channel():
    collector = AnalyticsCollector()
    collector.record(EngagementMetric(channel_id="ch1", content_id="c1", timestamp=datetime(2026, 1, 1), impressions=100, clicks=10))
    collector.record(EngagementMetric(channel_id="ch2", content_id="c2", timestamp=datetime(2026, 1, 2), impressions=200, clicks=20))
    assert len(collector.get_by_channel("ch1")) == 1


def test_get_by_content():
    collector = AnalyticsCollector()
    collector.record(EngagementMetric(channel_id="ch1", content_id="c1", timestamp=datetime(2026, 1, 1), impressions=100, clicks=10))
    collector.record(EngagementMetric(channel_id="ch2", content_id="c1", timestamp=datetime(2026, 1, 2), impressions=200, clicks=20))
    assert len(collector.get_by_content("c1")) == 2


def test_engagement_rate():
    m = EngagementMetric(channel_id="ch1", content_id="c1", timestamp=datetime(2026, 1, 1), impressions=100, clicks=5, shares=3, replies=2)
    assert m.engagement_rate == 0.1


def test_engagement_rate_zero_impressions():
    m = EngagementMetric(channel_id="ch1", content_id="c1", timestamp=datetime(2026, 1, 1))
    assert m.engagement_rate == 0.0


def test_aggregate_by_channel():
    collector = AnalyticsCollector()
    collector.record(EngagementMetric(channel_id="ch1", content_id="c1", timestamp=datetime(2026, 1, 1), impressions=100, clicks=10))
    collector.record(EngagementMetric(channel_id="ch1", content_id="c2", timestamp=datetime(2026, 1, 2), impressions=200, clicks=20))
    agg = collector.aggregate_by_channel()
    assert agg["ch1"]["impressions"] == 300
    assert agg["ch1"]["clicks"] == 30


def test_top_content():
    collector = AnalyticsCollector()
    collector.record(EngagementMetric(channel_id="ch1", content_id="low", timestamp=datetime(2026, 1, 1), impressions=100, clicks=1))
    collector.record(EngagementMetric(channel_id="ch1", content_id="high", timestamp=datetime(2026, 1, 1), impressions=100, clicks=50))
    top = collector.top_content(limit=1)
    assert top[0][0] == "high"


def test_to_dict():
    m = EngagementMetric(channel_id="ch1", content_id="c1", timestamp=datetime(2026, 1, 1), impressions=100, clicks=10)
    d = m.to_dict()
    assert d["channel_id"] == "ch1"
    assert "engagement_rate" in d
