#!/usr/bin/env python3
"""
=====================================================
HACKATHON TEMPLATE — Track 1
AI HR Agent
=====================================================
Starter template. Build on top of this.
DO NOT change class interfaces or output format.

Required output format for scoring:
{
    "team_id": "your_team_name",
    "track": "track_1_hr_agent",
    "results": {
        "resume_screening": {"ranked_candidates": [...], "scores": [...]},
        "scheduling": {"interviews_scheduled": [...], "conflicts": [...]},
        "questionnaire": {"questions": [...]},
        "pipeline": {"candidates": {id: status}},
        "leave_management": {"processed_requests": [...]},
        "escalations": [...]
    }
}
=====================================================
"""

import os
import re
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────
CONFIG = {
    "team_id": "Netrik_Code_Blooded",
    "llm_provider": "openai",
    "llm_model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small",
}


# ─────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────
class PipelineStatus(Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    SELECTED = "selected"
    REJECTED = "rejected"

    # Valid transitions
    @staticmethod
    def valid_transitions():
        return {
            "applied": ["shortlisted", "rejected"],
            "shortlisted": ["interview_scheduled", "rejected"],
            "interview_scheduled": ["interviewed", "rejected"],
            "interviewed": ["selected", "rejected"],
            "selected": [],
            "rejected": [],
        }


@dataclass
class Candidate:
    candidate_id: str
    name: str
    email: str
    resume_text: str
    skills: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    match_score: float = 0.0
    status: str = "applied"

@dataclass
class JobDescription:
    job_id: str
    title: str
    description: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    min_experience: float = 0.0

@dataclass
class InterviewSlot:
    slot_id: str
    interviewer_id: str
    start_time: datetime
    end_time: datetime
    is_available: bool = True

@dataclass
class LeaveRequest:
    request_id: str
    employee_id: str
    leave_type: str         # casual, sick, earned, etc.
    start_date: datetime
    end_date: datetime
    reason: str
    status: str = "pending"  # pending, approved, rejected
    policy_violations: List[str] = field(default_factory=list)

@dataclass
class LeavePolicy:
    leave_type: str
    annual_quota: int
    max_consecutive_days: int
    min_notice_days: int
    requires_document: bool = False  # e.g., medical certificate for sick leave


# ─────────────────────────────────────────────────────
# ABSTRACT INTERFACES — Implement these
# ─────────────────────────────────────────────────────

class ResumeScreener(ABC):
    @abstractmethod
    def extract_skills(self, resume_text: str) -> List[str]:
        """Extract skills from resume text."""
        pass

    @abstractmethod
    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        """Rank candidates against job description. Returns sorted list."""
        pass

class InterviewScheduler(ABC):
    @abstractmethod
    def schedule_interview(self, candidate: Candidate, available_slots: List[InterviewSlot]) -> Optional[InterviewSlot]:
        """Find and book an interview slot. Returns booked slot or None."""
        pass

class QuestionnaireGenerator(ABC):
    @abstractmethod
    def generate_questions(self, jd: JobDescription, candidate: Optional[Candidate] = None) -> List[Dict]:
        """Generate structured interview questions. Returns list of {question, type, category}."""
        pass

class LeaveManager(ABC):
    @abstractmethod
    def process_leave_request(self, request: LeaveRequest, policy: LeavePolicy,
                              current_balance: int) -> Dict:
        """Process a leave request. Returns {approved: bool, reason: str, violations: [...]}."""
        pass

class EscalationHandler(ABC):
    @abstractmethod
    def should_escalate(self, query: str, context: Dict) -> tuple:
        """Returns (should_escalate: bool, reason: str, priority: str)."""
        pass


# ─────────────────────────────────────────────────────
# REFERENCE IMPLEMENTATIONS
# ─────────────────────────────────────────────────────

class LLMResumeScreener(ResumeScreener):
    """Resume screening with LLM + embeddings."""

    def extract_skills(self, resume_text: str) -> List[str]:
        # Keyword-based skill extraction with normalisation
        SKILL_KEYWORDS = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
            "SQL", "NoSQL", "REST", "GraphQL", "API", "Docker", "Kubernetes",
            "AWS", "Azure", "GCP", "Machine Learning", "Deep Learning", "NLP",
            "TensorFlow", "PyTorch", "Scikit-learn", "Git", "React", "Angular", "Vue",
            "Node", "FastAPI", "Django", "Flask", "Spring Boot", "PostgreSQL", "MySQL",
            "MongoDB", "Redis", "Kafka", "Spark", "Airflow", "CI/CD", "DevOps",
            "Data Analysis", "Data Engineering", "Leadership", "Project Management",
            "Agile", "Scrum", "Microservices", "System Design",
        ]
        text_lower = (resume_text or "").lower()
        found: List[str] = []
        for skill in SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                found.append(skill)
        # Fallback: capitalised tokens not in common stopwords
        if not found:
            stopwords = frozenset({"the", "and", "with", "from", "this", "that",
                                   "have", "been", "will", "for", "are", "was"})
            for word in re.findall(r"[A-Za-z][A-Za-z0-9+#.]+", resume_text or ""):
                if len(word) > 3 and word.lower() not in stopwords:
                    found.append(word)
        # Deduplicate preserving order, cap at 20
        return list(dict.fromkeys(found))[:20]

    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        # ── Ensure skills are populated ───────────────────────────────────────
        for c in candidates:
            if not c.skills:
                c.skills = self.extract_skills(c.resume_text)

        # ── Build JD skill sets (normalised) ──────────────────────────────────
        required_norm  = {s.lower() for s in (jd.required_skills  or [])}
        preferred_norm = {s.lower() for s in (jd.preferred_skills or [])}
        all_jd_kw      = required_norm | preferred_norm
        jd_text        = f"{jd.title or ''} {jd.description or ''} " + " ".join(jd.required_skills or [])

        # ── Lightweight semantic similarity (shared word Dice coefficient) ─────
        def _dice(text_a: str, text_b: str) -> float:
            a = set(re.findall(r"[a-z]+", (text_a or "").lower()))
            b = set(re.findall(r"[a-z]+", (text_b or "").lower()))
            if not a or not b:
                return 0.5
            return 2 * len(a & b) / (len(a) + len(b))

        # ── Deduplicate by candidate_id (keep first) ──────────────────────────
        seen: Dict[str, bool] = {}
        unique: List[Candidate] = []
        for c in candidates:
            cid = (c.candidate_id or "").strip() or f"unknown_{id(c)}"
            if cid not in seen:
                seen[cid] = True
                unique.append(c)
            else:
                logger.warning("Duplicate candidate_id='%s' dropped.", cid)

        # ── Score each candidate ──────────────────────────────────────────────
        for c in unique:
            cand_norm = {s.lower() for s in (c.skills or [])}
            # 1. Skill score: required 70% + preferred 30%
            req_hit  = len(cand_norm & required_norm)  / max(len(required_norm),  1)
            pref_hit = len(cand_norm & preferred_norm) / max(len(preferred_norm), 1)
            skill_score = 0.70 * req_hit + 0.30 * pref_hit
            # 2. Experience score (capped at 1.0)
            exp_score = min((c.experience_years or 0.0) / max(jd.min_experience or 0.01, 0.01), 1.0)
            # 3. Keyword density in resume
            kw_score = (sum(1 for kw in all_jd_kw if kw in (c.resume_text or "").lower())
                        / max(len(all_jd_kw), 1))
            # 4. Semantic similarity
            sem_score = _dice(c.resume_text, jd_text)
            # 5. Education presence
            edu_kw    = ["b.tech", "m.tech", "b.sc", "m.sc", "mba", "phd",
                         "bachelor", "master", "doctorate", "iit", "nit", "bits"]
            edu_score = 1.0 if any(kw in (c.resume_text or "").lower() for kw in edu_kw) else 0.0
            # Weighted total
            c.match_score = round(
                0.40 * skill_score
                + 0.20 * exp_score
                + 0.15 * kw_score
                + 0.15 * sem_score
                + 0.10 * edu_score,
                6,
            )

        # Deterministic sort: score DESC, candidate_id ASC as tiebreaker
        return sorted(unique, key=lambda x: (-x.match_score, x.candidate_id or ""))


