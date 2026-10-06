#!/usr/bin/env python3
"""
Interactive Terminal TikTok / Reels Simulator.
Allows the user to experience the recommendation algorithm in real time!
Controls:
[Enter] or [1] -> Watch full (1.0x duration)
[2]            -> Loop / Replay twice (1.5x duration + High reward)
[3]            -> Like & Watch full
[4]            -> Share & Like
[5] or [s]     -> Quick Skip (Swipe away in 1.5s -> Negative penalty)
[q]            -> Quit
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
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def run_interactive_reels():
    print(f"""
{CYAN}======================================================================{RESET}
{BOLD}{MAGENTA}   📱 TIKTOK / REELS ALGORITHM v1 - INTERAKTIV TERMINAL FEED{RESET}
{DIM}      (Ko'rish vaqti va reaksiyalaringiz orqali AI didingizni o'rganadi){RESET}
{CYAN}======================================================================{RESET}
""")

    user_name = input(f"{BOLD}Ismingizni kiriting (masalan: jasper): {RESET}").strip()
    if not user_name:
        user_name = "jasper"

    service = TikTokFeedService()
    user_id = f"user_{user_name.lower()}"

    video_counter = 0

    while True:
        # Fetch next batch of personalized recommendations
        feed = service.get_feed(user_id, count=3)
        if not feed:
            print(f"{YELLOW}Barcha videolar ko'rib bo'lindi!{RESET}")
            break

        for video, score, breakdown in feed:
            video_counter += 1
            print(f"\n{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
            print(f"{BOLD}🎬 VIDEO #{video_counter}:{RESET} {BOLD}{video.title}{RESET}")
            print(f"   Muallif: {YELLOW}@{video.creator}{RESET} | Toifa: {GREEN}[{video.category.upper()}]{RESET} | Davomiyligi: {video.duration_sec:.0f}s")
            print(f"   Teglar: {DIM}#{' #'.join(video.tags)}{RESET}")
            print(f"   Algoritm bashorati: {MAGENTA}Ball = {score:+.2f}{RESET} (P_loop: {breakdown['p_loop']:.2f}, P_finish: {breakdown['p_finish']:.2f}, P_skip: {breakdown['p_skip']:.2f})")
            print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")

            print(f"""Harakatingizni tanlang:
  {BOLD}[1]{RESET} yoki {BOLD}[Enter]{RESET} -> Videoni to'liq ko'rish (Watch full)
  {BOLD}[2]{RESET}         -> Qayta-qayta ko'rish (Loop / Replay) 🔁 {MAGENTA}(Eng yuqori qiziqish){RESET}
  {BOLD}[3]{RESET}         -> Ko'rish va LAYK bosish ❤️
  {BOLD}[4]{RESET}         -> Ko'rish, LAYK va ULASHISH (Share) 🚀
  {BOLD}[5]{RESET} / {BOLD}[s]{RESET}   -> Darhol keyingisiga o'tkazib yuborish (Quick Skip) ⏩ {RED}(-Jazo){RESET}
  {BOLD}[p]{RESET}         -> Shaxsiy profil ko'rsatkichlarini ko'rish (Profile Stats)
  {BOLD}[q]{RESET}         -> Chiqish
""")

            choice = input(f"{BOLD}Tanlovingiz: {RESET}").strip().lower()

            if choice in ("q", "quit", "exit"):
                print(f"\n{YELLOW}Chiqildi. E'tiboringiz uchun rahmat!{RESET}")
                return

            if choice == "p":
                profile = service.get_or_create_user(user_id)
                print(f"\n{GREEN}📊 SIZNING HOZIRGI QIZIQISHLAR PROFILINGIZ:{RESET}")
                for cat, val in sorted(profile.category_affinity.items(), key=lambda x: x[1], reverse=True):
                    bar = "█" * int(val * 20)
                    print(f"  • {cat:<8}: {val:.2f} {bar}")
                input(f"{DIM}\nDavom etish uchun Enter bosing...{RESET}")
                continue

            # Process action
            if choice == "2":
                print(f"{MAGENTA}🔁 Siz videoni 2 marta qayta ko'rdingiz (Loop)!{RESET}")
                service.record_interaction(user_id, video.video_id, watch_time_sec=video.duration_sec * 1.5)
            elif choice == "3":
                print(f"{GREEN}❤️ Siz videoni ko'rdingiz va layk bosdingiz!{RESET}")
                service.record_interaction(user_id, video.video_id, watch_time_sec=video.duration_sec, liked=True)
            elif choice == "4":
                print(f"{GREEN}🚀 Siz videoni ko'rdingiz, layk bosdingiz va do'stlarga ulashdingiz!{RESET}")
                service.record_interaction(user_id, video.video_id, watch_time_sec=video.duration_sec, liked=True, shared=True)
            elif choice in ("5", "s", "skip"):
                print(f"{RED}⏩ 1.5 soniyada keyingi videoga surib o'tkazdingiz (Skip)!{RESET}")
                service.record_interaction(user_id, video.video_id, watch_time_sec=1.5)
            else:
                # Default: watched full
                print(f"{CYAN}👁️ Videoni oxirigacha ko'rdingiz.{RESET}")
                service.record_interaction(user_id, video.video_id, watch_time_sec=video.duration_sec)


if __name__ == "__main__":
    try:
        run_interactive_reels()
    except KeyboardInterrupt:
        print("\nDastur to'xtatildi.")
