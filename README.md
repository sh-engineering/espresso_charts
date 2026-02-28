# Espresso Charts — Stories

Data stories that turn trending topics into visual insights within 24 hours.

Published on [Instagram](https://instagram.com/espressocharts) and [Substack](https://espressocharts.substack.com).

| Day | Instagram (CET) | Substack |
|-----|-----------------|----------|
| **Mon** | Reel 11:00 · Poll | Stat Teaser |
| **Tue** | Carousel 11:00 | Cross-Post |
| **Wed** | Reel 11:00 · Poll | Source Spotlight · Evergreen |
| **Thu** | Process Story | Newsletter 07:00 · Stat Teaser |
| **Fri** | Reel 11:00 · Poll | Cross-Post |
| **Sat** | Carousel 13:00 | Source Spotlight |
| **Sun** | — | Source Spotlight |

### Story Publishing Map

Each week has 3 stories. Every story appears twice on Instagram (Reel → Carousel) and once on Substack (Newsletter for Story 2 only).

| Story | Reel | Carousel | Newsletter |
|-------|------|----------|------------|
| **Story 1** | Mon 11:00 | Tue 11:00 | — |
| **Story 2** | Wed 11:00 | — | Thu 07:00 |
| **Story 3** | Fri 11:00 | Sat 13:00 | — |

---

## Repository Structure

```
espresso_charts_stories/
├── README.md
├── 2026/
│   └── 02/
│       ├── 23_ai_energy/
│       │   ├── assets/
│       │   │   ├── cover.png
│       │   │   ├── chart1_grid_mix.png
│       │   │   ├── chart2_demand.png
│       │   │   └── reel_demand.mp4
│       │   └── weekly_pack.md
│       ├── 25_world_cup_economics/
│       │   ├── assets/
│       │   │   ├── cover.png
│       │   │   ├── chart1_cities.png
│       │   │   ├── chart2_spending.png
│       │   │   └── reel_cities.mp4
│       │   └── ...
│       └── 27_nvidia_revenue/
│           └── ...
```

Each story lives in a folder named `DD_topic_slug/` under its publication month. The `weekly_pack.md` file in the first story folder of each week contains the full editorial calendar for that week.

### Naming Conventions

- **Folders:** `DD_snake_case_slug/` where DD is the day the Reel publishes
- **Covers:** `assets/cover.png`
- **Charts:** `assets/chart1_descriptor.png`, `assets/chart2_descriptor.png`
- **Reels:** `assets/reel_descriptor.mp4`
- **Audio:** `assets/reel_with_voice.mp4` (final mixed version)

---

## Weekly Posting Schedule

All times CET (Berlin). Three stories per week, each appearing as a Reel first, then a Carousel or Newsletter.

### Monday

| Time | Platform | Format | Content |
|------|----------|--------|---------|
| 11:00 | Instagram | Reel | Story 1 animated chart + voiceover |
| Afternoon | Instagram | Story (Poll) | Binary question from Story 1 data |
| Anytime | Substack | Note (Single Stat Teaser) | Story 2 teaser stat + "Full story dropping tomorrow" |

### Tuesday

| Time | Platform | Format | Content |
|------|----------|--------|---------|
| 11:00 | Instagram | Carousel | Story 1 cover + 2 charts |
| Anytime | Substack | Note (Cross-Post) | Story 1 reframed for Substack audience |

### Wednesday

| Time | Platform | Format | Content |
|------|----------|--------|---------|
| 11:00 | Instagram | Reel | Story 2 animated chart + voiceover |
| Afternoon | Instagram | Story (Poll) | Binary question from Story 2 data |
| Anytime | Substack | Note (Source Spotlight) | Dataset highlight from Story 1 research |
| Anytime | Substack | Note (Evergreen) | Standalone fact from the week's research |

### Thursday

| Time | Platform | Format | Content |
|------|----------|--------|---------|
| 07:00 | Substack | Newsletter | Story 2 full article with 2 charts |
| Anytime | Instagram | Story (Process Screenshot) | Behind-the-scenes Colab notebook screenshot |
| Anytime | Substack | Note (Single Stat Teaser) | Story 3 teaser stat + "Full story dropping tomorrow" |

### Friday

| Time | Platform | Format | Content |
|------|----------|--------|---------|
| 11:00 | Instagram | Reel | Story 3 animated chart + voiceover |
| Afternoon | Instagram | Story (Poll) | Binary question from Story 3 data |
| Anytime | Substack | Note (Cross-Post) | Story 2 reframed for Substack audience |

### Saturday

| Time | Platform | Format | Content |
|------|----------|--------|---------|
| 13:00 | Instagram | Carousel | Story 3 cover + 2 charts |
| Anytime | Substack | Note (Source Spotlight) | Dataset highlight from Story 2 or 3 research |

### Sunday

| Time | Platform | Format | Content |
|------|----------|--------|---------|
| Anytime | Substack | Note (Source Spotlight) | Dataset highlight from Story 3 research |

---

## Weekly Totals

| Platform | Format | Count |
|----------|--------|-------|
| Instagram | Reels | 3 |
| Instagram | Carousels | 3 |
| Instagram | Stories (Polls) | 3 |
| Instagram | Stories (Process) | 1 |
| Substack | Newsletter | 1 |
| Substack | Notes (Single Stat Teaser) | 2 |
| Substack | Notes (Cross-Post) | 2 |
| Substack | Notes (Source Spotlight) | 3 |
| Substack | Notes (Evergreen) | 1 |
| **Total** | | **19 pieces/week** |

---

## End-to-End Pipeline

### Overview

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

---

### Step 1: Generate Content (Claude)

Open Claude and paste the full `espresso_charts_prompt_v3.md` prompt. Claude will search for trending topics and return two outputs:

**Output A — JSON config block:**
```python
config = json.loads(r'''
{ "week": {...}, "defaults": {...}, "stories": [...] }
''')
```

**Output B — `weekly_pack.md`:**
The full editorial calendar with every caption, voiceover script, Note, and Story for Mon–Sun.

**What to save:**
1. Copy the JSON config block (including the `config = json.loads(...)` wrapper)
2. Copy the full `weekly_pack.md` content

---

### Step 2: Set Up the Week's Folder (GitHub)

Create the week's story folders in the repo:

```
espresso_charts_stories/
└── YYYY/
    └── MM/
        ├── DD_story1_slug/
        │   └── assets/
        ├── DD_story2_slug/
        │   └── assets/
        └── DD_story3_slug/
            └── assets/
```

Use the `slug` values from the JSON config. DD = the day the Reel publishes (Mon, Wed, Fri).

Save `weekly_pack.md` in the first story folder of the week.

---

### Step 3: Run the Notebook (Google Colab)

Open the Espresso Charts Colab notebook (`Espresso_Charts.ipynb`). It contains all chart function definitions, helper functions, color variables, and the runner.

**Cell 1 — Paste the config:**

Paste the full `config = json.loads(r''' ... ''')` block from Step 1 into a new cell. Run it.

The config now holds all story data, chart params, reel specs, voiceover scripts, and copy as a Python dict.

**Cell 2 — Run the pipeline:**

The notebook's runner reads `config["stories"]` and for each story executes five phases:

| Phase | What it does | Output |
|-------|-------------|--------|
| **Cover** | Calls `eCoverTileInstagram()` with cover params | `assets/cover.png` |
| **Charts** | Loops through `charts[]`, calls the matching chart function with `data` + `params` | `assets/chart1_*.png`, `assets/chart2_*.png` |
| **Reels** | Calls animated chart functions from `reel.animated_charts[]` | `assets/reel_*.mp4` |
| **Audio** | Sends `reel.voiceover.text` to ElevenLabs API, generates background music, mixes them using `reel.music` and `defaults.audio_mix` settings | `assets/reel_with_voice.mp4` |
| **Copy** | (Optional) Sends `copy.substack_article` to Substack API for draft publishing | Substack draft |

**How the config connects to the Python functions:**

The runner maps JSON `type` values to function calls:

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

The runner converts snake_case JSON param names to the function's actual parameter names, creates a DataFrame from the `data` object, and passes `params` as keyword arguments.

**Color resolution:**

The config stores colors as strings (`"color_blue"`). The runner resolves these to hex values using the notebook's color variables before passing to chart functions.

---

### Step 4: Review and Adjust

After running, check the generated assets in Colab:

- **Covers:** Headline readable, accent line visible, text well-positioned
- **Charts:** Data labels not overlapping, source attribution present, bars sorted correctly
- **Reels:** Headings inside the safe zone (not hidden by Instagram UI), animation smooth
- **Audio:** Voiceover synced with animation, music fades in/out correctly

If anything needs adjustment, edit the relevant params in the config cell and re-run that story.

---

### Step 5: Push to GitHub

Download the generated assets from Colab and place them in the story folders:

```
YYYY/MM/DD_slug/
└── assets/
    ├── cover.png
    ├── chart1_descriptor.png
    ├── chart2_descriptor.png
    ├── reel_descriptor.mp4
    └── reel_with_voice.mp4
```

Commit and push.

---

### Step 6: Schedule and Publish

Use `weekly_pack.md` as the publishing checklist. For each day:

**Instagram (via Meta Business Suite or manually):**
- Upload the assets listed in the weekly pack entry
- Paste the caption directly from the weekly pack
- Schedule at the listed CET time

**Substack Newsletter (Thursday):**
- Create a new post in Substack
- Paste headline, subtitle, and body from the weekly pack
- Insert chart images at the marked positions
- Add source links and tags
- Schedule for 07:00 CET

**Substack Notes (daily):**
- Paste Note text directly from the weekly pack
- Publish at any time on the listed day

**Instagram Stories (daily):**
- For Polls: create using the question/option text from the weekly pack
- For Process Screenshots: screenshot Colab as described, add text overlay
- Post in the afternoon or anytime as listed

---

### API Keys Required

| Service | Key needed for | Where to set |
|---------|---------------|-------------|
| ElevenLabs | Voiceover generation + background music | Colab notebook env variable |
| FRED | Economic data pulls (if using `fetch_fred_series()`) | Colab notebook env variable |
| Substack | Automated draft publishing (optional) | Colab notebook env variable |

---

### Quick Reference: One-Line Pipeline

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
| Chart dimensions | 1080 x 1350 px @ 200 dpi |
| Reel format | 1080 x 1350 px (9:16 crop in app) |
| Reel safe zone | Middle ~50% of frame (top/bottom obscured by IG UI) |
| Reel cover `suptitle_y` | 0.65 or lower (keeps headline visible) |
