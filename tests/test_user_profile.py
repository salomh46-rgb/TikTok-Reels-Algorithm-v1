"""
Unit tests for user profile adaptation and affinity scoring.
"""

from reels_engine.core.user_profile import UserProfile
from reels_engine.models.video import Video
from reels_engine.models.interaction import UserInteraction


def test_profile_reward_on_video_loop():
    user = UserProfile("user_1")
    video = Video("v1", "Coding Tips", "Dev", "tech", ["python"], 10.0)

    initial_affinity = user.get_category_affinity("tech")

    # User watches 15 seconds on a 10-second clip (Loop = 1.5x) + Likes it
    interaction = UserInteraction(
        user_id="user_1",
        video_id="v1",
        watch_time_sec=15.0,
        video_duration_sec=10.0,
        liked=True,
    )
    user.update(interaction, video)

    updated_affinity = user.get_category_affinity("tech")
    assert updated_affinity > initial_affinity
    assert updated_affinity >= 0.70  # Massive jump for loop + like


def test_profile_penalty_on_quick_skip():
    user = UserProfile("user_2")
    video = Video("v2", "Cars", "Racer", "cars", ["drift"], 20.0)

    # User swipes away in 1.5 seconds (< 2.5s quick skip)
    interaction = UserInteraction(
        user_id="user_2",
        video_id="v2",
        watch_time_sec=1.5,
        video_duration_sec=20.0,
    )
    user.update(interaction, video)

    affinity = user.get_category_affinity("cars")
    assert affinity < 0.20  # Dropped from default 0.20 prior
