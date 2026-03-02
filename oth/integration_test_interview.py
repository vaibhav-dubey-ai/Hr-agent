#!/usr/bin/env python3
"""
Integration test for interview result endpoint (Feature 1 & 2)
Tests interview→Q&A flow and strict FSM state management.
"""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

BASE_URL = "http://localhost:8000/api"

def test_interview_selected_flow():
    """Test: Candidate selected → offer_extended + questions generated"""
    print("\n" + "="*80)
    print("TEST 1: Interview Result - SELECTED (Q&A Generated)")
    print("="*80)
    
    # Transition candidate to interviewed state first
    candidate_id = "candidate_0"
    
    transitions = ["screened", "interview_scheduled", "interviewed"]
    for state in transitions:
        response = requests.post(f"{BASE_URL}/transition", json={
            "candidate_id": candidate_id,
            "new_state": state,
            "reason": f"Moving to {state}"
        })
        print(f"  → Transitioned to {state}: {response.status_code}")
        assert response.status_code == 200
    
    # Submit interview result: SELECTED
    print("\n--- Submitting: SELECTED ---")
    response = requests.post(f"{BASE_URL}/interview-result", json={
        "candidate_id": candidate_id,
        "decision": "selected",
        "reason": "Excellent technical skills and cultural fit"
    })
    
    assert response.status_code == 200, f"Status: {response.status_code}"
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"New State: {data['new_state']}")
    print(f"Questions Generated: {data['questions_generated']}")
    
    assert data["status"] == "success"
    assert data["new_state"] == "offer_extended"
    assert data["questions_generated"] == True
    assert len(data.get("technical_questions", [])) > 0
    assert len(data.get("behavioral_questions", [])) > 0
    assert "timestamp" in data
    
    print(f"✓ Generated {len(data['technical_questions'])} technical questions")
    print(f"✓ Generated {len(data['behavioral_questions'])} behavioral questions")
    
    # Show sample questions
    if data["technical_questions"]:
        print(f"  Sample Q: {data['technical_questions'][0][:60]}...")
    
    return True


