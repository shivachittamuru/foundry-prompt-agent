PRICING = {
    # USD per 1M tokens, as of 2026-08-14. Update when model pricing changes.
    "gpt-5": {"input": 1.25, "cached": 0.125, "output": 10.00},
}


def compute_cost(usage: dict) -> float:
    rates = PRICING[usage["model"]]  # KeyError here is a feature: unknown model = unpriced spend
    billed_input = usage["input_tokens"] - usage["cached_tokens"]
    return (
        billed_input / 1_000_000 * rates["input"]
        + usage["cached_tokens"] / 1_000_000 * rates["cached"]
        + usage["output_tokens"] / 1_000_000 * rates["output"]
    )
