# -*- coding: utf-8 -*-
"""
espresso_charts.py — Espresso Charts Library
=============================================
Chart functions for Instagram carousels (4:5) and Reels (9:16).

Static charts:  eSingleBarChartNewInstagram, eMultiLineChartInstagram,
                eStemChartNewInstagram, eDonutChartInstagram, eCoverTileInstagram

Animated charts: eSingleBarChartAnimateInstagram, eMultiLineChartAnimateInstagram,
                 eStemChartAnimateInstagram, eDonutChartAnimateInstagram,
                 eCoverTileAnimateInstagram

Helpers:         save_chart, fetch_fred_series, add_custom_annotations,
                 add_lines, add_text, eConcatenateMP4

Usage (Colab):
    !pip install matplotlib pandas numpy scikit-learn requests
    !wget -q https://raw.githubusercontent.com/<you>/espresso-charts/main/espresso_charts.py
    from espresso_charts import *
"""

# ============================================================================
# IMPORTS
# ============================================================================
import os
import io
import subprocess
import tempfile
import warnings
from decimal import Decimal
from io import StringIO
from urllib.request import urlopen

import base64
from pathlib import Path
from datetime import datetime

import json
import time

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
# ESPRESSO CHARTS STYLE CONFIG
# ============================================================================
color_blue = '#3F5B83'
color_orange = '#DD6B20'
color_green = '#4D5523'
color_sand = '#CDAF7B'
face_color = '#F5F0E6'


def save_chart(fig, path, dpi=200):
    """Save chart with locked dimensions. Never uses bbox_inches='tight'."""
    fig.savefig(path, dpi=dpi, bbox_inches=None, pad_inches=0, facecolor=fig.get_facecolor())


def fetch_fred_series(series_id, api_key=None, start_date="2010-01-01"):
    """Fetch a FRED time series. Set api_key or FRED_API_KEY env var."""
    if api_key is None:
        api_key = os.environ.get("FRED_API_KEY", "")
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
    }

    data = requests.get(url, params=params).json()
    print(f"Data: {data}")
    df = pd.DataFrame(data["observations"])[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["series_id"] = series_id

    return df

def eSingleBarChartNewInstagram(
    df_chart,
    col_dim,
    col_measure,
    txt_suptitle,    # Main Headline (big, Serif) — rendered via fig.suptitle()
    txt_subtitle,    # Context / Secondary (smaller, Sans) — rendered via ax.set_title()
    txt_label,       # Source / X-axis label
    pos_text=None,
    pos_label=-1,
    num_format="{:.0f}",
    num_divisor=1,
    bar_height=None,
    bar_color=None,
    hide_left_spine=False,
    offset_label_x=0,
    min_val=None,
    max_val=None,
    factor_limit_x=1.0,
    aspect_ratio=None,
    label_custom_offset=None,
    suptitle_size=26,
    subtitle_size=14,
    label_size=12,

    # --- THEME (coffee) ---
    suptitle_color='#4b2e1a',
    subtitle_color='#4b2e1a',
    txt_label_color='#857052',
    tick_label_color='#3c3325',
    value_label_color='#4b2e1a',
    face_color='#f5f0e6',
    coffee_palette=('#9d8561','#857052','#6c5c43','#544734','#3c3325','#79664a','#d9d0c1','#0b0a07'),

    suptitle_font_weight='normal',
    subtitle_font_weight='normal',
    txt_label_font_weight='normal',

    # --- CUSTOM FONTS ---
    font='DejaVu Sans',
    suptitle_font='DejaVu Serif',
    subtitle_font='DejaVu Sans',
    suptitle_y_custom=1,
    subtitle_pad_custom=40,

    # --- ZERO LINE ---
    show_zero_line=False,
    zero_line_color='#4b2e1a',
    zero_line_style='--',
    zero_line_width=1.0,

    # --- INSTAGRAM 4x5 FORMAT ---
    instagram=True,
    px_width=1080,
    px_height=1350,
    dpi=200,

    # --- EXTRAS ---
    sep_index=None,
    sep_color='#4b2e1a',
    sep_style='-',
    sep_width=1.5,
    x_subtitle_offset=0.55
):

    # Base RC
    plt.rcdefaults()
    plt.rcParams['font.family'] = font

    # --- FIGURE SETUP ---
    if instagram:
        figsize = (px_width / dpi, px_height / dpi)
        # Turn off constrained_layout to allow manual subplots_adjust
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)

        # Pushing the plot area down to 0.72 leave the top 28% for text
        fig.subplots_adjust(top=0.85, bottom=0.1, left=0.1, right=0.8)

        suptitle_y = 0.93 if suptitle_y_custom is None else suptitle_y_custom
        subtitle_pad = 25 if subtitle_pad_custom is None else subtitle_pad_custom
    else:
        fig, ax = plt.subplots(figsize=(8, 10), dpi=160, facecolor=face_color)
        fig.subplots_adjust(top=0.82, bottom=0.12)
        suptitle_y = 0.96
        subtitle_pad = 20

    ax.set_facecolor(face_color)

    if bar_color is None:
        bar_color = coffee_palette[0]

    # --- TEXT HIERARCHY ---
    # 1. Main Headline (suptitle — big, Serif)
    fig.suptitle(
        txt_suptitle, y=suptitle_y, fontsize=suptitle_size, color=suptitle_color,
        ha='center', va='top', fontweight=suptitle_font_weight,
        fontfamily=suptitle_font
    )

    # 2. Subtitle (ax.set_title — smaller, Sans)
    ax.set_title(
        txt_subtitle, pad=subtitle_pad, color=subtitle_color,
        size=subtitle_size, fontweight=subtitle_font_weight,
        ha='center', va='top',
        x=x_subtitle_offset,
        fontfamily=subtitle_font
    )

    # 3. Source / X-axis Label
    ax.set_xlabel(
        txt_label, color=txt_label_color, labelpad=15,
        size=label_size, fontweight=txt_label_font_weight, x=x_subtitle_offset
    )

    # --- PLOTTING ---
    if bar_height is None:
        bar_height = 0.75

    bars = ax.barh(
        df_chart[col_dim], df_chart[col_measure],
        color=bar_color, height=bar_height, zorder=3
    )

    # --- SPINES & TICKS ---
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
    ax.set_xticks([])
    ax.tick_params(axis='x', colors=face_color)

    # X limits
    if min_val is None: min_val = float(df_chart[col_measure].min())
    if max_val is None: max_val = float(df_chart[col_measure].max())
    ax.set_xlim(min(min_val * factor_limit_x, 0), max(max_val * factor_limit_x, 0))

    if show_zero_line:
        ax.axvline(0, color=zero_line_color, linestyle=zero_line_style, linewidth=zero_line_width, zorder=2)

    # --- ANNOTATIONS ---
    for idx, (patch, value) in enumerate(zip(bars, df_chart[col_measure])):
        category = str(df_chart[col_dim].iloc[idx])
        y_center = patch.get_y() + patch.get_height() / 2
        x_start = patch.get_x()
        x_end = x_start + patch.get_width()
        is_positive = (x_end >= x_start)

        ha_cat = 'left' if is_positive else 'right'
        off_cat = 8 + offset_label_x if is_positive else -8 - offset_label_x
        ax.annotate(
            category, xy=(x_start if is_positive else x_end, y_center),
            xytext=(off_cat, 0), textcoords='offset points',
            ha=ha_cat, va='center', fontsize=label_size, color=tick_label_color, zorder=6,
            bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color, edgecolor='none', alpha=0.8)
        )

        val = value / num_divisor
        formatted = num_format.format(val) if num_format else str(val)
        custom_off = (label_custom_offset.get(idx, 0) if isinstance(label_custom_offset, dict) else 0)
        ha_val = 'left' if is_positive else 'right'
        off_val = 8 + custom_off if is_positive else -8 - custom_off

        ax.annotate(
            formatted, xy=(x_end, y_center), xytext=(off_val, 0),
            textcoords='offset points', ha=ha_val, va='center',
            fontsize=label_size, color=value_label_color, zorder=6
        )

    if aspect_ratio is not None:
        ax.set_box_aspect(aspect_ratio)

    return fig, ax


