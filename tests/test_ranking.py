"""Tests for ranking engine determinism, stable sorting, and score breakdowns."""

import pytest


JD_TEXT = "Senior Python Machine Learning Engineer with AWS and TensorFlow experience"


class TestRankingDeterminism:
    """Verify same input always produces identical output."""

    def test_same_input_identical_output(self, ranking_engine):
        """Run ranking twice with identical input — results must be identical."""
        result_1 = ranking_engine.rank_resumes(JD_TEXT, top_k=5)
        result_2 = ranking_engine.rank_resumes(JD_TEXT, top_k=5)

        assert len(result_1) == len(result_2)
        for r1, r2 in zip(result_1, result_2):
            assert r1["candidate_id"] == r2["candidate_id"]
            assert r1["score"] == r2["score"]
            assert r1["rank"] == r2["rank"]
            assert r1["normalized_score"] == r2["normalized_score"]

    def test_no_randomness_across_invocations(self, ranking_engine):
        """Three successive calls must yield identical orderings."""
        results = [ranking_engine.rank_resumes(JD_TEXT, top_k=3) for _ in range(3)]
        ids_lists = [[r["candidate_id"] for r in res] for res in results]
        assert ids_lists[0] == ids_lists[1] == ids_lists[2]


class TestStableSorting:
    """Verify tie-breaking is deterministic (ascending candidate_id)."""

    def test_stable_tiebreak_by_candidate_id(self, ranking_engine):
        """When scores are equal, lower candidate_id should rank first."""
        results = ranking_engine.rank_resumes(JD_TEXT, top_k=5)
        # Verify ordering: descending score, ascending id on tie
        for i in range(len(results) - 1):
            a, b = results[i], results[i + 1]
            assert a["score"] >= b["score"], "Results must be sorted descending by score"
            if a["score"] == b["score"]:
                a_idx = int(a["candidate_id"].split("_")[1])
                b_idx = int(b["candidate_id"].split("_")[1])
                assert a_idx < b_idx, "Ties must break by ascending candidate_id"


class TestScoreBreakdown:
    """Verify score_breakdown is complete and transparent."""

    def test_score_breakdown_fields_present(self, ranking_engine):
        """Every ranked candidate must expose a full score_breakdown."""
        results = ranking_engine.rank_resumes(JD_TEXT, top_k=5)
        required_keys = {
            "skills_match_score",
            "experience_score",
            "education_score",
            "certification_score",
            "final_score",
            "normalized_score",
        }
        for r in results:
            assert "score_breakdown" in r
            assert required_keys.issubset(set(r["score_breakdown"].keys()))

    def test_scores_are_numeric(self, ranking_engine):
        """All scores must be numeric (float)."""
        results = ranking_engine.rank_resumes(JD_TEXT, top_k=5)
        for r in results:
            bd = r["score_breakdown"]
            for key in bd:
                assert isinstance(bd[key], (int, float)), f"{key} must be numeric"

    def test_normalized_score_range(self, ranking_engine):
        """normalized_score must be in [0, 1]."""
        results = ranking_engine.rank_resumes(JD_TEXT, top_k=5)
        for r in results:
            assert 0.0 <= r["normalized_score"] <= 1.0

    def test_top_k_respects_limit(self, ranking_engine):
        """Must return no more than top_k results."""
        results = ranking_engine.rank_resumes(JD_TEXT, top_k=2)
        assert len(results) == 2

    def test_rank_numbers_sequential(self, ranking_engine):
        """Rank numbers must be 1, 2, 3, ..."""
        results = ranking_engine.rank_resumes(JD_TEXT, top_k=5)
        for i, r in enumerate(results):
            assert r["rank"] == i + 1

    def test_reasoning_fields_present(self, ranking_engine):
        """Each result must have a reasoning dict with key fields."""
        results = ranking_engine.rank_resumes(JD_TEXT, top_k=3)
        for r in results:
            assert "reasoning" in r
            assert "experience" in r["reasoning"]
            assert "degree" in r["reasoning"]
