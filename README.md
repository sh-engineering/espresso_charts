# Espresso Charts

**Thirty seconds of perspective.** Data journalism in chart form, published across Instagram, YouTube Shorts, and Substack.

## System Overview

The production pipeline is config-driven: a Python file containing a JSON config is loaded into a Google Colab notebook that renders all assets (charts, animations, voiceovers, posters, and copy) automatically.

### Files

| File | Purpose |
|---|---|
| `espresso_charts.py` | Core charting library (matplotlib). All chart functions, audio pipeline, poster generator, GitHub uploader, Substack publisher. |
| `espresso_charts_runner.ipynb` | Colab notebook. Loads JSON config, renders all assets for the week. |
| `espresso_charts_prompt_v7.md` | Weekly story generation prompt. Feed to Claude/GPT to produce the config + editorial calendar. |
| `config_YYYY_MM_DD.py` | Weekly config file. Contains all data, chart params, copy, and metadata for 3 stories. |

### Weekly Cadence

Three stories per week (Story 0 = Monday, Story 1 = Wednesday, Story 2 = Friday).

| Day | Instagram | YouTube | Substack |
|---|---|---|---|
| Mon | Reel (Story 0) | Short (Story 0) | Chart Note |
| Tue | Carousel (Story 0) | | Chart Note |
| Wed | Reel (Story 1) | Short (Story 1) | Chart Note |
| Thu | | | Newsletter (Story 1) + Chart Note |
| Fri | Reel (Story 2) | Short (Story 2) | Chart Note |
| Sat | Carousel (Story 2) | | Chart Note |
| Sun | | | Chart Note |

---

## Chart Library (`espresso_charts.py`)

### Static Charts (4:5 Instagram Carousels)

| Function | Type | Use |
|---|---|---|
| `eSingleBarChartNewInstagram` | Horizontal bar | Rankings, comparisons |
| `eMultiLineChartInstagram` | Multi-line | Trends over time |
| `eStemChartNewInstagram` | Lollipop/stem | Magnitude with categorical x-axis |
| `eDonutChartInstagram` | Donut | Part-to-whole (3-5 slices) |
| `eCoverTileInstagram` | Cover tile | Number-led editorial cover |

### Animated Charts (9:16 Reels/Shorts)

| Function | Type | Notes |
|---|---|---|
| `eSingleBarChartAnimateInstagram` | Bar | Bars grow with eased animation |
| `eMultiLineChartAnimateInstagram` | Line | Line draws with moving value label at tip |
| `eStemChartAnimateInstagram` | Stem | Stems grow from zero |
| `eDonutChartAnimateInstagram` | Donut | Wedges sweep open |
| `eCoverTileAnimateInstagram` | Cover | Frame 0 = complete design (thumbnail). Frame 1+ = elements animate in |

### Poster

| Function | Type | Notes |
|---|---|---|
| `eDataPoster` | Print PDF (A3) | Hero number 120pt, insight headline 28pt, hero chart + extra chart images, annotation band |

### Audio Pipeline

| Function | Purpose |
|---|---|
| `eGenerateVoiceover` | ElevenLabs TTS (default: "george" voice, British male) |
| `eGenerateMusic` | ElevenLabs AI music (presets: `lofi_coffee`, `editorial_minimal`, `upbeat_data`) |
| `eAddAudio` | Combine video + voiceover + music with fade controls |
| `eConcatenateMP4` | Join cover animation + chart animation into one reel |

### Helpers

| Function | Purpose |
|---|---|
| `save_chart` | Save with locked dimensions (never `bbox_inches='tight'`) |
| `fetch_fred_series` | Pull data from FRED API |
| `add_hlines` | Horizontal reference lines with `label_ha` support (`right`, `left_inside`, default) |
| `add_vlines` | Vertical reference lines |
| `add_reference_bands` | Shaded bands |
| `add_custom_annotations` | Callout annotations with optional arrows |
| `add_text` / `add_lines` | Manual text and line overlays |

### Publishing

| Class/Function | Purpose |
|---|---|
| `GitHubUploader` | Push assets to GitHub repo |
| `SubstackPublisher` | Create draft/scheduled/published Substack posts |

---

## Color System

All colors must be hex values in configs (the runner does not resolve color name strings inside nested dicts).

