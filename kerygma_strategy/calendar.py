"""Distribution calendar for grant deadlines, conferences, and quiet periods.

Tracks time-based events that modify posting behavior:
- grant_deadline: increase frequency (posting_modifier > 1.0)
- conference: increase frequency during event window
- quiet_period: reduce frequency (posting_modifier < 1.0)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CalendarEvent:
    """A calendar event that modifies distribution behavior."""
    event_id: str
    name: str
    event_type: str  # "grant_deadline", "conference", "quiet_period"
    start_date: date
    end_date: date | None = None
    posting_modifier: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_active(self, on_date: date | None = None) -> bool:
        """Check if this event is active on the given date."""
        check_date = on_date or date.today()
        if self.end_date:
            return self.start_date <= check_date <= self.end_date
        return check_date == self.start_date

    def days_until(self, from_date: date | None = None) -> int:
        """Days until event starts (negative if in the past)."""
        check_date = from_date or date.today()
        return (self.start_date - check_date).days


class DistributionCalendar:
    """Calendar of events that modify distribution strategy."""

    def __init__(self) -> None:
        self._events: dict[str, CalendarEvent] = {}

    def add_event(self, event: CalendarEvent) -> None:
        self._events[event.event_id] = event

    def get_event(self, event_id: str) -> CalendarEvent | None:
        return self._events.get(event_id)

    def get_active_events(self, on_date: date | None = None) -> list[CalendarEvent]:
        return [e for e in self._events.values() if e.is_active(on_date)]

    def get_upcoming(self, days: int = 30, from_date: date | None = None) -> list[CalendarEvent]:
        """Get events starting within the next N days."""
        check_date = from_date or date.today()
        return [
            e for e in self._events.values()
            if 0 <= e.days_until(check_date) <= days
        ]

    def get_posting_modifier(self, on_date: date | None = None) -> float:
        """Get the combined posting modifier for a date.

        Multiplies all active event modifiers. Defaults to 1.0 if no events.
        """
        active = self.get_active_events(on_date)
        if not active:
            return 1.0
        modifier = 1.0
        for event in active:
            modifier *= event.posting_modifier
        return modifier

    def is_quiet_period(self, on_date: date | None = None) -> bool:
        """Check if the date falls in a quiet period."""
        return any(
            e.event_type == "quiet_period" and e.is_active(on_date)
            for e in self._events.values()
        )

    @classmethod
    def from_yaml(cls, path: Path) -> DistributionCalendar:
        """Load calendar from YAML configuration."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cal = cls()
        calendar_data = data.get("calendar", data)
        events = calendar_data.get("events", [])
        for ev in events:
            start = ev["start_date"]
            if isinstance(start, str):
                start = date.fromisoformat(start)
            end = ev.get("end_date")
            if isinstance(end, str):
                end = date.fromisoformat(end)

            cal.add_event(CalendarEvent(
                event_id=ev["event_id"],
                name=ev["name"],
                event_type=ev["event_type"],
                start_date=start,
                end_date=end,
                posting_modifier=ev.get("posting_modifier", 1.0),
                metadata=ev.get("metadata", {}),
            ))
        return cal

    @property
    def total_events(self) -> int:
        return len(self._events)
