"""Report generator for distribution analytics.

Produces weekly and monthly reports in Markdown and JSON formats,
summarizing engagement metrics, top content, and channel performance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from kerygma_strategy.analytics import AnalyticsCollector, EngagementMetric


@dataclass
class ReportPeriod:
    """Time period for a report."""
    start: datetime
    end: datetime
    label: str

    @classmethod
    def weekly(cls, end: datetime | None = None) -> ReportPeriod:
        end_dt = end or datetime.now()
        start_dt = end_dt - timedelta(days=7)
        return cls(start=start_dt, end=end_dt, label="weekly")

    @classmethod
    def monthly(cls, end: datetime | None = None) -> ReportPeriod:
        end_dt = end or datetime.now()
        start_dt = end_dt - timedelta(days=30)
        return cls(start=start_dt, end=end_dt, label="monthly")


@dataclass
class ReportData:
    """Structured report data."""
    period: ReportPeriod
    total_metrics: int
    channel_summary: dict[str, dict[str, int]]
    top_content: list[tuple[str, float]]
    total_impressions: int
    total_engagement: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "period": {
                "start": self.period.start.isoformat(),
                "end": self.period.end.isoformat(),
                "label": self.period.label,
            },
            "total_metrics": self.total_metrics,
            "channel_summary": self.channel_summary,
            "top_content": [{"id": cid, "rate": rate} for cid, rate in self.top_content],
            "total_impressions": self.total_impressions,
            "total_engagement": self.total_engagement,
        }


class ReportGenerator:
    """Generates distribution performance reports."""

    def __init__(self, collector: AnalyticsCollector) -> None:
        self._collector = collector

    def _filter_metrics(self, period: ReportPeriod) -> list[EngagementMetric]:
        """Get metrics within the report period."""
        return [
            m for m in self._collector.all_metrics
            if period.start <= m.timestamp <= period.end
        ]

    def generate(self, period: ReportPeriod) -> ReportData:
        """Generate a report for the given period."""
        metrics = self._filter_metrics(period)

        channel_summary: dict[str, dict[str, int]] = {}
        total_impressions = 0
        total_engagement = 0

        for m in metrics:
            if m.channel_id not in channel_summary:
                channel_summary[m.channel_id] = {
                    "impressions": 0, "clicks": 0, "shares": 0, "replies": 0,
                }
            channel_summary[m.channel_id]["impressions"] += m.impressions
            channel_summary[m.channel_id]["clicks"] += m.clicks
            channel_summary[m.channel_id]["shares"] += m.shares
            channel_summary[m.channel_id]["replies"] += m.replies
            total_impressions += m.impressions
            total_engagement += m.clicks + m.shares + m.replies

        # Top content by engagement rate
        content_rates: dict[str, list[float]] = {}
        for m in metrics:
            content_rates.setdefault(m.content_id, []).append(m.engagement_rate)
        top_content = sorted(
            [(cid, sum(r) / len(r)) for cid, r in content_rates.items()],
            key=lambda x: x[1], reverse=True,
        )[:5]

        return ReportData(
            period=period,
            total_metrics=len(metrics),
            channel_summary=channel_summary,
            top_content=top_content,
            total_impressions=total_impressions,
            total_engagement=total_engagement,
        )

    def to_markdown(self, report: ReportData) -> str:
        """Render a report as Markdown."""
        lines = [
            f"# Distribution Report ({report.period.label})",
            "",
            f"**Period:** {report.period.start:%Y-%m-%d} to {report.period.end:%Y-%m-%d}",
            f"**Total metrics:** {report.total_metrics}",
            f"**Total impressions:** {report.total_impressions:,}",
            f"**Total engagement:** {report.total_engagement:,}",
            "",
            "## Channel Performance",
            "",
        ]
        for ch_id, stats in report.channel_summary.items():
            lines.append(f"### {ch_id}")
            lines.append(f"- Impressions: {stats['impressions']:,}")
            lines.append(f"- Clicks: {stats['clicks']:,}")
            lines.append(f"- Shares: {stats['shares']:,}")
            lines.append(f"- Replies: {stats['replies']:,}")
            lines.append("")

        if report.top_content:
            lines.append("## Top Content")
            lines.append("")
            for rank, (cid, rate) in enumerate(report.top_content, 1):
                lines.append(f"{rank}. **{cid}** — {rate:.2%} engagement")
            lines.append("")

        return "\n".join(lines)

    def to_json(self, report: ReportData) -> str:
        return json.dumps(report.to_dict(), indent=2)

    def save_report(self, report: ReportData, directory: Path, fmt: str = "both") -> list[Path]:
        """Save report to directory. Returns list of created file paths."""
        directory.mkdir(parents=True, exist_ok=True)
        base = f"report-{report.period.label}-{report.period.end:%Y%m%d}"
        created: list[Path] = []

        if fmt in ("markdown", "both"):
            md_path = directory / f"{base}.md"
            md_path.write_text(self.to_markdown(report), encoding="utf-8")
            created.append(md_path)

        if fmt in ("json", "both"):
            json_path = directory / f"{base}.json"
            json_path.write_text(self.to_json(report), encoding="utf-8")
            created.append(json_path)

        return created
