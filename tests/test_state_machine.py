"""Tests for FSM (Finite State Machine) pipeline enforcement."""

import pytest
from hr_agent.state_machine import StateMachine, PipelineState


class TestValidTransitions:
    """Verify full happy-path pipeline works."""

    def test_full_pipeline_applied_to_hired(self, state_machine):
        """Complete pipeline: applied → screened → ... → hired."""
        transitions = [
            PipelineState.SCREENED,
            PipelineState.INTERVIEW_SCHEDULED,
            PipelineState.INTERVIEWED,
            PipelineState.OFFER_EXTENDED,
            PipelineState.OFFER_ACCEPTED,
            PipelineState.HIRED,
        ]
        for target in transitions:
            success, error, allowed = state_machine.transition(target)
            assert success, f"Transition to {target.value} failed: {error}"
        assert state_machine.get_current_state() == "hired"

    def test_rejection_from_every_non_terminal_state(self):
        """Rejection must be allowed from every non-terminal state."""
        pre_states = [
            PipelineState.APPLIED,
            PipelineState.SCREENED,
            PipelineState.INTERVIEW_SCHEDULED,
            PipelineState.INTERVIEWED,
            PipelineState.OFFER_EXTENDED,
            PipelineState.OFFER_ACCEPTED,
        ]
        for pre in pre_states:
            sm = StateMachine(f"test_{pre.value}")
            # Advance to the target state
            seq = list(StateMachine.STATE_SEQUENCE)
            idx = seq.index(pre)
            for s in seq[1 : idx + 1]:
                sm.transition(s)
            assert sm.get_current_state() == pre.value
            success, error, _ = sm.transition(PipelineState.REJECTED)
            assert success, f"Rejection from {pre.value} should succeed: {error}"
            assert sm.get_current_state() == "rejected"


class TestNoSkipping:
    """No skipping states: must progress one step at a time."""

    @pytest.mark.parametrize(
        "skip_to",
        [
            PipelineState.INTERVIEW_SCHEDULED,
            PipelineState.INTERVIEWED,
            PipelineState.OFFER_EXTENDED,
            PipelineState.HIRED,
        ],
    )
    def test_cannot_skip_from_applied(self, skip_to):
        """Skipping directly from applied to later states must fail."""
        sm = StateMachine("skip_test")
        success, error, allowed = sm.transition(skip_to)
        assert not success
        assert "Cannot transition" in error


class TestNoReverting:
    """No backward transitions allowed."""

    def test_cannot_revert_screened_to_applied(self):
        """Once screened, cannot go back to applied."""
        sm = StateMachine("revert_test")
        sm.transition(PipelineState.SCREENED)
        success, error, _ = sm.transition(PipelineState.APPLIED)
        assert not success

    def test_cannot_revert_interviewed_to_screened(self):
        """Once interviewed, cannot go back to screened."""
        sm = StateMachine("revert_test_2")
        sm.transition(PipelineState.SCREENED)
        sm.transition(PipelineState.INTERVIEW_SCHEDULED)
        sm.transition(PipelineState.INTERVIEWED)
        success, error, _ = sm.transition(PipelineState.SCREENED)
        assert not success


class TestTerminalStates:
    """Terminal states block all transitions."""

    def test_hired_is_terminal(self, state_machine):
        """Once hired, no further transitions allowed."""
        for s in [
            PipelineState.SCREENED,
            PipelineState.INTERVIEW_SCHEDULED,
            PipelineState.INTERVIEWED,
            PipelineState.OFFER_EXTENDED,
            PipelineState.OFFER_ACCEPTED,
            PipelineState.HIRED,
        ]:
            state_machine.transition(s)
        assert state_machine.is_terminal_state()
        for target in PipelineState:
            success, _, _ = state_machine.transition(target)
            assert not success, f"Hired should block transition to {target.value}"

    def test_rejected_is_terminal(self):
        """Once rejected, no further transitions allowed."""
        sm = StateMachine("rejected_test")
        sm.transition(PipelineState.REJECTED)
        assert sm.is_terminal_state()
        for target in PipelineState:
            success, _, _ = sm.transition(target)
            assert not success, f"Rejected should block transition to {target.value}"


class TestTransitionLogs:
    """Transition history must be stored."""

    def test_history_populated(self, state_machine):
        """Each transition must add an entry to history."""
        assert len(state_machine.get_history()) == 1  # initial
        state_machine.transition(PipelineState.SCREENED, "screening done")
        history = state_machine.get_history()
        assert len(history) == 2
        assert history[1]["state"] == "screened"
        assert "timestamp" in history[1]

    def test_history_preserves_reason(self, state_machine):
        """Reason string must appear in history entry."""
        state_machine.transition(PipelineState.SCREENED, "Resume reviewed")
        entry = state_machine.get_history()[-1]
        assert entry["reason"] == "Resume reviewed"

    def test_to_dict_contains_all_fields(self, state_machine):
        """to_dict() must expose candidate_id, current_state, is_terminal, allowed_transitions, history."""
        d = state_machine.to_dict()
        required = {"candidate_id", "current_state", "is_terminal", "allowed_transitions", "history"}
        assert required.issubset(set(d.keys()))

    def test_allowed_transitions_accurate(self, state_machine):
        """get_allowed_transitions() must match VALID_TRANSITIONS."""
        allowed = state_machine.get_allowed_transitions()
        assert "screened" in allowed
        assert "rejected" in allowed
        assert "hired" not in allowed

    def test_string_state_transition(self):
        """Transition via string value should work."""
        sm = StateMachine("str_test")
        success, error, _ = sm.transition("screened")
        assert success

    def test_invalid_string_state(self):
        """Invalid string state should return error."""
        sm = StateMachine("invalid_str_test")
        success, error, allowed = sm.transition("nonexistent_state")
        assert not success
