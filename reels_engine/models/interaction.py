"""
User interaction telemetry model for TikTok / Reels.
Captures implicit signals (watch time, loops) and explicit feedback (likes, shares, skips).
"""

from dataclasses import dataclass
import time


@dataclass
class UserInteraction:
    user_id: str
    video_id: str
    watch_time_sec: float
    video_duration_sec: float
    liked: bool = False
    shared: bool = False
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    @property
    def watch_ratio(self) -> float:
        """Ratio of watch time to total duration (>1.0 indicates loop/replay)."""
        if self.video_duration_sec <= 0:
            return 0.0
        return self.watch_time_sec / self.video_duration_sec

    @property
    def is_completed(self) -> bool:
        """Did user finish watching the entire clip at least once?"""
        return self.watch_ratio >= 0.90

    @property
    def is_loop(self) -> bool:
        """Did user watch it more than once? (Strongest positive engagement signal in TikTok)"""
        return self.watch_ratio >= 1.25

    @property
    def is_quick_skip(self) -> bool:
        """Did user swipe away within 2.5 seconds or less than 25%?"""
        return self.watch_time_sec <= 2.5 or self.watch_ratio < 0.25