def test_interview_rejected_flow():
    """Test: Candidate rejected → rejected state (no questions)"""
    print("\n" + "="*80)
    print("TEST 2: Interview Result - REJECTED (No Q&A)")
    print("="*80)
    
    candidate_id = "candidate_1"
    
    # Transition to interviewed
    response = requests.post(f"{BASE_URL}/transition", json={
        "candidate_id": candidate_id,
        "new_state": "screened",
        "reason": "Screening passed"
    })
    print(f"  → Screened: {response.status_code}")
    
    response = requests.post(f"{BASE_URL}/transition", json={
        "candidate_id": candidate_id,
        "new_state": "interview_scheduled",
        "reason": "Interview scheduled"
    })
    print(f"  → Interview Scheduled: {response.status_code}")
    
    response = requests.post(f"{BASE_URL}/transition", json={
        "candidate_id": candidate_id,
        "new_state": "interviewed",
        "reason": "Interview completed"
    })
    print(f"  → Interviewed: {response.status_code}")
    
    # Submit interview result: REJECTED
    print("\n--- Submitting: REJECTED ---")
    response = requests.post(f"{BASE_URL}/interview-result", json={
        "candidate_id": candidate_id,
        "decision": "rejected",
        "reason": "Does not meet technical requirements"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"New State: {data['new_state']}")
    print(f"Questions Generated: {data['questions_generated']}")
    print(f"Rejection Reason: {data.get('rejection_reason')}")
    
    assert data["status"] == "success"
    assert data["new_state"] == "rejected"
    assert data["questions_generated"] == False
    assert data.get("rejection_reason") == "Does not meet technical requirements"
    
    return True


def test_strict_fsm_validation():
    """Test: Strict state machine - no skipping states"""
    print("\n" + "="*80)
    print("TEST 3: Strict FSM - Invalid Transitions Blocked")
    print("="*80)
    
    candidate_id = "candidate_2"
    
    # Try to skip from applied to interview_scheduled (should fail)
    print("\n--- Attempt: applied → interview_scheduled (invalid) ---")
    response = requests.post(f"{BASE_URL}/transition", json={
        "candidate_id": candidate_id,
        "new_state": "interview_scheduled",
        "reason": "Trying to skip screening"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"Success: {data['success']}")
    print(f"Message: {data['message']}")
    
    assert data["success"] == False
    assert "Cannot transition" in data["message"]
    
    # Now do valid transition
    print("\n--- Correct path: applied → screened ---")
    response = requests.post(f"{BASE_URL}/transition", json={
        "candidate_id": candidate_id,
        "new_state": "screened",
        "reason": "Screening passed"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    
    print("✓ Valid transition succeeded")
    
    return True


def test_terminal_states():
    """Test: Terminal states (hired, rejected) block further transitions"""
    print("\n" + "="*80)
    print("TEST 4: Terminal States (hired/rejected) Block Transitions")
    print("="*80)
    
    candidate_id = "candidate_3"
    
    # Transition to hired
    print("\n--- Fast-tracking to hired ---")
    transitions = ["screened", "interview_scheduled", "interviewed", 
                   "offer_extended", "offer_accepted", "hired"]
    
    for state in transitions:
        response = requests.post(f"{BASE_URL}/transition", json={
            "candidate_id": candidate_id,
            "new_state": state,
            "reason": f"Moving to {state}"
        })
        assert response.status_code == 200
        assert response.json()["success"] == True
    
    # Try to transition from hired (should fail)
    print("\n--- Attempt: hired → screened (invalid) ---")
    response = requests.post(f"{BASE_URL}/transition", json={
        "candidate_id": candidate_id,
        "new_state": "screened",
        "reason": "Trying to revert"
    })
    
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Message: {data['message']}")
    
    assert data["success"] == False
    assert "Cannot transition" in data["message"]
    print("✓ Terminal state prevents backward transition")
    
    return True


def test_invalid_input_validation():
    """Test: Input validation for interview-result endpoint"""
    print("\n" + "="*80)
    print("TEST 5: Input Validation")
    print("="*80)
    
    # Missing candidate_id
    print("\n--- Test: Missing candidate_id ---")
    response = requests.post(f"{BASE_URL}/interview-result", json={
        "decision": "selected",
        "reason": "Good fit"
    })
    # Should still return 422 validation error from Pydantic
    print(f"Status: {response.status_code}")
    assert response.status_code == 422
    
    # Invalid decision
    print("\n--- Test: Invalid decision (not 'selected' or 'rejected') ---")
    response = requests.post(f"{BASE_URL}/interview-result", json={
        "candidate_id": "candidate_5",
        "decision": "pending",
        "reason": "Needs review"
    })
    assert response.status_code == 200
    data = response.json()
    print(f"Error Code: {data.get('error_code')}")
    assert data["status"] == "error"
    assert "INVALID_DECISION" in data.get("error_code", "")
    
    # Nonexistent candidate
    print("\n--- Test: Nonexistent candidate ---")
    response = requests.post(f"{BASE_URL}/interview-result", json={
        "candidate_id": "candidate_99999",
        "decision": "selected",
        "reason": "Good fit"
    })
    assert response.status_code == 200
    data = response.json()
    print(f"Error Code: {data.get('error_code')}")
    assert data["status"] == "error"
    assert "NOT_FOUND" in data.get("error_code", "")
    
    return True


def test_json_robustness():
    """Test: All responses are valid JSON with correct schema"""
    print("\n" + "="*80)
    print("TEST 6: JSON Response Robustness")
    print("="*80)
    
    candidate_id = "candidate_6"
    
    # Transition to interviewed
    transitions = ["screened", "interview_scheduled", "interviewed"]
    for state in transitions:
        requests.post(f"{BASE_URL}/transition", json={
            "candidate_id": candidate_id,
            "new_state": state,
            "reason": "Moving to state"
        })
    
    # Get interview-result response
    response = requests.post(f"{BASE_URL}/interview-result", json={
        "candidate_id": candidate_id,
        "decision": "selected",
        "reason": "Great fit"
    })
    
    assert response.status_code == 200
    
    # Validate JSON structure
    try:
        data = response.json()
        
        # Check required fields
        assert "status" in data, "Missing 'status' field"
        assert "new_state" in data, "Missing 'new_state' field"
        assert "questions_generated" in data, "Missing 'questions_generated' field"
        assert "timestamp" in data, "Missing 'timestamp' field"
        
        # Validate timestamp format (ISO)
        datetime.fromisoformat(data["timestamp"])
        
        print("✓ Valid JSON structure")
        print(f"✓ All required fields present")
        print(f"✓ Timestamp is valid ISO format")
        
        return True
    
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "█"*80)
    print("INTERVIEW RESULT FEATURE - INTEGRATION TESTS")
    print("(Feature 1: Interview→Q&A Flow | Feature 2: Strict FSM)")
    print("█"*80)
    
    tests = [
        ("Interview Selected → Q&A Generation", test_interview_selected_flow),
        ("Interview Rejected → No Q&A", test_interview_rejected_flow),
        ("Strict FSM - Invalid Transitions", test_strict_fsm_validation),
        ("Terminal States Block Transitions", test_terminal_states),
        ("Input Validation", test_invalid_input_validation),
        ("JSON Response Robustness", test_json_robustness),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ PASSED: {test_name}")
            else:
                failed += 1
                print(f"\n✗ FAILED: {test_name}")
        except AssertionError as e:
            failed += 1
            print(f"\n✗ FAILED: {test_name}")
            print(f"   Assertion: {str(e)}")
        except Exception as e:
            failed += 1
            print(f"\n✗ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
    
    # Summary
    print("\n" + "█"*80)
    print("TEST SUMMARY")
    print("█"*80)
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Total:  {passed + failed}")
    print("█"*80 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
