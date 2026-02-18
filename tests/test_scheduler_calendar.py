"""Tests for scheduler + calendar integration."""

from datetime import datetime, date, timedelta

from kerygma_strategy.calendar import DistributionCalendar, CalendarEvent
from kerygma_strategy.scheduler import ContentScheduler, ScheduleEntry, Frequency


def _make_calendar_with_quiet() -> DistributionCalendar:
    cal = DistributionCalendar()
    cal.add_event(CalendarEvent(
        event_id="quiet", name="Quiet", event_type="quiet_period",
        start_date=date(2026, 12, 23), end_date=date(2027, 1, 2),
        posting_modifier=0.3,
    ))
    cal.add_event(CalendarEvent(
        event_id="conf", name="Conf", event_type="conference",
        start_date=date(2026, 7, 27), end_date=date(2026, 7, 31),
        posting_modifier=1.5,
    ))
    return cal


class TestSchedulerWithCalendar:
    def test_schedule_with_calendar_quiet_period(self):
        cal = _make_calendar_with_quiet()
        sched = ContentScheduler(calendar=cal)
        entry = ScheduleEntry(
            entry_id="E1", content_id="C1", channel="mastodon",
            scheduled_time=datetime(2026, 12, 25, 10, 0),
        )
        result = sched.schedule_with_calendar(entry)
        # Should be pushed past quiet period end (Jan 3)
        assert result.scheduled_time.date() == date(2027, 1, 3)

    def test_schedule_with_calendar_normal_period(self):
        cal = _make_calendar_with_quiet()
        sched = ContentScheduler(calendar=cal)
        entry = ScheduleEntry(
            entry_id="E1", content_id="C1", channel="mastodon",
            scheduled_time=datetime(2026, 3, 15, 10, 0),
        )
        result = sched.schedule_with_calendar(entry)
        # No quiet period — should keep original time
        assert result.scheduled_time == datetime(2026, 3, 15, 10, 0)

    def test_get_due_with_priority(self):
        cal = _make_calendar_with_quiet()
        sched = ContentScheduler(calendar=cal)
        past = datetime(2026, 7, 28, 10, 0)  # During conference
        sched.schedule(ScheduleEntry(
            entry_id="E1", content_id="C1", channel="mastodon",
            scheduled_time=past,
        ))
        now = datetime(2026, 7, 29, 10, 0)
        prioritized = sched.get_due_with_priority(now)
        assert len(prioritized) == 1
        assert prioritized[0].modifier == 1.5
        assert prioritized[0].priority > 0

    def test_priority_ordering(self):
        sched = ContentScheduler()
        # E1 is more overdue than E2
        sched.schedule(ScheduleEntry(
            entry_id="E1", content_id="C1", channel="mastodon",
            scheduled_time=datetime(2026, 2, 10, 10, 0),
        ))
        sched.schedule(ScheduleEntry(
            entry_id="E2", content_id="C2", channel="discord",
            scheduled_time=datetime(2026, 2, 16, 10, 0),
        ))
        now = datetime(2026, 2, 17, 10, 0)
        prioritized = sched.get_due_with_priority(now)
        assert len(prioritized) == 2
        assert prioritized[0].entry.entry_id == "E1"  # More overdue = higher priority
