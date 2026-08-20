# Contoso Coffee AI Agent — Tokenomics Business Case & Economics

## Executive Summary

This project asks a practical business question:

> **Can AI economically recover customer demand that a local coffee shop is currently unable to serve?**

The scenario is simple:

```text
Customer has a menu question
        ↓
Staff is busy or unavailable
        ↓
Inquiry goes unanswered
        ↓
Customer gives up
        ↓
Potential demand is lost
```

The Contoso Coffee agent answers menu-related questions using Microsoft Foundry and Azure AI Search. The project does not need a real ordering system to demonstrate the economics. Instead, it measures agent quality and inference cost, then models how successfully served interactions could translate into recovered orders and contribution.

The central thesis is:

> **The goal is not to minimize token consumption. The goal is to maximize economically valuable outcomes per dollar of AI inference while preserving quality.**

The full flow is:

```text
Unserved demand
      ↓
AI-addressable demand
      ↓
Measured agent quality
      ↓
Successfully served interactions
      ↓
Estimated conversion
      ↓
Recovered contribution
      ↓
AI inference cost
      ↓
AI Value Multiple
```

---

## 1. Business Problem — Recovering Unserved Demand

Coffee shops receive repetitive questions such as:

- What drinks are available?
- How much is a latte?
- What can I get for under $5?
- Do you have anything caffeine-free?
- Do you carry a specific menu item?

During peak periods, some inquiries may go unanswered.

The business question becomes:

> **How much otherwise-lost demand can AI safely recover, and how much contribution can that recovered demand create relative to AI inference cost?**

### Current agent scope

```text
Customer question
      ↓
Microsoft Foundry Prompt Agent
      ↓
Azure AI Search
      ↓
Grounded menu information
      ↓
Response
```

The current agent supports item/price lookup, filtering, budget math, semantic recommendations, abstention, hallucination resistance, and scope adherence.

A real order-processing system is intentionally out of scope. For this tokenomics model, estimated recovered orders from agent interactions is enough to model economic value as orders generate revenue.

---

## 2. From Tokens to Business Outcomes

Tokens are the atomic units of AI consumption; outcomes are the economic units of value.

Token metrics alone stop too early:

```text
Input tokens
Output tokens
Total tokens
Inference cost
```

The business cares about what those tokens produce:

```text
Tokens
   ↓
AI Cost
   ↓
Successful Interaction
   ↓
Recovered Order Opportunity
   ↓
Recovered Contribution
```

So the better question is not:

> How many tokens did we consume?

It is:

> **How much economically valuable demand did those tokens help recover?**

The reusable measurement framework behind this progression is documented in [`token_to_value_ladder.md`](token_to_value_ladder.md).

---

## 3. The Economics Model

The model deliberately separates **measured AI performance** from **business assumptions**.

### Business assumptions or inputs

- missed contacts/day,
- AI-eligible rate,
- conversion rate,
- average order value,
- contribution margin.

### Measured by the system

- token usage,
- inference cost,
- behavior success rate,
- cost per successful resolution.

These combine as:

```text
Missed interactions
      ↓ × AI-eligible rate
AI-Addressable interactions
      ↓ × measured success rate
Successfully served interactions
      ↓ × conversion rate
Recovered orders
      ↓ × average order value
Recovered revenue
      ↓ × contribution margin
Recovered contribution
```

The key boundary is:

> **AI performance is measured. Business outcomes are modeled from transparent assumptions.**

Only a real pilot can validate actual conversion and contribution lift.

---

## 4. Illustrative Coffee-Shop Economics

The assumptions below are the ones shipped in [`economics/business_assumptions.yaml`](../economics/business_assumptions.yaml), combined with a success rate and inference cost of the kind an evaluation run actually produces:

```text
Missed customer contacts/day          100
AI-eligible contacts                   60%
Successful-resolution rate             90%   (measured)
Conversion after successful answer     30%
Average order value                    $10
Contribution margin                    35%
Days/month                              30
Cost per interaction               $0.0074   (measured)
```

The business inputs are illustrative assumptions, not claims about a real shop. The two marked *measured* come from the evaluation run and change with every agent version.

### Demand funnel

```text
100 missed contacts
× 60% AI eligible
=
60 addressable contacts/day

60
× 90% measured success
=
54 successfully served/day

54
× 30% conversion
=
16.2 recovered orders/day
```

### Economics

```text
16.2 orders
× $10 AOV
=
$162.00 recovered revenue/day

$162.00
× 35% contribution margin
=
$56.70 recovered contribution/day

$56.70
× 30 days
=
$1,701 recovered contribution/month
```

Now compare that contribution with AI inference cost.

---

## 5. Primary Metric — AI Value Multiple

```text
AI Value Multiple
=
Recovered Contribution
÷
AI Inference Cost
```

The business pays for every AI-addressable interaction, not only the successful ones:

```text
60 addressable/day × 30 days × $0.0074
=
$13.36 AI inference cost/month
```

So:

```text
Recovered contribution/month       $1,701
AI inference cost/month               $13
------------------------------------------
AI Value Multiple                   ~127x
```

Interpretation:

> Under the stated assumptions, every $1 of AI inference supports roughly $127 of modeled recovered contribution opportunity.

