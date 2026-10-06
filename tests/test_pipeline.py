"""
End-to-end integration test for the entire TikTok feed pipeline.
"""

from reels_engine.feed_service import TikTokFeedService


def test_full_recommendation_lifecycle_learning():
    service = TikTokFeedService()
    user_id = "test_user_jasper"

    # Step 1: Initial cold feed (balanced)
    initial_feed = service.get_feed(user_id, count=5)
    assert len(initial_feed) == 5

    # Step 2: User repeatedly watches 'cars' clips (loops and likes them)
    # User skips 'cooking' clips immediately
    service.record_interaction(user_id, "v_car_1", watch_time_sec=30.0, liked=True)  # loop on 18s clip
    service.record_interaction(user_id, "v_car_2", watch_time_sec=25.0, liked=True)  # loop on 20s clip
    service.record_interaction(user_id, "v_food_1", watch_time_sec=1.0)              # skip in 1.0s

    user_profile = service.get_or_create_user(user_id)
    assert user_profile.get_category_affinity("cars") > 0.70
    assert user_profile.get_category_affinity("cooking") < 0.15

    # Step 3: Next feed should prioritize car content and deprioritize food
    next_feed = service.get_feed(user_id, count=5)
    categories_in_feed = [v[0].category for v in next_feed]

    assert "cars" in categories_in_feed
    assert categories_in_feed.count("cooking") == 0 or categories_in_feed.index("cars") < categories_in_feed.index("cooking")
