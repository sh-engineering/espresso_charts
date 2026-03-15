"""
espresso_charts_patch.py
========================
Patches 3 bugs in espresso_charts.py:

FIX 1: eSingleBarChartNewInstagram — value label ax.annotate() missing bbox
FIX 2: eMultiLineChartInstagram — point_label_offsets x-component (ox_pt) silently discarded
FIX 3: eMultiLineChartAnimateInstagram — same ox_pt bug (3 sub-fixes: 3a, 3b, 3c)

Usage:
    python espresso_charts_patch.py espresso_charts.py
"""
import sys

if len(sys.argv) < 2:
    print("Usage: python espresso_charts_patch.py <path_to_espresso_charts.py>")
    sys.exit(1)

path = sys.argv[1]
with open(path, 'r') as f:
    src = f.read()

applied = []
skipped = []

def patch(name, old, new):
    global src
    if old in src:
        src = src.replace(old, new, 1)
        applied.append(name)
    else:
        skipped.append(name)

# =========================================================================
# FIX 1: eSingleBarChartNewInstagram — value labels have no bbox background
# =========================================================================
patch(
    "FIX 1: bar chart value label bbox",
    # OLD: no bbox on value label annotate
    """        ax.annotate(
            formatted,
            xy=(x_end, y_center),
            xytext=(off_val, y_extra), textcoords='offset points',
            ha=ha_val, va='center',
            fontsize=label_size, color=value_label_color, zorder=6,
        )""",
    # NEW: add bbox so labels are readable over bars
    """        ax.annotate(
            formatted,
            xy=(x_end, y_center),
            xytext=(off_val, y_extra), textcoords='offset points',
            ha=ha_val, va='center',
            fontsize=label_size, color=value_label_color, zorder=6,
            bbox=dict(boxstyle='square,pad=0', facecolor=face_color,
                      edgecolor=face_color, alpha=0.85),
        )""",
)

# =========================================================================
# FIX 2: eMultiLineChartInstagram — ox_pt computed but never used
# ax.text() only takes data coords, so ox_pt (offset in points) was dead code.
# Switch to ax.annotate() with textcoords='offset points'.
# =========================================================================
patch(
    "FIX 2: multiline value label ox_pt",
    # OLD: ax.text ignores ox_pt
    """            ax.text(
                x.iloc[pos], raw + oy + oy_pt,
                fmt_s,
                ha='center', va='bottom', color=colors[idx],
                fontsize=label_size, zorder=11,
                bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                          edgecolor=face_color, alpha=0.8),
            )""",
    # NEW: ax.annotate applies ox_pt via xytext
    """            ax.annotate(
                fmt_s,
                xy=(x.iloc[pos], raw + oy + oy_pt),
                xytext=(ox_pt, 0), textcoords='offset points',
                ha='center', va='bottom', color=colors[idx],
                fontsize=label_size, zorder=11,
                bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                          edgecolor=face_color, alpha=0.8),
            )""",
)

# =========================================================================
# FIX 3a: eMultiLineChartAnimateInstagram — store ox_pt in value_targets
# =========================================================================
patch(
    "FIX 3a: animated line store ox_pt",
    # OLD: ox_pt computed but not stored
    """                value_targets.append(dict(pos=p, idx=idx, formatted=fmt_s,
                                          x=x.iloc[p], y=raw + oy + oy_pt, color=colors[idx]))""",
    # NEW: store ox so update() can use it
    """                value_targets.append(dict(pos=p, idx=idx, formatted=fmt_s,
                                          x=x.iloc[p], y=raw + oy + oy_pt,
                                          ox=ox_pt, color=colors[idx]))""",
)

# =========================================================================
# FIX 3b: Switch val_objs from ax.text() to ax.annotate()
# =========================================================================
patch(
    "FIX 3b: animated line val_objs annotate",
    # OLD: ax.text can't apply ox offset
    """    val_objs = []
    for vt in value_targets:
        t = ax.text(vt['x'], vt['y'], '', ha='center', va='bottom',
                    color=vt['color'], fontsize=label_size, zorder=11,
                    bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                              edgecolor=face_color, alpha=0.8))
        t.set_visible(False)
        val_objs.append(t)""",
    # NEW: ax.annotate with stored ox offset
    """    val_objs = []
    for vt in value_targets:
        t = ax.annotate('', xy=(vt['x'], vt['y']),
                         xytext=(vt.get('ox', 0), 0), textcoords='offset points',
                         ha='center', va='bottom',
                         color=vt['color'], fontsize=label_size, zorder=11,
                         bbox=dict(boxstyle='square,pad=0.1', facecolor=face_color,
                                   edgecolor=face_color, alpha=0.8))
        t.set_visible(False)
        val_objs.append(t)""",
)

# =========================================================================
# FIX 3c: update() must set .xy on annotate objects for position to update
# =========================================================================
patch(
    "FIX 3c: animated line update xy",
    # OLD: no xy update on annotate objects
    """        for vi, vt in enumerate(value_targets):
            if vt['pos'] < reveal - 0.5:
                val_objs[vi].set_visible(True); val_objs[vi].set_text(vt['formatted'])
            else:
                val_objs[vi].set_visible(False)""",
    # NEW: set xy so annotate positions correctly
    """        for vi, vt in enumerate(value_targets):
            if vt['pos'] < reveal - 0.5:
                val_objs[vi].set_visible(True)
                val_objs[vi].set_text(vt['formatted'])
                val_objs[vi].xy = (vt['x'], vt['y'])
            else:
                val_objs[vi].set_visible(False)""",
)

# =========================================================================
# Write result
# =========================================================================
with open(path, 'w') as f:
    f.write(src)

print(f"\n{'='*60}")
print(f"  espresso_charts.py patch results")
print(f"{'='*60}")
for name in applied:
    print(f"  [APPLIED] {name}")
for name in skipped:
    print(f"  [SKIPPED] {name} (pattern not found)")
print(f"{'='*60}")
print(f"  {len(applied)} applied, {len(skipped)} skipped")
print(f"{'='*60}\n")
