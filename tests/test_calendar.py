"""Tests for the calendar module."""

from datetime import date
from pathlib import Path

from kerygma_strategy.calendar import DistributionCalendar, CalendarEvent

FIXTURES = Path(__file__).parent / "fixtures"


class TestCalendarEvent:
    def test_is_active_single_day(self):
        ev = CalendarEvent(
            event_id="e1", name="Test", event_type="grant_deadline",
            start_date=date(2026, 4, 15),
        )
        assert ev.is_active(date(2026, 4, 15)) is True
        assert ev.is_active(date(2026, 4, 16)) is False

    def test_is_active_range(self):
        ev = CalendarEvent(
            event_id="e1", name="Conf", event_type="conference",
            start_date=date(2026, 7, 27), end_date=date(2026, 7, 31),
        )
        assert ev.is_active(date(2026, 7, 28)) is True
        assert ev.is_active(date(2026, 8, 1)) is False

    def test_days_until(self):
        ev = CalendarEvent(
            event_id="e1", name="Test", event_type="grant_deadline",
            start_date=date(2026, 4, 15),
        )
        assert ev.days_until(date(2026, 4, 10)) == 5
        assert ev.days_until(date(2026, 4, 20)) == -5


class TestDistributionCalendar:
    def test_add_and_get(self):
        cal = DistributionCalendar()
        ev = CalendarEvent(event_id="e1", name="Test", event_type="grant_deadline",
                          start_date=date(2026, 4, 15))
        cal.add_event(ev)
        assert cal.get_event("e1") is not None

    def test_get_active_events(self):
        cal = DistributionCalendar()
        cal.add_event(CalendarEvent("e1", "Active", "conference",
                                    date(2026, 7, 27), date(2026, 7, 31)))
        cal.add_event(CalendarEvent("e2", "Inactive", "grant_deadline",
                                    date(2026, 4, 15)))
        active = cal.get_active_events(date(2026, 7, 29))
        assert len(active) == 1
        assert active[0].event_id == "e1"

    def test_posting_modifier(self):
        cal = DistributionCalendar()
        cal.add_event(CalendarEvent("e1", "Conf", "conference",
                                    date(2026, 7, 27), date(2026, 7, 31),
                                    posting_modifier=1.5))
        assert cal.get_posting_modifier(date(2026, 7, 29)) == 1.5
        assert cal.get_posting_modifier(date(2026, 8, 1)) == 1.0

    def test_is_quiet_period(self):
        cal = DistributionCalendar()
        cal.add_event(CalendarEvent("qp", "Quiet", "quiet_period",
                                    date(2026, 12, 23), date(2027, 1, 2),
                                    posting_modifier=0.3))
        assert cal.is_quiet_period(date(2026, 12, 25)) is True
        assert cal.is_quiet_period(date(2026, 12, 22)) is False

    def test_get_upcoming(self):
        cal = DistributionCalendar()
        cal.add_event(CalendarEvent("e1", "Soon", "conference",
                                    date(2026, 3, 1)))
        cal.add_event(CalendarEvent("e2", "Far", "conference",
                                    date(2026, 12, 1)))
        upcoming = cal.get_upcoming(days=30, from_date=date(2026, 2, 15))
        assert len(upcoming) == 1
        assert upcoming[0].event_id == "e1"

    def test_from_yaml(self):
        cal = DistributionCalendar.from_yaml(FIXTURES / "sample_calendar.yaml")
        assert cal.total_events == 3
        knight = cal.get_event("knight-2026")
        assert knight is not None
        assert knight.posting_modifier == 1.5

    def test_multiple_modifiers_multiply(self):
        cal = DistributionCalendar()
        cal.add_event(CalendarEvent("e1", "A", "conference",
                                    date(2026, 7, 27), date(2026, 7, 31),
                                    posting_modifier=1.5))
        cal.add_event(CalendarEvent("e2", "B", "grant_deadline",
                                    date(2026, 7, 29),
                                    posting_modifier=2.0))
        assert cal.get_posting_modifier(date(2026, 7, 29)) == 3.0
