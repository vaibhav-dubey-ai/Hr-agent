"""Edge case tests for hardened behavior."""

import pytest
import pandas as pd
from hr_agent.ranking_engine import ResumeRankingEngine
from hr_agent.state_machine import StateMachine, PipelineState
from hr_agent.scheduler import InterviewScheduler
from hr_agent.leave_engine import LeaveEngine


class TestEmptyInputs:
    """Empty / minimal inputs should not crash."""

    def test_empty_jd_text(self, ranking_engine):
        """Empty JD string should still return results (no crash)."""
        results = ranking_engine.rank_resumes("", top_k=3)
        assert isinstance(results, list)
        assert len(results) == 3

    def test_single_word_jd(self, ranking_engine):
        """Single word JD should return results."""
        results = ranking_engine.rank_resumes("Python", top_k=2)
        assert len(results) == 2

    def test_empty_resume_dataset(self):
        """Ranking on empty dataset should raise or return empty."""
        engine = ResumeRankingEngine()
        with pytest.raises((ValueError, AttributeError)):
            engine.rank_resumes("Python Engineer", top_k=5)


class TestMalformedLeaveData:
    """Malformed leave request inputs."""

    def test_malformed_start_date(self, leave_engine):
        """Non-date string for start_date should be rejected."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "not-a-date", "2025-04-11", 1)
        assert result["decision_type"] == "rejected"

    def test_malformed_end_date(self, leave_engine):
        """Non-date string for end_date should be rejected."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "garbage", 1)
        assert result["decision_type"] == "rejected"

    def test_unexpected_leave_type(self, leave_engine):
        """Unknown leave type should be rejected by role eligibility."""
        result = leave_engine.approve_leave("Alice Smith", "Bereavement", "2025-04-10", "2025-04-11", 1)
        assert result["decision_type"] == "rejected"


class TestDuplicateCandidateIds:
    """Duplicate candidate IDs handled correctly."""

    def test_duplicate_candidate_scheduling(self):
        """Same candidate cannot be scheduled twice."""
        sched = InterviewScheduler()
        sched.add_interviewer_availability("A", ["2025-05-01", "2025-05-02"], ["10:00"])
        sched.schedule_interview("cand_dup", "A", "2025-05-01", "10:00")
        result = sched.schedule_interview("cand_dup", "A", "2025-05-02", "10:00")
        assert result["status"] == "failed"
        assert result["error_code"] == "CANDIDATE_ALREADY_SCHEDULED"


class TestInvalidStateTransitions:
    """Invalid state transition strings."""

    def test_invalid_state_string(self):
        """Meaningless state string should fail."""
        sm = StateMachine("edge_test")
        success, error, _ = sm.transition("flying")
        assert not success

    def test_numeric_state(self):
        """Numeric input should fail gracefully."""
        sm = StateMachine("num_test")
        success, error, _ = sm.transition("123")
        assert not success

    def test_empty_state_string(self):
        """Empty state string should fail."""
        sm = StateMachine("empty_test")
        success, error, _ = sm.transition("")
        assert not success

    def test_same_state_transition(self):
        """Transitioning to the same state should fail."""
        sm = StateMachine("same_test")
        success, error, _ = sm.transition(PipelineState.APPLIED)
        assert not success


class TestSchedulerEdgeCases:
    """Scheduler boundary conditions."""

    def test_whitespace_only_candidate_id(self):
        sched = InterviewScheduler()
        sched.add_interviewer_availability("A", ["2025-05-01"], ["10:00"])
        result = sched.schedule_interview("   ", "A", "2025-05-01", "10:00")
        assert result["status"] == "failed"

    def test_whitespace_only_interviewer_id(self):
        sched = InterviewScheduler()
        result = sched.schedule_interview("cand_1", "  ", "2025-05-01", "10:00")
        assert result["status"] == "failed"
