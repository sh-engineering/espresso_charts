# Espresso Charts — Story History Log

This file is the **authoritative record** of all published and in-production story topics.
**Include this file in the master prompt** (`espresso_charts_prompt_v9.md`) to prevent topic reuse.

Instruction for the prompt runner:
> Never generate a story whose core topic, dataset, or angle substantially overlaps with any entry in this log. "Substantially overlaps" means the same underlying data story even if the framing or time period differs slightly. When in doubt, skip the topic.

---

## Format

Each entry follows this structure:

```
### YYYY-MM-DD | Story N | slug
**Week:** Week of Mon D – Sun D, YYYY
**Topic:** One-line description of what the chart shows
**Dataset:** Primary source used
**Angle:** The specific data angle or hook
**Chart type:** bar / line / stem / donut (or unknown if not archived)
**Status:** published / drafted / planned
```

Entries are grouped by calendar week, **newest week first**. Within each week, stories are ordered Mon → Sat by story id.

---

## GitHub archive (`espresso_charts_stories`)

Published asset packs are intended to live at:

`https://github.com/sh-engineering/espresso_charts_stories` → `content/{year}/{slug}/`

**As of 2026-05-31:** this repo is not readable via public API (404). `gh` CLI is not installed in the local environment. Slugs below marked *(inferred)* were not verified against GitHub paths. Reconcile when archive access is restored.

---

## 2026

### Week of Mar 9 – Mar 15, 2026

*Source: `prompts/story_log.md` (logged 2026-03-15). Three-story weekly cadence. Posting dates assumed Mon / Wed / Fri.*

### 2026-03-09 | Story 0 | gold_price_surge *(inferred)*
**Week:** Week of Mar 9 – Mar 15, 2026
**Topic:** Gold price surge from $252 to $5,192; central bank buying
**Dataset:** Unknown — verify primary source before reuse
**Angle:** Record gold rally driven by central bank accumulation
**Chart type:** unknown
**Status:** planned

### 2026-03-11 | Story 1 | renewables_741gw_2024 *(inferred)*
**Week:** Week of Mar 9 – Mar 15, 2026
**Topic:** Record renewable energy additions — 741 GW in 2024, solar dominance
**Dataset:** IRENA / IEA (typical for this angle — verify)
**Angle:** Fastest year ever for global renewable capacity additions
**Chart type:** unknown
**Status:** planned

### 2026-03-13 | Story 2 | ev_sales_20pct_global *(inferred)*
**Week:** Week of Mar 9 – Mar 15, 2026
**Topic:** EV sales crossing 20% of global car sales — 17M units in 2024
**Dataset:** IEA Global EV Outlook (typical — verify)
**Angle:** One in five new cars sold is electric
**Chart type:** unknown
**Status:** planned

---

### Week of Mar 2 – Mar 8, 2026

*Source: `prompts/story_log.md` (logged 2026-03-15).*

### 2026-03-02 | Story 0 | planetary_parade_light_pollution *(inferred)*
**Week:** Week of Mar 2 – Mar 8, 2026
**Topic:** Planetary parade and light pollution
**Dataset:** Unknown — verify primary source before reuse
**Angle:** Rare planetary alignment vs. sky brightness / light pollution context
**Chart type:** unknown
**Status:** planned

### 2026-03-04 | Story 1 | ai_layoffs_wef_jobs *(inferred)*
**Week:** Week of Mar 2 – Mar 8, 2026
**Topic:** AI-driven layoffs (Block / Jack Dorsey, WEF Future of Jobs)
**Dataset:** WEF / company filings (typical — verify)
**Angle:** Automation and AI reshaping employment forecasts and corporate headcount
**Chart type:** unknown
**Status:** planned

### 2026-03-06 | Story 2 | us_gdp_germany_stagnation *(inferred)*
**Week:** Week of Mar 2 – Mar 8, 2026
**Topic:** U.S. Q4 GDP slowdown and Germany stagnation
**Dataset:** BEA / Destatis / OECD (typical — verify)
**Angle:** Transatlantic growth divergence
**Chart type:** unknown
**Status:** planned

---

### Week of Feb 23 – Mar 1, 2026

*Source: `prompts/story_log.md` + draft chart code in `previous version/espresso_charts.py`.*

### 2026-02-23 | Story 0 | ai_data_center_power *(inferred)*
**Week:** Week of Feb 23 – Mar 1, 2026
**Topic:** AI data center electricity demand; Microsoft 40 GW renewables contract
**Dataset:** IEA (data center demand projections); EIA (U.S. grid mix); Microsoft announcement
**Angle:** AI is driving a step-change in electricity demand; hyperscalers contracting record renewable capacity
**Chart type:** bar (grid mix) + line (IEA data center TWh 2015–2030)
**Status:** drafted

### 2026-02-25 | Story 1 | fifa_world_cup_41b *(inferred)*
**Week:** Week of Feb 23 – Mar 1, 2026
**Topic:** 2026 FIFA World Cup economic impact — ~$41B GDP, host city visitor spending
**Dataset:** Data Appeal Company / Mabrian (2026)
**Angle:** Where World Cup visitor spending lands by U.S. host city and category
**Chart type:** bar (city spending) + donut (spending category breakdown)
**Status:** drafted

### 2026-02-27 | Story 2 | nvidia_revenue_213b *(inferred)*
**Week:** Week of Feb 23 – Mar 1, 2026
**Topic:** Nvidia revenue growth from ~$6.9B to $213B in a decade
**Dataset:** Nvidia SEC filings / investor relations; company earnings (hyperscaler capex chart)
**Angle:** 30× revenue growth in ten fiscal years; Big Tech capex arms race
**Chart type:** stem (Nvidia annual revenue FY2017–FY2026E) + bar (2026 hyperscaler capex plans)
**Status:** drafted

---

## Example config (not production — do not treat as published)

*Embedded in `espresso_charts_runner.ipynb`. Week start **2025-03-24**. Old 3-story OECD macro demo — not in story log.*

| Story | Slug | Topic |
|-------|------|-------|
| 0 | `global_growth_squeezed` | OECD 2025 GDP growth forecasts by economy |
| 1 | `consumer_confidence_crash` | U.S. consumer expectations 12-year low |
| 2 | `solar_record_year` | Record global solar installs (452 GW narrative) |

---

## Instructions for updating this log

After each weekly pack is published:

1. Add one entry per daily story (Stories `id` 0–6 under the current v9 cadence; historically 0–2 for three-story weeks).
2. Use the story **slug** from the GitHub archive path (`content/{year}/{slug}/`) when available.
3. Include **Week of Mon D – Sun D, YYYY** and the **posting date** (YYYY-MM-DD).
4. Mark **Status:** `published` only after assets are pushed to `espresso_charts_stories`.
5. Keep weeks in reverse-chronological order (newest first).
6. Remove *(inferred)* from slug lines once verified against GitHub.

---

## Prompt injection block

Paste the block below into the weekly prompt under topic selection:

```
### Previously published stories (do not reuse)

The following topics have already been covered. Do not generate any story that
substantially overlaps with these angles, datasets, or data stories.

[PASTE ### entry blocks from ## 2026 above — omit Example config section]
```
