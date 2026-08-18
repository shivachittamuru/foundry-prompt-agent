import json

import pytest

from foundry_prompt_agent import history

LEGACY_ROW = {
    "run_id": "legacy01",
    "tasks": 10,
    "total_cost": 0.1,
    "success_rate": 0.9,
    "margin": 1.23,
    "profitable": True,
}


def business_row(run_id: str, **overrides) -> dict:
    row = {
        "run_id": run_id,
        "timestamp_utc": "2026-08-18T00:00:00+00:00",
        "tasks": 10,
        "total_tokens": 10_000,
        "total_cost": 0.1,
        "tokens_per_task": 1_000.0,
        "cost_per_task": 0.01,
        "success_rate": 0.9,
        "successful_tasks": 9.0,
        "cost_per_success": 0.0111,
        "missed_contacts_per_day": 100,
        "ai_eligible_rate": 0.6,
        "conversion_rate": 0.3,
        "average_order_value_usd": 10.0,
        "contribution_margin": 0.35,
        "days_per_month": 30,
        "ai_value_multiple": 200.0,
        "break_even_conversion_rate": 0.0015,
    }
    row.update(overrides)
    return row


def write_history(path, rows) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_load_history_returns_every_row_including_legacy(tmp_path):
    path = tmp_path / "tokenomics_history.jsonl"
    write_history(path, [LEGACY_ROW, business_row("run-a")])

    records = history.load_history(path)

    assert [record["run_id"] for record in records] == [
        "legacy01",
        "run-a",
    ]


def test_load_history_raises_when_file_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        history.load_history(tmp_path / "missing.jsonl")


def test_load_business_runs_ignores_legacy_rows(tmp_path):
    path = tmp_path / "tokenomics_history.jsonl"
    write_history(path, [LEGACY_ROW, business_row("run-a")])

    runs = history.load_business_runs(path)

    assert [run["run_id"] for run in runs] == ["run-a"]


def test_load_business_runs_raises_when_only_legacy_rows_exist(tmp_path):
    path = tmp_path / "tokenomics_history.jsonl"
    write_history(path, [LEGACY_ROW])

    with pytest.raises(RuntimeError):
        history.load_business_runs(path)


def test_latest_business_run_selects_the_last_compatible_row(tmp_path):
    path = tmp_path / "tokenomics_history.jsonl"
    write_history(
        path,
        [business_row("run-a"), LEGACY_ROW, business_row("run-b")],
    )

    assert history.latest_business_run(path)["run_id"] == "run-b"


def test_append_run_preserves_existing_rows(tmp_path):
    path = tmp_path / "tokenomics_history.jsonl"
    original_rows = [LEGACY_ROW, business_row("run-a")]
    write_history(path, original_rows)

    history.append_run(business_row("run-b"), path)

    records = history.load_history(path)

    assert records[:2] == original_rows
    assert records[-1]["run_id"] == "run-b"


def test_append_run_creates_the_ledger_when_absent(tmp_path):
    path = tmp_path / "nested" / "tokenomics_history.jsonl"

    history.append_run(business_row("run-a"), path)

    assert history.latest_business_run(path)["run_id"] == "run-a"
