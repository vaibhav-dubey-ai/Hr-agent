#!/usr/bin/env python3
"""
Test harness for HR Agent - Netrik Hackathon 2026 Track 1
Comprehensive testing without manual intervention.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hr_agent.main import HRAgent
from hr_agent.state_machine import PipelineState

def test_resume_ranking():
    """Test resume ranking with MRR optimization."""
    print("\n" + "="*80)
    print("TEST 1: Resume-JD Matching & Ranking")
    print("="*80)
    
    agent = HRAgent()
    
    # Load resume data
    resume_count = agent.load_resume_data("resume_dataset_1200.csv")
    print(f"✓ Loaded {resume_count} resumes")
    
    # Test JD
    test_jd = """
    Senior Backend Developer
    
    Requirements:
    - 5+ years Python experience
    - Strong understanding of Machine Learning
    - AWS cloud architecture
    - Docker and Kubernetes
    - Natural Language Processing
    
    Skills: Python, Machine Learning, AWS, Docker, Kubernetes, NLP, REST APIs
    """
    
    # Rank resumes
    rankings = agent.rank_resumes(test_jd, top_k=10)
    print(f"\n✓ Ranked {len(rankings)} candidates")
    
    # Display top 3
    for rank, result in enumerate(rankings[:3], 1):
        print(f"\n  Rank {rank}: {result['name']}")
        print(f"    Score: {result['normalized_score']:.3f}")
        print(f"    Experience: {result['reasoning']['experience']}")
        print(f"    Degree: {result['reasoning']['degree']}")
    
    return len(rankings) > 0

def test_leave_management():
    """Test deterministic leave approval engine."""
    print("\n" + "="*80)
    print("TEST 2: Leave Policy Compliance Engine")
    print("="*80)
    
    agent = HRAgent()
    
    # Load leave data
    leave_count = agent.load_leave_data("employee leave tracking data.xlsx")
    print(f"✓ Loaded {leave_count} employee records")
    
    # Test case 1: Valid leave request
    print("\n--- Test Case 1: Valid Leave Request ---")
    result = agent.process_leave_request(
        "Michael Moore",
        "Casual",
        "2025-03-10",
        "2025-03-12",
        2
    )
    print(f"Decision: {result['decision_type']}")
    print(f"Rules Applied: {', '.join(result['applied_policy_rules'])}")
    print(f"Evidence: {list(result['evidence'].keys())}")
    assert result['decision_type'] in ['approved', 'rejected'], "Invalid decision_type"
    
    # Test case 2: Insufficient balance
    print("\n--- Test Case 2: Insufficient Balance ---")
    result2 = agent.process_leave_request(
        "Michael Moore",
        "Casual",
        "2025-04-01",
        "2025-04-20",
        100  # Way more than available
    )
    print(f"Decision: {result2['decision_type']}")
    print(f"Rules Applied: {', '.join(result2['applied_policy_rules'])}")
    assert result2['decision_type'] == 'rejected', "Should reject high days"
    
    # Test case 3: Role restrictions
    print("\n--- Test Case 3: Role Eligibility Check ---")
    result3 = agent.process_leave_request(
        "Ashley Rogers",
        "Maternity",  # Not allowed for Finance
        "2025-05-01",
        "2025-05-05",
        5
    )
    print(f"Decision: {result3['decision_type']}")
    print(f"Rules Applied: {', '.join(result3['applied_policy_rules'])}")
    
    return True

def test_scheduling():
    """Test conflict-aware scheduling."""
    print("\n" + "="*80)
    print("TEST 3: Interview Scheduling Engine")
    print("="*80)
    
    agent = HRAgent()
    
    # Register interviewer availability
    agent.register_interviewer_availability(
        "interviewer_001",
        ["2025-03-10", "2025-03-11", "2025-03-12"],
        ["10:00", "11:00", "14:00"]
    )
    print("✓ Registered interviewer availability")
    
    # Schedule interview 1
    print("\n--- Scheduling Interview 1 ---")
    result1 = agent.schedule_interview(
        "candidate_1",
        "interviewer_001",
        "2025-03-10",
        "10:00"
    )
    print(f"Status: {result1['status']}")
    print(f"Scheduled: {result1['scheduled_date']} {result1['scheduled_time']}")
    assert result1['status'] == 'success', "First scheduling should succeed"
    
    # Try to schedule same slot (should overlap)
    print("\n--- Attempting Double-Booking (should fail) ---")
    result2 = agent.schedule_interview(
        "candidate_2",
        "interviewer_001",
        "2025-03-10",
        "10:30"  # Overlaps with 10:00-11:00
    )
    print(f"Status: {result2['status']}")
    print(f"Error Code: {result2.get('error_code')}")
    print(f"Error Message: {result2.get('error_message')}")
    assert result2['status'] == 'failed', "Overlapping slot should fail"
    assert result2.get('error_code') == 'SLOT_NOT_AVAILABLE', f"Should return SLOT_NOT_AVAILABLE, got {result2.get('error_code')}"
    
    # Schedule different slot
    print("\n--- Scheduling Interview 2 (different slot) ---")
    result3 = agent.schedule_interview(
        "candidate_2",
        "interviewer_001",
        "2025-03-11",
        "14:00"
    )
    print(f"Status: {result3['status']}")
    assert result3['status'] == 'success', "Different slot should work"
    
    return True

def test_state_machine():
    """Test pipeline state management."""
    print("\n" + "="*80)
    print("TEST 4: Candidate Pipeline State Management")
    print("="*80)
    
    agent = HRAgent()
    agent.load_resume_data("resume_dataset_1200.csv")
    
    candidate_id = "candidate_0"
    
    # Valid transitions
    print("\n--- Valid State Transitions ---")
    transitions = [
        ("screened", "Initial screening passed"),
        ("interview_scheduled", "Interview scheduled"),
        ("interviewed", "Interview completed"),
        ("offer_extended", "Offer sent"),
        ("offer_accepted", "Offer accepted"),
        ("hired", "Onboarded")
    ]
    
    for new_state, reason in transitions:
        success, error_msg = agent.advance_candidate_state(candidate_id, new_state, reason)
        current = agent.get_candidate_state(candidate_id)
        allowed = current['allowed_transitions']
        print(f"  → {new_state}: {'✓' if success else '✗'} (next: {allowed})")
        assert success, f"Transition to {new_state} should succeed. Error: {error_msg}"
    
    # Try invalid transition (hired is terminal)
    print("\n--- Invalid Transition (terminal state) ---")
    success, error_msg = agent.advance_candidate_state(candidate_id, "screened")
    current = agent.get_candidate_state(candidate_id)
    allowed = current['allowed_transitions']
    print(f"  Attempt to revert from hired: {'✓ Rejected' if not success else '✗ Allowed'}")
    print(f"    Allowed transitions: {allowed}")
    assert not success, "Should not allow transition from terminal state"
    
    # Test rejection at any state
    print("\n--- Rejection at Any State ---")
    candidate_id_2 = "candidate_1"
    success, _ = agent.advance_candidate_state(candidate_id_2, "screened", "Screening passed")
    success, _ = agent.advance_candidate_state(candidate_id_2, "rejected", "Does not meet requirements")
    state = agent.get_candidate_state(candidate_id_2)
    print(f"  Rejection after screening: {'✓' if success else '✗'}")
    print(f"    Final state: {state['current_state']}, Terminal: {state['is_terminal']}")
    assert success, "Should allow rejection"
    
    return True

def test_interview_questions():
    """Test interview question generation."""
    print("\n" + "="*80)
    print("TEST 5: Interview Question Generation")
    print("="*80)
    
    agent = HRAgent()
    
    jd = """Senior Data Scientist - Machine Learning
    
    Requirements:
    - 7+ years Python, Machine Learning, Deep Learning
    - Experience with TensorFlow, PyTorch
    - Data analysis and SQL expertise
    - Cloud platforms (AWS, Azure)
    """
    
    resume = """
    Name: John Doe
    Experience: 8 years
    Skills: Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, SQL, AWS
    Education: Master's in Data Science
    """
    
    questions = agent.generate_interview_questions(jd, resume)
    
    print(f"✓ Generated {len(questions['technical'])} technical questions")
    print(f"✓ Generated {len(questions['behavioral'])} behavioral questions")
    
    # Display questions
    print("\nTechnical Questions:")
    for i, q in enumerate(questions['technical'], 1):
        print(f"  {i}. {q[:70]}...")
    
    print("\nBehavioral Questions:")
    for i, q in enumerate(questions['behavioral'], 1):
        print(f"  {i}. {q[:70]}...")
    
    return len(questions['technical']) > 0

def test_json_export():
    """Test JSON export robustness and schema compliance."""
    print("\n" + "="*80)
    print("TEST 6: JSON Export & Schema Compliance")
    print("="*80)
    
    agent = HRAgent()
    agent.load_resume_data("resume_dataset_1200.csv")
    
    # Trigger various operations
    rankings = agent.rank_resumes("Python Django Backend Developer", top_k=5)
    success, msg = agent.advance_candidate_state("candidate_5", "screened")
    
    # Register interviewer and schedule
    agent.register_interviewer_availability("interviewer_001", ["2025-03-15", "2025-03-16"], ["10:00", "11:00"])
    agent.schedule_interview("candidate_10", "interviewer_001", "2025-03-15", "10:00")
    
    # Export
    json_str = agent.export_results()
    
    # Validate JSON
    try:
        data = json.loads(json_str)
        print("✓ Valid JSON export")
        
        # Check required fields
        required_fields = ["rankings", "leave_decisions", "pipeline_history", "interview_schedules", "interview_questions"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            print(f"  ✓ {field}: {len(data[field])} items")
        
        # Check no extra fields
        extra_fields = set(data.keys()) - set(required_fields)
        if extra_fields:
            print(f"  ⚠ Extra fields found (will penalize score): {extra_fields}")
        else:
            print(f"  ✓ No extra fields")
        
        # Validate score_breakdown in rankings
        if data['rankings']:
            assert 'score_breakdown' in data['rankings'][0], "Missing score_breakdown in ranking"
            print(f"  ✓ Score breakdowns present")
        
        return True
    except json.JSONDecodeError:
        print("✗ Invalid JSON")
        return False
    except AssertionError as e:
        print(f"✗ Schema validation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "█"*80)
    print("NETRIK HACKATHON 2026 - TRACK 1: AI HR AGENT")
    print("Automated Test Suite")
    print("█"*80)
    
    tests = [
        ("Resume Ranking", test_resume_ranking),
        ("Leave Management", test_leave_management),
        ("Interview Scheduling", test_scheduling),
        ("Pipeline State Machine", test_state_machine),
        ("Interview Questions", test_interview_questions),
        ("JSON Export", test_json_export)
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
