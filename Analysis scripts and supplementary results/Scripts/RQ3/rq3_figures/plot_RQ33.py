"""
Combine RQ3 results into one four-panel figure.

Run this script after the existing RQ3 analysis has generated its CSV files.
Change RESULT_DIR to the folder containing those CSV files.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


# ============================================================
# Input and output
# ============================================================
RESULT_DIR = Path("")
OUTPUT_DIR = RESULT_DIR

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Font settings — aligned with the latest RQ2 figure
# ============================================================
BASE_FONT_SIZE = 38
TICK_SIZE = 36
VALUE_SIZE = 35
TITLE_SIZE = 39
AXIS_LABEL_SIZE = 36
LEGEND_SIZE = 32

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT_SIZE,
    "axes.labelsize": AXIS_LABEL_SIZE,
    "axes.labelweight": "bold",
    "axes.titlesize": TITLE_SIZE,
    "axes.titleweight": "bold",
    "xtick.labelsize": TICK_SIZE,
    "ytick.labelsize": TICK_SIZE,
    "legend.fontsize": LEGEND_SIZE,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
})


# ============================================================
# Load existing analysis results
# ============================================================
def read_result(filename, index_col=None):
    path = RESULT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing result file: {path}\n"
            "Run the existing RQ3 analysis first, or change RESULT_DIR."
        )
    return pd.read_csv(path, index_col=index_col)


persistence = read_result("recording_persistence.csv")
stars = read_result("introduction_event_summary.csv")
association = read_result("association_introduction_sensitivity.csv")

business_pct = read_result(
    "repo_busi_domain_pattern_percent.csv",
    index_col=0,
)
business_counts = read_result(
    "repo_busi_domain_pattern_counts.csv",
    index_col=0,
)

software_pct = read_result(
    "repo_soft_domain_pattern_percent.csv",
    index_col=0,
)
software_counts = read_result(
    "repo_soft_domain_pattern_counts.csv",
    index_col=0,
)

PATTERNS = [
    "Introduction-year only",
    "Consecutive recording",
    "Intermittent recording",
]

PATTERN_COLORS = {
    "Introduction-year only": "#D9D9D9",
    "Consecutive recording": "#50868C",
    "Intermittent recording": "#C89B68",
}

for percentages, counts in [
    (business_pct, business_counts),
    (software_pct, software_counts),
]:
    missing = set(PATTERNS) - set(percentages.columns)
    if missing:
        raise ValueError(f"Missing recording-pattern columns: {missing}")

    if not percentages.index.equals(counts.index):
        raise ValueError("Context rows differ between counts and percentages.")

    if not np.allclose(
        percentages[PATTERNS].sum(axis=1),
        100,
        atol=0.01,
    ):
        raise ValueError("Recording-pattern percentages do not sum to 100.")


# ============================================================
# Layout
# More space is allocated to context comparisons.
# ============================================================
FIGURE_WIDTH = 44
FIGURE_HEIGHT = 36

fig = plt.figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))

outer = fig.add_gridspec(
    2,
    2,
    width_ratios=[1.05, 1.35],
    height_ratios=[1.75, 1.0],
    left=0.08,
    right=0.98,
    bottom=0.10,
    top=0.96,
    wspace=0.32,
    hspace=0.35,
)

ax_a = fig.add_subplot(outer[0, 0])

context_grid = outer[0, 1].subgridspec(
    2,
    1,
    height_ratios=[
        len(business_pct) + 2,
        len(software_pct) + 2,
    ],
    hspace=0.35,
)

ax_b_business = fig.add_subplot(context_grid[0])
ax_b_software = fig.add_subplot(context_grid[1])

ax_c = fig.add_subplot(outer[1, 0])
ax_d = fig.add_subplot(outer[1, 1])


# ============================================================
# Common styling
# ============================================================
def style_axis(ax, grid_axis=None):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)

    ax.tick_params(
        axis="both",
        labelsize=TICK_SIZE,
        length=8,
        width=1.5,
        pad=12,
    )

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight("bold")

    if grid_axis:
        ax.grid(
            axis=grid_axis,
            color="#E5E5E5",
            linewidth=1.5,
        )

    ax.set_axisbelow(True)


# ============================================================
# (a) Recording persistence
# ============================================================
persistence = persistence.sort_values("relative_year")
n_persistence = int(persistence["repositories"].iloc[0])

ax_a.plot(
    persistence["relative_year"],
    persistence["percent"],
    color="#50868C",
    linewidth=5,
    marker="o",
    markersize=17,
)

for row in persistence.itertuples():
    ax_a.annotate(
        f"{row.percent:.1f}%",
        (row.relative_year, row.percent),
        xytext=(0, 18),
        textcoords="offset points",
        ha="center",
        fontsize=VALUE_SIZE,
    )

ax_a.set_title(
    f"(a) Recording persistence\n"
    f"(n = {n_persistence:,} repositories)",
    loc="left",
    pad=30,
)

ax_a.set_xlabel("Years since first observed ADR", labelpad=22)
ax_a.set_ylabel("Repositories with new ADR records (%)", labelpad=22)

ax_a.set_xticks(persistence["relative_year"])
ax_a.set_ylim(0, 115)
ax_a.set_xlim(
    persistence["relative_year"].min() - 0.3,
    persistence["relative_year"].max() + 0.3,
)
ax_a.set_yticks([0, 20, 40, 60, 80, 100])

style_axis(ax_a, grid_axis="y")


# ============================================================
# (b) Recording patterns across contexts
# Context labels use codes; n gives repository counts.
# ============================================================
def draw_context_patterns(ax, percentages, counts, title):
    y = np.arange(len(percentages))
    left = np.zeros(len(percentages))

    for pattern in PATTERNS:
        values = percentages[pattern].to_numpy()

        ax.barh(
            y,
            values,
            left=left,
            height=0.76,
            color=PATTERN_COLORS[pattern],
            edgecolor="white",
            linewidth=1.2,
            label=pattern,
        )

        for i, value in enumerate(values):
            # Avoid overlapping labels in narrow segments.
            if value >= 12:
                ax.text(
                    left[i] + value / 2,
                    i,
                    f"{value:.1f}",
                    ha="center",
                    va="center",
                    fontsize=VALUE_SIZE,
                    color=(
                        "white"
                        if pattern == "Consecutive recording"
                        else "#222222"
                    ),
                )

        left += values

    repository_counts = counts[PATTERNS].sum(axis=1).astype(int)

    ax.set_yticks(
        y,
        labels=[
            f"{code} (n={repository_counts.loc[code]:,})"
            for code in percentages.index
        ],
    )

    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_title(title, loc="left", pad=25)

    style_axis(ax, grid_axis="x")


n_patterns = int(business_counts[PATTERNS].to_numpy().sum())

draw_context_patterns(
    ax_b_business,
    business_pct,
    business_counts,
    f"(b) Recording patterns across contexts\n"
    f"Business domains (n = {n_patterns:,} repositories)",
)

draw_context_patterns(
    ax_b_software,
    software_pct,
    software_counts,
    "Software types",
)

ax_b_software.set_xlabel("Repositories (%)", labelpad=18)

handles, labels = ax_b_business.get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="lower center",
    bbox_to_anchor=(0.5, 0.015),
    ncol=3,
    frameon=False,
    fontsize=LEGEND_SIZE,
    handlelength=2.0,
    columnspacing=2.5,
)


# ============================================================
# (c) Stars around ADR introduction
# Median and interquartile range of annual new stars.
# ============================================================
stars = stars.sort_values("relative_year")
n_stars = int(stars["n"].iloc[0])

x = stars["relative_year"].to_numpy()
median = stars["median"].to_numpy()
q25 = stars["q25"].to_numpy()
q75 = stars["q75"].to_numpy()

ax_c.fill_between(
    x,
    q25,
    q75,
    color="#C89B68",
    alpha=0.25,
    label="Interquartile range",
)

ax_c.plot(
    x,
    median,
    color="#9B703D",
    linewidth=5,
    marker="o",
    markersize=16,
    label="Median",
)

ax_c.axvline(
    0,
    color="#777777",
    linestyle="--",
    linewidth=2.5,
)

for year, value in zip(x, median):
    ax_c.annotate(
        f"{value:g}",
        (year, value),
        xytext=(0, 16),
        textcoords="offset points",
        ha="center",
        fontsize=VALUE_SIZE,
    )

ax_c.set_title(
    f"(c) Stars around ADR introduction\n"
    f"(n = {n_stars:,} repositories)",
    loc="left",
    pad=30,
)

ax_c.set_xlabel("Years relative to first observed ADR", labelpad=22)
ax_c.set_ylabel("Annual new stars", labelpad=22)

ax_c.set_xticks(x)
ax_c.set_xlim(x.min() - 0.3, x.max() + 0.3)
ax_c.set_ylim(bottom=0, top=max(q75.max() * 1.15, 20))

ax_c.legend(
    loc="upper left",
    frameon=False,
    fontsize=LEGEND_SIZE,
)

style_axis(ax_c, grid_axis="y")


# ============================================================
# (d) Association estimates
# Same-repository comparison: include/exclude introduction year.
# Coefficients and confidence intervals are read from CSV.
# ============================================================
expected_order = [
    "Including introduction year",
    "Excluding introduction year",
]

association = (
    association.set_index("association")
    .loc[expected_order]
    .reset_index()
)

y = np.arange(len(association))
coef = association["coefficient"].to_numpy()
low = association["low"].to_numpy()
high = association["high"].to_numpy()

ax_d.errorbar(
    coef,
    y,
    xerr=np.vstack([coef - low, high - coef]),
    fmt="o",
    color="#50868C",
    ecolor="#50868C",
    markersize=17,
    elinewidth=5,
    capsize=12,
    capthick=4,
)

ax_d.axvline(
    0,
    color="#777777",
    linestyle="--",
    linewidth=2.5,
)

ax_d.set_yticks(
    y,
    labels=[
        "Including\nintroduction year",
        "Excluding\nintroduction year",
    ],
)
ax_d.invert_yaxis()
ax_d.set_ylim(1.6, -0.6)

span = max(high.max() - min(0, low.min()), 0.05)
ax_d.set_xlim(
    min(0, low.min()) - 0.12 * span,
    high.max() + 0.20 * span,
)

for i, row in enumerate(association.itertuples()):
    ax_d.annotate(
        f"{row.coefficient:.3f} "
        f"[{row.low:.3f}, {row.high:.3f}]\n"
        f"{row.repo_years:,} repository-years",
        (row.coefficient, i),
        xytext=(0, -48),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=LEGEND_SIZE,
    )

repository_samples = association["repositories"].unique()
sample_text = (
    f"n = {int(repository_samples[0]):,} repositories"
    if len(repository_samples) == 1
    else "Sample sizes reported in the analysis results"
)

ax_d.set_title(
    f"(d) Association estimates\n({sample_text})",
    loc="left",
    pad=30,
)

ax_d.set_xlabel(
    "Regression coefficient (95% CI)",
    labelpad=22,
)

style_axis(ax_d, grid_axis="x")


# ============================================================
# Export
# ============================================================
output_stem = OUTPUT_DIR / "rq3_combined"

# PDF/SVG preserve vector text; PNG uses a lower DPI because
# the large canvas and font sizes otherwise create a huge image.
for extension in ["pdf", "svg", "png"]:
    path = output_stem.with_suffix(f".{extension}")
    fig.savefig(
        path,
        dpi=150,
        bbox_inches="tight",
        facecolor="white",
    )
    print(f"Saved: {path}")

plt.close(fig)