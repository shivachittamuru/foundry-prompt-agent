PRICING = {
    # USD per 1M tokens, as of 2026-08-14. Update when model pricing changes.
    "gpt-5": {"input": 1.25, "cached": 0.125, "output": 10.00},
}

# Step 2: Token Cost
def compute_cost(usage: dict) -> float:
    rates = PRICING[usage["model"]]  # KeyError here is a feature: unknown model = unpriced spend
    billed_input = usage["input_tokens"] - usage["cached_tokens"]
    return (
        billed_input / 1_000_000 * rates["input"]
        + usage["cached_tokens"] / 1_000_000 * rates["cached"]
        + usage["output_tokens"] / 1_000_000 * rates["output"]
    )

# Step 3: Token Efficiency
def summarize_efficiency(usages: list[dict]) -> dict:
    tasks = len(usages)
    if tasks == 0:
        return {
            "tasks": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "tokens_per_task": 0.0,
            "input_tokens_per_task": 0.0,
            "output_tokens_per_task": 0.0,
            "cost_per_task": 0.0,
        }

    total_tokens = sum(u["total_tokens"] for u in usages)
    total_input = sum(u["input_tokens"] for u in usages)
    total_output = sum(u["output_tokens"] for u in usages)
    total_cost = sum(compute_cost(u) for u in usages)

    return {
        "tasks": tasks,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "tokens_per_task": total_tokens / tasks,
        "input_tokens_per_task": total_input / tasks,
        "output_tokens_per_task": total_output / tasks,
        "cost_per_task": total_cost / tasks,
    }


def summarize_effectiveness(efficiency: dict, success_rate: float) -> dict:
    if success_rate <= 0:
        return {
            "success_rate": success_rate,
            "successful_tasks": 0.0,
            "tokens_per_success": float("inf"),
            "cost_per_success": float("inf"),
        }

    return {
        "success_rate": success_rate,
        "successful_tasks": success_rate * efficiency["tasks"],
        "tokens_per_success": efficiency["tokens_per_task"] / success_rate,
        "cost_per_success": efficiency["cost_per_task"] / success_rate,
    }


# Step 5: Token Economics
def summarize_economics(
    efficiency: dict,
    effectiveness: dict,
    value_per_success: float,
) -> dict:
    total_value = value_per_success * effectiveness["successful_tasks"]
    total_cost = efficiency["total_cost"]
    value_per_dollar = total_value / total_cost if total_cost > 0 else float("inf")

    return {
        "value_per_success": value_per_success,
        "total_value": total_value,
        "total_cost": total_cost,
        "value_per_dollar": value_per_dollar,
    }


# Step 6: Token Margin
def summarize_margin(
    efficiency: dict,
    effectiveness: dict,
    economics: dict,
    review_cost_per_task: float,
    error_cost_per_failure: float,
    judge_cost_per_run: float = 0.0,
) -> dict:
    tasks = efficiency["tasks"]
    failed_tasks = tasks - effectiveness["successful_tasks"]

    value = economics["total_value"]
    ai_runtime_cost = economics["total_cost"] + judge_cost_per_run
    human_review_cost = review_cost_per_task * tasks
    error_risk_cost = error_cost_per_failure * failed_tasks

    margin = value - ai_runtime_cost - human_review_cost - error_risk_cost

    return {
        "value": value,
        "ai_runtime_cost": ai_runtime_cost,
        "human_review_cost": human_review_cost,
        "error_risk_cost": error_risk_cost,
        "margin": margin,
        "profitable": margin > 0,
    }


def ladder_record(
    efficiency: dict,
    effectiveness: dict,
    economics: dict,
    margin: dict,
) -> dict:
    return {
        "tasks": efficiency["tasks"],
        "total_tokens": efficiency["total_tokens"],
        "total_cost": efficiency["total_cost"],
        "tokens_per_task": efficiency["tokens_per_task"],
        "cost_per_task": efficiency["cost_per_task"],
        "success_rate": effectiveness["success_rate"],
        "successful_tasks": effectiveness["successful_tasks"],
        "cost_per_success": effectiveness["cost_per_success"],
        "value_per_dollar": economics["value_per_dollar"],
        "margin": margin["margin"],
        "profitable": margin["profitable"],
    }





