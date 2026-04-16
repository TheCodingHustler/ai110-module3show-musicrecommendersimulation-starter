# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder is a content-based music recommender designed for classroom exploration. It suggests up to five songs from an 18-song catalog by comparing each song's characteristics to a user's stated preferences. The system is not intended for real users or production deployment. Its purpose is to demonstrate how a simple scoring rule can translate data into ranked recommendations, and to surface the tradeoffs and biases that emerge when you choose what to measure and how much to weight it.

The system assumes the user already knows what genre and mood they want. It does not learn from listening history, adapt over time, or consider social signals like what other users play.

---

## 3. How the Model Works

Every song in the catalog gets a "score" that measures how closely it matches what the user asked for. Think of it like a judge at a talent competition scoring each performer on four separate criteria, then averaging the scores.

The four criteria are:

1. **Genre** — Does the song's category (rock, pop, lofi, etc.) match what the user likes? This is a yes-or-no question worth the most points because genre is the strongest signal a listener has — a jazz fan almost never enjoys a metal recommendation, no matter how good the metal song is.

2. **Mood** — Does the song's feeling (happy, chill, intense, etc.) match? Also yes-or-no but worth fewer points than genre.

3. **Energy** — How close is the song's energy level to what the user wants? Energy is a number from 0.0 (completely calm) to 1.0 (extremely intense). Unlike genre and mood, energy is measured on a sliding scale — a song that's almost the right energy still earns partial credit.

4. **Acousticness** — Does the song's production style fit? Acoustic fans are rewarded songs with natural, instrument-forward sound; non-acoustic users are rewarded polished, produced sound.

Once each song has a score, all 18 are sorted from highest to lowest. The top five are returned with a plain-language breakdown of why each one ranked where it did.

---

## 4. Data

The catalog contains 18 songs stored in `data/songs.csv`. Each song has a title, artist, genre, mood, and five numeric attributes: energy, tempo in BPM, valence (emotional positivity), danceability, and acousticness.

The 18 genres represented are: pop (2 songs), lofi (3 songs), rock (1 song), jazz (1 song), synthwave (1 song), indie pop (1 song), classical (1 song), hip-hop (1 song), reggae (1 song), country (1 song), metal (1 song), R&B (1 song), funk (1 song), electronic (1 song), and ambient (1 song).

No songs were added or removed from the starter dataset. The catalog skews toward Western popular music styles with moderate-to-high energy. Genres like classical (1 song) and jazz (1 song) are vastly underrepresented, which means any user who prefers those styles immediately loses access to the genre-match bonus for nearly all songs.

---

## 5. Strengths

The system works well for users whose preferences match a well-represented genre. A "Chill Lofi" user gets a tight, coherent top-3 because lofi has three songs in the catalog and all three score correctly: Library Rain (0.99), Midnight Coding (0.95), and Focus Flow (0.76). The ranking matches intuition exactly — the two songs with both genre and mood matches beat the one with only a genre match.

Similarly, a "High-Energy Pop" user correctly gets Sunrise City first (genre + mood + energy + acousticness all match, score 0.96) and Gym Hero second (genre + energy match, no mood match, score 0.79). The score gap clearly explains why each song placed where it did.

The plain-language explanations — "genre match (+2.0), mood match (+1.0), energy proximity (+1.47)" — make the system's reasoning transparent. A user can immediately understand why a specific song was recommended without knowing anything about how scoring works.

---

## 6. Limitations and Bias

**Genre dominance creates a ceiling for underrepresented tastes.** Genre accounts for 40% of the maximum possible score. A classical music fan targeting high energy (0.95) still gets Moonlit Sonata ranked first (0.77) even though Moonlit Sonata's energy is 0.22 — completely opposite to what they asked for. The genre and mood match (2.0 + 1.0 points) is so strong that it overrides an almost-maximum energy penalty. The system is effectively telling the user "you said classical, here is the only classical song, take it" regardless of any other preference.

**Songs from genres with only one entry are always recommended to that genre's fans, no matter what.** With one rock song (Storm Runner), one classical song (Moonlit Sonata), and one jazz song (Coffee Shop Stories), users who prefer those genres will see the same song at #1 every single time. There is no variety possible.

**Unknown or niche genres break the genre-match entirely.** A user who enters "k-pop" as their favorite genre will get zero genre-match points for every song in the catalog. Their max possible score drops from 1.0 to 0.60, and recommendations fall back entirely to mood and energy — which are weaker signals. The system does not warn the user this is happening.

**The energy score is never zero, which creates a hidden ranking pressure.** Every song earns some energy points because `1.0 - abs(song.energy - target)` always produces a number between 0.0 and 1.0. This means energy quietly shapes the fallback rankings even when genre and mood both miss. Songs with energy close to 0.5 tend to appear in the middle of almost any list because they are "close enough" to most targets.

