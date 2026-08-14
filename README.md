# Foundry Prompt Agent

A small learning project that walks through the **Microsoft Foundry Prompt Agent lifecycle (ADLC)** using a simple *Contoso Coffee* assistant backed by **Azure AI Search**.

## Overview

The agent answers questions about a coffee-shop menu (prices, descriptions, filtering, budget math, recommendations) and is expected to stay in scope and abstain when it lacks evidence.

The important mental split:

- **The Prompt Agent itself lives in Microsoft Foundry.** Its instructions, model, and Azure AI Search tool are configured and persisted there — not in this repo.
- **This repository is everything *around* that agent:** a thin Python client to invoke it, an evaluation harness, curated datasets, custom evaluators, and a CI regression workflow.

The goal is to demonstrate one core lesson:

> Trust in an agent comes from repeatable evaluation evidence, not from a few successful playground tests.

## Architecture / mental model

```text
User / Evaluation Dataset
         ↓
  Foundry Prompt Agent
         ↓
      GPT model
         ↓
    Azure AI Search
         ↓
       Response
         ↓
Python evaluation harness
         ↓
   Foundry evaluators
         ↓
CI quality gate / monitoring
```

The Python side invokes the persisted agent and drives evaluation. Foundry owns the agent runtime, the judge model, the evaluator catalog, and result persistence.

## Project structure

Only the parts that matter for understanding the flow:

| Path | Purpose |
| --- | --- |
| [src/foundry_prompt_agent/](src/foundry_prompt_agent/) | Thin client. `agent.py` invokes the persisted Foundry Prompt Agent via `AIProjectClient`. |
| [evaluation.py](evaluation.py) | Evaluation harness: generates fresh responses, runs cloud evaluation in Foundry, enforces the quality gate. |
| [evals/](evals/) | Curated JSONL evaluation datasets and generated result/trace files. |
| [data/contoso.json](data/contoso.json) | The Contoso Coffee menu that backs the Azure AI Search index. |
| [docs/](docs/) | Conceptual notes on evaluation, monitoring, and automation. |
| [.github/workflows/](.github/workflows/) | CI regression evaluation workflows. |

## Prerequisites

- **Python `>=3.12`** (see [pyproject.toml](pyproject.toml)).
- **[uv](https://docs.astral.sh/uv/)** for dependency management and running scripts.
- **Azure CLI** (`az`) — the client authenticates with `AzureCliCredential`.
- Access to the appropriate **Microsoft Foundry project**.
- An **existing Prompt Agent** and **Azure AI Search** configuration in that Foundry project. The custom evaluators (`contoso_behavior_rubric`, `contoso_scope_adherence`) must also be registered in Foundry.

## Setup with uv

```bash
# clone and enter the repo
git clone <your-fork-or-repo-url>
cd foundry-prompt-agent

# install the locked environment
uv sync

# sign in so AzureCliCredential can get a token
az login

# create your local env file and fill in the values
cp .env.example .env
```

Populate `.env` with your Foundry project details (see [.env.example](.env.example)):

```text
FOUNDRY_PROJECT_ENDPOINT=       # your Foundry project endpoint
FOUNDRY_AGENT_NAME=foundry-prompt-agent
FOUNDRY_AGENT_VERSION=          # the persisted agent version
FOUNDRY_JUDGE_MODEL=gpt-5       # judge model for LLM-based evaluators
BEHAVIOR_PASS_RATE_THRESHOLD=0.90
SCOPE_PASS_RATE_THRESHOLD=1.00
```

## Running the agent

Invoke the persisted Foundry Prompt Agent directly:

```bash
uv run src/foundry_prompt_agent/agent.py
```

This sends a sample query through `ask_agent()` and prints the agent's response, confirming your Foundry and Azure CLI configuration works end to end.

## Running evaluations

```bash
uv run evaluation.py
```

[evaluation.py](evaluation.py) performs the full loop:

1. **Loads a curated JSONL dataset** from `evals/` (each row has `name`, `category`, `query`, `ground_truth`).
2. **Generates fresh agent responses** by calling the live Foundry agent for every case and writing a results JSONL.
3. **Runs cloud evaluation in Foundry** — uploads the results dataset and creates an evaluation with two **custom evaluators**:
   - `contoso_behavior_rubric` — semantic behavior/grounding/abstention rubric (judged by `FOUNDRY_JUDGE_MODEL`).
   - `contoso_scope_adherence` — checks the agent stays within Contoso Coffee scope.
4. **Enforces quality thresholds.** The behavior rubric must meet `BEHAVIOR_PASS_RATE_THRESHOLD` (default 90%) and scope adherence must meet `SCOPE_PASS_RATE_THRESHOLD` (default 100%).
5. **Exits non-zero** (`sys.exit(1)`) if the run did not complete or any threshold fails — this is what turns a plain evaluation into a regression gate. A link to the Foundry report is printed for diagnosis.

See [docs/evaluation.md](docs/evaluation.md) for the reasoning behind dataset design and evaluator selection.

## CI/CD

Two workflows live under [.github/workflows/](.github/workflows/):

- **[agent-regression-eval.yml](.github/workflows/agent-regression-eval.yml)** — the primary gate. It runs *our own* `evaluation.py` so the project controls dependencies, datasets, evaluators, and failure behavior.
- **[agent-builtin-eval.yml](.github/workflows/agent-builtin-eval.yml)** — an earlier experiment using the managed `microsoft/ai-agent-evals@v3-beta` action, kept for comparison.

Both workflows:

- Authenticate to Azure with **OIDC / workload identity federation** — no long-lived client secret is stored in GitHub.
- Reproduce the environment from **`uv.lock`** (`uv sync --locked`, `uv run --locked`).
- Are wired to run on pull requests / dispatch so regressions can be caught before merge, with **Foundry evaluation results** available for diagnosis.

The push triggers are currently commented out (run via **Run workflow** / `workflow_dispatch`). For the full CI reasoning, OIDC setup, and repository-variable list, see [docs/automation.md](docs/automation.md).

## Learning journey / ADLC

The repository walks through the Agent Development Lifecycle stages:

```text
Build     → Prompt Agent configured in Foundry
Observe   → traces / agent behavior
Evaluate  → curated datasets + built-in and custom evaluators
Optimize  → Agent Optimizer (preview)
Monitor   → continuous and scheduled evaluation
Automate  → GitHub Actions regression gates
```

The recurring theme across every stage: **trust comes from repeatable evaluation evidence, not from a handful of good playground conversations.** Each meaningful change to the prompt, model, or search configuration is re-checked against the same benchmark.

## Documentation

Conceptual notes under [docs/](docs/):

- [docs/evaluation.md](docs/evaluation.md) — how evaluation datasets, evaluator families (deterministic, LLM-as-judge, custom rubric), baselines, and regression comparisons work; also covers cloud evaluation from Python and the Agent Optimizer.
- [docs/monitoring.md](docs/monitoring.md) — operational vs. AI-quality health, traces, continuous vs. scheduled evaluation, alerts, and red-team monitoring.
- [docs/automation.md](docs/automation.md) — scheduled regression, the CI/CD gate, GitHub Actions mental model, OIDC federated identity, and quality gates.

## Future work

Small, obvious next steps already implied by the repo and docs:

- Enable the push/PR triggers in the workflows once the gate is trusted.
- Grow the regression dataset from production traces (see [docs/monitoring.md](docs/monitoring.md)).
- Explore the **Agent Optimizer** loop described in [docs/evaluation.md](docs/evaluation.md).
