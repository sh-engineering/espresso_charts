# Espresso Charts -- Publishing Cadence

## Model

One story per day, six days a week. Each story is one chart, one Reel, one Substack Note, one poster. Sunday is the weekly digest (auto-assembled).

All times CET (Berlin).

---

## Daily Schedule (Monday-Saturday)

| Time | Platform | Format | Notes |
|---|---|---|---|
| 09:00-11:00 | Instagram | Reel | 14-18 second video |
| 09:00-11:00 | YouTube Shorts | Short | Same video file as Reel |
| Anytime | Substack | Note | 2-4 sentences + chart image |

## Sunday

| Time | Platform | Format | Notes |
|---|---|---|---|
| 08:00 | Substack | Weekly Digest | Auto-assembled from 7 daily Notes. 300-400 words. |

---

## Assets Per Story

Each daily story produces:

| Asset | File | Format |
|---|---|---|
| Cover tile | `story{N}_chart0.png` | 1080x1350 PNG (4:5) |
| Chart | `story{N}_chart1.png` | 1080x1350 PNG (4:5) |
| Poster | `story{N}_poster.pdf` | A3 portrait PDF (300 DPI) |
| Reel | `story{N}_reel_with_voice.mp4` | 1080x1920 MP4 (9:16) |
| Reel caption | `story{N}_reel_caption.txt` | Text |
| YouTube description | `story{N}_youtube_description.txt` | Text |
| Substack Note | `story{N}_substack_note.md` | Markdown |

Total per week: 7 charts, 6 videos, 7 PDFs, ~20 text files.

---

## Reel Structure

1. **Cover hold** (2-3 seconds) -- Number visible from frame 0 (Instagram thumbnail). Elements animate in.
2. **Chart animation** (8-12 seconds) -- One chart builds with eased animation and moving value label.
3. **Voiceover** (30-40 words) -- One fact, one implication. Starts with the number.
4. **Background music** -- lo-fi or editorial preset, fades in/out.

Total: 14-18 seconds.

---

## Substack Note Format

2-4 sentences. Lead with the number. Paired with chart image. No teasers.

Ends with: "Subscribe for the full story: espressocharts.substack.com (coffee emoji)"

---

## Weekly Digest (Sunday)

Auto-assembled by the runner from the seven daily Notes. Format:

```markdown
# Espresso Charts -- Week of [Date]

---

**[Story 0 title]** [Mon]
[Note text]

---

**[Story 1 title]** [Tue]
[Note text]

...

---
*Charts and analysis: Espresso Charts*
*espressocharts.substack.com*
```

No manual article writing. The digest IS the seven notes with dividers.

---

## Instagram Grid

The grid shows one Reel per day (Mon-Sat). All thumbnails are number-led cover tiles. The visual variety comes from different accent colors, different numbers, and different chart types in the video.

---

## Story Log

After each week, append to `story_history.md`:

```markdown
| Date | Slug | Lead Number | Source | Chart Type |
|------|------|-------------|--------|------------|
| 2026-04-14 | global_trees_46pct | 46% | FAO 2025 | bar |
```

Inject last 30 entries into the weekly prompt to prevent topic repetition.

---

## Copy Rules

| Do | Don't |
|---|---|
| Lead with the number | Em dashes |
| Short declarative sentences | Exclamation marks |
| Active voice | Emojis in body (coffee emoji in sign-off only) |
| Specific numbers | "Did you know" / "Let's dive in" |
| Name sources by institution | "Interestingly" / "Notably" |

---

## Content Scope

**Espresso Charts:** Civilizational-scale, deep-time, wonder-inducing data. Natural science, demographics, energy, geography, space.

**Macro Ledger (separate brand):** GDP, CPI, NFP, rate decisions, trade balances, labor markets.

If the primary hook is a macro-economic release, it belongs to Macro Ledger.

---

## Metric Priorities

1. **Substack free subscriber growth** -- primary
2. **Instagram saves rate** -- content quality proxy
3. **Substack open rate** -- audience health

Every CTA directs to the free newsletter.
