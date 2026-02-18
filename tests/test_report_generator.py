"""Tests for the report generator module."""

from datetime import datetime

from kerygma_strategy.analytics import AnalyticsCollector, EngagementMetric
from kerygma_strategy.report_generator import ReportGenerator, ReportPeriod


def _make_collector() -> AnalyticsCollector:
    collector = AnalyticsCollector()
    collector.record(EngagementMetric(
        channel_id="mastodon", content_id="essay-01",
        timestamp=datetime(2026, 2, 15), impressions=1000, clicks=50, shares=20, replies=10,
    ))
    collector.record(EngagementMetric(
        channel_id="discord", content_id="essay-01",
        timestamp=datetime(2026, 2, 15), impressions=500, clicks=25, shares=10, replies=5,
    ))
    collector.record(EngagementMetric(
        channel_id="mastodon", content_id="essay-02",
        timestamp=datetime(2026, 2, 16), impressions=800, clicks=80, shares=30, replies=15,
    ))
    return collector


class TestReportPeriod:
    def test_weekly(self):
        end = datetime(2026, 2, 17)
        period = ReportPeriod.weekly(end)
        assert period.label == "weekly"
        assert period.start == datetime(2026, 2, 10)

    def test_monthly(self):
        end = datetime(2026, 2, 17)
        period = ReportPeriod.monthly(end)
        assert period.label == "monthly"


class TestReportGenerator:
    def test_generate_weekly(self):
        collector = _make_collector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        assert report.total_metrics == 3
        assert report.total_impressions == 2300
        assert "mastodon" in report.channel_summary

    def test_to_markdown(self):
        collector = _make_collector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        md = gen.to_markdown(report)
        assert "# Distribution Report" in md
        assert "mastodon" in md
        assert "essay-" in md

    def test_to_json(self):
        collector = _make_collector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        import json
        data = json.loads(gen.to_json(report))
        assert data["total_metrics"] == 3

    def test_save_report(self, tmp_path):
        collector = _make_collector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        files = gen.save_report(report, tmp_path)
        assert len(files) == 2  # markdown + json
        assert all(f.exists() for f in files)

    def test_top_content(self):
        collector = _make_collector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        assert len(report.top_content) > 0
        # essay-02 has higher engagement rate
        assert report.top_content[0][0] == "essay-02"

    def test_report_data_to_dict(self):
        collector = _make_collector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        d = report.to_dict()
        assert "period" in d
        assert "channel_summary" in d

    def test_empty_collector(self):
        collector = AnalyticsCollector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        assert report.total_metrics == 0

    def test_save_markdown_only(self, tmp_path):
        collector = _make_collector()
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        files = gen.save_report(report, tmp_path, fmt="markdown")
        assert len(files) == 1
        assert files[0].suffix == ".md"

    def test_metrics_outside_period_excluded(self):
        """Metrics with timestamps outside the report period should be filtered out."""
        collector = AnalyticsCollector()
        # Inside period (Feb 10-17)
        collector.record(EngagementMetric(
            channel_id="mastodon", content_id="in-range",
            timestamp=datetime(2026, 2, 15), impressions=500,
        ))
        # Outside period — too old
        collector.record(EngagementMetric(
            channel_id="mastodon", content_id="too-old",
            timestamp=datetime(2026, 1, 1), impressions=999,
        ))
        # Outside period — too new
        collector.record(EngagementMetric(
            channel_id="mastodon", content_id="too-new",
            timestamp=datetime(2026, 3, 1), impressions=888,
        ))
        gen = ReportGenerator(collector)
        period = ReportPeriod.weekly(datetime(2026, 2, 17))
        report = gen.generate(period)
        assert report.total_metrics == 1
        assert report.total_impressions == 500