def eMultiLineChartInstagram(
    df_chart,
    col_dim,
    col_measure_list,
    txt_suptitle,
    txt_subtitle,
    txt_label,
    pos_text,
    pos_label=-1,
    num_format="{:.0f}",
    num_divisor=1,
    x_ticks=None,
    x_tick_labels=None,
    tick_color='#4B2E1A',
    x_tick_size=10,
    aspect_ratio=1.0,
    line_colors=None,
    line_styles=None,
    line_widths=None,
    line_labels=None,
    suptitle_color='#4b2e1a',
    subtitle_color='#4b2e1a',
    txt_label_color='#857052',
    face_color='#F7F5F2',
    suptitle_font_weight='normal',
    suptitle_font='DejaVu Serif',
    subtitle_font_weight='normal',
    subtitle_font='DejaVu Sans',
    txt_label_font_weight='normal',
    show_zero_line=False,
    zero_line_color='#857052',
    zero_line_style='--',
    zero_line_width=1.0,
    zero_line_at=0,
    px=1080,
    py=1350,
    dpi=200,
    suptitle_size=26,
    subtitle_size=14,
    label_size=12,
    bottom_note_size=10,
    y_limits=None,
    suptitle_y=0.98,
    subtitle_y=0.94,
    text_offset_y=None,
    shade_between=None,
    shade_color='#c8b8a8',
    shade_alpha=0.25,
    shade_x=None,
    show_y_axis=False,
    y_ticks=None,
    y_tick_color='#857052',
    y_tick_size=10,
    y_num_format=None,
    show_legend=False,
    legend_labels_custom=None,  # NEW: separate legend labels (overrides line_labels in legend)
    legend_loc='upper left',
    legend_font_size=10,
    legend_text_color='#857052',
    legend_ncol=1,
    legend_bbox=(0, 1.02),
    chart_top_margin=0.15
):
    """
    Multi-line chart formatted for Instagram portrait (1080x1350px, 4:5 ratio).
    """

    # ---- Matplotlib defaults ----
    plt.rcdefaults()
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.size'] = 10

    # ---- Figure / Axes (Portrait format) ----
    figsize = (px / dpi, py / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)

    ax.set_facecolor(face_color)

    # ---- Defaults for colors and styles ----
    default_colors = ['#9d8561', '#857052', '#6c5c43', '#544734', '#3c3325']
    colors = line_colors if line_colors is not None else default_colors
    styles = line_styles if line_styles is not None else ['-'] * len(col_measure_list)
    widths = line_widths if line_widths is not None else [0.9] * len(col_measure_list)
    labels = line_labels if line_labels is not None else list(col_measure_list)

    # Safety: align list lengths
    if len(styles) < len(col_measure_list):
        styles = (styles * ((len(col_measure_list) // len(styles)) + 1))[:len(col_measure_list)]
    if len(widths) < len(col_measure_list):
        widths = (widths * ((len(col_measure_list) // len(widths)) + 1))[:len(col_measure_list)]
    if len(colors) < len(col_measure_list):
        colors = (colors * ((len(col_measure_list) // len(colors)) + 1))[:len(col_measure_list)]
    if len(labels) < len(col_measure_list):
        labels = (labels * ((len(col_measure_list) // len(labels)) + 1))[:len(col_measure_list)]

    # ---- Titles and labels ----
    ax.text(
        0.5, suptitle_y,
        txt_suptitle,
        fontsize=suptitle_size,
        color=suptitle_color,
        fontweight=suptitle_font_weight,
        family=suptitle_font,
        ha='center', va='top',
        transform=ax.transAxes
    )

    ax.text(
        0.5, subtitle_y,
        txt_subtitle,
        fontsize=subtitle_size,
        color=subtitle_color,
        fontweight=subtitle_font_weight,
        family=subtitle_font,
        ha='center', va='top',
        transform=ax.transAxes
    )

    ax.set_xlabel(
        txt_label,
        color=txt_label_color,
        labelpad=10,
        size=bottom_note_size,
        fontweight=txt_label_font_weight
    )

    # ---- Plot lines ----
    x = df_chart[col_dim]
    for idx, col_measure in enumerate(col_measure_list):
        ax.plot(
            x,
            df_chart[col_measure],
            color=colors[idx],
            linestyle=styles[idx],
            linewidth=widths[idx],
            zorder=9
        )

    # ---- Aesthetics ----
    for side in ['top', 'right', 'bottom']:
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.tick_params(
        axis='x',
        colors=tick_color,
        labelsize=x_tick_size
    )
    fig.patch.set_facecolor(face_color)
    fig.patch.set_edgecolor(face_color)
    fig.patch.set_linewidth(0)
    fig.patch.set_alpha(1)

    # ---- X ticks / labels ----
    if x_ticks is None:
        try:
            x_ticks = [x.iloc[0], x.iloc[-1]]
        except Exception:
            x_ticks = [min(x), max(x)]

    if x_tick_labels is None:
        x_tick_labels = x_ticks

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels)

    # ---- Y axis (optional) ----
    if show_y_axis:
        if y_ticks is not None:
            ax.set_yticks(y_ticks)

        fmt = y_num_format if y_num_format is not None else num_format

        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: fmt.format(v / num_divisor))
        )

        ax.tick_params(
            axis='y',
            labelleft=True,
            colors=y_tick_color,
            labelsize=y_tick_size,
            length=4,
            width=0.6
        )

        ax.spines['left'].set_visible(True)
        ax.spines['left'].set_linewidth(0.6)
        ax.spines['left'].set_color(y_tick_color)
    else:
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)

    # ---- Optional legend ----
    if show_legend:
        # Use custom legend labels if provided, otherwise use line_labels
        legend_labels = legend_labels_custom if legend_labels_custom is not None else labels

        leg = ax.legend(
            legend_labels,
            loc=legend_loc,
            bbox_to_anchor=legend_bbox,
            ncol=legend_ncol,
            frameon=False,
            fontsize=legend_font_size
        )

        if legend_text_color is not None:
            for txt in leg.get_texts():
                txt.set_color(legend_text_color)

    # ---- Zero line ----
    if show_zero_line:
        ax.axhline(zero_line_at, color=zero_line_color,
                   linestyle=zero_line_style,
                   linewidth=zero_line_width, zorder=8)

    # ---- Numeric value annotations ----
    n_rows = len(df_chart)
    for pos in (pos_text or []):
        if pos < 0:
            pos = n_rows + pos
        if not (0 <= pos < n_rows):
            continue
        for idx, col_measure in enumerate(col_measure_list):
            raw_val = df_chart[col_measure].iloc[pos]
            value = raw_val / num_divisor
            try:
                formatted = num_format.format(value)
            except Exception:
                formatted = str(value)

            offset_val = (
                text_offset_y[idx]
                if isinstance(text_offset_y, (list, tuple))
                else (text_offset_y or 0)
            )
            ax.text(
                x.iloc[pos],
                raw_val + offset_val,
                formatted,
                ha='center', va='bottom',
                color=colors[idx],
                fontsize=label_size, zorder=11,
                bbox=dict(boxstyle='square,pad=0.1',
                          facecolor=face_color, edgecolor=face_color, alpha=0.8)
            )

    # ---- Per-line text labels ----
    if pos_label is not None:
        if pos_label < 0:
            pos_label_eff = n_rows + pos_label
        else:
            pos_label_eff = pos_label
        if 0 <= pos_label_eff < n_rows:
            for idx, col_measure in enumerate(col_measure_list):
                x_i = x.iloc[pos_label_eff]
                y_i = df_chart[col_measure].iloc[pos_label_eff]

                ax.text(
                    x_i, y_i,
                    str(labels[idx]),
                    ha='left', va='center',
                    color=colors[idx],
                    fontsize=label_size, zorder=11,
                    fontweight=txt_label_font_weight,
                    bbox=dict(boxstyle='square,pad=0.1',
                              facecolor=face_color, edgecolor=face_color, alpha=0.8)
                )

    # ---- Optional shaded area ----
    if shade_between is not None:
        col_low, col_high = shade_between
        y1 = df_chart[col_low]
        y2 = df_chart[col_high]

        if shade_x is None:
            ax.fill_between(
                x, y1, y2,
                color=shade_color,
                alpha=shade_alpha,
                zorder=1
            )
        else:
            x_start, x_end = shade_x
            mask = (x >= x_start) & (x <= x_end)
            ax.fill_between(
                x[mask], y1[mask], y2[mask],
                color=shade_color,
                alpha=shade_alpha,
                zorder=1
            )

    # ---- Aspect ratio ----
    ax.set_box_aspect(aspect_ratio)

    # ---- Y-axis limits ----
    if y_limits is not None:
        ax.set_ylim(y_limits)

    # REMOVED plt.show() and plt.close() so you can add text after!

    return fig, ax


def eStemChartNewInstagram(
    df_chart,
    col_dim,
    col_measure_a,
    col_measure_b=None,
    col_category_pos=None,
    txt_suptitle="",
    suptitle_y=0.955,  # Adjusted for 4:5 ratio
    txt_subtitle="",
    txt_label="",
    num_format="{:.0f}",
    num_divisor=1,
    offset=0.1,
    x_tick_label_y_offset=0,
    marker_size=4,
    line_width=0.8,
    suptitle_color="#4b2e1a",
    subtitle_color="#4b2e1a",
    axis_label_color="#79664a",
    tick_label_color="#3c3325",
    face_color="#F7F5F2",
    color_a="#a58e6c",
    color_b="#573D09",
    year_label_a=None,
    year_label_b=None,
    label_a_offset_x=1,
    label_b_offset_x=1,
    label_a_offset_y=1,
    label_b_offset_y=1,
    instagram=True,
    px_width=1080,       # width in pixels
    px_height=1350,      # height in pixels (4:5 ratio)
    dpi=200,
    suptitle_size=26,
    subtitle_size=14,
    label_size=12,
    subtitle_pad=90,        # Adjusted for taller format
    labelpad=10,
    aspect_ratio=None,
    rotate_labels=False,
    xtick_align_ha="center",
    xtick_align_va="bottom",
    value_label_offset_pts=6,
    x_axis_line_width=0.8,
    x_axis_line_color="#857052",
    line_format_a="--",
    line_format_b="--",
    value_label_custom_offset=None,
    show_legend=False,
    legend_labels=None,  # tuple/list: (labelA, labelB)
    legend_loc='upper right',
    legend_font_size=10,
    legend_frame=False,
    legend_text_color='#3c3325',
    legend_bbox_to_anchor=None,  # tuple (x, y) for fine positioning
    y_min=None,  # Minimum y-axis limit
    y_max=None,  # Maximum y-axis limit
    font='DejaVu Sans',        # Base font for labels and ticks
    suptitle_font='DejaVu Serif',
    subtitle_font='DejaVu Sans',
):
    # --- Matplotlib defaults ---
    plt.rcdefaults()
    plt.rcParams['font.family'] = 'DejaVu Sans'

    # --- Figure setup for 4:5 aspect ratio ---
    if instagram:
        figsize = (px_width/dpi, px_height/dpi)  # 5.4 x 6.75 inches at 200 dpi
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi,
                               facecolor=face_color, constrained_layout=True)
    else:
        fig, ax = plt.subplots(figsize=(8, 10), dpi=160, facecolor=face_color)

    ax.set_facecolor(face_color)

    # --- Titles ---
    fig.suptitle(txt_suptitle, y=suptitle_y, fontsize=suptitle_size,
                 color=suptitle_color, fontweight="medium", fontfamily=suptitle_font)
    ax.set_title(txt_subtitle, pad=subtitle_pad, fontsize=subtitle_size,
                 color=subtitle_color, fontweight="light", fontfamily=subtitle_font)
    ax.set_xlabel(txt_label, color=axis_label_color, labelpad=labelpad,
                  size=label_size, fontweight="light")

    # --- Category positions ---
    xpos = np.arange(len(df_chart)) if col_category_pos is None else np.asarray(df_chart[col_category_pos])
    cats = df_chart[col_dim].tolist()

    # --- Series A ---
    y_a = df_chart[col_measure_a].to_numpy() / num_divisor
    markerline, stemlines, baseline = ax.stem(xpos - offset, y_a,
                                              markerfmt="o", linefmt=line_format_a, basefmt=" ")
    plt.setp(markerline, color=color_a, markersize=marker_size,
             linewidth=line_width, zorder=2)
    plt.setp(stemlines, color=color_a, linewidth=line_width, zorder=1)

    # --- Series B (optional) ---
    if col_measure_b is not None:
        y_b = df_chart[col_measure_b].to_numpy() / num_divisor
        markerline, stemlines, baseline = ax.stem(xpos + offset, y_b,
                                                  markerfmt="o", linefmt=line_format_b, basefmt=" ")
        plt.setp(markerline, color=color_b, markersize=marker_size,
                 linewidth=line_width, zorder=2)
        plt.setp(stemlines, color=color_b, linewidth=line_width, zorder=1)

    # --- Spines ---
    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_linewidth(0)

    # --- X-axis line at y=0 ---
    ax.axhline(0, color=x_axis_line_color, linewidth=x_axis_line_width)

    # --- Y-axis limits ---
    if y_min is not None or y_max is not None:
        current_min, current_max = ax.get_ylim()
        ax.set_ylim(
            y_min if y_min is not None else current_min,
            y_max if y_max is not None else current_max
        )

    # --- Labels under stems ---
    ax.set_xticks(xpos)
    ax.set_xticklabels(
        cats,
        color=tick_label_color,
        va=xtick_align_va, ha=xtick_align_ha,
        fontsize=label_size,
        rotation=90 if rotate_labels else 0,
        bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="white", alpha=0.7)
    )
    # Apply manual offsets
    for label in ax.get_xticklabels():
        x0, y0 = label.get_position()
        label.set_position((x0, y0 + x_tick_label_y_offset))
    ax.tick_params(axis="x", length=0)

    # Remove y ticks completely
    ax.set_yticks([])

    # --- Labels on Series A points ---
    for i, val in enumerate(y_a):
        text = num_format.format(val)
        base_offset = value_label_offset_pts if val >= 0 else -value_label_offset_pts
        custom_offset = 0
        if value_label_custom_offset and i in value_label_custom_offset:
            custom_offset = value_label_custom_offset[i]
        ax.annotate(
            text,
            xy=(xpos[i] - offset, val),
            xytext=(0, base_offset + custom_offset),
            textcoords="offset points",
            ha="center",
            va="bottom" if val >= 0 else "top",
            fontsize=label_size,
            color=color_a,
            bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="white", alpha=0.7),
            zorder=10
        )

    # --- Labels on Series B points ---
    if col_measure_b is not None:
        for i, val in enumerate(y_b):
            text = num_format.format(val)
            base_offset = value_label_offset_pts if val >= 0 else -value_label_offset_pts
            custom_offset = 0
            if value_label_custom_offset and i in value_label_custom_offset:
                custom_offset = value_label_custom_offset[i]
            ax.annotate(
                text,
                xy=(xpos[i] + offset, val),
                xytext=(0, base_offset + custom_offset),
                textcoords="offset points",
                ha="center",
                va="bottom" if val >= 0 else "top",
                fontsize=label_size,
                color=color_b,
                bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="white", alpha=0.7),
                zorder=10
            )

    # --- Year labels (optional side annotations) ---
    if year_label_a:
        ax.text(
            xpos[0] + label_a_offset_x, label_a_offset_y,
            str(year_label_a),
            color=color_a, ha="left", va="bottom", rotation=90, fontsize=label_size,
            bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="white", alpha=0.8)
        )
    if col_measure_b is not None and year_label_b:
        ax.text(
            xpos[0] + label_b_offset_x, label_b_offset_y,
            str(year_label_b),
            color=color_b, ha="left", va="bottom", rotation=90, fontsize=label_size,
            bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="white", alpha=0.8)
        )

    # --- Legend ---
    if show_legend:
        handles = []
        labels = []

        # Add Series A to legend
        line_a = plt.Line2D([0], [0], color=color_a, linewidth=line_width,
                           linestyle=line_format_a, marker='o', markersize=marker_size)
        handles.append(line_a)
        labels.append(legend_labels[0] if legend_labels else 'Series A')

        # Add Series B to legend if it exists
        if col_measure_b is not None:
            line_b = plt.Line2D([0], [0], color=color_b, linewidth=line_width,
                               linestyle=line_format_b, marker='o', markersize=marker_size)
            handles.append(line_b)
            labels.append(legend_labels[1] if legend_labels and len(legend_labels) > 1 else 'Series B')

        legend = ax.legend(handles, labels,
                          loc=legend_loc,
                          fontsize=legend_font_size,
                          frameon=legend_frame,
                          bbox_to_anchor=legend_bbox_to_anchor)

        # Set legend text color
        for text in legend.get_texts():
            text.set_color(legend_text_color)

    # --- Aspect ratio ---
    if aspect_ratio is not None:
        ax.set_box_aspect(aspect_ratio)

    return fig, ax


def eDonutChartInstagram(
    df_chart,
    col_value,
    col_label=None,
    col_inner=None,
    txt_suptitle="",
    txt_subtitle="",
    txt_label="",
    num_format="{:.0f}%",
    num_divisor=1,
    radius_outer=0.9,
    radius_inner=0.65,
    wedge_width=0.3,
    labeldistance=1.05,
    pctdistance_outer=0.8,
    pctdistance_inner=0.75,
    show_pct=True,
    autopct_outer=True,
    autopct_inner=True,
    colors=None,
    pct_colors=None,
    label_colors=None,
    center_text=None,
    center_text_color="#4b2e1a",
    center_text_size=12,
    center_text_weight="normal",
    suptitle_color='#4b2e1a',
    subtitle_color='#4b2e1a',
    txt_label_color='#857052',
    face_color='#F7F5F2',
    suptitle_font_weight='medium',
    subtitle_font_weight='light',
    txt_label_font_weight='light',
    suptitle_size=26,
    subtitle_size=14,
    label_size=10,
    bottom_note_size=10,
    font='DejaVu Sans',
    suptitle_font='DejaVu Serif',
    subtitle_font='DejaVu Sans',
    figsize=(8, 8),
    dpi=200,
    px=1080,
    instagram=True,
    instagram_format='4x5'    # New: '1x1' or '4x5'
):
    """
    Donut (single or double-ring) chart with coffee-style defaults.
    Titles/labels use fig.text so the donut stays square & centered.
    Supports Instagram 1x1 (square) or 4x5 (portrait) formats.
    """

    plt.rcdefaults()
    plt.rcParams['font.family'] = font
    plt.rcParams['font.size'] = 12

    # Calculate figsize based on format
    if instagram:
        if instagram_format == '4x5':
            # Instagram portrait: 1080x1350 pixels
            figsize = (px/dpi, (px * 1.25)/dpi)
        else:
            # Instagram square: 1080x1080 pixels
            figsize = (px/dpi, px/dpi)
    else:
        figsize = (8, 8)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi,
                       facecolor=face_color, constrained_layout=True)

    # ---- Defaults for colors ----
    default_colors = ['#d9d0c1', '#79664a', '#9d8561',
                      '#857052', '#6c5c43', '#544734', '#3c3325']
    if colors is None:
        colors = default_colors

    # ---- Place titles with fig.text (outside axes) ----
    if txt_suptitle:
        fig.text(0.5, 0.97, txt_suptitle, ha="center", va="top",
                fontsize=suptitle_size, color=suptitle_color, weight=suptitle_font_weight,
                fontfamily=suptitle_font)
    if txt_subtitle:
        fig.text(0.5, 0.91, txt_subtitle, ha="center", va="top",
                fontsize=subtitle_size, color=subtitle_color, weight=subtitle_font_weight,
                fontfamily=subtitle_font)
    if txt_label:
        fig.text(0.5, 0.04, txt_label, ha="center", va="bottom",
                fontsize=bottom_note_size, color=txt_label_color, weight=txt_label_font_weight)

    # ---- Labels ----
    labels = df_chart[col_label].astype(str) if col_label is not None else None

    # ---- Autopct helper ----
    def autopct_func(pct):
        try:
            return num_format.format(pct)
        except Exception:
            return f"{pct:.0f}%"

    outer_autopct = autopct_func if (show_pct and autopct_outer) else None
    inner_autopct = autopct_func if (show_pct and autopct_inner) else None

    # ---- Outer ring ----
    wedges, texts, autotexts = ax.pie(
        df_chart[col_value] / num_divisor,
        radius=radius_outer,
        labels=labels,
        labeldistance=labeldistance,
        colors=colors,
        wedgeprops=dict(width=wedge_width),
        startangle=90,
        autopct=outer_autopct,
        pctdistance=pctdistance_outer,
        textprops={'fontsize': label_size}
    )

    if label_colors:
        for i, t in enumerate(texts):
            if i < len(label_colors):
                t.set_color(label_colors[i])
    if pct_colors:
        for i, t in enumerate(autotexts):
            if i < len(pct_colors):
                t.set_color(pct_colors[i])

    # ---- Inner ring ----
    if col_inner:
        wedges2, texts2, autotexts2 = ax.pie(
            df_chart[col_inner] / num_divisor,
            radius=radius_inner,
            colors=colors,
            wedgeprops=dict(width=wedge_width),
            startangle=90,
            autopct=inner_autopct,
            pctdistance=pctdistance_inner,
            textprops={'fontsize': label_size}
        )
        if pct_colors:
            for i, t in enumerate(autotexts2):
                if i < len(pct_colors):
                    t.set_color(pct_colors[i])

    # ---- Center text ----
    if center_text:
        ax.text(
            0, 0, center_text,
            ha="center", va="center",
            fontsize=center_text_size,
            color=center_text_color,
            fontweight=center_text_weight,
            linespacing=1.2
        )

    # ---- Aesthetics ----
    for side in ['top', 'right', 'left', 'bottom']:
        ax.spines[side].set_linewidth(0)

    fig.patch.set_facecolor(face_color)
    fig.patch.set_edgecolor(face_color)
    fig.patch.set_linewidth(0)
    fig.patch.set_alpha(1)

    # 🔹 Force square donut
    ax.set_aspect("equal", adjustable="box")

    plt.show()
    plt.close()

    return fig, ax


def add_custom_annotations(ax, annotations):
    """
    Add text annotations to any matplotlib axes object

    annotations: list of dicts with keys:
        {
            'text': 'Important point!',
            'xy': (x, y),              # Position of text
            'color': '#4b2e1a',
            'fontsize': 12,
            'ha': 'center',
            'va': 'center',
            'bbox': {...},             # Optional background box
            'frame': True/False,       # Whether to show frame (default: True)
            'frame_color': '#857052',  # Frame edge color
            'frame_alpha': 0.9,        # Frame transparency
            'bg_color': 'white'        # Background color
        }
    """
    for anno in annotations:
        bbox_dict = None

        if anno.get('frame', True):  # Frame shown by default
            bbox_dict = anno.get('bbox', dict(
                boxstyle='round,pad=0.5',
                facecolor=anno.get('bg_color', 'white'),
                edgecolor=anno.get('frame_color', anno.get('color', '#857052')),
                alpha=anno.get('frame_alpha', 0.9)
            ))

        ax.text(
            anno['xy'][0],
            anno['xy'][1],
            anno['text'],
            color=anno.get('color', '#4b2e1a'),
            fontsize=anno.get('fontsize', 12),
            ha=anno.get('ha', 'center'),
            va=anno.get('va', 'center'),
            bbox=bbox_dict
        )
    return ax


def add_lines(ax, lines):
    """
    Add pointing lines/arrows to any matplotlib axes object

    lines: list of dicts with keys:
        {
            'start': (x1, y1),         # Line start point
            'end': (x2, y2),           # Line end point
            'arrow': True,             # Whether to add arrowhead
            'color': '#4b2e1a',
            'linewidth': 1.5,
            'linestyle': '-'
        }
    """
    for line in lines:
        if line.get('arrow', False):
            ax.annotate(
                '',  # Empty text, just the arrow
                xy=line['end'],        # Arrow points here
                xytext=line['start'],  # Arrow starts here
                arrowprops=dict(
                    arrowstyle=line.get('arrowstyle', '->'),
                    color=line.get('color', '#4b2e1a'),
                    lw=line.get('linewidth', 1.5),
                    linestyle=line.get('linestyle', '-')
                )
            )
        else:
            ax.plot(
                [line['start'][0], line['end'][0]],
                [line['start'][1], line['end'][1]],
                color=line.get('color', '#4b2e1a'),
                linewidth=line.get('linewidth', 1.5),
                linestyle=line.get('linestyle', '-')
            )
    return ax

    return ax


# ============================================================================
# HELPER FUNCTION: add_text
# ============================================================================
def add_text(ax, texts):
    """
    Add text elements to any matplotlib axes object

    texts: list of dicts with keys:
        {
            'text': 'Your text here',
            'xy': (x, y),              # Position in data coordinates
            'fontsize': 12,
            'color': '#4b2e1a',
            'ha': 'left',              # horizontal alignment: 'left', 'center', 'right'
            'va': 'bottom',            # vertical alignment: 'top', 'center', 'bottom'
            'fontweight': 'normal',    # 'normal', 'bold', 'light', 'medium'
            'rotation': 0,             # rotation angle in degrees
            'alpha': 1.0,              # transparency (0-1)
            'family': 'DejaVu Sans'    # font family
        }
    """
    for txt in texts:
        ax.text(
            txt['xy'][0],
            txt['xy'][1],
            txt['text'],
            fontsize=txt.get('fontsize', 12),
            color=txt.get('color', '#4b2e1a'),
            ha=txt.get('ha', 'left'),
            va=txt.get('va', 'bottom'),
            fontweight=txt.get('fontweight', 'normal'),
            rotation=txt.get('rotation', 0),
            alpha=txt.get('alpha', 1.0),
            family=txt.get('family', 'DejaVu Sans'),
            linespacing=txt.get('linespacing', 1.2)
        )
    return ax


# ============================================================================
# NEW FUNCTION: eCoverTileInstagram
# ============================================================================
def eCoverTileInstagram(
    txt_suptitle,
    txt_subtitle,
    txt_label="",
    # --- Suptitle styling (Main Headline) ---
    suptitle_color='#4b2e1a',
    suptitle_font='DejaVu Serif',
    suptitle_font_weight='normal',
    suptitle_size=42,
    suptitle_y=0.6,              # vertical position (0-1, from bottom)
    # --- Subtitle styling ---
    subtitle_color='#4b2e1a',
    subtitle_font='DejaVu Sans',
    subtitle_font_weight='normal',
    subtitle_size=18,
    subtitle_y=0.38,           # vertical position (0-1, from bottom)
    # --- Label/source styling ---
    txt_label_color='#857052',
    txt_label_font='DejaVu Sans',
    txt_label_font_weight='light',
    label_size=11,
    label_y=0.06,
    # --- Layout ---
    face_color='#F5F0E6',
    px_width=1080,
    px_height=1350,
    dpi=200,
    # --- Optional decorative line ---
    show_accent_line=True,
    accent_line_color='#3F5B83',
    accent_line_width=4,
    accent_line_y=0.48,        # position between title and subtitle
    accent_line_length=0.15,   # as fraction of width
):
    """
    Create an empty Instagram cover tile (4:5 format) with headline and subheadline.

    Perfect for carousel cover slides that grab attention before showing data.

    Parameters:
    -----------
    txt_suptitle : str
        Main headline text. Use \\n for line breaks.
    txt_subtitle : str
        Subheadline/hook text. Use \\n for line breaks.
    txt_label : str, optional
        Bottom attribution/source text.

    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """

    plt.rcdefaults()
    plt.rcParams['font.family'] = 'DejaVu Sans'

    # Create figure with 4:5 aspect ratio
    figsize = (px_width / dpi, px_height / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color)

    # Remove all axes elements
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Remove all spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Build text list for add_text function
    texts = []

    # Suptitle (large, serif — Main Headline)
    texts.append({
        'text': txt_suptitle,
        'xy': (0.5, suptitle_y),
        'fontsize': suptitle_size,
        'color': suptitle_color,
        'ha': 'center',
        'va': 'center',
        'fontweight': suptitle_font_weight,
        'family': suptitle_font,
        'linespacing': 1.1
    })

    # Subtitle (smaller, sans-serif)
    texts.append({
        'text': txt_subtitle,
        'xy': (0.5, subtitle_y),
        'fontsize': subtitle_size,
        'color': subtitle_color,
        'ha': 'center',
        'va': 'center',
        'fontweight': subtitle_font_weight,
        'family': subtitle_font,
        'linespacing': 1.3
    })

    # Label/source (bottom, small)
    if txt_label:
        texts.append({
            'text': txt_label,
            'xy': (0.5, label_y),
            'fontsize': label_size,
            'color': txt_label_color,
            'ha': 'center',
            'va': 'center',
            'fontweight': txt_label_font_weight,
            'family': txt_label_font
        })

    # Add all text using add_text helper
    add_text(ax, texts)

    # Optional accent line between title and subtitle
    if show_accent_line:
        line_start = 0.5 - (accent_line_length / 2)
        line_end = 0.5 + (accent_line_length / 2)
        ax.plot(
            [line_start, line_end],
            [accent_line_y, accent_line_y],
            color=accent_line_color,
            linewidth=accent_line_width,
            solid_capstyle='round'
        )

    plt.tight_layout(pad=0)

    return fig, ax


# ============================================================================
# EASING HELPERS
# ============================================================================
def _ease_out_cubic(t):
    """Smooth deceleration: fast start, gentle landing."""
    return 1 - (1 - t) ** 3

def _ease_out_quad(t):
    return 1 - (1 - t) ** 2

def _ease_linear(t):
    return t

_EASING = {
    'cubic': _ease_out_cubic,
    'quad': _ease_out_quad,
    'linear': _ease_linear,
}


# ============================================================================
# TYPEWRITER HELPER
# ============================================================================
def _typewriter(full_text, progress, start=0.0, end=0.95):
    """
    Return a substring of *full_text* based on animation progress.

    Parameters
    ----------
    full_text : str   — complete string (may contain \\n)
    progress  : float — overall animation progress 0 → 1
    start     : float — progress value where typing begins
    end       : float — progress value where typing finishes
    """
    if not full_text:
        return ""
    if progress >= end:
        return full_text
    if progress <= start:
        return ""
    local = (progress - start) / (end - start)
    n_chars = int(local * len(full_text))
    return full_text[:n_chars]


# ============================================================================
# 1.  ANIMATED SINGLE BAR CHART  (Reels 9×16)
# ============================================================================
def eSingleBarChartAnimateInstagram(
    df_chart,
    col_dim,
    col_measure,
    txt_suptitle,
    txt_subtitle,
    txt_label,
    # --- animation ---
    duration=8,
    fps=30,
    hold_frames=120,           # 4 s hold at end
    output_file="espresso_bar_animated.mp4",
    easing='cubic',
    # --- typewriter timing (fraction of duration) ---
    tw_suptitle_start=0.0,
    tw_suptitle_end=0.5,
    tw_subtitle_start=0.5,
    tw_subtitle_end=0.95,
    # --- static params (same defaults as eSingleBarChartNewInstagram) ---
    pos_text=None,
    pos_label=-1,
    num_format="{:.0f}",
    num_divisor=1,
    bar_height=None,
    bar_color=None,
    hide_left_spine=False,
    offset_label_x=0,
    min_val=None,
    max_val=None,
    factor_limit_x=1.0,
    aspect_ratio=None,
    label_custom_offset=None,
    suptitle_size=26,
    subtitle_size=14,
    label_size=12,
    suptitle_color='#4b2e1a',
    subtitle_color='#4b2e1a',
    txt_label_color='#857052',
    tick_label_color='#3c3325',
    value_label_color='#4b2e1a',
    face_color='#f5f0e6',
    coffee_palette=('#9d8561','#857052','#6c5c43','#544734','#3c3325',
                   '#79664a','#d9d0c1','#0b0a07'),
    suptitle_font_weight='normal',
    subtitle_font_weight='normal',
    txt_label_font_weight='normal',
    font='DejaVu Sans',
    suptitle_font='DejaVu Serif',
    subtitle_font='DejaVu Sans',
    suptitle_y_custom=0.96,
    subtitle_pad_custom=60,
    show_zero_line=False,
    zero_line_color='#4b2e1a',
    zero_line_style='--',
    zero_line_width=1.0,
    instagram=True,
    px_width=1080,
    px_height=1920,            # 9:16
    dpi=200,
    sep_index=None,
    sep_color='#4b2e1a',
    sep_style='-',
    sep_width=1.5,
    x_subtitle_offset=0.55,
):
    """
    Animated horizontal bar chart for Instagram Reels (9:16).
    Bars grow smoothly from zero; titles type on character by character.
    """
    ease_fn = _EASING.get(easing, _ease_out_cubic)

    plt.rcdefaults()
    plt.rcParams['font.family'] = font

    # --- Figure ---
    if instagram:
        figsize = (px_width / dpi, px_height / dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
        fig.subplots_adjust(top=0.82, bottom=0.08, left=0.10, right=0.80)
        suptitle_y = 0.93 if suptitle_y_custom is None else suptitle_y_custom
        subtitle_pad  = 30   if subtitle_pad_custom  is None else subtitle_pad_custom
    else:
        fig, ax = plt.subplots(figsize=(8, 14), dpi=160, facecolor=face_color)
        fig.subplots_adjust(top=0.82, bottom=0.08)
        suptitle_y = 0.96
        subtitle_pad  = 20

    ax.set_facecolor(face_color)
    if bar_color is None:
        bar_color = coffee_palette[0]

    # --- Titles (start empty — typewriter fills them) ---
    _tw_suptitle_full = txt_suptitle     # main headline → fig.suptitle position
    _tw_subtitle_full = txt_subtitle     # secondary     → ax.title position

    suptitle_obj = fig.suptitle(
        "", y=suptitle_y, fontsize=suptitle_size, color=suptitle_color,
        ha='center', va='top', fontweight=suptitle_font_weight,
        fontfamily=suptitle_font
    )
    ax.set_title(
        "", pad=subtitle_pad, color=subtitle_color, size=subtitle_size,
        fontweight=subtitle_font_weight, ha='center', va='top',
        x=x_subtitle_offset, fontfamily=subtitle_font
    )
    subtitle_obj = ax.title

    ax.set_xlabel(
        txt_label, color=txt_label_color, labelpad=15,
        size=label_size, fontweight=txt_label_font_weight, x=x_subtitle_offset
    )

    # --- Data ---
    dim_vals     = df_chart[col_dim].tolist()
    measure_vals = df_chart[col_measure].tolist()
    n = len(dim_vals)
    if bar_height is None:
        bar_height = 0.75

    if min_val is None: min_val = float(df_chart[col_measure].min())
    if max_val is None: max_val = float(df_chart[col_measure].max())
    ax.set_xlim(min(min_val * factor_limit_x, 0), max(max_val * factor_limit_x, 0))

    bars = ax.barh(dim_vals, [0]*n, color=bar_color, height=bar_height, zorder=3)

    # --- Spines & ticks ---
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
    ax.set_xticks([])
    ax.tick_params(axis='x', colors=face_color)

    if show_zero_line:
        ax.axvline(0, color=zero_line_color, linestyle=zero_line_style,
                   linewidth=zero_line_width, zorder=2)

    # --- Category labels (static) ---
    cat_anns = []
    for idx, patch in enumerate(bars):
        category = str(dim_vals[idx])
        y_center = patch.get_y() + patch.get_height() / 2
        is_positive = measure_vals[idx] >= 0
        ha_cat  = 'left' if is_positive else 'right'
        off_cat = 8 + offset_label_x if is_positive else -8 - offset_label_x
        ann = ax.annotate(
            category, xy=(0, y_center), xytext=(off_cat, 0),
            textcoords='offset points', ha=ha_cat, va='center',
            fontsize=label_size, color=tick_label_color, zorder=6,
            bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                      edgecolor='none', alpha=0.8)
        )
        cat_anns.append(ann)

    # --- Value labels (updated each frame) ---
    val_anns = []
    for idx in range(n):
        y_center = bars[idx].get_y() + bars[idx].get_height() / 2
        ann = ax.annotate(
            "", xy=(0, y_center), xytext=(8, 0), textcoords='offset points',
            ha='left', va='center', fontsize=label_size,
            color=value_label_color, zorder=6
        )
        val_anns.append(ann)

    # --- Animation ---
    total_anim = int(fps * duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)

        # Typewriter
        suptitle_obj.set_text(
            _typewriter(_tw_suptitle_full, progress, tw_suptitle_start, tw_suptitle_end))
        subtitle_obj.set_text(
            _typewriter(_tw_subtitle_full, progress, tw_subtitle_start, tw_subtitle_end))

        for idx, bar in enumerate(bars):
            cur = measure_vals[idx] * progress
            bar.set_width(cur)

            y_c   = bar.get_y() + bar.get_height() / 2
            x_end = bar.get_x() + bar.get_width()
            is_pos = measure_vals[idx] >= 0

            val = cur / num_divisor
            try:    formatted = num_format.format(val)
            except: formatted = str(val)

            c_off = (label_custom_offset.get(idx, 0)
                     if isinstance(label_custom_offset, dict) else 0)
            off = 8 + c_off if is_pos else -8 - c_off

            val_anns[idx].set_text(formatted)
            val_anns[idx].xy = (x_end, y_c)

        return list(bars) + val_anns

    anim = animation.FuncAnimation(fig, update, frames=total_frames,
                                   interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(
        fps=fps, bitrate=3000,
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi,
              savefig_kwargs={'facecolor': face_color})
    print(f"✅ Saved animated bar chart → {output_file}")
    return fig, ax


# ============================================================================
# 2.  ANIMATED MULTI-LINE CHART  (Reels 9×16)
# ============================================================================
def eMultiLineChartAnimateInstagram(
    df_chart,
    col_dim,
    col_measure_list,
    txt_suptitle,
    txt_subtitle,
    txt_label,
    pos_text,
    # --- animation ---
    duration=8,
    fps=30,
    hold_frames=120,
    output_file="espresso_line_animated.mp4",
    easing='cubic',
    tw_suptitle_start=0.0,
    tw_suptitle_end=0.5,
    tw_subtitle_start=0.5,
    tw_subtitle_end=0.95,
    # --- static params ---
    pos_label=-1,
    num_format="{:.0f}",
    num_divisor=1,
    x_ticks=None,
    x_tick_labels=None,
    tick_color='#4B2E1A',
    x_tick_size=10,
    aspect_ratio=None,
    line_colors=None,
    line_styles=None,
    line_widths=None,
    line_labels=None,
    suptitle_color='#4b2e1a',
    subtitle_color='#4b2e1a',
    txt_label_color='#857052',
    face_color='#F7F5F2',
    suptitle_font_weight='normal',
    suptitle_font='DejaVu Serif',
    subtitle_font_weight='normal',
    subtitle_font='DejaVu Sans',
    txt_label_font_weight='normal',
    show_zero_line=False,
    zero_line_color='#857052',
    zero_line_style='--',
    zero_line_width=1.0,
    zero_line_at=0,
    px=1080,
    py=1920,                   # 9:16
    dpi=200,
    suptitle_size=26,
    subtitle_size=14,
    label_size=12,
    bottom_note_size=10,
    y_limits=None,
    suptitle_y=0.98,
    subtitle_y=0.95,
    text_offset_y=None,
    shade_between=None,
    shade_color='#c8b8a8',
    shade_alpha=0.25,
    shade_x=None,
    show_y_axis=False,
    y_ticks=None,
    y_tick_color='#857052',
    y_tick_size=10,
    y_num_format=None,
    show_legend=False,
    legend_labels_custom=None,
    legend_loc='upper left',
    legend_font_size=10,
    legend_text_color='#857052',
    legend_ncol=1,
    legend_bbox=(0, 1.02),
    chart_top_margin=0.15,
):
    """
    Animated multi-line chart for Instagram Reels (9:16).
    Lines draw point-by-point with a leading dot; titles type on.
    """
    ease_fn = _EASING.get(easing, _ease_out_cubic)

    plt.rcdefaults()
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.size'] = 10

    figsize = (px / dpi, py / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color)

    # --- Defaults ---
    default_colors = ['#9d8561', '#857052', '#6c5c43', '#544734', '#3c3325']
    colors = line_colors  if line_colors  is not None else default_colors
    styles = line_styles  if line_styles  is not None else ['-'] * len(col_measure_list)
    widths = line_widths  if line_widths  is not None else [0.9] * len(col_measure_list)
    labels = line_labels  if line_labels  is not None else list(col_measure_list)

    def _pad(lst):
        if len(lst) < len(col_measure_list):
            return (lst * (len(col_measure_list) // len(lst) + 1))[:len(col_measure_list)]
        return lst
    colors, styles, widths, labels = _pad(colors), _pad(styles), _pad(widths), _pad(labels)

    # --- Titles (empty — typewriter fills them) ---
    _tw_suptitle_full = txt_suptitle     # main headline (top)
    _tw_subtitle_full = txt_subtitle     # secondary (below)

    suptitle_text_obj = ax.text(
        0.5, suptitle_y, "", fontsize=suptitle_size, color=suptitle_color,
        fontweight=suptitle_font_weight, family=suptitle_font,
        ha='center', va='top', transform=ax.transAxes
    )
    subtitle_text_obj = ax.text(
        0.5, subtitle_y, "", fontsize=subtitle_size, color=subtitle_color,
        fontweight=subtitle_font_weight, family=subtitle_font,
        ha='center', va='top', transform=ax.transAxes
    )
    ax.set_xlabel(txt_label, color=txt_label_color, labelpad=10,
                  size=bottom_note_size, fontweight=txt_label_font_weight)

    # --- Aesthetics ---
    for side in ['top', 'right', 'bottom']:
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='x', colors=tick_color, labelsize=x_tick_size)
    fig.patch.set_facecolor(face_color)
    fig.patch.set_edgecolor(face_color)
    fig.patch.set_linewidth(0)
    fig.patch.set_alpha(1)

    # --- X ticks ---
    x = df_chart[col_dim]
    if x_ticks is None:
        try:    x_ticks = [x.iloc[0], x.iloc[-1]]
        except: x_ticks = [min(x), max(x)]
    if x_tick_labels is None:
        x_tick_labels = x_ticks
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels)

    # --- Y axis ---
    if show_y_axis:
        if y_ticks is not None:
            ax.set_yticks(y_ticks)
        fmt = y_num_format if y_num_format else num_format
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v, _: fmt.format(v / num_divisor)))
        ax.tick_params(axis='y', labelleft=True, colors=y_tick_color,
                       labelsize=y_tick_size, length=4, width=0.6)
        ax.spines['left'].set_visible(True)
        ax.spines['left'].set_linewidth(0.6)
        ax.spines['left'].set_color(y_tick_color)
    else:
        ax.set_yticks([])

    # --- Limits ---
    if y_limits is not None:
        ax.set_ylim(y_limits)
    else:
        all_v = [v for c in col_measure_list for v in df_chart[c].tolist()]
        m = (max(all_v) - min(all_v)) * 0.1
        ax.set_ylim(min(all_v) - m, max(all_v) + m)

    x_vals = x.tolist()
    xm = (max(x_vals) - min(x_vals)) * 0.02
    ax.set_xlim(min(x_vals) - xm, max(x_vals) + xm)

    if show_zero_line:
        ax.axhline(zero_line_at, color=zero_line_color,
                   linestyle=zero_line_style, linewidth=zero_line_width, zorder=8)

    if aspect_ratio is not None:
        ax.set_box_aspect(aspect_ratio)

    # --- Line & dot objects ---
    line_objects = []
    dot_objects  = []
    for idx in range(len(col_measure_list)):
        ln, = ax.plot([], [], color=colors[idx], linestyle=styles[idx],
                       linewidth=widths[idx], zorder=9)
        line_objects.append(ln)
        dt, = ax.plot([], [], 'o', color=colors[idx], markersize=5, zorder=10)
        dot_objects.append(dt)

    # --- Value annotations for pos_text ---
    n_rows = len(df_chart)
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
                value_targets.append(dict(
                    pos=p, idx=idx, formatted=fmt_s,
                    x=x.iloc[p], y=raw + oy, color=colors[idx]))

    val_objs = []
    for vt in value_targets:
        t = ax.text(vt['x'], vt['y'], '', ha='center', va='bottom',
                    color=vt['color'], fontsize=label_size, zorder=11,
                    bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                              edgecolor=face_color, alpha=0.8))
        t.set_visible(False)
        val_objs.append(t)

    # --- Shade ---
    shade_patch = None
    if shade_between is not None:
        cl, ch = shade_between
        y1, y2 = df_chart[cl], df_chart[ch]
        if shade_x is None:
            shade_patch = ax.fill_between(x, y1, y2, color=shade_color,
                                          alpha=shade_alpha, zorder=1)
        else:
            xs, xe = shade_x
            mask = (x >= xs) & (x <= xe)
            shade_patch = ax.fill_between(x[mask], y1[mask], y2[mask],
                                          color=shade_color, alpha=shade_alpha, zorder=1)
        shade_patch.set_visible(False)

    # --- Animation ---
    total_anim = int(fps * duration)
    total_frames = total_anim + hold_frames
    x_arr = np.array(x.tolist(), dtype=float)

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)

        # Typewriter
        suptitle_text_obj.set_text(
            _typewriter(_tw_suptitle_full, progress, tw_suptitle_start, tw_suptitle_end))
        subtitle_text_obj.set_text(
            _typewriter(_tw_subtitle_full, progress, tw_subtitle_start, tw_subtitle_end))

        reveal = progress * n_rows
        for li, col in enumerate(col_measure_list):
            y_all = df_chart[col].values.astype(float)
            full = int(reveal)
            frac = reveal - full

            if full >= n_rows:
                line_objects[li].set_data(x_arr, y_all)
                dot_objects[li].set_data([x_arr[-1]], [y_all[-1]])
            elif full == 0:
                line_objects[li].set_data([x_arr[0]], [y_all[0]])
                dot_objects[li].set_data([x_arr[0]], [y_all[0]])
            else:
                xs = list(x_arr[:full])
                ys = list(y_all[:full])
                if full < n_rows:
                    xs.append(x_arr[full-1] + frac*(x_arr[full]-x_arr[full-1]))
                    ys.append(y_all[full-1] + frac*(y_all[full]-y_all[full-1]))
                line_objects[li].set_data(xs, ys)
                dot_objects[li].set_data([xs[-1]], [ys[-1]])

        for vi, vt in enumerate(value_targets):
            if vt['pos'] < reveal - 0.5:
                val_objs[vi].set_visible(True)
                val_objs[vi].set_text(vt['formatted'])
            else:
                val_objs[vi].set_visible(False)

        if shade_patch is not None:
            shade_patch.set_visible(progress >= 0.99)

        return line_objects + dot_objects + val_objs

    anim = animation.FuncAnimation(fig, update, frames=total_frames,
                                   interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(
        fps=fps, bitrate=3000,
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi,
              savefig_kwargs={'facecolor': face_color})
    print(f"✅ Saved animated line chart → {output_file}")
    return fig, ax


# ============================================================================
# 3.  ANIMATED STEM CHART  (Reels 9×16)
# ============================================================================
def eStemChartAnimateInstagram(
    df_chart,
    col_dim,
    col_measure_a,
    # --- animation ---
    duration=8,
    fps=30,
    hold_frames=120,
    output_file="espresso_stem_animated.mp4",
    easing='cubic',
    tw_suptitle_start=0.0,
    tw_suptitle_end=0.5,
    tw_subtitle_start=0.5,
    tw_subtitle_end=0.95,
    # --- static params ---
    col_measure_b=None,
    col_category_pos=None,
    txt_suptitle="",
    suptitle_y=0.96,
    txt_subtitle="",
    txt_label="",
    num_format="{:.0f}",
    num_divisor=1,
    offset=0.1,
    x_tick_label_y_offset=0,
    marker_size=4,
    line_width=0.8,
    suptitle_color="#4b2e1a",
    subtitle_color="#4b2e1a",
    axis_label_color="#79664a",
    tick_label_color="#3c3325",
    face_color="#F7F5F2",
    color_a="#a58e6c",
    color_b="#573D09",
    year_label_a=None,
    year_label_b=None,
    label_a_offset_x=1,
    label_b_offset_x=1,
    label_a_offset_y=1,
    label_b_offset_y=1,
    instagram=True,
    px_width=1080,
    px_height=1920,            # 9:16
    dpi=200,
    suptitle_size=26,
    subtitle_size=14,
    label_size=12,
    subtitle_pad=30,
    labelpad=10,
    aspect_ratio=None,
    rotate_labels=False,
    xtick_align_ha="center",
    xtick_align_va="bottom",
    value_label_offset_pts=6,
    x_axis_line_width=0.8,
    x_axis_line_color="#857052",
    line_format_a="--",
    line_format_b="--",
    value_label_custom_offset=None,
    show_legend=False,
    legend_labels=None,
    legend_loc='upper right',
    legend_font_size=10,
    legend_frame=False,
    legend_text_color='#3c3325',
    legend_bbox_to_anchor=None,
    y_min=None,
    y_max=None,
    font='DejaVu Sans',
    suptitle_font='DejaVu Serif',
    subtitle_font='DejaVu Sans',
):
    """
    Animated stem (lollipop) chart for Instagram Reels (9:16).
    Stems grow from baseline; titles type on.
    """
    ease_fn = _EASING.get(easing, _ease_out_cubic)

    plt.rcdefaults()
    plt.rcParams['font.family'] = font

    if instagram:
        figsize = (px_width / dpi, px_height / dpi)
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
        fig.subplots_adjust(top=0.82, bottom=0.08, left=0.12, right=0.92)
    else:
        fig, ax = plt.subplots(figsize=(8, 14), dpi=160, facecolor=face_color)

    ax.set_facecolor(face_color)

    # --- Titles (empty — typewriter, using fig.text for explicit positioning) ---
    _tw_suptitle_full = txt_suptitle
    _tw_subtitle_full = txt_subtitle

    suptitle_obj = fig.text(
        0.5, suptitle_y, "",
        fontsize=suptitle_size, color=suptitle_color,
        fontweight="medium", fontfamily=suptitle_font,
        ha='center', va='top')
    subtitle_obj = fig.text(
        0.5, suptitle_y - 0.05, "",
        fontsize=subtitle_size, color=subtitle_color,
        fontweight="light", fontfamily=subtitle_font,
        ha='center', va='top')
  
    ax.set_xlabel(txt_label, color=axis_label_color, labelpad=labelpad,
                  size=label_size, fontweight="light")

    # --- Positions ---
    xpos = (np.arange(len(df_chart)) if col_category_pos is None
            else np.asarray(df_chart[col_category_pos]))
    cats = df_chart[col_dim].tolist()
    n = len(df_chart)

    y_a_final = df_chart[col_measure_a].to_numpy(dtype=float) / num_divisor
    y_b_final = None
    if col_measure_b is not None:
        y_b_final = df_chart[col_measure_b].to_numpy(dtype=float) / num_divisor

    # --- Spines / baseline ---
    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_linewidth(0)
    ax.axhline(0, color=x_axis_line_color, linewidth=x_axis_line_width)

    # --- Y limits ---
    all_v = list(y_a_final) + (list(y_b_final) if y_b_final is not None else [])
    dmin, dmax = min(all_v), max(all_v)
    margin = (dmax - dmin) * 0.15
    ax.set_ylim(y_min if y_min is not None else (dmin - margin if dmin < 0 else -margin*0.5),
                y_max if y_max is not None else dmax + margin)

    # --- X tick labels ---
    ax.set_xticks(xpos)
    ax.set_xticklabels(
        cats, color=tick_label_color, va=xtick_align_va, ha=xtick_align_ha,
        fontsize=label_size, rotation=90 if rotate_labels else 0,
        bbox=dict(boxstyle="square,pad=0.1", facecolor="white",
                  edgecolor="white", alpha=0.7))
    for lbl in ax.get_xticklabels():
        x0, y0 = lbl.get_position()
        lbl.set_position((x0, y0 + x_tick_label_y_offset))
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])

    # --- Animated elements ---
    stem_a, mark_a, lbl_a = [], [], []
    stem_b, mark_b, lbl_b = [], [], []

    for i in range(n):
        ln, = ax.plot([xpos[i]-offset]*2, [0, 0], line_format_a,
                      color=color_a, linewidth=line_width, zorder=1)
        stem_a.append(ln)
        dt, = ax.plot(xpos[i]-offset, 0, 'o', color=color_a,
                      markersize=marker_size, linewidth=line_width, zorder=2)
        mark_a.append(dt)
        bo = value_label_offset_pts if y_a_final[i] >= 0 else -value_label_offset_pts
        co = (value_label_custom_offset.get(i, 0)
              if value_label_custom_offset and i in value_label_custom_offset else 0)
        t = ax.annotate("", xy=(xpos[i]-offset, 0), xytext=(0, bo+co),
                        textcoords="offset points", ha="center",
                        va="bottom" if y_a_final[i] >= 0 else "top",
                        fontsize=label_size, color=color_a,
                        bbox=dict(boxstyle="square,pad=0.2", facecolor="white",
                                  edgecolor="white", alpha=0.7), zorder=10)
        lbl_a.append(t)

    if y_b_final is not None:
        for i in range(n):
            ln, = ax.plot([xpos[i]+offset]*2, [0, 0], line_format_b,
                          color=color_b, linewidth=line_width, zorder=1)
            stem_b.append(ln)
            dt, = ax.plot(xpos[i]+offset, 0, 'o', color=color_b,
                          markersize=marker_size, linewidth=line_width, zorder=2)
            mark_b.append(dt)
            bo = value_label_offset_pts if y_b_final[i] >= 0 else -value_label_offset_pts
            co = (value_label_custom_offset.get(i, 0)
                  if value_label_custom_offset and i in value_label_custom_offset else 0)
            t = ax.annotate("", xy=(xpos[i]+offset, 0), xytext=(0, bo+co),
                            textcoords="offset points", ha="center",
                            va="bottom" if y_b_final[i] >= 0 else "top",
                            fontsize=label_size, color=color_b,
                            bbox=dict(boxstyle="square,pad=0.2", facecolor="white",
                                      edgecolor="white", alpha=0.7), zorder=10)
            lbl_b.append(t)

    # Year labels (static)
    if year_label_a:
        ax.text(xpos[0]+label_a_offset_x, label_a_offset_y, str(year_label_a),
                color=color_a, ha="left", va="bottom", rotation=90,
                fontsize=label_size,
                bbox=dict(boxstyle="square,pad=0.1", facecolor="white",
                          edgecolor="white", alpha=0.8))
    if y_b_final is not None and year_label_b:
        ax.text(xpos[0]+label_b_offset_x, label_b_offset_y, str(year_label_b),
                color=color_b, ha="left", va="bottom", rotation=90,
                fontsize=label_size,
                bbox=dict(boxstyle="square,pad=0.1", facecolor="white",
                          edgecolor="white", alpha=0.8))

    if aspect_ratio is not None:
        ax.set_box_aspect(aspect_ratio)

    # --- Animation ---
    total_anim = int(fps * duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)

        suptitle_obj.set_text(
            _typewriter(_tw_suptitle_full, progress, tw_suptitle_start, tw_suptitle_end))
        subtitle_obj.set_text(
            _typewriter(_tw_subtitle_full, progress, tw_subtitle_start, tw_subtitle_end))

        for i in range(n):
            ca = y_a_final[i] * progress
            stem_a[i].set_ydata([0, ca])
            mark_a[i].set_ydata([ca])
            lbl_a[i].set_text(num_format.format(ca))
            lbl_a[i].xy = (xpos[i]-offset, ca)

            if y_b_final is not None:
                cb = y_b_final[i] * progress
                stem_b[i].set_ydata([0, cb])
                mark_b[i].set_ydata([cb])
                lbl_b[i].set_text(num_format.format(cb))
                lbl_b[i].xy = (xpos[i]+offset, cb)

        return stem_a + mark_a + lbl_a + stem_b + mark_b + lbl_b

    anim = animation.FuncAnimation(fig, update, frames=total_frames,
                                   interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(
        fps=fps, bitrate=3000,
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi,
              savefig_kwargs={'facecolor': face_color})
    print(f"✅ Saved animated stem chart → {output_file}")
    return fig, ax


# ============================================================================
# 4.  ANIMATED DONUT CHART  (Reels 9×16)
# ============================================================================
def eDonutChartAnimateInstagram(
    df_chart,
    col_value,
    # --- animation ---
    duration=8,
    fps=30,
    hold_frames=120,
    output_file="espresso_donut_animated.mp4",
    easing='cubic',
    tw_suptitle_start=0.0,
    tw_suptitle_end=0.5,
    tw_subtitle_start=0.5,
    tw_subtitle_end=0.95,
    # --- static params ---
    col_label=None,
    col_inner=None,
    txt_suptitle="",
    txt_subtitle="",
    txt_label="",
    num_format="{:.0f}%",
    num_divisor=1,
    radius_outer=0.9,
    radius_inner=0.65,
    wedge_width=0.3,
    labeldistance=1.05,
    pctdistance_outer=0.8,
    pctdistance_inner=0.75,
    show_pct=True,
    autopct_outer=True,
    autopct_inner=True,
    colors=None,
    pct_colors=None,
    label_colors=None,
    center_text=None,
    center_text_color="#4b2e1a",
    center_text_size=12,
    center_text_weight="normal",
    suptitle_color='#4b2e1a',
    subtitle_color='#4b2e1a',
    txt_label_color='#857052',
    face_color='#F7F5F2',
    suptitle_font_weight='medium',
    subtitle_font_weight='light',
    txt_label_font_weight='light',
    suptitle_size=26,
    subtitle_size=14,
    label_size=10,
    bottom_note_size=10,
    font='DejaVu Sans',
    suptitle_font='DejaVu Serif',
    subtitle_font='DejaVu Sans',
    figsize=(8, 8),
    dpi=200,
    px=1080,
    instagram=True,
    instagram_format='9x16',
):
    """
    Animated donut chart for Instagram Reels (9:16).
    Wedges sweep open from top; titles type on.
    """
    ease_fn = _EASING.get(easing, _ease_out_cubic)

    plt.rcdefaults()
    plt.rcParams['font.family'] = font
    plt.rcParams['font.size'] = 12

    if instagram:
        if instagram_format == '9x16':
            figsize = (px / dpi, (px * 16/9) / dpi)     # 1080×1920
        elif instagram_format == '4x5':
            figsize = (px / dpi, (px * 1.25) / dpi)     # 1080×1350
        else:
            figsize = (px / dpi, px / dpi)               # 1080×1080
    else:
        figsize = (8, 8)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color)
    ax.set_aspect("equal", adjustable="box")

    default_colors = ['#d9d0c1', '#79664a', '#9d8561',
                      '#857052', '#6c5c43', '#544734', '#3c3325']
    if colors is None:
        colors = default_colors

    # --- Titles (empty — typewriter) ---
    _tw_suptitle_full = txt_suptitle if txt_suptitle else ""
    _tw_subtitle_full = txt_subtitle if txt_subtitle else ""

    suptitle_fig_obj = fig.text(
        0.5, 0.97, "", ha="center", va="top",
        fontsize=suptitle_size, color=suptitle_color, weight=suptitle_font_weight,
        fontfamily=suptitle_font)
    subtitle_fig_obj = fig.text(
        0.5, 0.92, "", ha="center", va="top",
        fontsize=subtitle_size, color=subtitle_color, weight=subtitle_font_weight,
        fontfamily=subtitle_font)
    if txt_label:
        fig.text(0.5, 0.03, txt_label, ha="center", va="bottom",
                 fontsize=bottom_note_size, color=txt_label_color,
                 weight=txt_label_font_weight)

    for side in ['top', 'right', 'left', 'bottom']:
        ax.spines[side].set_linewidth(0)
    fig.patch.set_facecolor(face_color)
    fig.patch.set_edgecolor(face_color)
    fig.patch.set_linewidth(0)
    fig.patch.set_alpha(1)

    # --- Pre-compute angles ---
    values    = (df_chart[col_value] / num_divisor).values.astype(float)
    total     = values.sum()
    fractions = values / total
    angles_deg = fractions * 360.0
    start_angle = 90.0

    labels_data = (df_chart[col_label].astype(str).tolist()
                   if col_label is not None else [None]*len(values))
    n_wedges = len(values)

    def fmt_pct(pct):
        try:    return num_format.format(pct)
        except: return f"{pct:.0f}%"

    # --- Animation ---
    total_anim = int(fps * duration)
    total_frames = total_anim + hold_frames

    def update(frame):
        ax.clear()
        ax.set_facecolor(face_color)
        ax.set_aspect("equal", adjustable="box")
        for side in ['top', 'right', 'left', 'bottom']:
            ax.spines[side].set_linewidth(0)
        ax.set_xticks([]); ax.set_yticks([])

        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)

        # Typewriter
        suptitle_fig_obj.set_text(
            _typewriter(_tw_suptitle_full, progress, tw_suptitle_start, tw_suptitle_end))
        subtitle_fig_obj.set_text(
            _typewriter(_tw_subtitle_full, progress, tw_subtitle_start, tw_subtitle_end))

        current_start = start_angle
        drawn = []

        for i in range(n_wedges):
            wa = angles_deg[i] * progress
            if wa < 0.5:
                current_start -= wa
                continue

            wedge = mpatches.Wedge(
                center=(0, 0), r=radius_outer,
                theta1=current_start - wa, theta2=current_start,
                width=wedge_width,
                facecolor=colors[i % len(colors)],
                edgecolor=face_color, linewidth=1.5, zorder=3)
            ax.add_patch(wedge)
            drawn.append(wedge)

            mid_rad = np.deg2rad(current_start - wa / 2)

            # Category label
            if labels_data[i] is not None and progress > 0.5:
                lr = radius_outer * labeldistance
                lx, ly = lr * np.cos(mid_rad), lr * np.sin(mid_rad)
                ha = 'left' if lx >= 0 else 'right'
                lc = (label_colors[i] if label_colors and i < len(label_colors)
                      else '#4b2e1a')
                ax.text(lx, ly, labels_data[i], ha=ha, va='center',
                        fontsize=label_size, color=lc)

            # Percentage
            if show_pct and autopct_outer and progress > 0.3:
                pr = radius_outer - wedge_width / 2
                px_c = pr * np.cos(mid_rad) * pctdistance_outer / 0.8
                py_c = pr * np.sin(mid_rad) * pctdistance_outer / 0.8
                pc = (pct_colors[i] if pct_colors and i < len(pct_colors)
                      else '#4b2e1a')
                ax.text(px_c, py_c, fmt_pct(fractions[i]*100),
                        ha='center', va='center', fontsize=label_size, color=pc)

            current_start -= wa

        if center_text:
            ax.text(0, 0, center_text, ha="center", va="center",
                    fontsize=center_text_size, color=center_text_color,
                    fontweight=center_text_weight, linespacing=1.2)

        lim = radius_outer * 1.4
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        return drawn

    anim = animation.FuncAnimation(fig, update, frames=total_frames,
                                   interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(
        fps=fps, bitrate=3000,
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi,
              savefig_kwargs={'facecolor': face_color})
    print(f"✅ Saved animated donut chart → {output_file}")
    return fig, ax


# ============================================================================
# ANIMATED COVER TILE  (Reels 9×16)
# ============================================================================
def eCoverTileAnimateInstagram(
    txt_suptitle,
    txt_subtitle,
    txt_label="",
    # --- animation ---
    duration=1.5,              # seconds of animation build
    hold_duration=1.0,         # seconds to hold the finished frame
    fps=30,
    output_file="espresso_cover_animated.mp4",
    easing='cubic',
    # --- typewriter timing (fraction of duration) ---
    tw_suptitle_start=0.0,
    tw_suptitle_end=0,
    tw_subtitle_start=0,
    tw_subtitle_end=0,
    # --- Suptitle styling (Main Headline) ---
    suptitle_color='#4b2e1a',
    suptitle_font='DejaVu Serif',
    suptitle_font_weight='normal',
    suptitle_size=42,
    suptitle_y=0.6,
    # --- Subtitle styling ---
    subtitle_color='#4b2e1a',
    subtitle_font='DejaVu Sans',
    subtitle_font_weight='normal',
    subtitle_size=18,
    subtitle_y=0.38,
    # --- Label/source styling ---
    txt_label_color='#857052',
    txt_label_font='DejaVu Sans',
    txt_label_font_weight='light',
    label_size=11,
    label_y=0.06,
    # --- Layout ---
    face_color='#F5F0E6',
    px_width=1080,
    px_height=1920,            # 9:16
    dpi=200,
    # --- Optional decorative line ---
    show_accent_line=True,
    accent_line_color='#3F5B83',
    accent_line_width=4,
    accent_line_y=0.48,
    accent_line_length=0.15,
    accent_line_start=0.40,    # progress at which line begins drawing
    accent_line_end=0.65,      # progress at which line is fully drawn
):
    """
    Animated cover tile for Instagram Reels (9:16).

    Title and subtitle type on character by character.
    The accent line draws itself from center outward.
    A hold phase keeps the finished frame on screen.

    Total video length ≈ duration + hold_duration  (default 3.5 s).

    Returns (fig, ax) and saves an MP4.
    """
    ease_fn = _EASING.get(easing, _ease_out_cubic)

    plt.rcdefaults()
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams["savefig.bbox"] = "standard"

    figsize = (px_width / dpi, px_height / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor=face_color)
    ax.set_facecolor(face_color)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    for spine in ax.spines.values():
        spine.set_visible(False)

    # --- Text objects (start empty) ---
    suptitle_obj = ax.text(
        0.5, suptitle_y, "", fontsize=suptitle_size, color=suptitle_color,
        ha='center', va='center', fontweight=suptitle_font_weight,
        fontfamily=suptitle_font, linespacing=1.1, transform=ax.transAxes
    )
    subtitle_obj = ax.text(
        0.5, subtitle_y, "", fontsize=subtitle_size, color=subtitle_color,
        ha='center', va='center', fontweight=subtitle_font_weight,
        fontfamily=subtitle_font, linespacing=1.3, transform=ax.transAxes
    )

    # Label (static — shown from frame 1)
    if txt_label:
        ax.text(
            0.5, label_y, txt_label, fontsize=label_size, color=txt_label_color,
            ha='center', va='center', fontweight=txt_label_font_weight,
            fontfamily=txt_label_font, transform=ax.transAxes
        )

    # --- Accent line (will be redrawn each frame) ---
    accent_line_obj, = ax.plot([], [], color=accent_line_color,
                                linewidth=accent_line_width,
                                solid_capstyle='round', transform=ax.transAxes)

    # --- Animation ---
    total_anim  = int(fps * duration)
    hold_frames = int(fps * hold_duration)
    total_frames = total_anim + hold_frames

    _tw_suptitle = txt_suptitle
    _tw_subtitle = txt_subtitle

    def update(frame):
        progress = 1.0 if frame >= total_anim else ease_fn(frame / total_anim)

        # Typewriter titles
        suptitle_obj.set_text(_typewriter(_tw_suptitle, progress,
                                       tw_suptitle_start, tw_suptitle_end))
        subtitle_obj.set_text(_typewriter(_tw_subtitle, progress,
                                     tw_subtitle_start, tw_subtitle_end))

        # Accent line: grows from center outward
        if show_accent_line:
            if progress <= accent_line_start:
                accent_line_obj.set_data([], [])
            elif progress >= accent_line_end:
                half = accent_line_length / 2
                accent_line_obj.set_data(
                    [0.5 - half, 0.5 + half],
                    [accent_line_y, accent_line_y])
            else:
                t = (progress - accent_line_start) / (accent_line_end - accent_line_start)
                cur_half = (accent_line_length / 2) * t
                accent_line_obj.set_data(
                    [0.5 - cur_half, 0.5 + cur_half],
                    [accent_line_y, accent_line_y])

        return [suptitle_obj, subtitle_obj, accent_line_obj]

    anim = animation.FuncAnimation(fig, update, frames=total_frames,
                                   interval=1000/fps, blit=False)
    writer = animation.FFMpegWriter(
        fps=fps, bitrate=3000,
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
    anim.save(output_file, writer=writer, dpi=dpi,
              savefig_kwargs={'facecolor': face_color, 'pad_inches': 0})

    print(f"✅ Saved animated cover tile → {output_file}  "
          f"({duration + hold_duration:.1f}s @ {fps}fps)")
    return fig, ax


# ============================================================================
# MP4 CONCATENATION
# ============================================================================
def eConcatenateMP4(input_files, output_file="espresso_reel.mp4"):
    """
    Join two or more MP4 files into a single video using ffmpeg.

    All inputs must share the same resolution, fps, and codec.
    (The animated chart functions all produce 1080×1920 / 30fps / H.264.)

    Parameters
    ----------
    input_files : list of str
        Paths to MP4 files in the order they should appear.
    output_file : str
        Path for the combined output.

    Returns
    -------
    output_file : str
        The path that was written.
    """
    if len(input_files) < 2:
        raise ValueError("Need at least 2 files to concatenate.")

    # Verify all files exist
    for f in input_files:
        if not os.path.isfile(f):
            raise FileNotFoundError(f"File not found: {f}")

    # Build ffmpeg concat list file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                      delete=False, dir='.') as tmp:
        for f in input_files:
            abs_path = os.path.abspath(f)
            tmp.write(f"file '{abs_path}'\n")
        list_path = tmp.name

    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_path,
            '-c', 'copy',        # no re-encoding (fast)
            output_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            # If stream copy fails (slightly different codecs), re-encode
            cmd_re = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_path,
                '-vcodec', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '18',
                output_file
            ]
            result = subprocess.run(cmd_re, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"ffmpeg failed:\n{result.stderr}")

    finally:
        os.unlink(list_path)

    print(f"✅ Concatenated {len(input_files)} clips → {output_file}")
    return output_file


# -*- coding: utf-8 -*-
"""
Espresso Charts — Audio Pipeline (ElevenLabs API)
====================================================
Generate voiceover and background music via the ElevenLabs API,
then mix them onto a silent chart animation MP4.

All functions use raw `requests` — no SDK dependency needed.

Setup in Colab
--------------
  from google.colab import userdata
  ELEVENLABS_API_KEY = userdata.get('ELEVENLABS_API_KEY')

Functions
---------
eListVoices           — browse available voices
eGenerateVoiceover    — text → voiceover MP3 (TTS API)
eGenerateMusic        — prompt → instrumental MP3 (Music API)
eAddVoiceover         — overlay voiceover onto video
eAddMusic             — overlay looping music onto video
eAddAudio             — overlay voiceover + music in one pass
eGetDuration          — read duration of any audio/video file
"""


# ============================================================================
# CONSTANTS
# ============================================================================

# Pre-made voice IDs (available to all accounts)
VOICES = {
    "adam":    "pNInz6obpgDQGcFmaJgB",   # American male, deep & warm
    "rachel": "21m00Tcm4TlvDq8ikWAM",   # American female, calm & clear
    "clyde":  "2EiwWnXFnvU5JabPnv8n",   # American male, war veteran
    "domi":   "AZnzlk1XvdvUeBnXmlld",   # American female, strong
    "bella":  "EXAVITQu4vr4xnSDxMaL",   # American female, soft
    "antoni": "ErXwobaYiN019PkySvjV",   # American male, professional
    "josh":   "TxGEqnHWrfWFTfGW9XjX",   # American male, deep narrator
    "sam":    "yoZ06aMxZJJ28mfd3POQ",   # American male, raspy
    "george": "JBFqnCBsd6RMkjVDRZzb",   # British male, warm narrator
}

# TTS model IDs
TTS_MODELS = {
    "v3":              "eleven_v3",               # most expressive (3k chars)
    "multilingual_v2": "eleven_multilingual_v2",  # 10k chars, 70+ languages
    "turbo_v2.5":      "eleven_turbo_v2_5",       # fast, 32 languages
    "flash_v2.5":      "eleven_flash_v2_5",       # ultra-low latency
}

# Suggested music prompts for Espresso Charts Reels
MUSIC_PRESETS = {
    "lofi_coffee": (
        "Gentle lo-fi hip-hop instrumental, soft Rhodes piano chords, "
        "warm vinyl crackle, slow tempo 75 BPM, relaxed coffee shop vibe, "
        "no vocals, ambient and minimal"
    ),
    "editorial_minimal": (
        "Minimal ambient instrumental, soft piano with subtle synth pads, "
        "calm and professional tone, 80 BPM, no percussion, "
        "suitable as background for news or data journalism"
    ),
    "upbeat_data": (
        "Light upbeat instrumental, acoustic guitar and soft percussion, "
        "positive and curious mood, 100 BPM, clean and modern, no vocals"
    ),
    "morning_news": (
        "Warm jazz instrumental, brushed drums, upright bass walking line, "
        "muted trumpet melody, 90 BPM, morning radio feel, no vocals"
    ),
}


# ============================================================================
# UTILITY
# ============================================================================
def eGetDuration(filepath):
    """Return duration in seconds of any video or audio file."""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        filepath
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {filepath}: {r.stderr}")
    return float(json.loads(r.stdout)['format']['duration'])


# ============================================================================
# LIST VOICES
# ============================================================================
def eListVoices(api_key, limit=20):
    """
    Print available voices from your ElevenLabs account.

    Parameters
    ----------
    api_key : str — ElevenLabs API key
    limit   : int — max voices to show
    """
    r = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key}
    )
    r.raise_for_status()
    voices = r.json().get("voices", [])

    print(f"{'Name':<20} {'Voice ID':<28} {'Labels'}")
    print("-" * 76)
    for v in voices[:limit]:
        labels = v.get("labels", {})
        lbl = ", ".join(f"{k}={val}" for k, val in labels.items()) if labels else ""
        print(f"{v['name']:<20} {v['voice_id']:<28} {lbl}")

    print(f"\nShowing {min(limit, len(voices))} of {len(voices)} voices")
    return voices


