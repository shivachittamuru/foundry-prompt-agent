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


DATASET_PATH = Path("evals/contoso_agent_eval_v1.jsonl")
RESULTS_PATH = Path("evals/results_v1.jsonl")

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


def load_dataset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def generate_results() -> None:
    cases = load_dataset(DATASET_PATH)

    with RESULTS_PATH.open("w", encoding="utf-8") as output_file:
        for case in cases:
            print(f"Running agent: {case['name']}")

            response = ask_agent(case["query"])

            result = {
                **case,
                "response": response,
            }

            output_file.write(json.dumps(result) + "\n")

    print(f"Saved agent responses to {RESULTS_PATH}")


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

    return run


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
    generate_results()
    run = run_cloud_evaluation()
    
    print(f"Final status: {run.status}")
    print(f"Foundry report: {run.report_url}")

    enforce_quality_gate(run)


if __name__ == "__main__":
    main()