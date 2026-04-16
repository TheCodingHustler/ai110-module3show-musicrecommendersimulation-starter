from typing import List, Dict, Tuple, Union
from dataclasses import dataclass
import csv


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    favorite_genre and favorite_mood accept a single string or a list of strings.
    target_energy accepts a single float or a (min, max) tuple for a range.
    Required by tests/test_recommender.py
    """
    favorite_genre: Union[str, List[str]]
    favorite_mood: Union[str, List[str]]
    target_energy: Union[float, Tuple[float, float]]
    likes_acoustic: bool


def _genre_score(song_genre: str, preference: Union[str, List[str]]) -> float:
    if isinstance(preference, list):
        return 1.0 if song_genre in preference else 0.0
    return 1.0 if song_genre == preference else 0.0


def _mood_score(song_mood: str, preference: Union[str, List[str]]) -> float:
    if isinstance(preference, list):
        return 1.0 if song_mood in preference else 0.0
    return 1.0 if song_mood == preference else 0.0


def _energy_score(song_energy: float, preference: Union[float, Tuple[float, float]]) -> float:
    if isinstance(preference, tuple):
        min_e, max_e = preference
        if min_e <= song_energy <= max_e:
            return 1.0
        return 1.0 - min(abs(song_energy - min_e), abs(song_energy - max_e))
    return 1.0 - abs(song_energy - preference)


def score_song(song: Song, user: UserProfile) -> Tuple[float, List[str]]:
    """
    Weighted scoring recipe (max 5.0 points, normalized to 0.0–1.0):
      +2.0  genre match
      +1.0  mood match
      +1.5  energy proximity  (scales with closeness to target)
      +0.5  acousticness fit  (rewards low acousticness for non-acoustic users, high for acoustic users)

    Returns (score, reasons) where reasons is a list of human-readable point breakdowns.
    """
    reasons: List[str] = []

    genre = _genre_score(song.genre, user.favorite_genre) * 2.0
    if genre > 0:
        reasons.append(f"genre match (+{genre:.1f})")

    mood = _mood_score(song.mood, user.favorite_mood) * 1.0
    if mood > 0:
        reasons.append(f"mood match (+{mood:.1f})")

    energy_pts = _energy_score(song.energy, user.target_energy) * 1.5
    reasons.append(f"energy proximity (+{energy_pts:.2f})")

    acoustic_raw = song.acousticness if user.likes_acoustic else 1.0 - song.acousticness
    acoustic = acoustic_raw * 0.5
    if acoustic >= 0.25:
        reasons.append(f"acousticness fit (+{acoustic:.2f})")

    total = (genre + mood + energy_pts + acoustic) / 5.0
    return total, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = [(song, score_song(song, user)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(song, user)
        if not reasons:
            reasons = ["close match to your overall taste profile"]
        return "Because: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def _score_song_dict(song: Dict, user_prefs: Dict) -> Tuple[float, List[str]]:
    """
    Weighted scoring recipe for the dict-based path (used by main.py).
    Returns (score, reasons) matching the same recipe as score_song.
    """
    reasons: List[str] = []

    genres = user_prefs.get("genres") or [user_prefs.get("genre")]
    moods = user_prefs.get("moods") or [user_prefs.get("mood")]

    genre_pts = 2.0 if song["genre"] in genres else 0.0
    if genre_pts > 0:
        reasons.append(f"genre match (+{genre_pts:.1f})")

    mood_pts = 1.0 if song["mood"] in moods else 0.0
    if mood_pts > 0:
        reasons.append(f"mood match (+{mood_pts:.1f})")

    energy_pref = user_prefs.get("energy")
    min_e = user_prefs.get("min_energy")
    max_e = user_prefs.get("max_energy")
    if min_e is not None and max_e is not None:
        raw_energy = 1.0 if min_e <= song["energy"] <= max_e else 1.0 - min(
            abs(song["energy"] - min_e), abs(song["energy"] - max_e)
        )
    else:
        raw_energy = 1.0 - abs(song["energy"] - (energy_pref or 0.5))
    energy_pts = raw_energy * 1.5
    reasons.append(f"energy proximity (+{energy_pts:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    acoustic_raw = song["acousticness"] if likes_acoustic else 1.0 - song["acousticness"]
    acoustic_pts = acoustic_raw * 0.5
    if acoustic_pts >= 0.25:
        reasons.append(f"acousticness fit (+{acoustic_pts:.2f})")

    total = (genre_pts + mood_pts + energy_pts + acoustic_pts) / 5.0
    return total, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [(song, *_score_song_dict(song, user_prefs)) for song in songs]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        (song, score, "Because: " + ", ".join(reasons))
        for song, score, reasons in scored[:k]
    ]
