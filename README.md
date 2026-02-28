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

## Content Pipeline

```
1. Identify 3 trending topics (Tier 1 preferred: macro, climate, demographics, science)
2. Source authoritative data (FRED, IEA, World Bank, Eurostat, etc.)
3. Generate weekly config JSON + weekly_pack.md via Claude prompt
4. Load config into Colab notebook → generates all charts, covers, reels, audio
5. Push assets to this repo
6. Schedule posts per weekly_pack.md calendar
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
