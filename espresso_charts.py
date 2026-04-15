# -*- coding: utf-8 -*-
"""
espresso_charts.py — Espresso Charts Library (v2 — Standardized Layout)
Fonts: Playfair Display (display) · Source Serif 4 (body) · DM Mono (mono)
Install fonts before use: install_espresso_fonts()
========================================================================
Chart functions for Instagram carousels (4:5) and Reels (9:16).

v2 CHANGES:
-----------
All chart types now share a unified layout system. Title positions, plot area
boundaries, and footnote positions are fixed via figure-relative coordinates.
This eliminates the inconsistency between chart types where bar charts used
fig.suptitle(), line charts used ax.text(transform=ax.transAxes), etc.

LAYOUT ZONES (figure coordinates, y=0 bottom, y=1 top):
  ┌─────────────────────────┐ y = 1.0
  │  suptitle (26pt, ≤2 ln) │ y ≈ 0.955 (4:5) / 0.965 (9:16)
  │  subtitle (14pt, ≤2 ln) │ y ≈ 0.890 (4:5) / 0.920 (9:16)
  ├─────────────────────────┤ plot_top ≈ 0.815 / 0.870
  │                         │
  │       PLOT AREA         │
  │                         │
  ├─────────────────────────┤ plot_bottom ≈ 0.085 / 0.055
  │  footnote (9pt, ≤2 ln)  │ y ≈ 0.040 / 0.025
  └─────────────────────────┘ y = 0.0

Static charts:  eSingleBarChartNewInstagram, eMultiLineChartInstagram,
                eStemChartNewInstagram, eDonutChartInstagram, eCoverTileInstagram

Animated charts: eSingleBarChartAnimateInstagram, eMultiLineChartAnimateInstagram,
                 eStemChartAnimateInstagram, eDonutChartAnimateInstagram,
                 eCoverTileAnimateInstagram

Helpers:         save_chart, fetch_fred_series, add_custom_annotations,
                 add_lines, add_text, add_reference_bands, add_vlines, eConcatenateMP4
"""

import os, io, subprocess, tempfile, warnings
from decimal import Decimal
from io import StringIO
from urllib.request import urlopen
import base64
from pathlib import Path
from datetime import datetime
import json, time

import matplotlib.animation as animation
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression

warnings.filterwarnings("ignore")


# ============================================================================
# FONT INSTALLER
# ============================================================================

def install_espresso_fonts():
    """
    Download and install the Espresso Charts font set from Google Fonts GitHub.
    Run once per Colab session before rendering any charts.
    Fonts installed: Playfair Display, Source Serif 4, DM Mono.
    """
    from pathlib import Path as _Path

    FONT_DIR = _Path("/usr/local/share/fonts/espresso")
    FONT_DIR.mkdir(parents=True, exist_ok=True)

    fonts = [
        # Playfair Display — variable font from google/fonts repo
        ("PlayfairDisplay[wght].ttf",
         "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"),
        # Source Serif 4 — variable font from google/fonts repo
        ("SourceSerif4[opsz,wght].ttf",
         "https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/SourceSerif4%5Bopsz%2Cwght%5D.ttf"),
        ("SourceSerif4-Italic[opsz,wght].ttf",
         "https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/SourceSerif4-Italic%5Bopsz%2Cwght%5D.ttf"),
        # DM Mono — static TTFs (still available)
        ("DMMono-Regular.ttf",
         "https://raw.githubusercontent.com/google/fonts/main/ofl/dmmono/DMMono-Regular.ttf"),
        ("DMMono-Light.ttf",
         "https://raw.githubusercontent.com/google/fonts/main/ofl/dmmono/DMMono-Light.ttf"),
    ]

    for filename, url in fonts:
        dest = FONT_DIR / filename
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"  Already installed: {filename}")
            continue
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 1000:
            dest.write_bytes(r.content)
            print(f"  Installed: {filename}")
        else:
            print(f"  FAILED ({r.status_code}): {filename}")

    # Delete matplotlib's font cache
    import matplotlib as mpl
    cache_dir = _Path(mpl.get_cachedir())
    for cache_file in cache_dir.glob("fontlist-*.json"):
        try:
            cache_file.unlink()
            print(f"  Deleted cache: {cache_file.name}")
        except Exception:
            pass

    # Rebuild font manager from scratch (clean slate)
    fm._load_fontmanager(try_read_cache=False)

    # Register our fonts LAST — nothing modifies the manager after this
    for filename, url in fonts:
        font_path = str(FONT_DIR / filename)
        try:
            fm.fontManager.addfont(font_path)
        except Exception:
            pass

    # Verify fonts are found
    print()
    for name in ['Playfair Display', 'Source Serif 4', 'DM Mono']:
        try:
            match = fm.findfont(fm.FontProperties(family=name))
            found = name.lower().replace(' ', '') in match.lower().replace(' ', '')
            print(f"  {'✓' if found else '✗'} {name} -> {match}")
        except Exception:
            print(f"  ✗ {name} -> NOT FOUND")

    print("\nReady: Playfair Display, Source Serif 4, DM Mono")


# ============================================================================
# STYLE CONFIG
# ============================================================================
color_blue   = '#3F5B83'
color_orange = '#A14516'
color_green  = '#4D5523'
color_sand   = '#CDAF7B'
face_color   = '#F5F0E6'

font_display = 'Playfair Display'   # headlines, suptitle, cover, opening numbers
font_body    = 'Source Serif 4'     # subtitles, body text
font_mono    = 'DM Mono'            # labels, ticks, source lines, data values


# ============================================================================
# STANDARDIZED LAYOUT SYSTEM
# ============================================================================
# All values are figure-relative coordinates (0 = bottom/left, 1 = top/right).
# Tuned for: 2-line suptitle at 26pt + 2-line subtitle at 14pt + 2-line footnote at 9pt.
# If titles are shorter, the extra space becomes clean whitespace above the plot.

_LAYOUT = {
    # Computed from font metrics:
    #   suptitle 26pt × 2 lines × 1.2 ls = 57.2pt block
    #   subtitle 14pt × 2 lines × 1.2 ls = 30.8pt block
    #   footnote  9pt × 2 lines × 1.2 ls = 19.8pt block
    #   gap between elements = 0.015 fig units
    #
    # 4:5 figure = 6.75 in tall → suptitle block = 0.118, subtitle block = 0.063
    # 9:16 figure = 9.6 in tall → suptitle block = 0.083, subtitle block = 0.045
    '4x5': {
        'figsize_px': (1080, 1350),
        'suptitle_y':  0.960,   # top of suptitle text block
        'subtitle_y':  0.827,   # = 0.960 - 0.118 (sup block) - 0.015 (gap)
        'plot_top':    0.749,   # = 0.827 - 0.063 (sub block) - 0.015 (gap)
        'plot_bottom': 0.085,   # axes bottom edge
        'footnote_y':  0.045,   # top of footnote text block
    },
    '9x16': {
        # Instagram Reel safe zones: top ~250px, bottom ~200px are covered by UI.
        # Content must stay within y=0.104 to y=0.870 (in figure coords).
        # Top:  250px / 1920 = 0.130 buffer → content ceiling at 0.870
        # Bottom: 200px / 1920 = 0.104 buffer → content floor at 0.104
        'figsize_px': (1080, 1920),
        'suptitle_y':  0.870,   # right at the top safe edge
        'subtitle_y':  0.772,   # = 0.870 - 0.083 (sup block) - 0.015 (gap)
        'plot_top':    0.712,   # = 0.772 - 0.045 (sub block) - 0.015 (gap)
        'plot_bottom': 0.185,   # extra space for x-axis tick labels
        'footnote_y':  0.120,   # just above bottom safe zone (floor = 0.104)
    },
}

# Font defaults
_SUPTITLE_SIZE = 26
_SUBTITLE_SIZE = 14
_FOOTNOTE_SIZE = 9
_SUPTITLE_FONT = 'Playfair Display'
_SUBTITLE_FONT = 'Source Serif 4'
_BODY_FONT     = 'DM Mono'


def _setup_chart(layout='4x5', face_color='#F5F0E6', dpi=200,
                 plot_left=0.10, plot_right=0.90):
    """Create figure + axes with standardized layout zones.

    Parameters
    ----------
    layout : '4x5' or '9x16'
    face_color : background color
    dpi : resolution
    plot_left, plot_right : horizontal margins (chart-type specific)

    Returns
    -------
    fig, ax, L : figure, axes, layout dict for downstream use
    """
    plt.rcdefaults()
    plt.rcParams['font.family'] = _BODY_FONT

    L = _LAYOUT[layout]
    px_w, px_h = L['figsize_px']
    figsize = (px_w / dpi, px_h / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    fig.subplots_adjust(
        top=L['plot_top'], bottom=L['plot_bottom'],
        left=plot_left, right=plot_right,
    )
    ax.set_facecolor(face_color)
    fig.patch.set_facecolor(face_color)
    fig.patch.set_edgecolor(face_color)
    fig.patch.set_linewidth(0)
    fig.patch.set_alpha(1)
    return fig, ax, L


def _add_titles(fig, txt_suptitle, txt_subtitle, L,
                suptitle_color='#4b2e1a', subtitle_color='#4b2e1a',
                suptitle_font=None, subtitle_font=None,
                suptitle_font_weight='normal', subtitle_font_weight='normal',
                suptitle_size=None, subtitle_size=None):
    """Place suptitle and subtitle at fixed positions using fig.text().

    Returns (suptitle_obj, subtitle_obj) for animation use.
    """
    sf = suptitle_font or _SUPTITLE_FONT
    tf = subtitle_font or _SUBTITLE_FONT
    ss = suptitle_size or _SUPTITLE_SIZE
    ts = subtitle_size or _SUBTITLE_SIZE

    sup = fig.text(
        0.5, L['suptitle_y'], txt_suptitle,
        fontsize=ss, color=suptitle_color,
        fontweight=suptitle_font_weight, fontfamily=sf,
        ha='center', va='top', linespacing=1.2,
    )
    sub = fig.text(
        0.5, L['subtitle_y'], txt_subtitle,
        fontsize=ts, color=subtitle_color,
        fontweight=subtitle_font_weight, fontfamily=tf,
        ha='center', va='top', linespacing=1.2,
    )
    return sup, sub


def _add_footnote(fig, txt_label, L,
                  color='#857052', font_weight='light', size=None):
    """Place footnote at fixed position below the plot area."""
    fs = size or _FOOTNOTE_SIZE
    return fig.text(
        0.5, L['footnote_y'], txt_label,
        fontsize=fs, color=color, fontweight=font_weight,
        ha='center', va='top', linespacing=1.2,
    )


# ============================================================================
# INTERNAL: coerce string-keyed dicts to int keys (JSON compat)
# ============================================================================
def _int_keys(d):
    """Convert {'0': 4, '1': 2} -> {0: 4, 1: 2}. Pass-through for None or already-int-keyed."""
    if not isinstance(d, dict):
        return d
    try:
        return {int(k): v for k, v in d.items()}
    except (ValueError, TypeError):
        return d


def save_chart(fig, path, dpi=200):
    """Save chart with locked dimensions. Never uses bbox_inches='tight'."""
    fig.savefig(path, dpi=dpi, bbox_inches=None, pad_inches=0,
                facecolor=fig.get_facecolor())


def fetch_fred_series(series_id, api_key=None, start_date="2010-01-01"):
    if api_key is None:
        api_key = os.environ.get("FRED_API_KEY", "")
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series_id, "api_key": api_key,
              "file_type": "json", "observation_start": start_date}
    data = requests.get(url, params=params).json()
    df = pd.DataFrame(data["observations"])[["date", "value"]]
    df["date"]  = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["series_id"] = series_id
    return df


# ============================================================================
# SHARED HELPERS
# ============================================================================

def add_reference_bands(ax, bands, orientation='horizontal'):
    for band in bands:
        lo    = band['min']
        hi    = band['max']
        color = band.get('color', '#857052')
        alpha = band.get('alpha', 0.15)
        zo    = band.get('zorder', 0)
        if orientation == 'horizontal':
            ax.axhspan(lo, hi, color=color, alpha=alpha, zorder=zo, linewidth=0)
        else:
            ax.axvspan(lo, hi, color=color, alpha=alpha, zorder=zo, linewidth=0)
        if band.get('label'):
            lc   = band.get('label_color', color)
            ls   = band.get('label_size', 10)
            mid  = (lo + hi) / 2
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            if orientation == 'horizontal':
                ax.text(xlim[1], mid, f"  {band['label']}",
                        ha='left', va='center', color=lc, fontsize=ls, zorder=zo+1)
            else:
                ax.text(mid, ylim[1], f"  {band['label']}",
                        ha='center', va='bottom', color=lc, fontsize=ls,
                        rotation=90, zorder=zo+1)
    return ax


def add_vlines(ax, lines):
    for ln in lines:
        color = ln.get('color', '#857052')
        ax.axvline(
            ln['x'], color=color, linestyle=ln.get('style', '--'),
            linewidth=ln.get('width', 1.0), alpha=ln.get('alpha', 0.8),
            zorder=ln.get('zorder', 5))
        if ln.get('label'):
            lc = ln.get('label_color', color)
            ls = ln.get('label_size', 10)
            ha = ln.get('label_ha', 'center')
            ylim = ax.get_ylim()
            ax.text(ln['x'], ylim[1], f" {ln['label']}",
                    ha=ha, va='top', color=lc, fontsize=ls,
                    zorder=ln.get('zorder', 5) + 1)
    return ax


def add_hlines(ax, lines):
    for ln in lines:
        color = ln.get('color', '#857052')
        ax.axhline(
            ln['y'], color=color, linestyle=ln.get('style', '--'),
            linewidth=ln.get('width', 1.0), alpha=ln.get('alpha', 0.8),
            zorder=ln.get('zorder', 5))
        if ln.get('label'):
            lc = ln.get('label_color', color)
            ls = ln.get('label_size', 10)
            ha = ln.get('label_ha', 'left')
            zo = ln.get('zorder', 5) + 1
            if ha == 'right':
                ax.text(0.98, ln['y'], ln['label'],
                        ha='right', va='bottom', color=lc, fontsize=ls,
                        transform=ax.get_yaxis_transform(), zorder=zo)
            elif ha == 'left_inside':
                ax.text(0.02, ln['y'], ln['label'],
                        ha='left', va='bottom', color=lc, fontsize=ls,
                        transform=ax.get_yaxis_transform(), zorder=zo)
            else:
                xlim = ax.get_xlim()
                ax.text(xlim[1], ln['y'], f"  {ln['label']}",
                        ha='left', va='center', color=lc, fontsize=ls,
                        zorder=zo)
    return ax


def add_custom_annotations(ax, annotations):
    for anno in annotations:
        color  = anno.get('color', '#4b2e1a')
        zo     = anno.get('zorder', 10)
        bbox_d = None
        if anno.get('frame', True):
            bbox_d = anno.get('bbox', dict(
                boxstyle='round,pad=0.4',
                facecolor=anno.get('bg_color', 'white'),
                edgecolor=anno.get('frame_color', color),
                alpha=anno.get('frame_alpha', 0.9),
            ))
        if anno.get('arrow_to') is not None:
            ac = anno.get('arrow_color', color)
            ax.annotate(
                anno['text'], xy=anno['arrow_to'], xytext=anno['xy'],
                ha=anno.get('ha', 'center'), va=anno.get('va', 'center'),
                color=color, fontsize=anno.get('fontsize', 12), bbox=bbox_d,
                arrowprops=dict(arrowstyle=anno.get('arrowstyle', '->'), color=ac,
                                lw=anno.get('arrow_lw', 1.2), connectionstyle='arc3,rad=0'),
                zorder=zo)
        else:
            ax.text(
                anno['xy'][0], anno['xy'][1], anno['text'],
                color=color, fontsize=anno.get('fontsize', 12),
                ha=anno.get('ha', 'center'), va=anno.get('va', 'center'),
                bbox=bbox_d, zorder=zo)
    return ax


def add_lines(ax, lines):
    for ln in lines:
        zo = ln.get('zorder', 8)
        if ln.get('arrow', False):
            ax.annotate(
                '', xy=ln['end'], xytext=ln['start'],
                arrowprops=dict(arrowstyle=ln.get('arrowstyle', '->'),
                                color=ln.get('color', '#4b2e1a'),
                                lw=ln.get('linewidth', 1.5),
                                linestyle=ln.get('linestyle', '-')),
                zorder=zo)
        else:
            ax.plot(
                [ln['start'][0], ln['end'][0]], [ln['start'][1], ln['end'][1]],
                color=ln.get('color', '#4b2e1a'), linewidth=ln.get('linewidth', 1.5),
                linestyle=ln.get('linestyle', '-'), zorder=zo)
    return ax


