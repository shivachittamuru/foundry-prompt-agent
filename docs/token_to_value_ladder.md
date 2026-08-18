# Token-to-Value Ladder

This document explains the **general tokenomics framework** used in this project: how to move from raw token usage to business value.

It is intentionally different from [`business_case_and_economics.md`](business_case_and_economics.md):

- **This document** explains the reusable measurement ladder and how the repository implements it.
- **The business-case document** applies that ladder to the Contoso Coffee demand-recovery scenario.

The two documents therefore complement each other:

```text
Token-to-Value Ladder
        ↓
general measurement framework
        ↓
Business Case & Economics
        ↓
scenario-specific application
```

The central lesson is:

> **The goal is not to minimize token consumption. The goal is to maximize economically valuable outcomes per dollar of AI inference while preserving quality.**

---

## The Ladder

```text
Step 6: Economic Value
        Is the AI economically worth operating?
        Recovered contribution ÷ AI inference cost
        Break-even conversion
        Sensitivity / scenario resilience

Step 5: Business Economics
        What is a successful interaction worth?
        Successful interactions
        → expected orders
        → revenue
        → contribution

Step 4: Token Effectiveness
        What does one successful outcome cost?
        Cost per successful resolution

Step 3: Token Efficiency
        What does one interaction cost?
        Tokens per interaction
        Cost per interaction

Step 2: Token Cost
        What did the consumed tokens cost?

Step 1: Token Spend
        How many tokens did we use?
```

Each rung depends on the one below it.

At the bottom, we know what the AI consumed.

At the top, we can answer:

> **Was that spend economically worthwhile?**

---

# Step 1 — Token Spend

## Question

> How many tokens did the agent use?

The agent client captures token usage returned by the Responses API:

```python
usage = {
    "model": response.model,
    "input_tokens": response.usage.input_tokens,
    "output_tokens": response.usage.output_tokens,
    "total_tokens": response.usage.total_tokens,
    "cached_tokens": response.usage.input_tokens_details.cached_tokens,
    "reasoning_tokens": response.usage.output_tokens_details.reasoning_tokens,
}
```

Important details:

- input and output tokens are tracked separately,
- cached input is captured because it may be priced differently,
- reasoning tokens are kept for visibility,
- the actual model returned by the API is recorded.

Without this rung, every later economics calculation is guesswork.

---

# Step 2 — Token Cost

## Question

> What did those tokens cost?

Token counts become dollar cost using model pricing.

Conceptually:

```text
Fresh input tokens
× input price

+

Cached input tokens
× cached-input price

+

Output tokens
× output price

=

AI inference cost
```

The repository keeps pricing logic in `src/foundry_prompt_agent/tokenomics.py`.

This layer should remain independent of the business scenario.

The result is:

```text
total AI cost
```

for an evaluation run.

---

# Step 3 — Token Efficiency

## Question

> How expensive is one interaction?

Raw totals are difficult to compare because evaluation runs can contain different numbers of cases.

Efficiency normalizes by task count:

```text
tokens per interaction
=
total tokens / tasks
```

and:

```text
cost per interaction
=
total AI cost / tasks
```

This produces metrics such as:

```text
Tokens / interaction
Input tokens / interaction
Output tokens / interaction
Cost / interaction
```

These are useful when comparing:

- prompt versions,
- agent versions,
- models,
- retrieval strategies,
- context sizes.

But efficiency is deliberately **quality-blind**.

A cheap wrong answer is still cheap at this rung.

That is why the ladder continues.

---

# Step 4 — Token Effectiveness

## Question

> What does one successful outcome cost?

The Foundry behavior evaluator provides the success signal.

If:

```text
Cost / interaction = $0.01
Success rate = 50%
```

then:

```text
Cost / successful resolution
=
$0.01 / 50%
=
$0.02
```

The repository calculates:

```text
tokens per success
cost per success
```

using:

```text
cost per success
=
cost per interaction / success rate
```

This is a critical step because failures still consume tokens.

The business pays for both:

```text
successful interactions
+
failed interactions
```

so the honest question is:

> How much total AI spend was required to produce one acceptable outcome?

This is where evaluation becomes part of tokenomics.

---

# Step 5 — Business Economics

## Question

> What is one successful interaction economically worth?

