"""Tests for leave engine: balance, eligibility, overlap, evidence."""

import pytest


class TestBalanceValidation:
    """Leave balance must never underflow."""

    def test_sufficient_balance_approved(self, leave_engine):
        """Request within balance must be approved."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "2025-04-11", 2)
        assert result["decision_type"] == "approved"

    def test_insufficient_balance_rejected(self, leave_engine):
        """Request exceeding balance must be rejected."""
        result = leave_engine.approve_leave("Bob Jones", "Casual", "2025-04-10", "2025-04-20", 10)
        assert result["decision_type"] == "rejected"
        assert "RULE_INSUFFICIENT_BALANCE" in result["applied_policy_rules"]

    def test_balance_decremented_after_approval(self, leave_engine):
        """After approval, remaining balance must decrease."""
        before = leave_engine.employee_data["Alice Smith"]["remaining"]
        leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "2025-04-11", 2)
        after = leave_engine.employee_data["Alice Smith"]["remaining"]
        assert after == before - 2

    def test_no_balance_underflow_on_successive_requests(self, leave_engine):
        """Approve first, then second request that would exceed remaining → reject."""
        leave_engine.approve_leave("Dave Brown", "Casual", "2025-04-10", "2025-04-10", 1)
        # Dave had 1 remaining, now has 0
        result = leave_engine.approve_leave("Dave Brown", "Casual", "2025-04-15", "2025-04-15", 1)
        assert result["decision_type"] == "rejected"

    def test_zero_balance_rejected(self, leave_engine):
        """Request with exactly 0 remaining must be rejected."""
        leave_engine.employee_data["Bob Jones"]["remaining"] = 0
        result = leave_engine.approve_leave("Bob Jones", "Casual", "2025-05-01", "2025-05-01", 1)
        assert result["decision_type"] == "rejected"


class TestRoleEligibility:
    """Role-based leave type restrictions."""

    def test_allowed_leave_type(self, leave_engine):
        """IT employee requesting Casual leave should pass eligibility."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-05-01", "2025-05-02", 2)
        assert "RULE_ROLE_ELIGIBILITY_PASSED" in result["applied_policy_rules"]

    def test_maternity_for_hr_allowed(self, leave_engine):
        """HR employees are eligible for Maternity leave."""
        result = leave_engine.approve_leave("Carol White", "Maternity", "2025-06-01", "2025-06-10", 10)
        assert result["decision_type"] == "approved"

    def test_maternity_for_it_rejected(self, leave_engine):
        """IT employees are NOT eligible for Maternity leave."""
        result = leave_engine.approve_leave("Alice Smith", "Maternity", "2025-06-01", "2025-06-05", 5)
        assert result["decision_type"] == "rejected"
        assert "RULE_ROLE_INELIGIBLE" in result["applied_policy_rules"]

    def test_maternity_for_finance_rejected(self, leave_engine):
        """Finance employees are NOT eligible for Maternity leave."""
        result = leave_engine.approve_leave("Bob Jones", "Maternity", "2025-06-01", "2025-06-02", 1)
        assert result["decision_type"] == "rejected"


class TestDateOverlap:
    """Overlapping leave dates must be detected."""

    def test_no_overlap_first_request(self, leave_engine):
        """First leave request should not have overlap."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "2025-04-11", 2)
        assert result["evidence"]["date_overlap_check"]["passed"] is True

    def test_overlapping_dates_rejected(self, leave_engine):
        """Second request overlapping first approved dates must be rejected."""
        leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "2025-04-14", 5)
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-12", "2025-04-16", 3)
        assert result["decision_type"] == "rejected"
        assert "RULE_DATE_OVERLAP" in result["applied_policy_rules"]

    def test_adjacent_dates_allowed(self, leave_engine):
        """Non-overlapping adjacent dates must be allowed."""
        leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "2025-04-11", 2)
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-12", "2025-04-14", 3)
        assert result["decision_type"] == "approved"


class TestStructuredEvidence:
    """Evidence dict must be complete and structured."""

    def test_approved_evidence_complete(self, leave_engine):
        """Approved decision must have all evidence sections."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "2025-04-11", 2)
        assert "date_validation" in result["evidence"]
        assert "balance_check" in result["evidence"]
        assert "role_eligibility_check" in result["evidence"]
        assert "date_overlap_check" in result["evidence"]

    def test_evidence_balance_has_required_available(self, leave_engine):
        """Balance evidence must report required vs available."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-10", "2025-04-11", 2)
        bc = result["evidence"]["balance_check"]
        assert "required" in bc
        assert "available" in bc
        assert "passed" in bc

    def test_invalid_date_format_rejected(self, leave_engine):
        """Malformed date string must be rejected with proper rule."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "10-04-2025", "2025-04-11", 1)
        assert result["decision_type"] == "rejected"
        assert "RULE_INVALID_DATE_FORMAT" in result["applied_policy_rules"]

    def test_start_after_end_rejected(self, leave_engine):
        """Start date after end date must be rejected."""
        result = leave_engine.approve_leave("Alice Smith", "Casual", "2025-04-15", "2025-04-10", 1)
        assert result["decision_type"] == "rejected"
        assert "RULE_INVALID_DATE_RANGE" in result["applied_policy_rules"]

    def test_unknown_employee_rejected(self, leave_engine):
        """Non-existent employee must be rejected."""
        result = leave_engine.approve_leave("Unknown Person", "Casual", "2025-04-10", "2025-04-11", 1)
        assert result["decision_type"] == "rejected"
        assert "RULE_EMPLOYEE_NOT_FOUND" in result["applied_policy_rules"]
