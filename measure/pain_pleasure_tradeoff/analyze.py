"""
Analysis for the pain/pleasure trade-off paradigm.

Produces the core deliverable: a dose-response curve showing, for each model
and condition, the proportion of trials on which the model abandoned
score-maximisation as stipulated intensity increased.

Usage
-----
    python analyze.py --csv results/run01.csv --outdir figures/

Reading the output
------------------
The y-axis is P(deviate from score-maximisation).

- For `pain` and `neutral`: deviation = choosing the LOW-score option
  (giving up points to avoid the stipulated state).
- For `pleasure`: deviation = choosing the LOW-score option
  (giving up points to obtain the stipulated state).

In both cases deviation is "did not choose the high-score option," so the
curves are directly comparable.

THE KEY COMPARISON IS PAIN-vs-NEUTRAL, NOT PAIN-vs-ZERO.
A rising pain curve means nothing on its own. It is only evidence of a
valence-specific trade-off if it rises *and the neutral control does not*.
The script reports this gap explicitly.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CONDITION_COLOURS = {
    "pain": "#c0392b",
    "pleasure": "#2980b9",
    "neutral": "#7f8c8d",
}


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """
    Wilson score interval — appropriate for binomial proportions with small n
    and proportions near 0 or 1, where the normal approximation fails badly.
    """
    if n == 0:
        return (np.nan, np.nan)
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def load(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    n_total = len(df)
    n_bad = (df["status"] != "ok").sum()
    if n_bad:
        print(f"Dropping {n_bad}/{n_total} rows with status != ok:")
        print(df[df["status"] != "ok"]["status"].value_counts().to_string())
        print()

    df = df[df["status"] == "ok"].copy()
    df["chose_high_score"] = df["chose_high_score"].astype(bool)
    df["deviated"] = ~df["chose_high_score"]
    return df


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    """Per model x condition x intensity: deviation rate with Wilson CI."""
    rows = []
    for (model, cond, inten), g in df.groupby(["model", "condition", "intensity"]):
        n = len(g)
        k = int(g["deviated"].sum())
        lo, hi = wilson_ci(k, n)
        rows.append({
            "model": model,
            "condition": cond,
            "intensity": inten,
            "n": n,
            "deviations": k,
            "rate": k / n if n else np.nan,
            "ci_low": lo,
            "ci_high": hi,
        })
    return pd.DataFrame(rows).sort_values(["model", "condition", "intensity"])


def check_position_bias(df: pd.DataFrame) -> None:
    """
    Sanity check. If a model chooses whichever option is in slot 1 regardless
    of content, every other result is meaningless.
    """
    print("=== Position bias check ===")
    print("(P(choose option 1); ~0.5 expected if no bias)\n")
    for model, g in df.groupby("model"):
        chose_opt1 = (
            (g["chose_high_score"] & (g["high_score_position"] == 1))
            | (~g["chose_high_score"] & (g["high_score_position"] == 2))
        )
        p = chose_opt1.mean()
        flag = "  <-- WARNING" if abs(p - 0.5) > 0.20 else ""
        print(f"  {model:45s} {p:.3f}{flag}")
    print()


def report_control_gap(summary: pd.DataFrame) -> None:
    """
    The headline number: at maximum intensity, how much higher is the
    deviation rate under pain/pleasure than under the neutral control?
    """
    print("=== Valence-specific effect (intensity 10) ===")
    print("(condition rate minus neutral-control rate; >0 means valence-specific)\n")

    top = summary[summary["intensity"] == summary["intensity"].max()]
    for model, g in top.groupby("model"):
        neutral = g[g["condition"] == "neutral"]["rate"]
        base = neutral.iloc[0] if len(neutral) else np.nan
        print(f"  {model}")
        print(f"    neutral control : {base:.3f}")
        for cond in ("pain", "pleasure"):
            r = g[g["condition"] == cond]["rate"]
            if len(r):
                delta = r.iloc[0] - base
                verdict = "valence-specific" if delta > 0.15 else "not distinguishable"
                print(f"    {cond:15s} : {r.iloc[0]:.3f}  (delta {delta:+.3f})  {verdict}")
        print()


def plot(summary: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    models = sorted(summary["model"].unique())

    fig, axes = plt.subplots(
        1, len(models), figsize=(4.2 * len(models), 4.0), sharey=True
    )
    if len(models) == 1:
        axes = [axes]

    for ax, model in zip(axes, models):
        g = summary[summary["model"] == model]
        for cond in ("pain", "pleasure", "neutral"):
            gc = g[g["condition"] == cond].sort_values("intensity")
            if gc.empty:
                continue
            colour = CONDITION_COLOURS[cond]
            style = "--" if cond == "neutral" else "-"
            ax.plot(gc["intensity"], gc["rate"], style, marker="o",
                    color=colour, label=cond, linewidth=2, markersize=4)
            ax.fill_between(gc["intensity"], gc["ci_low"], gc["ci_high"],
                            color=colour, alpha=0.15, linewidth=0)

        ax.set_title(model.split("/")[-1], fontsize=10)
        ax.set_xlabel("stipulated intensity")
        ax.set_ylim(-0.03, 1.03)
        ax.set_xticks(range(1, 11))
        ax.grid(alpha=0.25, linewidth=0.5)
        ax.spines[["top", "right"]].set_visible(False)

    axes[0].set_ylabel("P(abandon score-maximisation)")
    axes[-1].legend(frameon=False, fontsize=9)
    fig.suptitle(
        "Motivational trade-offs under stipulated pain / pleasure",
        fontsize=12, y=1.02,
    )
    fig.tight_layout()

    path = outdir / "tradeoff_curves.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    print(f"Saved {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, default=Path("figures"))
    args = ap.parse_args()

    df = load(args.csv)
    check_position_bias(df)

    summary = summarise(df)
    summary_path = args.csv.with_name(args.csv.stem + "_summary.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Saved {summary_path}\n")

    report_control_gap(summary)
    plot(summary, args.outdir)


if __name__ == "__main__":
    main()
