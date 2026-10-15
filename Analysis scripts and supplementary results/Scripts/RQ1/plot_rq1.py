#!/usr/bin/env python3

from pathlib import Path
import argparse
import textwrap

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size


DEFAULT_INPUT = 'your file.xlsx'

REPO = 'PROPOSED'
TOPIC = 'ADR type'

GROUPS = {
    'business': 'repo_busi_domain',
    'software': 'repo_soft_domain'
}


# ============================================================
# Font settings — aligned with previous figure
# ============================================================

BASE_FONT_SIZE = 24

# Heatmap
HEATMAP_XTICK_SIZE = 23
HEATMAP_YTICK_SIZE = 23
HEATMAP_CELL_SIZE = 22
HEATMAP_AXIS_LABEL_SIZE = 25
HEATMAP_COLORBAR_SIZE = 23

# Bootstrap CI figure
CI_SUPTITLE_SIZE = 28
CI_TITLE_SIZE = 24
CI_YTICK_SIZE = 20
CI_XTICK_SIZE = 20
CI_AXIS_LABEL_SIZE = 22


# ============================================================
# Fixed heatmap geometry
# Makes cells comparable across figures
# ============================================================

CELL_WIDTH = 2.20
CELL_HEIGHT = 1.10

LEFT_SPACE = 4.5
RIGHT_SPACE = 1.8
TOP_BOTTOM_SPACE = 3.0

COLORBAR_WIDTH = 0.35
COLORBAR_PAD = 0.20


TOPICS = {
    'D01': 'Allocation of responsibilities',
    'D02': 'Coordination model',
    'D03': 'Data model',
    'D04': 'Management of resources',
    'D05': 'Mapping among architectural elements',
    'D06': 'Binding time decisions',
    'D07': 'Choice of technology',
    'D98': 'Other',
}

EXTRA_TOPIC_LABELS = {
    'D99': 'NA'
}

BUSINESS_LABELS = {
    'B00': 'General-purpose technology / no specific business context',
    'B01': 'Finance and insurance',
    'B02': 'Healthcare and health services',
    'B03': 'Education and training',
    'B04': 'Commerce and consumer services',
    'B05': 'Transportation, logistics and mobility',
    'B06': 'Government and public services',
    'B07': 'Industry, manufacturing and engineering',
    'B08': 'Agriculture, energy and environment',
    'B09': 'Real estate, accommodation and tourism',
    'B10': 'Media, content and entertainment',
    'B11': 'Research and professional domain services',
    'B12': 'Enterprise operations and collaboration',
    'B98': 'Other',
    'B99': 'NA',
}

SOFTWARE_LABELS = {
    'T01': 'Application software',
    'T02': 'System software',
    'T03': 'Web libraries and frameworks',
    'T04': 'Non-web libraries and frameworks',
    'T05': 'Software tools',
    'T06': 'Documentation',
    'T99': 'Other',
}


def topic_label(t):
    return t


def group_label(g, labels):
    return g


EXCLUDE_BUSINESS_CODES = []
EXCLUDE_SOFTWARE_CODES = []


def save(fig, out, name):
    fig.savefig(out / f'{name}.pdf', bbox_inches='tight')
    plt.close(fig)


def heatmap(matrix, sizes, topics, labels, title, out, name):

    # ========================================================
    # Fixed geometry
    # ========================================================

    n_rows = len(matrix)
    n_cols = len(topics)

    fig_width = (
        LEFT_SPACE
        + n_cols * CELL_WIDTH
        + RIGHT_SPACE
    )

    fig_height = (
        n_rows * CELL_HEIGHT
        + TOP_BOTTOM_SPACE
    )

    fig, ax = plt.subplots(
        figsize=(fig_width, fig_height)
    )

    # ========================================================
    # Heatmap
    # ========================================================

    im = ax.imshow(
        matrix.to_numpy() * 100,
        vmin=0,
        vmax=100,
        cmap='YlOrBr',
        aspect='auto'
    )

    # ========================================================
    # X-axis labels
    # ========================================================

    xlabels = [
        textwrap.fill(
            topic_label(t),
            23
        )
        for t in topics
    ]

    ax.set_xticks(
        range(len(topics))
    )

    ax.set_xticklabels(
        xlabels,
        fontsize=HEATMAP_XTICK_SIZE,
        fontweight='bold'
    )

    # ========================================================
    # Y-axis labels
    # ========================================================

    rowlabels = [
        (
            textwrap.fill(
                group_label(g, labels),
                45
            )
            + f'\n(R={sizes.loc[g, "repositories"]:,}; '
              f'N={sizes.loc[g, "adrs"]:,})'
        )
        for g in matrix.index
    ]

    ax.set_yticks(
        range(len(matrix))
    )

    ax.set_yticklabels(
        rowlabels,
        fontsize=HEATMAP_YTICK_SIZE,
        fontweight='bold'
    )

    # ========================================================
    # Cell values
    # Not bold
    # ========================================================

    for i in range(len(matrix)):
        for j in range(len(topics)):

            v = matrix.iloc[i, j] * 100

            ax.text(
                j,
                i,
                f'{v:.1f}',
                ha='center',
                va='center',
                fontsize=HEATMAP_CELL_SIZE,
                color='white' if v > 55 else '#242424'
            )

    # ========================================================
    # No top title
    # ========================================================

    # ax.set_title(...)

    # ========================================================
    # X-axis title
    # ========================================================

    ax.set_xlabel(
        'Decision topic',
        fontsize=HEATMAP_AXIS_LABEL_SIZE,
        fontweight='bold',
        labelpad=14
    )

    # ========================================================
    # Fixed-width colorbar
    # ========================================================

    divider = make_axes_locatable(ax)

    cax = divider.append_axes(
        'right',
        size=axes_size.Fixed(COLORBAR_WIDTH),
        pad=axes_size.Fixed(COLORBAR_PAD)
    )

    cbar = fig.colorbar(
        im,
        cax=cax
    )

    cbar.set_label(
        'Proportion (%)',
        fontsize=HEATMAP_COLORBAR_SIZE,
        fontweight='bold'
    )

    cbar.ax.tick_params(
        labelsize=HEATMAP_COLORBAR_SIZE
    )

    fig.tight_layout()

    save(
        fig,
        out,
        name
    )


