"""
Unit tests for multi-objective ranking calculation.
"""

from reels_engine.core.user_profile import UserProfile
from reels_engine.core.ranking import FeedRanker
from reels_engine.models.video import Video


def test_ranking_prefers_high_affinity_content():
    user = UserProfile("user_techie")
    user.category_affinity["tech"] = 0.90
    user.category_affinity["cooking"] = 0.05

    video_tech = Video("v_t", "Python Code", "Dev", "tech", ["coding"], 15.0)
    video_cook = Video("v_c", "Cake Recipe", "Chef", "cooking", ["cake"], 15.0)

    score_tech, breakdown_tech = FeedRanker.calculate_score(video_tech, user)
    score_cook, breakdown_cook = FeedRanker.calculate_score(video_cook, user)

    assert score_tech > score_cook
    assert breakdown_tech["personal_affinity"] > breakdown_cook["personal_affinity"]
