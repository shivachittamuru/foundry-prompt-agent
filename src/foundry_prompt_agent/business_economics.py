"""Business economics for the Contoso Coffee tokenomics demo.

This module keeps business assumptions separate from the generic technical
token/evaluation metrics in ``tokenomics.py``.

Measured inputs such as ``success_rate`` and ``cost_per_task_usd`` should come
from actual agent/evaluation runs. Business inputs such as missed contacts,
conversion rate, average order value, and contribution margin are assumptions.
"""

from __future__ import annotations
from pathlib import Path

import yaml


def load_business_assumptions(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config["business"]


def summarize_business_economics(
    *,
    missed_contacts_per_day: float,
    ai_eligible_rate: float,
    success_rate: float,
    conversion_rate: float,
    average_order_value_usd: float,
    contribution_margin: float,
    cost_per_task_usd: float,
    days_per_month: int = 30,
) -> dict:
    """Estimate demand recovery and AI economics for the coffee-shop scenario."""

    _validate_rate("ai_eligible_rate", ai_eligible_rate)
    _validate_rate("success_rate", success_rate)
    _validate_rate("conversion_rate", conversion_rate)
    _validate_rate("contribution_margin", contribution_margin)

    if missed_contacts_per_day < 0:
        raise ValueError("missed_contacts_per_day must be >= 0")
    if average_order_value_usd < 0:
        raise ValueError("average_order_value_usd must be >= 0")
    if cost_per_task_usd < 0:
        raise ValueError("cost_per_task_usd must be >= 0")
    if days_per_month <= 0:
        raise ValueError("days_per_month must be > 0")

    # 1. Demand funnel.
    addressable_contacts_per_day = missed_contacts_per_day * ai_eligible_rate
    successful_contacts_per_day = addressable_contacts_per_day * success_rate
    recovered_orders_per_day = successful_contacts_per_day * conversion_rate

    # 2. Business value.
    recovered_revenue_per_day = (
        recovered_orders_per_day * average_order_value_usd
    )
    recovered_contribution_per_day = (
        recovered_revenue_per_day * contribution_margin
    )

    # 3. Monthly projection.
    addressable_contacts_per_month = (
        addressable_contacts_per_day * days_per_month
    )
    successful_contacts_per_month = (
        successful_contacts_per_day * days_per_month
    )
    recovered_orders_per_month = recovered_orders_per_day * days_per_month
    recovered_revenue_per_month = recovered_revenue_per_day * days_per_month
    recovered_contribution_per_month = (
        recovered_contribution_per_day * days_per_month
    )

    # 4. AI cost. We pay for every AI-addressable interaction, not just
    # successful ones.
    ai_inference_cost_per_month = (
        addressable_contacts_per_month * cost_per_task_usd
    )

    # 5. Primary tokenomics metric.
    ai_value_multiple = (
        recovered_contribution_per_month / ai_inference_cost_per_month
        if ai_inference_cost_per_month > 0
        else float("inf")
    )

    # 6. Expected contribution from one successful interaction.
    expected_contribution_per_success_usd = (
        conversion_rate
        * average_order_value_usd
        * contribution_margin
    )

    # 7. Minimum conversion required for contribution to cover inference cost.
    break_even_denominator = (
        successful_contacts_per_month
        * average_order_value_usd
        * contribution_margin
    )
    break_even_conversion_rate = (
        ai_inference_cost_per_month / break_even_denominator
        if break_even_denominator > 0
        else float("inf")
    )

    return {
        "missed_contacts_per_day": missed_contacts_per_day,
        "addressable_contacts_per_day": addressable_contacts_per_day,
        "successful_contacts_per_day": successful_contacts_per_day,
        "recovered_orders_per_day": recovered_orders_per_day,
        "addressable_contacts_per_month": addressable_contacts_per_month,
        "successful_contacts_per_month": successful_contacts_per_month,
        "recovered_orders_per_month": recovered_orders_per_month,
        "recovered_revenue_per_month": recovered_revenue_per_month,
        "recovered_contribution_per_month": recovered_contribution_per_month,
        "ai_inference_cost_per_month": ai_inference_cost_per_month,
        "expected_contribution_per_success_usd": (
            expected_contribution_per_success_usd
        ),
        "ai_value_multiple": ai_value_multiple,
        "break_even_conversion_rate": break_even_conversion_rate,
    }


def _validate_rate(name: str, value: float) -> None:
    """Validate a decimal rate such as 0.60 or 0.35."""
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    
    
if __name__ == "__main__":
    assumptions = load_business_assumptions(
        Path("economics/business_assumptions.yaml")
    )
    print(assumptions)
    
    success_rate = 0.95
    cost_per_task_usd = 0.012
    
    summary = summarize_business_economics(
        missed_contacts_per_day=assumptions["missed_contacts_per_day"],
        ai_eligible_rate=assumptions["ai_eligible_rate"],
        success_rate=success_rate,
        conversion_rate=assumptions["conversion_rate"],
        average_order_value_usd=assumptions["average_order_value_usd"],
        contribution_margin=assumptions["contribution_margin"],
        cost_per_task_usd=cost_per_task_usd,
        days_per_month=assumptions["days_per_month"],
    )

    print(summary)
    
    
    

# uv run src/foundry_prompt_agent/business_economics.py