class BasicInterviewScheduler(InterviewScheduler):
    """Greedy scheduler — enhance with constraint optimization."""

    def schedule_interview(self, candidate: Candidate, available_slots: List[InterviewSlot]) -> Optional[InterviewSlot]:
        # Deterministic: sort by slot_id before scanning
        for slot in sorted(available_slots, key=lambda s: s.slot_id):
            if not slot.is_available:
                continue
            # Check interviewer has no overlapping already-booked slot
            conflict = False
            for other in available_slots:
                if other.slot_id == slot.slot_id or other.is_available:
                    continue
                if other.interviewer_id != slot.interviewer_id:
                    continue
                # Overlap: intervals share any time
                if not (other.end_time <= slot.start_time or other.start_time >= slot.end_time):
                    conflict = True
                    break
            if not conflict:
                slot.is_available = False
                return slot
        return None


class LLMQuestionnaireGenerator(QuestionnaireGenerator):
    """Generate role-specific interview questions using LLM."""

    def generate_questions(self, jd: JobDescription, candidate: Optional[Candidate] = None) -> List[Dict]:
        questions: List[Dict] = []
        # Technical questions — one per required skill (up to 5)
        for skill in (jd.required_skills or ["General"])[:5]:
            questions.append({
                "question": f"Describe your hands-on experience with {skill} and a specific challenge you solved using it.",
                "type": "technical",
                "category": "technical",
                "expected_answer_points": [
                    f"Depth of {skill} knowledge",
                    "Concrete project or use-case mentioned",
                    "Problem-solving approach",
                ],
            })
        # Behavioral questions (STAR format)
        for q_text in [
            "Tell me about a time you faced a critical technical deadline. How did you manage it? (STAR)",
            "Describe a situation where you had to collaborate across teams with conflicting priorities. (STAR)",
            "Give an example of when you proactively improved a process or system without being asked. (STAR)",
        ]:
            questions.append({
                "question": q_text,
                "type": "behavioral",
                "category": "behavioral",
                "expected_answer_points": ["Situation clarity", "Action taken", "Measurable result"],
            })
        # Situational questions
        questions.append({
            "question": f"If you joined our team as {jd.title} and discovered a critical bug in production on your first day, what would you do?",
            "type": "situational",
            "category": "situational",
            "expected_answer_points": ["Prioritisation", "Communication", "Resolution steps"],
        })
        questions.append({
            "question": "How would you handle a disagreement with a senior engineer about the technical direction of a project?",
            "type": "situational",
            "category": "situational",
            "expected_answer_points": ["Respectful challenge", "Data-driven reasoning", "Team alignment"],
        })
        # Role-specific questions
        if candidate and candidate.skills:
            highlighted = ", ".join(candidate.skills[:3])
            questions.append({
                "question": f"Your profile highlights {highlighted}. How have these skills contributed to a recent project?",
                "type": "role_specific",
                "category": "role_specific",
                "expected_answer_points": ["Relevance to role", "Impact", "Technical depth"],
            })
        questions.append({
            "question": f"Where do you see the {jd.title} role evolving over the next 2–3 years, and how do you plan to grow with it?",
            "type": "role_specific",
            "category": "role_specific",
            "expected_answer_points": ["Industry awareness", "Learning mindset", "Alignment with role"],
        })
        return questions


