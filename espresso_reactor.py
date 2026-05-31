#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
espresso_reactor.py — News-reactive chart generator for Espresso Charts.

Given a news topic or URL, calls Claude to produce a story_config JSON,
then renders the static chart PNG and optionally the animated reel.

Usage:
    python espresso_reactor.py --topic "Solar hits 1 TW installed globally"
    python espresso_reactor.py --topic "..." --reel          # also render MP4
    python espresso_reactor.py --topic "..." --publish       # post Substack draft
    python espresso_reactor.py --topic "..." --push          # push to GitHub
    python espresso_reactor.py --config path/config.json     # skip Claude, just render

Required env vars:
    ANTHROPIC_API_KEY

Optional env vars (for --publish / --push):
    GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO   (default repo: espresso_charts_stories)
    SUBSTACK_URL, SUBSTACK_EMAIL, SUBSTACK_PASSWORD
    ANTHROPIC_MODEL   (default: claude-opus-4-5)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")   # non-interactive — works in CI and headless environments
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR  = Path(__file__).parent
PROMPT_FILE = SCRIPT_DIR / "prompts" / "espresso_charts_prompt_v9.md"
CHARTS_LIB  = SCRIPT_DIR / "espresso_charts.py"

# ─────────────────────────────────────────────────────────────────────────────
# CHART TYPE → FUNCTION DISPATCH   (mirrors espresso_charts_runner.ipynb)
# ─────────────────────────────────────────────────────────────────────────────

CHART_FUNCTIONS = {
    "bar":   "eSingleBarChartNewInstagram",
    "donut": "eDonutChartInstagram",
    "line":  "eMultiLineChartInstagram",
    "stem":  "eStemChartNewInstagram",
}

ANIMATE_FUNCTIONS = {
    "bar_animate":   "eSingleBarChartAnimateInstagram",
    "stem_animate":  "eStemChartAnimateInstagram",
    "line_animate":  "eMultiLineChartAnimateInstagram",
    "donut_animate": "eDonutChartAnimateInstagram",
}

