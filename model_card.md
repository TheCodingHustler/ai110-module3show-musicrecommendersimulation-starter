# Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

I picked this name because the whole point of the system is to match a song's "vibe" to what the user is feeling. It's simple but it describes what the thing actually does.

---

## 2. Goal / Task

VibeFinder tries to answer one question: *given what a user likes, which songs in the catalog should I show them first?*

It looks at a user's favorite genre, mood, energy level, and whether they like acoustic music. Then it scores every song in the catalog based on how well it fits those preferences. The top 5 scores become the recommendations.

This is not a "smart" AI that learns from you. It's more like a very organized checklist. You tell it what you want, it checks every song, and it gives back the ones that matched best.

---

## 3. Algorithm Summary

Here's how the scoring works in plain English:

Every song starts at zero points. Then it earns points in four categories:

- **Genre match** — worth the most (2 points). If the song's genre matches what you asked for, you get the full 2 points. If not, you get zero. I gave this the most weight because genre is kind of a dealbreaker — a jazz fan usually doesn't want a metal song, even if the energy is perfect.

- **Mood match** — worth 1 point. Same idea: if the song's mood label matches yours, you get the point. If not, you don't.

- **Energy** — worth up to 1.5 points. This one is different because it's a sliding scale. If a song's energy is really close to your target, you get close to 1.5 points. If it's far away, you get less. The formula is `1.5 × (1 - how far apart they are)`.

- **Acousticness** — worth up to 0.5 points. If you like acoustic music, songs with high acousticness score better. If you don't, produced/electronic-sounding songs score better.

After all four categories are added up (max 5.0 points total), the score gets divided by 5 to put it on a 0 to 1 scale. Then all 18 songs are sorted from highest to lowest, and the top 5 come back with a note explaining which categories they earned points in.

---

## 4. Data Used

The dataset is `data/songs.csv` — 18 songs total.

Each song has: title, artist, genre, mood, energy (0.0 to 1.0), tempo in BPM, valence (how "positive" it sounds), danceability, and acousticness.

Genres in the catalog: pop, lofi, rock, jazz, synthwave, indie pop, classical, hip-hop, reggae, country, metal, R&B, funk, electronic, and ambient.

Some genres only have **one song**. Rock has one. Classical has one. Jazz has one. That's a real problem because if you like jazz, the system has basically nothing to compare — you'll always get the same song at #1 with no variety.

I didn't add or remove any songs from the starter dataset. The catalog is pretty small and mostly Western pop-adjacent music. There's no K-pop, no Afrobeats, no Latin genres. So users who like those styles will get zero genre matches and the system quietly fails without telling them.

---

## 5. Observed Behavior / Biases

**The system works really well when the genre is represented.**
For the "Chill Lofi Study" profile, the top 3 results were all lofi songs and they ranked in exactly the order I expected. Library Rain scored 0.99 — almost perfect. That felt genuinely good.

**But the system gets confidently wrong when there's a conflict between genre and energy.**
I tested a "Classical but High-Energy" profile — someone who wants intense classical music at energy 0.95. The system still recommended Moonlit Sonata (a slow, quiet piano piece with energy 0.22) as #1, with a score of 0.77. That's really wrong, and the scary part is the system sounds confident about it. It doesn't know it made a mistake.

The reason is that genre + mood together are worth 3 out of 5 points max. Energy is only worth 1.5. So even a huge energy mismatch can't overcome a genre + mood match. In the classical case there's only one classical song in the entire catalog, so the system has no choice but to give you that one song no matter what.

**Mood matching is brittle.**
"Intense" and "aggressive" sound basically the same to a human. But the system treats them as completely different labels and gives zero points for a near-miss. A rock fan who says "intense" gets no mood credit for Shatter, which is labeled "aggressive." That doesn't feel right.

**Unknown genres silently fail.**
If you type "k-pop" as your genre, no song in the catalog matches, so the max score anyone can get is 0.60. The system just quietly returns lower-quality results without saying "hey, we don't have any k-pop." A user would have no idea why their top recommendation only scored 0.58.

---

## 6. Evaluation Process

I ran six profiles through the recommender and looked at the results:

- **High-Energy Pop** — worked as expected. Sunrise City hit 0.96, Gym Hero was second. The gap between them made sense because Sunrise City matched mood and Gym Hero didn't.