# ============================================================================
# GENERATE VOICEOVER (TTS API)
# ============================================================================
def eGenerateVoiceover(
    text,
    api_key,
    output_file="voiceover.mp3",
    voice_id=None,
    voice_name="george",
    model="multilingual_v2",
    stability=0.50,
    similarity_boost=0.75,
    style=0.0,
    speed=1.0,
    output_format="mp3_44100_128",
    language=None,
):
    """
    Generate voiceover audio from text via the ElevenLabs TTS API.

    Parameters
    ----------
    text            : str   — script to speak
    api_key         : str   — ElevenLabs API key
    output_file     : str   — output path (.mp3)
    voice_id        : str   — explicit voice ID (overrides voice_name)
    voice_name      : str   — shortcut from VOICES dict ("george", "rachel", etc.)
    model           : str   — model shortcut or full ID
    stability       : float — 0.0 (variable) to 1.0 (stable)
    similarity_boost: float — 0.0 to 1.0
    style           : float — 0.0 to 1.0, expressiveness (v2+ models)
    speed           : float — playback speed (0.7 to 1.3 typical)
    output_format   : str   — e.g. "mp3_44100_128", "mp3_44100_192"
    language        : str   — ISO 639-1 code to force language (e.g. "en")

    Returns
    -------
    output_file : str

    Example
    -------
    eGenerateVoiceover(
        text="Valentine's Day spending hit a record twenty-nine billion dollars.",
        api_key=ELEVENLABS_API_KEY,
        voice_name="george",
        output_file="vo.mp3"
    )
    """
    # Resolve voice ID
    if voice_id is None:
        voice_id = VOICES.get(voice_name.lower())
        if voice_id is None:
            raise ValueError(
                f"Unknown voice_name '{voice_name}'. "
                f"Use one of {list(VOICES.keys())} or pass voice_id directly."
            )

    model_id = TTS_MODELS.get(model, model)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": model_id,
        "output_format": output_format,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": True,
        },
    }

    if speed != 1.0:
        payload["voice_settings"]["speed"] = speed
    if language:
        payload["language_code"] = language

    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs TTS error ({r.status_code}): {r.text[:500]}")

    with open(output_file, "wb") as f:
        f.write(r.content)

    size_kb = os.path.getsize(output_file) / 1024
    dur = eGetDuration(output_file)
    print(f"✅ Voiceover saved → {output_file}  ({dur:.1f}s, {size_kb:.0f} KB, "
          f"voice={voice_name}, model={model})")
    return output_file