**Mood comparison is exact string matching.** The moods "intense" and "aggressive" feel nearly identical to a human listener, but the system scores them as completely different. A rock fan who says "intense" gets zero mood points from Shatter ("aggressive"), and zero from Block Party ("energetic"), even though those songs would almost certainly satisfy the listener.

---

## 7. Evaluation

Six user profiles were tested against all 18 songs. Three were designed to represent natural use cases; three were adversarial profiles designed to expose weaknesses in the scoring logic.

**High-Energy Pop** (`genre=pop, mood=happy, energy=0.9`): Results were correct and intuitive. Sunrise City led at 0.96 because it matched on all four signals. Gym Hero was second at 0.79 with genre and energy but no mood match. The system correctly penalized Gym Hero for the mood mismatch.

**Chill Lofi Study** (`genre=lofi, mood=chill, energy=0.35, likes_acoustic=True`): The best-performing profile. Library Rain scored 0.99 — nearly perfect — and the top three were all lofi tracks. The recommendations matched intuition exactly and would be genuinely useful recommendations.

**Deep Intense Rock** (`genre=rock, mood=intense, energy=0.92`): Storm Runner scored 0.99 and was the clear #1. However, #2 was Gym Hero (pop/intense) — wrong genre entirely. This is because only one song in the catalog is rock. Everything after #1 is a genre miss, which exposes how much the catalog limits diversity for niche genres.

**EDGE — Classical but High-Energy** (`genre=classical, mood=melancholic, energy=0.95`): The most revealing result. Moonlit Sonata (energy=0.22) ranked first at 0.77 despite being almost the furthest possible song from the user's energy target. Genre and mood dominated. This is a real failure case — the system would recommend a slow, quiet piano piece to someone who asked for intense, energetic classical music.

**EDGE — Unknown Genre (k-pop)** (`genre=k-pop, mood=happy, energy=0.8`): No genre matches at all. The system fell back to mood and energy, producing reasonable but lower-confidence results. Sunrise City still appeared at #1 on the strength of its mood and energy match. The system did not crash or produce nonsense — it degraded gracefully.

**EDGE — Conflicting Mood vs Energy** (`genre=electronic, mood=dreamy, energy=0.05`): Neon Pulse won at 0.78 because it matched genre (electronic) and mood (dreamy). But Neon Pulse has energy 0.74, which is extremely far from the target 0.05. This is another failure case — the user wanted something almost silent, but got a mid-energy track because the genre and mood labels overrode the energy signal.

**Weight experiment**: Halving the genre weight (2.0→1.0) and doubling the energy weight (1.5→3.0) narrowed the gap between ranked songs but did not fix the Classical edge case — Moonlit Sonata still ranked first (0.60 vs 0.54 for the next best). This shows the bias is not just about the genre weight being too high; the catalog itself is the deeper problem. With only one classical song, no weight adjustment can produce variety for that user.

---

## 8. Future Work

- **Expand the catalog**: 18 songs is too small for genre-match to be meaningful. At 100+ songs per genre, the energy and mood signals would have more room to differentiate within a genre.
- **Semantic mood matching**: Replace exact string comparison with a mood similarity map (e.g., "intense" and "aggressive" score 0.8 against each other instead of 0). This would surface Shatter for a rock/intense fan even though it is labeled "aggressive."
- **Warn on no genre match**: When zero songs in the catalog match the requested genre, tell the user — "No k-pop songs found; showing closest alternatives by mood and energy" — rather than silently returning lower-quality results.
- **Energy range instead of single target**: Many real listeners want a floor, not a point target. A gym user wants energy ≥ 0.8, not exactly 0.8. Range-based scoring already exists in `UserProfile` but is not exposed in the `main.py` interface.
- **Diversity re-ranking**: After scoring, apply a penalty for songs that are too similar to each other. This would prevent the top-5 from being four versions of the same sound.

---

## 9. Personal Reflection

Building this recommender made the invisible math inside streaming apps visible. Spotify and YouTube feel like they "understand" you, but they are running some version of the same loop: score every candidate, sort descending, return top-k. The magic is entirely in which signals you choose and how much weight you give each one.

The most surprising discovery was how much the catalog size matters. No matter how carefully you tune the weights, a dataset with one rock song and one classical song cannot produce diverse recommendations for fans of those genres. The model's limitations are not just in the code — they are baked into the data it was trained on. Real recommenders deal with this by mixing collaborative filtering (what similar users played) with content features, so that even a niche genre fan can discover songs they didn't know to ask for. A pure content-based system like this one has no way to make that leap.

The adversarial profiles were the most educational part. A user with "classical" + energy=0.95 gets confidently wrong results — the system does not know it is confused. It returns Moonlit Sonata with a 0.77 score and a polished explanation, but the recommendation is genuinely bad. That gap between confident output and correct output is exactly why real AI systems need human review, diverse test cases, and honest model cards.
