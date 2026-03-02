#!/usr/bin/env python3
"""
Demo script showcasing HR Agent capabilities.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hr_agent.main import HRAgent

def demo():
    print("\n" + "="*80)
    print("AI HR AGENT - LIVE DEMONSTRATION")
    print("="*80)
    
    agent = HRAgent()
    
    # 1. Load data
    print("\n[PHASE 1] Loading Data...")
    print("-" * 80)
    resume_count = agent.load_resume_data("resume_dataset_1200.csv")
    leave_count = agent.load_leave_data("employee leave tracking data.xlsx")
    print(f"✓ Loaded {resume_count} resumes")
    print(f"✓ Loaded {leave_count} employee leave records")
    
    # 2. Demonstrate resume ranking
    print("\n[PHASE 2] Resume-JD Matching & Ranking (MRR Optimized)...")
    print("-" * 80)
    
    jd = """
    Senior Machine Learning Engineer
    
    Requirements:
    - 5+ years Python programming
    - Expertise in Machine Learning and Deep Learning
    - TensorFlow or PyTorch experience
    - Cloud platforms (AWS/Azure/GCP)
    - Data Analysis and SQL
    
    Responsibilities:
    - Design and implement ML models
    - Optimize algorithms for production
    - Collaborate with data engineers
    - Publish research and insights
    """
    
    rankings = agent.rank_resumes(jd, top_k=5)
    print(f"\nRanked candidates for: 'Senior Machine Learning Engineer'\n")
    for result in rankings:
        print(f"  #{result['rank']} - {result['name']}")
        print(f"      Score: {result['normalized_score']:.1%}")
        print(f"      Experience: {result['reasoning']['experience']}")
        print(f"      Education: {result['reasoning']['degree']}")
        print(f"      Match Confidence: {float(result['reasoning']['embedding_match']):.2f}")
        print()
    
    # 3. Demonstrate leave approval
    print("\n[PHASE 3] Leave Policy Compliance...")
    print("-" * 80)
    print("\nProcessing leave requests with deterministic rules:\n")
    
    leave_cases = [
        ("Michael Moore", "Casual", "2025-03-15", "2025-03-17", 2),
        ("Ashley Rogers", "Casual", "2025-04-01", "2025-04-30", 15),
    ]
    
    for emp_name, leave_type, start, end, days in leave_cases:
        result = agent.process_leave_request(emp_name, leave_type, start, end, days)
        status_icon = "✓" if result['status'] == 'approved' else "✗"
        print(f"{status_icon} {emp_name} - {leave_type} ({days} days)")
        print(f"   Result: {result['status'].upper()}")
        print(f"   Reason: {result['reason']}")
        print()
    
    # 4. Demonstrate scheduling
    print("\n[PHASE 4] Conflict-Aware Interview Scheduling...")
    print("-" * 80)
    print("\nRegistering interviewer availability...")
    
    agent.register_interviewer_availability(
        "interviewer_alice",
        ["2025-03-20", "2025-03-21", "2025-03-22"],
        ["10:00", "14:00", "16:00"]
    )
    agent.register_interviewer_availability(
        "interviewer_bob",
        ["2025-03-20", "2025-03-21", "2025-03-22"],
        ["11:00", "15:00"]
    )
    print("✓ Registered 2 interviewers with 11 available slots\n")
    
    print("Scheduling interviews...")
    interviews = [
        ("candidate_5", "interviewer_alice", "2025-03-20", "10:00"),
        ("candidate_10", "interviewer_alice", "2025-03-20", "14:00"),
        ("candidate_15", "interviewer_alice", "2025-03-20", "10:00"),  # Will conflict
        ("candidate_20", "interviewer_bob", "2025-03-21", "11:00"),
    ]
    
    for cand_id, interview_id, date, time in interviews:
        result = agent.schedule_interview(cand_id, interview_id, date, time)
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {cand_id} with {interview_id} on {date} at {time}")
        if result['status'] != 'success':
            print(f"   Reason: {result['reason']}")
    
    # 5. Demonstrate state machine
    print("\n\n[PHASE 5] Pipeline State Management...")
    print("-" * 80)
    print("\nMoving candidate through pipeline...\n")
    
    cand_id = "candidate_5"
    transitions = [
        ("screened", "CV screening passed"),
        ("interview_scheduled", "Interview confirmed"),
        ("interviewed", "Interview completed, strong performance"),
        ("offer_extended", "Offer sent to candidate"),
    ]
    
    print(f"Candidate: {cand_id}\n")
    for new_state, reason in transitions:
        success = agent.advance_candidate_state(cand_id, new_state, reason)
        status = "✓" if success else "✗"
        print(f"{status} → {new_state}")
        print(f"   Reason: {reason}")
    
    state = agent.get_candidate_state(cand_id)
    print(f"\nCurrent State: {state['current_state'].upper()}")
    print(f"Pipeline History: {len(state['history'])} transitions")
    
    # 6. Demonstrate interview questions
    print("\n\n[PHASE 6] Context-Aware Interview Questions...")
    print("-" * 80)
    
    resume = """
    Name: Sarah Kumar
    Experience: 6 years Python, Machine Learning
    Skills: Python, TensorFlow, PyTorch, Data Analysis, SQL, AWS
    Certifications: Google Cloud Professional, TensorFlow Developer Certificate
    Education: Master's in Computer Science
    """
    
    questions = agent.generate_interview_questions(jd, resume)
    
    print(f"\nInterview Plan for: Sarah Kumar\n")
    print("Technical Questions (Role-Specific):")
    for i, q in enumerate(questions['technical'], 1):
        print(f"  {i}. {q}")
    
    print("\nBehavioral Questions (Standard):")
    for i, q in enumerate(questions['behavioral'], 1):
        print(f"  {i}. {q}")
    
    # 7. Export results
    print("\n\n[PHASE 7] Exporting Results...")
    print("-" * 80)
    
    json_output = agent.export_results()
    data = json.loads(json_output)
    
    print(f"\n✓ JSON Export Summary:")
    print(f"  - Top Resume Rankings: {len(data['rankings'])}")
    print(f"  - Scheduled Interviews: {len(data['schedules'])}")
    print(f"  - Leave Decisions: {len(data['leave_decisions'])}")
    print(f"  - Pipeline State Changes: {len(data['pipeline_states'])}")
    print(f"  - Interview Question Sets: {len(data['interview_questions'])}")
    
    print("\n✓ Sample JSON Structure (Rankings):")
    if data['rankings']:
        print(json.dumps(data['rankings'][0], indent=2)[:500] + "...\n")
    
    print("\n" + "="*80)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(demo())
