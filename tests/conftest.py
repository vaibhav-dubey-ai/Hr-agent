"""Shared fixtures for HR Agent test suite."""

import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hr_agent.ranking_engine import ResumeRankingEngine
from hr_agent.state_machine import StateMachine, PipelineState
from hr_agent.scheduler import InterviewScheduler
from hr_agent.leave_engine import LeaveEngine
from hr_agent.main import HRAgent


@pytest.fixture
def sample_resume_df():
    """Minimal reproducible resume DataFrame for unit tests."""
    data = {
        "Name": ["Alice Smith", "Bob Jones", "Carol White", "Dave Brown", "Eve Davis"],
        "Education_Level": ["Master's", "Bachelor's", "PhD", "Bachelor's", "Master's"],
        "Field_of_Study": ["Computer Science", "Engineering", "Data Science", "Marketing", "Computer Science"],
        "Current_Job_Title": ["ML Engineer", "Software Developer", "Data Scientist", "Sales Lead", "Backend Developer"],
        "Skills": [
            "Python, Machine Learning, TensorFlow, AWS",
            "Java, Spring Boot, Docker",
            "Python, Deep Learning, PyTorch, Statistics",
            "Sales, Marketing, CRM",
            "Python, Django, REST APIs, PostgreSQL",
        ],
        "Target_Job_Description": [
            "Machine Learning Engineer with Python and AWS experience",
            "Full Stack Java Developer for enterprise applications",
            "Senior Data Scientist for AI research team",
            "Sales Manager for SaaS products",
            "Backend Python Developer for fintech platform",
        ],
        "Experience_Years": [7, 4, 10, 3, 6],
        "Certifications": ["AWS Certified", "None", "Google ML", "None", "None"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_leave_df():
    """Minimal reproducible leave DataFrame for unit tests."""
    data = {
        "Employee Name": ["Alice Smith", "Bob Jones", "Carol White", "Dave Brown"],
        "Department": ["IT", "Finance", "HR", "Operations"],
        "Position": ["Engineer", "Analyst", "Manager", "Coordinator"],
        "Total Leave Entitlement": [20, 18, 22, 15],
        "Leave Taken So Far": [5, 16, 3, 14],
        "Remaining Leaves": [15, 2, 19, 1],
    }
    return pd.DataFrame(data)


@pytest.fixture
def ranking_engine(sample_resume_df):
    """Pre-loaded ranking engine."""
    engine = ResumeRankingEngine()
    engine.load_resumes(sample_resume_df)
    return engine


@pytest.fixture
def leave_engine(sample_leave_df):
    """Pre-loaded leave engine."""
    engine = LeaveEngine()
    engine.load_employee_data(sample_leave_df)
    return engine


@pytest.fixture
def scheduler():
    """Scheduler with pre-registered interviewer availability."""
    sched = InterviewScheduler()
    sched.add_interviewer_availability(
        "interviewer_A",
        ["2025-04-07", "2025-04-08", "2025-04-09"],
        ["09:00", "10:00", "11:00", "14:00", "15:00"],
    )
    sched.add_interviewer_availability(
        "interviewer_B",
        ["2025-04-07", "2025-04-08"],
        ["10:00", "14:00"],
    )
    return sched


@pytest.fixture
def state_machine():
    """Fresh state machine for candidate_0."""
    return StateMachine("candidate_0")


@pytest.fixture
def hr_agent(tmp_path, sample_resume_df, sample_leave_df):
    """Fully initialized HR Agent with sample data (no file I/O)."""
    agent = HRAgent()
    # Directly load DataFrames instead of reading files
    agent.ranking_engine.load_resumes(sample_resume_df)
    for idx, row in sample_resume_df.iterrows():
        candidate_id = f"candidate_{idx}"
        agent.candidate_pipelines[candidate_id] = StateMachine(candidate_id)
    agent.leave_engine.load_employee_data(sample_leave_df)
    return agent
