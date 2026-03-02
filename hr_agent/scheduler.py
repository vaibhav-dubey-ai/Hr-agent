from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class InterviewScheduler:
    """Deterministic interview scheduling engine with interval validation."""
    
    INTERVIEW_DURATION_MINUTES = 60  # Standard 1-hour interview
    
    def __init__(self):
        self.schedules = {}  # interviewer_id -> list of (date, time) slots
        self.candidate_slots = {}  # candidate_id -> (date, time, interviewer_id)
        self.blocked_slots = []  # list of unavailable (date, time) tuples
    
    def add_interviewer_availability(self, interviewer_id: str, 
                                     available_dates: List[str],
                                     available_times: List[str]):
        """
        Register interviewer availability.
        Dates in YYYY-MM-DD format, times in HH:MM format.
        """
        if interviewer_id not in self.schedules:
            self.schedules[interviewer_id] = []
        
        for date in available_dates:
            for time in available_times:
                if self._is_valid_datetime(date, time):
                    self.schedules[interviewer_id].append({
                        "date": date,
                        "time": time,
                        "available": True
                    })
    
    def add_candidate_availability(self, candidate_id: str,
                                   available_dates: List[str],
                                   available_times: List[str]):
        """Register candidate availability constraints."""
        if candidate_id not in self.candidate_slots:
            self.candidate_slots[candidate_id] = {
                "available_dates": available_dates,
                "available_times": available_times
            }
    
    def _is_valid_datetime(self, date: str, time: str) -> bool:
        """Validate date and time formats."""
        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")
            return True
        except ValueError:
            return False
    
    def _is_slot_available(self, interviewer_id: str, date: str, time: str) -> bool:
        """Check if a time slot is available with overlap detection."""
        if interviewer_id not in self.schedules:
            return False
        
        # Check if this exact slot exists and is available
        slot_exists = False
        for slot in self.schedules[interviewer_id]:
            if slot["date"] == date and slot["time"] == time:
                slot_exists = True
                if not slot["available"]:
                    return False
                break
        
        if not slot_exists:
            return False
        
        # Check for overlapping bookings
        try:
            requested_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            requested_end = requested_start + timedelta(minutes=self.INTERVIEW_DURATION_MINUTES)
        except ValueError:
            return False
        
        # Look for any booked slots that overlap with this time
        for slot in self.schedules[interviewer_id]:
            if slot["date"] != date or slot["available"]:
                continue
            
            try:
                slot_start = datetime.strptime(f"{slot['date']} {slot['time']}", "%Y-%m-%d %H:%M")
                slot_end = slot_start + timedelta(minutes=self.INTERVIEW_DURATION_MINUTES)
                
                # Check for overlap
                if not (requested_end <= slot_start or requested_start >= slot_end):
                    return False  # Overlap detected!
            except ValueError:
                continue
        
        return True
    
    def _mark_slot_booked(self, interviewer_id: str, date: str, time: str) -> bool:
        """Mark a slot as booked."""
        if interviewer_id not in self.schedules:
            return False
        
        for slot in self.schedules[interviewer_id]:
            if slot["date"] == date and slot["time"] == time:
                slot["available"] = False
                return True
        
        return False
    
    def schedule_interview(self, candidate_id: str, interviewer_id: str,
                          preferred_date: str, preferred_time: str) -> Dict:
        """
        Schedule an interview with deterministic conflict detection (interval-based).
        Returns structured result with status, error codes, and conflict details.
        """
        result = {
            "candidate_id": candidate_id,
            "interviewer_id": interviewer_id,
            "status": "failed",
            "error_code": None,
            "error_message": "",
            "conflict_details": None,
            "scheduled_date": None,
            "scheduled_time": None
        }
        
        # Validate inputs
        if not candidate_id or not candidate_id.strip():
            result["error_code"] = "INVALID_CANDIDATE_ID"
            result["error_message"] = "Candidate ID cannot be empty"
            return result
        
        if not interviewer_id or not interviewer_id.strip():
            result["error_code"] = "INVALID_INTERVIEWER_ID"
            result["error_message"] = "Interviewer ID cannot be empty"
            return result
        
        if not self._is_valid_datetime(preferred_date, preferred_time):
            result["error_code"] = "INVALID_DATETIME_FORMAT"
            result["error_message"] = "Date must be YYYY-MM-DD, time must be HH:MM"
            return result
        
        # Check if slot is available (interval-based)
        if not self._is_slot_available(interviewer_id, preferred_date, preferred_time):
            result["error_code"] = "SLOT_NOT_AVAILABLE"
            result["error_message"] = f"Interviewer not available at requested time"
            result["conflict_details"] = {
                "requested_date": preferred_date,
                "requested_time": preferred_time,
                "duration_minutes": self.INTERVIEW_DURATION_MINUTES
            }
            return result
        
        # Check if candidate already has interview scheduled
        if candidate_id in self.candidate_slots and "scheduled" in self.candidate_slots[candidate_id]:
            result["error_code"] = "CANDIDATE_ALREADY_SCHEDULED"
            result["error_message"] = "Candidate already has interview scheduled"
            result["conflict_details"] = self.candidate_slots[candidate_id]["scheduled"]
            return result
        
        # Check candidate availability if registered
        if candidate_id in self.candidate_slots:
            if "available_dates" in self.candidate_slots[candidate_id]:
                cand_dates = self.candidate_slots[candidate_id]["available_dates"]
                cand_times = self.candidate_slots[candidate_id]["available_times"]
                if preferred_date not in cand_dates or preferred_time not in cand_times:
                    result["error_code"] = "CANDIDATE_UNAVAILABLE"
                    result["error_message"] = "Requested time conflicts with candidate availability"
                    return result
        
        # Book the slot
        if self._mark_slot_booked(interviewer_id, preferred_date, preferred_time):
            result["status"] = "success"
            result["error_code"] = None
            result["scheduled_date"] = preferred_date
            result["scheduled_time"] = preferred_time
            result["error_message"] = "Interview scheduled successfully"
            
            # Record the scheduling
            if candidate_id not in self.candidate_slots:
                self.candidate_slots[candidate_id] = {}
            self.candidate_slots[candidate_id]["scheduled"] = {
                "date": preferred_date,
                "time": preferred_time,
                "interviewer_id": interviewer_id
            }
        else:
            result["error_code"] = "BOOKING_FAILED"
            result["error_message"] = "Failed to book slot (system error)"
        
        return result
    
    def get_schedule_summary(self) -> Dict:
        """Get a summary of all scheduled interviews."""
        summary = {
            "scheduled_interviews": [],
            "interviewer_availability": {}
        }
        
        # Add scheduled interviews
        for cand_id, data in self.candidate_slots.items():
            if "scheduled" in data:
                summary["scheduled_interviews"].append({
                    "candidate_id": cand_id,
                    "interviewer_id": data["scheduled"]["interviewer_id"],
                    "date": data["scheduled"]["date"],
                    "time": data["scheduled"]["time"]
                })
        
        # Add interviewer availability
        for interviewer_id, slots in self.schedules.items():
            available_slots = [s for s in slots if s["available"]]
            summary["interviewer_availability"][interviewer_id] = len(available_slots)
        
        return summary