def add_text(ax, texts):
    for txt in texts:
        ax.text(
            txt['xy'][0], txt['xy'][1], txt['text'],
            fontsize=txt.get('fontsize', 12), color=txt.get('color', '#4b2e1a'),
            ha=txt.get('ha', 'left'), va=txt.get('va', 'bottom'),
            fontweight=txt.get('fontweight', 'normal'), rotation=txt.get('rotation', 0),
            alpha=txt.get('alpha', 1.0), family=txt.get('family', 'DM Mono'),
            linespacing=txt.get('linespacing', 1.2), zorder=txt.get('zorder', 10))
    return ax



# ============================================================================
# STATIC CHART: SINGLE BAR  (4:5 Instagram)
# ============================================================================
def eSingleBarChartNewInstagram(
    df_chart, col_dim, col_measure, txt_suptitle, txt_subtitle, txt_label,
    pos_text=None, pos_label=-1, num_format="{:.0f}", num_divisor=1,
    bar_height=None, bar_color=None, bar_colors=None,
    hide_left_spine=False, offset_label_x=0,
    min_val=None, max_val=None, factor_limit_x=1.0, aspect_ratio=None,
    label_custom_offset=None, value_label_offset_x=None, value_label_offset_y=None,
    show_x_axis=False, x_axis_num_format=None,
    reference_bands=None, vlines=None, hlines=None,
    suptitle_size=None, subtitle_size=None, label_size=12,
    suptitle_color='#4b2e1a', subtitle_color='#4b2e1a',
    txt_label_color='#857052', tick_label_color='#3c3325',
    value_label_color='#4b2e1a', face_color='#f5f0e6',
    coffee_palette=('#9d8561','#857052','#6c5c43','#544734','#3c3325',
                    '#79664a','#d9d0c1','#0b0a07'),
    suptitle_font_weight='normal', subtitle_font_weight='normal',
    txt_label_font_weight='normal',
    font='DM Mono', suptitle_font=None, subtitle_font=None,
    show_zero_line=False, zero_line_color='#4b2e1a',
    zero_line_style='--', zero_line_width=1.0,
    instagram=True, px_width=1080, px_height=1350, dpi=200,
    sep_index=None, sep_color='#4b2e1a', sep_style='-', sep_width=1.5,
    # Legacy params — accepted but ignored in v2 standardized layout
    suptitle_y_custom=None, subtitle_pad_custom=None, x_subtitle_offset=None,
):
    # JSON compat
    label_custom_offset  = _int_keys(label_custom_offset)
    value_label_offset_x = _int_keys(value_label_offset_x)
    value_label_offset_y = _int_keys(value_label_offset_y)

    # --- Standardized layout ---
    # Auto-detect if all values are negative to swap margins
    all_negative = (df_chart[col_measure] < 0).all()
    all_positive = (df_chart[col_measure] >= 0).all()
    if all_negative:
        p_left, p_right = 0.05, 0.75  # wide right margin for category labels
    else:
        p_left, p_right = 0.10, 0.80  # standard: right margin for value labels

    fig, ax, L = _setup_chart(
        layout='4x5', face_color=face_color, dpi=dpi,
        plot_left=p_left, plot_right=p_right,
    )
    _add_titles(fig, txt_suptitle, txt_subtitle, L,
                suptitle_color=suptitle_color, subtitle_color=subtitle_color,
                suptitle_font=suptitle_font, subtitle_font=subtitle_font,
                suptitle_font_weight=suptitle_font_weight,
                subtitle_font_weight=subtitle_font_weight,
                suptitle_size=suptitle_size, subtitle_size=subtitle_size)
    _add_footnote(fig, txt_label, L,
                  color=txt_label_color, font_weight=txt_label_font_weight)

    if bar_color is None:
        bar_color = coffee_palette[0]
    if bar_height is None:
        bar_height = 0.75

    n = len(df_chart)
    if bar_colors is not None:
        bar_colors = _int_keys(bar_colors)
        if isinstance(bar_colors, dict):
            colors_list = [bar_colors.get(i, bar_color) for i in range(n)]
        else:
            colors_list = list(bar_colors)
    else:
        colors_list = [bar_color] * n

    bars = ax.barh(df_chart[col_dim], df_chart[col_measure],
                   color=colors_list, height=bar_height, zorder=3)

    if reference_bands:
        add_reference_bands(ax, reference_bands, orientation='vertical')

    for side in ['top', 'right', 'bottom']:
        ax.spines[side].set_linewidth(0)
    if hide_left_spine:
        ax.spines['left'].set_linewidth(0)
    else:
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['left'].set_color(tick_label_color)
        ax.spines['left'].set_zorder(5)

    ax.set_yticks([])
    ax.tick_params(axis='y', left=False)

    if show_x_axis:
        ax.spines['bottom'].set_linewidth(0.8)
        ax.spines['bottom'].set_color(tick_label_color)
        ax.tick_params(axis='x', colors=tick_label_color, labelsize=label_size - 1)
        if x_axis_num_format:
            ax.xaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: x_axis_num_format.format(v / num_divisor)))
    else:
        ax.set_xticks([])
        ax.tick_params(axis='x', colors=face_color)

    if min_val is None: min_val = float(df_chart[col_measure].min())
    if max_val is None: max_val = float(df_chart[col_measure].max())
    ax.set_xlim(min(min_val * factor_limit_x, 0), max(max_val * factor_limit_x, 0))

    if show_zero_line:
        ax.axvline(0, color=zero_line_color, linestyle=zero_line_style,
                   linewidth=zero_line_width, zorder=2)
    if vlines: add_vlines(ax, vlines)
    if hlines: add_hlines(ax, hlines)

    if sep_index is not None:
        for si in (sep_index if isinstance(sep_index, (list, tuple)) else [sep_index]):
            ax.axhline(si + 0.5, color=sep_color, linestyle=sep_style,
                       linewidth=sep_width, zorder=4)

    for idx, (patch, value) in enumerate(zip(bars, df_chart[col_measure])):
        category = str(df_chart[col_dim].iloc[idx])
        y_center = patch.get_y() + patch.get_height() / 2
        x_start  = patch.get_x()
        x_end    = x_start + patch.get_width()
        is_pos   = (value >= 0)

        # Category label: always at x=0 (the axis), reading rightward.
        # For positive bars: label sits inside the bar near its base (parchment bbox).
        # For negative bars: label sits in the right margin (bars extend left).
        cat_extra = 0
        if isinstance(label_custom_offset, dict):
            cat_extra = label_custom_offset.get(idx, 0)
        cat_anchor = 0
        off_cat = 8 + offset_label_x + cat_extra
        ax.annotate(
            category, xy=(cat_anchor, y_center),
            xytext=(off_cat, 0), textcoords='offset points',
            ha='left', va='center', fontsize=label_size,
            color=tick_label_color, zorder=6, clip_on=False,
            bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                      edgecolor='none', alpha=0.8))

        # Value label: at the tip of the bar
        val       = value / num_divisor
        formatted = num_format.format(val) if num_format else str(val)
        x_extra = 0
        if isinstance(value_label_offset_x, dict):
            x_extra += value_label_offset_x.get(idx, 0)
        y_extra = 0
        if isinstance(value_label_offset_y, dict):
            y_extra = value_label_offset_y.get(idx, 0)
        tip = x_end if is_pos else x_start
        ha_val  = 'left' if is_pos else 'right'
        off_val = 8 + x_extra if is_pos else -8 - x_extra
        ax.annotate(
            formatted, xy=(tip, y_center),
            xytext=(off_val, y_extra), textcoords='offset points',
            ha=ha_val, va='center',
            fontsize=label_size, color=value_label_color, zorder=6, clip_on=False,
            bbox=dict(boxstyle='square,pad=0', facecolor=face_color,
                      edgecolor=face_color, alpha=0.85))

    if aspect_ratio is not None:
        ax.set_box_aspect(aspect_ratio)

    return fig, ax



# ============================================================================
# STATIC CHART: MULTI-LINE  (4:5 Instagram)
# ============================================================================
def eMultiLineChartInstagram(
    df_chart, col_dim, col_measure_list, txt_suptitle, txt_subtitle, txt_label,
    pos_text, pos_label=None, num_format="{:.0f}", num_divisor=1,
    x_ticks=None, x_tick_labels=None, tick_color='#4B2E1A', x_tick_size=10,
    aspect_ratio=1.0, line_colors=None, line_styles=None, line_widths=None, line_labels=None,
    suptitle_color='#4b2e1a', subtitle_color='#4b2e1a', txt_label_color='#857052',
    face_color='#F5F0E6',
    suptitle_font_weight='normal', suptitle_font=None,
    subtitle_font_weight='normal', subtitle_font=None,
    txt_label_font_weight='normal',
    show_zero_line=False, zero_line_color='#857052', zero_line_style='--',
    zero_line_width=1.0, zero_line_at=0,
    px=1080, py=1350, dpi=200,
    suptitle_size=None, subtitle_size=None, label_size=12, bottom_note_size=None,
    y_limits=None, text_offset_y=None,
    shade_between=None, shade_color='#c8b8a8', shade_alpha=0.25, shade_x=None,
    show_y_axis=False, y_ticks=None, y_tick_color='#857052', y_tick_size=10,
    y_num_format=None,
    show_legend=False, legend_labels_custom=None, legend_loc='upper left',
    legend_font_size=10, legend_text_color='#857052', legend_ncol=1,
    legend_bbox=(0, 1.02), chart_top_margin=0.15,
    hide_x_axis=False,
    label_offset_x=8, label_offset_y=0, point_label_offsets=None,
    show_markers=False, marker_size=4, marker_styles=None,
    show_trend_lines=False, trend_line_colors=None, trend_line_style='--',
    trend_line_width=1.0, trend_line_alpha=0.6,
    reference_bands=None, vlines=None, hlines=None,
    # Legacy params — accepted but ignored in v2
    suptitle_y=None, subtitle_y=None,
):
    # --- Standardized layout ---
    fig, ax, L = _setup_chart(
        layout='4x5', face_color=face_color, dpi=dpi,
        plot_left=0.10, plot_right=0.90,
    )
    _add_titles(fig, txt_suptitle, txt_subtitle, L,
                suptitle_color=suptitle_color, subtitle_color=subtitle_color,
                suptitle_font=suptitle_font, subtitle_font=subtitle_font,
                suptitle_font_weight=suptitle_font_weight,
                subtitle_font_weight=subtitle_font_weight,
                suptitle_size=suptitle_size, subtitle_size=subtitle_size)
    _add_footnote(fig, txt_label, L,
                  color=txt_label_color, font_weight=txt_label_font_weight,
                  size=bottom_note_size)

    default_colors = ['#9d8561', '#857052', '#6c5c43', '#544734', '#3c3325']
    colors  = line_colors  if line_colors  is not None else default_colors
    styles  = line_styles  if line_styles  is not None else ['-']   * len(col_measure_list)
    widths  = line_widths  if line_widths  is not None else [0.9]   * len(col_measure_list)
    labels  = line_labels  if line_labels  is not None else list(col_measure_list)
    mstyles = marker_styles if marker_styles is not None else ['o'] * len(col_measure_list)

    def _pad(lst):
        if len(lst) < len(col_measure_list):
            return (lst * (len(col_measure_list) // len(lst) + 1))[:len(col_measure_list)]
        return lst
    colors, styles, widths, labels, mstyles = (_pad(colors), _pad(styles),
                                                _pad(widths), _pad(labels), _pad(mstyles))

    if reference_bands:
        add_reference_bands(ax, reference_bands, orientation='horizontal')

    x = df_chart[col_dim]
    for idx, col in enumerate(col_measure_list):
        ax.plot(x, df_chart[col], color=colors[idx], linestyle=styles[idx],
                linewidth=widths[idx], zorder=9)
        if show_markers:
            ax.plot(x, df_chart[col], mstyles[idx], color=colors[idx],
                    markersize=marker_size, zorder=10, linewidth=0)
        if show_trend_lines:
            xnum = np.arange(len(df_chart)).reshape(-1, 1)
            ynum = df_chart[col].values.astype(float)
            reg  = LinearRegression().fit(xnum, ynum)
            yfit = reg.predict(xnum)
            tc   = (trend_line_colors[idx] if trend_line_colors and idx < len(trend_line_colors)
                    else colors[idx])
            ax.plot(x, yfit, color=tc, linestyle=trend_line_style,
                    linewidth=trend_line_width, alpha=trend_line_alpha, zorder=8)

    for side in ['top', 'right', 'bottom']:
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_visible(False)

    if hide_x_axis:
        ax.set_xticks([]); ax.tick_params(axis='x', length=0, labelsize=0)
    else:
        ax.tick_params(axis='x', colors=tick_color, labelsize=x_tick_size)

    if not hide_x_axis:
        if x_ticks is None:
            try:    x_ticks = [x.iloc[0], x.iloc[-1]]
            except: x_ticks = [min(x), max(x)]
        if x_tick_labels is None: x_tick_labels = x_ticks
        ax.set_xticks(x_ticks); ax.set_xticklabels(x_tick_labels)

    if show_y_axis:
        if y_ticks is not None: ax.set_yticks(y_ticks)
        fmt = y_num_format if y_num_format is not None else num_format
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: fmt.format(v / num_divisor)))
        ax.tick_params(axis='y', labelleft=True, colors=y_tick_color,
                       labelsize=y_tick_size, length=4, width=0.6)
        ax.spines['left'].set_visible(True)
        ax.spines['left'].set_linewidth(0.6)
        ax.spines['left'].set_color(y_tick_color)
    else:
        ax.set_yticks([]); ax.spines['left'].set_visible(False)

    if show_legend:
        leg_labels = legend_labels_custom if legend_labels_custom is not None else labels
        leg = ax.legend(leg_labels, loc=legend_loc, bbox_to_anchor=legend_bbox,
                        ncol=legend_ncol, frameon=False, fontsize=legend_font_size)
        if legend_text_color is not None:
            for t in leg.get_texts(): t.set_color(legend_text_color)

    if show_zero_line:
        ax.axhline(zero_line_at, color=zero_line_color, linestyle=zero_line_style,
                   linewidth=zero_line_width, zorder=8)
    if vlines: add_vlines(ax, vlines)
    if hlines: add_hlines(ax, hlines)

    n_rows = len(df_chart)
    for pos in (pos_text or []):
        if pos < 0: pos = n_rows + pos
        if not (0 <= pos < n_rows): continue
        for idx, col in enumerate(col_measure_list):
            raw = df_chart[col].iloc[pos]
            val = raw / num_divisor
            try:    fmt_s = num_format.format(val)
            except: fmt_s = str(val)
            oy = (text_offset_y[idx] if isinstance(text_offset_y, (list, tuple))
                  else (text_offset_y or 0))
            if isinstance(point_label_offsets, dict):
                ox_pt, oy_pt = point_label_offsets.get((pos, idx), (0, 0))
            else:
                ox_pt, oy_pt = 0, 0
            ax.annotate(
                fmt_s, xy=(x.iloc[pos], raw + oy + oy_pt),
                xytext=(ox_pt, 0), textcoords='offset points',
                ha='center', va='bottom', color=colors[idx],
                fontsize=label_size, zorder=11,
                bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                          edgecolor=face_color, alpha=0.8))

    if pos_label is not None:
        pos_eff = n_rows + pos_label if pos_label < 0 else pos_label
        if 0 <= pos_eff < n_rows:
            for idx, col in enumerate(col_measure_list):
                x_i = x.iloc[pos_eff]
                y_i = df_chart[col].iloc[pos_eff]
                if isinstance(point_label_offsets, dict):
                    ox_s, oy_s = point_label_offsets.get((pos_eff, idx), (label_offset_x, label_offset_y))
                else:
                    ox_s, oy_s = label_offset_x, label_offset_y
                ax.annotate(
                    str(labels[idx]), xy=(x_i, y_i),
                    xytext=(ox_s, oy_s), textcoords='offset points',
                    ha='left', va='center', color=colors[idx],
                    fontsize=label_size, zorder=11,
                    bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                              edgecolor=face_color, alpha=0.8))

    if shade_between is not None:
        cl, ch = shade_between
        y1, y2 = df_chart[cl], df_chart[ch]
        if shade_x is None:
            ax.fill_between(x, y1, y2, color=shade_color, alpha=shade_alpha, zorder=1)
        else:
            xs, xe = shade_x; mask = (x >= xs) & (x <= xe)
            ax.fill_between(x[mask], y1[mask], y2[mask],
                            color=shade_color, alpha=shade_alpha, zorder=1)

    ax.set_box_aspect(aspect_ratio)
    if y_limits is not None: ax.set_ylim(y_limits)

    return fig, ax