class PolicyLeaveManager(LeaveManager):
    """Leave management with policy enforcement."""

    def process_leave_request(self, request: LeaveRequest, policy: LeavePolicy,
                              current_balance: int) -> Dict:
        violations = []

        # ── Edge case: malformed / reversed dates ─────────────────────────────
        try:
            start = request.start_date if isinstance(request.start_date, datetime) \
                    else datetime.fromisoformat(str(request.start_date))
            end   = request.end_date   if isinstance(request.end_date,   datetime) \
                    else datetime.fromisoformat(str(request.end_date))
        except (ValueError, TypeError) as exc:
            return {
                "approved": False,
                "reason": f"Malformed date(s): {exc}",
                "violations": [f"Malformed date(s): {exc}"],
                "days_requested": 0,
                "remaining_balance": current_balance,
            }

        if end < start:
            violations.append("End date is before start date.")

        days_requested = max((end - start).days + 1, 0)

        # Check balance (no underflow allowed)
        if days_requested > current_balance:
            violations.append(f"Insufficient balance: requested {days_requested}, available {current_balance}")

        # Check max consecutive days
        if days_requested > policy.max_consecutive_days:
            violations.append(f"Exceeds max consecutive days ({policy.max_consecutive_days})")

        # Check notice period (floor to 0 for past/same-day requests)
        notice_days = max((start.date() - datetime.now().date()).days, 0)
        if notice_days < policy.min_notice_days:
            violations.append(f"Insufficient notice: {notice_days} days (min: {policy.min_notice_days})")

        # Check documentation requirement
        if policy.requires_document and not (request.reason or "").strip():
            violations.append("Medical certificate/documentation required")

        approved = len(violations) == 0
        return {
            "approved": approved,
            "reason": "Approved" if approved else "Denied due to policy violations",
            "violations": violations,
            "days_requested": days_requested,
            "remaining_balance": max(0, current_balance - days_requested) if approved else current_balance,
        }


