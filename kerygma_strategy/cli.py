"""CLI entry point for distribution-strategy.

Usage:
    distrib channels              — list configured channels
    distrib calendar [--upcoming] — show calendar events
    distrib report [--weekly|--monthly] — generate a report
    distrib schedule              — show pending schedule entries
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from kerygma_strategy.config import load_config


def cmd_channels(channels_path: str) -> None:
    if not channels_path:
        print("No channels_path configured.")
        return
    from kerygma_strategy.channels import ChannelRegistry
    path = Path(channels_path)
    if not path.exists():
        print(f"Channels file not found: {path}")
        return
    reg = ChannelRegistry.from_yaml(path)
    enabled = reg.get_enabled()
    print(f"Channels ({len(enabled)} enabled / {reg.total_channels} total):")
    for ch in enabled:
        print(f"  {ch.channel_id}: {ch.name} ({ch.platform})")


def cmd_calendar(calendar_path: str, upcoming: bool) -> None:
    if not calendar_path:
        print("No calendar_path configured.")
        return
    from kerygma_strategy.calendar import DistributionCalendar
    path = Path(calendar_path)
    if not path.exists():
        print(f"Calendar file not found: {path}")
        return
    cal = DistributionCalendar.from_yaml(path)
    if upcoming:
        events = cal.get_upcoming(days=90)
        print(f"Upcoming events (next 90 days): {len(events)}")
    else:
        events = list(cal._events.values())
        print(f"All calendar events: {len(events)}")
    for ev in events:
        end = f" → {ev.end_date}" if ev.end_date else ""
        print(f"  {ev.event_id}: {ev.name} ({ev.event_type}) {ev.start_date}{end} [×{ev.posting_modifier}]")


def cmd_report(analytics_path: str, reports_dir: str, period: str) -> None:
    from kerygma_strategy.analytics import AnalyticsCollector
    from kerygma_strategy.persistence import JsonStore
    from kerygma_strategy.report_generator import ReportGenerator, ReportPeriod

    store_path = Path(analytics_path)
    store = JsonStore(store_path) if store_path.exists() else None
    collector = AnalyticsCollector(store=store)

    if collector.total_records == 0:
        print("No analytics data to report.")
        return

    gen = ReportGenerator(collector)
    rp = ReportPeriod.weekly() if period == "weekly" else ReportPeriod.monthly()
    report = gen.generate(rp)

    out_dir = Path(reports_dir)
    files = gen.save_report(report, out_dir)
    for f in files:
        print(f"  Created: {f}")
    print(gen.to_markdown(report))


def cmd_schedule() -> None:
    print("Schedule viewing requires a running scheduler instance.")
    print("Use the Python API: ContentScheduler.get_due()")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="distrib", description="Distribution strategy CLI")
    parser.add_argument("--config", type=Path, default=None)
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("channels", help="List channels")

    cal_p = sub.add_parser("calendar", help="Show calendar")
    cal_p.add_argument("--upcoming", action="store_true")

    rep_p = sub.add_parser("report", help="Generate report")
    rep_p.add_argument("--monthly", action="store_true")

    sub.add_parser("schedule", help="Show schedule")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return

    cfg = load_config(args.config)

    if args.command == "channels":
        cmd_channels(cfg.channels_path)
    elif args.command == "calendar":
        cmd_calendar(cfg.calendar_path, args.upcoming)
    elif args.command == "report":
        period = "monthly" if args.monthly else "weekly"
        cmd_report(cfg.analytics_store_path, cfg.reports_directory, period)
    elif args.command == "schedule":
        cmd_schedule()


if __name__ == "__main__":
    main()
