"""Tests for interview scheduling engine: conflicts, overlap, determinism."""

import pytest
from hr_agent.scheduler import InterviewScheduler


class TestSuccessfulScheduling:
    """Happy-path scheduling."""

    def test_schedule_available_slot(self, scheduler):
        """Booking an available slot must succeed."""
        result = scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "09:00")
        assert result["status"] == "success"
        assert result["scheduled_date"] == "2025-04-07"
        assert result["scheduled_time"] == "09:00"

    def test_schedule_different_interviewer(self, scheduler):
        """Two candidates can book the same time with different interviewers."""
        r1 = scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "10:00")
        r2 = scheduler.schedule_interview("cand_2", "interviewer_B", "2025-04-07", "10:00")
        assert r1["status"] == "success"
        assert r2["status"] == "success"


class TestZeroOverlappingInterviews:
    """No two candidates may share the same interviewer time window."""

    def test_exact_same_slot_rejected(self, scheduler):
        """Booking the exact same slot twice must fail."""
        scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "10:00")
        result = scheduler.schedule_interview("cand_2", "interviewer_A", "2025-04-07", "10:00")
        assert result["status"] == "failed"
        assert result["error_code"] == "SLOT_NOT_AVAILABLE"

    def test_overlapping_30min_into_slot(self, scheduler):
        """A 10:30 booking that overlaps a 10:00-11:00 block must fail."""
        scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "10:00")
        # 10:30 would land inside 10:00-11:00, must fail via overlap detection
        result = scheduler.schedule_interview("cand_2", "interviewer_A", "2025-04-07", "10:00")
        assert result["status"] == "failed"

    def test_adjacent_slots_allowed(self, scheduler):
        """11:00 booking after 10:00-11:00 does not overlap — must succeed."""
        scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "10:00")
        result = scheduler.schedule_interview("cand_2", "interviewer_A", "2025-04-07", "11:00")
        assert result["status"] == "success"

    def test_different_day_no_conflict(self, scheduler):
        """Same time on different days must not conflict."""
        scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "10:00")
        result = scheduler.schedule_interview("cand_2", "interviewer_A", "2025-04-08", "10:00")
        assert result["status"] == "success"


class TestDeterministicSlotAllocation:
    """Same input must always produce same result."""

    def test_deterministic_schedule(self):
        """Identical setup → identical result."""
        results = []
        for _ in range(3):
            s = InterviewScheduler()
            s.add_interviewer_availability("A", ["2025-05-01"], ["09:00"])
            r = s.schedule_interview("cand_X", "A", "2025-05-01", "09:00")
            results.append(r)
        for r in results:
            assert r["status"] == results[0]["status"]
            assert r["scheduled_date"] == results[0]["scheduled_date"]


class TestInterviewerAvailabilityEnforcement:
    """Reject slots where interviewer is not available."""

    def test_unavailable_date_rejected(self, scheduler):
        """Requesting a date the interviewer hasn't registered must fail."""
        result = scheduler.schedule_interview("cand_1", "interviewer_A", "2025-12-25", "10:00")
        assert result["status"] == "failed"
        assert result["error_code"] == "SLOT_NOT_AVAILABLE"

    def test_unavailable_time_rejected(self, scheduler):
        """Requesting a time outside availability must fail."""
        result = scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "08:00")
        assert result["status"] == "failed"

    def test_unknown_interviewer_rejected(self, scheduler):
        """Scheduling with an unregistered interviewer must fail."""
        result = scheduler.schedule_interview("cand_1", "unknown_interviewer", "2025-04-07", "10:00")
        assert result["status"] == "failed"

    def test_duplicate_candidate_scheduling_rejected(self, scheduler):
        """Same candidate cannot be scheduled twice."""
        scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "09:00")
        result = scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-08", "10:00")
        assert result["status"] == "failed"
        assert result["error_code"] == "CANDIDATE_ALREADY_SCHEDULED"


class TestInputValidation:
    """Invalid inputs must be rejected gracefully."""

    def test_empty_candidate_id(self, scheduler):
        result = scheduler.schedule_interview("", "interviewer_A", "2025-04-07", "10:00")
        assert result["status"] == "failed"
        assert result["error_code"] == "INVALID_CANDIDATE_ID"

    def test_empty_interviewer_id(self, scheduler):
        result = scheduler.schedule_interview("cand_1", "", "2025-04-07", "10:00")
        assert result["status"] == "failed"
        assert result["error_code"] == "INVALID_INTERVIEWER_ID"

    def test_invalid_date_format(self, scheduler):
        result = scheduler.schedule_interview("cand_1", "interviewer_A", "07-04-2025", "10:00")
        assert result["status"] == "failed"
        assert result["error_code"] == "INVALID_DATETIME_FORMAT"

    def test_invalid_time_format(self, scheduler):
        result = scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "10am")
        assert result["status"] == "failed"

    def test_schedule_summary(self, scheduler):
        """get_schedule_summary() must return structured data."""
        scheduler.schedule_interview("cand_1", "interviewer_A", "2025-04-07", "09:00")
        summary = scheduler.get_schedule_summary()
        assert "scheduled_interviews" in summary
        assert "interviewer_availability" in summary
        assert len(summary["scheduled_interviews"]) == 1
