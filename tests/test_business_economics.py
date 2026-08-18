import pytest

from foundry_prompt_agent.business_economics import (
    conversion_sensitivity,
    scenario_from_measured_run,
    summarize_business_economics,
)

ASSUMPTIONS = {
    "missed_contacts_per_day": 100,
    "ai_eligible_rate": 0.60,
    "conversion_rate": 0.20,
    "average_order_value_usd": 10.00,
    "contribution_margin": 0.50,
    "days_per_month": 30,
}

MEASURED = {
    "success_rate": 0.50,
    "cost_per_task": 0.01,
}


def summarize(**overrides) -> dict:
    kwargs = {
        **ASSUMPTIONS,
        "success_rate": MEASURED["success_rate"],
        "cost_per_task_usd": MEASURED["cost_per_task"],
    }
    kwargs.update(overrides)
    return summarize_business_economics(**kwargs)


def test_demand_funnel_arithmetic():
    result = summarize()

    assert result["addressable_contacts_per_day"] == pytest.approx(60)
    assert result["successful_contacts_per_day"] == pytest.approx(30)
    assert result["recovered_orders_per_day"] == pytest.approx(6)
    assert result["recovered_orders_per_month"] == pytest.approx(180)
    assert result["recovered_revenue_per_month"] == pytest.approx(1_800)
    assert result["recovered_contribution_per_month"] == pytest.approx(900)


def test_ai_inference_cost_covers_every_addressable_contact():
    result = summarize()

    # 60 addressable/day * 30 days * $0.01, not just the successful ones.
    assert result["addressable_contacts_per_month"] == pytest.approx(1_800)
    assert result["ai_inference_cost_per_month"] == pytest.approx(18)


def test_ai_value_multiple_is_contribution_over_inference_cost():
    result = summarize()

    assert result["ai_value_multiple"] == pytest.approx(900 / 18)


def test_break_even_conversion_rate():
    result = summarize()

    # 18 / (900 successful contacts * $10 * 0.50 margin)
    assert result["break_even_conversion_rate"] == pytest.approx(0.004)


def test_expected_contribution_per_success():
    result = summarize()

    assert result["expected_contribution_per_success_usd"] == pytest.approx(
        1.0
    )


def test_zero_inference_cost_gives_infinite_value_multiple():
    result = summarize(cost_per_task_usd=0.0)

    assert result["ai_inference_cost_per_month"] == 0.0
    assert result["ai_value_multiple"] == float("inf")
    assert result["break_even_conversion_rate"] == pytest.approx(0.0)


def test_zero_success_rate_gives_infinite_break_even():
    result = summarize(success_rate=0.0)

    assert result["successful_contacts_per_month"] == 0
    assert result["break_even_conversion_rate"] == float("inf")


@pytest.mark.parametrize(
    "field",
    [
        "ai_eligible_rate",
        "success_rate",
        "conversion_rate",
        "contribution_margin",
    ],
)
def test_rates_outside_zero_to_one_are_rejected(field):
    with pytest.raises(ValueError, match=field):
        summarize(**{field: 1.5})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("missed_contacts_per_day", -1),
        ("average_order_value_usd", -1),
        ("cost_per_task_usd", -1),
        ("days_per_month", 0),
    ],
)
def test_invalid_magnitudes_are_rejected(field, value):
    with pytest.raises(ValueError):
        summarize(**{field: value})


def test_scenario_from_measured_run_matches_direct_call():
    scenario = scenario_from_measured_run(MEASURED, ASSUMPTIONS)

    assert scenario == summarize()


def test_cost_stress_multiplier_scales_inference_cost_only():
    baseline = scenario_from_measured_run(MEASURED, ASSUMPTIONS)
    stressed = scenario_from_measured_run(
        MEASURED,
        ASSUMPTIONS,
        cost_stress_multiplier=10.0,
    )

    assert stressed["ai_inference_cost_per_month"] == pytest.approx(
        baseline["ai_inference_cost_per_month"] * 10
    )
    assert stressed["recovered_contribution_per_month"] == pytest.approx(
        baseline["recovered_contribution_per_month"]
    )
    assert stressed["ai_value_multiple"] == pytest.approx(
        baseline["ai_value_multiple"] / 10
    )


def test_conversion_sensitivity_varies_only_conversion():
    scenarios = conversion_sensitivity(
        MEASURED,
        ASSUMPTIONS,
        [0.10, 0.20],
    )

    assert [scenario["conversion_rate"] for scenario in scenarios] == [
        0.10,
        0.20,
    ]

    # Inference cost is independent of conversion; contribution is not.
    assert scenarios[0]["ai_inference_cost_per_month"] == pytest.approx(
        scenarios[1]["ai_inference_cost_per_month"]
    )
    assert scenarios[1]["recovered_contribution_per_month"] == pytest.approx(
        scenarios[0]["recovered_contribution_per_month"] * 2
    )
