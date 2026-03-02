import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
from sklearn.ensemble import GradientBoostingRegressor
from hr_agent.utils.embeddings import EmbeddingEngine
import shap

class ResumeRankingEngine:
    """Resume-JD matching and ranking using embeddings + XGBoost."""
    
    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.ranker = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.is_trained = False
        self.resume_data = None
        self.feature_names = []
    
    def _normalize_text(self, text: str) -> str:
        """Deterministic text normalization for reproducibility."""
        if not isinstance(text, str):
            text = str(text)
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def load_resumes(self, df: pd.DataFrame):
        """Load resume dataset."""
        self.resume_data = df.copy()
        # Prepare texts for embedding
        resume_texts = self._prepare_resume_text(df)
        self.embedding_engine.fit(resume_texts)
    
    def _prepare_resume_text(self, df: pd.DataFrame) -> List[str]:
        """Combine relevant fields into resume text with deterministic normalization."""
        texts = []
        for idx, row in df.iterrows():
            parts = [
                self._normalize_text(str(row['Education_Level'])),
                self._normalize_text(str(row['Field_of_Study'])),
                self._normalize_text(str(row['Current_Job_Title'])),
                self._normalize_text(str(row['Skills'])),
                self._normalize_text(str(row['Target_Job_Description']))
            ]
            text = ' '.join(parts)
            text = self._normalize_text(text)
            texts.append(text)
        return texts
    
    def _extract_features(self, resume_idx: int, jd_text: str) -> np.ndarray:
        """
        Extract features for ranking (deterministic):
        - Embedding similarity
        - Experience years
        - Degree level (ordinal)
        - Skills count
        - Certification count
        """
        row = self.resume_data.iloc[resume_idx]
        
        # Normalize JD text deterministically
        jd_normalized = self._normalize_text(jd_text)
        
        # Embedding similarity
        resume_text = self._prepare_resume_text(
            self.resume_data.iloc[[resume_idx]]
        )[0]
        embedding_sim = self.embedding_engine.similarity(resume_text, jd_normalized)
        
        # Experience years (normalized to 0-1)
        exp_years = min(float(row['Experience_Years']) / 20.0, 1.0)
        
        # Degree level
        degree_map = {
            'High School': 1,
            'Certificate': 2,
            'Diploma': 3,
            'Bachelor\'s': 4,
            'Master\'s': 5,
            'PhD': 6
        }
        degree_level = degree_map.get(row['Education_Level'], 1) / 6.0
        
        # Skills count (normalized to 0-1)
        skills_count = min(len(str(row['Skills']).split(',')) / 10.0, 1.0)
        
        # Certification count (0 or 1)
        cert_count = 0.0 if pd.isna(row['Certifications']) or row['Certifications'] == 'None' else 1.0
        
        return np.array([
            embedding_sim,
            exp_years,
            degree_level,
            skills_count,
            cert_count
        ])
    
    def train(self, jd_texts: List[str], relevance_scores: List[float]):
        """
        Train the ranker with JD-resume pairs and their relevance scores.
        For hackathon, we'll use a simple synthetic training approach.
        """
        if self.resume_data is None:
            raise ValueError("Load resumes first with load_resumes()")
        
        # For each JD, extract features for all resumes
        X = []
        y = []
        groups = []
        
        for jd_text, rel_score in zip(jd_texts, relevance_scores):
            for resume_idx in range(len(self.resume_data)):
                features = self._extract_features(resume_idx, jd_text)
                X.append(features)
                y.append(rel_score)
            groups.append(len(self.resume_data))
        
        if len(X) > 0:
            X = np.array(X)
            y = np.array(y)
            self.ranker.fit(X, y, group=groups)
            self.is_trained = True
            self.feature_names = [
                'embedding_similarity',
                'experience_years',
                'degree_level',
                'skills_count',
                'certifications'
            ]
    
    def rank_resumes(self, jd_text: str, top_k: int = 10, explain: bool = False) -> List[Dict]:
        """
        Rank all resumes against a JD deterministically.
        Returns top-k candidates with scores and reasoning.
        If explain=True, includes SHAP explanations.
        """
        if self.resume_data is None:
            raise ValueError("Load resumes first")
        
        scores = []
        features_list = []
        
        for resume_idx in range(len(self.resume_data)):
            features = self._extract_features(resume_idx, jd_text)
            features_list.append(features)
            
            # If trained, use ranker; otherwise use embedding similarity
            if self.is_trained:
                score = self.ranker.predict(features.reshape(1, -1))[0]
            else:
                # Default: use embedding similarity with experience boost
                score = features[0] * (1 + features[1])
            
            scores.append(score)
        
        # Get top-k with stable tie-breaking by candidate_id
        score_id_pairs = [(scores[i], i) for i in range(len(scores))]
        score_id_pairs.sort(key=lambda x: (-x[0], x[1]))  # Descending score, ascending id
        top_indices = [x[1] for x in score_id_pairs[:top_k]]
        
        max_score = max(scores) if scores else 1.0
        
        results = []
        for rank, idx in enumerate(top_indices):
            row = self.resume_data.iloc[idx]
            features = features_list[idx]
            score = scores[idx]
            normalized = float(score / max_score) if max_score > 0 else 0
            
            # Generate reasoning
            reasoning = {
                "skills_match_score": f"{features[0]:.4f}",
                "experience_score": f"{features[1]:.4f}",
                "education_score": f"{features[2]:.4f}",
                "certification_score": f"{features[4]:.4f}",
                "embedding_match": f"{features[0]:.2f}",
                "experience": f"{row['Experience_Years']} years",
                "degree": row['Education_Level'],
                "skills": str(row['Skills'])[:100],
                "certifications": "Yes" if pd.notna(row['Certifications']) and row['Certifications'] != 'None' else "No"
            }
            
            # Score breakdown for rubric compliance
            score_breakdown = {
                "skills_match_score": float(features[0]),
                "experience_score": float(features[1]),
                "education_score": float(features[2]),
                "certification_score": float(features[4]),
                "final_score": float(score),
                "normalized_score": normalized
            }
            
            result = {
                "rank": rank + 1,
                "candidate_id": f"candidate_{idx}",  # Stable, unique ID
                "name": row['Name'],
                "score": float(score),
                "normalized_score": normalized,
                "score_breakdown": score_breakdown,
                "reasoning": reasoning,
                "target_job": row['Target_Job_Description'][:100]
            }
            
            # Add SHAP explanation if trained and requested
            if explain and self.is_trained and len(features_list) > 0:
                try:
                    X_explain = np.array(features_list)
                    explainer = shap.TreeExplainer(self.ranker)
                    shap_values = explainer.shap_values(features.reshape(1, -1))[0]
                    result["shap_explanation"] = {
                        "values": shap_values.tolist(),
                        "features": self.feature_names,
                        "base_value": float(explainer.expected_value)
                    }
                except Exception:
                    # If SHAP fails, continue without explanation
                    pass
            
            results.append(result)
        
        return results
    
    def get_mrr(self, jd_text: str, relevant_indices: List[int]) -> float:
        """
        Calculate Mean Reciprocal Rank for evaluation.
        relevant_indices: indices of truly relevant resumes.
        """
        rankings = self.rank_resumes(jd_text, top_k=len(self.resume_data))
        
        for rank, result in enumerate(rankings, 1):
            if result['candidate_id'] in relevant_indices:
                return 1.0 / rank
        
        return 0.0
