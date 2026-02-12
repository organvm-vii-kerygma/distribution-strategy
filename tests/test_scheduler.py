"""Tests for the scheduler module."""
from datetime import datetime, timedelta
from src.scheduler import ContentScheduler, ScheduleEntry, Frequency

def test_schedule_entry_is_due():
    past = datetime.now() - timedelta(hours=1)
    entry = ScheduleEntry(entry_id="E1", content_id="C1", channel="mastodon", scheduled_time=past)
    assert entry.is_due() is True

def test_schedule_entry_not_due():
    future = datetime.now() + timedelta(hours=1)
    entry = ScheduleEntry(entry_id="E1", content_id="C1", channel="mastodon", scheduled_time=future)
    assert entry.is_due() is False

def test_scheduler_get_due():
    sched = ContentScheduler()
    past = datetime.now() - timedelta(hours=1)
    future = datetime.now() + timedelta(hours=1)
    sched.schedule(ScheduleEntry(entry_id="E1", content_id="C1", channel="ch1", scheduled_time=past))
    sched.schedule(ScheduleEntry(entry_id="E2", content_id="C2", channel="ch2", scheduled_time=future))
    due = sched.get_due()
    assert len(due) == 1
    assert due[0].entry_id == "E1"

def test_publish_creates_next_for_recurring():
    sched = ContentScheduler()
    t = datetime.now() - timedelta(hours=1)
    sched.schedule(ScheduleEntry(entry_id="E1", content_id="C1", channel="ch1", scheduled_time=t, frequency=Frequency.WEEKLY))
    sched.publish_entry("E1")
    assert sched.total_entries == 2
    assert sched.pending_count == 1