def analyze(df, key, group, out, bootstrap, rng):

    excluded = (
        EXCLUDE_BUSINESS_CODES
        if key == 'business'
        else EXCLUDE_SOFTWARE_CODES
    )

    labels = (
        BUSINESS_LABELS
        if key == 'business'
        else SOFTWARE_LABELS
    )

    d = df.loc[
        ~df[group].isin(excluded)
    ].copy()

    order = sorted(
        d[group].unique()
    )

    # ========================================================
    # Two analysis scopes
    # ========================================================

    for scope in [
        'all_adrs',
        'classified_only'
    ]:

        x = (
            d
            if scope == 'all_adrs'
            else d[d[TOPIC].isin(TOPICS)]
        )

        topics = [
            t
            for t in TOPICS
            if t in x[TOPIC].unique()
        ]

        if scope == 'all_adrs':

            topics += sorted(
                set(x[TOPIC])
                - set(TOPICS)
            )

        sizes = (
            x.groupby(group)
            .agg(
                adrs=(TOPIC, 'size'),
                repositories=(REPO, 'nunique')
            )
        )

        active_order = [
            g
            for g in order
            if g in sizes.index
        ]

        sizes = sizes.reindex(
            active_order
        )

        cnt = (
            pd.crosstab(
                x[group],
                x[TOPIC]
            )
            .reindex(
                index=active_order,
                columns=topics,
                fill_value=0
            )
        )

        # ADR-weighted
        adr = cnt.div(
            cnt.sum(axis=1),
            axis=0
        )

        # ====================================================
        # Repository-equal
        # ====================================================

        rc = (
            pd.crosstab(
                [x[group], x[REPO]],
                x[TOPIC]
            )
            .reindex(
                columns=topics,
                fill_value=0
            )
        )

        rp = rc.div(
            rc.sum(axis=1),
            axis=0
        )

        equal = (
            rp.groupby(level=0)
            .mean()
            .reindex(active_order)
        )




        # ====================================================
        # Heatmaps
        # ====================================================

        for method, matrix in [
            ('adr_weighted', adr),
            ('repo_equal', equal)
        ]:

            heatmap(
                matrix,
                sizes,
                topics,
                labels,
                (
                    f'{key.capitalize()} context | '
                    f'{scope.replace("_", " ")} | '
                    f'{method.replace("_", " ")}'
                ),
                out,
                f'{key}_{scope}_{method}_heatmap'
            )

        # ====================================================
        # Repository bootstrap
        # ====================================================

        results = []

        for g in active_order:

            values = (
                rp.xs(
                    g,
                    level=0
                )
                .to_numpy()
            )

            draws = np.empty(
                (
                    bootstrap,
                    len(topics)
                )
            )

            for b in range(bootstrap):

                draws[b] = values[
                    rng.integers(
                        0,
                        len(values),
                        len(values)
                    )
                ].mean(axis=0)

            lo, hi = np.quantile(
                draws,
                [.025, .975],
                axis=0
            )

            for j, t in enumerate(topics):

                results.append({
                    'group': g,
                    'topic': t,
                    'mean': values[:, j].mean(),
                    'low': (
                        lo[j]
                        if len(values) > 1
                        else np.nan
                    ),
                    'high': (
                        hi[j]
                        if len(values) > 1
                        else np.nan
                    ),
                    'repositories': len(values)
                })

        ci = pd.DataFrame(
            results
        )


        # ====================================================
        # Compact uncertainty figure
        # ====================================================

        if scope == 'classified_only':

            fig_height = max(
                15,
                len(active_order) * 1.05 + 5
            )

            fig, axes = plt.subplots(
                2,
                4,
                figsize=(30, fig_height),
                sharey=True
            )

            for ax, t in zip(
                axes.flat,
                topics
            ):

                z = (
                    ci[
                        ci.topic == t
                    ]
                    .set_index('group')
                    .reindex(active_order)
                )

                y = np.arange(
                    len(z)
                )

                mean = (
                    z['mean']
                    .to_numpy()
                    * 100
                )

                ax.hlines(
                    y,
                    z.low * 100,
                    z.high * 100,
                    color='#9a6735',
                    linewidth=2.2
                )

                ax.scatter(
                    mean,
                    y,
                    color='#70421e',
                    s=42,
                    zorder=3
                )

                ax.set_title(
                    textwrap.fill(
                        topic_label(t),
                        26
                    ),
                    fontsize=CI_TITLE_SIZE,
                    fontweight='bold',
                    pad=14
                )

                ax.set_xlim(
                    0,
                    100
                )

                ax.set_yticks(
                    y
                )

                ax.set_yticklabels(
                    [
                        textwrap.fill(
                            group_label(g, labels),
                            38
                        )
                        for g in active_order
                    ],
                    fontsize=CI_YTICK_SIZE,
                    fontweight='bold'
                )

                ax.set_xlabel(
                    'Repository-equal proportion (%)',
                    fontsize=CI_AXIS_LABEL_SIZE,
                    fontweight='bold'
                )

                ax.tick_params(
                    axis='x',
                    labelsize=CI_XTICK_SIZE
                )

                ax.grid(
                    axis='x',
                    alpha=.2
                )

                ax.set_ylim(
                    len(active_order) - .5,
                    -.5
                )

            for ax in list(
                axes.flat
            )[len(topics):]:

                ax.axis('off')

            # No overall title
            fig.tight_layout()

            save(
                fig,
                out,
                f'{key}_classified_repo_ci'
            )


