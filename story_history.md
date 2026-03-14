# Espresso Charts — Story History Log

This file is the authoritative record of all published story topics.
**Include this file in the master prompt** to prevent topic reuse.

Instruction for the prompt runner:
> Never generate a story whose core topic, dataset, or angle substantially overlaps with any entry in this log. "Substantially overlaps" means the same underlying data story even if the framing or time period differs slightly. When in doubt, skip the topic.

---

## Format

Each entry follows this structure:

```
### YYYY-MM-DD | Story N | slug
**Topic:** One-line description of what the chart shows
**Dataset:** Primary source used (FRED / World Bank / etc.)
**Angle:** The specific data angle or hook
**Chart type:** bar / line / stem / donut / cover
```

---

## 2026

### 2026-03-09 | Story 0 | [slug-unknown]
> *Add slug and details when first week's story pack is archived to GitHub.*
> This entry is a placeholder — update with actual topic once confirmed.

---

## Instructions for updating this log

After each weekly pack is published:
1. Add an entry for each story (Stories 0–2 per week).
2. Use the story slug from the GitHub archive path (`content/YYYY/MM-story-slug/`).
3. One entry per story, not per asset.
4. Keep entries in reverse-chronological order (newest first within each year).

---

## Prompt injection block

Paste the block below directly into the master prompt (`espresso_charts_prompt_v3.md`)
under the **Topic Selection** section:

```
### Previously published stories (do not reuse)

The following topics have already been covered. Do not generate any story that
substantially overlaps with these angles, datasets, or data stories.

[PASTE STORY HISTORY ENTRIES HERE — copy the ### blocks above]
```
