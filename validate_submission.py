#!/usr/bin/env python3
"""
=====================================================
Submission Validator — Netrik Hackathon Track 1
=====================================================
Validates that submission.py produces EXACTLY the
required output schema, deterministic results, and
correct data types.

Run:  python validate_submission.py
=====================================================
"""

import json
import sys
from copy import deepcopy
from datetime import datetime, timedelta

# Import everything from submission (DO NOT MODIFY submission.py)
from submission import (
    HRAgent, CONFIG,
    Candidate, JobDescription, InterviewSlot, LeaveRequest, LeavePolicy,
    PipelineStatus, SAMPLE_JD, SAMPLE_CANDIDATES, SAMPLE_LEAVE_POLICY,
)


# ─────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────
class Result:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def ok(self, msg: str):
        self.passed += 1
        print(f"  ✅  {msg}")

    def fail(self, msg: str):
        self.failed += 1
        print(f"  ❌  {msg}")

    def warn(self, msg: str):
        self.warnings += 1
        print(f"  ⚠️   {msg}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'═' * 60}")
        print(f"  RESULTS: {self.passed}/{total} passed, {self.failed} failed, {self.warnings} warnings")
        print(f"{'═' * 60}")
        return self.failed == 0


R = Result()


def _build_agent():
    """Create a fully-exercised HRAgent for validation."""
    agent = HRAgent()

    # Prepare candidates with experience
    candidates = [
        Candidate("C001", "Priya Sharma", "priya@email.com",
                  "5 years Python, Django, REST APIs, Docker, AWS, PostgreSQL. Built ML pipelines.",
                  experience_years=5.0),
        Candidate("C002", "Rahul Verma", "rahul@email.com",
                  "3 years Java, Spring Boot, MySQL. Learning Python and Docker.",
                  experience_years=3.0),
        Candidate("C003", "Anita Reddy", "anita@email.com",
                  "6 years Python, FastAPI, Kubernetes, AWS, ML, TensorFlow. Open source contributor.",
                  experience_years=6.0),
    ]

    jd = JobDescription(
        job_id="JD_001",
        title="Senior Python Developer",
        description="Looking for experienced Python developer with REST, microservices, cloud.",
        required_skills=["Python", "REST APIs", "Docker", "SQL", "Git"],
        preferred_skills=["Kubernetes", "AWS", "Machine Learning", "FastAPI"],
        min_experience=4.0,
    )

    # 1. Screen resumes
    ranked = agent.screen_resumes(candidates, jd)

    # 2. Schedule interviews
    base = datetime(2025, 5, 1, 10, 0, 0)
    slots = [
        InterviewSlot("S1", "IV1", base, base + timedelta(hours=1)),
        InterviewSlot("S2", "IV1", base + timedelta(days=1), base + timedelta(days=1, hours=1)),
    ]
    agent.shortlist_and_schedule(ranked, top_n=2, slots=slots)

    # 3. Generate questions
    agent.generate_interview_questions(jd)

    # 4. Process leave
    leave_req = LeaveRequest(
        request_id="LR001", employee_id="EMP042",
        leave_type="casual",
        start_date=base + timedelta(days=3),
        end_date=base + timedelta(days=5),
        reason="Family function",
    )
    agent.process_leave(leave_req, SAMPLE_LEAVE_POLICY, balance=10)

    # 5. Pipeline transition
    if ranked:
        agent.update_pipeline_status(ranked[0].candidate_id, "interviewed")

    # 6. Escalation
    agent.handle_query("I want to file a harassment complaint against my manager")

    return agent


# ─────────────────────────────────────────────────────
# SCHEMA CHECKS
# ─────────────────────────────────────────────────────
def check_export_schema(export: dict):
    """Validate the top-level export schema."""
    print("\n📋  Schema Validation")
    print("─" * 40)

    # Top-level keys
    required_top = {"team_id", "track", "results"}
    actual_top = set(export.keys())

    if required_top == actual_top:
        R.ok("Top-level keys match exactly")
    else:
        missing = required_top - actual_top
        extra = actual_top - required_top
        if missing:
            R.fail(f"Missing top-level keys: {missing}")
        if extra:
            R.fail(f"Extra top-level keys: {extra}")

    # team_id / track types
    if isinstance(export.get("team_id"), str):
        R.ok(f"team_id is str: '{export['team_id']}'")
    else:
        R.fail(f"team_id is not str: {type(export.get('team_id'))}")

    if export.get("track") == "track_1_hr_agent":
        R.ok("track == 'track_1_hr_agent'")
    else:
        R.fail(f"track is '{export.get('track')}', expected 'track_1_hr_agent'")

    # Results sub-keys
    results = export.get("results", {})
    required_results = {"resume_screening", "scheduling", "questionnaire", "pipeline", "leave_management", "escalations"}
    actual_results = set(results.keys())

    if required_results == actual_results:
        R.ok("results sub-keys match exactly")
    else:
        missing = required_results - actual_results
        extra = actual_results - required_results
        if missing:
            R.fail(f"Missing results keys: {missing}")
        if extra:
            R.fail(f"Extra results keys: {extra}")


