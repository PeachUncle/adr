from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


# ============================================================
# Input and output
# ============================================================
INPUT_FILE = Path("your file.xlsx")
OUTPUT_DIR = Path("rq2_figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Font settings — aligned with RQ1
# ============================================================
BASE_FONT_SIZE = 38

HEATMAP_XTICK_SIZE = 36
HEATMAP_YTICK_SIZE = 36
HEATMAP_CELL_SIZE = 35
HEATMAP_AXIS_LABEL_SIZE = 39
HEATMAP_COLORBAR_SIZE = 36

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT_SIZE,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
})


# ============================================================
# Fixed heatmap geometry — aligned with RQ1
# ============================================================
CELL_WIDTH = 2.20
CELL_HEIGHT = 1.80

LEFT_SPACE = 8.0
RIGHT_SPACE = 1.8
TOP_BOTTOM_SPACE = 3.0

COLORBAR_WIDTH = 0.35
COLORBAR_PAD = 0.20

BLOCK_GAP = 2.40
RIGHT_SPACE = 2.40
PANEL_GAP = TOP_BOTTOM_SPACE


# ============================================================
# Category definitions
# English names are used for parsing and CSV exports.
# Figures display codes only.
# ============================================================
BUSINESS_LABELS = {
    "B00": "General-purpose technology / no specific business context",
    "B01": "Finance and insurance",
    "B02": "Healthcare and health services",
    "B03": "Education and training",
    "B04": "Commerce and consumer services",
    "B05": "Transportation, logistics and mobility",
    "B06": "Government and public services",
    "B07": "Industry, manufacturing and engineering",
    "B08": "Agriculture, energy and environment",
    "B09": "Real estate, accommodation and tourism",
    "B10": "Media, content and entertainment",
    "B11": "Research and professional domain services",
    "B12": "Enterprise operations and collaboration",
    "B98": "Other identifiable specialized business contexts",
    "B99": "Insufficient evidence / undetermined",
}

SOFTWARE_LABELS = {
    "T01": "Application software",
    "T02": "System software",
    "T03": "Web libraries and frameworks",
    "T04": "Non-web libraries and frameworks",
    "T05": "Software tools",
    "T06": "Documentation",
    "T99": "Insufficient evidence / pending review",
}

QA_LABELS = {
    "Q01": "Functional suitability",
    "Q02": "Performance efficiency",
    "Q03": "Compatibility",
    "Q04": "Interaction capability",
    "Q05": "Reliability",
    "Q06": "Security",
    "Q07": "Maintainability",
    "Q08": "Flexibility",
    "Q09": "Safety",
}

NQ_LABELS = {
    "NQ01": "Economic cost",
    "NQ02": "Delivery effort",
    "NQ03": "Team capability",
    "NQ04": "Legal/regulatory constraint",
    "NQ05": "Licensing",
    "NQ06": "Delivery schedule",
    "NQ00": "No non-quality consideration recorded",
}

TR_LABELS = {
    "TR00": "No trade-off recorded in the coded summary",
    "TR01": "Product quality vs product quality",
    "TR02": "Product quality vs non-quality considerations",
    "TR03": "Non-quality vs non-quality considerations",
    "TR04": "Alternative comparison with unclear dimensions",
    "TR99": "Conflicting information or insufficient evidence",
}

# Preserve Q99 as well.
QA_LABELS["Q99"] = "No explicit quality-attribute evidence"

QA_COLUMNS = list(QA_LABELS)
NQ_COLUMNS = list(NQ_LABELS)

# Only TR99 is hidden.
TR_COLUMNS = [
    code for code in TR_LABELS
    if code != "TR99"
]

ALL_COLUMNS = QA_COLUMNS + NQ_COLUMNS + TR_COLUMNS

# Set to a numeric value for a fixed upper bound.
# None: determine the upper bound from both panels.
QA_VMAX = None
NQ_VMAX = None
TR_VMAX = None


