"""
Unit tests for diversity filter and anti-fatigue re-ranking.
"""

from reels_engine.core.diversity import DiversityFilter
from reels_engine.models.video import Video


def test_diversity_avoids_consecutive_categories():
    filter_engine = DiversityFilter()

    # 4 tech videos and 2 cooking videos with artificial scores
    candidates = [
        (Video("v1", "Tech 1", "CreatorA", "tech"), 10.0, {}),
        (Video("v2", "Tech 2", "CreatorB", "tech"), 9.5, {}),
        (Video("v3", "Cooking 1", "ChefA", "cooking"), 8.0, {}),
        (Video("v4", "Tech 3", "CreatorC", "tech"), 7.5, {}),
        (Video("v5", "Cooking 2", "ChefB", "cooking"), 7.0, {}),
    ]

    diversified = filter_engine.filter_and_diversify(candidates, target_count=4)

    # Check that no two adjacent videos share the same category
    for i in range(len(diversified) - 1):
        cat1 = diversified[i][0].category
        cat2 = diversified[i + 1][0].category
        assert cat1 != cat2, f"Consecutive categories detected: {cat1} followed by {cat2}"
