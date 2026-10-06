"""
Stage 1: Candidate Retrieval (Nomzodlarni saralash).
Filters a large corpus down to high-probability candidate pools:
- High-affinity matches
- Viral/Trending items
- Exploration / Cold-start items
"""

from typing import List, Dict
from reels_engine.models.video import Video
from reels_engine.core.user_profile import UserProfile


class CandidateRetriever:
    """
    Retrieves candidates for scoring stage while filtering previously viewed clips.
    """

    def __init__(self, video_catalog: Dict[str, Video]):
        self.catalog = video_catalog

    def retrieve_candidates(self, user: UserProfile, max_candidates: int = 50) -> List[Video]:
        """
        Retrieves a diversified pool of candidate videos for the ranking pipeline.
        Excludes videos the user has already seen.
        """
        # Step 1: Filter unseen videos
        unseen = [v for vid, v in self.catalog.items() if vid not in user.seen_videos]
        if not unseen:
            # If all seen, fallback to all catalog to prevent blank screen
            unseen = list(self.catalog.values())

        if len(unseen) <= max_candidates:
            return unseen

        # Step 2: Affinity bucket (60% quota)
        # Sort by user category affinity * global quality
        affinity_bucket = sorted(
            unseen,
            key=lambda v: user.get_category_affinity(v.category) * v.global_quality_score,
            reverse=True,
        )

        # Step 3: Viral/Trending bucket (25% quota)
        trending_bucket = sorted(
            unseen,
            key=lambda v: v.global_quality_score,
            reverse=True,
        )

        # Step 4: Explore bucket (15% quota) - items from unvisited categories
        explore_bucket = sorted(
            unseen,
            key=lambda v: user.get_category_affinity(v.category),  # lowest affinity first for discovery
        )

        # Merge with quota guarantees
        num_affinity = int(max_candidates * 0.60)
        num_trending = int(max_candidates * 0.25)
        num_explore = max_candidates - num_affinity - num_trending

        selected: List[Video] = []
        selected_ids = set()

        for pool in (affinity_bucket[:num_affinity], trending_bucket[:num_trending], explore_bucket[:num_explore]):
            for v in pool:
                if v.video_id not in selected_ids:
                    selected.append(v)
                    selected_ids.add(v.video_id)
                    if len(selected) >= max_candidates:
                        break

        # Fill remaining slots if any
        if len(selected) < max_candidates:
            for v in unseen:
                if v.video_id not in selected_ids:
                    selected.append(v)
                    selected_ids.add(v.video_id)
                    if len(selected) >= max_candidates:
                        break

        return selected