# ============================================================
# Load and validate
# ============================================================
df = pd.read_excel(
    INPUT_FILE,
    sheet_name=0,
    engine="openpyxl",
)

required_columns = [
    "PROPOSED",
    "repo_busi_domain",
    "repo_soft_domain",
    "QA",
    "Non-quality considerations",
    "Tradeoff code",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]
if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

if df.empty:
    raise ValueError("The input dataset is empty.")

for column in required_columns:
    df[column] = df[column].fillna("").astype(str).str.strip()

for column in [
    "PROPOSED",
    "repo_busi_domain",
    "repo_soft_domain",
    "QA",
    "Tradeoff code",
]:
    if df[column].eq("").any():
        excel_rows = (
            df.index[df[column].eq("")].to_numpy() + 2
        )
        raise ValueError(
            f"Blank values in {column}; "
            f"Excel rows: {excel_rows[:10].tolist()}"
        )

for column, mapping in [
    ("repo_busi_domain", BUSINESS_LABELS),
    ("repo_soft_domain", SOFTWARE_LABELS),
]:
    unknown_codes = set(df[column]) - set(mapping)
    if unknown_codes:
        raise ValueError(
            f"Unknown codes in {column}: "
            f"{sorted(unknown_codes)}"
        )

    conflicting_repositories = (
        df.groupby("PROPOSED")[column].nunique()
    )
    conflicting_repositories = conflicting_repositories[
        conflicting_repositories.gt(1)
    ]

    if not conflicting_repositories.empty:
        raise ValueError(
            f"Conflicting repository labels in {column}: "
            f"{conflicting_repositories.index.tolist()[:10]}"
        )


# ============================================================
# QA indicators
# ============================================================
def parse_qa(value):
    codes = {
        token
        for token in re.split(r"[;,，；|\s]+", value)
        if token
    }

    unknown_codes = codes - set(QA_LABELS) - {"Q99"}
    if unknown_codes:
        raise ValueError(
            f"Unknown QA codes in {value!r}: "
            f"{sorted(unknown_codes)}"
        )

    if "Q99" in codes and len(codes) > 1:
        raise ValueError(
            f"Q99 cannot be combined with QA codes: {value!r}"
        )

    return codes


qa_sets = df["QA"].map(parse_qa)

for code in QA_COLUMNS:
    df[code] = qa_sets.map(
        lambda codes, current_code=code:
        int(current_code in codes)
    )


# ============================================================
# Non-QA indicators
# ============================================================
nq_sets = df["Non-quality considerations"].map(
    lambda value: {
        item.strip()
        for item in re.split(r"[;；]", value)
        if item.strip()
    }
)

allowed_nq_labels = {
    name
    for code, name in NQ_LABELS.items()
    if code != "NQ00"
}

observed_nq_labels = set().union(*nq_sets.tolist())
unknown_nq_labels = observed_nq_labels - allowed_nq_labels

if unknown_nq_labels:
    raise ValueError(
        f"Unknown non-quality labels: {sorted(unknown_nq_labels)}"
    )

for code, name in NQ_LABELS.items():
    if code == "NQ00":
        df[code] = nq_sets.map(
            lambda values: int(not values)
        )
    else:
        df[code] = nq_sets.map(
            lambda values, current_name=name:
            int(current_name in values)
        )

# ============================================================
# Trade-off indicators
# ============================================================
unknown_tradeoff_codes = (
    set(df["Tradeoff code"]) - set(TR_LABELS)
)

if unknown_tradeoff_codes:
    raise ValueError(
        f"Unknown trade-off codes: "
        f"{sorted(unknown_tradeoff_codes)}"
    )

for code in TR_COLUMNS:
    df[code] = df["Tradeoff code"].eq(code).astype(int)

# TR99 rows remain in the dataset and denominator.
# No TR_ANY indicator is added.