- **Chill Lofi Study** — best results of all six. All three lofi songs in the catalog landed in the top 3 and in the right order. If this were a real app, these recommendations would actually be good.

- **Deep Intense Rock** — Storm Runner was a perfect 0.99 at #1. But #2 through #5 were all wrong genres because there's only one rock song. The catalog is the bottleneck here.

- **EDGE: Classical + High-Energy** — this is where I found the biggest failure. The user asked for intense classical (energy 0.95), and got a quiet piano piece (energy 0.22) as the top result. Genre dominates so hard that the energy preference basically doesn't matter.

- **EDGE: Unknown Genre (k-pop)** — the system still gave back a top 5, but all scores were below 0.60. It degraded gracefully, meaning it didn't crash, but it also didn't warn the user.

- **EDGE: Conflicting Mood vs Energy** — asked for dreamy electronic at energy 0.05 (nearly silent). Got Neon Pulse at 0.78 — a mid-energy track — because genre and mood matched. Energy preference was basically ignored.

I also ran an experiment where I halved the genre weight (2.0 → 1.0) and doubled the energy weight (1.5 → 3.0). The classical edge case still failed — Moonlit Sonata still won. That told me the problem isn't just the weights. It's the size of the catalog. With only one classical song, no math can produce variety for that user.

---

## 7. Intended Use and Non-Intended Use

**What it's for:**
- Classroom exploration and learning about how recommender systems work
- Demonstrating how weighted scoring turns data into ranked suggestions
- Practicing content-based filtering with a small, readable dataset

**What it's NOT for:**
- Real music discovery for actual users — the catalog is too small and too limited
- Replacing or comparing to apps like Spotify or Apple Music
- Any situation where the recommendations actually matter to someone
- Users who prefer genres not represented in the dataset (K-pop, Afrobeats, Latin, etc.)
- Adapting to a user's taste over time — this system has no memory

---

## 8. Ideas for Improvement

**1. Way more songs, more genres.**
18 songs is the core problem. If I had 200+ songs with at least 10 per genre, the energy and mood signals would actually have room to matter within a genre. Right now, genre is basically a "yes you get results / no you don't" gate.

**2. Fuzzy mood matching.**
Instead of exact string comparisons, I'd build a small similarity table where "intense" and "aggressive" are 80% similar, "chill" and "relaxed" are 90% similar, etc. This would fix the Shatter problem and make the mood signal a lot more useful.

**3. Tell the user when their genre isn't in the catalog.**
If zero songs match the requested genre, print something like: "No k-pop in catalog — showing closest matches by mood and energy." Right now the system is silent about this failure, which is worse than just telling the truth.

---

## 9. Personal Reflection

Honestly, before this project I thought recommender systems were way more complicated than what I built here. Like I assumed Spotify must be doing something really sophisticated. And maybe it is — but the core idea is the same loop I wrote: score every song, sort the list, give back the top ones. The "magic" is just in which features you pick and how you weight them.

My biggest learning moment was the Classical + High-Energy edge case. I built the system myself and I still didn't expect it to fail that way. It gave me a confident 0.77 score with a polished explanation for a recommendation that was genuinely wrong. That gap between "sounds right" and "is right" is something I'm going to think about a lot. Real AI tools do this all the time — they produce confident output that looks correct but isn't — and now I understand why that happens at a mechanical level.

AI tools helped me a ton during this project, especially for figuring out how to structure the scoring function and for thinking through edge cases. But I had to double-check a lot. When I first asked for a scoring formula, the suggestion didn't normalize the output correctly — the numbers could go over 1.0. I had to catch that myself and fix the denominator. The AI gave me a starting point, but the reasoning about whether it was right was still on me.

What surprised me most was how much personality the output has even though the logic is so simple. When the system says "Because: genre match (+2.0), mood match (+1.0), energy proximity (+1.47)" it actually sounds like a thoughtful recommendation. It doesn't feel like math. That's kind of unsettling when you think about it — users might trust the explanation without realizing it's just addition.

If I kept working on this I'd want to try two things. First, add collaborative filtering — "users who like lofi also liked these ambient songs" — so the system can suggest things the user didn't know to ask for. Second, I'd add a diversity penalty so the top 5 can't all be the same genre. Right now a lofi fan just gets the three lofi songs plus two fallbacks. A better system would try to introduce one surprising but relevant pick.
