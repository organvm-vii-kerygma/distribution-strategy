"""Tests for kerygma_strategy.data_export module."""
import json
from pathlib import Path

import pytest

from kerygma_strategy.data_export import (
    build_channel_report,
    build_distribution_plan,
    export_all,
)


@pytest.fixture
def fixtures_dir():
    d = Path(__file__).parent / "fixtures"
    if not d.is_dir():
        pytest.skip("fixtures directory not found")
    return d


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path / "data"


def test_build_distribution_plan(fixtures_dir):
    result = build_distribution_plan(fixtures_dir)
    assert result["total_channels"] == 3
    assert result["total_events"] == 3
    assert len(result["channels"]) == 3
    assert len(result["events"]) == 3


def test_distribution_plan_has_scheduling_frequencies(fixtures_dir):
    result = build_distribution_plan(fixtures_dir)
    assert "scheduling_frequencies" in result
    assert "daily" in result["scheduling_frequencies"]
    assert "weekly" in result["scheduling_frequencies"]


def test_distribution_plan_channel_entries(fixtures_dir):
    result = build_distribution_plan(fixtures_dir)
    for ch in result["channels"]:
        assert "channel_id" in ch
        assert "platform" in ch
        assert "max_length" in ch
        assert "enabled" in ch


def test_distribution_plan_event_entries(fixtures_dir):
    result = build_distribution_plan(fixtures_dir)
    for ev in result["events"]:
        assert "event_id" in ev
        assert "event_type" in ev
        assert "posting_modifier" in ev


def test_build_channel_report(fixtures_dir):
    result = build_channel_report(fixtures_dir)
    assert "platforms" in result
    assert "analytics_schema" in result
    assert "report_schema" in result
    assert len(result["platforms"]) > 0


def test_channel_report_analytics_schema(fixtures_dir):
    result = build_channel_report(fixtures_dir)
    schema = result["analytics_schema"]
    assert schema["class"] == "EngagementMetric"
    field_names = [f["field"] for f in schema["fields"]]
    assert "impressions" in field_names
    assert "engagement_rate" in field_names


def test_export_all_creates_two_files(fixtures_dir, tmp_output):
    paths = export_all(fixtures_dir, tmp_output)
    assert len(paths) == 2
    names = {p.name for p in paths}
    assert "distribution-plan.json" in names
    assert "channel-report.json" in names


def test_export_all_valid_json(fixtures_dir, tmp_output):
    paths = export_all(fixtures_dir, tmp_output)
    for p in paths:
        data = json.loads(p.read_text())
        assert data["organ"] == "VII"
        assert data["organ_name"] == "Kerygma"
        assert data["repo"] == "distribution-strategy"
        assert "generated_at" in data