# ============================================================
# Repository-equal proportions
# ============================================================
def summarize_context(context_column, labels):
    # Step 1: calculate proportions within each repository.
    # Denominator: all sampled ADRs in that repository.
    within_repository = df.groupby(
        [context_column, "PROPOSED"],
        sort=False,
    )[ALL_COLUMNS].mean()

    # Step 2: average across repositories within each context.
    # Repositories with zero proportions remain included.
    percentages = (
        within_repository.groupby(level=0).mean() * 100
    )

    sample_sizes = df.groupby(context_column).agg(
        repositories=("PROPOSED", "nunique"),
        adrs=("PROPOSED", "size"),
    )

    order = [
        code for code in labels
        if code in percentages.index
    ]

    return (
        percentages.reindex(order),
        sample_sizes.reindex(order),
    )


business, business_sizes = summarize_context(
    "repo_busi_domain",
    BUSINESS_LABELS,
)

software, software_sizes = summarize_context(
    "repo_soft_domain",
    SOFTWARE_LABELS,
)


# ============================================================
# Shared color scales across the two panels
# ============================================================
def choose_vmax(columns, specified):
    maximum = max(
        business[columns].to_numpy().max(),
        software[columns].to_numpy().max(),
    )

    if specified is not None:
        specified = float(specified)

        if specified <= 0:
            raise ValueError("Color-scale upper bounds must be positive.")

        if specified < maximum:
            raise ValueError(
                f"Specified upper bound {specified} is below "
                f"the observed maximum {maximum:.2f}."
            )

        return specified

    return max(
        5.0,
        float(np.ceil(maximum / 5.0) * 5.0),
    )


blocks = [
    {
        "columns": QA_COLUMNS,
        "ticks": QA_COLUMNS,
        "cmap": "Blues",
        "vmax": choose_vmax(QA_COLUMNS, QA_VMAX),
    },
    {
        "columns": NQ_COLUMNS,
        "ticks": NQ_COLUMNS,
        "cmap": "Oranges",
        "vmax": choose_vmax(NQ_COLUMNS, NQ_VMAX),
    },
    {
        "columns": TR_COLUMNS,
        "ticks": TR_COLUMNS,
        "cmap": "Purples",
        "vmax": choose_vmax(TR_COLUMNS, TR_VMAX),
    },
]


# ============================================================
# Fixed-size layout
# ============================================================
block_widths = [
    len(block["columns"]) * CELL_WIDTH
    for block in blocks
]

block_total_widths = [
    width + COLORBAR_PAD + COLORBAR_WIDTH
    for width in block_widths
]

plot_width = (
    sum(block_total_widths)
    + BLOCK_GAP * (len(blocks) - 1)
)

business_height = len(business) * CELL_HEIGHT
software_height = len(software) * CELL_HEIGHT

figure_width = LEFT_SPACE + plot_width + RIGHT_SPACE
figure_height = (
    TOP_BOTTOM_SPACE
    + business_height
    + PANEL_GAP
    + software_height
    + TOP_BOTTOM_SPACE
)

fig = plt.figure(
    figsize=(figure_width, figure_height)
)

business_bottom = (
    figure_height
    - TOP_BOTTOM_SPACE
    - business_height
)

software_bottom = TOP_BOTTOM_SPACE

panels = [
    (business, business_sizes, business_bottom, "(a) Business domains"),
    (software, software_sizes, software_bottom, "(b) Software types"),
]