This is **not** a claim of proven production ROI. It is a transparent economic model that can be inspected and stress-tested. `scripts/generate_economics_report.py` regenerates these figures from the latest recorded run, so the exact numbers move as the agent changes.

### Break-even conversion

A second useful metric is:

> **How low can conversion fall before modeled recovered contribution no longer covers inference cost?**

Conceptually:

```text
Break-even conversion rate
=
AI inference cost
÷
(successfully served interactions
 × average order value
 × contribution margin)
```

For the run above that threshold is roughly **0.24%** — far below the 30% assumption, which is the real point of the metric. It is usually more useful than defending one optimistic conversion number.

---

## 6. Why Quality Belongs in Tokenomics

A cheap agent is not automatically an economically good agent.

| Metric | Agent A | Agent B |
|---|---:|---:|
| Average tokens/request | 3,000 | 1,800 |
| Cost/request | $0.020 | $0.012 |
| Quality | 94% | 82% |
| Resolution rate | 90% | 72% |

A token-consumption view says Agent B is cheaper.

But suppose:

```text
Agent A
Recovered contribution = $2,300
AI cost                = $30

Agent B
Recovered contribution = $1,600
AI cost                = $18
```

Agent B consumes fewer tokens, but Agent A creates more modeled business value.

Therefore:

> **Optimize economic value per inference dollar, not token consumption.**

The relevant optimization target is:

```text
quality
+
successful outcomes
+
efficient inference
=
stronger economics
```

Useful metrics therefore progress from:

```text
Cost per token
      ↓
Cost per interaction
      ↓
Cost per successful resolution
      ↓
Recovered contribution
      ↓
Contribution per AI dollar
```

---

## 7. Sensitivity, Evidence Boundaries, and the Dashboard

Business assumptions are uncertain, so the economics should not depend on one scenario.

The current implementation allows scenario analysis across:

- missed contacts/day,
- AI-eligible rate,
- conversion rate,
- average order value,
- contribution margin,
- AI inference cost.

It also supports inference-cost stress testing such as:

```text
Measured cost
1x
5x
10x
20x
```

This helps answer:

> What if customer conversion is much lower than expected?

and:

> What if production inference cost is much higher than the current benchmark?

### Measured vs. assumed vs. proven

| Measured by the system | Assumed in the model | Validate in a real pilot |
|---|---|---|
| Tokens | Missed contacts/day | Actual missed demand |
| AI cost | AI-eligible rate | Incremental orders |
| Behavior success rate | Conversion rate | Actual conversion lift |
| Cost per successful resolution | Average order value | Actual AOV |
| Quality/scope metrics | Contribution margin | Actual contribution lift |

The project can measure the first column, transparently model the second, and only a production pilot can establish the third.

### Current implementation flow

```text
scripts/run_evaluation.py
      ↓
Measures quality + token cost
      ↓
evals/tokenomics_history.jsonl
      ↓
src/foundry_prompt_agent/business_economics.py
      ↓
Combines measurements with assumptions
      ↓
scripts/generate_economics_report.py + apps/dashboard.py
```

`evals/tokenomics_history.jsonl` is the experiment ledger. Every run appends measured AI metrics, the assumptions used, and the modeled economics, so a later comparison can tell whether the economics moved because the agent changed or because the assumptions did.

The Streamlit dashboard keeps measured AI metrics fixed while allowing business assumptions to change interactively. It includes:

- Conservative / Base / Optimistic presets,
- conversion sensitivity,
- AI cost stress testing,
- contribution-vs-AI-cost visualization,
- historical Agent / Run comparison under the same business assumptions.

Scenario exploration does **not** call the model again.

---

## 8. Demo Story and Decision Questions

### Act 1 — Show the lost-demand problem

```text
Customer inquiry
      ↓
No response
      ↓
Potential demand lost
```

### Act 2 — Show that the agent is measured

Demonstrate representative menu questions, then show:

```text
Foundry evaluation
      ↓
behavior quality
      ↓
token usage
      ↓
cost per successful resolution
```

### Act 3 — Show the economics

```text
Missed demand
      ↓
AI-addressable demand
      ↓
measured agent quality
      ↓
recovered orders
      ↓
recovered contribution
      ↓
AI Value Multiple
```

Then stress the assumptions live:

```text
Conversion 20% → 5%
AI cost 1x → 10x
```

This turns tokenomics into a **decision model**, not a billing dashboard.

The recurring questions are:

- How much demand currently goes unserved?
- What share is suitable for AI?
- What percentage of AI interactions meet the quality bar?
- What does one successful resolution cost?
- What contribution could recovered demand create?
- What conversion rate is required to break even?
- Does a cheaper model actually produce better economics?
- Are additional tokens buying enough quality to justify their cost?

---

## Final Business Thesis

The core business question is:

> **Can AI economically recover demand that the business is currently unable to serve?**

The core tokenomics question is:

> **How much high-quality economic value can we create for every dollar of AI inference?**

And the project tells one continuous story:

```text
Unserved demand
      ↓
AI interaction
      ↓
Measured quality
      ↓
Measured inference cost
      ↓
Modeled recovered contribution
      ↓
AI Value Multiple
      ↓
Business decision
```

That is the intended scope of this project: **connect agent quality to business outcomes, and quantify those outcomes against token spend.**
