#!/usr/bin/env python3
"""Render F1 Mechanical Scientific Model hierarchy for NewInML manuscript."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/newinml2026_solo/final_v4/manuscript/figures/F1_msm_hierarchy.png"


def main() -> int:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.5)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#E8F0FE", ec="#333333", fontsize=9):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.03",
            linewidth=1.2,
            edgecolor=ec,
            facecolor=fc,
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, wrap=True)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.2,
                color="#444444",
            )
        )

    box(2.5, 9.2, 5.0, 0.7, "Mechanical Scientific Method", fc="#DDEEFF")
    arrow(5.0, 9.2, 5.0, 8.75)
    box(2.5, 8.0, 5.0, 0.7, "FCO / FCG custody substrate", fc="#DDEEFF")
    arrow(5.0, 8.0, 5.0, 7.55)
    box(2.0, 6.7, 6.0, 0.8, "Mechanical Scientific Models\n(proposed model class)", fc="#FFF4DD")
    arrow(3.2, 6.7, 2.8, 6.15)
    arrow(6.8, 6.7, 7.2, 6.15)
    box(0.5, 5.2, 3.6, 0.9, "HydraDG\n(primary evaluated implementation)", fc="#E8F8E8")
    box(
        5.6,
        5.0,
        3.9,
        1.2,
        "Vithia (vitaology / FCO repos)\nPRIOR RUN RECEIPTS (exec host)\nZERO_PRIMARY_WEIGHT EXP008/009",
        fc="#F5F5F5",
        fontsize=7,
    )
    arrow(2.3, 5.2, 2.3, 4.65)
    arrow(7.5, 5.0, 7.5, 4.65)
    box(
        0.2,
        3.35,
        4.4,
        1.25,
        "HydraDG + HydraLamp\nlocal real-time scoring (M1-class, 32GB)\nLongMemEval / benchmarks: small local models only",
        fc="#F0F0FF",
        fontsize=7,
    )
    box(5.4, 3.55, 4.4, 1.05, "Antigence\nanticube + temporal classification", fc="#FFF8E8", fontsize=8)
    arrow(2.4, 3.35, 2.4, 2.75)
    box(
        0.4,
        1.55,
        4.0,
        1.05,
        "EXP-008 / EXP-009\nUNDERPOWERED | EFFECT_NOT_ESTABLISHED",
        fc="#FDECEC",
        ec="#8B0000",
        fontsize=8,
    )

    ax.set_title("F1: Proposed hierarchy (conceptual; not treatment-effect evidence)", fontsize=10)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
