# Espresso Charts — Parameter Reference

Complete reference for every parameter used in the JSON config. Covers chart types, cover tiles, reel elements, voiceover, music, and copy.

---

## How This Document Works

The JSON config uses **snake_case** parameter names. The Colab runner maps these to the Python function's actual parameter names (often camelCase). This document lists the **JSON config name** for each parameter, explains what it does, gives its default value, and shows an example.

All text parameters support `\n` for line breaks. Never use triple-quoted Python strings or actual newlines in JSON values.

---

## Table of Contents

1. [Week Metadata](#week-metadata)
2. [Defaults](#defaults)
3. [Cover Tile](#cover-tile)
4. [Bar Chart](#bar-chart)
5. [Line Chart](#line-chart)
6. [Stem Chart](#stem-chart)
7. [Donut Chart](#donut-chart)
8. [Animated Charts (Reel)](#animated-charts-reel)
9. [Voiceover](#voiceover)
10. [Music](#music)
11. [Story Files](#story-files)
12. [Copy](#copy)
13. [Color Palette](#color-palette)
14. [Typography](#typography)

---

## Week Metadata

Top-level object identifying the content week.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `year` | string | Four-digit year | `"2026"` |
| `month` | string | Two-digit month | `"02"` |
| `week_start` | string | Day of the month the week starts (Monday) | `"23"` |

```json
"week": { "year": "2026", "month": "02", "week_start": "23" }
```

---

## Defaults

Global settings applied to all stories unless overridden at the story level.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `face_color` | string | `"#F5F0E6"` | Background color for all charts and covers (Latte Cream) |
| `dpi` | int | `200` | Dots per inch. Combined with px dimensions this controls file resolution |
| `px_width` | int | `1080` | Canvas width in pixels |
| `px_height` | int | `1350` | Canvas height in pixels (4:5 ratio for Instagram) |
| `suptitle_font` | string | `"DejaVu Serif"` | Default headline font |
| `subtitle_font` | string | `"DejaVu Sans"` | Default body/subtitle font |

### Defaults — Voiceover

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `voiceover.voice_name` | string | `"bella"` | ElevenLabs voice ID |
| `voiceover.model` | string | `"multilingual_v2"` | ElevenLabs model |
| `voiceover.stability` | float | `0.5` | Voice stability (0–1). Lower = more expressive |
| `voiceover.speed` | float | `0.95` | Playback speed. 0.95 is slightly slower than natural for clarity |

### Defaults — Audio Mix

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_mix.vo_delay` | float | `0.5` | Seconds of silence before voiceover starts |
| `audio_mix.vo_volume` | float | `1.0` | Voiceover volume multiplier |
| `audio_mix.music_volume` | float | `0.12` | Background music volume (0–1). Keep low so voice is clear |
| `audio_mix.music_fade_in` | float | `0.5` | Seconds for music to fade in at start |
| `audio_mix.music_fade_out` | float | `2.0` | Seconds for music to fade out at end |

---

## Cover Tile

The story's title card. No data, just typography and an accent line.

**Python function:** `eCoverTileInstagram()`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `txt_suptitle` | string | — | Main headline. Large serif text. Use `\n` for line breaks. Keep to 3–6 words |
| `txt_subtitle` | string | — | Subheadline. Smaller sans-serif text below the accent line. 1–2 sentences |
| `suptitle_size` | int | `42` | Font size for the headline |
| `subtitle_size` | int | `18` | Font size for the subheadline |
| `suptitle_y` | float | `0.6` | Vertical position of the headline (0 = bottom, 1 = top). For reel covers use `0.65` or lower |
| `subtitle_y` | float | `0.38` | Vertical position of the subheadline |
| `accent_line_color` | string | `"color_blue"` | Color of the decorative line between headline and subheadline. Use a color variable string |
| `show_accent_line` | bool | `true` | Whether to draw the accent line |
| `accent_line_y` | float | `0.48` | Vertical position of the accent line |
| `accent_line_width` | int | `4` | Thickness of the accent line in points |
| `accent_line_length` | float | `0.15` | Length of the accent line as fraction of canvas width |

**Example:**
```json
"cover": {
  "txt_suptitle": "Big Tech Is\nBuying the Grid",
  "txt_subtitle": "Microsoft just matched 100% of its\nelectricity with renewables.",
  "suptitle_size": 42,
  "subtitle_size": 18,
  "accent_line_color": "color_green"
}
```

---

## Bar Chart

Horizontal bar chart. Best for rankings, comparisons, and part-to-whole when order matters.

**Python function:** `eSingleBarChartNewInstagram()`

**Config `type`:** `"bar"`

### Data Object

| Parameter | Type | Description |
|-----------|------|-------------|
| `data.DimColumn` | array | Category labels for each bar (y-axis). Displayed as text on the left side of bars |
| `data.MeasureColumn` | array | Numeric values for each bar (x-axis). Determines bar length |

Data should be sorted ascending (smallest at top, largest at bottom) unless there is a logical ordering like chronology.

### Params

**Data mapping:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `col_dim` | string | Name of the dimension column in the data object |
| `col_measure` | string | Name of the measure column in the data object |

**Text hierarchy (note: reversed naming in bar charts):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `txt_suptitle` | string | — | **Main heading** (TOP, large, serif). Despite the name, this is rendered as `fig.suptitle()` at the top of the chart. This is the primary headline |
| `txt_subtitle` | string | — | **Contextual subtitle** (below heading, smaller, sans-serif). Despite the name, this is rendered via `ax.set_title()`. Explains or qualifies the headline |
| `txt_label` | string | — | **Source attribution** (bottom of chart, smallest). Include source name, URL, and `© Espresso Charts` on separate `\n` lines |

> **Why the names seem reversed:** In the bar chart Instagram function, `txt_suptitle` maps to `fig.suptitle()` (visually the main headline), and `txt_subtitle` maps to `ax.set_title()` (visually the subtitle). This is the opposite of the line/stem/donut functions. The prompt handles the mapping, but be aware of this when reading the code.

**Number formatting:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_format` | string | `"{:.0f}"` | Python format string for bar value labels. Examples: `"{:.1f} GW"`, `"${:,.0f}M"`, `"{:.0f}%"`, `"+{:.0f}%"` |

**Bar styling:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bar_color` | string | `"color_blue"` | Color of all bars. Use a color variable string |
| `bar_height` | float | `0.75` | Height of each bar (0–1). Controls spacing between bars |
| `hide_left_spine` | bool | `false` | Remove the left axis line |

**Font sizes:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suptitle_size` | int | `26` | Font size for the main heading |
| `subtitle_size` | int | `14` | Font size for the contextual subtitle |
| `label_size` | int | `10` | Font size for the source attribution |

**Positioning:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suptitle_y_custom` | float | `0.99` | Vertical position of the main heading (0–1). Lower values push it down. For reel animations use `0.93` |
| `subtitle_pad_custom` | float | `39` | Padding between subtitle and chart area in points. Higher values push the subtitle up |
| `x_title_offset` | float | `0.55` | Horizontal centering of title text (0–1). 0.5 = center, 0.55 = slightly right |

**Advanced:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `show_zero_line` | bool | `false` | Draw a vertical line at x=0. Useful for charts with negative values |
| `zero_line_color` | string | `"#4b2e1a"` | Color of the zero line |
| `zero_line_style` | string | `"--"` | Line style: `"-"` solid, `"--"` dashed, `":"` dotted |
| `sep_index` | int | `null` | Draw a horizontal separator line between bar at this index and the next. Useful for grouping |
| `label_custom_offset` | object | `null` | Dict of `{bar_index: pixel_offset}` to manually nudge specific value labels |
| `min_val` | float | auto | Override minimum x-axis value |
| `max_val` | float | auto | Override maximum x-axis value |
| `factor_limit_x` | float | `1.0` | Multiplier for x-axis limits. Values > 1 add padding |

**Example:**
```json
{
  "type": "bar",
  "data": {
    "City": ["Philadelphia", "Miami", "Houston"],
    "Spending_M": [42, 45, 48]
  },
  "params": {
    "col_dim": "City",
    "col_measure": "Spending_M",
    "txt_suptitle": "Where the Money Lands",
    "txt_subtitle": "Projected visitor spending by U.S.\nWorld Cup host city ($ millions)",
    "txt_label": "Source: Data Appeal Company\nhttps://www.datappeal.io\n© Espresso Charts",
    "num_format": "${:,.0f}M",
    "bar_color": "color_green",
    "suptitle_size": 26,
    "subtitle_size": 14,
    "label_size": 10,
    "suptitle_y_custom": 0.99,
    "subtitle_pad_custom": 39
  }
}
```

---

## Line Chart

Multi-line time series chart. Best for trends over time, comparisons between series, and projections.

**Python function:** `eMultiLineChartInstagram()`

**Config `type`:** `"line"`

### Data Object

| Parameter | Type | Description |
|-----------|------|-------------|
| `data.DimColumn` | array | X-axis values (typically dates or years) |
| `data.MeasureColumn1` | array | Y-axis values for line 1 |
| `data.MeasureColumn2` | array | Y-axis values for line 2 (optional) |

### Params

**Data mapping:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `col_dim` | string | Name of the dimension column |
| `col_measure_list` | array | List of measure column names. One line drawn per column |

**Text hierarchy:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `txt_suptitle` | string | — | **Main heading** (large, serif). Rendered via `fig.text()` at the top |
| `txt_subtitle` | string | — | **Contextual subtitle** (smaller, sans-serif). Rendered below the heading |
| `txt_label` | string | — | **Source attribution** (bottom of chart) |

**Data labels:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pos_text` | array | — | Row indices where numeric value labels appear on the line. Example: `[0, 3, 7]` labels the 1st, 4th, and 8th data points |
| `pos_label` | int | `-1` | Row index where the line's text label (column name) is placed. `-1` = last point, `0` = first point |
| `num_format` | string | `"{:.0f}"` | Format string for numeric labels |
| `num_divisor` | float | `1` | Divide values before formatting (e.g., `1000000` to show millions) |

**Line styling:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `line_colors` | array | auto | List of color strings, one per line. Example: `["color_blue", "color_orange"]` |
| `line_styles` | array | `["-"]` | Line styles per line: `"-"` solid, `"--"` dashed, `":"` dotted, `"-."` dash-dot |
| `line_widths` | array | `[2]` | Line thickness per line in points |
| `line_labels` | array | auto | Text labels for each line. Defaults to column names |

**Axes:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x_ticks` | array | auto | Specific x-axis tick positions. Must match values in the dimension column |
| `x_tick_labels` | array | auto | Custom labels for x-axis ticks. Must be same length as `x_ticks` |
| `x_tick_size` | int | `10` | Font size for x-axis tick labels |
| `y_limits` | array | auto | `[y_min, y_max]` to fix the y-axis range. Prevents auto-scaling |
| `y_ticks` | array | auto | Specific y-axis tick values |
| `y_num_format` | string | auto | Format string for y-axis tick labels. Defaults to `num_format` |
| `show_y_axis` | bool | `false` | Show y-axis ticks and spine |
| `y_tick_color` | string | `"#857052"` | Color for y-axis tick labels |

**Font sizes:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suptitle_size` | int | `28` | Headline font size |
| `subtitle_size` | int | `16` | Subtitle font size |
| `label_size` | int | `12` | Source text and data label font size |

**Positioning:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suptitle_y` | float | `1.2` | Vertical position of headline in axes coordinates. Values > 1 place it above the plot area. For reel animations use `1.05` |
| `subtitle_y` | float | `1.09` | Vertical position of subtitle in axes coordinates. For reel animations use `0.98` |
| `chart_top_margin` | float | `0.15` | Fraction of canvas height reserved above the chart for titles |
| `aspect_ratio` | float | `1.0` | Height-to-width ratio of the plot area |

**Canvas:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `px` | int | `1080` | Width in pixels |
| `py` | int | `1350` | Height in pixels |

**Shading (optional):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `shade_between` | array | `null` | Tuple of two measure column names. Fills the area between the two lines |
| `shade_color` | string | `"#c8b8a8"` | Fill color for the shaded area |
| `shade_alpha` | float | `0.25` | Opacity of the shaded area (0 = transparent, 1 = opaque) |
| `shade_x` | array | `null` | `[x_start, x_end]` to limit shading to a date range. `null` = shade the full series |

**Zero line:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `show_zero_line` | bool | `false` | Draw a horizontal reference line |
| `zero_line_at` | float | `0` | Y-value where the line is drawn |
| `zero_line_color` | string | `"#857052"` | Color of the reference line |
| `zero_line_style` | string | `"--"` | Line style |

**Legend:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `show_legend` | bool | `false` | Display a legend box |
| `legend_loc` | string | `"upper left"` | Position: `"upper left"`, `"lower right"`, `"best"`, etc. |
| `legend_font_size` | int | `10` | Font size for legend text |
| `legend_text_color` | string | `"#857052"` | Color for legend labels |
| `legend_ncol` | int | `1` | Number of columns in the legend |
| `legend_bbox` | array | `[0, 1.02]` | `[x, y]` fine-tuning of legend position |
| `legend_labels_custom` | array | `null` | Override legend labels (separate from line labels on chart) |

---

## Stem Chart

Lollipop/stem chart with markers on a baseline. Best for showing magnitude at discrete points, especially timelines.

**Python function:** `eStemChartNewInstagram()`

**Config `type`:** `"stem"`

### Data Object

| Parameter | Type | Description |
|-----------|------|-------------|
| `data.DimColumn` | array | Category labels (x-axis) |
| `data.MeasureColumnA` | array | Primary values (required) |
| `data.MeasureColumnB` | array | Optional second series for comparison |

### Params

**Data mapping:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `col_dim` | string | Dimension column name |
| `col_measure_a` | string | Primary measure column |
| `col_measure_b` | string | Optional second measure column. Draws a second series of stems |

**Text hierarchy:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `txt_suptitle` | string | — | Main heading. In stem charts, rendered via `fig.suptitle()` |
| `txt_subtitle` | string | — | Subtitle. Rendered via `ax.set_title()` |
| `txt_label` | string | — | Source attribution |

**Number formatting:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_format` | string | `"{:.0f}"` | Format for value labels above each marker |

**Stem styling:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `color_a` | string | `"color_blue"` | Color for primary series stems and markers |
| `color_b` | string | `"#573D09"` | Color for optional second series |
| `marker_size` | int | `5` | Size of the dot at the top of each stem |
| `line_width` | float | `2.2` | Thickness of the stem lines |
| `line_format_a` | string | `"--"` | Line style for primary stems: `"-"` solid, `"--"` dashed |
| `line_format_b` | string | `"--"` | Line style for secondary stems |
| `x_axis_line_width` | float | `0.8` | Thickness of the horizontal baseline |
| `x_axis_line_color` | string | `"#857052"` | Color of the baseline |

**Font sizes:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suptitle_size` | int | `26` | Headline font size |
| `subtitle_size` | int | `14` | Subtitle font size |
| `label_size` | int | `11` | Source and value label font size |

**Positioning:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suptitle_y` | float | `1.06` | Vertical position of headline. For reel animations use `0.98` |
| `title_pad` | int | `90` | Padding above the subtitle in points |
| `labelpad` | int | `10` | Padding below the chart for the source label |
| `value_label_offset_pts` | int | `6` | Vertical offset (in points) of value labels above markers |

**Axes:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `y_min` | float | auto | Minimum y-axis value |
| `y_max` | float | auto | Maximum y-axis value |
| `rotate_labels` | bool | `false` | Rotate x-axis labels 90 degrees. Useful when labels are long (e.g., fiscal years) |
| `x_tick_label_y_offset` | float | `0` | Vertical offset for x-axis labels. Positive values push them down |
| `offset` | float | `0.1` | Horizontal offset between series A and B stems at the same x position |

**Legend:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `show_legend` | bool | `false` | Show legend (only relevant with two series) |
| `legend_labels` | array | `null` | `["Label A", "Label B"]` custom legend labels |
| `legend_loc` | string | `"upper right"` | Legend position |

**Year labels (optional):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year_label_a` | string | `null` | Text label placed at the last point of series A (e.g., `"2025"`) |
| `year_label_b` | string | `null` | Text label placed at the last point of series B |

---

## Donut Chart

Donut/pie chart. Best for part-to-whole relationships. Keep to 2–5 slices maximum.

**Python function:** `eDonutChartInstagram()`

**Config `type`:** `"donut"`

### Data Object

| Parameter | Type | Description |
|-----------|------|-------------|
| `data.LabelColumn` | array | Category names for each slice. Use `\n` in strings for multiline labels |
| `data.ValueColumn` | array | Numeric values for each slice. Can be percentages or absolute values |

### Params

**Data mapping:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `col_value` | string | Name of the value column |
| `col_label` | string | Name of the label column |

**Text hierarchy:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `txt_suptitle` | string | — | Main heading. Placed at top of figure via `fig.text()` |
| `txt_subtitle` | string | — | Subtitle. Placed below heading via `fig.text()` |
| `txt_label` | string | — | Source attribution. Placed at bottom via `fig.text()` |

**Number formatting:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_format` | string | `"{:.0f}%"` | Format for percentage labels on slices |

**Slice styling:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `colors` | array | auto | List of color strings, one per slice. Example: `["color_blue", "color_sand"]`. Order matches data order |
| `radius_outer` | float | `0.9` | Outer radius of the donut |
| `radius_inner` | float | `0.65` | Inner radius (creates the donut hole) |
| `wedge_width` | float | `0.3` | Width of the donut ring. Should equal `radius_outer - radius_inner` |
| `labeldistance` | float | `1.05` | Distance of category labels from center (1.0 = at edge) |
| `pctdistance_outer` | float | `0.8` | Distance of percentage labels from center |

**Center text (optional):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `center_text` | string | `null` | Text displayed in the donut hole |
| `center_text_color` | string | `"#4b2e1a"` | Color of center text |
| `center_text_size` | int | `12` | Font size of center text |

**Font sizes:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `suptitle_size` | int | `26` | Headline font size |
| `subtitle_size` | int | `14` | Subtitle font size |
| `label_size` | int | `10` | Slice label and source font size |

**Canvas:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `instagram_format` | string | `"4x5"` | `"4x5"` for portrait (1080x1350) or `"1x1"` for square (1080x1080) |
| `px` | int | `1080` | Width in pixels |

---

## Animated Charts (Reel)

Each reel contains a sequence of animated elements. The `animated_charts` array in the reel object defines this sequence.

### cover_animate

Animated version of the cover tile. Text fades/slides in.

Uses the same parameters as [Cover Tile](#cover-tile), with one critical difference:

| Parameter | Reel Value | Static Value | Why |
|-----------|-----------|-------------|-----|
| `suptitle_y` | `0.65` or lower | `0.6–0.85` | Instagram overlays UI on top ~15% of Reels. Headlines must sit lower |

### bar_animate

Bars grow from zero to their final values.

**Python function:** `eSingleBarChartAnimate()`

Uses all [Bar Chart](#bar-chart) params, plus:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | int | `12` | Animation length in seconds (bars growing) |
| `hold_frames` | int | `150` | Number of frames to hold the final state (at 24fps, 150 = ~6 seconds) |
| `fps` | int | `24` | Frames per second |

Reel-specific overrides:

| Parameter | Reel Value | Static Value | Why |
|-----------|-----------|-------------|-----|
| `suptitle_y_custom` | `0.93` | `0.99` | Keeps heading below Instagram's top UI overlay |

### line_animate

Lines draw progressively from left to right.

Uses all [Line Chart](#line-chart) params, plus `duration` and `hold_frames`.

Reel-specific overrides:

| Parameter | Reel Value | Static Value | Why |
|-----------|-----------|-------------|-----|
| `suptitle_y` | `1.05` | `1.2` | Safe zone adjustment |
| `subtitle_y` | `0.98` | `1.09` | Safe zone adjustment |

### stem_animate

Stems grow upward from the baseline.

Uses all [Stem Chart](#stem-chart) params, plus `duration` and `hold_frames`.

Reel-specific overrides:

| Parameter | Reel Value | Static Value | Why |
|-----------|-----------|-------------|-----|
| `suptitle_y` | `0.98` | `1.06` | Safe zone adjustment |

### Timing Rule

Total reel duration must exceed voiceover duration by at least 3 seconds.

```
Reel duration = cover hold (~4s) + chart duration + (hold_frames / fps)
Voiceover duration ≈ word count / 2.5

Example: 4s + 12s + (150/24)s = 22.25s
50-word voiceover ≈ 20s
22.25 > 20 + 3? No → increase duration to 15 or hold_frames to 200
```

---

## Voiceover

Spoken narration over the reel animation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | string | The spoken script. Approximately 50 words for 15–20 seconds at 0.95 speed. Write for the ear: short sentences, specific numbers, no jargon |

Voice settings are inherited from `defaults.voiceover` unless overridden.

**Writing tips:**
- Lead with the most striking number
- Use "X to Y" patterns for growth ("from 6 gigawatts to over 62")
- End with a punchy one-liner
- Avoid words that are hard to pronounce or ambiguous when spoken

---

## Music

Background music for the reel.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preset` | string | `"lofi_coffee"` | Music style. Options: `"lofi_coffee"` (chill, default), `"upbeat_data"` (energetic), `"editorial_minimal"` (serious/clean) |
| `duration_ms` | int | `24000` | Length of the music track in milliseconds. Must be at least 3000ms longer than the voiceover. Set to match or slightly exceed total reel duration |

---

## Story Files

Array defining which files the runner should generate for each story.

Each entry is a tuple: `[phase, index, file_type, extension]`

| Position | Description | Values |
|----------|-------------|--------|
| 0 | Phase number | `1` = charts/covers |
| 1 | Index within phase | `0` = first chart, `1` = second chart, `3` = reel with voice |
| 2 | File type | `"chart"`, `"cover"`, `"reel_with_voice"` |
| 3 | File extension | `"png"`, `"mp4"` |

**Standard story_files:**
```json
"story_files": [
  [1, 0, "chart", "png"],
  [1, 1, "chart", "png"],
  [1, 3, "reel_with_voice", "mp4"]
]
```

---

## Copy

All written content for a story across platforms.

### copy.instagram (Carousel Caption)

| Parameter | Type | Description |
|-----------|------|-------------|
| `caption` | string | 150–250 words. Opens with a hook, explains the data, ends with a question. No emojis in body except single ☕ sign-off |
| `hashtags` | string | 10–15 hashtags. Always include `#EspressoCharts #DataVisualization #DataJournalism` plus topic and reach tags |

### copy.instagram_reel (Reel Caption)

| Parameter | Type | Description |
|-----------|------|-------------|
| `caption` | string | 50–100 words. Punchier and shorter than carousel caption. Refers to "swipe for the data" |
| `hashtags` | string | 5–8 hashtags. Lighter set than carousel |

### copy.substack_article (Newsletter)

| Parameter | Type | Description |
|-----------|------|-------------|
| `headline` | string | Article title. Same as or similar to cover headline |
| `subhead` | string | Subtitle. Critical because it becomes the email subject line |
| `body` | string | 300–500 words. Lead with a number, reference charts explicitly ("As the first chart shows..."), section headings promise specific takeaways |
| `tags` | string | Comma-separated Substack tags for discoverability |
| `schedule_for` | string/null | ISO datetime for scheduled publishing. `null` = draft |

### copy.substack_note (Note)

| Parameter | Type | Description |
|-----------|------|-------------|
| (string) | string | Under 280 characters. Single stat teaser for the story. Used for daily Notes |

---

## Color Palette

Colors in the config are stored as strings that the runner resolves to hex values.

| Config String | Hex Value | Usage |
|---------------|-----------|-------|
| `"color_blue"` | `#3F5B83` | Primary accent. Default for bar charts and single-series charts |
| `"color_orange"` | `#A14516` | Secondary accent. Good for highlighting, warnings, growth |
| `"color_green"` | `#4D5523` | Tertiary. Good for environment, money, positive trends |
| `"color_sand"` | `#CDAF7B` | Neutral. Good for secondary donut slices, backgrounds, deemphasis |

When a parameter expects a color, always pass the string name, not the hex value:

```json
"bar_color": "color_green"     ← correct
"bar_color": "#4D5523"         ← will work but not recommended
```

---

## Typography

| Role | Font Family | Weight | Used For |
|------|-------------|--------|----------|
| Headlines | DejaVu Serif | normal/medium | Cover titles, chart main headings |
| Body text | DejaVu Sans | normal/light | Subtitles, source labels, axis labels, value labels |

All text must use `\n` for line breaks. Never use triple-quoted strings or actual newlines in JSON values.
