import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: render to file, no display needed

import matplotlib.pyplot as plt

HISTORY_PATH = Path("evals/tokenomics_history.jsonl")
PLOT_PATH = Path("docs/images/tokenomics_margin.png")


def load_history(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main() -> None:
    records = load_history(HISTORY_PATH)
    if not records:
        print("No history records found.")
        return

    print(f"{'run_id':<16}{'tasks':>7}{'margin':>12}{'margin/task':>14}")
    for record in records:
        margin_per_task = record["margin"] / record["tasks"] if record["tasks"] else 0.0
        print(
            f"{record['run_id']:<16}"
            f"{record['tasks']:>7}"
            f"{record['margin']:>12.4f}"
            f"{margin_per_task:>14.4f}"
        )

    x = range(len(records))
    labels = [record["run_id"] for record in records]
    total_margin = [record["margin"] for record in records]
    margin_per_task = [record["margin"] / record["tasks"] for record in records]

    PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(x, total_margin, marker="o", color="#1f4e79", label="Total margin")
    ax.set_xlabel("Run")
    ax.set_ylabel("Total margin (USD)", color="#1f4e79")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.grid(True, linestyle="--", alpha=0.4)

    # Per-task margin on a second axis, since total margin scales with task count.
    ax2 = ax.twinx()
    ax2.plot(x, margin_per_task, marker="s", color="#2f7d32", label="Margin per task")
    ax2.set_ylabel("Margin per task (USD)", color="#2f7d32")

    ax.set_title("Token margin over runs")
    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150)
    print(f"\nSaved plot to {PLOT_PATH}")


if __name__ == "__main__":
    main()
