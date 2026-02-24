# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`kerygma_strategy` — the analytics, scheduling, and distribution strategy package for ORGAN-VII (Kerygma). Tracks engagement metrics, manages publication calendars with posting modifiers, configures channel registries, and generates distribution reports.

## Package Structure

Source is in `kerygma_strategy/`, installed as the `kerygma_strategy` package:

| Module | Purpose |
|--------|---------|
| `analytics.py` | `AnalyticsCollector` — records `EngagementMetric` dataclasses (impressions, clicks, shares, replies). Auto-persists every N records via `JsonStore`. `aggregate_by_channel()`, `top_content()` queries. |
| `scheduler.py` | `ContentScheduler` — manages `ScheduleEntry` with recurrence (`Frequency` enum: ONCE/DAILY/WEEKLY/BIWEEKLY/MONTHLY). `get_due()`, `get_upcoming()`. Calendar-aware: `schedule_with_calendar()` delays posts during quiet periods. `get_due_with_priority()` returns `PrioritizedEntry` scored by overdue hours * calendar modifier. |
| `calendar.py` | `DistributionCalendar` — tracks `CalendarEvent` objects (grant_deadline, conference, quiet_period). `get_posting_modifier()` multiplies active event modifiers. `is_quiet_period()` check. Loadable from YAML via `from_yaml()`. |
| `channels.py` | `ChannelRegistry` — `ChannelConfig` dataclasses with `channel_id`, `platform`, `max_length`, `enabled`. `format_content()` truncates to limit. YAML serialize/deserialize via `from_yaml()`/`to_yaml()`. |
| `persistence.py` | `JsonStore` — key-value store with atomic writes (`os.replace` via `.tmp` file). Used by `AnalyticsCollector` for metric persistence. |
| `report_generator.py` | Generates Markdown distribution reports from analytics data. |
| `ghost_metrics.py` | Pull-back adapter for Ghost newsletter engagement metrics. |
| `mastodon_metrics.py` | Pull-back adapter for Mastodon post engagement metrics. |
| `config.py` | `load_config(path)` → `StrategyConfig` dataclass. YAML-based config for analytics store path, calendar path, channels path, reports directory. |
| `cli.py` | CLI entry point (`distrib`). |

## Development Commands

```bash
# Install (from superproject root or this directory)
pip install -e .[dev]

# Tests
pytest tests/ -v
pytest tests/test_scheduler.py::TestContentScheduler::test_get_due -v

# Lint
ruff check kerygma_strategy/
```

## Key Design Details

- **Calendar modifiers** are multiplicative: a `posting_modifier` of 1.5 (conference) combined with another 1.5 (grant deadline) yields 2.25x. Quiet periods use < 1.0 (e.g., 0.3). The scheduler uses these to prioritize what to post.
- **Scheduler auto-reschedules recurring entries** — when `publish_entry()` is called on a recurring entry, it creates a new `{id}-next` entry at the next occurrence time.
- **Analytics flush** — `AnalyticsCollector` buffers records in memory and auto-persists every `persist_every` records (default 50). Call `flush()` explicitly after batch operations.
- **JsonStore uses atomic writes** — same pattern as other ORGAN-VII stores: write to `.tmp`, then `os.replace()`.
- **Runtime dependency**: only `pyyaml>=6.0` (for channel/calendar/config YAML loading).

## Test Structure

Tests in `tests/` with `fixtures/` directory:
- `test_analytics.py` — recording, aggregation, top content
- `test_analytics_persistence.py` — JsonStore round-trip
- `test_scheduler.py` — due/upcoming, publish, recurrence
- `test_scheduler_calendar.py` — calendar-aware scheduling, quiet periods, priority
- `test_calendar.py` — event lifecycle, modifiers, active windows
- `test_channels.py` — registry, format_content, enable/disable
- `test_channels_yaml.py` — YAML serialize/deserialize
- `test_persistence.py` — JsonStore atomic writes, from_dict
- `test_report_generator.py` — Markdown report output
- `test_ghost_metrics.py` — Ghost metrics adapter
- `test_mastodon_metrics.py` — Mastodon metrics adapter

## ORGANVM Context

Consumes essays from ORGAN-V. Produces distribution artifacts consumed by ORGAN-IV. Subscribes to `essay.published` and `promotion.completed` events.

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-VII (Marketing) | **Tier:** standard | **Status:** GRADUATED
**Org:** `unknown` | **Repo:** `distribution-strategy`

### Edges
- **Produces** → `unknown`: unknown
- **Consumes** ← `ORGAN-V`: unknown

### Siblings in Marketing
`announcement-templates`, `social-automation`, `.github`

### Governance
- *Standard ORGANVM governance applies*

*Last synced: 2026-02-24T01:01:15Z*
<!-- ORGANVM:AUTO:END -->
