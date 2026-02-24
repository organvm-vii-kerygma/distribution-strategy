"""Generate static data artifacts for distribution-strategy.

Produces:
  data/distribution-plan.json  — channel inventory, calendar events, scheduling config
  data/channel-report.json     — platform capabilities, analytics schema, report schema

No running server or database required.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from kerygma_strategy.calendar import DistributionCalendar
from kerygma_strategy.channels import ChannelRegistry
from kerygma_strategy.scheduler import Frequency

REPO_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


def build_distribution_plan(fixtures_dir: Path | None = None) -> dict[str, Any]:
    """Build distribution plan from channel and calendar configurations."""
    fixtures_dir = fixtures_dir or FIXTURES_DIR

    # Channels
    channels_path = fixtures_dir / "sample_channels.yaml"
    raw_channels = yaml.safe_load(channels_path.read_text(encoding="utf-8"))
    registry = ChannelRegistry.from_yaml(channels_path)

    channel_entries = []
    for ch_data in raw_channels.get("channels", []):
        channel_entries.append({
            "channel_id": ch_data["channel_id"],
            "name": ch_data.get("name", ch_data["channel_id"]),
            "platform": ch_data["platform"],
            "endpoint": ch_data.get("endpoint", ""),
            "max_length": ch_data.get("max_length", 0),
            "enabled": ch_data.get("enabled", True),
        })

    # Calendar
    calendar_path = fixtures_dir / "sample_calendar.yaml"
    raw_calendar = yaml.safe_load(calendar_path.read_text(encoding="utf-8"))
    calendar = DistributionCalendar.from_yaml(calendar_path)

    event_entries = []
    for ev_data in raw_calendar.get("calendar", {}).get("events", []):
        event_entries.append({
            "event_id": ev_data["event_id"],
            "name": ev_data["name"],
            "event_type": ev_data["event_type"],
            "start_date": str(ev_data["start_date"]),
            "end_date": str(ev_data.get("end_date", "")),
            "posting_modifier": ev_data.get("posting_modifier", 1.0),
        })

    # Scheduling frequencies
    frequencies = [f.value for f in Frequency]

    return {
        "total_channels": registry.total_channels,
        "enabled_channels": len(registry.get_enabled()),
        "channels": channel_entries,
        "total_events": calendar.total_events,
        "events": event_entries,
        "scheduling_frequencies": frequencies,
    }


def build_channel_report(fixtures_dir: Path | None = None) -> dict[str, Any]:
    """Build channel capabilities and analytics/report schema documentation."""
    fixtures_dir = fixtures_dir or FIXTURES_DIR

    # Platform capabilities from channel config
    channels_path = fixtures_dir / "sample_channels.yaml"
    raw = yaml.safe_load(channels_path.read_text(encoding="utf-8"))

    platforms: dict[str, dict[str, Any]] = {}
    for ch_data in raw.get("channels", []):
        platform = ch_data["platform"]
        if platform not in platforms:
            platforms[platform] = {
                "platform": platform,
                "channels": [],
                "max_length": ch_data.get("max_length", 0),
            }
        platforms[platform]["channels"].append(ch_data["channel_id"])

    # Analytics schema from EngagementMetric fields
    analytics_fields = [
        {"field": "channel_id", "type": "string"},
        {"field": "content_id", "type": "string"},
        {"field": "timestamp", "type": "datetime"},
        {"field": "impressions", "type": "integer"},
        {"field": "clicks", "type": "integer"},
        {"field": "shares", "type": "integer"},
        {"field": "replies", "type": "integer"},
        {"field": "engagement_rate", "type": "float", "computed": True},
    ]

    # Report schema from ReportData fields
    report_fields = [
        {"field": "period", "type": "object", "subfields": ["start", "end", "label"]},
        {"field": "total_metrics", "type": "integer"},
        {"field": "channel_summary", "type": "object"},
        {"field": "top_content", "type": "list"},
        {"field": "total_impressions", "type": "integer"},
        {"field": "total_engagement", "type": "integer"},
    ]

    return {
        "platforms": list(platforms.values()),
        "analytics_schema": {
            "class": "EngagementMetric",
            "fields": analytics_fields,
        },
        "report_schema": {
            "class": "ReportData",
            "fields": report_fields,
        },
    }


def export_all(
    fixtures_dir: Path | None = None,
    output_dir: Path | None = None,
) -> list[Path]:
    """Generate all data artifacts and return output paths."""
    fixtures_dir = fixtures_dir or FIXTURES_DIR
    output_dir = output_dir or REPO_ROOT / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    # distribution-plan.json
    plan = build_distribution_plan(fixtures_dir)
    plan_path = output_dir / "distribution-plan.json"
    plan_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "organ": "VII",
        "organ_name": "Kerygma",
        "repo": "distribution-strategy",
        **plan,
    }
    plan_path.write_text(json.dumps(plan_data, indent=2) + "\n")
    outputs.append(plan_path)

    # channel-report.json
    report = build_channel_report(fixtures_dir)
    report_path = output_dir / "channel-report.json"
    report_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "organ": "VII",
        "organ_name": "Kerygma",
        "repo": "distribution-strategy",
        **report,
    }
    report_path.write_text(json.dumps(report_data, indent=2) + "\n")
    outputs.append(report_path)

    return outputs


def main() -> None:
    """CLI entry point for data export."""
    paths = export_all()
    for p in paths:
        print(f"Written: {p}")


if __name__ == "__main__":
    main()
