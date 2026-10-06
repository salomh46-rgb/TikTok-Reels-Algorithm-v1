"""
Video model representation for TikTok / Reels Recommendation Engine.
Contains metadata, categorization, content tags, and global engagement metrics.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Video:
    video_id: str
    title: str
    creator: str
    category: str  # e.g., 'coding', 'cooking', 'cars', 'fitness', 'travel', 'humor'
    tags: List[str] = field(default_factory=list)
    duration_sec: float = 20.0
    
    # Global population metrics (used for cold-start priors)
    views: int = 100
    completions: int = 40
    likes: int = 20
    shares: int = 5
    skips: int = 20

    @property
    def completion_rate(self) -> float:
        return self.completions / max(1, self.views)

    @property
    def like_rate(self) -> float:
        return self.likes / max(1, self.views)

    @property
    def skip_rate(self) -> float:
        return self.skips / max(1, self.views)

    @property
    def global_quality_score(self) -> float:
        """Normalized baseline score (0.0 - 1.0) based on global audience response."""
        return (
            (self.completion_rate * 0.45)
            + (self.like_rate * 0.35)
            + ((self.shares / max(1, self.views)) * 0.20)
            - (self.skip_rate * 0.25)
        )