# ============================================================
# Draw heatmaps — codes only
# ============================================================
for matrix, sizes, panel_bottom, panel_label in panels:
    panel_height = len(matrix) * CELL_HEIGHT
    block_left = LEFT_SPACE

    for block_index, block in enumerate(blocks):
        block_width = block_widths[block_index]

        ax = fig.add_axes([
            block_left / figure_width,
            panel_bottom / figure_height,
            block_width / figure_width,
            panel_height / figure_height,
        ])

        values = matrix[block["columns"]].to_numpy()
        norm = Normalize(vmin=0, vmax=block["vmax"])
        cmap = plt.get_cmap(block["cmap"])

        ax.imshow(
            values,
            cmap=cmap,
            norm=norm,
            aspect="auto",
            interpolation="nearest",
        )

        ax.set_xticks(
            range(len(block["columns"])),
            labels=block["ticks"],
            fontsize=HEATMAP_XTICK_SIZE,
            fontweight="bold",
        )

        ax.set_yticks(range(len(matrix)))

        if block_index == 0:
            ax.set_yticklabels(
                [
                    f"{code}\n"
                    f"(R={int(sizes.loc[code, 'repositories']):,}; "
                    f"N={int(sizes.loc[code, 'adrs']):,})"
                    for code in matrix.index
                ],
                fontsize=HEATMAP_YTICK_SIZE,
                fontweight="bold",
            )

            ax.annotate(
                panel_label,
                xy=(0, 1),
                xycoords="axes fraction",
                xytext=(0, 25),
                textcoords="offset points",
                fontsize=HEATMAP_AXIS_LABEL_SIZE,
                fontweight="bold",
                ha="left",
                va="bottom",
            )
        else:
            ax.set_yticklabels([])

        ax.tick_params(
            axis="both",
            which="both",
            length=0,
            pad=12,
        )

        ax.set_xticks(
            np.arange(-0.5, len(block["columns"]), 1),
            minor=True,
        )

        ax.set_yticks(
            np.arange(-0.5, len(matrix), 1),
            minor=True,
        )

        ax.grid(
            which="minor",
            color="white",
            linewidth=1.0,
        )

        for spine in ax.spines.values():
            spine.set_visible(False)

        for i in range(values.shape[0]):
            for j in range(values.shape[1]):
                value = values[i, j]

                text = (
                    "<0.1"
                    if 0 < value < 0.1
                    else f"{value:.1f}"
                )

                red, green, blue, _ = cmap(norm(value))
                luminance = (
                    0.2126 * red
                    + 0.7152 * green
                    + 0.0722 * blue
                )

                ax.text(
                    j,
                    i,
                    text,
                    ha="center",
                    va="center",
                    fontsize=HEATMAP_CELL_SIZE,
                    color=(
                        "white"
                        if luminance < 0.52
                        else "#222222"
                    ),
                )

        # Color scale for this block.
        # Bounds are identical in panels (a) and (b).
        colorbar_left = (
            block_left
            + block_width
            + COLORBAR_PAD
        )

        cax = fig.add_axes([
            colorbar_left / figure_width,
            panel_bottom / figure_height,
            COLORBAR_WIDTH / figure_width,
            panel_height / figure_height,
        ])

        colorbar = fig.colorbar(
            ScalarMappable(norm=norm, cmap=cmap),
            cax=cax,
            orientation="vertical",
        )

        colorbar.set_ticks(np.linspace(0, block["vmax"], 5))
        colorbar.ax.tick_params(
            labelsize=HEATMAP_COLORBAR_SIZE,
            labelright=True,
            labelleft=False,
        )
        for tick_label in colorbar.ax.get_yticklabels():
            tick_label.set_fontweight("bold")

        colorbar.ax.set_title(
            "%",
            fontsize=HEATMAP_COLORBAR_SIZE,
            pad=12,
        )

        block_left += (
            block_width
            + COLORBAR_PAD
            + COLORBAR_WIDTH
            + BLOCK_GAP
        )


# ============================================================
# Export figures
# ============================================================
output_stem = OUTPUT_DIR / "rq2_project_context_combined"

output_path = output_stem.with_suffix(".pdf")

fig.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

print(f"Saved: {output_path}")

plt.close(fig)

print(
    f"Complete: {len(df):,} ADRs from "
    f"{df['PROPOSED'].nunique():,} repositories."
)