# ============================================================================
# STATIC CHART: STEM  (4:5 Instagram)
# ============================================================================
def eStemChartNewInstagram(
    df_chart, col_dim, col_measure_a, col_measure_b=None, col_category_pos=None,
    txt_suptitle="", txt_subtitle="", txt_label="",
    num_format="{:.0f}", num_divisor=1, offset=0.1, x_tick_label_y_offset=0,
    marker_size=4, line_width=0.8,
    suptitle_color="#4b2e1a", subtitle_color="#4b2e1a",
    axis_label_color="#79664a", tick_label_color="#3c3325",
    face_color="#F5F0E6", color_a="#a58e6c", color_b="#573D09",
    year_label_a=None, year_label_b=None,
    label_a_offset_x=1, label_b_offset_x=1,
    label_a_offset_y=1, label_b_offset_y=1,
    instagram=True, px_width=1080, px_height=1350, dpi=200,
    suptitle_size=None, subtitle_size=None, label_size=12,
    aspect_ratio=None, rotate_labels=False,
    xtick_align_ha="center", xtick_align_va="top",
    value_label_offset_pts=6, value_label_offset_y=None, value_label_offset_x=None,
    x_axis_line_width=0.8, x_axis_line_color="#857052",
    line_format_a="--", line_format_b="--",
    value_label_custom_offset=None,
    show_legend=False, legend_labels=None, legend_loc='upper right',
    legend_font_size=10, legend_frame=False, legend_text_color='#3c3325',
    legend_bbox_to_anchor=None, y_min=None, y_max=None,
    show_x_axis=False, reference_bands=None, vlines=None, hlines=None,
    font='DM Mono', suptitle_font=None, subtitle_font=None,
    # Legacy params — accepted but ignored in v2
    suptitle_y=None, subtitle_y=None, subtitle_pad=None, labelpad=None,
):
    # JSON compat
    value_label_offset_y      = _int_keys(value_label_offset_y)
    value_label_offset_x      = _int_keys(value_label_offset_x)
    value_label_custom_offset = _int_keys(value_label_custom_offset)

    # --- Standardized layout ---
    fig, ax, L = _setup_chart(
        layout='4x5', face_color=face_color, dpi=dpi,
        plot_left=0.12, plot_right=0.92,
    )
    _add_titles(fig, txt_suptitle, txt_subtitle, L,
                suptitle_color=suptitle_color, subtitle_color=subtitle_color,
                suptitle_font=suptitle_font, subtitle_font=subtitle_font,
                suptitle_size=suptitle_size, subtitle_size=subtitle_size)
    _add_footnote(fig, txt_label, L, color=axis_label_color)

    xpos = (np.arange(len(df_chart)) if col_category_pos is None
            else np.asarray(df_chart[col_category_pos]))
    cats = df_chart[col_dim].tolist()

    y_a = df_chart[col_measure_a].to_numpy() / num_divisor
    markerline, stemlines, baseline = ax.stem(xpos - offset, y_a,
                                               markerfmt="o", linefmt=line_format_a, basefmt=" ")
    plt.setp(markerline, color=color_a, markersize=marker_size, linewidth=line_width, zorder=2)
    plt.setp(stemlines,  color=color_a, linewidth=line_width, zorder=1)

    if col_measure_b is not None:
        y_b = df_chart[col_measure_b].to_numpy() / num_divisor
        markerline, stemlines, baseline = ax.stem(xpos + offset, y_b,
                                                   markerfmt="o", linefmt=line_format_b, basefmt=" ")
        plt.setp(markerline, color=color_b, markersize=marker_size, linewidth=line_width, zorder=2)
        plt.setp(stemlines,  color=color_b, linewidth=line_width, zorder=1)

    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_linewidth(0)
    ax.axhline(0, color=x_axis_line_color, linewidth=x_axis_line_width)

    if y_min is not None or y_max is not None:
        cur_min, cur_max = ax.get_ylim()
        ax.set_ylim(y_min if y_min is not None else cur_min,
                    y_max if y_max is not None else cur_max)

    ax.set_xticks(xpos)
    ax.set_xticklabels([])  # hide default tick labels
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])

    # Place category labels manually at y=0 in data coordinates.
    # This ensures labels align with the x-axis line regardless of plot limits.
    # va="top" -> top of text box touches y=0 (labels hang below axis)
    # va="bottom" -> bottom of text box touches y=0 (labels sit above axis)
    label_y_data = 0 + x_tick_label_y_offset  # offset is in data units
    for idx, (xp, cat) in enumerate(zip(xpos, cats)):
        ax.text(xp, label_y_data, cat, color=tick_label_color,
                fontsize=label_size, ha=xtick_align_ha, va=xtick_align_va,
                rotation=90 if rotate_labels else 0,
                bbox=dict(boxstyle="square,pad=0.1", facecolor="white",
                          edgecolor="white", alpha=0.7),
                transform=ax.transData, clip_on=False)

    if reference_bands: add_reference_bands(ax, reference_bands, orientation='horizontal')
    if vlines: add_vlines(ax, vlines)
    if hlines: add_hlines(ax, hlines)

    def _get_offsets(i, val, global_y_offset, per_label_y, per_label_x, legacy_custom=None):
        base_y = global_y_offset if val >= 0 else -global_y_offset
        extra_y = 0
        if per_label_y and i in per_label_y: extra_y = per_label_y[i]
        elif legacy_custom and i in legacy_custom: extra_y = legacy_custom[i]
        extra_x = 0
        if per_label_x and i in per_label_x: extra_x = per_label_x[i]
        return base_y + extra_y, extra_x

    for i, val in enumerate(y_a):
        y_off, x_off = _get_offsets(i, val, value_label_offset_pts,
                                     value_label_offset_y, value_label_offset_x,
                                     value_label_custom_offset)
        ax.annotate(num_format.format(val), xy=(xpos[i] - offset, val),
            xytext=(x_off, y_off), textcoords="offset points",
            ha="center", va="bottom" if val >= 0 else "top",
            fontsize=label_size, color=color_a,
            bbox=dict(boxstyle="square,pad=0.2", facecolor="white",
                      edgecolor="white", alpha=0.7), zorder=10)

    if col_measure_b is not None:
        for i, val in enumerate(y_b):
            y_off, x_off = _get_offsets(i, val, value_label_offset_pts,
                                         value_label_offset_y, value_label_offset_x,
                                         value_label_custom_offset)
            ax.annotate(num_format.format(val), xy=(xpos[i] + offset, val),
                xytext=(x_off, y_off), textcoords="offset points",
                ha="center", va="bottom" if val >= 0 else "top",
                fontsize=label_size, color=color_b,
                bbox=dict(boxstyle="square,pad=0.2", facecolor="white",
                          edgecolor="white", alpha=0.7), zorder=10)

    if year_label_a:
        ax.text(xpos[0] + label_a_offset_x, label_a_offset_y, str(year_label_a),
                color=color_a, ha="left", va="bottom", rotation=90, fontsize=label_size,
                bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="white", alpha=0.8))
    if col_measure_b is not None and year_label_b:
        ax.text(xpos[0] + label_b_offset_x, label_b_offset_y, str(year_label_b),
                color=color_b, ha="left", va="bottom", rotation=90, fontsize=label_size,
                bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="white", alpha=0.8))

    if show_legend:
        handles, leg_labels = [], []
        line_a = plt.Line2D([0], [0], color=color_a, linewidth=line_width,
                            linestyle=line_format_a, marker='o', markersize=marker_size)
        handles.append(line_a)
        leg_labels.append(legend_labels[0] if legend_labels else 'Series A')
        if col_measure_b is not None:
            line_b = plt.Line2D([0], [0], color=color_b, linewidth=line_width,
                                linestyle=line_format_b, marker='o', markersize=marker_size)
            handles.append(line_b)
            leg_labels.append(legend_labels[1] if legend_labels and len(legend_labels) > 1 else 'Series B')
        legend = ax.legend(handles, leg_labels, loc=legend_loc, fontsize=legend_font_size,
                           frameon=legend_frame, bbox_to_anchor=legend_bbox_to_anchor)
        for t in legend.get_texts(): t.set_color(legend_text_color)

    if aspect_ratio is not None:
        ax.set_box_aspect(aspect_ratio)

    return fig, ax



# ============================================================================
# STATIC CHART: DONUT  (4:5 Instagram)
# ============================================================================
def eDonutChartInstagram(
    df_chart, col_value, col_label=None, col_inner=None,
    txt_suptitle="", txt_subtitle="", txt_label="",
    num_format="{:.0f}%", num_divisor=1,
    radius_outer=0.9, inner_radius=None, wedge_width=0.4,
    radius_inner=0.65, wedge_width_inner=None,
    labeldistance=1.05, pctdistance_outer=0.8, pctdistance_inner=0.75,
    show_pct=True, autopct_outer=True, autopct_inner=True,
    colors=None, pct_colors=None, label_colors=None,
    center_text=None, center_text_color="#4b2e1a",
    center_text_size=12, center_text_weight="normal",
    suptitle_color='#4b2e1a', subtitle_color='#4b2e1a', txt_label_color='#857052',
    face_color='#F5F0E6',
    suptitle_font_weight='medium', subtitle_font_weight='light', txt_label_font_weight='light',
    suptitle_size=None, subtitle_size=None, label_size=10, bottom_note_size=None,
    font='DM Mono', suptitle_font=None, subtitle_font=None,
    figsize=(8, 8), dpi=200, px=1080, instagram=True, instagram_format='4x5',
    # Legacy params — accepted but ignored in v2
    suptitle_y=None, subtitle_y=None, label_y=None,
):
    # --- Standardized layout ---
    fig, ax, L = _setup_chart(
        layout='4x5', face_color=face_color, dpi=dpi,
        plot_left=0.05, plot_right=0.95,  # donut needs wide axes for labels
    )
    _add_titles(fig, txt_suptitle, txt_subtitle, L,
                suptitle_color=suptitle_color, subtitle_color=subtitle_color,
                suptitle_font=suptitle_font, subtitle_font=subtitle_font,
                suptitle_font_weight=suptitle_font_weight,
                subtitle_font_weight=subtitle_font_weight,
                suptitle_size=suptitle_size, subtitle_size=subtitle_size)
    _add_footnote(fig, txt_label, L,
                  color=txt_label_color, font_weight=txt_label_font_weight,
                  size=bottom_note_size)

    default_colors = ['#d9d0c1','#79664a','#9d8561','#857052','#6c5c43','#544734','#3c3325']
    if colors is None: colors = default_colors
    outer_band = radius_outer - inner_radius if inner_radius is not None else wedge_width
    inner_band = wedge_width_inner if wedge_width_inner is not None else outer_band

    pie_labels = df_chart[col_label].astype(str) if col_label is not None else None
    def autopct_func(pct):
        try:    return num_format.format(pct)
        except: return f"{pct:.0f}%"
    outer_autopct = autopct_func if (show_pct and autopct_outer) else None
    inner_autopct = autopct_func if (show_pct and autopct_inner) else None

    # ax.pie returns 2 values when autopct is None, 3 when it's set
    pie_result = ax.pie(
        df_chart[col_value] / num_divisor, radius=radius_outer, labels=pie_labels,
        labeldistance=labeldistance, colors=colors, wedgeprops=dict(width=outer_band),
        startangle=90, autopct=outer_autopct, pctdistance=pctdistance_outer,
        textprops={'fontsize': label_size})
    if outer_autopct is not None:
        wedges, texts, autotexts = pie_result
    else:
        wedges, texts = pie_result
        autotexts = []
    if label_colors:
        for i, t in enumerate(texts):
            if i < len(label_colors): t.set_color(label_colors[i])
    if pct_colors:
        for i, t in enumerate(autotexts):
            if i < len(pct_colors): t.set_color(pct_colors[i])

    # --- Fix overlapping pie labels ---
    # Collect (index, y-position) for all visible label texts, sort by y,
    # then nudge any pair that is closer than min_gap apart.
    if texts:
        fig.canvas.draw()  # force position calculation
        min_gap = 0.08
        positions = [(i, t.get_position()[1]) for i, t in enumerate(texts)
                     if t.get_text().strip()]
        positions.sort(key=lambda p: p[1])
        for k in range(len(positions) - 1):
            idx_lo, y_lo = positions[k]
            idx_hi, y_hi = positions[k + 1]
            if abs(y_hi - y_lo) < min_gap:
                nudge = (min_gap - abs(y_hi - y_lo)) / 2 + 0.02
                x_lo, _ = texts[idx_lo].get_position()
                x_hi, _ = texts[idx_hi].get_position()
                texts[idx_lo].set_position((x_lo, y_lo - nudge))
                texts[idx_hi].set_position((x_hi, y_hi + nudge))
                # Update sorted list for cascading checks
                positions[k]     = (idx_lo, y_lo - nudge)
                positions[k + 1] = (idx_hi, y_hi + nudge)

    if col_inner:
        inner_result = ax.pie(
            df_chart[col_inner] / num_divisor, radius=radius_inner, colors=colors,
            wedgeprops=dict(width=inner_band), startangle=90, autopct=inner_autopct,
            pctdistance=pctdistance_inner, textprops={'fontsize': label_size})
        if inner_autopct is not None:
            wedges2, texts2, autotexts2 = inner_result
        else:
            wedges2, texts2 = inner_result
            autotexts2 = []
        if pct_colors:
            for i, t in enumerate(autotexts2):
                if i < len(pct_colors): t.set_color(pct_colors[i])
    if center_text:
        ax.text(0, 0, center_text, ha="center", va="center", fontsize=center_text_size,
                color=center_text_color, fontweight=center_text_weight, linespacing=1.2)

    for side in ['top','right','left','bottom']: ax.spines[side].set_linewidth(0)
    ax.set_aspect("equal", adjustable="box")
    return fig, ax


