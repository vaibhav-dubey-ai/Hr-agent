"""Bridge between FastAPI and Python HR Agent."""

import sys
from pathlib import Path

# Add parent directory to path to import hr_agent
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from hr_agent.main import HRAgent

# Global singleton instance
_agent: HRAgent = None

def get_hr_agent() -> HRAgent:
    """Get or create the HR Agent singleton."""
    global _agent
    
    if _agent is None:
        _agent = HRAgent()
        # Load data from project root
        project_root = Path(__file__).parent.parent.parent.parent
        _agent.load_resume_data(str(project_root / "resume_dataset_1200.csv"))
        _agent.load_leave_data(str(project_root / "employee leave tracking data.xlsx"))
    
    return _agent

def reset_agent():
    """Reset the agent (useful for testing)."""
    global _agent
    _agent = None