COLOR_MAP = {
    "color_blue":   "#3F5B83",
    "color_orange": "#DD6B20",
    "color_green":  "#4D5523",
    "color_sand":   "#CDAF7B",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def resolve_colors(params: dict) -> dict:
    """Replace named color strings ('color_blue') with hex values."""
    out = {}
    for k, v in params.items():
        if isinstance(v, str) and v in COLOR_MAP:
            out[k] = COLOR_MAP[v]
        elif isinstance(v, list):
            out[k] = [COLOR_MAP[x] if isinstance(x, str) and x in COLOR_MAP else x for x in v]
        else:
            out[k] = v
    return out


def save_chart(fig, path: Path, dpi: int = 200):
    """Save chart with locked dimensions — no bbox_inches='tight'."""
    fig.savefig(path, dpi=dpi, bbox_inches=None, pad_inches=0,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"    Saved → {path.name}")


def load_ec():
    """Load espresso_charts.py into a module object at runtime."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("espresso_charts", CHARTS_LIB)
    ec   = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ec)
    return ec


# ─────────────────────────────────────────────────────────────────────────────
# RENDER ONE STORY
# ─────────────────────────────────────────────────────────────────────────────

def render_story(story: dict, out_dir: Path, ec, dpi: int = 200,
                 render_reel: bool = False) -> list[Path]:
    """
    Render one story's static charts (and optionally animated reel) to out_dir.
    Returns list of generated PNG paths.
    """
    sid  = story["id"]
    slug = story["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    pngs: list[Path] = []

    print(f"\n  Story {sid}: {slug}")

    # ── Static charts (PNG) ───────────────────────────────────────────────
    for ci, chart in enumerate(story.get("charts", []), start=1):
        chart_type = chart["type"]
        fn_name    = CHART_FUNCTIONS.get(chart_type)
        if not fn_name:
            print(f"    [chart {ci}] unknown type '{chart_type}' — skipped")
            continue
        fn = getattr(ec, fn_name, None)
        if fn is None:
            print(f"    [chart {ci}] {fn_name} not in library — skipped")
            continue

        df     = pd.DataFrame(chart["data"])
        params = ec.sanitize_chart_text_params(
            resolve_colors(chart.get("params", {})), slug=slug,
        )
        out_f  = out_dir / f"story{sid}_chart{ci}.png"

        print(f"    [chart {ci}] {fn_name}")
        try:
            result = fn(df_chart=df, **params)
            fig    = result[0] if isinstance(result, (tuple, list)) else result
            save_chart(fig, out_f, dpi=dpi)
            pngs.append(out_f)
        except Exception as exc:
            print(f"    [chart {ci}] ERROR: {exc}")

    # ── Animated reel (MP4) — only when --reel is set ────────────────────
    if render_reel and "reel" in story:
        for ai, ac in enumerate(story["reel"].get("animated_charts", []), start=1):
            ac_type = ac["type"]
            fn_name = ANIMATE_FUNCTIONS.get(ac_type)
            if not fn_name:
                print(f"    [reel {ai}] unknown type '{ac_type}' — skipped")
                continue
            fn = getattr(ec, fn_name, None)
            if fn is None:
                print(f"    [reel {ai}] {fn_name} not in library — skipped")
                continue

            df     = pd.DataFrame(ac["data"])
            params = ec.sanitize_chart_text_params(
                resolve_colors(ac.get("params", {})), slug=slug,
            )
            out_f  = out_dir / f"story{sid}_reel{ai}.mp4"
            params.setdefault("output_file", str(out_f))

            print(f"    [reel {ai}] {fn_name}")
            try:
                fn(df_chart=df, **params)
                print(f"    Saved → {out_f.name}")
            except Exception as exc:
                print(f"    [reel {ai}] ERROR: {exc}")

    return pngs


# ─────────────────────────────────────────────────────────────────────────────
# CLAUDE — GENERATE CONFIG FROM NEWS TOPIC
# ─────────────────────────────────────────────────────────────────────────────

_REACTOR_SUFFIX = """
---
## REACTOR MODE

You are being called by the Espresso Charts automated news-reactive pipeline.

Given the news topic or URL below, generate a **single-story JSON config** for today.

Hard rules:
- Follow all guidelines in this prompt exactly.
- Output ONLY valid JSON — no markdown fences, no preamble, no explanation.
- Top-level structure: {"week": {...}, "defaults": {...}, "stories": [...]}
- Exactly 1 story in "stories".
- The story must include: cover, charts (≥1 static chart), reel, story_files, poster, copy.
- The static chart (in "charts") is mandatory — it produces the PNG image.
- Choose the chart archetype that best fits the data (bar / line / stem / donut).
- Use all current headline rules: exactly 2 suptitle lines, ≤30 chars each.
- Set week fields from today's date for asset paths only. Never set txt_issue or calendar posting dates on chart text fields.
"""


def generate_config(topic: str, today: str) -> dict:
    """Call Claude API to generate a story_config dict for the given topic."""
    try:
        import anthropic
    except ImportError:
        sys.exit("ERROR: anthropic package not installed. Run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: ANTHROPIC_API_KEY environment variable not set.")

    model       = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")
    prompt_text = PROMPT_FILE.read_text(encoding="utf-8")
    client      = anthropic.Anthropic(api_key=api_key)

    user_msg = (
        f"Today's date: {today}\n\n"
        f"NEWS TOPIC / URL:\n{topic}\n\n"
        "Generate the story_config JSON now."
    )

    print(f"  Calling Claude ({model}) to generate story config...")
    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=prompt_text + _REACTOR_SUFFIX,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = message.content[0].text.strip()
    # Strip accidental markdown fences
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
    raw = re.sub(r"\n?```\s*$", "", raw)
    # Strip any BOM or leading whitespace
    raw = raw.lstrip("\ufeff").strip()

    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"\n[ERROR] Claude returned invalid JSON.\nFirst 600 chars:\n{raw[:600]}\n{exc}")
        sys.exit(1)

    return config


# ─────────────────────────────────────────────────────────────────────────────
# OPTIONAL: PUBLISH & PUSH
# ─────────────────────────────────────────────────────────────────────────────

def publish_to_substack(story: dict):
    """Post a Substack draft from the story's copy block."""
    url   = os.environ.get("SUBSTACK_URL")
    email = os.environ.get("SUBSTACK_EMAIL")
    pw    = os.environ.get("SUBSTACK_PASSWORD")
    if not all([url, email, pw]):
        print("  [publish] SUBSTACK_URL / EMAIL / PASSWORD not set — skipping.")
        return

    sys.path.insert(0, str(SCRIPT_DIR))
    from github_substack_publisher import SubstackPublisher

    copy  = story.get("copy", {})
    ig    = copy.get("instagram_reel", {})
    yt    = copy.get("youtube_shorts", {})
    body  = ig.get("caption") or yt.get("description", "")
    title = yt.get("title") or story["slug"].replace("_", " ").title()

    sp = SubstackPublisher(url, email, pw)
    sp.post_draft(title=title, body=body)
    print(f"  [publish] Substack draft created: {title}")


def push_to_github(out_dir: Path, week: dict):
    """Push all output files to the espresso_charts_stories GitHub repo."""
    token = os.environ.get("GITHUB_TOKEN")
    owner = os.environ.get("GITHUB_OWNER")
    repo  = os.environ.get("GITHUB_REPO", "espresso_charts_stories")
    if not all([token, owner]):
        print("  [github] GITHUB_TOKEN / GITHUB_OWNER not set — skipping.")
        return

    sys.path.insert(0, str(SCRIPT_DIR))
    from github_substack_publisher import GitHubUploader

    uploader  = GitHubUploader(token=token, owner=owner, repo=repo)
    dest_base = f"assets/{week['year']}/{week['month']}/{week['week_start']}"

    for f in sorted(out_dir.iterdir()):
        if f.suffix in (".png", ".mp4", ".json", ".pdf"):
            uploader.push_file(str(f), dest=f"{dest_base}/{f.name}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap  = argparse.ArgumentParser(
        description="Espresso Charts — news-reactive chart generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--topic",
        metavar="TEXT",
        help="News headline, URL, or free-text description to react to",
    )
    src.add_argument(
        "--config",
        metavar="PATH",
        help="Path to an existing story_config.json (skips Claude generation)",
    )
    ap.add_argument("--reel",    action="store_true", help="Also render animated MP4 reel")
    ap.add_argument("--publish", action="store_true", help="Post Substack draft after generation")
    ap.add_argument("--push",    action="store_true", help="Push outputs to GitHub")
    ap.add_argument(
        "--out-dir",
        default=None,
        metavar="PATH",
        help="Output directory (default: reactor_output/YYYYMMDD-HHMMSS/)",
    )
    args = ap.parse_args()

    today   = datetime.now().strftime("%Y-%m-%d")
    ts      = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out_dir) if args.out_dir else Path("reactor_output") / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Load or generate config ────────────────────────────────────────────
    if args.config:
        print(f"Loading config: {args.config}")
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    else:
        print(f"\nTopic: {args.topic}")
        config = generate_config(args.topic, today)

    config_path = out_dir / "story_config.json"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    print(f"  Config → {config_path}")

    # ── Load chart library ─────────────────────────────────────────────────
    print("\nLoading espresso_charts library...")
    ec  = load_ec()
    dpi = config.get("defaults", {}).get("dpi", 200)

    # ── Render all stories ─────────────────────────────────────────────────
    all_pngs: list[Path] = []
    for story in config.get("stories", []):
        pngs = render_story(story, out_dir, ec, dpi=dpi, render_reel=args.reel)
        all_pngs.extend(pngs)

    print(f"\n✓ {len(all_pngs)} chart(s) generated → {out_dir}/")

    # ── Optional: push to GitHub ───────────────────────────────────────────
    if args.push:
        week = config.get("week", {"year": today[:4], "month": today[5:7], "week_start": today[8:10]})
        push_to_github(out_dir, week)

    # ── Optional: Substack draft ───────────────────────────────────────────
    if args.publish:
        for story in config.get("stories", []):
            publish_to_substack(story)


if __name__ == "__main__":
    main()
