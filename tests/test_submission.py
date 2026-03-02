"""Tests for submission.py schema compliance — Netrik Hackathon Track 1.

These tests validate that submission.py's HRAgent produces EXACTLY the
required output format without modification.
"""

import json
import sys
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from submission import (
    HRAgent,
    Candidate,
    JobDescription,
    InterviewSlot,
    LeaveRequest,
    LeavePolicy,
    PipelineStatus,
    CONFIG,
)


# ─────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────
@pytest.fixture
def sample_jd():
    return JobDescription(
        job_id="JD_001",
        title="Senior Python Developer",
        description="Looking for experienced Python developer.",
        required_skills=["Python", "REST APIs", "Docker", "SQL", "Git"],
        preferred_skills=["Kubernetes", "AWS", "Machine Learning", "FastAPI"],
        min_experience=4.0,
    )


@pytest.fixture
def sample_candidates():
    return [
        Candidate("C001", "Priya Sharma", "priya@email.com",
                  "5 years Python, Django, REST APIs, Docker, AWS, PostgreSQL.",
                  experience_years=5.0),
        Candidate("C002", "Rahul Verma", "rahul@email.com",
                  "3 years Java, Spring Boot, MySQL. Learning Python and Docker.",
                  experience_years=3.0),
        Candidate("C003", "Anita Reddy", "anita@email.com",
                  "6 years Python, FastAPI, Kubernetes, AWS, ML, TensorFlow.",
                  experience_years=6.0),
    ]


@pytest.fixture
def sample_slots():
    base = datetime(2025, 5, 1, 10, 0, 0)
    return [
        InterviewSlot("S1", "IV1", base, base + timedelta(hours=1)),
        InterviewSlot("S2", "IV1", base + timedelta(days=1),
                      base + timedelta(days=1, hours=1)),
    ]


@pytest.fixture
def sample_leave_policy():
    return LeavePolicy(
        leave_type="casual", annual_quota=12,
        max_consecutive_days=3, min_notice_days=2,
    )


@pytest.fixture
def submission_agent(sample_candidates, sample_jd, sample_slots, sample_leave_policy):
    """Fully-exercised submission HRAgent."""
    agent = HRAgent()

    # 1. Screen resumes
    ranked = agent.screen_resumes(sample_candidates, sample_jd)

    # 2. Schedule
    agent.shortlist_and_schedule(ranked, top_n=2, slots=sample_slots)

    # 3. Questions
    agent.generate_interview_questions(sample_jd)

    # 4. Leave
    base = datetime(2025, 5, 1, 10, 0, 0)
    leave_req = LeaveRequest(
        request_id="LR001", employee_id="EMP042",
        leave_type="casual",
        start_date=base + timedelta(days=3),
        end_date=base + timedelta(days=5),
        reason="Family function",
    )
    agent.process_leave(leave_req, sample_leave_policy, balance=10)

    # 5. Pipeline transition
    if ranked:
        agent.update_pipeline_status(ranked[0].candidate_id, "interviewed")

    # 6. Escalation
    agent.handle_query("I want to file a harassment complaint")

    return agent


# ─────────────────────────────────────────────────────
# TOP-LEVEL SCHEMA TESTS
# ─────────────────────────────────────────────────────
class TestExportTopLevelSchema:
    """export_results() must return a dict with exact top-level keys."""

    def test_returns_dict(self, submission_agent):
        export = submission_agent.export_results()
        assert isinstance(export, dict), f"Expected dict, got {type(export)}"

    def test_top_level_keys(self, submission_agent):
        export = submission_agent.export_results()
        assert set(export.keys()) == {"team_id", "track", "results"}

    def test_team_id_is_string(self, submission_agent):
        export = submission_agent.export_results()
        assert isinstance(export["team_id"], str)
        assert len(export["team_id"]) > 0

    def test_track_value(self, submission_agent):
        export = submission_agent.export_results()
        assert export["track"] == "track_1_hr_agent"

    def test_results_keys(self, submission_agent):
        export = submission_agent.export_results()
        expected = {"resume_screening", "scheduling", "questionnaire",
                    "pipeline", "leave_management", "escalations"}
        assert set(export["results"].keys()) == expected

    def test_no_extra_top_keys(self, submission_agent):
        export = submission_agent.export_results()
        extra = set(export.keys()) - {"team_id", "track", "results"}
        assert extra == set(), f"Extra top-level keys: {extra}"

    def test_no_extra_results_keys(self, submission_agent):
        export = submission_agent.export_results()
        expected = {"resume_screening", "scheduling", "questionnaire",
                    "pipeline", "leave_management", "escalations"}
        extra = set(export["results"].keys()) - expected
        assert extra == set(), f"Extra result keys: {extra}"


