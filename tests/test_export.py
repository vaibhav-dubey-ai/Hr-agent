"""Tests for export_results() JSON schema compliance."""

import json
import pytest


EXPORT_REQUIRED_KEYS = {"rankings", "leave_decisions", "pipeline_history", "interview_schedules", "interview_questions"}


class TestStrictJsonSchema:
    """export_results() must produce strict JSON with exactly the required keys."""

    def test_valid_json(self, hr_agent):
        """Export must produce valid JSON."""
        json_str = hr_agent.export_results()
        data = json.loads(json_str)
        assert isinstance(data, dict)

    def test_required_keys_present(self, hr_agent):
        """All 5 required keys must be present."""
        data = json.loads(hr_agent.export_results())
        assert EXPORT_REQUIRED_KEYS.issubset(set(data.keys()))

    def test_no_extra_keys(self, hr_agent):
        """No extra keys beyond the 5 required ones."""
        data = json.loads(hr_agent.export_results())
        extra = set(data.keys()) - EXPORT_REQUIRED_KEYS
        assert extra == set(), f"Extra keys found: {extra}"

    def test_all_values_are_lists(self, hr_agent):
        """All top-level values must be lists."""
        data = json.loads(hr_agent.export_results())
        for key in EXPORT_REQUIRED_KEYS:
            assert isinstance(data[key], list), f"{key} must be a list"


class TestExportAfterOperations:
    """Export must capture data from all operations."""

    def test_rankings_in_export(self, hr_agent):
        """After ranking, export must contain ranking entries."""
        hr_agent.rank_resumes("Python Machine Learning Engineer", top_k=3)
        data = json.loads(hr_agent.export_results())
        assert len(data["rankings"]) == 3

    def test_ranking_entry_schema(self, hr_agent):
        """Each ranking entry must have required fields."""
        hr_agent.rank_resumes("Python Engineer", top_k=2)
        data = json.loads(hr_agent.export_results())
        for r in data["rankings"]:
            assert "rank" in r
            assert "candidate_id" in r
            assert "score" in r
            assert "score_breakdown" in r
            assert "reasoning" in r

    def test_leave_decisions_in_export(self, hr_agent):
        """After leave processing, export must contain leave decisions."""
        hr_agent.process_leave_request("Alice Smith", "Casual", "2025-04-10", "2025-04-11", 2)
        data = json.loads(hr_agent.export_results())
        assert len(data["leave_decisions"]) == 1
        d = data["leave_decisions"][0]
        assert "employee_name" in d
        assert "decision_type" in d
        assert "applied_policy_rules" in d
        assert "evidence" in d

    def test_pipeline_in_export(self, hr_agent):
        """After state transitions, export must contain pipeline history."""
        hr_agent.advance_candidate_state("candidate_0", "screened", "Reviewed")
        data = json.loads(hr_agent.export_results())
        assert len(data["pipeline_history"]) >= 1
        p = data["pipeline_history"][0]
        assert "candidate_id" in p
        assert "current_state" in p
        assert "history" in p

    def test_schedules_in_export(self, hr_agent):
        """After scheduling, export must contain interview schedules."""
        hr_agent.register_interviewer_availability("int_A", ["2025-05-01"], ["10:00"])
        hr_agent.schedule_interview("candidate_0", "int_A", "2025-05-01", "10:00")
        data = json.loads(hr_agent.export_results())
        assert len(data["interview_schedules"]) == 1
        s = data["interview_schedules"][0]
        assert "candidate_id" in s
        assert "interviewer_id" in s
        assert "status" in s

    def test_empty_export(self, hr_agent):
        """Fresh agent export with no operations must have empty lists."""
        data = json.loads(hr_agent.export_results())
        for key in EXPORT_REQUIRED_KEYS:
            assert data[key] == []
