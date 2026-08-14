import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileID,
)

from src.foundry_prompt_agent.agent import ask_agent, project_client
from src.foundry_prompt_agent.tokenomics import (
    ladder_record,
    summarize_economics,
    summarize_effectiveness,
    summarize_efficiency,
    summarize_margin,
)


DATASET_PATH = Path("evals/contoso_agent_eval_v1.jsonl")
RESULTS_PATH = Path("evals/results_v1.jsonl")
HISTORY_PATH = Path("evals/tokenomics_history.jsonl")

JUDGE_MODEL = os.environ["FOUNDRY_JUDGE_MODEL"]


DATASET_NAME = "contoso-agent-results"

github_sha = os.getenv("GITHUB_SHA")

RUN_ID = (
    github_sha[:8]
    if github_sha
    else datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
)

DATASET_VERSION = RUN_ID

BEHAVIOR_THRESHOLD = float(
    os.getenv("BEHAVIOR_PASS_RATE_THRESHOLD", "0.90")
)

SCOPE_THRESHOLD = float(
    os.getenv("SCOPE_PASS_RATE_THRESHOLD", "1.00")
)

# Business assumption: value of one successful task. Varies by deployment context.
VALUE_PER_SUCCESS_USD = float(os.getenv("VALUE_PER_SUCCESS_USD", "0.10"))

# Business assumptions for the margin rung. All vary by deployment context.
REVIEW_COST_PER_TASK_USD = float(os.getenv("REVIEW_COST_PER_TASK_USD", "0.02"))
ERROR_COST_PER_FAILURE_USD = float(os.getenv("ERROR_COST_PER_FAILURE_USD", "0.50"))
JUDGE_COST_PER_RUN_USD = float(os.getenv("JUDGE_COST_PER_RUN_USD", "0.00"))


def load_dataset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip() and not line.lstrip().startswith("//")
        ]


def generate_results() -> dict:
    cases = load_dataset(DATASET_PATH)
    usages = []

    with RESULTS_PATH.open("w", encoding="utf-8") as output_file:
        for case in cases:
            print(f"Running agent: {case['name']}")

            response, usage = ask_agent(case["query"])
            usages.append(usage)

            # Foundry validates every uploaded field, so usage stays local.
            result = {
                **case,
                "response": response,
            }

            output_file.write(json.dumps(result) + "\n")

    print(f"Saved agent responses to {RESULTS_PATH}")

    efficiency = summarize_efficiency(usages)
    print_efficiency(efficiency)
    return efficiency


def print_efficiency(summary: dict) -> None:
    print("\n=== Token Efficiency ===")
    print(f"Tasks: {summary['tasks']}")
    print(f"Total tokens: {summary['total_tokens']:,}")
    print(f"Tokens per task: {summary['tokens_per_task']:,.1f}")
    print(f"  input/task:  {summary['input_tokens_per_task']:,.1f}")
    print(f"  output/task: {summary['output_tokens_per_task']:,.1f}")
    print(f"Total cost: ${summary['total_cost']:.6f}")
    print(f"Cost per task: ${summary['cost_per_task']:.6f}")


def print_effectiveness(summary: dict) -> None:
    print("\n=== Token Effectiveness ===")
    print(f"Success rate: {summary['success_rate']:.1%}")
    print(f"Successful tasks: {summary['successful_tasks']:.1f}")
    print(f"Tokens per success: {summary['tokens_per_success']:,.1f}")
    print(f"Cost per success: ${summary['cost_per_success']:.6f}")


def print_economics(summary: dict) -> None:
    print("\n=== Token Economics ===")
    print(f"Value per success (assumed): ${summary['value_per_success']:.2f}")
    print(f"Total value created: ${summary['total_value']:.2f}")
    print(f"Total token cost: ${summary['total_cost']:.6f}")
    print(f"Value per dollar: {summary['value_per_dollar']:,.1f}x")


def print_margin(summary: dict) -> None:
    print("\n=== Token Margin ===")
    print(f"Business value created: ${summary['value']:.2f}")
    print(f"- AI runtime cost:      ${summary['ai_runtime_cost']:.6f}")
    print(f"- Human review cost:    ${summary['human_review_cost']:.2f}")
    print(f"- Error/risk cost:      ${summary['error_risk_cost']:.2f}")
    print(f"= Token margin:         ${summary['margin']:.2f}")
    print(f"Profitable: {summary['profitable']}")


def append_history(record: dict) -> None:
    with HISTORY_PATH.open("a", encoding="utf-8") as history_file:
        history_file.write(json.dumps(record) + "\n")


