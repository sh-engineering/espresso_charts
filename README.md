# Espresso Charts — Stories

Data stories that turn trending topics into visual insights within 24 hours.

Published on [Instagram](https://instagram.com/espressocharts), [YouTube](https://youtube.com/@espressocharts), and [Substack](https://espressocharts.substack.com).

**Goal:** Grow Substack free subscribers. Every post on Instagram and YouTube is top-of-funnel. Every caption ends with a prompt to subscribe at espressocharts.substack.com.

---

## Weekly Schedule at a Glance

All times CET (Berlin).

| Day | Instagram | YouTube Shorts | Substack |
|-----|-----------|----------------|----------|
| **Mon** | Reel 09–11 | Short 09–11 | Story 0 — Chart Note |
| **Tue** | Story 0 Carousel 09–11 | — | Story 0 — Chart Note |
| **Wed** | Reel 09–11 | Short 09–11 | Story 1 — Chart Note |
| **Thu** | — | — | Story 1 Newsletter 06–08 · Story 1 — Chart Note |
| **Fri** | Reel 09–11 | Short 09–11 | Story 2 — Chart Note |
| **Sat** | Story 2 Carousel 12–14 | — | Story 2 — Chart Note |
| **Sun** | — | — | Story 2 — Chart Note |

### Story Publishing Map

| Story | Reel + Short | Carousel | Newsletter |
|-------|-------------|----------|------------|
| **Story 0** | Mon 09–11 | Tue 09–11 | — |
| **Story 1** | Wed 09–11 | — | Thu 06–08 |
| **Story 2** | Fri 09–11 | Sat 12–14 | — |

---

## What Each Format Is

| Format | What it is |
|--------|------------|
| **Reel** | 15–25 second animated chart video with voiceover and music. The hook that drives people to the carousel or newsletter. |
| **YouTube Short** | Same video as the Reel, uploaded to YouTube with an adapted title and description. |
| **Carousel** | 3–5 static chart slides posted as a swipeable Instagram post. Starts directly on the first chart — no cover slide. Each slide adds a distinct layer: overall trend, breakdown by category, historical context, geographic comparison, share of total. |
| **Newsletter** | Full Substack article, 600–900 words, 2–5 charts. The deepest version of the story. |
| **Chart Note** | 2–4 sentences delivering one real data insight from the story, with one chart image attached. No teasers. Every Note must stand alone as something worth reading. |

---

## Posting Time Guidance

Exact minutes do not matter. What matters is landing in the right window when the audience is active.

| Platform | Best windows (CET) | Notes |
|----------|-------------------|-------|
| **Instagram Reels** | 08:00–11:00 · 18:00–20:00 | Morning window preferred. Avoid posting mid-afternoon (12:00–17:00). |
| **Instagram Carousels** | 08:00–11:00 · 19:00–21:00 | Saves rate is highest in the evening window. Morning is reliable either way. |
| **YouTube Shorts** | Same window as the Reel | Upload within 30 minutes of the Instagram Reel. |
| **Substack Newsletter** | 06:00–08:00 | Early morning catches readers before work. Thursday is the strongest newsletter day. |
| **Substack Chart Notes** | Any time | Notes surface in a feed, not an inbox. Publish when ready. |

---

## Weekly Totals

| Platform | Format | Count |
|----------|--------|-------|
| Instagram | Reels | 3 |
| Instagram | Carousels | 2 |
| YouTube Shorts | Shorts | 3 |
| Substack | Newsletter | 1 |
| Substack | Chart Notes | 7 |
| **Total** | | **16 pieces/week** |

---

## Repository Structure

```
espresso_charts_stories/
├── README.md
├── weekly_packs/
│   └── 2026_02_23.md
└── assets/
    └── 2026/
        └── 02/
            ├── 23/             ← Story 0 (Monday Reel date)
            │   ├── story_0_cover.png
            │   ├── story_0_chart_1.png
            │   ├── story_0_chart_2.png
            │   ├── story_0_chart_3.png
            │   ├── story_0_chart_4.png
            │   ├── story_0_reel.mp4
            │   └── story_0_reel_with_voice.mp4
            ├── 25/             ← Story 1 (Wednesday Reel date)
            │   └── ...
            └── 27/             ← Story 2 (Friday Reel date)
                └── ...
```

Each story's assets live in `assets/YYYY/MM/DD/` where DD is the Reel publish date. Weekly packs live in `weekly_packs/` named by the Monday of that week.

### File Naming

Files are prefixed with the story's series ID (`story_0`, `story_1`, `story_2`) so any file can be identified at a glance regardless of which folder it sits in. The ID resets each week — Story 0 is always Monday, Story 1 is always Wednesday, Story 2 is always Friday.

| File | Name |
|------|------|
| Cover tile | `story_N_cover.png` |
| Charts | `story_N_chart_1.png`, `story_N_chart_2.png`, etc. (numbered in carousel order) |
| Reel (no audio) | `story_N_reel.mp4` |
| Reel (with voiceover + music) | `story_N_reel_with_voice.mp4` |
| Weekly editorial calendar | `weekly_packs/YYYY_MM_DD.md` |

Charts are numbered in the order they appear in the carousel. The cover tile is generated for the reel thumbnail and Substack header but does not appear as a carousel slide.

---

## End-to-End Pipeline

```
Claude Prompt → JSON config + weekly_pack.md
                    ↓
         Google Colab Notebook
                    ↓
    covers, charts, reels, audio (assets/)
                    ↓
              GitHub repo
                    ↓
    Schedule via weekly_pack.md calendar
```

### Step 1: Generate Content (Claude)

Paste the full `espresso_charts_prompt_v3.md` prompt into Claude. It will search for trending topics and return two outputs:

**Output A — JSON config block:**
```python
config = json.loads(r'''
{ "week": {...}, "defaults": {...}, "stories": [...] }
''')
```

**Output B — `weekly_pack.md`:**
The full editorial calendar with every caption, voiceover script, Chart Note, and newsletter for Mon–Sun.

Save both outputs before closing the session.

---

### Step 2: Set Up the Week's Folders (GitHub)

Create a folder for each story under `assets/YYYY/MM/`:

```
assets/2026/03/
├── 02/   ← Story 0 (Monday Reel date)
├── 04/   ← Story 1 (Wednesday Reel date)
└── 06/   ← Story 2 (Friday Reel date)
```

Save the editorial calendar as `weekly_packs/2026_03_02.md`.

---

### Step 3: Run the Notebook (Google Colab)

Open `Espresso_Charts.ipynb`. Paste the config block into a new cell and run it. Then run the pipeline cell.

The runner reads `config["stories"]` and executes five phases per story:

| Phase | What it does | Output |
|-------|-------------|--------|
| **Cover** | Generates the story title card | `story_N_cover.png` |
| **Charts** | Generates each chart in order | `story_N_chart_1.png`, `story_N_chart_2.png`, etc. |
| **Reel** | Renders the animated chart video | `story_N_reel.mp4` |
| **Audio** | Generates voiceover via ElevenLabs, adds music, mixes | `story_N_reel_with_voice.mp4` |
| **Copy** | (Optional) Sends the newsletter draft to Substack API | Substack draft |

**Config type → Python function mapping:**

| Config `type` | Python function |
|---------------|----------------|
| `"bar"` | `eSingleBarChartNewInstagram()` |
| `"line"` | `eMultiLineChartInstagram()` |
| `"stem"` | `eStemChartNewInstagram()` |
| `"donut"` | `eDonutChartInstagram()` |
| `"cover_animate"` | `eCoverTileInstagram(animate=True)` |
| `"bar_animate"` | `eSingleBarChartAnimate()` |
| `"line_animate"` | `eMultiLineChartInstagram(animate=True)` |
| `"stem_animate"` | `eStemChartNewInstagram(animate=True)` |

Colors are stored in the config as strings (`"color_blue"`). The runner resolves them to hex before passing to chart functions.

---

### Step 4: Review Assets

Check each generated file before publishing:

- **story_N_cover.png** — Headline readable, accent line visible, text well-positioned
- **story_N_chart_N.png** — Labels not overlapping, source credit present, bars sorted correctly
- **story_N_reel.mp4** — Cover title card present, chart animation present, headings inside the safe zone
- **story_N_reel_with_voice.mp4** — Voiceover synced with animation, music fades correctly, total duration at least 3 seconds longer than voiceover

Adjust params in the config cell and re-run any story that needs a fix.

---

### Step 5: Push to GitHub

Download from Colab and place in the story folder:

```
assets/2026/03/02/
├── story_0_cover.png
├── story_0_chart_1.png
├── story_0_chart_2.png
├── story_0_chart_3.png
├── story_0_chart_4.png
├── story_0_reel.mp4
└── story_0_reel_with_voice.mp4
```

Commit and push.

---

### Step 6: Schedule and Publish

Use `weekly_pack.md` as the publishing checklist.

**Instagram Reels and Carousels (via Meta Business Suite):**
- Upload assets listed in the weekly pack entry
- Paste caption from the weekly pack
- Schedule within the posting window for that day

**YouTube Shorts:**
- Upload `story_N_reel_with_voice.mp4`
- Paste the title and description from the weekly pack's `youtube_shorts` block
- Publish or schedule within 30 minutes of the Instagram Reel

**Substack Newsletter (Thursday):**
- Create a new post in Substack
- Paste headline, subtitle, and body from the weekly pack
- Insert chart images at the marked positions
- Add source links and tags
- Schedule within the 06:00–08:00 window

**Substack Chart Notes (daily):**
- Paste Note text from the weekly pack
- Attach the chart image listed in the Note's `Image:` line
- Publish when ready

---

### API Keys Required

| Service | Key needed for | Where to set |
|---------|---------------|-------------|
| ElevenLabs | Voiceover + background music | Colab env variable |
| FRED | Economic data pulls | Colab env variable |
| Substack | Automated draft publishing (optional) | Colab env variable |

---

### Quick Reference

```
Prompt Claude → paste config into Colab → run all → download assets → push to GitHub → schedule per weekly_pack.md
```

---

## Brand Reference

| Element | Value |
|---------|-------|
| Background | `#F5F0E6` (Latte Cream) |
| Primary accent | `#3F5B83` (Blue) |
| Secondary accent | `#A14516` (Orange) |
| Tertiary | `#4D5523` (Green) |
| Neutral | `#CDAF7B` (Sand) |
| Title font | DejaVu Serif |
| Body font | DejaVu Sans |
| Chart dimensions | 1080 × 1350 px @ 200 dpi |
| Reel / Short format | 1080 × 1350 px (9:16 crop in app) |
| Reel safe zone | Middle ~50% of frame (top/bottom obscured by platform UI) |
| Reel cover `suptitle_y` | 0.65 or lower |
| Charts per carousel | 3–5 |
| Charts per newsletter | 2–5 |
| Newsletter length | 600–900 words |
