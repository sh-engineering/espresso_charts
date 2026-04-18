# Espresso Charts

**Thirty seconds of perspective.** Data journalism in chart form. One story per day, one chart per story.

## System Overview

Daily single-chart stories published across Instagram Reels, YouTube Shorts, and Substack. The production pipeline is config-driven: a JSON config loaded into a Google Colab notebook renders all assets automatically.

### Files

| File | Purpose |
|---|---|
| `espresso_charts.py` | Core charting library (matplotlib). Charts, animations, poster, audio, publishing. |
| `espresso_charts_runner.ipynb` | Colab notebook. JSON config in, all assets out. |
| `espresso_charts_prompt_v8.md` | Weekly prompt. Feed to Claude to produce 7 daily stories. |
| `config_YYYY_MM_DD.py` | Weekly config. 7 stories with data, chart params, copy. |
| `cadence.md` | Publishing schedule and workflow. |
| `story_history.md` | Story log for topic repetition avoidance. |

### Daily Model

One story per day (Mon-Sat). Each story = one number + one chart + one Reel + one Note + one poster. Sunday = auto-assembled weekly digest. No multi-chart carousels or long-form articles in the daily cadence.

---

## Chart Library (`espresso_charts.py`)

### Static Charts (4:5 Instagram)

| Function | Type |
|---|---|
| `eSingleBarChartNewInstagram` | Horizontal bar (rankings, comparisons) |
| `eMultiLineChartInstagram` | Multi-line (trends over time) |
| `eStemChartNewInstagram` | Lollipop/stem (magnitude, categorical x) |
| `eDonutChartInstagram` | Donut (part-to-whole, 3-5 slices) |
| `eCoverTileInstagram` | Number-led editorial cover |

### Animated Charts (9:16 Reels)

| Function | Notes |
|---|---|
| `eSingleBarChartAnimateInstagram` | Bars grow with easing |
| `eMultiLineChartAnimateInstagram` | Line draws with moving value label at tip |
| `eStemChartAnimateInstagram` | Stems grow from zero |
| `eDonutChartAnimateInstagram` | Wedges sweep open |
| `eCoverTileAnimateInstagram` | Frame 0 = complete (thumbnail). Frame 1+ = elements animate in |

### Poster

| Function | Notes |
|---|---|
| `eDataPoster` | A3 PDF. Hero 120pt, insight headline 28pt, hero chart + extra charts, annotations. |

### Audio

| Function | Purpose |
|---|---|
| `eGenerateVoiceover` | ElevenLabs TTS ("george" voice) |
| `eGenerateMusic` | ElevenLabs AI music (presets: `lofi_coffee`, `editorial_minimal`, `upbeat_data`) |
| `eAddAudio` | Combine video + voiceover + music |
| `eConcatenateMP4` | Join cover + chart clips |

### Helpers

| Function | Purpose |
|---|---|
| `add_hlines` | Horizontal lines with `label_ha` support (`right`, `left_inside`, default) |
| `add_vlines` | Vertical lines |
| `add_reference_bands` | Shaded bands |
| `add_custom_annotations` | Callout annotations |
| `GitHubUploader` | Push assets to GitHub |
| `SubstackPublisher` | Substack API integration |

---

## Color System

```python
color_blue   = '#3F5B83'
color_orange = '#A14516'
color_green  = '#4D5523'
color_sand   = '#CDAF7B'
face_color   = '#F5F0E6'
```

All config values must be hex codes. The runner does not resolve color name strings.

## Font System

| Font | Role |
|---|---|
| Playfair Display | Headlines, hero numbers, cover tiles (700 italic) |
| Source Serif 4 | Body text, subtitles (300-400) |
| DM Mono | Labels, ticks, masthead (300-400) |

Install at start of every Colab session:

```python
from espresso_charts import install_espresso_fonts
install_espresso_fonts()
```

---

## Cover Tile

Number-led editorial layout (B template). 12 visual layers: background, top rule, date + brand corners, eyebrow, hero number (86pt), unit (24pt), accent line, insight sentence, context, bottom rule, source, corner mark.

**Cover animate:** Frame 0 = complete design (Instagram thumbnail). Frame 1+ = accent line expands, unit/insight fade in. Do NOT set position overrides (`suptitle_y`, `subtitle_y`, `accent_line_y`).

---

## Data Poster

A3 PDF at 300 DPI. Layout: hero number 120pt, insight headline 28pt, hero chart with first/last value labels (no Y axis), extra chart images side-by-side, annotation band, context, footer. PDF rendered via PIL (no reportlab needed).

---

## Data Sources

**Tier 1 (daily story ideas):** Our World in Data, Gapminder, NASA, NOAA, UN Data, World Bank

**Tier 2 (domain-specific):** USGS, IUCN, Global Carbon Project, FAO, IRENA, Copernicus, Met Office Hadley Centre

**Tier 3 (carousel deep-dives only):** FRED, IMF, OECD, Eurostat, BLS, BEA, IEA

**OWID Rule:** Discover and download via Our World in Data, cite the underlying primary source.

**Macro exclusion:** GDP, CPI, NFP, rate decisions belong to Macro Ledger, not Espresso Charts.

---

## Story Log

`story_history.md` at repo root. Append after each week:

```markdown
| Date | Slug | Lead Number | Source | Chart Type |
|------|------|-------------|--------|------------|
| 2026-04-14 | global_trees_46pct | 46% | FAO 2025 | bar |
```

Inject last 30 entries into weekly prompts to avoid repetition.

---

## Production Rules

### Daily Story Rules
- 1 chart per story, 1 number per chart
- Headline IS the number, not the topic
- Voiceover: 30-40 words maximum
- Reel: 14-18 seconds total (cover 2-3s, chart 8-12s)
- No `substack_article` for daily stories
- `substack_note`: 2-4 sentences, lead with the number

### Config Rules
- Bar chart data sorted ascending
- All text uses `\n`, all colors as hex
- Dollar signs: `\\$`
- JSON string keys for index dicts (`{"0": 4}`)
- Cover: do NOT override position params

### Known Bugs
- ffmpeg `%` in drawtext: `expansion=none` + `textfile=`
- ffmpeg `[]` in font paths: temp symlinks
- matplotlib PDF + variable fonts: render PNG, wrap via PIL
- Colab caching: `importlib.reload()` after uploading new `.py`