# ─────────────────────────────────────────────────────
# RESUME SCREENING SCHEMA
# ─────────────────────────────────────────────────────
class TestResumeScreeningSchema:
    def test_has_ranked_candidates_and_scores(self, submission_agent):
        rs = submission_agent.export_results()["results"]["resume_screening"]
        assert "ranked_candidates" in rs
        assert "scores" in rs

    def test_no_extra_keys(self, submission_agent):
        rs = submission_agent.export_results()["results"]["resume_screening"]
        assert set(rs.keys()) == {"ranked_candidates", "scores"}

    def test_lists_same_length(self, submission_agent):
        rs = submission_agent.export_results()["results"]["resume_screening"]
        assert len(rs["ranked_candidates"]) == len(rs["scores"])

    def test_scores_descending(self, submission_agent):
        rs = submission_agent.export_results()["results"]["resume_screening"]
        scores = rs["scores"]
        assert scores == sorted(scores, reverse=True)

    def test_no_none_values(self, submission_agent):
        rs = submission_agent.export_results()["results"]["resume_screening"]
        assert None not in rs["ranked_candidates"]
        assert None not in rs["scores"]


# ─────────────────────────────────────────────────────
# SCHEDULING SCHEMA
# ─────────────────────────────────────────────────────
class TestSchedulingSchema:
    def test_has_required_keys(self, submission_agent):
        s = submission_agent.export_results()["results"]["scheduling"]
        assert set(s.keys()) == {"interviews_scheduled", "conflicts"}

    def test_interviews_are_list(self, submission_agent):
        s = submission_agent.export_results()["results"]["scheduling"]
        assert isinstance(s["interviews_scheduled"], list)
        assert isinstance(s["conflicts"], list)

    def test_interview_entry_keys(self, submission_agent):
        s = submission_agent.export_results()["results"]["scheduling"]
        for entry in s["interviews_scheduled"]:
            assert "candidate_id" in entry
            assert "slot_id" in entry
            assert "interviewer_id" in entry
            assert "start_time" in entry
            assert "end_time" in entry


# ─────────────────────────────────────────────────────
# QUESTIONNAIRE SCHEMA
# ─────────────────────────────────────────────────────
class TestQuestionnaireSchema:
    def test_has_questions_key(self, submission_agent):
        q = submission_agent.export_results()["results"]["questionnaire"]
        assert set(q.keys()) == {"questions"}

    def test_questions_is_list(self, submission_agent):
        q = submission_agent.export_results()["results"]["questionnaire"]
        assert isinstance(q["questions"], list)
        assert len(q["questions"]) > 0

    def test_question_entry_fields(self, submission_agent):
        q = submission_agent.export_results()["results"]["questionnaire"]
        for qn in q["questions"]:
            assert "question" in qn
            assert "type" in qn
            assert "category" in qn


# ─────────────────────────────────────────────────────
# PIPELINE SCHEMA
# ─────────────────────────────────────────────────────
class TestPipelineSchema:
    def test_has_candidates_key(self, submission_agent):
        p = submission_agent.export_results()["results"]["pipeline"]
        assert set(p.keys()) == {"candidates"}

    def test_candidates_is_dict(self, submission_agent):
        p = submission_agent.export_results()["results"]["pipeline"]
        assert isinstance(p["candidates"], dict)

    def test_all_statuses_valid(self, submission_agent):
        p = submission_agent.export_results()["results"]["pipeline"]
        valid = {s.value for s in PipelineStatus}
        for cid, status in p["candidates"].items():
            assert status in valid, f"{cid} has invalid status: {status}"