# ============================================================================
# GENERATE MUSIC (Music API — streaming endpoint)
# ============================================================================
def eGenerateMusic(
    api_key,
    prompt=None,
    output_file="background_music.mp3",
    duration_ms=15000,
    force_instrumental=True,
    output_format="mp3_44100_128",
    preset=None,
):
    """
    Generate background music via the ElevenLabs Music API.

    Parameters
    ----------
    prompt              : str   — text description of desired music
    api_key             : str   — ElevenLabs API key
    output_file         : str   — output path (.mp3)
    duration_ms         : int   — desired length in milliseconds (3000–600000)
    force_instrumental  : bool  — guarantee no vocals
    output_format       : str   — audio format string
    preset              : str   — key from MUSIC_PRESETS to use instead of prompt
                                  ("lofi_coffee", "editorial_minimal",
                                   "upbeat_data", "morning_news")

    Returns
    -------
    output_file : str

    Example
    -------
    eGenerateMusic(
        preset="lofi_coffee",
        api_key=ELEVENLABS_API_KEY,
        duration_ms=20000,
        output_file="bg_music.mp3"
    )
    """
    if preset is not None:
        if preset not in MUSIC_PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. "
                f"Options: {list(MUSIC_PRESETS.keys())}"
            )
        prompt = MUSIC_PRESETS[preset]

    url = "https://api.elevenlabs.io/v1/music/stream"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "prompt": prompt,
        "music_length_ms": duration_ms,
        "force_instrumental": force_instrumental,
        "output_format": output_format,
    }

    print(f"⏳ Generating music ({duration_ms/1000:.0f}s)... this may take 30–90 seconds.")
    r = requests.post(url, headers=headers, json=payload, stream=True)

    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs Music error ({r.status_code}): {r.text[:500]}")

    with open(output_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    size_kb = os.path.getsize(output_file) / 1024
    dur = eGetDuration(output_file)
    print(f"✅ Music saved → {output_file}  ({dur:.1f}s, {size_kb:.0f} KB)")
    return output_file


# ============================================================================
# ADD VOICEOVER TO VIDEO
# ============================================================================
def eAddVoiceover(
    video_file,
    voiceover_file,
    output_file="espresso_with_vo.mp4",
    vo_volume=1.0,
    vo_delay=0.0,
    vo_fade_in=0.0,
    vo_fade_out=0.3,
):
    """
    Overlay a voiceover audio file onto a video.

    Parameters
    ----------
    video_file     : str   — input MP4 (silent)
    voiceover_file : str   — voiceover audio (mp3/wav/m4a)
    output_file    : str   — output MP4
    vo_volume      : float — volume multiplier (1.0 = original)
    vo_delay       : float — seconds to delay voiceover start
    vo_fade_in     : float — seconds of fade-in
    vo_fade_out    : float — seconds of fade-out at end of voiceover
    """
    for f in [video_file, voiceover_file]:
        if not os.path.isfile(f):
            raise FileNotFoundError(f"File not found: {f}")

    vid_dur = eGetDuration(video_file)

    vo_filters = [f"volume={vo_volume}"]
    if vo_delay > 0:
        ms = int(vo_delay * 1000)
        vo_filters.append(f"adelay={ms}|{ms}")
    if vo_fade_in > 0:
        vo_filters.append(f"afade=t=in:st=0:d={vo_fade_in}")
    if vo_fade_out > 0:
        vo_dur = eGetDuration(voiceover_file)
        fo_start = vo_dur - vo_fade_out + vo_delay
        vo_filters.append(f"afade=t=out:st={fo_start:.2f}:d={vo_fade_out}")

    vo_chain = ",".join(vo_filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', video_file,
        '-i', voiceover_file,
        '-filter_complex',
        f'[1:a]{vo_chain}[vo];'
        f'[vo]apad=whole_dur={vid_dur:.2f}[aout]',
        '-map', '0:v', '-map', '[aout]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output_file
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")

    print(f"✅ Added voiceover → {output_file}")
    return output_file


# ============================================================================
# ADD MUSIC TO VIDEO
# ============================================================================
def eAddMusic(
    video_file,
    music_file,
    output_file="espresso_with_music.mp4",
    music_volume=0.15,
    fade_in=1.0,
    fade_out=2.0,
    loop=True,
):
    """
    Add background music to a video. Loops and fades automatically.

    Parameters
    ----------
    video_file   : str   — input MP4
    music_file   : str   — background music (mp3/wav/m4a)
    output_file  : str   — output MP4
    music_volume : float — volume (0.15 = 15%, sits under voiceover)
    fade_in      : float — seconds of fade-in
    fade_out     : float — seconds of fade-out at end
    loop         : bool  — loop music if shorter than video
    """
    for f in [video_file, music_file]:
        if not os.path.isfile(f):
            raise FileNotFoundError(f"File not found: {f}")

    vid_dur = eGetDuration(video_file)

    mu_filters = [f"volume={music_volume}"]
    if fade_in > 0:
        mu_filters.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        fo_start = vid_dur - fade_out
        mu_filters.append(f"afade=t=out:st={fo_start:.2f}:d={fade_out}")

    mu_chain = ",".join(mu_filters)
    loop_args = ['-stream_loop', '-1'] if loop else []

    cmd = [
        'ffmpeg', '-y',
        '-i', video_file,
        *loop_args, '-i', music_file,
        '-filter_complex',
        f'[1:a]{mu_chain},atrim=0:{vid_dur:.2f},asetpts=PTS-STARTPTS[music]',
        '-map', '0:v', '-map', '[music]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output_file
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")

    print(f"✅ Added background music → {output_file}")
    return output_file


# ============================================================================
# ADD VOICEOVER + MUSIC COMBINED
# ============================================================================
def eAddAudio(
    video_file,
    output_file="espresso_final.mp4",
    # --- voiceover ---
    voiceover_file=None,
    vo_volume=1.0,
    vo_delay=0.5,
    vo_fade_in=0.0,
    vo_fade_out=0.3,
    # --- music ---
    music_file=None,
    music_volume=0.12,
    music_fade_in=1.0,
    music_fade_out=2.0,
    music_loop=True,
):
    """
    Add voiceover and/or background music to a video in a single pass.

    Parameters
    ----------
    video_file     : str        — input MP4
    output_file    : str        — output MP4
    voiceover_file : str|None   — voiceover audio (skip if None)
    vo_volume      : float      — voiceover volume (1.0 = full)
    vo_delay       : float      — seconds before voiceover starts
    vo_fade_in     : float      — voiceover fade-in seconds
    vo_fade_out    : float      — voiceover fade-out seconds
    music_file     : str|None   — background music (skip if None)
    music_volume   : float      — music volume (0.12 = sits under voice)
    music_fade_in  : float      — music fade-in seconds
    music_fade_out : float      — music fade-out seconds
    music_loop     : bool       — loop music to fill video length
    """
    if voiceover_file is None and music_file is None:
        raise ValueError("Provide at least one of voiceover_file or music_file.")

    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"Video not found: {video_file}")

    vid_dur = eGetDuration(video_file)

    inputs = ['-i', video_file]
    input_idx = 1
    filter_parts = []
    mix_inputs = []

    # --- Voiceover stream ---
    if voiceover_file is not None:
        if not os.path.isfile(voiceover_file):
            raise FileNotFoundError(f"Voiceover not found: {voiceover_file}")

        inputs += ['-i', voiceover_file]
        vo_idx = input_idx
        input_idx += 1

        vo_filters = [f"volume={vo_volume}"]
        if vo_delay > 0:
            ms = int(vo_delay * 1000)
            vo_filters.append(f"adelay={ms}|{ms}")
        if vo_fade_in > 0:
            vo_filters.append(f"afade=t=in:st={vo_delay:.2f}:d={vo_fade_in}")
        if vo_fade_out > 0:
            vo_dur = eGetDuration(voiceover_file)
            fo_start = vo_delay + vo_dur - vo_fade_out
            vo_filters.append(f"afade=t=out:st={fo_start:.2f}:d={vo_fade_out}")

        vo_chain = ",".join(vo_filters)
        filter_parts.append(f"[{vo_idx}:a]{vo_chain},apad=whole_dur={vid_dur:.2f}[vo]")
        mix_inputs.append("[vo]")

    # --- Music stream ---
    if music_file is not None:
        if not os.path.isfile(music_file):
            raise FileNotFoundError(f"Music not found: {music_file}")

        if music_loop:
            inputs += ['-stream_loop', '-1', '-i', music_file]
        else:
            inputs += ['-i', music_file]
        mu_idx = input_idx
        input_idx += 1

        mu_filters = [f"volume={music_volume}"]
        if music_fade_in > 0:
            mu_filters.append(f"afade=t=in:st=0:d={music_fade_in}")
        if music_fade_out > 0:
            fo_start = vid_dur - music_fade_out
            mu_filters.append(f"afade=t=out:st={fo_start:.2f}:d={music_fade_out}")

        mu_chain = ",".join(mu_filters)
        filter_parts.append(
            f"[{mu_idx}:a]{mu_chain},"
            f"atrim=0:{vid_dur:.2f},asetpts=PTS-STARTPTS[music]"
        )
        mix_inputs.append("[music]")

    # --- Mix ---
    if len(mix_inputs) == 2:
        mix_labels = "".join(mix_inputs)
        filter_parts.append(
            f"{mix_labels}amix=inputs=2:duration=first:dropout_transition=0[aout]"
        )
    else:
        single_tag = mix_inputs[0].strip("[]")
        filter_parts[-1] = filter_parts[-1].rsplit(f"[{single_tag}]", 1)[0] + "[aout]"

    filter_complex = ";".join(filter_parts)

    cmd = [
        'ffmpeg', '-y',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '0:v', '-map', '[aout]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output_file
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr}")

    final_dur = eGetDuration(output_file)
    parts = []
    if voiceover_file: parts.append("voiceover")
    if music_file:     parts.append("music")

    print(f"✅ Added {' + '.join(parts)} → {output_file}  ({final_dur:.1f}s)")
    return output_file



# ============================================================================
# ESPRESSO CHARTS — GITHUB UPLOADER + SUBSTACK PUBLISHER
# ============================================================================
# Add to your espresso_charts_main.ipynb as a new section.
# No UI. Call functions directly from notebook cells.
#
# SETUP (run once per session):
#   uploader = GitHubUploader(token="ghp_xxx", owner="you", repo="espresso-charts")
#   substack = SubstackPublisher(publication_url="https://yourpub.substack.com",
#                                 email="you@email.com", password="yourpassword")
#
# GITHUB USAGE:
#   uploader.push_file("/content/chart.png", dest="assets/2026-02-buffett.png")
#   uploader.push_figure(fig, dest="assets/2026-02-buffett.png")
#   uploader.push_text(caption_text, dest="prompts/04_instagram_caption.md")
#   uploader.push_story_pack("02-buffett-indicator", {...})
#
# SUBSTACK USAGE:
#   substack.post_draft(title="...", body="...", subtitle="...")
#   substack.post_scheduled(title="...", body="...", publish_at="2026-02-25T08:00:00")
#   substack.post_now(title="...", body="...", subtitle="...")
# ============================================================================


# ============================================================================
# GITHUB UPLOADER
# ============================================================================

class GitHubUploader:
    """Push files, figures, and text to your GitHub repo from Colab."""

    def __init__(self, token: str, owner: str, repo: str, branch: str = "main"):
        self.token  = token
        self.owner  = owner
        self.repo   = repo
        self.branch = branch

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        }

    def _get_sha(self, path: str):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        r   = requests.get(url, headers=self._headers(), params={"ref": self.branch})
        return r.json().get("sha") if r.ok else None

    def _push(self, path: str, content_b64: str, commit_msg: str):
        url  = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        body = {"message": commit_msg, "content": content_b64, "branch": self.branch}
        sha  = self._get_sha(path)
        if sha:
            body["sha"] = sha
        r = requests.put(url, headers=self._headers(), data=json.dumps(body))
        if not r.ok:
            raise RuntimeError(f"GitHub {r.status_code}: {r.json().get('message')}")
        return r.json()

    # ── Public methods ────────────────────────────────────────────────────────

    def push_file(self, local_path: str, dest: str = None, commit_msg: str = None):
        """
        Push a local file to GitHub.

        Args:
            local_path:  Path on disk, e.g. "/content/chart.png"
            dest:        Repo path, e.g. "assets/2026-02-buffett.png"
                         Defaults to assets/<filename>
            commit_msg:  Defaults to "Upload <filename> [YYYY-MM-DD]"

        Example:
            uploader.push_file("/content/chart_sq.png", dest="assets/2026-02-buffett-sq.png")
        """
        local_path = Path(local_path)
        dest       = dest or f"assets/{local_path.name}"
        msg        = commit_msg or f"Upload {local_path.name} [{datetime.now().strftime('%Y-%m-%d')}]"

        with open(local_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        self._push(dest, b64, msg)
        print(f"✅  {local_path.name}  →  {dest}")

    def push_figure(self, fig, dest: str, dpi: int = 200, commit_msg: str = None):
        """
        Push a matplotlib Figure directly — no saving to disk needed.

        Args:
            fig:   Matplotlib Figure object
            dest:  Repo path, e.g. "assets/2026-02-buffett.png"
            dpi:   Resolution (default 200, matches your chart pipeline)

        Example:
            uploader.push_figure(fig, dest="assets/2026-02-buffett-sq.png")
        """
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        buf.seek(0)
        b64  = base64.b64encode(buf.read()).decode()
        name = Path(dest).name
        msg  = commit_msg or f"Push chart {name} [{datetime.now().strftime('%Y-%m-%d')}]"

        self._push(dest, b64, msg)
        print(f"✅  {name}  →  {dest}")

    def push_text(self, text: str, dest: str, commit_msg: str = None):
        """
        Push a string (prompt, caption, article, markdown) to GitHub.

        Args:
            text:  The text content to save
            dest:  Repo path, e.g. "prompts/04_instagram_caption.md"

        Example:
            uploader.push_text(instagram_caption, dest="prompts/04_instagram_caption.md")
            uploader.push_text(substack_article,  dest="content/2026/02-buffett/article.md")
        """
        name = Path(dest).name
        msg  = commit_msg or f"Save {name} [{datetime.now().strftime('%Y-%m-%d')}]"
        b64  = base64.b64encode(text.encode("utf-8")).decode()

        self._push(dest, b64, msg)
        print(f"✅  {name}  →  {dest}")

    def push_story_pack(self, story_slug: str, files: dict, year: str = None):
        """
        Push a full story pack in one call.

        Args:
            story_slug:  e.g. "02-buffett-indicator"
            files:       {dest_suffix: local_path_or_text_string}
            year:        e.g. "2026". Defaults to current year.

        Example:
            uploader.push_story_pack("02-buffett-indicator", {
                "caption.md"    : instagram_caption,
                "article.md"    : substack_article,
                "chart_sq.png"  : "/content/chart_sq.png",
                "chart_pt.png"  : "/content/chart_pt.png",
            })
        """
        year = year or str(datetime.now().year)
        base = f"content/{year}/{story_slug}"
        print(f"\n☕  Pushing story pack → {base}/\n{'─'*50}")

        for suffix, source in files.items():
            dest = f"{base}/{suffix}"
            if isinstance(source, str) and os.path.exists(source):
                self.push_file(source, dest)
            elif isinstance(source, str):
                self.push_text(source, dest)
            else:
                print(f"⚠️  Skipped {suffix}: pass a file path or text string")

        print(f"{'─'*50}\n✅  Story pack complete\n")


# ============================================================================
# SUBSTACK PUBLISHER
# ============================================================================

class SubstackPublisher:
    """
    Publish draft and scheduled posts to Substack via their internal API.

    NOTE: Substack does not have an official public API. This uses the same
    endpoints their web app uses. It works as of early 2026 but may change
    if Substack updates their platform.

    Args:
        publication_url:  Your full Substack URL, e.g. "https://espressocharts.substack.com"
        email:            Your Substack login email
        password:         Your Substack login password
    """

    def __init__(self, publication_url: str, email: str, password: str):
        self.pub_url    = publication_url.rstrip("/")
        self.email      = email
        self.password   = password
        self.session    = requests.Session()
        self._logged_in = False

    def _login(self):
        """Authenticate and store session cookie."""
        if self._logged_in:
            return
        r = self.session.post(
            "https://substack.com/api/v1/email-login",
            json={"email": self.email, "password": self.password, "captcha_response": None},
        )
        if not r.ok:
            raise RuntimeError(f"Substack login failed {r.status_code}: {r.text}")
        self._logged_in = True
        print("✅  Logged in to Substack")

    def _markdown_to_html(self, text: str) -> str:
        """
        Markdown → HTML. Installs 'markdown' package if not present.
        """
        try:
            import markdown
        except ImportError:
            os.system("pip install markdown -q")
            import markdown
        return markdown.markdown(text, extensions=["extra", "nl2br"])

    def _create_post(self, title: str, body_html: str, subtitle: str = "") -> dict:
        """Create a post draft and return the post object."""
        self._login()
        r = self.session.post(
            f"{self.pub_url}/api/v1/posts",
            json={
                "type"          : "newsletter",
                "draft_title"   : title,
                "draft_subtitle": subtitle,
                "draft_body"    : body_html,
                "audience"      : "everyone",
            },
        )
        if not r.ok:
            raise RuntimeError(f"Failed to create post {r.status_code}: {r.text}")
        return r.json()

    # ── Public methods ────────────────────────────────────────────────────────

    def post_draft(self, title: str, body: str, subtitle: str = "", body_is_html: bool = False):
        """
        Save a post as a draft (not published, not scheduled).

        Args:
            title:        Post title
            body:         Post body in markdown (default) or HTML
            subtitle:     Optional subtitle shown in previews and email
            body_is_html: Set True if body is already HTML

        Example:
            substack.post_draft(
                title    = "The Buffett Indicator Just Hit 200%",
                subtitle = "What the stock market's favourite valuation metric is telling us",
                body     = substack_article,
            )
        """
        html = body if body_is_html else self._markdown_to_html(body)
        post = self._create_post(title, html, subtitle)
        print(f"✅  Draft saved: '{title}'")
        print(f"    Edit at: {self.pub_url}/publish/post/{post.get('id', '')}")
        return post

    def post_scheduled(self, title: str, body: str, publish_at: str,
                        subtitle: str = "", body_is_html: bool = False):
        """
        Create and schedule a post for future publication.

        Args:
            title:        Post title
            body:         Post body in markdown (default) or HTML
            publish_at:   UTC datetime string: "YYYY-MM-DDTHH:MM:SS"
                          Berlin is UTC+1 (CET, winter) or UTC+2 (CEST, summer).
                          For 9 AM Berlin CET  → use "08:00:00" UTC
                          For 9 AM Berlin CEST → use "07:00:00" UTC
            subtitle:     Optional subtitle shown in previews and email
            body_is_html: Set True if body is already HTML

        Example — Wednesday 9 AM Berlin (CET, winter):
            substack.post_scheduled(
                title      = "The Buffett Indicator Just Hit 200%",
                subtitle   = "What the stock market's favourite valuation metric is telling us",
                body       = substack_article,
                publish_at = "2026-02-25T08:00:00",
            )
        """
        self._login()
        html    = body if body_is_html else self._markdown_to_html(body)
        post    = self._create_post(title, html, subtitle)
        post_id = post["id"]

        r = self.session.post(
            f"{self.pub_url}/api/v1/posts/{post_id}/schedule",
            json={"post_date": f"{publish_at}Z"},
        )
        if not r.ok:
            raise RuntimeError(f"Failed to schedule post {r.status_code}: {r.text}")

        print(f"✅  Scheduled: '{title}'")
        print(f"    Publishes: {publish_at} UTC")
        print(f"    Edit at:   {self.pub_url}/publish/post/{post_id}")
        return r.json()

    def post_now(self, title: str, body: str, subtitle: str = "", body_is_html: bool = False):
        """
        Publish a post immediately.

        Example:
            substack.post_now(
                title    = "The Buffett Indicator Just Hit 200%",
                subtitle = "What the stock market's favourite valuation metric is telling us",
                body     = substack_article,
            )
        """
        self._login()
        html    = body if body_is_html else self._markdown_to_html(body)
        post    = self._create_post(title, html, subtitle)
        post_id = post["id"]

        r = self.session.post(f"{self.pub_url}/api/v1/posts/{post_id}/publish")
        if not r.ok:
            raise RuntimeError(f"Failed to publish {r.status_code}: {r.text}")

        print(f"✅  Published: '{title}'")
        print(f"    Live at: {self.pub_url}/p/{post.get('slug', '')}")
        return r.json()
