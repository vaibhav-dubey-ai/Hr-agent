import json
from datetime import datetime
from typing import Any, Dict, List, Optional

class JSONValidator:
    @staticmethod
    def validate_resume_ranking_output(data: Dict) -> bool:
        """Validate resume ranking output format."""
        required_keys = ['rank', 'candidate_id', 'name', 'score', 'normalized_score', 'score_breakdown', 'reasoning']
        return all(key in data for key in required_keys)
    
    @staticmethod
    def validate_schedule_output(data: Dict) -> bool:
        """Validate interview schedule output format."""
        required_keys = ['candidate_id', 'interviewer_id', 'status', 'error_code', 'scheduled_date', 'scheduled_time']
        return all(key in data for key in required_keys)
    
    @staticmethod
    def validate_leave_decision(data: Dict) -> bool:
        """Validate leave decision output format."""
        required_keys = ['employee_name', 'leave_type', 'decision_type', 'applied_policy_rules', 'evidence']
        return all(key in data for key in required_keys)
    
    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """Check if date string is valid."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_time(time_str: str) -> bool:
        """Check if time string is valid HH:MM format."""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

class SchemaValidator:
    @staticmethod
    def validate_json_schema(data: Dict, schema: Dict) -> bool:
        """Basic JSON schema validation."""
        try:
            for key, expected_type in schema.items():
                if key not in data:
                    return False
                if not isinstance(data[key], expected_type):
                    return False
            return True
        except Exception:
            return False

def safe_json_dumps(obj: Any, default_on_error: str = "{}") -> str:
    """Safely convert object to JSON string."""
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return default_on_error
