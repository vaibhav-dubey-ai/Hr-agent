"""Full lifecycle integration test: Ranking → Screening → Scheduling → Interview → Hired → Leave → Export."""

import json
import pytest


class TestFullHiringLifecycle:
    """End-to-end hiring pipeline integration test."""

    def test_complete_lifecycle(self, hr_agent):
        """
        Full lifecycle:
        1. Rank resumes against JD
        2. Screen top candidate (applied → screened)
        3. Register interviewer & schedule interview
        4. Mark interviewed
        5. Extend offer
        6. Accept offer
        7. Hire
        8. Process leave request for existing employee
        9. Export all results and validate schema
        """
        # 1. RANK
        jd = "Senior Python Machine Learning Engineer with AWS experience"
        rankings = hr_agent.rank_resumes(jd, top_k=5)
        assert len(rankings) == 5
        top_candidate = rankings[0]["candidate_id"]

        # 2. SCREEN
        success, err = hr_agent.advance_candidate_state(top_candidate, "screened", "Strong resume")
        assert success, f"Screening failed: {err}"

        # 3. SCHEDULE
        hr_agent.register_interviewer_availability("lead_1", ["2025-05-01"], ["10:00"])
        schedule = hr_agent.schedule_interview(top_candidate, "lead_1", "2025-05-01", "10:00")
        assert schedule["status"] == "success"

        success, err = hr_agent.advance_candidate_state(top_candidate, "interview_scheduled", "Scheduled")
        assert success

        # 4. INTERVIEW
        success, err = hr_agent.advance_candidate_state(top_candidate, "interviewed", "Completed")
        assert success

        # Generate interview questions
        questions = hr_agent.generate_interview_questions(jd)
        assert len(questions["technical"]) >= 3
        assert len(questions["behavioral"]) >= 3

        # 5. OFFER
        success, err = hr_agent.advance_candidate_state(top_candidate, "offer_extended", "Good fit")
        assert success

        # 6. ACCEPT
        success, err = hr_agent.advance_candidate_state(top_candidate, "offer_accepted", "Accepted")
        assert success

        # 7. HIRED
        success, err = hr_agent.advance_candidate_state(top_candidate, "hired", "Onboarded")
        assert success

        # Verify terminal state
        state = hr_agent.get_candidate_state(top_candidate)
        assert state["current_state"] == "hired"
        assert state["is_terminal"] is True

        # 8. LEAVE REQUEST
        leave = hr_agent.process_leave_request("Alice Smith", "Casual", "2025-06-01", "2025-06-02", 2)
        assert leave["decision_type"] in ("approved", "rejected")

        # 9. EXPORT
        export_json = hr_agent.export_results()
        data = json.loads(export_json)
        required = {"rankings", "leave_decisions", "pipeline_history", "interview_schedules", "interview_questions"}
        assert required.issubset(set(data.keys()))
        assert len(data["rankings"]) == 5
        assert len(data["leave_decisions"]) == 1
        assert len(data["pipeline_history"]) >= 1
        assert len(data["interview_schedules"]) == 1
        assert len(data["interview_questions"]) >= 1

    def test_rejection_lifecycle(self, hr_agent):
        """Candidate rejected mid-pipeline → verify terminal."""
        jd = "Data Analyst with SQL"
        rankings = hr_agent.rank_resumes(jd, top_k=3)
        candidate = rankings[1]["candidate_id"]

        hr_agent.advance_candidate_state(candidate, "screened", "Reviewed")
        hr_agent.advance_candidate_state(candidate, "interview_scheduled", "Scheduled")
        success, err = hr_agent.advance_candidate_state(candidate, "rejected", "Failed interview")
        assert success

        state = hr_agent.get_candidate_state(candidate)
        assert state["current_state"] == "rejected"
        assert state["is_terminal"] is True

        # Verify no further transitions possible
        success, err = hr_agent.advance_candidate_state(candidate, "interviewed", "Retry")
        assert not success

    def test_leave_approval_and_rejection(self, hr_agent):
        """Test approval followed by a conflicting request."""
        # First: approve
        result1 = hr_agent.process_leave_request("Carol White", "Annual", "2025-07-01", "2025-07-05", 5)
        assert result1["decision_type"] == "approved"

        # Second: overlap → reject
        result2 = hr_agent.process_leave_request("Carol White", "Casual", "2025-07-03", "2025-07-07", 3)
        assert result2["decision_type"] == "rejected"

    def test_multiple_interviewers_no_conflict(self, hr_agent):
        """Two interviewers can schedule same time independently."""
        hr_agent.register_interviewer_availability("int_X", ["2025-08-01"], ["09:00"])
        hr_agent.register_interviewer_availability("int_Y", ["2025-08-01"], ["09:00"])

        r1 = hr_agent.schedule_interview("candidate_0", "int_X", "2025-08-01", "09:00")
        r2 = hr_agent.schedule_interview("candidate_1", "int_Y", "2025-08-01", "09:00")
        assert r1["status"] == "success"
        assert r2["status"] == "success"