An early version of this framework assigned a flat value to a successful task, such as `$0.10`. That is easy to explain but too abstract to defend as a business case, so the implemented model derives value from an explicit demand-recovery funnel instead.

For Contoso Coffee:

```text
Missed customer contacts
        ↓
AI-addressable contacts
        ↓
measured agent success rate
        ↓
successfully served interactions
        ↓
assumed conversion rate
        ↓
estimated recovered orders
        ↓
average order value
        ↓
recovered revenue
        ↓
contribution margin
        ↓
recovered contribution
```

The reusable formula for expected contribution from one successful interaction is:

```text
Expected contribution / successful interaction
=
conversion rate
× average order value
× contribution margin
```

Example:

```text
30% conversion
× $10 average order
× 35% contribution margin
=
$1.05 expected contribution per successful interaction
```

This is much more explainable than assigning an arbitrary value to a successful task.

---

# Step 6 — Economic Value

## Question

> Is the AI economically worth operating?

The primary metric for this project is:

## AI Value Multiple

```text
AI Value Multiple
=
Recovered Contribution
÷
AI Inference Cost
```

For example:

```text
Recovered contribution / month    $1,795
AI inference cost / month            $216
-----------------------------------------
AI Value Multiple                    8.3x
```

Interpretation:

> Under the stated business assumptions, every $1 of AI inference supports approximately $8.30 of recovered contribution opportunity.

This is the top of the ladder because it connects:

```text
tokens
+
quality
+
business outcomes
```

into one economic decision.

---

# Break-Even Economics

A large value multiple is useful, but a more robust question is:

> **How low can conversion fall before AI stops paying for itself?**

The model therefore calculates:

```text
Break-even conversion rate
=
AI inference cost
÷
(successful contacts
 × average order value
 × contribution margin)
```

This helps avoid relying on a single optimistic business assumption.

Instead of saying:

> "We believe conversion will be 30%."

the analysis can say:

> "Here is the minimum conversion rate required for modeled recovered contribution to cover inference cost."

---

# Sensitivity Analysis

Business assumptions are uncertain.

Therefore economics should be explored across scenarios rather than represented as one fixed ROI number.

Examples:

```text
Conversion rate:
5%
10%
20%
30%
```

or:

```text
AI inference cost:
measured
5x measured
10x measured
20x measured
```

The measured AI performance remains fixed while business assumptions are changed locally.

```text
Measured
────────
success rate
tokens / interaction
cost / interaction

        +

Scenario assumptions
────────────────────
missed contacts
AI eligibility
conversion
AOV
contribution margin
cost stress

        ↓

Economic model
```

No new model call is required simply to explore business assumptions.

---

# Measured vs. Assumed vs. Proven

This distinction is essential.

| Measured by the system | Assumed in the model | Validate in a real pilot |
|---|---|---|
| Token usage | Missed contacts/day | Actual missed demand |
| AI inference cost | AI-eligible rate | Incremental orders |
| Evaluation success rate | Conversion rate | Actual conversion lift |
| Cost per successful resolution | Average order value | Actual AOV |
| Scope/quality metrics | Contribution margin | Actual contribution lift |

The repository can prove the first column.

It can transparently model the second.

Only a production experiment can prove the third.

---

# Why Cheapness Is Not the Goal

Suppose two configurations produce:

| Metric | Agent A | Agent B |
|---|---:|---:|
| Tokens / interaction | 3,000 | 1,800 |
| Cost / interaction | $0.020 | $0.012 |
| Success rate | 94% | 82% |

A token-consumption view says:

> Agent B is cheaper.

But token effectiveness asks:

```text
What does each successful resolution cost?
```

and business economics asks:

```text
How much recovered contribution does each configuration support?
```

A more expensive configuration can be economically superior if its higher quality produces more valuable outcomes.

Therefore:

> **Optimize economic value per inference dollar, not token consumption.**

---

# How the Ladder Maps to the Repository

