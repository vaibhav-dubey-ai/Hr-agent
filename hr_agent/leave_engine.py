from typing import Dict, Tuple, List
from datetime import datetime
import pandas as pd

class LeaveEngine:
    """Deterministic rule-based leave approval system."""
    
    # Role-specific leave type eligibility
    ROLE_LEAVE_ELIGIBILITY = {
        "IT": ["Casual", "Sick", "Annual"],
        "HR": ["Casual", "Sick", "Annual", "Maternity"],
        "Finance": ["Casual", "Sick", "Annual"],
        "Operations": ["Casual", "Sick", "Annual"],
        "Marketing": ["Casual", "Sick", "Annual"]
    }
    
    def __init__(self):
        self.employee_data = {}
        self.leaves_approved = {}
    
    def load_employee_data(self, df: pd.DataFrame):
        """Load employee leave data from DataFrame."""
        for idx, row in df.iterrows():
            emp_key = row['Employee Name']
            if emp_key not in self.employee_data:
                self.employee_data[emp_key] = {
                    'department': row['Department'],
                    'position': row['Position'],
                    'total_entitlement': row['Total Leave Entitlement'],
                    'taken_so_far': row['Leave Taken So Far'],
                    'remaining': row['Remaining Leaves']
                }
    
    def check_balance(self, employee_name: str, requested_days: int) -> Tuple[bool, str]:
        """Check if employee has sufficient leave balance."""
        if employee_name not in self.employee_data:
            return False, "Employee not found in records"
        
        emp_data = self.employee_data[employee_name]
        if emp_data['remaining'] < requested_days:
            return False, f"Insufficient Balance. Available: {emp_data['remaining']}, Requested: {requested_days}"
        
        return True, "Sufficient balance available"
    
    def check_role_eligibility(self, employee_name: str, leave_type: str) -> Tuple[bool, str]:
        """Check if leave type is eligible for employee's role."""
        if employee_name not in self.employee_data:
            return False, "Employee not found in records"
        
        department = self.employee_data[employee_name]['department']
        if department not in self.ROLE_LEAVE_ELIGIBILITY:
            return False, f"Department '{department}' not configured"
        
        allowed_types = self.ROLE_LEAVE_ELIGIBILITY[department]
        if leave_type not in allowed_types:
            return False, f"Role Restriction. {leave_type} not allowed for {department}"
        
        return True, f"Leave type '{leave_type}' is eligible for {department}"
    
    def check_date_overlap(self, employee_name: str, start_date: str, end_date: str) -> Tuple[bool, str]:
        """Check for overlapping leave dates."""
        if employee_name not in self.leaves_approved:
            return True, "No overlapping leaves"
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
        
        for approved_start, approved_end in self.leaves_approved[employee_name]:
            if not (end < approved_start or start > approved_end):
                return False, "Team Conflict. Overlapping leave dates detected"
        
        return True, "No overlapping leaves"
    
    def approve_leave(self, employee_name: str, leave_type: str, 
                     start_date: str, end_date: str, days_requested: int) -> Dict:
        """
        Complete leave approval workflow with formal evidence.
        Returns decision with structured proof of each check.
        """
        decision = {
            "employee_name": employee_name,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "days_requested": days_requested,
            "decision_type": "pending",
            "applied_policy_rules": [],
            "evidence": {}
        }
        
        # RULE 1: Validate date format and range
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                decision["decision_type"] = "rejected"
                decision["evidence"]["date_validation"] = {
                    "passed": False,
                    "reason": f"Start date {start_date} is after end date {end_date}"
                }
                decision["applied_policy_rules"].append("RULE_INVALID_DATE_RANGE")
                return decision
        except ValueError as e:
            decision["decision_type"] = "rejected"
            decision["evidence"]["date_validation"] = {
                "passed": False,
                "reason": f"Invalid date format: {str(e)}"
            }
            decision["applied_policy_rules"].append("RULE_INVALID_DATE_FORMAT")
            return decision
        
        decision["evidence"]["date_validation"] = {"passed": True}
        decision["applied_policy_rules"].append("RULE_DATE_VALIDATION_PASSED")
        
        # RULE 2: Check balance
        if employee_name not in self.employee_data:
            decision["decision_type"] = "rejected"
            decision["evidence"]["balance_check"] = {
                "required": days_requested,
                "available": 0,
                "passed": False,
                "reason": "Employee not found in records"
            }
            decision["applied_policy_rules"].append("RULE_EMPLOYEE_NOT_FOUND")
            return decision
        
        emp_data = self.employee_data[employee_name]
        balance_ok = emp_data['remaining'] >= days_requested
        
        decision["evidence"]["balance_check"] = {
            "required": int(days_requested),
            "available": int(emp_data['remaining']),
            "passed": balance_ok,
            "reason": f"Balance check {'passed' if balance_ok else 'failed'}"
        }
        
        if not balance_ok:
            decision["decision_type"] = "rejected"
            decision["applied_policy_rules"].append("RULE_INSUFFICIENT_BALANCE")
            return decision
        
        decision["applied_policy_rules"].append("RULE_BALANCE_CHECK_PASSED")
        
        # RULE 3: Check role eligibility
        department = emp_data.get('department', '')
        allowed_types = self.ROLE_LEAVE_ELIGIBILITY.get(department, [])
        eligibility_ok = leave_type in allowed_types
        
        decision["evidence"]["role_eligibility_check"] = {
            "department": department,
            "allowed_types": allowed_types,
            "requested_type": leave_type,
            "passed": eligibility_ok,
            "reason": f"Role check {'passed' if eligibility_ok else 'failed'}"
        }
        
        if not eligibility_ok:
            decision["decision_type"] = "rejected"
            decision["applied_policy_rules"].append("RULE_ROLE_INELIGIBLE")
            return decision
        
        decision["applied_policy_rules"].append("RULE_ROLE_ELIGIBILITY_PASSED")
        
        # RULE 4: Check date overlap
        overlaps = []
        if employee_name in self.leaves_approved:
            for approved_start, approved_end in self.leaves_approved[employee_name]:
                if not (end < approved_start or start > approved_end):
                    overlaps.append({
                        "start_date": approved_start.isoformat(),
                        "end_date": approved_end.isoformat()
                    })
        
        decision["evidence"]["date_overlap_check"] = {
            "start_date": start_date,
            "end_date": end_date,
            "overlapping_leaves": overlaps,
            "passed": len(overlaps) == 0,
            "reason": f"Found {len(overlaps)} overlapping leave periods"
        }
        
        if len(overlaps) > 0:
            decision["decision_type"] = "rejected"
            decision["applied_policy_rules"].append("RULE_DATE_OVERLAP")
            return decision
        
        decision["applied_policy_rules"].append("RULE_OVERLAP_CHECK_PASSED")
        
        # ALL RULES PASSED - APPROVE
        decision["decision_type"] = "approved"
        decision["applied_policy_rules"].append("POLICY_APPROVED_ALL_CHECKS_PASSED")
        
        # Record the approved leave
        if employee_name not in self.leaves_approved:
            self.leaves_approved[employee_name] = []
        
        self.leaves_approved[employee_name].append((start, end))
        
        # Decrement balance to prevent underflow on subsequent requests
        emp_data['remaining'] -= days_requested
        emp_data['taken_so_far'] += days_requested
        
        return decision
