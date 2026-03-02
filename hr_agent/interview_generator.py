from typing import Dict, List

class InterviewQuestionGenerator:
    """Generate contextual interview questions based on JD and resume."""
    
    # Question templates by role/skill
    QUESTION_BANK = {
        "Python": [
            "Describe your experience with Python. What projects have you built?",
            "How do you handle exceptions and error handling in Python?",
            "Explain decorators and their use cases in Python."
        ],
        "Machine Learning": [
            "Tell us about a machine learning project you've worked on.",
            "How do you approach feature engineering?",
            "What techniques do you use for model evaluation and validation?"
        ],
        "Cloud Computing": [
            "Describe your experience with cloud platforms (AWS, Azure, GCP).",
            "How would you design a scalable cloud architecture?",
            "Explain your approach to security in cloud environments."
        ],
        "DevOps": [
            "What CI/CD tools have you worked with?",
            "Describe your containerization experience (Docker, Kubernetes).",
            "How do you approach infrastructure as code?"
        ],
        "Data Analysis": [
            "Walk us through a data analysis project you've completed.",
            "How do you approach data cleaning and preprocessing?",
            "What visualization tools do you prefer and why?"
        ],
        "Leadership": [
            "Describe a time you led a team through a challenging project.",
            "How do you approach conflict resolution?",
            "Tell us about your experience mentoring junior team members."
        ]
    }
    
    BEHAVIORAL_QUESTIONS = [
        "Tell us about a time you faced a technical challenge. How did you solve it?",
        "Describe a situation where you had to learn something new quickly.",
        "Tell us about a time you worked in a cross-functional team.",
        "Describe a failure and what you learned from it.",
        "How do you stay updated with latest technologies?"
    ]
    
    def __init__(self):
        self.questions_cache = {}
    
    def generate_questions(self, jd_text: str, resume_text: str, 
                          num_technical: int = 5, num_behavioral: int = 3) -> Dict:
        """
        Generate interview questions based on JD and resume.
        DETERMINISTIC: Same input produces same questions.
        
        Args:
            jd_text: Job description
            resume_text: Candidate resume
            num_technical: Number of technical questions (5-7)
            num_behavioral: Number of behavioral questions (3-5)
        
        Returns:
            Dict with organized questions and scoring guide
        """
        # Extract key skills from JD (deterministic)
        key_skills = self._extract_skills(jd_text)
        
        questions = {
            "technical": [],
            "behavioral": [],
            "scoring_guide": self._get_scoring_guide(key_skills)
        }
        
        # Generate technical questions deterministically
        # Use skill index as seed for consistent selection
        selected_skills = key_skills if key_skills else ["General Technical"]
        for i, skill in enumerate(selected_skills[:num_technical]):
            if skill in self.QUESTION_BANK:
                # Use modulo with skill index for deterministic selection
                q_idx = i % len(self.QUESTION_BANK[skill])
                q = self.QUESTION_BANK[skill][q_idx]
            else:
                q = f"Tell us about your experience with {skill}."
            questions["technical"].append(q)
        
        # Pad with generic questions if needed
        while len(questions["technical"]) < num_technical:
            q = "What is your approach to solving complex problems in your domain?"
            questions["technical"].append(q)
        
        # Add behavioral questions deterministically (in order)
        questions["behavioral"] = self.BEHAVIORAL_QUESTIONS[:num_behavioral]
        
        return questions
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract key skills from text."""
        skill_keywords = [
            "Python", "JavaScript", "Java", "C++",
            "Machine Learning", "Deep Learning", "Data Science",
            "Cloud Computing", "AWS", "Azure", "GCP",
            "DevOps", "Docker", "Kubernetes",
            "Data Analysis", "SQL", "NoSQL",
            "API", "REST", "GraphQL",
            "Leadership", "Project Management"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills[:5]  # Return top 5
    
    def _get_scoring_guide(self, skills: List[str]) -> Dict:
        """Generate scoring rubric for interview."""
        return {
            "technical_depth": {
                "excellent": "Demonstrates deep knowledge, provides concrete examples",
                "good": "Shows solid understanding, explains concepts clearly",
                "acceptable": "Basic understanding, some gaps in knowledge",
                "poor": "Limited knowledge, unable to explain concepts"
            },
            "communication": {
                "excellent": "Clear, concise, well-structured responses",
                "good": "Generally clear with minor issues",
                "acceptable": "Somewhat unclear but understandable",
                "poor": "Difficult to understand"
            },
            "problem_solving": {
                "excellent": "Systematic approach, considers edge cases",
                "good": "Logical approach, handles main scenarios",
                "acceptable": "Basic approach, may miss some considerations",
                "poor": "Unclear or illogical approach"
            }
        }
