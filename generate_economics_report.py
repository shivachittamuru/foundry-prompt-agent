import json
from pathlib import Path
from src.foundry_prompt_agent.business_economics import (
    summarize_business_economics,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HISTORY_PATH = Path(
    "evals/tokenomics_history.jsonl"
)
SENSITIVITY_PLOT_PATH = Path(
    "docs/images/tokenomics_sensitivity.png"
)
REPORT_PATH = Path(
    "reports/token_economics_latest.md"
)


def load_latest_run(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    # Ignore old records from the previous economics model.
    records = [
        record
        for record in records
        if "ai_value_multiple" in record
    ]

    if not records:
        raise RuntimeError(
            "No business-economics runs found. "
            "Run evaluation.py first."
        )

    return records[-1]


def build_conversion_sensitivity(
    latest: dict,
    conversion_rates: list[float],
) -> list[dict]:

    scenarios = []

    for conversion_rate in conversion_rates:
        economics = summarize_business_economics(
            missed_contacts_per_day=latest[
                "missed_contacts_per_day"
            ],
            ai_eligible_rate=latest[
                "ai_eligible_rate"
            ],
            success_rate=latest[
                "success_rate"
            ],
            conversion_rate=conversion_rate,
            average_order_value_usd=latest[
                "average_order_value_usd"
            ],
            contribution_margin=latest[
                "contribution_margin"
            ],
            cost_per_task_usd=latest[
                "cost_per_task"
            ],
            days_per_month=latest[
                "days_per_month"
            ],
        )

        scenarios.append({
            "conversion_rate": conversion_rate,
            **economics,
        })

    return scenarios


def plot_sensitivity(scenarios: list[dict]) -> None:
    conversion_rates = [
        scenario["conversion_rate"] * 100
        for scenario in scenarios
    ]

    value_multiples = [
        scenario["ai_value_multiple"]
        for scenario in scenarios
    ]

    SENSITIVITY_PLOT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(
        conversion_rates,
        value_multiples,
        marker="o",
    )

    ax.axhline(
        y=1.0,
        linestyle="--",
        label="Break even",
    )

    ax.set_xlabel("Customer conversion rate (%)")
    ax.set_ylabel("AI Value Multiple")
    ax.set_title(
        "Token Economics Sensitivity to Conversion"
    )

    ax.grid(
        True,
        linestyle="--",
        alpha=0.3,
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        SENSITIVITY_PLOT_PATH,
        dpi=150,
    )

    plt.close(fig)

    print(
        f"Saved sensitivity chart to "
        f"{SENSITIVITY_PLOT_PATH}"
    )
    
def generate_markdown_report(
    latest: dict,
    scenarios: list[dict],
) -> str:

    scenario_rows = "\n".join(
        (
            f"| {scenario['conversion_rate']:.0%} "
            f"| ${scenario['recovered_contribution_per_month']:,.2f} "
            f"| ${scenario['ai_inference_cost_per_month']:,.2f} "
            f"| {scenario['ai_value_multiple']:,.1f}x |"
        )
        for scenario in scenarios
    )

    return f"""# Contoso Coffee — Token Economics Report

Generated from evaluation run `{latest["run_id"]}`.

> This report combines measured AI performance with explicit business assumptions.
> Business outcomes are modeled estimates, not proven production revenue.

## Executive Summary

The Contoso Coffee agent is evaluated as a demand-recovery system rather than
a labor-replacement system.

The business question is:

> **Can AI economically recover customer demand that would otherwise go unserved?**

The primary economics metric is:

**AI Value Multiple = Recovered Contribution / AI Inference Cost**

For this run:

- Behavior success rate: **{latest["success_rate"]:.1%}**
- Cost per interaction: **${latest["cost_per_task"]:.6f}**
- Cost per successful resolution: **${latest["cost_per_success"]:.6f}**
- Estimated recovered contribution/month: **${latest["recovered_contribution_per_month"]:,.2f}**
- Estimated AI inference cost/month: **${latest["ai_inference_cost_per_month"]:,.2f}**
- AI Value Multiple: **{latest["ai_value_multiple"]:,.1f}x**
- Break-even conversion rate: **{latest["break_even_conversion_rate"]:.2%}**

---

## 1. Measured AI Performance

These values came from the actual agent and Foundry evaluation run.

| Metric | Measured value |
|---|---:|
| Evaluation cases | {latest["tasks"]} |
| Behavior success rate | {latest["success_rate"]:.1%} |
| Tokens per interaction | {latest["tokens_per_task"]:,.1f} |
| Cost per interaction | ${latest["cost_per_task"]:.6f} |
| Cost per successful resolution | ${latest["cost_per_success"]:.6f} |

These values are **measured**, not business assumptions.

---

## 2. Business Assumptions

| Assumption | Value |
|---|---:|
| Missed contacts/day | {latest["missed_contacts_per_day"]} |
| AI-eligible rate | {latest["ai_eligible_rate"]:.0%} |
| Conversion rate | {latest["conversion_rate"]:.0%} |
| Average order value | ${latest["average_order_value_usd"]:.2f} |
| Contribution margin | {latest["contribution_margin"]:.0%} |
| Operating days/month | {latest["days_per_month"]} |

These values are illustrative assumptions and should be replaced with
observed business data in a real pilot.

---

## 3. Estimated Demand-Recovery Funnel

```text
Missed contacts/day
        {latest["missed_contacts_per_day"]:.0f}
          ↓
AI-addressable
        {latest["addressable_contacts_per_day"]:.1f}
          ↓
Successfully served
        {latest["successful_contacts_per_day"]:.1f}
          ↓
Estimated recovered orders
        {latest["recovered_orders_per_day"]:.1f}
"""

def save_report(report: str) -> None:
    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        report,
        encoding="utf-8",
    )

    print(f"Saved report to {REPORT_PATH}")
        
        
def main() -> None:
    latest = load_latest_run(
        HISTORY_PATH
    )
    
    CONVERSION_SCENARIOS = [
            0.05,
            0.10,
            0.20,
            0.30,
        ]

    print(
        f"Using measured run: "
        f"{latest['run_id']}"
    )

    scenarios = build_conversion_sensitivity(
        latest,
        CONVERSION_SCENARIOS,
    )

    plot_sensitivity(
        scenarios
    )

    report = generate_markdown_report(
        latest,
        scenarios,
    )

    save_report(report)


if __name__ == "__main__":
    main()
    
# uv run generate_economics_report.py