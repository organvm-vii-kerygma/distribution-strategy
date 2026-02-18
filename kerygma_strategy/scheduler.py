"""Scheduler module for time-based content distribution.

Manages publication schedules with timezone support, recurrence rules,
and optimal timing based on audience analytics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kerygma_strategy.calendar import DistributionCalendar


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


@dataclass
class ScheduleEntry:
    entry_id: str
    content_id: str
    channel: str
    scheduled_time: datetime
    frequency: Frequency = Frequency.ONCE
    published: bool = False

    def is_due(self, now: datetime | None = None) -> bool:
        current = now or datetime.now()
        return not self.published and current >= self.scheduled_time

    def mark_published(self) -> None:
        self.published = True

    def next_occurrence(self) -> datetime | None:
        if self.frequency == Frequency.ONCE:
            return None
        deltas = {
            Frequency.DAILY: timedelta(days=1),
            Frequency.WEEKLY: timedelta(weeks=1),
            Frequency.BIWEEKLY: timedelta(weeks=2),
            Frequency.MONTHLY: timedelta(days=30),
        }
        return self.scheduled_time + deltas[self.frequency]


@dataclass
class PrioritizedEntry:
    """A schedule entry with a calendar-adjusted priority score."""
    entry: ScheduleEntry
    priority: float
    modifier: float = 1.0


class ContentScheduler:
    """Manages the publication schedule for content across channels."""

    def __init__(self, calendar: DistributionCalendar | None = None) -> None:
        self._entries: dict[str, ScheduleEntry] = {}
        self._calendar = calendar

    def schedule(self, entry: ScheduleEntry) -> None:
        if entry.entry_id in self._entries:
            raise ValueError(f"Schedule entry '{entry.entry_id}' already exists")
        self._entries[entry.entry_id] = entry

    def get_due(self, now: datetime | None = None) -> list[ScheduleEntry]:
        return [e for e in self._entries.values() if e.is_due(now)]

    def get_upcoming(self, hours: int = 24, now: datetime | None = None) -> list[ScheduleEntry]:
        current = now or datetime.now()
        window = current + timedelta(hours=hours)
        return [
            e for e in self._entries.values()
            if not e.published and current <= e.scheduled_time <= window
        ]

    def publish_entry(self, entry_id: str) -> ScheduleEntry:
        entry = self._entries[entry_id]
        entry.mark_published()
        if entry.frequency != Frequency.ONCE:
            next_time = entry.next_occurrence()
            if next_time:
                new_id = f"{entry_id}-next"
                new_entry = ScheduleEntry(
                    entry_id=new_id, content_id=entry.content_id,
                    channel=entry.channel, scheduled_time=next_time,
                    frequency=entry.frequency,
                )
                self._entries[new_id] = new_entry
        return entry

    @property
    def total_entries(self) -> int:
        return len(self._entries)

    def schedule_with_calendar(self, entry: ScheduleEntry) -> ScheduleEntry:
        """Schedule with calendar awareness — delays during quiet periods."""
        if self._calendar and self._calendar.is_quiet_period(entry.scheduled_time.date()):
            # Push to end of quiet period
            active = self._calendar.get_active_events(entry.scheduled_time.date())
            for ev in active:
                if ev.event_type == "quiet_period" and ev.end_date:
                    new_time = datetime.combine(
                        ev.end_date + timedelta(days=1),
                        entry.scheduled_time.time(),
                    )
                    entry = ScheduleEntry(
                        entry_id=entry.entry_id,
                        content_id=entry.content_id,
                        channel=entry.channel,
                        scheduled_time=new_time,
                        frequency=entry.frequency,
                    )
                    break
        self.schedule(entry)
        return entry

    def get_due_with_priority(self, now: datetime | None = None) -> list[PrioritizedEntry]:
        """Get due entries with calendar-adjusted priority scores."""
        due = self.get_due(now)
        results: list[PrioritizedEntry] = []
        for entry in due:
            modifier = 1.0
            if self._calendar:
                modifier = self._calendar.get_posting_modifier(entry.scheduled_time.date())
            # Base priority: how overdue (in hours), multiplied by calendar modifier
            current = now or datetime.now()
            overdue_hours = (current - entry.scheduled_time).total_seconds() / 3600
            priority = max(0.1, overdue_hours) * modifier
            results.append(PrioritizedEntry(
                entry=entry, priority=priority, modifier=modifier,
            ))
        return sorted(results, key=lambda p: p.priority, reverse=True)

    @property
    def pending_count(self) -> int:
        return sum(1 for e in self._entries.values() if not e.published)