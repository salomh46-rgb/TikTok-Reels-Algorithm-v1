"""
Stage 2: Ranking & Multi-Task Scoring (Reytinglash va Ball berish).
Implements ByteDance / Monolith multi-objective engagement prediction.
Combines predicted loop, completion, like, share, and skip probabilities.
"""

from typing import List, Tuple
from reels_engine.models.video import Video
from reels_engine.core.user_profile import UserProfile


class FeedRanker:
    """
    Ranks candidate videos using calibrated multi-objective utility scoring.
    """

    # Multi-task objective weights based on modern short-form video models
    W_LOOP = 4.0        # Replay/loop is the single most valuable engagement metric
    W_FINISH = 2.5      # Watch to completion
    W_LIKE = 1.8        # Explicit appreciation
    W_SHARE = 2.2       # High viral propensity
    W_SKIP = 3.2        # Immediate swipe penalty

    @classmethod
    def calculate_score(cls, video: Video, user: UserProfile) -> Tuple[float, dict]:
        """
        Calculates expected utility score for (user, video) pair.
        Returns total score and breakdown of objective probabilities.
        """
        cat_affinity = user.get_category_affinity(video.category)
        creator_affinity = user.get_creator_affinity(video.creator)
        
        # Aggregate tag affinity
        tag_scores = [user.get_tag_affinity(t) for t in video.tags]
        tag_affinity = sum(tag_scores) / len(tag_scores) if tag_scores else 0.15

        # Blended personalized affinity
        personal_affinity = (cat_affinity * 0.60) + (tag_affinity * 0.25) + (creator_affinity * 0.15)

        # Multi-objective probability approximations
        p_finish = min(0.98, max(0.05, (personal_affinity * 0.7) + (video.completion_rate * 0.3)))
        p_loop = min(0.90, max(0.01, (personal_affinity ** 1.5) * 0.5 + (video.like_rate * 0.2)))
        p_like = min(0.95, max(0.02, (personal_affinity * 0.6) + (video.like_rate * 0.4)))
        p_share = min(0.80, max(0.01, (personal_affinity * 0.4) + ((video.shares / max(1, video.views)) * 0.6)))
        p_skip = min(0.95, max(0.05, ((1.0 - personal_affinity) * 0.7) + (video.skip_rate * 0.3)))

        # Final multi-task score
        score = (
            (cls.W_LOOP * p_loop)
            + (cls.W_FINISH * p_finish)
            + (cls.W_LIKE * p_like)
            + (cls.W_SHARE * p_share)
            - (cls.W_SKIP * p_skip)
        )

        breakdown = {
            "p_loop": round(p_loop, 3),
            "p_finish": round(p_finish, 3),
            "p_like": round(p_like, 3),
            "p_share": round(p_share, 3),
            "p_skip": round(p_skip, 3),
            "personal_affinity": round(personal_affinity, 3),
            "final_score": round(score, 3),
        }
        return score, breakdown

    def rank_candidates(self, candidates: List[Video], user: UserProfile) -> List[Tuple[Video, float, dict]]:
        """
        Ranks candidate videos in descending order of predicted score.
        """
        scored_items = []
        for v in candidates:
            score, breakdown = self.calculate_score(v, user)
            scored_items.append((v, score, breakdown))

        # Sort descending by score
        scored_items.sort(key=lambda item: item[1], reverse=True)
        return scored_items
