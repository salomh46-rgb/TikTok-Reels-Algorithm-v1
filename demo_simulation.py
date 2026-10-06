#!/usr/bin/env python3
"""
Multi-Persona Behavioral Simulation for TikTok / Reels Algorithm v1.
Demonstrates how the recommendation engine instantaneously personalizes feeds for 3 distinct personas:
1. 'Jasur' (Software Engineer) -> Focuses on Tech/Coding
2. 'Madina' (Culinary Enthusiast) -> Focuses on Cooking/Food
3. 'Sardor' (Automotive Fan) -> Focuses on Cars/Drift
"""

import sys
from reels_engine.feed_service import TikTokFeedService

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    print(f"""
{CYAN}  _______ _ _    _______    _      _____            _     {RESET}
{CYAN} |__   __(_) |  |__   __|  | |    |  __ \\          | |    {RESET}
{MAGENTA}    | |   _| | __  | | ___ | | __ | |__) |___  ___ | |___ {RESET}
{MAGENTA}    | |  | | |/ /  | |/ _ \\| |/ / |  _  // _ \\/ _ \\| / __|{RESET}
{CYAN}    | |  | |   <   | | (_) |   <  | | \\ \\  __/  __/| \\__ \\{RESET}
{CYAN}    |_|  |_|_|\\_\\  |_|\\___/|_|\\_\\ |_|  \\_\\___|\\___||_|___/{RESET}
{BOLD}        ByteDance / Monolith Inspired Recommendation Engine v1{RESET}
----------------------------------------------------------------------
""")


def simulate_persona(service: TikTokFeedService, user_id: str, persona_name: str, preferred_cat: str):
    print(f"\n{BOLD}{YELLOW}======================================================================{RESET}")
    print(f"{BOLD}👤 SINOV: {persona_name} (Qiziqishi: {preferred_cat.upper()}){RESET}")
    print(f"{DIM}Dastlabki neytral bosqich: foydalanuvchi hali bitta ham video ko'rmagan (Cold Start).{RESET}")

    # 1. First cold feed
    cold_feed = service.get_feed(user_id, count=4)
    print(f"\n{CYAN}1-Feed (Sovuq start - barcha toifalardan aralash):{RESET}")
    for idx, (v, score, b) in enumerate(cold_feed, 1):
        print(f"  {idx}. [{v.category.upper():<7}] {v.title:<36} (Bashorat ball: {score:+.2f})")

    # 2. Simulate viewing session
    print(f"\n{MAGENTA}▶️ Foydalanuvchi ko'rish sessiyasi simulyatsiyasi:{RESET}")
    # User interacts with 2 videos
    for v, _, _ in cold_feed:
        if v.category == preferred_cat:
            # Loop + Like
            print(f"  💚 [{v.category.upper()}] '{v.title}' videoni 2 marta qayta ko'rdi (LOOP) va LAYK bosdi!")
            service.record_interaction(user_id, v.video_id, watch_time_sec=v.duration_sec * 1.5, liked=True)
        else:
            # Quick Skip
            print(f"  ⏩ [{v.category.upper()}] '{v.title}' videoni 1.5 soniyada surib o'tkazib yubordi (SKIP).")
            service.record_interaction(user_id, v.video_id, watch_time_sec=1.5)

    # 3. Check learned user profile
    profile = service.get_or_create_user(user_id)
    print(f"\n{GREEN}🧠 Algoritm o'rgangan profil ko'rsatkichlari (Real-Time Affinity):{RESET}")
    for cat, score in sorted(profile.category_affinity.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(score * 20)
        print(f"  • {cat:<8}: {score:.2f} {bar}")

    # 4. Next personalized feed
    personalized_feed = service.get_feed(user_id, count=4)
    print(f"\n{GREEN}🎯 2-Feed (Algoritm tomonidan 100% shaxsiylashtirilgan yangi lenta):{RESET}")
    for idx, (v, score, b) in enumerate(personalized_feed, 1):
        is_pref = "⭐ TAVSIYA" if v.category == preferred_cat else "🔄 DIVERSITY"
        print(f"  {idx}. [{v.category.upper():<7}] {v.title:<36} (Ball: {score:+.2f}) [{is_pref}]")


def main():
    print_banner()
    service = TikTokFeedService()

    simulate_persona(service, "user_jasur", "Jasur (Senior Dasturchi)", "tech")
    simulate_persona(service, "user_madina", "Madina (Oshpaz / Foodie)", "cooking")
    simulate_persona(service, "user_sardor", "Sardor (Avtomobil & Drift ishqibozi)", "cars")

    print(f"\n{BOLD}{GREEN}=== 🚀 SINOV MUVAFFAQIYATLI YAKUNLANDI! ==={RESET}\n")


if __name__ == "__main__":
    main()
