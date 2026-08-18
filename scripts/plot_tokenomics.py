"""Plot AI Value Multiple across historical evaluation runs.

Run from the repository root:

    uv run scripts/plot_tokenomics.py

Reads measured history only. Never calls the agent, Foundry, or any model.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from foundry_prompt_agent import history

PLOT_PATH = Path("docs/images/tokenomics_value_multiple.png")


def main() -> None:
    try:
        records = history.load_business_runs()
    except (FileNotFoundError, RuntimeError) as exc:
        print(exc)
        return

    labels = [record["run_id"] for record in records]
    values = [record["ai_value_multiple"] for record in records]

    print(
        f"{'run_id':<18}"
        f"{'success':>12}"
        f"{'cost/task':>14}"
        f"{'value multiple':>18}"
    )

    for record in records:
        print(
            f"{record['run_id']:<18}"
            f"{record['success_rate']:>11.1%}"
            f"${record['cost_per_task']:>12.6f}"
            f"{record['ai_value_multiple']:>17.1f}x"
        )

    PLOT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(
        range(len(records)),
        values,
        marker="o",
    )

    ax.axhline(
        y=1.0,
        linestyle="--",
        label="Break even",
    )

    ax.set_xlabel("Evaluation run")
    ax.set_ylabel("AI Value Multiple")
    ax.set_title(
        "Recovered Contribution per $1 of AI Inference"
    )

    ax.set_xticks(range(len(records)))
    ax.set_xticklabels(
        labels,
        rotation=45,
        ha="right",
    )

    ax.legend()

    fig.tight_layout()
    fig.savefig(
        PLOT_PATH,
        dpi=150,
    )

    print(f"\nSaved plot to {PLOT_PATH}")


if __name__ == "__main__":
    main()
