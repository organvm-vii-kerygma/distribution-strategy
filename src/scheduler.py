"""Scheduler module for time-based content distribution.

Manages publication schedules with timezone support, recurrence rules,
and optimal timing based on audience analytics.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


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


class ContentScheduler:
    """Manages the publication schedule for content across channels."""

    def __init__(self) -> None:
        self._entries: dict[str, ScheduleEntry] = {}

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

    @property
    def pending_count(self) -> int:
        return sum(1 for e in self._entries.values() if not e.published)