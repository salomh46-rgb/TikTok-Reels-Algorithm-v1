"""
High-level Feed Service Orchestrator for TikTok / Reels Algorithm v1.
Manages video catalog, user profile registry, 3-stage recommendation pipeline,
and real-time feedback ingestion.
"""

from typing import Dict, List, Tuple
from reels_engine.models.video import Video
from reels_engine.models.interaction import UserInteraction
from reels_engine.core.user_profile import UserProfile
from reels_engine.core.candidate_retrieval import CandidateRetriever
from reels_engine.core.ranking import FeedRanker
from reels_engine.core.diversity import DiversityFilter


class TikTokFeedService:
    """
    End-to-end TikTok / Reels Recommendation Service.
    """

    def __init__(self):
        self.catalog: Dict[str, Video] = {}
        self.users: Dict[str, UserProfile] = {}
        self.retriever = CandidateRetriever(self.catalog)
        self.ranker = FeedRanker()
        self.diversity_filter = DiversityFilter()

        self._seed_sample_catalog()

    def get_or_create_user(self, user_id: str) -> UserProfile:
        if user_id not in self.users:
            self.users[user_id] = UserProfile(user_id)
        return self.users[user_id]

    def add_video(self, video: Video) -> None:
        self.catalog[video.video_id] = video

    def get_feed(self, user_id: str, count: int = 5) -> List[Tuple[Video, float, dict]]:
        """
        Executes the full 3-Stage recommendation pipeline:
        1. Candidate Retrieval
        2. Multi-Objective Utility Ranking
        3. Diversity & Anti-Fatigue Filtering
        """
        user = self.get_or_create_user(user_id)

        # Stage 1: Retrieval
        candidates = self.retriever.retrieve_candidates(user, max_candidates=30)

        # Stage 2: Ranking
        scored_candidates = self.ranker.rank_candidates(candidates, user)

        # Stage 3: Diversity filtering
        feed = self.diversity_filter.filter_and_diversify(scored_candidates, target_count=count)
        return feed

    def record_interaction(
        self,
        user_id: str,
        video_id: str,
        watch_time_sec: float,
        liked: bool = False,
        shared: bool = False,
    ) -> UserProfile:
        """
        Ingests user view telemetry and executes real-time online profile adaptation.
        """
        user = self.get_or_create_user(user_id)
        video = self.catalog.get(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found in catalog")

        interaction = UserInteraction(
            user_id=user_id,
            video_id=video_id,
            watch_time_sec=watch_time_sec,
            video_duration_sec=video.duration_sec,
            liked=liked,
            shared=shared,
        )

        user.update(interaction, video)

        # Update global video counters
        video.views += 1
        if interaction.is_completed:
            video.completions += 1
        if interaction.liked:
            video.likes += 1
        if interaction.shared:
            video.shares += 1
        if interaction.is_quick_skip:
            video.skips += 1

        return user

    def _seed_sample_catalog(self) -> None:
        """Seeds realistic short-form video database across diverse niches."""
        sample_videos = [
            # Tech / Coding
            Video("v_tech_1", "Python 3.14 xususiyatlari 60 soniyada", "DevNinja", "tech", ["python", "coding", "ai"], 15.0, 1000, 700, 450, 120, 80),
            Video("v_tech_2", "Rust nima uchun C++ dan xavfsizroq?", "CodeMaster", "tech", ["rust", "systems", "memory"], 20.0, 800, 500, 310, 80, 100),
            Video("v_tech_3", "Docker konteynerini noldan yasash", "DevOpsUz", "tech", ["docker", "devops", "linux"], 30.0, 1200, 850, 600, 190, 70),
            Video("v_tech_4", "Neovim sozlash: VS Code dan 10x tezroq", "VimGod", "tech", ["neovim", "terminal", "editor"], 18.0, 600, 400, 250, 50, 70),
            
            # Cooking / Food
            Video("v_food_1", "Samarqandcha palov tayyorlash siri", "OshPaz", "cooking", ["palov", "milliy", "go'sht"], 25.0, 2500, 1800, 1200, 450, 120),
            Video("v_food_2", "Qarsildoq pitsa xamirini tayyorlash", "PizzaChef", "cooking", ["pitsa", "fastfood", "xamir"], 15.0, 1400, 950, 620, 200, 110),
            Video("v_food_3", "Steyk pishirishning 3 ta oltin qoidasi", "MeatMaster", "cooking", ["steyk", "go'sht", "restoran"], 22.0, 1900, 1400, 900, 320, 90),
            Video("v_food_4", "5 daqiqada tayyor bo'ladigan nonushta", "HealthyFood", "cooking", ["nonushta", "tuxum", "tezkor"], 12.0, 900, 600, 350, 90, 80),

            # Cars / Automotive
            Video("v_car_1", "BMW M5 CS 0-100 km/soat sinovi", "AutoDrive", "cars", ["bmw", "m5", "tezlik", "drift"], 18.0, 3200, 2400, 1900, 700, 150),
            Video("v_car_2", "Porsche 911 GT3 RS aerodinamikasi", "SpeedHunter", "cars", ["porsche", "supercar", "trek"], 20.0, 2800, 2100, 1600, 580, 120),
            Video("v_car_3", "Elektromobillar qishda qancha yuradi?", "EVReview", "cars", ["tesla", "elektrokar", "akkumulyator"], 25.0, 1500, 900, 500, 150, 180),
            Video("v_car_4", "Toshkent ko'chalarida drift san'ati", "DriftTashkent", "cars", ["drift", "toshkent", "sport"], 15.0, 4000, 3100, 2500, 1100, 100),

            # Fitness / Gym
            Video("v_fit_1", "Turnikda tortilishni 0 dan 20 taga chiqarish", "GymBro", "fitness", ["turnik", "sport", "mashq"], 20.0, 1100, 750, 510, 190, 90),
            Video("v_fit_2", "Qorin mushaklari (press) uchun 4 ta mashq", "FitCoach", "fitness", ["press", "ozish", "qorin"], 15.0, 2100, 1400, 1000, 340, 140),
            Video("v_fit_3", "Bicepsni to'g'ri o'stirish anatomiyasi", "MuscleLab", "fitness", ["biceps", "kuch", "zal"], 22.0, 1300, 900, 600, 180, 100),

            # Humor / Comedy
            Video("v_humor_1", "Dasturchi va mijoz o'rtasidagi suhbat", "TrollDev", "comedy", ["hazil", "it", "mijoz"], 16.0, 5000, 4100, 3500, 1800, 120),
            Video("v_humor_2", "Qarindoshlar to'yida sodir bo'ladigan holatlar", "KulguShow", "comedy", ["to'y", "uzb", "kulgu"], 18.0, 6500, 5200, 4200, 2200, 150),
            Video("v_humor_3", "Ertalab uyg'onish qiyin bo'lganida", "DailyMeme", "comedy", ["ertalab", "uyqu", "mem"], 10.0, 4200, 3300, 2700, 1100, 90),

            # Travel
            Video("v_travel_1", "Zomin tog'laridagi aqlbovar qilmas manzara", "TravelerUz", "travel", ["zomin", "tog'", "tabiat"], 20.0, 1700, 1200, 850, 300, 80),
            Video("v_travel_2", "Buxoroning 1000 yillik qadimiy ko'chalari", "SilkRoad", "travel", ["buxoro", "tarix", "sayohat"], 24.0, 1900, 1300, 920, 350, 70),
        ]
        for v in sample_videos:
            self.add_video(v)
