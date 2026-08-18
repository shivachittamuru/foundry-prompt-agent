"""Append-only experiment ledger for tokenomics runs.

Every evaluation run appends one JSON object to ``evals/tokenomics_history.jsonl``
containing measured AI performance, the business assumptions used, and the
modeled economics for that run.

Rows written by the earlier token-margin model are kept on disk but ignored by
readers that require the current business-economics fields.
"""

from __future__ import annotations

import json
from pathlib import Path

HISTORY_PATH = Path("evals/tokenomics_history.jsonl")

# A row must carry all of these to be usable by the current economics model.
BUSINESS_ECONOMICS_FIELDS = frozenset(
    {
        "run_id",
        "success_rate",
        "tokens_per_task",
        "cost_per_task",
        "cost_per_success",
        "missed_contacts_per_day",
        "ai_eligible_rate",
        "conversion_rate",
        "average_order_value_usd",
        "contribution_margin",
        "days_per_month",
        "ai_value_multiple",
    }
)

NO_COMPATIBLE_RUNS_MESSAGE = (
    "No compatible business-economics history records were found. "
    "Run `uv run scripts/run_evaluation.py` first."
)


def load_history(path: Path = HISTORY_PATH) -> list[dict]:
    """Load every JSONL row, including rows from older schemas."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. "
            "Run `uv run scripts/run_evaluation.py` first."
        )

    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def is_business_run(record: dict) -> bool:
    return BUSINESS_ECONOMICS_FIELDS.issubset(record)


def load_business_runs(path: Path = HISTORY_PATH) -> list[dict]:
    """Load only the rows produced by the current business-economics model."""
    compatible = [
        record for record in load_history(path) if is_business_run(record)
    ]

    if not compatible:
        raise RuntimeError(NO_COMPATIBLE_RUNS_MESSAGE)

    return compatible


def latest_business_run(path: Path = HISTORY_PATH) -> dict:
    return load_business_runs(path)[-1]


def append_run(record: dict, path: Path = HISTORY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(record) + "\n")
