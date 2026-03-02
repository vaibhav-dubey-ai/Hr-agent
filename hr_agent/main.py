import json
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

from hr_agent.ranking_engine import ResumeRankingEngine
from hr_agent.leave_engine import LeaveEngine
from hr_agent.scheduler import InterviewScheduler
from hr_agent.state_machine import StateMachine, PipelineState
from hr_agent.interview_generator import InterviewQuestionGenerator
from hr_agent.utils.validation import JSONValidator, safe_json_dumps

class HRAgent:
    """Main orchestrator for HR automation."""
    
    def __init__(self):
        self.ranking_engine = ResumeRankingEngine()
        self.leave_engine = LeaveEngine()
        self.scheduler = InterviewScheduler()
        self.interview_generator = InterviewQuestionGenerator()
        self.candidate_pipelines = {}  # candidate_id -> StateMachine
        self.interview_results = []  # Store interview result decisions
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "rankings": [],
            "leave_decisions": [],
            "schedules": [],
            "pipeline_states": [],
            "interview_questions": [],
            "interview_results": []
        }
    
    def load_resume_data(self, csv_path: str):
        """Load resume dataset."""
        df = pd.read_csv(csv_path)
        self.ranking_engine.load_resumes(df)
        
        # Initialize state machines for candidates
        for idx, row in df.iterrows():
            candidate_id = f"candidate_{idx}"
            self.candidate_pipelines[candidate_id] = StateMachine(candidate_id)
        
        return len(df)
    
    def load_leave_data(self, excel_path: str):
        """Load employee leave tracking data."""
        df = pd.read_excel(excel_path, sheet_name="Sheet1")
        self.leave_engine.load_employee_data(df)
        return len(df)
    
    def rank_resumes(self, jd_text: str, top_k: int = 20) -> List[Dict]:
        """
        Rank resumes against a job description.
        MRR-optimized ranking.
        """
        rankings = self.ranking_engine.rank_resumes(jd_text, top_k=top_k)
        self.results["rankings"] = rankings
        return rankings
    
    def process_leave_request(self, employee_name: str, leave_type: str,
                             start_date: str, end_date: str, days_requested: int) -> Dict:
        """
        Process leave request deterministically.
        Returns decision with evidence.
        """
        decision = self.leave_engine.approve_leave(
            employee_name, leave_type, start_date, end_date, days_requested
        )
        self.results["leave_decisions"].append(decision)
        return decision
    
    def schedule_interview(self, candidate_id: str, interviewer_id: str,
                          preferred_date: str, preferred_time: str) -> Dict:
        """Schedule an interview with conflict detection."""
        schedule_result = self.scheduler.schedule_interview(
            candidate_id, interviewer_id, preferred_date, preferred_time
        )
        self.results["schedules"].append(schedule_result)
        return schedule_result
    
    def advance_candidate_state(self, candidate_id: str, new_state: str, reason: str = "") -> tuple:
        """
        Advance a candidate through the pipeline with strict FSM validation.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        if candidate_id not in self.candidate_pipelines:
            return False, f"Candidate {candidate_id} not found"
        
        try:
            if isinstance(new_state, str):
                state = PipelineState(new_state)
            else:
                state = new_state
            
            success, error_msg, allowed = self.candidate_pipelines[candidate_id].transition(state, reason)
            if success:
                self.results["pipeline_states"].append(
                    self.candidate_pipelines[candidate_id].to_dict()
                )
            return success, error_msg
        except ValueError as e:
            return False, f"Invalid state: {new_state}"
    
    def get_candidate_state(self, candidate_id: str) -> Dict:
        """Get current state and history of a candidate."""
        if candidate_id not in self.candidate_pipelines:
            return {}
        
        return self.candidate_pipelines[candidate_id].to_dict()
    
    def generate_interview_questions(self, jd_text: str, resume_text: str = "", 
                                     num_technical: int = 5, num_behavioral: int = 3) -> Dict:
        """Generate structured interview questions deterministically."""
        questions = self.interview_generator.generate_questions(
            jd_text, resume_text, num_technical, num_behavioral
        )
        self.results["interview_questions"].append(questions)
        return questions
    
    def register_interviewer_availability(self, interviewer_id: str,
                                         available_dates: List[str],
                                         available_times: List[str]):
        """Register when interviewers are available."""
        self.scheduler.add_interviewer_availability(
            interviewer_id, available_dates, available_times
        )
    
    def export_results(self) -> str:
        """
        Export all results as strict JSON format for rubric evaluation.
        Implements exact schema required with no extra fields.
        
        Returns strict JSON with exactly these fields:
        {
            "rankings": [...],
            "leave_decisions": [...],
            "pipeline_history": [...],
            "interview_schedules": [...],
            "interview_questions": [...]
        }
        """
        # Build export structure - STRICT format with no extra fields
        export_data = {
            "rankings": self._export_rankings(),
            "leave_decisions": self._export_leave_decisions(),
            "pipeline_history": self._export_pipeline_history(),
            "interview_schedules": self._export_interview_schedules(),
            "interview_questions": self._export_interview_questions()
        }
        
        return safe_json_dumps(export_data)
    
    def _export_rankings(self) -> list:
        """Export rankings with score_breakdown."""
        rankings = []
        for ranking in self.results.get("rankings", []):
            r = {
                "rank": ranking.get("rank"),
                "candidate_id": ranking.get("candidate_id"),
                "name": ranking.get("name"),
                "score": ranking.get("score"),
                "normalized_score": ranking.get("normalized_score"),
                "score_breakdown": ranking.get("score_breakdown", {}),
                "reasoning": ranking.get("reasoning", {}),
                "target_job": ranking.get("target_job", "")
            }
            rankings.append(r)
        return rankings
    
    def _export_leave_decisions(self) -> list:
        """Export leave decisions with formal evidence."""
        decisions = []
        for decision in self.results.get("leave_decisions", []):
            d = {
                "employee_name": decision.get("employee_name"),
                "leave_type": decision.get("leave_type", ""),
                "start_date": decision.get("start_date", ""),
                "end_date": decision.get("end_date", ""),
                "days_requested": decision.get("days_requested", 0),
                "decision_type": decision.get("decision_type", decision.get("status", "")),
                "applied_policy_rules": decision.get("applied_policy_rules", []),
                "evidence": decision.get("evidence", {})
            }
            decisions.append(d)
        return decisions
    
    def _export_pipeline_history(self) -> list:
        """Export pipeline states with FSM metadata."""
        states = []
        for state in self.results.get("pipeline_states", []):
            s = {
                "candidate_id": state.get("candidate_id"),
                "current_state": state.get("current_state"),
                "is_terminal": state.get("is_terminal", False),
                "allowed_transitions": state.get("allowed_transitions", []),
                "history": state.get("history", [])
            }
            states.append(s)
        return states
    
    def _export_interview_schedules(self) -> list:
        """Export interview schedules with error codes."""
        schedules = []
        for schedule in self.results.get("schedules", []):
            sc = {
                "candidate_id": schedule.get("candidate_id"),
                "interviewer_id": schedule.get("interviewer_id"),
                "status": schedule.get("status"),
                "error_code": schedule.get("error_code"),
                "error_message": schedule.get("error_message", schedule.get("reason", "")),
                "conflict_details": schedule.get("conflict_details"),
                "scheduled_date": schedule.get("scheduled_date"),
                "scheduled_time": schedule.get("scheduled_time")
            }
            schedules.append(sc)
        return schedules
    
    def _export_interview_questions(self) -> list:
        """Export interview questions."""
        questions = []
        for q in self.results.get("interview_questions", []):
            qu = {
                "jd_text": q.get("jd_text", ""),
                "technical_questions": q.get("technical", []),
                "behavioral_questions": q.get("behavioral", []),
                "candidate_name": q.get("candidate_name", "")
            }
            questions.append(qu)
        return questions
    
    def get_results_dict(self) -> Dict:
        """Get results as dictionary."""
        return self.results
    
    def reset_results(self):
        """Clear results cache."""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "rankings": [],
            "leave_decisions": [],
            "schedules": [],
            "pipeline_states": [],
            "interview_questions": [],
            "interview_results": []
        }