class RuleBasedEscalation(EscalationHandler):
    """Escalation for complex HR queries."""

    ESCALATION_PATTERNS = {
        "high": ["grievance", "harassment", "discrimination", "termination", "legal"],
        "medium": ["compensation", "salary revision", "policy exception", "transfer"],
        "low": ["general complaint", "feedback"],
    }

    def should_escalate(self, query: str, context: Dict) -> tuple:
        query_lower = (query or "").lower()
        # Iterate in deterministic priority order: high → medium → low
        for priority in ("high", "medium", "low"):
            for kw in self.ESCALATION_PATTERNS[priority]:
                if kw in query_lower:
                    return (True, f"Matched escalation keyword: {kw}", priority)
        return (False, "No escalation needed", "none")


# ─────────────────────────────────────────────────────
# MAIN HR AGENT
# ─────────────────────────────────────────────────────
class HRAgent:
    """Main HR Agent orchestrator."""

    def __init__(self):
        self.screener = LLMResumeScreener()
        self.scheduler = BasicInterviewScheduler()
        self.questionnaire = LLMQuestionnaireGenerator()
        self.leave_mgr = PolicyLeaveManager()
        self.escalation = RuleBasedEscalation()
        self.pipeline: Dict[str, Candidate] = {}  # candidate_id -> Candidate

        # Accumulated results for export
        self._resume_screening: Dict = {"ranked_candidates": [], "scores": []}
        self._scheduling: Dict       = {"interviews_scheduled": [], "conflicts": []}
        self._questionnaire: List    = []
        self._leave_processed: List  = []
        self._escalations: List      = []

        logger.info("HR Agent initialized")

    def screen_resumes(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        """Screen and rank candidates. Entry point for resume screening evaluation."""
        if not candidates:
            logger.warning("screen_resumes called with empty candidate list.")
            return []
        for c in candidates:
            if not c.resume_text:
                logger.warning("Candidate '%s' has empty resume_text.", c.candidate_id)
            c.skills = self.screener.extract_skills(c.resume_text)
        ranked = self.screener.rank_candidates(candidates, jd)
        for c in ranked:
            self.pipeline[c.candidate_id] = c
        self._resume_screening["ranked_candidates"] = [c.candidate_id for c in ranked]
        self._resume_screening["scores"]            = [c.match_score  for c in ranked]
        return ranked

    def shortlist_and_schedule(self, ranked_candidates: List[Candidate],
                                top_n: int, slots: List[InterviewSlot]) -> List[Dict]:
        """Shortlist top N and schedule interviews."""
        results = []
        top_n = max(top_n, 0)
        valid_transitions = PipelineStatus.valid_transitions()

        for candidate in ranked_candidates[:top_n]:
            cid = candidate.candidate_id

            # Advance: applied → shortlisted (validate transition)
            if "shortlisted" in valid_transitions.get(candidate.status, []):
                candidate.status = "shortlisted"

            slot = self.scheduler.schedule_interview(candidate, slots)
            if slot:
                # Advance: shortlisted → interview_scheduled
                if "interview_scheduled" in valid_transitions.get(candidate.status, []):
                    candidate.status = "interview_scheduled"
                entry = {
                    "candidate_id":   cid,
                    "candidate":      candidate.name,
                    "slot_id":        slot.slot_id,
                    "interviewer_id": slot.interviewer_id,
                    "start_time":     slot.start_time.isoformat() if hasattr(slot.start_time, "isoformat") else str(slot.start_time),
                    "end_time":       slot.end_time.isoformat()   if hasattr(slot.end_time,   "isoformat") else str(slot.end_time),
                }
                self._scheduling["interviews_scheduled"].append(entry)
                results.append({**entry, "status": "scheduled"})
            else:
                self._scheduling["conflicts"].append({
                    "candidate_id": cid,
                    "candidate":    candidate.name,
                    "reason":       "no_available_slot",
                })
                results.append({"candidate": candidate.name, "slot": None, "status": "no_slot_available"})
        return results

    def generate_interview_questions(self, jd: JobDescription) -> List[Dict]:
        """Generate interview questionnaire for a role."""
        questions = self.questionnaire.generate_questions(jd)
        self._questionnaire = questions
        return questions

    def process_leave(self, request: LeaveRequest, policy: LeavePolicy, balance: int) -> Dict:
        """Process a leave request with policy checks."""
        result = self.leave_mgr.process_leave_request(request, policy, balance)
        self._leave_processed.append({
            "request_id":        request.request_id or "",
            "employee_id":       request.employee_id or "",
            "leave_type":        request.leave_type or "",
            "start_date":        request.start_date.isoformat() if hasattr(request.start_date, "isoformat") else str(request.start_date),
            "end_date":          request.end_date.isoformat()   if hasattr(request.end_date,   "isoformat") else str(request.end_date),
            "approved":          result.get("approved", False),
            "reason":            result.get("reason", ""),
            "violations":        result.get("violations", []),
            "days_requested":    result.get("days_requested", 0),
            "remaining_balance": result.get("remaining_balance", balance),
        })
        return result

    def update_pipeline_status(self, candidate_id: str, new_status: str) -> Dict:
        """Update candidate pipeline status with validation."""
        if candidate_id not in self.pipeline:
            return {"error": f"Candidate {candidate_id} not found"}
        candidate = self.pipeline[candidate_id]
        valid = PipelineStatus.valid_transitions()
        # Guard terminal states
        if candidate.status in ("selected", "rejected"):
            return {"error": f"State '{candidate.status}' is terminal; no further transitions allowed."}
        if new_status not in valid.get(candidate.status, []):
            return {"error": f"Invalid transition: {candidate.status} → {new_status}"}
        candidate.status = new_status
        return {"success": True, "candidate": candidate.name, "new_status": new_status}

    def handle_query(self, query: str, context: Dict = None) -> Dict:
        """Handle an HR query — check for escalation first."""
        should_esc, reason, priority = self.escalation.should_escalate(query, context or {})
        if should_esc:
            entry = {"query": query, "reason": reason, "priority": priority}
            self._escalations.append(entry)
            return {"escalated": True, "reason": reason, "priority": priority}
        return {"escalated": False, "response": "Query processed"}

    def export_results(self) -> Dict:
        """Export results in EVALUATION FORMAT."""
        pipeline_export = {cid: c.status for cid, c in self.pipeline.items()}
        return {
            "team_id": CONFIG["team_id"],
            "track": "track_1_hr_agent",
            "results": {
                "resume_screening": {
                    "ranked_candidates": self._resume_screening["ranked_candidates"],
                    "scores":            self._resume_screening["scores"],
                },
                "scheduling": {
                    "interviews_scheduled": self._scheduling["interviews_scheduled"],
                    "conflicts":            self._scheduling["conflicts"],
                },
                "questionnaire":    {"questions": self._questionnaire},
                "pipeline":         {"candidates": pipeline_export},
                "leave_management": {"processed_requests": self._leave_processed},
                "escalations":      self._escalations,
            },
        }


# ─────────────────────────────────────────────────────
# SAMPLE DATA FOR TESTING
# ─────────────────────────────────────────────────────
SAMPLE_JD = JobDescription(
    job_id="JD_001",
    title="Senior Python Developer",
    description="We are looking for an experienced Python developer with expertise in "
                "building REST APIs, microservices, and cloud deployments. "
                "Experience with ML/AI pipelines is a plus.",
    required_skills=["Python", "REST APIs", "Docker", "SQL", "Git"],
    preferred_skills=["Kubernetes", "AWS", "Machine Learning", "FastAPI"],
    min_experience=4.0,
)

SAMPLE_CANDIDATES = [
    Candidate("C001", "Priya Sharma", "priya@email.com",
              "5 years Python, Django, REST APIs, Docker, AWS, PostgreSQL. Built ML pipelines."),
    Candidate("C002", "Rahul Verma", "rahul@email.com",
              "3 years Java, Spring Boot, MySQL. Learning Python and Docker."),
    Candidate("C003", "Anita Reddy", "anita@email.com",
              "6 years Python, FastAPI, Kubernetes, AWS, ML, TensorFlow. Open source contributor."),
]

SAMPLE_LEAVE_POLICY = LeavePolicy(
    leave_type="casual", annual_quota=12,
    max_consecutive_days=3, min_notice_days=2,
)


if __name__ == "__main__":
    agent = HRAgent()
    sep = "=" * 56
    print(sep)
    print("  AI HR Agent — Track 1 Submission Demo")
    print(f"  Team: {CONFIG['team_id']}")
    print(sep)

    # Add experience_years to sample candidates
    SAMPLE_CANDIDATES[0].experience_years = 5.0
    SAMPLE_CANDIDATES[1].experience_years = 3.0
    SAMPLE_CANDIDATES[2].experience_years = 6.0

    # 1. Resume Screening
    ranked = agent.screen_resumes(SAMPLE_CANDIDATES, SAMPLE_JD)
    print("\n[1] Resume Screening:")
    for c in ranked:
        print(f"    {c.candidate_id}  {c.name:<20s}  score={c.match_score:.4f}")

    # 2. Shortlist + Schedule
    base = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    slots = [
        InterviewSlot("S1", "IV1", base,                      base + timedelta(hours=1)),
        InterviewSlot("S2", "IV1", base + timedelta(days=1),  base + timedelta(days=1, hours=1)),
    ]
    sched = agent.shortlist_and_schedule(ranked, top_n=2, slots=slots)
    print("\n[2] Scheduling:")
    for r in sched:
        print(f"    {r.get('candidate')} → {r.get('status')}")

    # 3. Questionnaire
    questions = agent.generate_interview_questions(SAMPLE_JD)
    print(f"\n[3] Questionnaire: {len(questions)} question(s) generated.")

    # 4. Leave Management
    leave_req = LeaveRequest(
        request_id="LR001", employee_id="EMP042",
        leave_type="casual", start_date=datetime.now() + timedelta(days=3),
        end_date=datetime.now() + timedelta(days=5), reason="Family function"
    )
    result = agent.process_leave(leave_req, SAMPLE_LEAVE_POLICY, balance=10)
    print(f"\n[4] Leave: approved={result['approved']}  days={result['days_requested']}  remaining={result['remaining_balance']}")

    # 5. Pipeline transition
    if ranked:
        t = agent.update_pipeline_status(ranked[0].candidate_id, "interviewed")
        print(f"\n[5] Pipeline transition for {ranked[0].candidate_id}: {t}")

    # 6. Escalation
    esc_result = agent.handle_query("I want to file a harassment complaint against my manager")
    print(f"\n[6] Escalation: {esc_result}")

    # Export
    export = agent.export_results()
    print(f"\n{sep}\nEXPORT (evaluation format):\n{sep}")
    print(json.dumps(export, indent=2, default=str))