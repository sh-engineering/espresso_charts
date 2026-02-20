# Espresso Charts

Chart library for Instagram carousels (4:5) and Reels (9:16). Coffee-themed data journalism visuals built on matplotlib.

## Repo Structure

```
espresso-charts/
├── espresso_charts.py          ← The library (import this)
├── README.md
├── .gitignore
└── stories/                    ← One notebook per story
    ├── 2025_02_21_clean_energy.ipynb
    ├── 2025_02_18_nvidia.ipynb
    └── ...
```

Keep it flat. One library file, one folder for story notebooks. No packages, no `setup.py`, no complexity.

## Setup in Colab

```python
# Cell 1: Install & import
!wget -q https://raw.githubusercontent.com/<your-username>/espresso-charts/main/espresso_charts.py

from espresso_charts import *

# Optional: set FRED API key
import os
os.environ["FRED_API_KEY"] = "your_key_here"
```

Then write your story cells using the functions directly.

## Functions

### Static Charts (Instagram 4:5)
| Function | Use |
|---|---|
| `eSingleBarChartNewInstagram()` | Horizontal bar chart |
| `eMultiLineChartInstagram()` | Multi-line time series |
| `eStemChartNewInstagram()` | Lollipop / stem chart |
| `eDonutChartInstagram()` | Donut (single or double ring) |
| `eCoverTileInstagram()` | Text-only cover slide |

### Animated Charts (Reels 9:16)
| Function | Use |
|---|---|
| `eSingleBarChartAnimateInstagram()` | Bars grow + typewriter titles |
| `eMultiLineChartAnimateInstagram()` | Lines draw + typewriter titles |
| `eStemChartAnimateInstagram()` | Stems grow + typewriter titles |
| `eDonutChartAnimateInstagram()` | Wedges sweep + typewriter titles |
| `eCoverTileAnimateInstagram()` | Animated cover tile |
| `eConcatenateMP4()` | Join clips into one reel |

### Helpers
| Function | Use |
|---|---|
| `save_chart()` | Save with locked dimensions (no `bbox_inches='tight'`) |
| `fetch_fred_series()` | Pull data from FRED API |
| `add_custom_annotations()` | Add framed text annotations |
| `add_lines()` | Add arrows / pointing lines |
| `add_text()` | Add free text elements |

## Title Hierarchy

Every chart function uses the same naming convention:

| Level | Parameter | Default Font | Default Size |
|---|---|---|---|
| **Main Headline** | `txt_suptitle` | `suptitle_font='DejaVu Serif'` | 26pt (charts) / 42pt (covers) |
| **Context Line** | `txt_subtitle` | `subtitle_font='DejaVu Sans'` | 14pt (charts) / 18pt (covers) |
| **Source** | `txt_label` | DejaVu Sans | 10pt |

## Brand Colors

```python
color_blue   = '#3F5B83'
color_orange = '#DD6B20'
color_green  = '#4D5523'
color_sand   = '#CDAF7B'
face_color   = '#F5F0E6'
```
