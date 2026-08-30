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
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    fig, ax = plt.subplots(figsize=(8.5, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
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

    box(2.5, 9.0, 5.0, 0.7, "Mechanical Scientific Method", fc="#DDEEFF")
    arrow(5.0, 9.0, 5.0, 8.55)
    box(2.5, 7.8, 5.0, 0.7, "FCO / FCG custody substrate", fc="#DDEEFF")
    arrow(5.0, 7.8, 5.0, 7.35)
    box(2.0, 6.5, 6.0, 0.8, "Mechanical Scientific Models\n(proposed model class)", fc="#FFF4DD")
    arrow(3.2, 6.5, 2.8, 5.95)
    arrow(6.8, 6.5, 7.2, 5.95)
    box(0.6, 5.0, 3.6, 0.9, "HydraDG\n(primary evaluated implementation)", fc="#E8F8E8")
    box(5.8, 5.0, 3.6, 1.1, "Vithia\nCOMPANION_IMPLEMENTATION\nZERO_PRIMARY_WEIGHT_EXP008_009", fc="#F5F5F5", fontsize=8)
    arrow(2.4, 5.0, 2.4, 4.45)
    box(0.4, 3.2, 4.0, 1.1, "SeedGraph / Ollarma / HydraLamp\n(execution & systems validation)", fc="#F0F0FF", fontsize=8)
    arrow(2.4, 3.2, 2.4, 2.65)
    box(0.4, 1.5, 4.0, 1.0, "EXP-008 / EXP-009\nUNDERPOWERED | EFFECT_NOT_ESTABLISHED", fc="#FDECEC", ec="#8B0000", fontsize=8)

    ax.set_title("F1: Proposed hierarchy (conceptual; not treatment-effect evidence)", fontsize=10)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