# ============================================================================
# STATIC CHART: COVER TILE  (4:5 Instagram)
# ============================================================================
def eCoverTileInstagram(
    txt_suptitle, txt_subtitle, txt_label="",
    # New cover-specific parameters
    txt_eyebrow="", txt_issue="", txt_unit=None, txt_context=None,
    eyebrow_y=0.78, eyebrow_size=9, eyebrow_color='#9e8b76',
    unit_size=14, unit_color=None,
    context_y=0.10, context_size=12, context_color='#79664a',
    issue_size=8, descender_pad=0.015,
    show_corner_mark=False, corner_mark_size=28,
    suptitle_font_style='italic',
    # Existing parameters (some defaults updated)
    suptitle_color='#2A1F14', suptitle_font='Playfair Display',
    suptitle_font_weight='bold', suptitle_size=86, suptitle_y=0.60,
    subtitle_color='#2A1F14', subtitle_font='Source Serif 4',
    subtitle_font_weight='normal', subtitle_size=16, subtitle_y=0.19,
    txt_label_color='#CDAF7B', txt_label_font='DM Mono',
    txt_label_font_weight='light', label_size=8, label_y=0.038,
    face_color='#F5F0E6', px_width=1080, px_height=1350, dpi=200,
    show_accent_line=True, accent_line_color='#3F5B83', accent_line_width=4,
    accent_line_y=0.29, accent_line_length=0.15,
):
    """Number-led cover tile with editorial layout.

    If hero number + unit overlaps the accent line, reduce suptitle_y
    or reduce suptitle_size in the config.

    Layers: background, top rule, corners, eyebrow, hero number,
    unit, accent line, insight (txt_subtitle), context, bottom rule,
    source, corner mark.
    """
    rule_color = '#C8BBA8'
    plt.rcdefaults(); plt.rcParams['font.family'] = 'DM Mono'
    figsize = (px_width / dpi, px_height / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    for spine in ax.spines.values(): spine.set_visible(False)

    # Layer 2: Top rule
    ax.plot([0.08, 0.92], [0.895, 0.895], color=rule_color, linewidth=0.6,
            transform=ax.transAxes, zorder=3)

    # Layer 3: Corner labels
    if txt_issue:
        ax.text(0.08, 0.925, txt_issue, fontfamily='DM Mono',
                fontsize=issue_size, color='#9e8b76', ha='left', va='center',
                transform=ax.transAxes, zorder=4)
    ax.text(0.92, 0.925, "Espresso Charts", fontfamily='DM Mono',
            fontsize=issue_size, color='#9e8b76', ha='right', va='center',
            transform=ax.transAxes, zorder=4)

    # Layer 4: Eyebrow
    if txt_eyebrow:
        ax.text(0.5, eyebrow_y, txt_eyebrow, fontfamily='DM Mono',
                fontsize=eyebrow_size, color=eyebrow_color,
                ha='center', va='center', transform=ax.transAxes, zorder=4)

    # Layer 5: Hero number
    suptitle_obj = ax.text(
        0.5, suptitle_y, txt_suptitle, fontsize=suptitle_size,
        color=suptitle_color, ha='center', va='center',
        fontweight=suptitle_font_weight, fontstyle=suptitle_font_style,
        fontfamily=suptitle_font, linespacing=0.9, transform=ax.transAxes, zorder=4)

    # Layer 6: Unit line (with descender fix)
    if txt_unit:
        uc = unit_color or suptitle_color
        try:
            renderer = fig.canvas.get_renderer()
            bb = suptitle_obj.get_window_extent(renderer=renderer)
            bb_axes = bb.transformed(ax.transAxes.inverted())
            unit_y = bb_axes.y0 - descender_pad
        except Exception:
            unit_y = suptitle_y - 0.12  # fallback
        ax.text(0.5, unit_y, txt_unit, fontfamily=suptitle_font,
                fontsize=unit_size, fontstyle='italic', fontweight='normal',
                color=uc, alpha=0.75, ha='center', va='top',
                transform=ax.transAxes, zorder=4)

    # Layer 7: Accent line
    if show_accent_line:
        half = accent_line_length / 2
        ax.plot([0.5 - half, 0.5 + half], [accent_line_y, accent_line_y],
                color=accent_line_color, linewidth=accent_line_width,
                solid_capstyle='round', transform=ax.transAxes, zorder=3)

    # Layer 8: Insight sentence (txt_subtitle)
    ax.text(0.5, subtitle_y, txt_subtitle, fontsize=subtitle_size,
            color=subtitle_color, ha='center', va='center',
            fontweight='semibold', fontstyle='italic',
            fontfamily=suptitle_font, linespacing=1.35,
            transform=ax.transAxes, zorder=4)

    # Layer 9: Context sentence
    if txt_context:
        ax.text(0.5, context_y, txt_context, fontfamily=subtitle_font,
                fontsize=context_size, fontstyle='italic', fontweight='light',
                color=context_color, ha='center', va='center',
                linespacing=1.5, transform=ax.transAxes, zorder=4)

    # Layer 10: Bottom rule
    ax.plot([0.08, 0.92], [0.07, 0.07], color=rule_color, linewidth=0.6,
            transform=ax.transAxes, zorder=3)

    # Layer 11: Source line
    if txt_label:
        ax.text(0.5, label_y, txt_label, fontfamily='DM Mono',
                fontsize=label_size, color=txt_label_color,
                ha='center', va='center', fontweight=txt_label_font_weight,
                transform=ax.transAxes, zorder=4)

    # Layer 12: Corner mark
    if show_corner_mark:
        fig_w_pts = fig.get_size_inches()[0] * fig.dpi
        fig_h_pts = fig.get_size_inches()[1] * fig.dpi
        cx = corner_mark_size / fig_w_pts
        cy = corner_mark_size / fig_h_pts
        triangle = mpatches.Polygon(
            [[1.0 - cx, 0.0], [1.0, 0.0], [1.0, cy]],
            closed=True, facecolor=accent_line_color, edgecolor='none',
            alpha=0.65, transform=ax.transAxes, zorder=5)
        ax.add_patch(triangle)

    plt.tight_layout(pad=0)
    return fig, ax



# ============================================================================
# EASING HELPERS
# ============================================================================
def _ease_out_cubic(t): return 1 - (1 - t) ** 3
def _ease_out_quad(t):  return 1 - (1 - t) ** 2
def _ease_linear(t):    return t
_EASING = {'cubic': _ease_out_cubic, 'quad': _ease_out_quad, 'linear': _ease_linear}

def _typewriter(full_text, progress, start=0.0, end=0.95):
    if not full_text:    return ""
    if progress >= end:  return full_text
    if progress <= start:return ""
    local = (progress - start) / (end - start)
    return full_text[:int(local * len(full_text))]


# ============================================================================
# ANIMATED: SINGLE BAR  (9:16 Reels)
# ============================================================================
def eSingleBarChartAnimateInstagram(
    df_chart, col_dim, col_measure, txt_suptitle, txt_subtitle, txt_label,
    duration=8, fps=30, hold_frames=120,
    output_file="espresso_bar_animated.mp4", easing='cubic',
    tw_suptitle_start=0.0, tw_suptitle_end=0.5,
    tw_subtitle_start=0.5, tw_subtitle_end=0.95,
    pos_text=None, pos_label=-1, num_format="{:.0f}", num_divisor=1,
    bar_height=None, bar_color=None, bar_colors=None,
    hide_left_spine=False, offset_label_x=0,
    min_val=None, max_val=None, factor_limit_x=1.0,
    aspect_ratio=None, label_custom_offset=None,
    value_label_offset_x=None, value_label_offset_y=None,
    suptitle_size=None, subtitle_size=None, label_size=12,
    suptitle_color='#4b2e1a', subtitle_color='#4b2e1a',
    txt_label_color='#857052', tick_label_color='#3c3325',
    value_label_color='#4b2e1a', face_color='#f5f0e6',
    coffee_palette=('#9d8561','#857052','#6c5c43','#544734','#3c3325',
                    '#79664a','#d9d0c1','#0b0a07'),
    suptitle_font_weight='normal', subtitle_font_weight='normal',
    txt_label_font_weight='normal',
    font='DM Mono', suptitle_font=None, subtitle_font=None,
    show_zero_line=False, zero_line_color='#4b2e1a',
    zero_line_style='--', zero_line_width=1.0,
    instagram=True, px_width=1080, px_height=1920, dpi=200,
    sep_index=None, sep_color='#4b2e1a', sep_style='-', sep_width=1.5,
    reference_bands=None, vlines=None, hlines=None,
    # Legacy params — accepted but ignored in v2
    suptitle_y_custom=None, subtitle_pad_custom=None, x_subtitle_offset=None,
):
    label_custom_offset  = _int_keys(label_custom_offset)
    value_label_offset_x = _int_keys(value_label_offset_x)
    value_label_offset_y = _int_keys(value_label_offset_y)

    ease_fn = _EASING.get(easing, _ease_out_cubic)

    # --- Standardized layout (9:16) ---
    fig, ax, L = _setup_chart(
        layout='9x16', face_color=face_color, dpi=dpi,
        plot_left=0.10, plot_right=0.80,
    )
    # Titles start blank for typewriter animation
    sup_obj = fig.text(
        0.5, L['suptitle_y'], "",
        fontsize=suptitle_size or _SUPTITLE_SIZE, color=suptitle_color,
        fontweight=suptitle_font_weight, fontfamily=suptitle_font or _SUPTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    sub_obj = fig.text(
        0.5, L['subtitle_y'], "",
        fontsize=subtitle_size or _SUBTITLE_SIZE, color=subtitle_color,
        fontweight=subtitle_font_weight, fontfamily=subtitle_font or _SUBTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    _add_footnote(fig, txt_label, L,
                  color=txt_label_color, font_weight=txt_label_font_weight)

    if bar_color is None: bar_color = coffee_palette[0]
    dim_vals     = df_chart[col_dim].tolist()
    measure_vals = df_chart[col_measure].tolist()
    n = len(dim_vals)
    if bar_height is None: bar_height = 0.75
    if min_val is None: min_val = float(df_chart[col_measure].min())
    if max_val is None: max_val = float(df_chart[col_measure].max())
    ax.set_xlim(min(min_val * factor_limit_x, 0), max(max_val * factor_limit_x, 0))

    if bar_colors is not None:
        bar_colors = _int_keys(bar_colors)
        if isinstance(bar_colors, dict):
            colors_list = [bar_colors.get(i, bar_color) for i in range(n)]
        else: colors_list = list(bar_colors)
    else: colors_list = [bar_color] * n

    bars = ax.barh(dim_vals, [0]*n, color=colors_list, height=bar_height, zorder=3)
    if reference_bands: add_reference_bands(ax, reference_bands, orientation='vertical')
    if vlines: add_vlines(ax, vlines)
    if hlines: add_hlines(ax, hlines)

    for side in ['top','right','bottom']: ax.spines[side].set_linewidth(0)
    if hide_left_spine: ax.spines['left'].set_linewidth(0)
    else:
        ax.spines['left'].set_linewidth(1.2); ax.spines['left'].set_color(tick_label_color)
        ax.spines['left'].set_zorder(5)
    ax.set_yticks([]); ax.tick_params(axis='y', left=False)
    ax.set_xticks([]); ax.tick_params(axis='x', colors=face_color)

    if show_zero_line:
        ax.axvline(0, color=zero_line_color, linestyle=zero_line_style, linewidth=zero_line_width, zorder=2)

    cat_anns = []
    for idx, patch in enumerate(bars):
        y_center = patch.get_y() + patch.get_height() / 2
        is_pos = measure_vals[idx] >= 0
        cat_extra = label_custom_offset.get(idx, 0) if isinstance(label_custom_offset, dict) else 0
        ha_cat = 'left' if is_pos else 'right'
        off_cat = 8 + offset_label_x + cat_extra if is_pos else -8 - offset_label_x - cat_extra
        ann = ax.annotate(str(dim_vals[idx]), xy=(0, y_center), xytext=(off_cat, 0),
            textcoords='offset points', ha=ha_cat, va='center',
            fontsize=label_size, color=tick_label_color, zorder=6,
            bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color, edgecolor='none', alpha=0.8))
        cat_anns.append(ann)

    val_anns = []
    for idx in range(n):
        y_center = bars[idx].get_y() + bars[idx].get_height() / 2
        is_pos = measure_vals[idx] >= 0
        ha_v = 'left' if is_pos else 'right'
        off_v = 8 if is_pos else -8
        ann = ax.annotate("", xy=(0, y_center), xytext=(off_v, 0),
                          textcoords='offset points', ha=ha_v, va='center',
                          fontsize=label_size, color=value_label_color, zorder=6)
        val_anns.append(ann)

    total_anim   = int(fps * duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)
        sup_obj.set_text(_typewriter(txt_suptitle, progress, tw_suptitle_start, tw_suptitle_end))
        sub_obj.set_text(_typewriter(txt_subtitle, progress, tw_subtitle_start, tw_subtitle_end))
        for idx, bar in enumerate(bars):
            cur = measure_vals[idx] * progress
            bar.set_width(cur)
            y_c = bar.get_y() + bar.get_height() / 2
            x_end = bar.get_x() + bar.get_width()
            is_pos = measure_vals[idx] >= 0
            val = cur / num_divisor
            try:    formatted = num_format.format(val)
            except: formatted = str(val)
            x_extra = 0
            if isinstance(value_label_offset_x, dict): x_extra += value_label_offset_x.get(idx, 0)
            y_extra = 0
            if isinstance(value_label_offset_y, dict): y_extra = value_label_offset_y.get(idx, 0)
            off = 8 + x_extra if is_pos else -8 - x_extra
            val_anns[idx].set_text(formatted)
            val_anns[idx].xy    = (x_end, y_c)
            val_anns[idx].xyann = (off, y_extra)
        return list(bars) + val_anns

    anim   = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000,
                                    extra_args=['-vcodec','libx264','-pix_fmt','yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi, savefig_kwargs={'facecolor': face_color})
    print(f"Saved animated bar chart -> {output_file}")
    return fig, ax



# ============================================================================
# ANIMATED: MULTI-LINE  (9:16 Reels)
# ============================================================================
def eMultiLineChartAnimateInstagram(
    df_chart, col_dim, col_measure_list, txt_suptitle, txt_subtitle, txt_label, pos_text,
    duration=8, fps=30, hold_frames=120,
    output_file="espresso_line_animated.mp4", easing='cubic',
    tw_suptitle_start=0.0, tw_suptitle_end=0.5,
    tw_subtitle_start=0.5, tw_subtitle_end=0.95,
    pos_label=None, num_format="{:.0f}", num_divisor=1,
    x_ticks=None, x_tick_labels=None, tick_color='#4B2E1A', x_tick_size=10,
    aspect_ratio=None, line_colors=None, line_styles=None, line_widths=None, line_labels=None,
    suptitle_color='#4b2e1a', subtitle_color='#4b2e1a', txt_label_color='#857052',
    face_color='#F5F0E6', suptitle_font_weight='normal', suptitle_font=None,
    subtitle_font_weight='normal', subtitle_font=None, txt_label_font_weight='normal',
    show_zero_line=False, zero_line_color='#857052', zero_line_style='--',
    zero_line_width=1.0, zero_line_at=0, px=1080, py=1920, dpi=200,
    suptitle_size=None, subtitle_size=None, label_size=12, bottom_note_size=None,
    y_limits=None, text_offset_y=None,
    shade_between=None, shade_color='#c8b8a8', shade_alpha=0.25, shade_x=None,
    show_y_axis=False, y_ticks=None, y_tick_color='#857052', y_tick_size=10,
    y_num_format=None, show_legend=False, legend_labels_custom=None,
    legend_loc='upper left', legend_font_size=10, legend_text_color='#857052',
    legend_ncol=1, legend_bbox=(0, 1.02), chart_top_margin=0.15,
    label_offset_x=8, label_offset_y=0, point_label_offsets=None,
    reference_bands=None, vlines=None, hlines=None,
    # Legacy params — accepted but ignored in v2
    suptitle_y=None, subtitle_y=None,
):
    ease_fn = _EASING.get(easing, _ease_out_cubic)

    # --- Standardized layout (9:16) ---
    fig, ax, L = _setup_chart(
        layout='9x16', face_color=face_color, dpi=dpi,
        plot_left=0.10, plot_right=0.90,
    )
    sup_obj = fig.text(
        0.5, L['suptitle_y'], "",
        fontsize=suptitle_size or _SUPTITLE_SIZE, color=suptitle_color,
        fontweight=suptitle_font_weight, fontfamily=suptitle_font or _SUPTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    sub_obj = fig.text(
        0.5, L['subtitle_y'], "",
        fontsize=subtitle_size or _SUBTITLE_SIZE, color=subtitle_color,
        fontweight=subtitle_font_weight, fontfamily=subtitle_font or _SUBTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    _add_footnote(fig, txt_label, L,
                  color=txt_label_color, font_weight=txt_label_font_weight,
                  size=bottom_note_size)

    default_colors = ['#9d8561','#857052','#6c5c43','#544734','#3c3325']
    colors = line_colors  if line_colors  is not None else default_colors
    styles = line_styles  if line_styles  is not None else ['-']  * len(col_measure_list)
    widths = line_widths  if line_widths  is not None else [0.9] * len(col_measure_list)
    labels = line_labels  if line_labels  is not None else list(col_measure_list)
    def _pad(lst):
        if len(lst) < len(col_measure_list):
            return (lst * (len(col_measure_list) // len(lst) + 1))[:len(col_measure_list)]
        return lst
    colors, styles, widths, labels = _pad(colors), _pad(styles), _pad(widths), _pad(labels)

    if reference_bands: add_reference_bands(ax, reference_bands, orientation='horizontal')
    if vlines: add_vlines(ax, vlines)
    if hlines: add_hlines(ax, hlines)

    for side in ['top','right','bottom']: ax.spines[side].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='x', colors=tick_color, labelsize=x_tick_size)

    x = df_chart[col_dim]
    n_rows = len(df_chart)
    x_idx  = list(range(n_rows))
    ax.set_xticks([x_idx[0], x_idx[-1]])
    ax.set_xticklabels([str(x.iloc[0]), str(x.iloc[-1])])

    if show_y_axis:
        if y_ticks is not None: ax.set_yticks(y_ticks)
        fmt = y_num_format if y_num_format else num_format
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt.format(v / num_divisor)))
        ax.tick_params(axis='y', labelleft=True, colors=y_tick_color,
                       labelsize=y_tick_size, length=4, width=0.6)
        ax.spines['left'].set_visible(True); ax.spines['left'].set_linewidth(0.6)
        ax.spines['left'].set_color(y_tick_color)
    else:
        ax.set_yticks([])

    if y_limits is not None:
        ax.set_ylim(y_limits)
    else:
        all_v = [v for c in col_measure_list for v in df_chart[c].tolist()]
        m = (max(all_v) - min(all_v)) * 0.1
        ax.set_ylim(min(all_v) - m, max(all_v) + m)

    x_vals = x.tolist()
    xm = len(x_vals) * 0.02
    ax.set_xlim(-xm, len(x_vals) - 1 + xm)

    if show_zero_line:
        ax.axhline(zero_line_at, color=zero_line_color, linestyle=zero_line_style,
                   linewidth=zero_line_width, zorder=8, label='_nolegend_')
    if aspect_ratio is not None: ax.set_box_aspect(aspect_ratio)

    line_objects, dot_objects = [], []
    moving_labels = []  # value label that tracks the leading edge
    for idx in range(len(col_measure_list)):
        ln, = ax.plot([], [], color=colors[idx], linestyle=styles[idx], linewidth=widths[idx], zorder=9)
        line_objects.append(ln)
        dt, = ax.plot([], [], 'o', color=colors[idx], markersize=5, zorder=10, linewidth=0, label='_nolegend_')
        dot_objects.append(dt)
        # Moving value label: shows current interpolated value at the line tip
        ml = ax.annotate('', xy=(0, 0), xytext=(8, 6), textcoords='offset points',
                         ha='left', va='bottom', color=colors[idx],
                         fontsize=label_size, fontweight='bold', zorder=12,
                         bbox=dict(boxstyle='square,pad=0.15', facecolor=face_color,
                                   edgecolor=face_color, alpha=0.85))
        ml.set_visible(False)
        moving_labels.append(ml)

    if show_legend:
        leg_labels = legend_labels_custom if legend_labels_custom is not None else labels
        leg = ax.legend(leg_labels, loc=legend_loc, bbox_to_anchor=legend_bbox,
                        ncol=legend_ncol, frameon=False, fontsize=legend_font_size)
        if legend_text_color is not None:
            for t in leg.get_texts(): t.set_color(legend_text_color)

    value_targets = []
    for pos in (pos_text or []):
        p = pos if pos >= 0 else n_rows + pos
        if 0 <= p < n_rows:
            for idx, col in enumerate(col_measure_list):
                raw = df_chart[col].iloc[p]
                val = raw / num_divisor
                try:    fmt_s = num_format.format(val)
                except: fmt_s = str(val)
                oy = (text_offset_y[idx] if isinstance(text_offset_y, (list, tuple))
                      else (text_offset_y or 0))
                if isinstance(point_label_offsets, dict):
                    ox_pt, oy_pt = point_label_offsets.get((p, idx), (0, 0))
                else:
                    ox_pt, oy_pt = 0, 0
                value_targets.append(dict(pos=p, idx=idx, formatted=fmt_s,
                                          x=float(p), y=raw + oy + oy_pt,
                                          ox=ox_pt, color=colors[idx]))

    val_objs = []
    for vt in value_targets:
        t = ax.annotate('', xy=(vt['x'], vt['y']),
                         xytext=(vt.get('ox', 0), 0), textcoords='offset points',
                         ha='center', va='bottom',
                         color=vt['color'], fontsize=label_size, zorder=11,
                         bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                                   edgecolor=face_color, alpha=0.8))
        t.set_visible(False)
        val_objs.append(t)

    shade_patch = None
    if shade_between is not None:
        cl, ch = shade_between
        y1, y2 = df_chart[cl], df_chart[ch]
        if shade_x is None:
            shade_patch = ax.fill_between(x, y1, y2, color=shade_color, alpha=shade_alpha, zorder=1)
        else:
            xs, xe = shade_x; mask = (x >= xs) & (x <= xe)
            shade_patch = ax.fill_between(x[mask], y1[mask], y2[mask],
                                          color=shade_color, alpha=shade_alpha, zorder=1)
        shade_patch.set_visible(False)

    total_anim   = int(fps * duration)
    total_frames = total_anim + hold_frames
    x_arr        = np.arange(n_rows, dtype=float)

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)
        sup_obj.set_text(_typewriter(txt_suptitle, progress, tw_suptitle_start, tw_suptitle_end))
        sub_obj.set_text(_typewriter(txt_subtitle,  progress, tw_subtitle_start,  tw_subtitle_end))
        reveal = progress * n_rows
        for li, col in enumerate(col_measure_list):
            y_all = df_chart[col].values.astype(float)
            full  = int(reveal); frac = reveal - full
            if full >= n_rows:
                line_objects[li].set_data(x_arr, y_all)
                dot_objects[li].set_data([x_arr[-1]], [y_all[-1]])
                tip_x, tip_y = x_arr[-1], y_all[-1]
            elif full == 0:
                line_objects[li].set_data([x_arr[0]], [y_all[0]])
                dot_objects[li].set_data([x_arr[0]], [y_all[0]])
                tip_x, tip_y = x_arr[0], y_all[0]
            else:
                xs2 = list(x_arr[:full]); ys2 = list(y_all[:full])
                if full < n_rows:
                    xs2.append(x_arr[full-1] + frac*(x_arr[full]-x_arr[full-1]))
                    ys2.append(y_all[full-1] + frac*(y_all[full]-y_all[full-1]))
                line_objects[li].set_data(xs2, ys2)
                dot_objects[li].set_data([xs2[-1]], [ys2[-1]])
                tip_x, tip_y = xs2[-1], ys2[-1]
            # Update moving value label at the leading edge
            if progress > 0.01:
                val = tip_y / num_divisor
                try:    fmt_s = num_format.format(val)
                except: fmt_s = str(val)
                moving_labels[li].set_visible(True)
                moving_labels[li].set_text(fmt_s)
                moving_labels[li].xy = (tip_x, tip_y)
            else:
                moving_labels[li].set_visible(False)
        # Fixed position value labels — hide when moving labels are active
        # (moving labels already show the value at the leading edge)
        if not moving_labels:
            for vi, vt in enumerate(value_targets):
                if vt['pos'] < reveal - 0.5:
                    val_objs[vi].set_visible(True)
                    val_objs[vi].set_text(vt['formatted'])
                    val_objs[vi].xy = (vt['x'], vt['y'])
                else:
                    val_objs[vi].set_visible(False)
        if shade_patch is not None:
            shade_patch.set_visible(progress >= 0.99)
        return line_objects + dot_objects + moving_labels + val_objs

    anim   = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000,
                                    extra_args=['-vcodec','libx264','-pix_fmt','yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi, savefig_kwargs={'facecolor': face_color})
    print(f"Saved animated line chart -> {output_file}")
    return fig, ax


# ============================================================================
# ANIMATED: STEM  (9:16 Reels)
# ============================================================================
def eStemChartAnimateInstagram(
    df_chart, col_dim, col_measure_a,
    duration=8, fps=30, hold_frames=120,
    output_file="espresso_stem_animated.mp4", easing='cubic',
    tw_suptitle_start=0.0, tw_suptitle_end=0.5,
    tw_subtitle_start=0.5, tw_subtitle_end=0.95,
    col_measure_b=None, col_category_pos=None,
    txt_suptitle="", txt_subtitle="", txt_label="",
    num_format="{:.0f}", num_divisor=1, offset=0.1, x_tick_label_y_offset=0,
    marker_size=4, line_width=0.8,
    suptitle_color="#4b2e1a", subtitle_color="#4b2e1a",
    axis_label_color="#79664a", tick_label_color="#3c3325",
    face_color="#F5F0E6", color_a="#a58e6c", color_b="#573D09",
    year_label_a=None, year_label_b=None,
    label_a_offset_x=1, label_b_offset_x=1, label_a_offset_y=1, label_b_offset_y=1,
    instagram=True, px_width=1080, px_height=1920, dpi=200,
    suptitle_size=None, subtitle_size=None, label_size=12,
    aspect_ratio=None,
    rotate_labels=False, xtick_align_ha="center", xtick_align_va="top",
    value_label_offset_pts=6, value_label_offset_y=None, value_label_offset_x=None,
    value_label_custom_offset=None,
    x_axis_line_width=0.8, x_axis_line_color="#857052",
    line_format_a="--", line_format_b="--",
    show_legend=False, legend_labels=None, legend_loc='upper right',
    legend_font_size=10, legend_frame=False, legend_text_color='#3c3325',
    legend_bbox_to_anchor=None, y_min=None, y_max=None,
    font='DM Mono', suptitle_font=None, subtitle_font=None,
    reference_bands=None, vlines=None, hlines=None,
    # Legacy params
    suptitle_y=None, subtitle_y=None, subtitle_pad=None, labelpad=None,
):
    value_label_offset_y      = _int_keys(value_label_offset_y)
    value_label_offset_x      = _int_keys(value_label_offset_x)
    value_label_custom_offset = _int_keys(value_label_custom_offset)

    ease_fn = _EASING.get(easing, _ease_out_cubic)

    # --- Standardized layout (9:16) ---
    fig, ax, L = _setup_chart(
        layout='9x16', face_color=face_color, dpi=dpi,
        plot_left=0.12, plot_right=0.92,
    )
    sup_obj = fig.text(
        0.5, L['suptitle_y'], "",
        fontsize=suptitle_size or _SUPTITLE_SIZE, color=suptitle_color,
        fontweight="medium", fontfamily=suptitle_font or _SUPTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    sub_obj = fig.text(
        0.5, L['subtitle_y'], "",
        fontsize=subtitle_size or _SUBTITLE_SIZE, color=subtitle_color,
        fontweight="light", fontfamily=subtitle_font or _SUBTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    _add_footnote(fig, txt_label, L, color=axis_label_color)

    xpos = (np.arange(len(df_chart)) if col_category_pos is None
            else np.asarray(df_chart[col_category_pos]))
    cats = df_chart[col_dim].tolist()
    n    = len(df_chart)
    y_a_final = df_chart[col_measure_a].to_numpy(dtype=float) / num_divisor
    y_b_final = None
    if col_measure_b is not None:
        y_b_final = df_chart[col_measure_b].to_numpy(dtype=float) / num_divisor

    for side in ["top","right","left","bottom"]: ax.spines[side].set_linewidth(0)
    ax.axhline(0, color=x_axis_line_color, linewidth=x_axis_line_width)
    if reference_bands: add_reference_bands(ax, reference_bands, orientation='horizontal')
    if vlines: add_vlines(ax, vlines)
    if hlines: add_hlines(ax, hlines)

    all_v = list(y_a_final) + (list(y_b_final) if y_b_final is not None else [])
    dmin, dmax = min(all_v), max(all_v)
    margin = (dmax - dmin) * 0.15
    ax.set_ylim(y_min if y_min is not None else (dmin - margin if dmin < 0 else -margin*0.5),
                y_max if y_max is not None else dmax + margin)

    ax.set_xticks(xpos)
    ax.set_xticklabels([])  # hide default tick labels
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])

    # Place category labels manually at y=0 in data coordinates
    label_y_data = 0 + x_tick_label_y_offset
    for idx, (xp, cat) in enumerate(zip(xpos, cats)):
        ax.text(xp, label_y_data, cat, color=tick_label_color,
                fontsize=label_size, ha=xtick_align_ha, va=xtick_align_va,
                rotation=90 if rotate_labels else 0,
                bbox=dict(boxstyle="square,pad=0.1", facecolor="white",
                          edgecolor="white", alpha=0.7),
                transform=ax.transData, clip_on=False)

    def _resolve_offsets(i, val, g_y, per_y, per_x, legacy):
        base_y  = g_y if val >= 0 else -g_y
        extra_y = 0
        if per_y and i in per_y:         extra_y = per_y[i]
        elif legacy and i in legacy:     extra_y = legacy[i]
        extra_x = per_x.get(i, 0) if per_x else 0
        return base_y + extra_y, extra_x

    stem_a, mark_a, lbl_a = [], [], []
    stem_b, mark_b, lbl_b = [], [], []
    for i in range(n):
        ln, = ax.plot([xpos[i]-offset]*2, [0,0], line_format_a, color=color_a, linewidth=line_width, zorder=1)
        stem_a.append(ln)
        dt, = ax.plot(xpos[i]-offset, 0, 'o', color=color_a, markersize=marker_size, linewidth=line_width, zorder=2)
        mark_a.append(dt)
        y_off, x_off = _resolve_offsets(i, y_a_final[i], value_label_offset_pts,
                                         value_label_offset_y, value_label_offset_x, value_label_custom_offset)
        t = ax.annotate("", xy=(xpos[i]-offset, 0), xytext=(x_off, y_off),
                        textcoords="offset points", ha="center",
                        va="bottom" if y_a_final[i] >= 0 else "top",
                        fontsize=label_size, color=color_a,
                        bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="white", alpha=0.7), zorder=10)
        lbl_a.append(t)
    if y_b_final is not None:
        for i in range(n):
            ln, = ax.plot([xpos[i]+offset]*2, [0,0], line_format_b, color=color_b, linewidth=line_width, zorder=1)
            stem_b.append(ln)
            dt, = ax.plot(xpos[i]+offset, 0, 'o', color=color_b, markersize=marker_size, linewidth=line_width, zorder=2)
            mark_b.append(dt)
            y_off, x_off = _resolve_offsets(i, y_b_final[i], value_label_offset_pts,
                                             value_label_offset_y, value_label_offset_x, value_label_custom_offset)
            t = ax.annotate("", xy=(xpos[i]+offset, 0), xytext=(x_off, y_off),
                            textcoords="offset points", ha="center",
                            va="bottom" if y_b_final[i] >= 0 else "top",
                            fontsize=label_size, color=color_b,
                            bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="white", alpha=0.7), zorder=10)
            lbl_b.append(t)
    if aspect_ratio is not None: ax.set_box_aspect(aspect_ratio)

    total_anim   = int(fps * duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)
        sup_obj.set_text(_typewriter(txt_suptitle, progress, tw_suptitle_start, tw_suptitle_end))
        sub_obj.set_text(_typewriter(txt_subtitle,  progress, tw_subtitle_start,  tw_subtitle_end))
        for i in range(n):
            ca = y_a_final[i] * progress
            stem_a[i].set_ydata([0, ca]); mark_a[i].set_ydata([ca])
            lbl_a[i].set_text(num_format.format(ca)); lbl_a[i].xy = (xpos[i]-offset, ca)
            if y_b_final is not None:
                cb = y_b_final[i] * progress
                stem_b[i].set_ydata([0, cb]); mark_b[i].set_ydata([cb])
                lbl_b[i].set_text(num_format.format(cb)); lbl_b[i].xy = (xpos[i]+offset, cb)
        return stem_a + mark_a + lbl_a + stem_b + mark_b + lbl_b

    anim   = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000,
                                    extra_args=['-vcodec','libx264','-pix_fmt','yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi, savefig_kwargs={'facecolor': face_color})
    print(f"Saved animated stem chart -> {output_file}")
    return fig, ax



# ============================================================================
# ANIMATED: DONUT  (9:16 Reels)
# ============================================================================
def eDonutChartAnimateInstagram(
    df_chart, col_value, duration=8, fps=30, hold_frames=120,
    output_file="espresso_donut_animated.mp4", easing='cubic',
    tw_suptitle_start=0.0, tw_suptitle_end=0.5, tw_subtitle_start=0.5, tw_subtitle_end=0.95,
    col_label=None, col_inner=None, txt_suptitle="", txt_subtitle="", txt_label="",
    num_format="{:.0f}%", num_divisor=1,
    radius_outer=0.9, inner_radius=None, wedge_width=0.4,
    radius_inner=0.65, wedge_width_inner=None,
    labeldistance=1.05, pctdistance_outer=0.8, pctdistance_inner=0.75,
    show_pct=True, autopct_outer=True, autopct_inner=True,
    colors=None, pct_colors=None, label_colors=None,
    center_text=None, center_text_color="#4b2e1a", center_text_size=12, center_text_weight="normal",
    suptitle_color='#4b2e1a', subtitle_color='#4b2e1a', txt_label_color='#857052',
    face_color='#F5F0E6', suptitle_font_weight='medium', subtitle_font_weight='light',
    txt_label_font_weight='light', suptitle_size=None, subtitle_size=None,
    label_size=10, bottom_note_size=None, font='DM Mono',
    suptitle_font=None, subtitle_font=None,
    figsize=(8,8), dpi=200, px=1080, instagram=True, instagram_format='9x16',
    # Legacy params
    suptitle_y=None, subtitle_y=None, label_y=None,
):
    ease_fn = _EASING.get(easing, _ease_out_cubic)

    # --- Standardized layout (9:16) ---
    fig, ax, L = _setup_chart(
        layout='9x16', face_color=face_color, dpi=dpi,
        plot_left=0.05, plot_right=0.95,
    )
    ax.set_aspect("equal", adjustable="box")

    sup_obj = fig.text(
        0.5, L['suptitle_y'], "",
        fontsize=suptitle_size or _SUPTITLE_SIZE, color=suptitle_color,
        weight=suptitle_font_weight, fontfamily=suptitle_font or _SUPTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    sub_obj = fig.text(
        0.5, L['subtitle_y'], "",
        fontsize=subtitle_size or _SUBTITLE_SIZE, color=subtitle_color,
        weight=subtitle_font_weight, fontfamily=subtitle_font or _SUBTITLE_FONT,
        ha='center', va='top', linespacing=1.2)
    if txt_label:
        _add_footnote(fig, txt_label, L,
                      color=txt_label_color, font_weight=txt_label_font_weight,
                      size=bottom_note_size)

    default_colors = ['#d9d0c1','#79664a','#9d8561','#857052','#6c5c43','#544734','#3c3325']
    if colors is None: colors = default_colors
    outer_band = radius_outer - inner_radius if inner_radius is not None else wedge_width
    inner_band = wedge_width_inner if wedge_width_inner is not None else outer_band

    for side in ['top','right','left','bottom']: ax.spines[side].set_linewidth(0)

    values     = (df_chart[col_value] / num_divisor).values.astype(float)
    total      = values.sum()
    fractions  = values / total
    angles_deg = fractions * 360.0
    start_angle = 90.0
    labels_data = (df_chart[col_label].astype(str).tolist() if col_label is not None
                   else [None]*len(values))
    n_wedges = len(values)
    def fmt_pct(pct):
        try:    return num_format.format(pct)
        except: return f"{pct:.0f}%"

    total_anim   = int(fps * duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        ax.clear(); ax.set_facecolor(face_color); ax.set_aspect("equal", adjustable="box")
        for side in ['top','right','left','bottom']: ax.spines[side].set_linewidth(0)
        ax.set_xticks([]); ax.set_yticks([])
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)
        sup_obj.set_text(_typewriter(txt_suptitle, progress, tw_suptitle_start, tw_suptitle_end))
        sub_obj.set_text(_typewriter(txt_subtitle,  progress, tw_subtitle_start,  tw_subtitle_end))
        cur_start = start_angle; drawn = []
        for i in range(n_wedges):
            wa = angles_deg[i] * progress
            if wa < 0.5: cur_start -= wa; continue
            wedge = mpatches.Wedge(center=(0,0), r=radius_outer, theta1=cur_start-wa, theta2=cur_start,
                                   width=outer_band, facecolor=colors[i%len(colors)],
                                   edgecolor=face_color, linewidth=1.5, zorder=3)
            ax.add_patch(wedge); drawn.append(wedge)
            mid_rad = np.deg2rad(cur_start - wa/2)
            if labels_data[i] is not None and progress > 0.5:
                lr = radius_outer * labeldistance
                lx, ly = lr*np.cos(mid_rad), lr*np.sin(mid_rad)
                ha  = 'left' if lx >= 0 else 'right'
                lc  = (label_colors[i] if label_colors and i < len(label_colors) else '#4b2e1a')
                ax.text(lx, ly, labels_data[i], ha=ha, va='center', fontsize=label_size, color=lc)
            if show_pct and autopct_outer and progress > 0.3:
                pr  = radius_outer - outer_band/2
                px_ = pr*np.cos(mid_rad)*pctdistance_outer/0.8
                py_ = pr*np.sin(mid_rad)*pctdistance_outer/0.8
                pc  = (pct_colors[i] if pct_colors and i < len(pct_colors) else '#4b2e1a')
                ax.text(px_, py_, fmt_pct(fractions[i]*100), ha='center', va='center', fontsize=label_size, color=pc)
            cur_start -= wa
        if center_text:
            ax.text(0, 0, center_text, ha="center", va="center", fontsize=center_text_size,
                    color=center_text_color, fontweight=center_text_weight, linespacing=1.2)
        lim = radius_outer * 1.4
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
        return drawn

    anim   = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000,
                                    extra_args=['-vcodec','libx264','-pix_fmt','yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi, savefig_kwargs={'facecolor': face_color})
    print(f"Saved animated donut chart -> {output_file}")
    return fig, ax


# ============================================================================
# ANIMATED: COVER TILE  (9:16 Reels)
# ============================================================================
def eCoverTileAnimateInstagram(
    txt_suptitle, txt_subtitle, txt_label="",
    duration=3.5, hold_duration=2.0, fps=30,
    output_file="espresso_cover_animated.mp4", easing='cubic',
    # Legacy typewriter params (ignored, kept for backward compat)
    tw_suptitle_start=0.0, tw_suptitle_end=0, tw_subtitle_start=0, tw_subtitle_end=0,
    # New cover-specific parameters
    txt_eyebrow="", txt_issue="", txt_unit=None, txt_context=None,
    eyebrow_y=0.78, eyebrow_size=9, eyebrow_color='#9e8b76',
    unit_size=14, unit_color=None,
    context_y=0.10, context_size=12, context_color='#79664a',
    issue_size=8, descender_pad=0.015,
    show_corner_mark=False, corner_mark_size=28,
    suptitle_font_style='italic',
    # Count-up animation
    count_up=True,
    count_format=None,
    # Existing parameters (some defaults updated)
    suptitle_color='#2A1F14', suptitle_font='Playfair Display', suptitle_font_weight='bold',
    suptitle_size=86, suptitle_y=0.6,
    subtitle_color='#2A1F14', subtitle_font='Source Serif 4', subtitle_font_weight='normal',
    subtitle_size=16, subtitle_y=0.19,
    txt_label_color='#CDAF7B', txt_label_font='DM Mono', txt_label_font_weight='light',
    label_size=8, label_y=0.038,
    face_color='#F5F0E6', px_width=1080, px_height=1920, dpi=200,
    show_accent_line=True, accent_line_color='#3F5B83', accent_line_width=4,
    accent_line_y=0.29, accent_line_length=0.15,
    # Legacy params (ignored)
    accent_line_start=0.40, accent_line_end=0.65,
):
    """Animated number-led cover tile with editorial reveal sequence.

    The hero number counts up from 0 to the target value (when count_up=True).
    Uses alpha fade + subtle drift (not typewriter). Each element appears
    in a staggered sequence over the animation duration.

    Parameters
    ----------
    count_up : bool
        If True, the hero number animates from 0 to its final value.
        The function parses prefix ('+', '$') and suffix ('%', 'M', etc.)
        from txt_suptitle automatically.
    count_format : str or None
        Format string for the counting number. If None, auto-detected
        from txt_suptitle (e.g. "14.29" uses "{:.2f}", "53" uses "{:.0f}").
    """
    import re

    rule_color = '#C8BBA8'
    ease_fn = _EASING.get(easing, _ease_out_cubic)
    plt.rcdefaults(); plt.rcParams['font.family'] = 'DM Mono'
    plt.rcParams["savefig.bbox"] = "standard"
    figsize = (px_width / dpi, px_height / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.patch.set_facecolor(face_color)
    fig.patch.set_edgecolor(face_color)
    fig.patch.set_linewidth(0)
    fig.patch.set_alpha(1)

    # Parse hero number for count-up animation
    # Extract prefix (non-numeric start), numeric core, suffix (non-numeric end)
    # Handles: "+28", "53", "14.29", "$11.4T", "27", "14.29M", "+50%"
    num_prefix, num_value, num_suffix, num_decimals = "", 0.0, "", 0
    if count_up and txt_suptitle:
        # Split on newlines, count up only the first line
        first_line = txt_suptitle.split('\n')[0]
        remaining_lines = '\n'.join(txt_suptitle.split('\n')[1:])
        m = re.match(r'^([^0-9]*?)([\d,.]+)(.*?)$', first_line)
        if m:
            num_prefix = m.group(1)
            num_str = m.group(2).replace(',', '')
            num_suffix = m.group(3)
            num_value = float(num_str)
            num_decimals = len(num_str.split('.')[1]) if '.' in num_str else 0
            if count_format is None:
                if num_decimals > 0:
                    count_format = f"{{:,.{num_decimals}f}}"
                else:
                    count_format = "{:,.0f}"
        else:
            count_up = False  # can't parse, fall back to fade only

    def _ep(gp, start, end):
        if gp <= start: return 0.0
        if gp >= end: return 1.0
        return _ease_out_cubic((gp - start) / (end - start))

    def _format_number(progress):
        """Format the hero number at a given count-up progress (0-1)."""
        if not count_up:
            return txt_suptitle
        current = num_value * progress
        formatted = count_format.format(current)
        result = f"{num_prefix}{formatted}{num_suffix}"
        if remaining_lines:
            result += '\n' + remaining_lines
        return result

    # Create all elements.
    # Chrome (rules, corners, eyebrow, source) + hero number visible from frame 1.
    # Accent line expands, insight/context/unit fade in for motion.

    # Top rule — visible immediately
    top_rule, = ax.plot([0.08, 0.92], [0.895, 0.895], color=rule_color, linewidth=0.6,
                        transform=ax.transAxes, zorder=3)
    # Corners — visible immediately
    issue_obj = ax.text(0.08, 0.925, txt_issue if txt_issue else "",
                        fontfamily='DM Mono', fontsize=issue_size, color='#9e8b76',
                        ha='left', va='center', transform=ax.transAxes, alpha=1, zorder=4)
    brand_obj = ax.text(0.92, 0.925, "Espresso Charts", fontfamily='DM Mono',
                        fontsize=issue_size, color='#9e8b76', ha='right', va='center',
                        transform=ax.transAxes, alpha=1, zorder=4)
    # Eyebrow — visible immediately
    eyebrow_obj = ax.text(0.5, eyebrow_y, txt_eyebrow or "", fontfamily='DM Mono',
                          fontsize=eyebrow_size, color=eyebrow_color,
                          ha='center', va='center', transform=ax.transAxes, alpha=1, zorder=4)
    # Hero number — final value from frame 1
    number_obj = ax.text(0.5, suptitle_y, txt_suptitle, fontsize=suptitle_size,
                         color=suptitle_color, ha='center', va='center',
                         fontweight=suptitle_font_weight, fontstyle=suptitle_font_style,
                         fontfamily=suptitle_font, linespacing=0.9,
                         transform=ax.transAxes, alpha=1, zorder=4)
    # Unit — fades in
    uc = unit_color or suptitle_color
    unit_obj = ax.text(0.5, suptitle_y - 0.12, txt_unit or "", fontfamily=suptitle_font,
                       fontsize=unit_size, fontstyle='italic', fontweight='normal',
                       color=uc, ha='center', va='top',
                       transform=ax.transAxes, alpha=0, zorder=4)
    # Accent line — expands from center
    accent_obj, = ax.plot([], [], color=accent_line_color, linewidth=accent_line_width,
                          solid_capstyle='round', transform=ax.transAxes, zorder=3)
    # Insight — fades in with drift
    insight_obj = ax.text(0.5, subtitle_y, txt_subtitle, fontsize=subtitle_size,
                          color=subtitle_color, ha='center', va='center',
                          fontweight='semibold', fontstyle='italic',
                          fontfamily=suptitle_font, linespacing=1.35,
                          transform=ax.transAxes, alpha=0, zorder=4)
    # Context — fades in with drift
    context_obj = ax.text(0.5, context_y, txt_context or "", fontfamily=subtitle_font,
                          fontsize=context_size, fontstyle='italic', fontweight='light',
                          color=context_color, ha='center', va='center',
                          linespacing=1.5, transform=ax.transAxes, alpha=0, zorder=4)
    # Bottom rule — visible immediately
    bot_rule, = ax.plot([0.08, 0.92], [0.07, 0.07], color=rule_color, linewidth=0.6,
                        transform=ax.transAxes, zorder=3)
    # Source — visible immediately
    source_obj = ax.text(0.5, label_y, txt_label or "", fontfamily='DM Mono',
                         fontsize=label_size, color=txt_label_color,
                         ha='center', va='center', fontweight=txt_label_font_weight,
                         transform=ax.transAxes, alpha=1, zorder=4)
    # Corner mark — visible immediately
    corner_patch = None
    if show_corner_mark:
        fig_w_pts = fig.get_size_inches()[0] * fig.dpi
        fig_h_pts = fig.get_size_inches()[1] * fig.dpi
        cx = corner_mark_size / fig_w_pts
        cy = corner_mark_size / fig_h_pts
        corner_patch = mpatches.Polygon(
            [[1.0 - cx, 0.0], [1.0, 0.0], [1.0, cy]],
            closed=True, facecolor=accent_line_color, edgecolor='none',
            alpha=0.65, transform=ax.transAxes, zorder=5)
        ax.add_patch(corner_patch)

    total_anim = int(fps * duration)
    hold_frames = int(fps * hold_duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        # Frame 0: complete cover with final number (Instagram thumbnail)
        if frame == 0:
            number_obj.set_text(txt_suptitle)
            number_obj.set_alpha(1)
            if txt_unit:
                unit_obj.set_alpha(0.75)
                try:
                    renderer = fig.canvas.get_renderer()
                    bb = number_obj.get_window_extent(renderer=renderer)
                    bb_ax = bb.transformed(ax.transAxes.inverted())
                    unit_obj.set_position((0.5, bb_ax.y0 - descender_pad))
                except Exception:
                    unit_obj.set_position((0.5, suptitle_y - 0.12))
            if show_accent_line:
                ah = accent_line_length / 2
                accent_obj.set_data([0.5 - ah, 0.5 + ah], [accent_line_y, accent_line_y])
            insight_obj.set_alpha(1)
            insight_obj.set_position((0.5, subtitle_y))
            if txt_context:
                context_obj.set_alpha(1)
                context_obj.set_position((0.5, context_y))
            return [number_obj, unit_obj, accent_obj, insight_obj, context_obj]

        # Frame 1+: count up from 0
        p = 1.0 if frame >= total_anim else frame / total_anim

        # Number: count up (0.0 - 0.55)
        nr = _ep(p, 0.0, 0.55)
        if count_up:
            number_obj.set_text(_format_number(nr))
        number_obj.set_alpha(1)

        # Unit: fade in (0.40 - 0.60)
        if txt_unit:
            ur = _ep(p, 0.40, 0.60)
            unit_obj.set_alpha(ur * 0.75)
            try:
                renderer = fig.canvas.get_renderer()
                bb = number_obj.get_window_extent(renderer=renderer)
                bb_ax = bb.transformed(ax.transAxes.inverted())
                uy = bb_ax.y0 - descender_pad
            except Exception:
                uy = suptitle_y - 0.12
            unit_obj.set_position((0.5, uy))

        # Accent line: expand from center (0.15 - 0.35)
        if show_accent_line:
            al = _ep(p, 0.15, 0.35)
            if al > 0:
                ah = (accent_line_length / 2) * al
                accent_obj.set_data([0.5 - ah, 0.5 + ah], [accent_line_y, accent_line_y])
            else:
                accent_obj.set_data([], [])

        # Insight: fade + drift up (0.45 - 0.70)
        ir = _ep(p, 0.45, 0.70)
        insight_obj.set_alpha(ir)
        insight_obj.set_position((0.5, subtitle_y + 0.010 * (1 - ir)))

        # Context: fade + drift up (0.60 - 0.80)
        if txt_context:
            xr = _ep(p, 0.60, 0.80)
            context_obj.set_alpha(xr)
            context_obj.set_position((0.5, context_y + 0.008 * (1 - xr)))

        return [number_obj, unit_obj, accent_obj, insight_obj, context_obj]

    anim = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000,
                                    extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi,
              savefig_kwargs={'facecolor': face_color, 'pad_inches': 0})
    print(f"Saved animated cover tile -> {output_file}  ({duration+hold_duration:.1f}s @ {fps}fps)")
    return fig, ax


# ============================================================================
# MP4 CONCATENATION
# ============================================================================
def eConcatenateMP4(input_files, output_file="espresso_reel.mp4"):
    if len(input_files) < 2: raise ValueError("Need at least 2 files to concatenate.")
    for f in input_files:
        if not os.path.isfile(f): raise FileNotFoundError(f"File not found: {f}")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, dir='.') as tmp:
        for f in input_files: tmp.write(f"file '{os.path.abspath(f)}'\n")
        list_path = tmp.name
    try:
        cmd = ['ffmpeg','-y','-f','concat','-safe','0','-i',list_path,'-c','copy',output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            cmd_re = ['ffmpeg','-y','-f','concat','-safe','0','-i',list_path,
                      '-vcodec','libx264','-pix_fmt','yuv420p','-crf','18',output_file]
            result = subprocess.run(cmd_re, capture_output=True, text=True)
            if result.returncode != 0: raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")
    finally:
        os.unlink(list_path)
    print(f"Concatenated {len(input_files)} clips -> {output_file}")
    return output_file


# ============================================================================
# AUDIO PIPELINE (ElevenLabs)
# ============================================================================
VOICES = {
    "adam": "pNInz6obpgDQGcFmaJgB", "rachel": "21m00Tcm4TlvDq8ikWAM",
    "clyde": "2EiwWnXFnvU5JabPnv8n", "domi": "AZnzlk1XvdvUeBnXmlld",
    "bella": "EXAVITQu4vr4xnSDxMaL", "antoni": "ErXwobaYiN019PkySvjV",
    "josh": "TxGEqnHWrfWFTfGW9XjX", "sam": "yoZ06aMxZJJ28mfd3POQ",
    "george": "JBFqnCBsd6RMkjVDRZzb",
}
TTS_MODELS = {
    "v3": "eleven_v3", "multilingual_v2": "eleven_multilingual_v2",
    "turbo_v2.5": "eleven_turbo_v2_5", "flash_v2.5": "eleven_flash_v2_5",
}
MUSIC_PRESETS = {
    "lofi_coffee": "Gentle lo-fi hip-hop instrumental, soft Rhodes piano chords, warm vinyl crackle, slow tempo 75 BPM, relaxed coffee shop vibe, no vocals, ambient and minimal",
    "editorial_minimal": "Minimal ambient instrumental, soft piano with subtle synth pads, calm and professional tone, 80 BPM, no percussion, suitable as background for data journalism",
    "upbeat_data": "Light upbeat instrumental, acoustic guitar and soft percussion, positive and curious mood, 100 BPM, clean and modern, no vocals",
    "morning_news": "Warm jazz instrumental, brushed drums, upright bass walking line, muted trumpet melody, 90 BPM, morning radio feel, no vocals",
}

def eGetDuration(filepath):
    cmd = ['ffprobe','-v','quiet','-print_format','json','-show_format', filepath]
    r   = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"ffprobe failed on {filepath}: {r.stderr}")
    return float(json.loads(r.stdout)['format']['duration'])

def eListVoices(api_key, limit=20):
    r = requests.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": api_key})
    r.raise_for_status()
    voices = r.json().get("voices", [])
    print(f"{'Name':<20} {'Voice ID':<28} {'Labels'}")
    print("-" * 76)
    for v in voices[:limit]:
        labels = v.get("labels", {}); lbl = ", ".join(f"{k}={val}" for k, val in labels.items()) if labels else ""
        print(f"{v['name']:<20} {v['voice_id']:<28} {lbl}")
    print(f"\nShowing {min(limit,len(voices))} of {len(voices)} voices")
    return voices

def eGenerateVoiceover(
    text, api_key, output_file="voiceover.mp3", voice_id=None, voice_name="george",
    model="multilingual_v2", stability=0.50, similarity_boost=0.75, style=0.0,
    speed=1.0, output_format="mp3_44100_128", language=None,
):
    if voice_id is None:
        voice_id = VOICES.get(voice_name.lower())
        if voice_id is None: raise ValueError(f"Unknown voice_name '{voice_name}'. Use one of {list(VOICES.keys())}")
    model_id = TTS_MODELS.get(model, model)
    url      = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers  = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
    payload  = {"text": text, "model_id": model_id, "output_format": output_format,
                "voice_settings": {"stability": stability, "similarity_boost": similarity_boost,
                                   "style": style, "use_speaker_boost": True}}
    if speed != 1.0:  payload["voice_settings"]["speed"] = speed
    if language:      payload["language_code"] = language
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200: raise RuntimeError(f"ElevenLabs TTS error ({r.status_code}): {r.text[:500]}")
    with open(output_file, "wb") as f: f.write(r.content)
    dur = eGetDuration(output_file)
    print(f"Voiceover saved -> {output_file}  ({dur:.1f}s, voice={voice_name}, model={model})")
    return output_file

def eGenerateMusic(
    api_key, prompt=None, output_file="background_music.mp3",
    duration_ms=15000, force_instrumental=True, output_format="mp3_44100_128", preset=None,
):
    if preset is not None:
        if preset not in MUSIC_PRESETS: raise ValueError(f"Unknown preset '{preset}'. Options: {list(MUSIC_PRESETS.keys())}")
        prompt = MUSIC_PRESETS[preset]
    url     = "https://api.elevenlabs.io/v1/music/stream"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
    payload = {"prompt": prompt, "music_length_ms": duration_ms,
               "force_instrumental": force_instrumental, "output_format": output_format}
    print(f"Generating music ({duration_ms/1000:.0f}s)... this may take 30-90 seconds.")
    r = requests.post(url, headers=headers, json=payload, stream=True)
    if r.status_code != 200: raise RuntimeError(f"ElevenLabs Music error ({r.status_code}): {r.text[:500]}")
    with open(output_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk: f.write(chunk)
    dur = eGetDuration(output_file)
    print(f"Music saved -> {output_file}  ({dur:.1f}s)")
    return output_file

def eAddVoiceover(video_file, voiceover_file, output_file="espresso_with_vo.mp4",
                  vo_volume=1.0, vo_delay=0.0, vo_fade_in=0.0, vo_fade_out=0.3):
    for f in [video_file, voiceover_file]:
        if not os.path.isfile(f): raise FileNotFoundError(f"File not found: {f}")
    vid_dur    = eGetDuration(video_file)
    vo_filters = [f"volume={vo_volume}"]
    if vo_delay  > 0: ms = int(vo_delay*1000); vo_filters.append(f"adelay={ms}|{ms}")
    if vo_fade_in > 0: vo_filters.append(f"afade=t=in:st=0:d={vo_fade_in}")
    if vo_fade_out > 0:
        vo_dur = eGetDuration(voiceover_file)
        vo_filters.append(f"afade=t=out:st={vo_dur-vo_fade_out+vo_delay:.2f}:d={vo_fade_out}")
    vo_chain = ",".join(vo_filters)
    cmd = ['ffmpeg','-y','-i',video_file,'-i',voiceover_file,'-filter_complex',
           f'[1:a]{vo_chain}[vo];[vo]apad=whole_dur={vid_dur:.2f}[aout]',
           '-map','0:v','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',output_file]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")
    print(f"Added voiceover -> {output_file}")
    return output_file

def eAddMusic(video_file, music_file, output_file="espresso_with_music.mp4",
              music_volume=0.15, fade_in=1.0, fade_out=2.0, loop=True):
    for f in [video_file, music_file]:
        if not os.path.isfile(f): raise FileNotFoundError(f"File not found: {f}")
    vid_dur    = eGetDuration(video_file)
    mu_filters = [f"volume={music_volume}"]
    if fade_in  > 0: mu_filters.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0: mu_filters.append(f"afade=t=out:st={vid_dur-fade_out:.2f}:d={fade_out}")
    mu_chain   = ",".join(mu_filters)
    loop_args  = ['-stream_loop','-1'] if loop else []
    cmd = ['ffmpeg','-y','-i',video_file,*loop_args,'-i',music_file,'-filter_complex',
           f'[1:a]{mu_chain},atrim=0:{vid_dur:.2f},asetpts=PTS-STARTPTS[music]',
           '-map','0:v','-map','[music]','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',output_file]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")
    print(f"Added background music -> {output_file}")
    return output_file

def eAddAudio(video_file, output_file="espresso_final.mp4",
              voiceover_file=None, vo_volume=1.0, vo_delay=0.5, vo_fade_in=0.0, vo_fade_out=0.3,
              music_file=None, music_volume=0.12, music_fade_in=1.0, music_fade_out=2.0, music_loop=True):
    if voiceover_file is None and music_file is None:
        raise ValueError("Provide at least one of voiceover_file or music_file.")
    if not os.path.isfile(video_file): raise FileNotFoundError(f"Video not found: {video_file}")
    vid_dur = eGetDuration(video_file)
    inputs  = ['-i', video_file]; input_idx = 1; filter_parts = []; mix_inputs = []
    if voiceover_file is not None:
        if not os.path.isfile(voiceover_file): raise FileNotFoundError(f"Voiceover not found: {voiceover_file}")
        inputs += ['-i', voiceover_file]; vo_idx = input_idx; input_idx += 1
        vo_filters = [f"volume={vo_volume}"]
        if vo_delay   > 0: ms=int(vo_delay*1000); vo_filters.append(f"adelay={ms}|{ms}")
        if vo_fade_in > 0: vo_filters.append(f"afade=t=in:st={vo_delay:.2f}:d={vo_fade_in}")
        if vo_fade_out > 0:
            vo_dur = eGetDuration(voiceover_file)
            vo_filters.append(f"afade=t=out:st={vo_delay+vo_dur-vo_fade_out:.2f}:d={vo_fade_out}")
        filter_parts.append(f"[{vo_idx}:a]{','.join(vo_filters)},apad=whole_dur={vid_dur:.2f}[vo]")
        mix_inputs.append("[vo]")
    if music_file is not None:
        if not os.path.isfile(music_file): raise FileNotFoundError(f"Music not found: {music_file}")
        if music_loop: inputs += ['-stream_loop','-1','-i',music_file]
        else:          inputs += ['-i', music_file]
        mu_idx = input_idx; input_idx += 1
        mu_filters = [f"volume={music_volume}"]
        if music_fade_in  > 0: mu_filters.append(f"afade=t=in:st=0:d={music_fade_in}")
        if music_fade_out > 0: mu_filters.append(f"afade=t=out:st={vid_dur-music_fade_out:.2f}:d={music_fade_out}")
        filter_parts.append(f"[{mu_idx}:a]{','.join(mu_filters)},atrim=0:{vid_dur:.2f},asetpts=PTS-STARTPTS[music]")
        mix_inputs.append("[music]")
    if len(mix_inputs) == 2:
        filter_parts.append(f"{''.join(mix_inputs)}amix=inputs=2:duration=first:dropout_transition=0[aout]")
    else:
        single_tag = mix_inputs[0].strip("[]")
        filter_parts[-1] = filter_parts[-1].rsplit(f"[{single_tag}]", 1)[0] + "[aout]"
    cmd = ['ffmpeg','-y',*inputs,'-filter_complex',';'.join(filter_parts),
           '-map','0:v','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',output_file]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")
    parts = []
    if voiceover_file: parts.append("voiceover")
    if music_file:     parts.append("music")
    print(f"Added {' + '.join(parts)} -> {output_file}  ({eGetDuration(output_file):.1f}s)")
    return output_file


# ============================================================================
# OPENING FRAME GENERATOR (Gemini Veo)
# ============================================================================

def _find_font(filename):
    """Locate a font file on the system. Returns path string or None."""
    # Check espresso font dir first (known install location)
    espresso_dir = "/usr/local/share/fonts/espresso"
    direct_path = os.path.join(espresso_dir, filename)
    if os.path.exists(direct_path):
        return direct_path
    # Try common font directories with os.walk (handles brackets in filenames)
    search_dirs = ["/usr/local/share/fonts", "/usr/share/fonts"]
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            if filename in files:
                return os.path.join(root, filename)
    # Fallback: fc-match
    base = filename.split("[")[0].split(".")[0]  # strip brackets and extension
    result = subprocess.run(
        ["fc-match", "--format=%{file}", base],
        capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def eGenerateOpeningFrame(
    video_prompt,
    number_text,
    label_text,
    output_file="opening_frame.mp4",
    number_size=130,
    label_size=36,
    number_color="#A14516",
    label_color="#CDAF7B",
    number_y_offset=-60,
    label_y_offset=40,
    duration_seconds=5,
    poll_interval=15,
    max_wait=300,
    scrim_opacity=0.45,
    gemini_api_key=None,
    gcp_project="main-voltage-446412-p1",
    gcp_location="us-central1",
):
    """Generate an animated opening frame for a Reel using Gemini Veo.

    Pipeline:
      1. Call Gemini Veo API to generate a 1080x1920 portrait video clip
      2. Poll until generation is complete
      3. Download the resulting video
      4. Overlay a headline statistic and label using ffmpeg drawtext
      5. Return the output file path, ready for eConcatenateMP4

    Parameters
    ----------
    gemini_api_key : str or None
        Google Gemini API key. Fallback only; Vertex AI auth is preferred.
        If None, reads from GEMINI_API_KEY env var.
    gcp_project : str or None
        GCP project ID for Vertex AI auth. Default uses the Espresso Charts
        project. Set to None to force API key auth instead.
    gcp_location : str
        GCP region for Vertex AI. Default "us-central1".
    video_prompt : str
        Creative prompt for the video background. A portrait-format preamble
        is automatically prepended.
    number_text : str
        Headline statistic, e.g. "+28 days" or "4.2%".
    label_text : str
        Short label below the number (max ~8 words). Use single quotes
        inside the string; ffmpeg drawtext cannot handle double quotes.
    output_file : str
        Path for the final composited video.
    number_size : int
        Font size for the headline number. Default 130.
    label_size : int
        Font size for the label text. Default 36.
    number_color : str
        Hex color for the number, e.g. "#A14516".
    label_color : str
        Hex color for the label, e.g. "#CDAF7B".
    number_y_offset : int
        Vertical pixel offset from center for the number (negative = up).
    label_y_offset : int
        Vertical pixel offset from center for the label (positive = down).
    duration_seconds : int
        Target clip duration to request from Gemini.
    scrim_opacity : float
        Opacity of the dark scrim behind the text (0.0 = invisible, 1.0 = solid
        black). Default 0.45. Set to 0 to disable the scrim entirely.
    poll_interval : int
        Seconds between status polls.
    max_wait : int
        Maximum seconds to wait before raising a timeout error.

    Returns
    -------
    str
        Path to the output video file.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        os.system("pip install google-genai --break-system-packages -q")
        from google import genai
        from google.genai import types

    if gemini_api_key is None:
        gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

    # --- 1. Build prompt with portrait preamble ---
    portrait_preamble = (
        "Generate a 1080x1920 pixel video. Portrait orientation, taller than "
        "it is wide, like a phone screen held upright. Do not generate landscape "
        "or square format. The frame is 1080 pixels wide and 1920 pixels tall. "
    )
    full_prompt = portrait_preamble + video_prompt

    # --- 2. Submit generation job ---
    # Vertex AI auth (service account) supports the full pipeline including
    # operation polling. API key auth fails on operations.get() with 401.
    # Use Vertex AI by default; fall back to API key only if no project set.
    print("Generating Gemini video clip...")
    if gcp_project:
        print(f"  Using Vertex AI (project={gcp_project}, location={gcp_location})")
        client = genai.Client(
            vertexai=True,
            project=gcp_project,
            location=gcp_location,
        )
    elif gemini_api_key:
        print("  Using API key auth (operation polling may fail)")
        client = genai.Client(api_key=gemini_api_key)
    else:
        raise ValueError(
            "No auth configured. Either set gcp_project for Vertex AI "
            "or set GEMINI_API_KEY env var."
        )

    operation = client.models.generate_videos(
        model="veo-2.0-generate-001",
        prompt=full_prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            number_of_videos=1,
            duration_seconds=duration_seconds,
        ),
    )

    # --- 3. Poll until done ---
    elapsed = 0
    while not operation.done:
        time.sleep(poll_interval)
        elapsed += poll_interval
        print(f"Waiting for Gemini video... {elapsed}s elapsed")
        if elapsed >= max_wait:
            raise RuntimeError(
                f"Gemini video generation timed out after {max_wait}s. "
                f"Operation name: {getattr(operation, 'name', 'unknown')}"
            )
        operation = client.operations.get(operation)

    # --- 4. Download raw clip ---
    generated = getattr(operation.response, 'generated_videos', None)
    if not generated or len(generated) == 0:
        raise RuntimeError(
            "Gemini returned no generated videos. "
            f"Operation response: {operation.response}"
        )

    video = generated[0].video
    raw_path = output_file.replace(".mp4", "_raw.mp4")

    # Download differs between Vertex AI and API key auth
    if gcp_project:
        # Vertex AI: video_bytes is populated directly (uri is None).
        # Just call .save() to write to disk.
        video.save(raw_path)
    else:
        # API key auth: need to download first, then save
        client.files.download(file=video)
        video.save(raw_path)

    raw_dur = eGetDuration(raw_path)
    print(f"Raw clip saved -> {raw_path}  ({raw_dur:.1f}s)")

    # --- 5. Overlay text with ffmpeg drawtext ---
    font_serif = (_find_font("PlayfairDisplay[wght].ttf")
                  or _find_font("PlayfairDisplay-Medium.ttf")
                  or _find_font("DejaVuSerif-Bold.ttf")
                  or _find_font("DejaVuSerif.ttf"))
    font_sans  = (_find_font("SourceSerif4[opsz,wght].ttf")
                  or _find_font("SourceSerif4-Regular.ttf")
                  or _find_font("DMMono-Regular.ttf")
                  or _find_font("DejaVuSans.ttf"))
    print(f"  Fonts: serif={font_serif}, sans={font_sans}")

    # Probe actual video dimensions (Veo may not produce exactly 1080x1920)
    probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
                 '-show_streams', raw_path]
    probe_r = subprocess.run(probe_cmd, capture_output=True, text=True)
    vid_w, vid_h = 1080, 1920  # defaults
    if probe_r.returncode == 0:
        streams = json.loads(probe_r.stdout).get('streams', [])
        for s in streams:
            if s.get('codec_type') == 'video':
                vid_w = int(s['width'])
                vid_h = int(s['height'])
                break
    print(f"  Video dimensions: {vid_w}x{vid_h}")

    # Compute absolute pixel positions (no ffmpeg expressions)
    center_y = vid_h // 2
    # Approximate text heights: number ~130px at fontsize 130, label ~36px at fontsize 36
    num_text_h = int(number_size * 1.0)
    lbl_text_h = int(label_size * 1.0)

    num_y = center_y + number_y_offset - num_text_h // 2  # number_y_offset is negative = up
    lbl_y = center_y + label_y_offset - lbl_text_h // 2

    # Scrim: covers from above number to below label
    scrim_y = num_y - 40
    scrim_bottom = lbl_y + lbl_text_h + 40
    scrim_h = scrim_bottom - scrim_y

    print(f"  Positions: number_y={num_y}, label_y={lbl_y}, scrim={scrim_y}-{scrim_bottom} (h={scrim_h})")

    # Write text to temp files to avoid ALL ffmpeg escaping issues (%, quotes, colons)
    num_txt_path = raw_path.replace("_raw.mp4", "_num.txt")
    lbl_txt_path = raw_path.replace("_raw.mp4", "_lbl.txt")
    with open(num_txt_path, "w") as f:
        f.write(number_text)
    with open(lbl_txt_path, "w") as f:
        f.write(label_text)

    # Build filters with hardcoded pixel positions
    scrim_filter = (
        f"drawbox=x=0:y={scrim_y}:w={vid_w}:h={scrim_h}"
        f":color=black@{scrim_opacity}:t=fill"
    )

    num_filter = (
        f"drawtext=textfile={num_txt_path}"
        f":expansion=none"
        f":fontsize={number_size}"
        f":fontcolor=0x{number_color.lstrip('#')}"
        f":borderw=3:bordercolor=0x000000@0.6"
        f":x=({vid_w}-text_w)/2"
        f":y={num_y}"
    )
    # ffmpeg cannot handle [ ] in font paths (filter graph syntax conflict).
    # Create temp symlinks with clean names if needed.
    _temp_font_links = []
    def _ffmpeg_safe_font(font_path):
        if not font_path or ('[' not in font_path and ']' not in font_path):
            return font_path
        import tempfile
        clean_name = os.path.basename(font_path).replace('[', '_').replace(']', '_').replace(',', '_')
        link_path = os.path.join(tempfile.gettempdir(), clean_name)
        if not os.path.exists(link_path):
            os.symlink(font_path, link_path)
        _temp_font_links.append(link_path)
        return link_path

    safe_serif = _ffmpeg_safe_font(font_serif)
    safe_sans  = _ffmpeg_safe_font(font_sans)

    if safe_serif:
        num_filter += f":fontfile={safe_serif}"

    lbl_filter = (
        f"drawtext=textfile={lbl_txt_path}"
        f":expansion=none"
        f":fontsize={label_size}"
        f":fontcolor=0x{label_color.lstrip('#')}"
        f":borderw=2:bordercolor=0x000000@0.5"
        f":x=({vid_w}-text_w)/2"
        f":y={lbl_y}"
    )
    if safe_sans:
        lbl_filter += f":fontfile={safe_sans}"

    filter_chain = f"{num_filter},{lbl_filter}"
    if scrim_opacity > 0:
        filter_chain = f"{scrim_filter},{filter_chain}"

    cmd = [
        'ffmpeg', '-y',
        '-i', raw_path,
        '-vf', filter_chain,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        output_file,
    ]
    print(f"  ffmpeg -vf: {filter_chain}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg overlay failed:\n{r.stderr}")

    # Cleanup temp text files and font symlinks
    for p in [num_txt_path, lbl_txt_path] + _temp_font_links:
        if os.path.exists(p):
            os.remove(p)

    print(f"Overlay applied -> {output_file}")
    return output_file


# ============================================================================
# GITHUB UPLOADER
# ============================================================================
class GitHubUploader:
    def __init__(self, token, owner, repo, branch="main"):
        self.token = token; self.owner = owner; self.repo = repo; self.branch = branch
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"}
    def _get_sha(self, path):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        r   = requests.get(url, headers=self._headers(), params={"ref": self.branch})
        return r.json().get("sha") if r.ok else None
    def _push(self, path, content_b64, commit_msg):
        url  = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        body = {"message": commit_msg, "content": content_b64, "branch": self.branch}
        sha  = self._get_sha(path)
        if sha: body["sha"] = sha
        r = requests.put(url, headers=self._headers(), data=json.dumps(body))
        if not r.ok: raise RuntimeError(f"GitHub {r.status_code}: {r.json().get('message')}")
        return r.json()
    def push_file(self, local_path, dest=None, commit_msg=None):
        local_path = Path(local_path); dest = dest or f"assets/{local_path.name}"
        msg = commit_msg or f"Upload {local_path.name} [{datetime.now().strftime('%Y-%m-%d')}]"
        with open(local_path, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        self._push(dest, b64, msg); print(f"  {local_path.name}  ->  {dest}")
    def push_figure(self, fig, dest, dpi=200, commit_msg=None):
        buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        buf.seek(0); b64 = base64.b64encode(buf.read()).decode()
        name = Path(dest).name
        msg = commit_msg or f"Push chart {name} [{datetime.now().strftime('%Y-%m-%d')}]"
        self._push(dest, b64, msg); print(f"  {name}  ->  {dest}")
    def push_text(self, text, dest, commit_msg=None):
        name = Path(dest).name; msg = commit_msg or f"Save {name} [{datetime.now().strftime('%Y-%m-%d')}]"
        b64 = base64.b64encode(text.encode("utf-8")).decode()
        self._push(dest, b64, msg); print(f"  {name}  ->  {dest}")
    def push_story_pack(self, story_slug, files, year=None):
        year = year or str(datetime.now().year); base = f"content/{year}/{story_slug}"
        print(f"\nPushing story pack -> {base}/")
        for suffix, source in files.items():
            dest = f"{base}/{suffix}"
            if isinstance(source, str) and os.path.exists(source): self.push_file(source, dest)
            elif isinstance(source, str): self.push_text(source, dest)
            else: print(f"  Skipped {suffix}: pass a file path or text string")
        print(f"  Story pack complete\n")


# ============================================================================
# SUBSTACK PUBLISHER
# ============================================================================
class SubstackPublisher:
    def __init__(self, publication_url, email, password):
        self.pub_url = publication_url.rstrip("/"); self.email = email
        self.password = password; self.session = requests.Session(); self._logged_in = False
    def _login(self):
        if self._logged_in: return
        r = self.session.post("https://substack.com/api/v1/email-login",
                              json={"email": self.email, "password": self.password, "captcha_response": None})
        if not r.ok: raise RuntimeError(f"Substack login failed {r.status_code}: {r.text}")
        self._logged_in = True; print("Logged in to Substack")
    def _markdown_to_html(self, text):
        try:    import markdown
        except: os.system("pip install markdown -q"); import markdown
        return markdown.markdown(text, extensions=["extra", "nl2br"])
    def _create_post(self, title, body_html, subtitle=""):
        self._login()
        r = self.session.post(f"{self.pub_url}/api/v1/posts",
                              json={"type": "newsletter", "draft_title": title,
                                    "draft_subtitle": subtitle, "draft_body": body_html, "audience": "everyone"})
        if not r.ok: raise RuntimeError(f"Failed to create post {r.status_code}: {r.text}")
        return r.json()
    def post_draft(self, title, body, subtitle="", body_is_html=False):
        html = body if body_is_html else self._markdown_to_html(body)
        post = self._create_post(title, html, subtitle)
        print(f"Draft saved: '{title}'\n    Edit at: {self.pub_url}/publish/post/{post.get('id','')}")
        return post
    def post_scheduled(self, title, body, publish_at, subtitle="", body_is_html=False):
        self._login(); html = body if body_is_html else self._markdown_to_html(body)
        post = self._create_post(title, html, subtitle); post_id = post["id"]
        r = self.session.post(f"{self.pub_url}/api/v1/posts/{post_id}/schedule",
                              json={"post_date": f"{publish_at}Z"})
        if not r.ok: raise RuntimeError(f"Failed to schedule post {r.status_code}: {r.text}")
        print(f"Scheduled: '{title}'\n    Publishes: {publish_at} UTC\n    Edit at: {self.pub_url}/publish/post/{post_id}")
        return r.json()
    def post_now(self, title, body, subtitle="", body_is_html=False):
        self._login(); html = body if body_is_html else self._markdown_to_html(body)
        post = self._create_post(title, html, subtitle); post_id = post["id"]
        r = self.session.post(f"{self.pub_url}/api/v1/posts/{post_id}/publish")
        if not r.ok: raise RuntimeError(f"Failed to publish {r.status_code}: {r.text}")
        print(f"Published: '{title}'\n    Live at: {self.pub_url}/p/{post.get('slug','')}")
        return r.json()


# ============================================================================
# DATA POSTER (Print-quality PDF)
# ============================================================================

def eDataPoster(
    # Hero block
    hero_number="8.1",
    hero_number_color=None,
    hero_unit="billion people",
    hero_eyebrow="People on Earth, 2024",
    # Insight block
    insight_text="It took all of human history to reach one billion people.\nWe added seven more in two centuries.",
    insight_context="The first billion took roughly 300,000 years.\nThe second took 127 years. The third took 33.",
    # Chart data (simple line chart)
    chart_x=None,
    chart_y=None,
    chart_x_labels=None,
    chart_y_labels=None,
    chart_y_format="{:.0f}",
    chart_color='#3F5B83',
    chart_fill_alpha=0.12,
    # Annotations (list of dicts: {year, value, desc, color})
    annotations=None,
    # Metadata
    issue_number="001",
    issue_topic="World Population",
    source_lines=None,
    # Layout
    accent_color='#3F5B83',
    output_file="poster.pdf",
    dpi=300,
    paper_width_in=11.69,
    paper_height_in=16.54,
):
    """Generate a print-quality data poster as PDF (A3 portrait).

    Hero number at 120pt. Chart has no Y axis — first/last data points
    are labeled directly. PDF rendered via PIL (no reportlab needed).
    """
    fc = '#F5F0E6'
    ink = '#2A1F14'
    ink_muted = '#79664a'
    ink_faint = '#9e8b76'
    rule_color = '#C8BBA8'

    plt.rcdefaults()
    plt.rcParams['font.family'] = 'DM Mono'

    fig = plt.figure(figsize=(paper_width_in, paper_height_in), dpi=dpi, facecolor=fc)
    ml, mr = 0.076, 0.924

    # ── MASTHEAD ──
    fig.text(ml, 0.972, "ESPRESSO CHARTS",
             fontfamily='DM Mono', fontsize=9, fontweight=300,
             color=ink_muted, ha='left', va='top')
    fig.text(mr, 0.972, f"No. {issue_number}  \u00b7  {issue_topic}",
             fontfamily='DM Mono', fontsize=8, fontweight=300,
             color=ink_faint, ha='right', va='top')
    fig.add_artist(plt.Line2D([ml, mr], [0.963, 0.963],
                              color=rule_color, linewidth=0.5, transform=fig.transFigure))

    # ── EYEBROW ──
    fig.text(ml, 0.950, hero_eyebrow,
             fontfamily='DM Mono', fontsize=9, fontweight=300,
             color=ink_faint, ha='left', va='top')

    # ── HERO NUMBER (120pt) ──
    num_y = 0.935
    fig.text(ml, num_y, hero_number,
             fontfamily='Playfair Display', fontsize=120, fontweight=700,
             fontstyle='italic', color=accent_color,
             ha='left', va='top', linespacing=0.85)

    # ── UNIT LABEL ──
    fig.text(ml, num_y - 0.110, hero_unit,
             fontfamily='Playfair Display', fontsize=26, fontweight=400,
             fontstyle='italic', color=ink_muted,
             ha='left', va='top')

    # ── ACCENT RULE ──
    accent_y = num_y - 0.140
    fig.add_artist(plt.Line2D([ml, ml + 0.055], [accent_y, accent_y],
                              color=accent_color, linewidth=2.5, solid_capstyle='round',
                              transform=fig.transFigure))

    # ── CHART ──
    chart_top = accent_y - 0.030
    chart_height = 0.30
    chart_bottom = chart_top - chart_height
    chart_section_present = chart_x is not None and chart_y is not None

    if chart_section_present:
        ax = fig.add_axes([ml, chart_bottom, mr - ml, chart_height])
        ax.set_facecolor(fc)
        ax.grid(axis='y', color=rule_color, linewidth=0.3, linestyle=(0, (3, 4)), zorder=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(axis='both', length=0)

        ax.fill_between(chart_x, chart_y, alpha=chart_fill_alpha, color=chart_color, zorder=1)
        ax.plot(chart_x, chart_y, color=chart_color, linewidth=2.2,
                solid_capstyle='round', solid_joinstyle='round', zorder=2)
        ax.plot(chart_x[-1], chart_y[-1], 'o', color=chart_color, markersize=5, zorder=3)
        ax.plot(chart_x[0], chart_y[0], 'o', color=chart_color, markersize=4, zorder=3)

        # Annotation dots on chart
        if annotations:
            for anno in annotations:
                if 'chart_x' in anno and 'chart_y' in anno:
                    ax.plot(anno['chart_x'], anno['chart_y'], 'o',
                            color=anno.get('color', accent_color), markersize=4, zorder=3)

        # X axis labels
        if chart_x_labels:
            ax.set_xticks([l[0] for l in chart_x_labels])
            xlabels = ax.set_xticklabels([l[1] for l in chart_x_labels],
                                          fontfamily='DM Mono', fontsize=9.5, color=ink_faint)
            for lbl in xlabels:
                if lbl.get_text() == "Now":
                    lbl.set_color(chart_color); lbl.set_fontweight(400)
        else:
            ax.tick_params(axis='x', labelbottom=False)

        # No Y axis — value labels on first and last data points instead
        ax.set_yticks([])
        ax.tick_params(axis='y', labelleft=False)

        # First data point label
        first_label = chart_y_format.format(chart_y[0])
        ax.annotate(first_label, xy=(chart_x[0], chart_y[0]),
                    xytext=(-6, 8), textcoords='offset points',
                    ha='right', va='bottom', fontfamily='DM Mono',
                    fontsize=10, color=chart_color, fontweight=400, zorder=5)
        # Last data point label
        last_label = chart_y_format.format(chart_y[-1])
        ax.annotate(last_label, xy=(chart_x[-1], chart_y[-1]),
                    xytext=(6, 8), textcoords='offset points',
                    ha='left', va='bottom', fontfamily='DM Mono',
                    fontsize=10, color=chart_color, fontweight=400, zorder=5)

        ax.set_xlim(min(chart_x), max(chart_x))
        ax.margins(y=0.10)

    # ── ANNOTATION BAND ──
    anno_y = (chart_bottom - 0.020) if chart_section_present else (accent_y - 0.35)

    if annotations:
        n = len(annotations)
        band_width = mr - ml
        col_width = band_width / n

        for i, anno in enumerate(annotations):
            x_pos = ml + i * col_width + 0.012
            dot_color = anno.get('color', accent_color)

            fig.text(x_pos, anno_y, '\u25CF', fontsize=9, color=dot_color,
                     ha='left', va='top', transform=fig.transFigure)

            text_x = x_pos + 0.022
            fig.text(text_x, anno_y + 0.002, anno.get('year', ''),
                     fontfamily='DM Mono', fontsize=9, fontweight=300,
                     color=ink_faint, ha='left', va='top')
            fig.text(text_x, anno_y - 0.018, anno.get('value', ''),
                     fontfamily='Playfair Display', fontsize=17, fontweight=600,
                     color=ink, ha='left', va='top')
            fig.text(text_x, anno_y - 0.042, anno.get('desc', ''),
                     fontfamily='Source Serif 4', fontsize=12, fontweight=300,
                     color=ink_muted, ha='left', va='top', linespacing=1.4)

    # ── INSIGHT BLOCK ──
    insight_top = anno_y - 0.085 if annotations else (anno_y - 0.015)
    fig.add_artist(plt.Line2D([ml, mr], [insight_top, insight_top],
                              color=rule_color, linewidth=0.5, transform=fig.transFigure))

    fig.text(ml, insight_top - 0.025, insight_text,
             fontfamily='Playfair Display', fontsize=26, fontweight=400,
             fontstyle='italic', color=ink, ha='left', va='top',
             linespacing=1.45, transform=fig.transFigure)

    # Estimate insight height
    n_insight_lines = max(1, insight_text.count('\n') + 1)
    context_top = insight_top - 0.025 - (n_insight_lines * 0.032) - 0.020

    if insight_context:
        fig.text(ml, context_top, insight_context,
                 fontfamily='Source Serif 4', fontsize=15, fontweight=300,
                 color=ink_muted, ha='left', va='top',
                 linespacing=1.6, transform=fig.transFigure)

    # ── FOOTER ──
    footer_y = 0.040
    fig.add_artist(plt.Line2D([ml, mr], [footer_y + 0.015, footer_y + 0.015],
                              color=rule_color, linewidth=0.5, transform=fig.transFigure))

    if source_lines:
        source_text = '\n'.join(source_lines)
        fig.text(ml, footer_y, source_text,
                 fontfamily='DM Mono', fontsize=7, fontweight=300,
                 color=ink_faint, ha='left', va='top', linespacing=1.7)

    fig.text(mr, footer_y, "Thirty seconds of perspective",
             fontfamily='Playfair Display', fontsize=10, fontstyle='italic',
             color=ink_muted, ha='right', va='top')
    fig.text(mr, footer_y - 0.016, "espressocharts.substack.com \u2615",
             fontfamily='DM Mono', fontsize=7, fontweight=300,
             color=ink_faint, ha='right', va='top')

    # ── CORNER MARK ──
    from matplotlib.patches import Polygon
    corner_size = 0.020
    triangle = Polygon(
        [[1.0, 0.0], [1.0, corner_size], [1.0 - corner_size, 0.0]],
        closed=True, facecolor=accent_color, edgecolor='none',
        alpha=0.6, transform=fig.transFigure, zorder=10)
    fig.add_artist(triangle)

    # ── SAVE ──
    # Render to PNG, then convert to PDF via PIL (avoids matplotlib
    # PDF backend crash on variable font style flags)
    if output_file.lower().endswith('.pdf'):
        import tempfile
        from PIL import Image as PILImage
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_png = tmp.name
        fig.savefig(tmp_png, dpi=dpi, facecolor=fc, bbox_inches=None, pad_inches=0)
        plt.close(fig)
        img = PILImage.open(tmp_png)
        img.save(output_file, 'PDF', resolution=dpi)
        os.unlink(tmp_png)
    else:
        fig.savefig(output_file, dpi=dpi, facecolor=fc, bbox_inches=None, pad_inches=0)
        plt.close(fig)

    print(f"Poster saved -> {output_file}  ({paper_width_in:.1f}x{paper_height_in:.1f}in @ {dpi}dpi)")
    return output_file
