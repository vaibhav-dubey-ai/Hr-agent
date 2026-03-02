#  AI HR Agent — Netrik Hackathon 2026 (Track 1)


**Autonomous, Deterministic HR Pipeline Automation**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-85%20passed-brightgreen?style=flat-square&logo=pytest)](tests/)
[![Deterministic](https://img.shields.io/badge/determinism-100%25-gold?style=flat-square)](#-determinism--reproducibility)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue?style=flat-square)](#)

*A production-grade AI HR Agent that automates the complete hiring lifecycle — from resume ranking to onboarding — with **zero randomness**, **strict FSM enforcement**, and **formal evidence trails**.*

</div>

---

## Code Blooded
Sahil Kumar ( IIITDMK )
Vaibhav Dubey ( IIITDMK )
Ramyapriya Sivasankar ( SRMIST Chennai )
Shreya Gaur ( VIT Bhopal )


##  Project Overview

This AI HR Agent fully automates the enterprise hiring pipeline, replacing manual HR workflows with deterministic, auditable AI-driven decision-making. The system processes 1,200+ resumes, schedules conflict-free interviews, enforces strict candidate pipeline states, and evaluates leave compliance — all with reproducible outputs and formal evidence.

**Key Capabilities:**
- **Resume–JD Matching & Ranking** — TF-IDF embeddings with stable sorting and full score breakdowns
- **Interview Scheduling** — Interval-based conflict detection with zero overlapping bookings
- **Candidate Pipeline (FSM)** — Strict finite state machine with no skipping, no reverting, terminal state enforcement
- **Leave Compliance Engine** — Rule-based approval with balance tracking, role eligibility, and overlap detection
- **Interview Question Generation** — Deterministic, JD-aware technical and behavioral question generation
- **Structured JSON Export** — Strict schema compliance for test harness evaluation

---


## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FastAPI REST API Layer                        │
│   /api/rank  /api/leave  /api/schedule  /api/transition  /api/export│
├──────────────────────────────────────────────────────────────────────┤
│                        HRAgent Orchestrator                          │
│                         (hr_agent/main.py)                           │
├────────────┬──────────┬─────────────┬────────────┬──────────────────┤
│  Ranking   │ Scheduler│ StateMachine│ Leave      │ Interview        │
│  Engine    │ Engine   │ (FSM)       │ Engine     │ Generator        │
│            │          │             │            │                  │
│ TF-IDF     │ Interval │ Enum States │ 4-Rule     │ Skill-Based      │
│ Embeddings │ Overlap  │ Transition  │ Evidence   │ Question Bank    │
│ + GBR      │ Detection│ Logging     │ Chain      │                  │
├────────────┴──────────┴─────────────┴────────────┴──────────────────┤
│                     Utility Layer                                    │
│            validation.py    embeddings.py    config.py               │
├──────────────────────────────────────────────────────────────────────┤
│                     Data Layer                                       │
│         resume_dataset_1200.csv    employee_leave_tracking.xlsx      │
└──────────────────────────────────────────────────────────────────────┘
```

---

##  Hiring Workflow Demonstration

Complete lifecycle with actual system output:

```
Step 1: RANK RESUMES       → 1200 candidates scored against JD
Step 2: SHORTLIST TOP-K    → applied → shortlisted (FSM transition)
Step 3: SCHEDULE INTERVIEW → shortlisted → interview_scheduled (conflict-free slot allocated)
Step 4: INTERVIEW          → interview_scheduled → interviewed
Step 5: SELECT / REJECT    → interviewed → selected (TERMINAL) or rejected (TERMINAL)
Step 6: EXPORT             → All results in strict JSON schema
```

### Example Ranking Output (Top Candidate)

```json
{
  "rank": 1,
  "candidate_id": "C001",
  "name": "Priya Sharma",
  "score": 0.6748,
  "score_breakdown": {
    "skill_score": 0.635,
    "experience_score": 1.0,
    "keyword_score": 0.5556,
    "semantic_score": 0.25,
    "education_score": 1.0,
    "total": 0.6748
  }
}
```

---

##  Automated Testing

### Run Tests
```bash
# Install dependencies
pip install -r backend/requirements.txt pytest

# Run full test suite
python3 -m pytest tests/ -v

# Run specific module
python3 -m pytest tests/test_ranking.py -v

# Run with coverage
python3 -m pytest tests/ -v --tb=short
```

---

##  Quick Start

```bash
# 1. Clone and install
git clone <repo-url> && cd hack
pip install -r backend/requirements.txt

# 2. Run test suite (85 tests)
python3 -m pytest tests/ -v

# 3. Start API server
cd backend && python3 -m uvicorn app.main:app --reload
# API docs at http://localhost:8000/docs
```

---

##  Track 1 Hackathon Submission

**HireEasy - An autonomous AI HR Agent**

For **Track 1** evaluation, use the template-compliant entry point that outputs the **exact scoring format** required by the judges.

### Run the submission
```bash
# From project root
cd /path/to/Netrik_Code_Blooded_track1-main

# Install dependencies (if not already)
pip install -r requirements.txt

# Run the submission demo (prints full JSON export)
python submission.py
```

### Methodology

- **`submission.py`** implements the hackathon template: same class names, data models (`Candidate`, `JobDescription`, `InterviewSlot`, `LeaveRequest`, `LeavePolicy`, `PipelineStatus`), and the **exact output schema** for scoring.
- It uses your existing engines where possible:
  - Resume ranking: `hr_agent.utils.embeddings` (TF-IDF) + skill overlap.
  - Questionnaire: `hr_agent.interview_generator` for JD/resume-based questions.
  - Leave and escalation: template’s policy + rule-based escalation.
- **Export format** (what judges expect):

```json
{
  "team_id": "Netrik_Code_Blooded",
  "track": "track_1_hr_agent",
  "results": {
    "resume_screening": { "ranked_candidates": [...], "scores": [...] },
    "scheduling": { "interviews_scheduled": [...], "conflicts": [...] },
    "questionnaire": { "questions": [...] },
    "pipeline": { "candidates": { "id": "status", ... } },
    "leave_management": { "processed_requests": [...] },
    "escalations": [...]
  }
}
```

### Change team name

Edit `CONFIG["team_id"]` at the top of `submission.py`:

```python
CONFIG = {
    "team_id": "CODE_BLOODED",  # ← change this
    ...
}
```


---

## Frontend Screenshots

<img width="1919" height="1074" alt="Screenshot 2026-03-01 095618" src="https://github.com/user-attachments/assets/47fe7860-b07f-4c7b-a61a-69b66f2af75c" />
<img width="1919" height="1079" alt="Screenshot 2026-03-01 095656" src="https://github.com/user-attachments/assets/be94de0f-7d71-4fda-97db-5cf2366e8abd" />
<img width="1919" height="1079" alt="Screenshot 2026-03-01 112835" src="https://github.com/user-attachments/assets/a65f288d-2132-42ec-a577-3316812697e3" />
<img width="1919" height="1079" alt="Screenshot 2026-03-01 112926" src="https://github.com/user-attachments/assets/669a451d-bd43-420d-8d38-575d73dd9719" />
<img width="1919" height="1079" alt="Screenshot 2026-03-01 112835" src="https://github.com/user-attachments/assets/47deec49-6a6a-4c4f-806e-a01a0e1f29b9" />
<img width="1919" height="1070" alt="Screenshot 2026-03-01 113136" src="https://github.com/user-attachments/assets/07efb4e6-644f-40d6-8b90-aa0f625302b7" />
<img width="1919" height="1079" alt="Screenshot 2026-03-01 113159" src="https://github.com/user-attachments/assets/41e10642-14b8-4ad1-85ae-bde2759ffd33" />
<img width="1919" height="1079" alt="Screenshot 2026-03-01 113224" src="https://github.com/user-attachments/assets/e22cc293-65c3-4405-a105-e520d42970eb" />
<img width="1916" height="1024" alt="Screenshot 2026-03-01 113235" src="https://github.com/user-attachments/assets/8ef4e63d-7810-41a4-9855-c5b4546fbb12" />
<img width="1919" height="1079" alt="Screenshot 2026-03-01 121547" src="https://github.com/user-attachments/assets/b8b2d350-bdb9-41a1-9f97-1cd1312b8f97" />

---

## Backend Screenshots

![WhatsApp Image 2026-03-01 at 1 42 30 PM](https://github.com/user-attachments/assets/2cd7fb61-969e-412d-9f82-0a57a26ff528)
![WhatsApp Image 2026-03-01 at 1 44 17 PM](https://github.com/user-attachments/assets/ecea90bc-e583-4e27-98bf-17d093d59db9)
![WhatsApp Image 2026-03-01 at 1 45 50 PM](https://github.com/user-attachments/assets/063e6688-1dea-486b-85db-2c219ec49bf8)
![WhatsApp Image 2026-03-01 at 1 46 27 PM](https://github.com/user-attachments/assets/a733b704-888b-4bce-833c-1362259386e6)

---

## 🔍 Edge Case Handling

| Edge Case | Handling | Test |
|:---|:---|:---|
| Empty JD text | Returns rankings (no crash) | `test_empty_jd_text` |
| Empty resume dataset | Raises `ValueError` | `test_empty_resume_dataset` |
| Malformed leave dates | Rejected with `RULE_INVALID_DATE_FORMAT` | `test_malformed_start_date` |
| Start date after end date | Rejected with `RULE_INVALID_DATE_RANGE` | `test_start_after_end_rejected` |
| Unknown employee | Rejected with `RULE_EMPLOYEE_NOT_FOUND` | `test_unknown_employee_rejected` |
| Duplicate candidate scheduling | Rejected with `CANDIDATE_ALREADY_SCHEDULED` | `test_duplicate_candidate_scheduling` |
| Invalid state transition string | Returns error with allowed states | `test_invalid_state_string` |
| Numeric state input | Graceful failure | `test_numeric_state` |
| Empty state string | Graceful failure | `test_empty_state_string` |
| Same-state transition | Blocked | `test_same_state_transition` |
| Whitespace-only IDs | Rejected | `test_whitespace_only_*` |
| Zero leave balance | Rejected with evidence | `test_zero_balance_rejected` |
| Leave balance underflow | Balance decremented, successive request fails | `test_no_balance_underflow_on_successive_requests` |

---

## Project Structure

```
├── hr_agent/                    # Core engine package
│   ├── main.py                  #   HRAgent orchestrator
│   ├── ranking_engine.py        #   Resume-JD matching (TF-IDF + GBR)
│   ├── scheduler.py             #   Interview scheduling (interval overlap)
│   ├── state_machine.py         #   FSM pipeline enforcement
│   ├── leave_engine.py          #   Policy-based leave approval
│   ├── interview_generator.py   #   Deterministic question generation
│   └── utils/
│       ├── embeddings.py        #   TF-IDF embedding engine
│       └── validation.py        #   JSON schema validation
├── backend/                     # FastAPI REST API
│   ├── app/
│   │   ├── main.py              #   App entry point
│   │   ├── schemas.py           #   Pydantic models
│   │   ├── routers/             #   API endpoints
│   │   └── core/                #   Agent singleton
│   └── requirements.txt         #   Python dependencies
├── frontend/                    # Next.js dashboard UI
├── tests/                       # Pytest test suite (85 tests)
│   ├── conftest.py              #   Shared fixtures
│   ├── test_ranking.py          #   Ranking determinism
│   ├── test_state_machine.py    #   FSM enforcement
│   ├── test_scheduler.py        #   Scheduling conflicts
│   ├── test_leave_engine.py     #   Leave validation
│   ├── test_edge_cases.py       #   Edge case handling
│   ├── test_export.py           #   JSON schema compliance
│   ├── test_integration.py      #   Full lifecycle
│   └── sample_output/           #   Example JSON outputs
├── test_harness.py              # Hackathon test harness
├── integration_test.py          # Full workflow test
├── track1_submission.py         # Track 1 hackathon submission entry point
├── resume_dataset_1200.csv      # 1200 candidate resumes
├── docker-compose.yml           # Container orchestration
└── README.md                    # This file
```

---

## Scalability:

The AI HR Agent is built with a modular, stateless architecture where core components such as resume ranking, interview scheduling, FSM enforcement, and leave validation operate independently and can be scaled horizontally. Because each engine processes inputs deterministically without shared mutable state, the system can handle large resume volumes and concurrent hiring workflows by parallel execution or microservice deployment, making it suitable for enterprise-scale hiring scenarios.

## Future Scope:

The system can be extended by adding contextual semantic embeddings, recruiter feedback loops, and fairness or bias monitoring dashboards on top of the existing deterministic core. Additional integrations with enterprise ATS platforms, calendar systems, and identity management tools can further enhance real-world usability, while optional LLM-based assistants can be layered for insights or recommendations without compromising reproducibility.

## Conclusion:

This project delivers a production-grade AI HR Agent that automates the complete hiring lifecycle with strict determinism, explainability, and rule enforcement. By combining transparent scoring, formal state management, and comprehensive testing, the system ensures trust, correctness, and auditability, positioning it as a robust solution for compliance-critical hiring environments beyond hackathon evaluation.