def check_resume_screening(results: dict):
    """Validate resume_screening section."""
    print("\n📋  Resume Screening Validation")
    print("─" * 40)
    rs = results.get("resume_screening", {})

    if "ranked_candidates" in rs and "scores" in rs:
        R.ok("resume_screening has ranked_candidates and scores")
    else:
        R.fail(f"resume_screening missing keys. Has: {list(rs.keys())}")
        return

    # No extra keys
    extra = set(rs.keys()) - {"ranked_candidates", "scores"}
    if extra:
        R.fail(f"Extra keys in resume_screening: {extra}")
    else:
        R.ok("No extra keys in resume_screening")

    rc = rs["ranked_candidates"]
    sc = rs["scores"]

    if isinstance(rc, list) and isinstance(sc, list):
        R.ok("ranked_candidates and scores are lists")
    else:
        R.fail("ranked_candidates or scores is not a list")

    if len(rc) == len(sc):
        R.ok(f"Same length: {len(rc)} candidates / {len(sc)} scores")
    else:
        R.fail(f"Length mismatch: {len(rc)} candidates vs {len(sc)} scores")

    # Check scores are sorted descending
    if sc == sorted(sc, reverse=True):
        R.ok("Scores are sorted descending")
    else:
        R.warn("Scores NOT sorted descending")

    # No None values
    if None not in rc and None not in sc:
        R.ok("No None values in rankings")
    else:
        R.fail("None value found in rankings")


def check_scheduling(results: dict):
    """Validate scheduling section."""
    print("\n📋  Scheduling Validation")
    print("─" * 40)
    sched = results.get("scheduling", {})

    required = {"interviews_scheduled", "conflicts"}
    if required == set(sched.keys()):
        R.ok("scheduling has exactly interviews_scheduled and conflicts")
    else:
        extra = set(sched.keys()) - required
        missing = required - set(sched.keys())
        if missing:
            R.fail(f"Missing scheduling keys: {missing}")
        if extra:
            R.fail(f"Extra scheduling keys: {extra}")

    for entry in sched.get("interviews_scheduled", []):
        required_keys = {"candidate_id", "candidate", "slot_id", "interviewer_id", "start_time", "end_time"}
        if required_keys.issubset(set(entry.keys())):
            R.ok(f"Interview entry for {entry.get('candidate_id')} has required keys")
        else:
            R.fail(f"Interview entry missing keys: {required_keys - set(entry.keys())}")


def check_questionnaire(results: dict):
    """Validate questionnaire section."""
    print("\n📋  Questionnaire Validation")
    print("─" * 40)
    q = results.get("questionnaire", {})

    if "questions" in q:
        R.ok("questionnaire has 'questions' key")
    else:
        R.fail("questionnaire missing 'questions' key")
        return

    extra = set(q.keys()) - {"questions"}
    if extra:
        R.fail(f"Extra keys in questionnaire: {extra}")
    else:
        R.ok("No extra keys in questionnaire")

    questions = q["questions"]
    if isinstance(questions, list) and len(questions) > 0:
        R.ok(f"questions is a non-empty list ({len(questions)} items)")
    else:
        R.warn(f"questions is empty or not a list")

    # Check each question has required fields
    for i, qn in enumerate(questions):
        required = {"question", "type", "category"}
        if required.issubset(set(qn.keys())):
            pass  # OK, don't spam
        else:
            R.fail(f"Question {i} missing keys: {required - set(qn.keys())}")
            break
    else:
        R.ok("All questions have required fields (question, type, category)")


def check_pipeline(results: dict):
    """Validate pipeline section."""
    print("\n📋  Pipeline Validation")
    print("─" * 40)
    p = results.get("pipeline", {})

    if "candidates" in p:
        R.ok("pipeline has 'candidates' key")
    else:
        R.fail("pipeline missing 'candidates' key")
        return

    extra = set(p.keys()) - {"candidates"}
    if extra:
        R.fail(f"Extra keys in pipeline: {extra}")
    else:
        R.ok("No extra keys in pipeline")

    cands = p["candidates"]
    if isinstance(cands, dict):
        R.ok(f"candidates is a dict ({len(cands)} entries)")
    else:
        R.fail(f"candidates is not a dict: {type(cands)}")
        return

    valid_statuses = {s.value for s in PipelineStatus}
    for cid, status in cands.items():
        if status not in valid_statuses:
            R.fail(f"Candidate {cid} has invalid status: {status}")
            break
    else:
        R.ok("All candidate statuses are valid PipelineStatus values")


