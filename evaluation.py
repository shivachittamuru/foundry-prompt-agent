import json
import os
import time
from pathlib import Path

from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileID,
)

from src.foundry_prompt_agent.agent import ask_agent, project_client


DATASET_PATH = Path("evals/contoso_agent_eval_v2.jsonl")
RESULTS_PATH = Path("evals/results_v2.jsonl")

JUDGE_MODEL = os.environ["FOUNDRY_JUDGE_MODEL"]

DATASET_NAME = "contoso-agent-results"
DATASET_VERSION = "2"


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

    # 3. Define exactly two evaluators
    testing_criteria = [
        # Deterministic evaluator
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="f1",
            evaluator_name="builtin.f1_score",
            data_mapping={
                "response": "{{item.response}}",
                "ground_truth": "{{item.ground_truth}}",
            },
        ),

        # LLM-as-a-judge evaluator
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={
                "model": JUDGE_MODEL,
            },
            data_mapping={
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        ),
    ]

    # 4. Create the evaluation definition in Foundry
    evaluation = openai_client.evals.create(
        name="contoso-agent-baseline",
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


def main() -> None:
    generate_results()
    run_cloud_evaluation()


if __name__ == "__main__":
    main()