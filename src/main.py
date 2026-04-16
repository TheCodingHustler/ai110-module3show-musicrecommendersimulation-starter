"""
Command line runner for the Music Recommender Simulation.

Runs six user profiles:
  - Three standard profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock)
  - Three adversarial/edge-case profiles designed to expose scoring weaknesses
"""
try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


PROFILES = [
    # ── Standard profiles ──────────────────────────────────────────────────
    {
        "label": "High-Energy Pop",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    },
    {
        "label": "Chill Lofi Study",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    },
    {
        "label": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
    },
    # ── Adversarial / edge-case profiles ───────────────────────────────────
    {
        # Conflict: calm classical genre but target energy that classical never reaches
        "label": "EDGE: Classical but High-Energy",
        "prefs": {"genre": "classical", "mood": "melancholic", "energy": 0.95, "likes_acoustic": True},
    },
    {
        # Genre not in catalog at all — pure energy + mood fallback
        "label": "EDGE: Unknown Genre (k-pop)",
        "prefs": {"genre": "k-pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
    },
    {
        # Contradictory: wants dreamy/low-energy but metal-level aggression
        "label": "EDGE: Conflicting Mood vs Energy",
        "prefs": {"genre": "electronic", "mood": "dreamy", "energy": 0.05, "likes_acoustic": False},
    },
]


def print_profile(label: str, prefs: dict, recommendations: list) -> None:
    width = 56
    print()
    print("=" * width)
    print(f"  {label}")
    pref_str = "  " + "  ".join(f"{k}={v}" for k, v in prefs.items())
    print(pref_str)
    print("=" * width)
    print(f"  {'#':<3} {'Title':<22} {'Artist':<16} {'Score'}")
    print(f"  {'-'*3} {'-'*22} {'-'*16} {'-'*5}")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  {rank:<3} {song['title']:<22} {song['artist']:<16} {score:.2f}")
        print(f"      {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    for profile in PROFILES:
        recs = recommend_songs(profile["prefs"], songs, k=5)
        print_profile(profile["label"], profile["prefs"], recs)


if __name__ == "__main__":
    main()