def main():

    p = argparse.ArgumentParser(
        description=__doc__
    )

    p.add_argument(
        '--input',
        type=Path,
        default=(
            Path(__file__)
            .resolve()
            .parent
            / DEFAULT_INPUT
        )
    )

    p.add_argument(
        '--output',
        type=Path,
        default=None
    )

    p.add_argument(
        '--bootstrap',
        type=int,
        default=1000
    )

    a = p.parse_args()

    if a.bootstrap < 100:

        raise ValueError(
            '--bootstrap must be at least 100'
        )

    out = (
        a.output
        or a.input.parent / 'rq1_figures'
    )

    out.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # Read input
    # ========================================================

    df = pd.read_excel(
        a.input,
        sheet_name=0,
        engine='openpyxl'
    )

    required = [
        REPO,
        TOPIC,
        *GROUPS.values()
    ]

    missing = (
        set(required)
        - set(df.columns)
    )

    if missing:

        raise ValueError(
            f'Missing columns: {missing}'
        )

    for c in required:

        df[c] = (
            df[c]
            .fillna('MISSING')
            .astype(str)
            .str.strip()
            .replace(
                '',
                'MISSING'
            )
        )

    if (
        df[REPO] == 'MISSING'
    ).any():

        raise ValueError(
            'Missing repository identifiers; '
            'fix before plotting.'
        )

    # ========================================================
    # Repository category consistency
    # ========================================================

    for c in GROUPS.values():

        conflicts = (
            df.groupby(REPO)[c]
            .nunique()
        )

        if (
            conflicts > 1
        ).any():

            raise ValueError(
                f'Inconsistent repository category: {c}'
            )

    # ========================================================
    # Global style
    # ========================================================

    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': BASE_FONT_SIZE,

        'axes.labelsize':
            HEATMAP_AXIS_LABEL_SIZE,

        'xtick.labelsize':
            HEATMAP_XTICK_SIZE,

        'ytick.labelsize':
            HEATMAP_YTICK_SIZE,

        'axes.spines.top':
            False,

        'axes.spines.right':
            False,

        'pdf.fonttype':
            42,

        'ps.fonttype':
            42,

        'svg.fonttype':
            'none'
    })

    rng = np.random.default_rng(
        20261002
    )

    for key, group in GROUPS.items():

        analyze(
            df,
            key,
            group,
            out,
            a.bootstrap,
            rng
        )

    print(
        f'Complete: {len(df):,} ADRs, '
        f'{df[REPO].nunique():,} repositories. '
        f'Output: {out.resolve()}'
    )


if __name__ == '__main__':
    main()