def check_leave_management(results: dict):
    """Validate leave_management section."""
    print("\n📋  Leave Management Validation")
    print("─" * 40)
    lm = results.get("leave_management", {})

    if "processed_requests" in lm:
        R.ok("leave_management has 'processed_requests' key")
    else:
        R.fail("leave_management missing 'processed_requests' key")
        return

    extra = set(lm.keys()) - {"processed_requests"}
    if extra:
        R.fail(f"Extra keys in leave_management: {extra}")
    else:
        R.ok("No extra keys in leave_management")

    requests = lm["processed_requests"]
    if isinstance(requests, list):
        R.ok(f"processed_requests is a list ({len(requests)} items)")
    else:
        R.fail("processed_requests is not a list")
        return

    required_entry_keys = {"request_id", "employee_id", "leave_type", "start_date", "end_date",
                           "approved", "reason", "violations", "days_requested", "remaining_balance"}
    for i, req in enumerate(requests):
        missing = required_entry_keys - set(req.keys())
        if missing:
            R.fail(f"Leave request {i} missing keys: {missing}")
            break
    else:
        if requests:
            R.ok("All leave requests have required fields")


def check_escalations(results: dict):
    """Validate escalations section."""
    print("\n📋  Escalations Validation")
    print("─" * 40)
    esc = results.get("escalations", [])

    if isinstance(esc, list):
        R.ok(f"escalations is a list ({len(esc)} items)")
    else:
        R.fail(f"escalations is not a list: {type(esc)}")
        return

    for i, e in enumerate(esc):
        required = {"query", "reason", "priority"}
        if required.issubset(set(e.keys())):
            pass
        else:
            R.fail(f"Escalation {i} missing keys: {required - set(e.keys())}")
            break
    else:
        if esc:
            R.ok("All escalation entries have required fields")


def check_no_none_values(export: dict):
    """Recursively check for None values that should be empty arrays."""
    print("\n📋  None Value Check")
    print("─" * 40)

    found_none = []

    def _walk(obj, path=""):
        if obj is None:
            found_none.append(path)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                _walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _walk(v, f"{path}[{i}]")

    _walk(export, "export")

    if not found_none:
        R.ok("No None values found anywhere in export")
    else:
        for p in found_none:
            R.warn(f"None value at {p}")


def check_determinism():
    """Verify that running twice produces identical output."""
    print("\n📋  Determinism Check")
    print("─" * 40)

    agent1 = _build_agent()
    export1 = agent1.export_results()

    agent2 = _build_agent()
    export2 = agent2.export_results()

    json1 = json.dumps(export1, sort_keys=True, default=str)
    json2 = json.dumps(export2, sort_keys=True, default=str)

    if json1 == json2:
        R.ok("Output is deterministic (identical across two runs)")
    else:
        R.fail("Output is NOT deterministic — differs across runs!")
        # Show first difference
        for i, (c1, c2) in enumerate(zip(json1, json2)):
            if c1 != c2:
                R.fail(f"  First diff at char {i}: '{json1[max(0,i-20):i+20]}' vs '{json2[max(0,i-20):i+20]}'")
                break


def check_json_serializable(export: dict):
    """Verify the export can be serialized to JSON cleanly."""
    print("\n📋  JSON Serialization Check")
    print("─" * 40)
    try:
        json_str = json.dumps(export, default=str)
        reparsed = json.loads(json_str)
        R.ok(f"Export is JSON serializable ({len(json_str)} bytes)")
    except (TypeError, json.JSONDecodeError) as e:
        R.fail(f"JSON serialization failed: {e}")


# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────
def main():
    sep = "═" * 60
    print(f"\n{sep}")
    print("  NETRIK HACKATHON — Track 1 Submission Validator")
    print(f"  Team: {CONFIG['team_id']}")
    print(f"{sep}")

    # Build fully-exercised agent
    print("\n🔨  Building HRAgent and running all operations...")
    try:
        agent = _build_agent()
        R.ok("HRAgent constructed and all operations executed without error")
    except Exception as e:
        R.fail(f"HRAgent construction/operation failed: {e}")
        R.summary()
        return 1

    # Get export
    try:
        export = agent.export_results()
        if isinstance(export, dict):
            R.ok("export_results() returns dict")
        else:
            R.fail(f"export_results() returns {type(export)}, expected dict")
            R.summary()
            return 1
    except Exception as e:
        R.fail(f"export_results() raised: {e}")
        R.summary()
        return 1

    results = export.get("results", {})

    # Run all checks
    check_export_schema(export)
    check_resume_screening(results)
    check_scheduling(results)
    check_questionnaire(results)
    check_pipeline(results)
    check_leave_management(results)
    check_escalations(results)
    check_no_none_values(export)
    check_json_serializable(export)
    check_determinism()

    # Print final export
    print(f"\n{'─' * 60}")
    print("  EXPORT OUTPUT (for review):")
    print(f"{'─' * 60}")
    print(json.dumps(export, indent=2, default=str))

    success = R.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
