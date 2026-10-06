"""
Real-time Dynamic User Interest Profile for TikTok / Reels.
Updates user category/creator/tag weights instantaneously using implicit & explicit signals.
"""

from typing import Dict, List, Set
from reels_engine.models.interaction import UserInteraction
from reels_engine.models.video import Video


class UserProfile:
    """
    Maintains user preferences and real-time behavioral affinity state.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        # category -> affinity score in [0.0, 1.0]
        self.category_affinity: Dict[str, float] = {}
        # tag -> affinity score in [0.0, 1.0]
        self.tag_affinity: Dict[str, float] = {}
        # creator -> affinity score in [0.0, 1.0]
        self.creator_affinity: Dict[str, float] = {}
        # video_ids seen in current session
        self.seen_videos: Set[str] = set()
        self.total_interactions = 0

    def get_category_affinity(self, category: str) -> float:
        """Returns category affinity, default 0.20 for unvisited categories (mild prior)."""
        return self.category_affinity.get(category, 0.20)

    def get_tag_affinity(self, tag: str) -> float:
        return self.tag_affinity.get(tag, 0.15)

    def get_creator_affinity(self, creator: str) -> float:
        return self.creator_affinity.get(creator, 0.10)

    def update(self, interaction: UserInteraction, video: Video) -> None:
        """
        Calculates delta based on implicit and explicit feedback and applies
        an exponential moving update to affinities.
        """
        self.seen_videos.add(interaction.video_id)
        self.total_interactions += 1

        delta = 0.0

        # 1. Quick Skip penalty (Strong negative signal)
        if interaction.is_quick_skip:
            delta -= 0.20
        else:
            # 2. Watch duration rewards
            if interaction.is_loop:
                # Replay/Loop is the holy grail of TikTok algorithms
                delta += 0.35
            elif interaction.is_completed:
                delta += 0.20
            elif interaction.watch_ratio >= 0.50:
                delta += 0.10

            # 3. Explicit feedback rewards
            if interaction.liked:
                delta += 0.25
            if interaction.shared:
                delta += 0.30

        # Update category affinity with momentum
        current_cat_score = self.get_category_affinity(video.category)
        new_cat_score = max(0.02, min(1.0, current_cat_score + delta))
        self.category_affinity[video.category] = round(new_cat_score, 4)

        # Update tag affinities
        for tag in video.tags:
            current_tag_score = self.get_tag_affinity(tag)
            new_tag_score = max(0.02, min(1.0, current_tag_score + (delta * 0.7)))
            self.tag_affinity[tag] = round(new_tag_score, 4)

        # Update creator affinity
        current_creator_score = self.get_creator_affinity(video.creator)
        new_creator_score = max(0.02, min(1.0, current_creator_score + (delta * 0.8)))
        self.creator_affinity[video.creator] = round(new_creator_score, 4)
