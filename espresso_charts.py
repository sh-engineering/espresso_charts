# -*- coding: utf-8 -*-
"""
espresso_charts.py — Espresso Charts Library (v2 — Standardized Layout)
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
# STYLE CONFIG
# ============================================================================
color_blue   = '#3F5B83'
color_orange = '#DD6B20'
color_green  = '#4D5523'
color_sand   = '#CDAF7B'
face_color   = '#F5F0E6'


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
        'figsize_px': (1080, 1920),
        'suptitle_y':  0.970,
        'subtitle_y':  0.872,   # = 0.970 - 0.083 - 0.015
        'plot_top':    0.812,   # = 0.872 - 0.045 - 0.015
        'plot_bottom': 0.055,
        'footnote_y':  0.025,
    },
}

# Font defaults
_SUPTITLE_SIZE = 26
_SUBTITLE_SIZE = 14
_FOOTNOTE_SIZE = 9
_SUPTITLE_FONT = 'DejaVu Serif'
_SUBTITLE_FONT = 'DejaVu Sans'
_BODY_FONT     = 'DejaVu Sans'


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
            lc   = ln.get('label_color', color)
            ls   = ln.get('label_size', 10)
            xlim = ax.get_xlim()
            ax.text(xlim[1], ln['y'], f"  {ln['label']}",
                    ha='left', va='center', color=lc, fontsize=ls,
                    zorder=ln.get('zorder', 5) + 1)
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
            alpha=txt.get('alpha', 1.0), family=txt.get('family', 'DejaVu Sans'),
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
    font='DejaVu Sans', suptitle_font=None, subtitle_font=None,
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
    fig, ax, L = _setup_chart(
        layout='4x5', face_color=face_color, dpi=dpi,
        plot_left=0.10, plot_right=0.80,  # bar charts need right margin for value labels
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
        is_pos   = (x_end >= x_start)

        cat_extra = 0
        if isinstance(label_custom_offset, dict):
            cat_extra = label_custom_offset.get(idx, 0)
        ha_cat  = 'left' if is_pos else 'right'
        off_cat = 8 + offset_label_x + cat_extra if is_pos else -8 - offset_label_x - cat_extra
        ax.annotate(
            category, xy=(x_start if is_pos else x_end, y_center),
            xytext=(off_cat, 0), textcoords='offset points',
            ha=ha_cat, va='center', fontsize=label_size,
            color=tick_label_color, zorder=6,
            bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                      edgecolor='none', alpha=0.8))

        val       = value / num_divisor
        formatted = num_format.format(val) if num_format else str(val)
        x_extra = 0
        if isinstance(value_label_offset_x, dict):
            x_extra += value_label_offset_x.get(idx, 0)
        y_extra = 0
        if isinstance(value_label_offset_y, dict):
            y_extra = value_label_offset_y.get(idx, 0)
        ha_val  = 'left' if is_pos else 'right'
        off_val = 8 + x_extra if is_pos else -8 - x_extra
        ax.annotate(
            formatted, xy=(x_end, y_center),
            xytext=(off_val, y_extra), textcoords='offset points',
            ha=ha_val, va='center',
            fontsize=label_size, color=value_label_color, zorder=6,
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
    xtick_align_ha="center", xtick_align_va="bottom",
    value_label_offset_pts=6, value_label_offset_y=None, value_label_offset_x=None,
    x_axis_line_width=0.8, x_axis_line_color="#857052",
    line_format_a="--", line_format_b="--",
    value_label_custom_offset=None,
    show_legend=False, legend_labels=None, legend_loc='upper right',
    legend_font_size=10, legend_frame=False, legend_text_color='#3c3325',
    legend_bbox_to_anchor=None, y_min=None, y_max=None,
    show_x_axis=False, reference_bands=None, vlines=None, hlines=None,
    font='DejaVu Sans', suptitle_font=None, subtitle_font=None,
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
    ax.set_xticklabels(cats, color=tick_label_color, va=xtick_align_va, ha=xtick_align_ha,
                        fontsize=label_size, rotation=90 if rotate_labels else 0,
                        bbox=dict(boxstyle="square,pad=0.1", facecolor="white",
                                  edgecolor="white", alpha=0.7))
    for lbl in ax.get_xticklabels():
        x0, y0 = lbl.get_position()
        lbl.set_position((x0, y0 + x_tick_label_y_offset))
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])

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
    font='DejaVu Sans', suptitle_font=None, subtitle_font=None,
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
    suptitle_color='#4b2e1a', suptitle_font='DejaVu Serif',
    suptitle_font_weight='normal', suptitle_size=42, suptitle_y=0.6,
    subtitle_color='#4b2e1a', subtitle_font='DejaVu Sans',
    subtitle_font_weight='normal', subtitle_size=18, subtitle_y=0.38,
    txt_label_color='#857052', txt_label_font='DejaVu Sans',
    txt_label_font_weight='light', label_size=11, label_y=0.06,
    face_color='#F5F0E6', px_width=1080, px_height=1350, dpi=200,
    show_accent_line=True, accent_line_color='#3F5B83', accent_line_width=4,
    accent_line_y=0.48, accent_line_length=0.15,
):
    """Cover tile — full-bleed typography, no plot area. Layout is custom per design."""
    plt.rcdefaults(); plt.rcParams['font.family'] = 'DejaVu Sans'
    figsize = (px_width / dpi, px_height / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    for spine in ax.spines.values(): spine.set_visible(False)
    texts = [
        {'text': txt_suptitle, 'xy': (0.5, suptitle_y), 'fontsize': suptitle_size,
         'color': suptitle_color, 'ha': 'center', 'va': 'center',
         'fontweight': suptitle_font_weight, 'family': suptitle_font, 'linespacing': 1.1},
        {'text': txt_subtitle, 'xy': (0.5, subtitle_y), 'fontsize': subtitle_size,
         'color': subtitle_color, 'ha': 'center', 'va': 'center',
         'fontweight': subtitle_font_weight, 'family': subtitle_font, 'linespacing': 1.3},
    ]
    if txt_label:
        texts.append({'text': txt_label, 'xy': (0.5, label_y), 'fontsize': label_size,
                      'color': txt_label_color, 'ha': 'center', 'va': 'center',
                      'fontweight': txt_label_font_weight, 'family': txt_label_font})
    add_text(ax, texts)
    if show_accent_line:
        half = accent_line_length / 2
        ax.plot([0.5 - half, 0.5 + half], [accent_line_y, accent_line_y],
                color=accent_line_color, linewidth=accent_line_width, solid_capstyle='round')
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
    font='DejaVu Sans', suptitle_font=None, subtitle_font=None,
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
        ann = ax.annotate("", xy=(0, y_center), xytext=(8, 0),
                          textcoords='offset points', ha='left', va='center',
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
                   linewidth=zero_line_width, zorder=8)
    if aspect_ratio is not None: ax.set_box_aspect(aspect_ratio)

    line_objects, dot_objects = [], []
    for idx in range(len(col_measure_list)):
        ln, = ax.plot([], [], color=colors[idx], linestyle=styles[idx], linewidth=widths[idx], zorder=9)
        line_objects.append(ln)
        dt, = ax.plot([], [], 'o', color=colors[idx], markersize=5, zorder=10)
        dot_objects.append(dt)

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
            elif full == 0:
                line_objects[li].set_data([x_arr[0]], [y_all[0]])
                dot_objects[li].set_data([x_arr[0]], [y_all[0]])
            else:
                xs2 = list(x_arr[:full]); ys2 = list(y_all[:full])
                if full < n_rows:
                    xs2.append(x_arr[full-1] + frac*(x_arr[full]-x_arr[full-1]))
                    ys2.append(y_all[full-1] + frac*(y_all[full]-y_all[full-1]))
                line_objects[li].set_data(xs2, ys2)
                dot_objects[li].set_data([xs2[-1]], [ys2[-1]])
        for vi, vt in enumerate(value_targets):
            if vt['pos'] < reveal - 0.5:
                val_objs[vi].set_visible(True)
                val_objs[vi].set_text(vt['formatted'])
                val_objs[vi].xy = (vt['x'], vt['y'])
            else:
                val_objs[vi].set_visible(False)
        if shade_patch is not None:
            shade_patch.set_visible(progress >= 0.99)
        return line_objects + dot_objects + val_objs

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
    rotate_labels=False, xtick_align_ha="center", xtick_align_va="bottom",
    value_label_offset_pts=6, value_label_offset_y=None, value_label_offset_x=None,
    value_label_custom_offset=None,
    x_axis_line_width=0.8, x_axis_line_color="#857052",
    line_format_a="--", line_format_b="--",
    show_legend=False, legend_labels=None, legend_loc='upper right',
    legend_font_size=10, legend_frame=False, legend_text_color='#3c3325',
    legend_bbox_to_anchor=None, y_min=None, y_max=None,
    font='DejaVu Sans', suptitle_font=None, subtitle_font=None,
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
    ax.set_xticklabels(cats, color=tick_label_color, va=xtick_align_va, ha=xtick_align_ha,
                        fontsize=label_size, rotation=90 if rotate_labels else 0,
                        bbox=dict(boxstyle="square,pad=0.1", facecolor="white",
                                  edgecolor="white", alpha=0.7))
    for lbl in ax.get_xticklabels():
        x0, y0 = lbl.get_position()
        lbl.set_position((x0, y0 + x_tick_label_y_offset))
    ax.tick_params(axis="x", length=0); ax.set_yticks([])

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
    label_size=10, bottom_note_size=None, font='DejaVu Sans',
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
    duration=1.5, hold_duration=1.0, fps=30,
    output_file="espresso_cover_animated.mp4", easing='cubic',
    tw_suptitle_start=0.0, tw_suptitle_end=0, tw_subtitle_start=0, tw_subtitle_end=0,
    suptitle_color='#4b2e1a', suptitle_font='DejaVu Serif', suptitle_font_weight='normal',
    suptitle_size=42, suptitle_y=0.6,
    subtitle_color='#4b2e1a', subtitle_font='DejaVu Sans', subtitle_font_weight='normal',
    subtitle_size=18, subtitle_y=0.38,
    txt_label_color='#857052', txt_label_font='DejaVu Sans', txt_label_font_weight='light',
    label_size=11, label_y=0.06,
    face_color='#F5F0E6', px_width=1080, px_height=1920, dpi=200,
    show_accent_line=True, accent_line_color='#3F5B83', accent_line_width=4,
    accent_line_y=0.48, accent_line_length=0.15,
    accent_line_start=0.40, accent_line_end=0.65,
):
    """Animated cover tile — full-bleed typography, no plot area. Layout is custom per design."""
    ease_fn = _EASING.get(easing, _ease_out_cubic)
    plt.rcdefaults(); plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams["savefig.bbox"] = "standard"
    figsize = (px_width/dpi, px_height/dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.patch.set_facecolor(face_color)
    fig.patch.set_edgecolor(face_color)
    fig.patch.set_linewidth(0)
    fig.patch.set_alpha(1)

    suptitle_obj = ax.text(0.5, suptitle_y, "", fontsize=suptitle_size, color=suptitle_color,
                            ha='center', va='center', fontweight=suptitle_font_weight,
                            fontfamily=suptitle_font, linespacing=1.1, transform=ax.transAxes)
    subtitle_obj = ax.text(0.5, subtitle_y, "", fontsize=subtitle_size, color=subtitle_color,
                            ha='center', va='center', fontweight=subtitle_font_weight,
                            fontfamily=subtitle_font, linespacing=1.3, transform=ax.transAxes)
    if txt_label:
        ax.text(0.5, label_y, txt_label, fontsize=label_size, color=txt_label_color,
                ha='center', va='center', fontweight=txt_label_font_weight,
                fontfamily=txt_label_font, transform=ax.transAxes)
    accent_line_obj, = ax.plot([], [], color=accent_line_color, linewidth=accent_line_width,
                                solid_capstyle='round', transform=ax.transAxes)
    total_anim   = int(fps * duration)
    hold_frames  = int(fps * hold_duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)
        suptitle_obj.set_text(_typewriter(txt_suptitle, progress, tw_suptitle_start, tw_suptitle_end))
        subtitle_obj.set_text(_typewriter(txt_subtitle,  progress, tw_subtitle_start,  tw_subtitle_end))
        if show_accent_line:
            if progress <= accent_line_start:
                accent_line_obj.set_data([], [])
            elif progress >= accent_line_end:
                h = accent_line_length/2
                accent_line_obj.set_data([0.5-h, 0.5+h], [accent_line_y, accent_line_y])
            else:
                t  = (progress-accent_line_start)/(accent_line_end-accent_line_start)
                ch = (accent_line_length/2)*t
                accent_line_obj.set_data([0.5-ch, 0.5+ch], [accent_line_y, accent_line_y])
        return [suptitle_obj, subtitle_obj, accent_line_obj]

    anim   = animation.FuncAnimation(fig, update, frames=total_frames, interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3000,
                                    extra_args=['-vcodec','libx264','-pix_fmt','yuv420p'])
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