# ─────────────────────────────────────────────────────
# LEAVE MANAGEMENT SCHEMA
# ─────────────────────────────────────────────────────
class TestLeaveManagementSchema:
    def test_has_processed_requests(self, submission_agent):
        lm = submission_agent.export_results()["results"]["leave_management"]
        assert set(lm.keys()) == {"processed_requests"}

    def test_processed_requests_is_list(self, submission_agent):
        lm = submission_agent.export_results()["results"]["leave_management"]
        assert isinstance(lm["processed_requests"], list)

    def test_request_entry_keys(self, submission_agent):
        lm = submission_agent.export_results()["results"]["leave_management"]
        required = {"request_id", "employee_id", "leave_type", "start_date", "end_date",
                     "approved", "reason", "violations", "days_requested", "remaining_balance"}
        for entry in lm["processed_requests"]:
            assert required.issubset(set(entry.keys())), \
                f"Missing keys: {required - set(entry.keys())}"


# ─────────────────────────────────────────────────────
# ESCALATIONS SCHEMA
# ─────────────────────────────────────────────────────
class TestEscalationsSchema:
    def test_is_list(self, submission_agent):
        esc = submission_agent.export_results()["results"]["escalations"]
        assert isinstance(esc, list)

    def test_entry_keys(self, submission_agent):
        esc = submission_agent.export_results()["results"]["escalations"]
        for entry in esc:
            assert "query" in entry
            assert "reason" in entry
            assert "priority" in entry


# ─────────────────────────────────────────────────────
# DETERMINISM & SERIALIZATION
# ─────────────────────────────────────────────────────
class TestDeterminismAndSerialization:
    def test_json_serializable(self, submission_agent):
        export = submission_agent.export_results()
        json_str = json.dumps(export, default=str)
        reparsed = json.loads(json_str)
        assert isinstance(reparsed, dict)

    def test_deterministic_output(self, sample_candidates, sample_jd,
                                   sample_slots, sample_leave_policy):
        """Two identical runs must produce identical export."""
        base = datetime(2025, 5, 1, 10, 0, 0)

        def _run():
            cands = [
                Candidate("C001", "Priya Sharma", "priya@email.com",
                          "5 years Python, Django, REST APIs, Docker, AWS.",
                          experience_years=5.0),
                Candidate("C002", "Rahul Verma", "rahul@email.com",
                          "3 years Java, Spring Boot, MySQL. Learning Python.",
                          experience_years=3.0),
                Candidate("C003", "Anita Reddy", "anita@email.com",
                          "6 years Python, FastAPI, Kubernetes, AWS, ML.",
                          experience_years=6.0),
            ]
            slots = [
                InterviewSlot("S1", "IV1", base, base + timedelta(hours=1)),
                InterviewSlot("S2", "IV1", base + timedelta(days=1),
                              base + timedelta(days=1, hours=1)),
            ]
            jd = JobDescription(
                job_id="JD_001", title="Senior Python Developer",
                description="Looking for Python dev.",
                required_skills=["Python", "REST APIs", "Docker", "SQL", "Git"],
                preferred_skills=["Kubernetes", "AWS", "Machine Learning", "FastAPI"],
                min_experience=4.0,
            )
            agent = HRAgent()
            ranked = agent.screen_resumes(cands, jd)
            agent.shortlist_and_schedule(ranked, top_n=2, slots=slots)
            agent.generate_interview_questions(jd)
            lr = LeaveRequest("LR001", "EMP042", "casual",
                              base + timedelta(days=3), base + timedelta(days=5),
                              "Family function")
            lp = LeavePolicy("casual", 12, 3, 2)
            agent.process_leave(lr, lp, balance=10)
            return agent.export_results()

        r1 = _run()
        r2 = _run()
        assert json.dumps(r1, sort_keys=True, default=str) == \
               json.dumps(r2, sort_keys=True, default=str), \
               "Output is not deterministic"

    def test_empty_agent_export(self):
        """Fresh agent with no operations should still have valid schema."""
        agent = HRAgent()
        export = agent.export_results()
        assert set(export.keys()) == {"team_id", "track", "results"}
        results = export["results"]
        expected = {"resume_screening", "scheduling", "questionnaire",
                    "pipeline", "leave_management", "escalations"}
        assert set(results.keys()) == expected