| Rung | Primary question | Main implementation |
|---|---|---|
| Token Spend | How many tokens? | `src/foundry_prompt_agent/agent.py` |
| Token Cost | What did they cost? | `src/foundry_prompt_agent/tokenomics.py` |
| Token Efficiency | Cost per interaction? | `src/foundry_prompt_agent/tokenomics.py` |
| Token Effectiveness | Cost per successful resolution? | `src/foundry_prompt_agent/tokenomics.py` + Foundry evaluation |
| Business Economics | What could successful interactions be worth? | `src/foundry_prompt_agent/business_economics.py` |
| Economic Value | Is recovered contribution worth the inference spend? | `src/foundry_prompt_agent/business_economics.py` + `apps/dashboard.py` / `scripts/generate_economics_report.py` |

Two supporting modules keep the rungs separable: `src/foundry_prompt_agent/foundry_eval.py` holds the Foundry evaluation calls and the CI quality gate, and `src/foundry_prompt_agent/history.py` reads and appends the experiment ledger.

The orchestration lives in:

```text
scripts/run_evaluation.py
```

It connects:

```text
agent execution
      ↓
token measurements
      ↓
Foundry quality evaluation
      ↓
technical tokenomics
      ↓
business economics
      ↓
history
```

---

# Run History as an Experiment Ledger

`evals/tokenomics_history.jsonl` should be treated as an experiment ledger.

Each current-style record should preserve three categories.

## Measured AI data

```text
run id
timestamp
tasks
tokens / interaction
cost / interaction
success rate
cost / successful resolution
```

## Business assumptions

```text
missed contacts/day
AI-eligible rate
conversion rate
average order value
contribution margin
days/month
```

## Modeled outcomes

```text
recovered orders
recovered revenue
recovered contribution
AI inference cost
AI Value Multiple
break-even conversion
```

This allows later comparisons to answer:

> Did economics change because the agent changed, or because the assumptions changed?

---

# Visualization

Three views make the ladder legible. `scripts/plot_tokenomics.py` and `scripts/generate_economics_report.py` render static versions from the ledger; `apps/dashboard.py` provides the interactive version.

## Run comparison

Track:

```text
success rate
cost / interaction
cost / success
AI Value Multiple
```

This is useful for comparing genuine prompt/model/agent changes.

## Contribution vs. AI cost

```text
Recovered contribution
        vs.
AI inference cost
```

This visually communicates the business asymmetry.

## Conversion sensitivity

```text
AI Value Multiple
        ↑
        │
        │
        └────────────→ conversion rate
```

This shows whether the economics survive more conservative assumptions.

The Streamlit dashboard provides an interactive version of these analyses.

---

# Why the Top Rung Is Not a Full Margin Model

A fully loaded view of AI economics would subtract every operating cost:

```text
Recovered contribution
- inference cost
- human review cost
- operational cost
- failure/risk cost
=
fully loaded AI contribution
```

That model is the right destination for a real production deployment, and an
earlier version of this project implemented it. It was removed because the
review and failure-cost inputs were invented rather than observed, which made
the headline number less trustworthy than the simpler ratio.

The implemented top rung is therefore:

```text
Recovered Contribution
÷
AI Inference Cost
=
AI Value Multiple
```

Inference cost is measured, and every other input is a stated assumption that
can be stress-tested. The ladder has not abandoned margin; it has made the top
rung evidence-driven, and the fully loaded model can return once review,
operational, and failure costs come from a real pilot.

---

# The Complete Mental Model

```text
TOKENS
  ↓
What did we consume?

COST
  ↓
What did inference cost?

EFFICIENCY
  ↓
What did one interaction cost?

EFFECTIVENESS
  ↓
What did one successful outcome cost?

BUSINESS ECONOMICS
  ↓
What might one successful outcome be worth?

ECONOMIC VALUE
  ↓
How much recovered contribution
do we get per dollar of inference?
```

That is the path from:

> **token visibility**

to:

> **token accountability**

---

# Final Takeaway

Token optimization alone asks:

> Can we use fewer tokens?

Token economics asks:

> Can we create more valuable outcomes per inference dollar?

The second question is the one the business ultimately cares about.

The ladder therefore evolves from:

```text
Token Spend
→ Token Cost
→ Token Efficiency
→ Token Effectiveness
→ Business Economics
→ Economic Value
```

The Contoso Coffee business case is one concrete application of that reusable framework.

For the scenario-specific economics, assumptions, sensitivity analysis, and demo story, see:

[`business_case_and_economics.md`](business_case_and_economics.md)
