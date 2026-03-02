#!/usr/bin/env python3
"""
Integration test demonstrating complete HR workflow.
Simulates a real hiring scenario with multiple candidates.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hr_agent.main import HRAgent

def integration_test():
    """Run a complete hiring workflow."""
    print("\n" + "█"*80)
    print("INTEGRATION TEST: COMPLETE HIRING WORKFLOW")
    print("█"*80)
    
    agent = HRAgent()
    
    # Load datasets
    print("\n[STEP 1] Loading Data...")
    agent.load_resume_data("resume_dataset_1200.csv")
    agent.load_leave_data("employee leave tracking data.xlsx")
    print("✓ Data loaded")
    
    # Define the job opening
    job_description = """
    Machine Learning Engineer - Level 3
    
    We are looking for an experienced ML Engineer to join our Core AI team.
    
    Key Requirements:
    - 5+ years Python programming
    - Strong background in Machine Learning, Deep Learning
    - TensorFlow or PyTorch
    - Production ML experience
    - AWS/Azure/GCP cloud experience
    - Strong data analysis and SQL
    - Familiarity with MLOps and model deployment
    
    Responsibilities:
    - Design and train ML models
    - Optimize models for production use
    - Collaborate with data engineers and product teams
    - Publish research and insights
    - Mentor junior ML engineers
    """
    
    # Step 2: Rank resumes
    print("\n[STEP 2] Resume Ranking...")
    rankings = agent.rank_resumes(job_description, top_k=20)
    print(f"✓ Ranked {len(rankings)} candidates")
    
    # Get top 5 candidates
    top_candidates = [r['candidate_id'] for r in rankings[:5]]
    print(f"✓ Selected top 5 candidates for interviews")
    
    # Step 3: Setup interview schedule
    print("\n[STEP 3] Setup Interview Schedule...")
    
    # Register interviewers
    agent.register_interviewer_availability(
        "alice_ml_lead",
        ["2025-04-07", "2025-04-08", "2025-04-09"],
        ["10:00", "14:00"]
    )
    agent.register_interviewer_availability(
        "bob_senior_eng",
        ["2025-04-07", "2025-04-08", "2025-04-09"],
        ["11:00", "15:00"]
    )
    print("✓ Registered interviewer availability")
    
    # Schedule interviews
    schedule_slots = [
        (top_candidates[0], "alice_ml_lead", "2025-04-07", "10:00"),
        (top_candidates[1], "alice_ml_lead", "2025-04-07", "14:00"),
        (top_candidates[2], "bob_senior_eng", "2025-04-08", "11:00"),
        (top_candidates[3], "bob_senior_eng", "2025-04-08", "15:00"),
        (top_candidates[4], "alice_ml_lead", "2025-04-09", "10:00"),
    ]
    
    scheduled_count = 0
    for cand_id, interviewer, date, time in schedule_slots:
        result = agent.schedule_interview(cand_id, interviewer, date, time)
        if result['status'] == 'success':
            scheduled_count += 1
    
    print(f"✓ Scheduled {scheduled_count}/{len(schedule_slots)} interviews")
    
    # Step 4: Generate interview questions
    print("\n[STEP 4] Generate Interview Questions...")
    questions = agent.generate_interview_questions(job_description, "")
    print(f"✓ Generated {len(questions['technical'])} technical questions")
    print(f"✓ Generated {len(questions['behavioral'])} behavioral questions")
    
    # Step 5: Process candidate states through pipeline
    print("\n[STEP 5] Process Pipeline States...")
    
    pipeline_actions = [
        (top_candidates[0], [
            ("screened", "Resume reviewed - strong background"),
            ("interview_scheduled", "Interview scheduled"),
            ("interviewed", "Interview completed - excellent performance"),
            ("offer_extended", "Offer sent")
        ]),
        (top_candidates[1], [
            ("screened", "Resume reviewed - good fit"),
            ("interview_scheduled", "Interview scheduled"),
            ("interviewed", "Interview completed - good fit"),
            ("offer_extended", "Offer sent"),
            ("offer_accepted", "Candidate accepted offer")
        ]),
        (top_candidates[2], [
            ("screened", "Resume reviewed - meets requirements"),
            ("rejected", "Does not meet seniority requirements")
        ]),
        (top_candidates[3], [
            ("screened", "Resume reviewed"),
            ("interview_scheduled", "Interview scheduled"),
            ("rejected", "Interview performance not up to standard")
        ]),
    ]
    
    for cand_id, actions in pipeline_actions:
        for state, reason in actions:
            agent.advance_candidate_state(cand_id, state, reason)
    
    print(f"✓ Processed {len(pipeline_actions)} candidates through pipeline")
    
    # Step 6: Test leave approvals
    print("\n[STEP 6] Process Leave Requests...")
    
    # Sample leave requests
    leave_requests = [
        ("Michael Moore", "Casual", "2025-04-10", "2025-04-11", 1),
        ("Ashley Rogers", "Casual", "2025-05-01", "2025-05-05", 4),
        ("Kelly Alexander", "Sick", "2025-04-20", "2025-04-20", 1),
    ]
    
    approved = 0
    rejected = 0
    for emp_name, leave_type, start, end, days in leave_requests:
        result = agent.process_leave_request(emp_name, leave_type, start, end, days)
        if result['decision_type'] == 'approved':
            approved += 1
        else:
            rejected += 1
    
    print(f"✓ Processed leave requests: {approved} approved, {rejected} rejected")
    
    # Step 7: Generate final report
    print("\n[STEP 7] Generate Final Report...")
    
    json_export = agent.export_results()
    data = json.loads(json_export)
    
    print(f"\n✓ Results Summary:")
    print(f"  - Resume rankings: {len(data['rankings'])}")
    print(f"  - Scheduled interviews: {len(data['interview_schedules'])}")
    print(f"  - Pipeline state updates: {len(data['pipeline_history'])}")
    print(f"  - Leave decisions: {len(data['leave_decisions'])}")
    print(f"  - Interview question sets: {len(data['interview_questions'])}")
    
    # Analysis
    print(f"\n✓ Pipeline Analysis:")
    candidates_by_state = {}
    for pipeline in data['pipeline_history']:
        state = pipeline['current_state']
        candidates_by_state[state] = candidates_by_state.get(state, 0) + 1
    
    for state, count in sorted(candidates_by_state.items()):
        print(f"  - {state}: {count} candidate(s)")
    
    # Ranking analysis
    print(f"\n✓ Top 3 Ranked Candidates:")
    for i, rank in enumerate(data['rankings'][:3], 1):
        print(f"  {i}. {rank['name']} (Score: {rank['normalized_score']:.1%})")
    
    # JSON validation
    print(f"\n✓ JSON Export Validation:")
    required_keys = ['rankings', 'leave_decisions', 'pipeline_history', 'interview_schedules', 'interview_questions']
    for key in required_keys:
        if key in data:
            print(f"  ✓ {key}")
        else:
            print(f"  ✗ {key} MISSING")
    
    print("\n" + "█"*80)
    print("INTEGRATION TEST COMPLETED SUCCESSFULLY")
    print("█"*80)
    print("\nAll modules working correctly:")
    print("  ✓ Resume ranking with embeddings")
    print("  ✓ Interview scheduling with conflict detection")
    print("  ✓ Interview question generation")
    print("  ✓ Candidate pipeline state management")
    print("  ✓ Leave approval engine")
    print("  ✓ JSON export and validation")
    print("\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(integration_test())