```python
color_blue   = '#3F5B83'
color_orange = '#A14516'
color_green  = '#4D5523'
color_sand   = '#CDAF7B'
face_color   = '#F5F0E6'
```

## Font System

Three font families, all from Google Fonts:

| Font | Role | Weight |
|---|---|---|
| Playfair Display | Headlines, hero numbers, cover tiles | 700 italic (hero), 400 italic (insight) |
| Source Serif 4 | Body text, subtitles, context | 300 (light), 400 (regular) |
| DM Mono | Labels, ticks, eyebrows, source lines, masthead | 300 (light), 400 (regular) |

### Installation (required at start of every Colab session)

```python
from espresso_charts import install_espresso_fonts
install_espresso_fonts()
```

This downloads fonts from Google Fonts GitHub (`raw.githubusercontent.com`), deletes matplotlib's font cache, rebuilds the font manager, and registers each font via `addfont()`. Order matters: delete cache, then `_load_fontmanager(try_read_cache=False)`, then `addfont()` last.

---

## Cover Tile Design

The cover tile is a number-led editorial layout with 12 visual layers:

1. **Background** — parchment fill (#F5F0E6)
2. **Top rule** — thin horizontal line
3. **Corner labels** — date (left), "Espresso Charts" (right), DM Mono
4. **Eyebrow** — topic + year, DM Mono, centered
5. **Hero number** — Playfair Display 86pt bold italic
6. **Unit line** — 24pt below the number (e.g. "of the world's trees, cut")
7. **Accent line** — short colored rule, expands from center in animation
8. **Insight sentence** — Playfair italic, the story's one-sentence hook
9. **Context sentence** — Source Serif 4 light italic (optional)
10. **Bottom rule**
11. **Source line** — DM Mono, centered
12. **Corner mark** — small triangle, bottom-right

### Cover Animate Behavior

- **Frame 0:** Complete design visible (Instagram grid thumbnail)
- **Frame 1+:** Accent line expands, unit/insight/context fade in with subtle drift
- **No position overrides needed** — do NOT set `suptitle_y`, `subtitle_y`, or `accent_line_y` in config

### Config Example

```json
{
  "type": "cover_animate",
  "params": {
    "txt_suptitle": "46%",
    "txt_subtitle": "Nearly half of all trees that existed\nwhen humans arrived are gone.",
    "txt_unit": "of the world's trees, cut",
    "txt_eyebrow": "Global Forests \u00b7 FAO 2025",
    "txt_issue": "April 14, 2026",
    "suptitle_size": 86,
    "accent_line_color": "#4D5523",
    "show_corner_mark": true,
    "duration": 3.5,
    "hold_duration": 2.0
  }
}
```

---

## Data Poster (`eDataPoster`)

Print-quality A3 PDF poster. Layout:

- **Masthead** — ESPRESSO CHARTS + No. + topic
- **Hero number** — 120pt Playfair italic in accent color
- **Unit label** — 26pt below number
- **Insight headline** — 28pt Playfair italic, large and readable
- **Accent rule**
- **Hero chart** — line chart with first/last value labels (no Y axis)
- **Extra charts** — 2-3 smaller chart images side-by-side (auto-collected by runner)
- **Annotation band** — 2-3 milestone callouts with colored dots
- **Context** — Source Serif 4, supporting detail
- **Footer** — source lines + tagline + corner mark

### PDF Generation

Matplotlib's PDF backend crashes on variable fonts (`StyleFlags invalid value`). The poster renders to a temp PNG at full DPI, then wraps it in PDF via PIL (`Image.save(format='PDF')`). No extra dependencies needed beyond Pillow.

### Config Example

```json
"poster": {
  "hero_number": "46%",
  "hero_unit": "of the world's trees, cut",
  "hero_eyebrow": "GLOBAL FORESTS, FAO 2025",
  "insight_text": "Nearly half of all trees that existed\nwhen humans arrived are gone.",
  "insight_context": "An estimated 3.04 trillion trees remain.\nBefore human civilization, the number was 5.6 trillion.",
  "chart_x_labels": [[1990, "1990"], [2000, "2000"], [2010, "2010"], [2025, "Now"]],
  "chart_y_format": "{:.1f}T",
  "annotations": [
    {"year": "1990", "value": "3.5T trees", "desc": "Earliest estimate", "color": "#4D5523"}
  ],
  "source_lines": ["SOURCE: FAO Global Forest Assessment 2025", "fao.org"],
  "issue_number": "015",
  "issue_topic": "Global Forests",
  "accent_color": "#4D5523"
}
```

The runner auto-extracts `chart_x`/`chart_y` from the first line chart in the story. If no line chart exists, provide them explicitly. Extra chart images are collected automatically from the story's rendered PNGs.

---

## Runner Pipeline

The runner processes each story in this order:

1. **Cover** (PNG) — `eCoverTileInstagram`
2. **Static charts** (PNG) — bar, line, stem, donut
3. **Copy** (text files) — captions, articles, chart notes
4. **Poster** (PDF) — `eDataPoster` with auto-collected extra charts
5. **Reel** (MP4) — cover_animate + chart_animate + voiceover + music
6. **GitHub push** — all assets uploaded to repo

### Data Pipeline

- `_resolve_secrets()` — replaces `{{SECRET_NAME}}` with Colab userdata secrets
- `make_df()` — tries `data_source` API first, falls back to inline `data`
- `_post_process()` — sort, dropna, tail/head, column selection

### Running

```python
from espresso_charts import *
install_espresso_fonts()

# Load config
exec(open("config_2026_04_14.py").read())

# Run everything
run_config(config)

# Run one story, charts only
run_config(config, story_ids=[0], only='charts')

# Run one specific chart
run_config(config, story_ids=[1], chart_indices=[2])
```

---

## Config Schema

```python
config = json.loads(r'''
{
  "week": {"year": "2026", "month": "04", "week_start": "14"},
  "defaults": {
    "face_color": "#F5F0E6",
    "dpi": 200,
    "suptitle_font": "Playfair Display",
    "subtitle_font": "Source Serif 4",
    "voiceover": {"voice_name": "george", "model": "multilingual_v2", "speed": 0.95},
    "audio_mix": {"vo_delay": 0.5, "music_volume": 0.12}
  },
  "stories": [
    {
      "id": 0,
      "slug": "story_slug",
      "cover": { ... },
      "charts": [ ... ],
      "reel": { ... },
      "poster": { ... },
      "story_files": [ ... ],
      "copy": { ... }
    }
  ]
}
''')
```

---

## Key Production Rules

### Config Rules
- Bar chart data must be sorted ascending (smallest first)
- All text uses `\n` for line breaks
- Colors as hex strings (`"#3F5B83"`) — the runner does not resolve color names in nested dicts
- Dollar signs in matplotlib text: escape as `\\$`
- JSON requires string keys for index-based dicts (`{"0": 4}`)

### Cover Tile Rules
- Do NOT set `suptitle_y`, `subtitle_y`, or `accent_line_y` — defaults handle layout
- `txt_issue` is a date string (e.g. "April 14, 2026"), not an issue number
- `suptitle_size` defaults to 86
- `unit_size` defaults to 24

### Reel Rules
- Every reel starts with `cover_animate`, followed by one chart animation
- `line_animate` must never include `x_ticks` or `x_tick_labels` (causes categorical converter crash)
- `music.duration_ms` must exceed total reel duration
- Voiceover target: 33-50 words

### Writing Rules
- No em dashes anywhere
- No exclamation marks in analytical text
- No emojis except single coffee emoji in sign-offs
- Substack articles: 300-450 words (espresso length)
- Chart notes: 2-4 sentences, real insight, no teasers

### Known Bugs / Workarounds
- ffmpeg `%` in drawtext: use `expansion=none` + `textfile=`
- ffmpeg `[]` in font paths: copy to bracket-free temp paths
- matplotlib PDF + variable fonts: render PNG, wrap in PDF via PIL
- Colab runtime caching: `importlib.reload()` after uploading new `.py` files

---

## Approved Data Sources

| Domain | Sources |
|---|---|
| Macroeconomics | FRED, IMF, OECD, World Bank, Eurostat, BLS, BEA |
| Energy / Climate | IEA, EIA, IRENA, Our World in Data, NOAA |
| Demographics | UN Data, Census Bureau, Pew Research, UNESCO |
| Science / Space | NASA, ESA, NOAA, USGS |
| Trade | WTO, World Bank, UNCTAD, WIPO |

No aggregators, news articles, or Wikipedia as primary sources.
