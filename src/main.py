"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""
try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print()
    print("=" * 52)
    print(f"  User profile: genre=pop  mood=happy  energy=0.8")
    print("=" * 52)
    print(f"  {'#':<3} {'Title':<22} {'Artist':<16} {'Score'}")
    print(f"  {'-'*3} {'-'*22} {'-'*16} {'-'*5}")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  {rank:<3} {song['title']:<22} {song['artist']:<16} {score:.2f}")
        print(f"      {explanation}")
        print()


if __name__ == "__main__":
    main()