def run_cloud_evaluation() -> None:
    # 1. Upload our generated response dataset to Foundry
    dataset = project_client.datasets.upload_file(
        name=DATASET_NAME,
        version=DATASET_VERSION,
        file_path=str(RESULTS_PATH),
    )

    print(f"Uploaded dataset: {dataset.id}")

    openai_client = project_client.get_openai_client()

    # 2. Tell Foundry what each JSONL row looks like
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "category": {"type": "string"},
                "query": {"type": "string"},
                "ground_truth": {"type": "string"},
                "response": {"type": "string"},
            },
            "required": [
                "query",
                "ground_truth",
                "response",
            ],
        },
    )

    # 3. Define the custom evaluators registered in Foundry.
    # `name` must match the keys read by enforce_quality_gate, and
    # `evaluator_name` must match the names registered in Foundry.
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="contoso_behavior_rubric",
            evaluator_name="contoso_behavior_rubric",
            initialization_parameters={
                "deployment_name": JUDGE_MODEL,
                "pass_threshold": 0.5,
            },
            data_mapping={
                "query": "{{item.query}}",
                "ground_truth": "{{item.ground_truth}}",
                "response": "{{item.response}}",
            },
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="contoso_scope_adherence",
            evaluator_name="contoso_scope_adherence",
            initialization_parameters={
                "pass_threshold": 0.5,
            },
            data_mapping={
                "category": "{{item.category}}",
                "response": "{{item.response}}",
            },
        ),
    ]

    # 4. Create the evaluation definition in Foundry
    evaluation = openai_client.evals.create(
        name=f"contoso-regression-{RUN_ID}",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )

    print(f"Created evaluation: {evaluation.id}")

    # 5. Run it against our uploaded JSONL dataset
    run = openai_client.evals.runs.create(
        eval_id=evaluation.id,
        name="contoso-agent-baseline-v2",
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileID(
                type="file_id",
                id=dataset.id,
            ),
        ),
    )

    print(f"Started evaluation run: {run.id}")

    # 6. Poll until Foundry finishes
    while run.status not in {"completed", "failed", "cancelled"}:
        print(f"Evaluation status: {run.status}")
        time.sleep(5)

        run = openai_client.evals.runs.retrieve(
            eval_id=evaluation.id,
            run_id=run.id,
        )

    print(f"Final status: {run.status}")

    if run.status != "completed":
        report_run_failure(openai_client, evaluation.id, run)

    return run


def report_run_failure(openai_client, eval_id: str, run) -> None:
    print(f"\n=== Run did not complete: {run.status} ===")

    run_error = getattr(run, "error", None)
    if run_error:
        print(f"Run-level error: {run_error}")

    counts = getattr(run, "result_counts", None)
    if counts:
        print(f"Result counts: {counts}")

    # Surface per-item errors, which usually explain evaluator failures.
    try:
        output_items = openai_client.evals.runs.output_items.list(
            eval_id=eval_id,
            run_id=run.id,
        )
        for item in output_items:
            for result in getattr(item, "results", []) or []:
                if isinstance(result, dict) and result.get("error"):
                    print(f"- {result.get('name')}: {result['error']}")
    except Exception as exc:  # diagnostics only; never mask the original failure
        print(f"Could not fetch per-item errors: {exc}")



def get_pass_rate(run, evaluator_name: str) -> float:
    for result in run.per_testing_criteria_results or []:
        if result.testing_criteria == evaluator_name:
            total = result.passed + result.failed
            return result.passed / total if total else 0.0

    raise RuntimeError(
        f"Evaluator result not found: {evaluator_name}"
    )


def enforce_quality_gate(run) -> None:
    if run.status != "completed":
        raise RuntimeError(
            f"Evaluation did not complete successfully: {run.status}"
        )

    behavior_pass_rate = get_pass_rate(
        run,
        "contoso_behavior_rubric",
    )

    scope_pass_rate = get_pass_rate(
        run,
        "contoso_scope_adherence",
    )

    print("\n=== Regression Gate ===")
    print(
        f"Behavior rubric: "
        f"{behavior_pass_rate:.1%} "
        f"(required >= {BEHAVIOR_THRESHOLD:.1%})"
    )
    print(
        f"Scope adherence: "
        f"{scope_pass_rate:.1%} "
        f"(required >= {SCOPE_THRESHOLD:.1%})"
    )

    failures = []

    if behavior_pass_rate < BEHAVIOR_THRESHOLD:
        failures.append(
            "Behavior rubric regression: "
            f"{behavior_pass_rate:.1%} "
            f"< {BEHAVIOR_THRESHOLD:.1%}"
        )

    if scope_pass_rate < SCOPE_THRESHOLD:
        failures.append(
            "Scope adherence regression: "
            f"{scope_pass_rate:.1%} "
            f"< {SCOPE_THRESHOLD:.1%}"
        )

    if failures:
        print("\nQUALITY GATE FAILED")
        for failure in failures:
            print(f"- {failure}")

        sys.exit(1)

    print("\nQUALITY GATE PASSED")


def main() -> None:
    efficiency = generate_results()
    run = run_cloud_evaluation()

    print(f"Final status: {run.status}")
    print(f"Foundry report: {run.report_url}")

    # Behavior rubric is the success signal; scope adherence is a separate guardrail.
    if run.status == "completed":
        success_rate = get_pass_rate(run, "contoso_behavior_rubric")
        effectiveness = summarize_effectiveness(efficiency, success_rate)
        print_effectiveness(effectiveness)

        economics = summarize_economics(
            efficiency, effectiveness, VALUE_PER_SUCCESS_USD
        )
        print_economics(economics)

        margin = summarize_margin(
            efficiency,
            effectiveness,
            economics,
            REVIEW_COST_PER_TASK_USD,
            ERROR_COST_PER_FAILURE_USD,
            JUDGE_COST_PER_RUN_USD,
        )
        print_margin(margin)

        record = {
            "run_id": RUN_ID,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **ladder_record(efficiency, effectiveness, economics, margin),
        }
        append_history(record)
        print(f"\nAppended ladder to {HISTORY_PATH}")

    enforce_quality_gate(run)


if __name__ == "__main__":
    main()