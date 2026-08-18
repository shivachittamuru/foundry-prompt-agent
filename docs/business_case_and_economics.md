# Contoso Coffee AI Agent — Tokenomics Business Case & Economics Report

## Executive Summary

This project asks a practical business question:

> **Can AI economically recover customer demand that a local coffee shop or restaurant is currently unable to serve?**

The baseline is not necessarily:

```text
Human does the job for $X/hour
vs.
AI does the job for $Y/hour
```

For a busy local business, the real baseline may be:

```text
Phone rings
   ↓
Staff is busy
   ↓
Nobody answers
   ↓
Customer gives up
   ↓
Revenue disappears
```

This makes the project a **demand-recovery story**, not primarily a labor-replacement story.

The current Contoso Coffee agent answers menu questions using Microsoft Foundry and Azure AI Search. That is enough to demonstrate tokenomics; a real ordering system is intentionally out of scope.

The central thesis is:

> **The goal is not to minimize token consumption. The goal is to maximize economically valuable outcomes per dollar of AI inference while preserving quality.**

---

## 1. Business Problem

Coffee shops and restaurants receive repetitive questions such as:

- What drinks are available?
- How much is a latte?
- What can I get for under $5?
- Do you have anything caffeine-free?
- Do you carry a specific menu item?

During peak periods, some inquiries go unanswered.

```text
Customer demand
      ↓
No response
      ↓
Abandoned interaction
      ↓
Potential order lost
      ↓
$0 realized value
```

The business question becomes:

> **How much otherwise-lost demand can AI safely recover, and how much contribution does that recovered demand create relative to the cost of AI?**

---

## 2. Current Agent Scope

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

The agent already demonstrates:

- item and price lookup,
- budget filtering,
- recommendations,
- abstention when information is unavailable,
- hallucination resistance,
- scope adherence.

A real ordering system is **not required** to prove the economics. The model can instead represent:

```text
Successful interaction
      ↓
Probability customer proceeds to order
      ↓
Estimated recovered demand
```

This keeps the project focused on token economics rather than payments, POS integration, inventory, or fulfillment.

---

## 3. From Token Cost to Business Value

A basic AI dashboard reports:

```text
Input tokens
Output tokens
Total tokens
Inference cost
```

Those metrics stop too early.

The business-value chain is:

```text
TOKENS
   ↓
AI COST
   ↓
SUCCESSFUL INTERACTION
   ↓
CUSTOMER INTENT PRESERVED
   ↓
POTENTIAL ORDER RECOVERED
   ↓
CONTRIBUTION RECOVERED
```

The better question is not:

> How many tokens did we consume?

It is:

> **How much economically valuable demand did those tokens help recover?**

---

## 4. Primary Metric — AI Value Multiple

```text
AI Value Multiple
=
Recovered Contribution
÷
AI Inference Cost
```

Example:

```text
Recovered monthly contribution     $2,381
AI inference cost                     $25
------------------------------------------
AI Value Multiple                      94x
```

This does **not** claim a proven 94x production ROI.

It means:

> Under the stated assumptions, every $1 of AI inference supports approximately $94 of recovered contribution opportunity.

The assumptions must always remain explicit and adjustable.

---

## 5. Illustrative Coffee-Shop Economics

Assume:

```text
Missed customer contacts/day          100
AI-eligible contacts                   60%
Successful-resolution rate             70%
Conversion after successful answer     30%
Average order value                    $18
Contribution margin                    35%
```

These are illustrative demo assumptions.

### Addressable demand

```text
100 × 60% = 60 contacts/day
```

### Successfully served interactions

```text
60 × 70% = 42 successful interactions/day
```

### Estimated recovered orders

```text
42 × 30% = 12.6 orders/day
```

### Estimated recovered revenue

```text
12.6 × $18 = $226.80/day
```

### Estimated recovered contribution

```text
$226.80 × 35% = $79.38/day

$79.38 × 30
≈ $2,381/month
```

---

## 6. Add AI Inference Cost

Suppose measured token usage and model pricing work out to an illustrative:

```text
AI cost per successful interaction = $0.02
```

Then:

```text
42 × $0.02 × 30
=
$25.20 AI inference cost/month
```

So:

```text
Recovered contribution/month       ≈ $2,381
AI inference cost/month            ≈    $25
-------------------------------------------
AI Value Multiple                  ≈    94x
```

The important relationship is:

```text
Measured AI behavior
        +
Transparent business assumptions
        ↓
Estimated economic value
```

---

## 7. Metric Ladder

```text
Cost per token
      ↓
Cost per interaction
      ↓
Cost per successful resolution
      ↓
Cost per recovered order
      ↓
Contribution per AI dollar
```

A business does not ultimately buy tokens.

It buys outcomes.

---

## 8. Metrics to Track

### AI / Operational
- Average input tokens
- Average output tokens
- Total tokens
- Inference cost
- Latency
- Search/tool usage

### Quality
- Behavior rubric pass rate
- Scope adherence
- Successful-resolution rate
- Abstention quality
- Hallucination rate
- Retrieval/grounding quality

### Business
- Estimated recoverable interactions
- Estimated recovered orders
- Average order value
- Contribution margin
- Estimated recovered contribution

### Tokenomics
- Cost per interaction
- Cost per successful resolution
- Cost per recovered order
- Value per 1K tokens
- AI Value Multiple
- Break-even conversion rate

---

## 9. Quality Is More Important Than Cheapness

> **Lower token cost does not automatically mean better economics.**

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

Agent B is cheaper, but Agent A creates substantially more business value.

Therefore:

> **Optimize token margins, not token consumption.**

The objective is not:

```text
fewest tokens
```

It is:

```text
highest valuable outcome
per dollar of inference
```

---

## 10. Cost per Successful Resolution

```text
Cost per Successful Resolution
=
Total AI inference cost
÷
Successful customer interactions
```

Example:

```text
$25 ÷ 1,260
≈ $0.02 per successful resolution
```

This answers:

> **How much AI spending is required to produce one interaction that meets our quality bar?**

---

## 11. Value per 1K Tokens

```text
Value per 1K Tokens
=
Recovered Contribution
÷
Total Tokens
× 1,000
```

This can help compare prompt versions, model choices, context sizes, retrieval strategies, and tool-use patterns.

It should remain secondary to business-level measures such as **contribution per AI dollar**.

---

## 12. Break-Even Conversion Rate

A strong business question is:

> **How little conversion does the agent need to generate merely to pay for its inference cost?**

Conceptually:

```text
Break-even conversion rate
=
AI cost
÷
(successfully served interactions
   × average order value
   × contribution margin)
```

Instead of arguing, “conversion will be 30%,” the demo can say:

> **Here is the minimum conversion rate required for inference to break even. Anything above it creates positive contribution under these assumptions.**

---

## 13. Sensitivity Analysis

Do not depend on one assumption.

| Scenario | Conversion Rate | Interpretation |
|---|---:|---|
| Bear | 10% | Conservative recovery |
| Base | 20% | Moderate recovery |
| Bull | 30% | Strong recovery |

Also vary:

- missed contacts/day,
- AI-eligible rate,
- successful-resolution rate,
- average order value,
- contribution margin,
- inference cost.

The purpose is not to manufacture a large ROI number.

It is to understand:

> **Under what conditions does this system create economic value?**

---

## 14. Measured vs Assumed vs Proven

| Measured by AI System | Assumed for Demo | Validate in Real Pilot |
|---|---|---|
| Tokens | Missed contacts | Actual missed demand |
| AI cost | AI-eligible rate | Incremental orders |
| Latency | Conversion rate | Actual conversion |
| Evaluation quality | Average order value | Actual AOV |
| Scope adherence | Contribution margin | Contribution lift |
| Resolution quality | — | Repeat behavior |

The demo should never confuse **modeled economics** with **proven production ROI**.

---

## 15. Connecting Evaluation to Economics

```text
Regression dataset
      ↓
Foundry evaluators
      ↓
Measured behavior quality
      ↓
Economic model
```

If behavior pass rate is 92%, the economics should not pretend that 100% of interactions create value.

Evaluation answers:

> **How much of the token spend actually produces acceptable behavior?**

That makes evaluation directly relevant to tokenomics.

---

## 16. Why Evaluation Is Part of Tokenomics

```text
Cheap model
   ↓
Poorer answers
   ↓
Lower successful-resolution rate
   ↓
Lower economic value
```

versus:

```text
More expensive model
   ↓
Better answers
   ↓
Higher successful-resolution rate
   ↓
Higher economic value
```

Therefore:

> **Token cost without quality context is incomplete.**

The correct optimization target combines:

```text
token usage
+
quality
+
business outcome
```

---

## 17. Questions We Should Keep Asking

### Where is value leaking?
- How many interactions go unanswered?
- When does it happen?
- Which requests are repetitive enough for AI?

### How much can AI safely recover?
- What percentage is AI-addressable?
- What percentage does the agent resolve successfully?
- Where should it abstain?
- What is the cost of a wrong answer?

### What is a successful interaction worth?
- What percentage might proceed to purchase?
- What is average order value?
- What is contribution margin?

### What does the intelligence cost?
- Input/output tokens?
- Search/tool calls?
- Retries?
- Cost per successful resolution?
- Contribution per AI dollar?

---

## 18. What Optimization Should Mean

```text
Token optimization
      ↓
Cost optimization
      ↓
Outcome optimization
      ↓
Economic optimization
```

A naïve goal is:

```text
Reduce tokens
```

A better goal is:

```text
Maintain or improve quality
while reducing cost per successful outcome
```

The business goal is:

```text
Maximize recovered contribution
per dollar of AI inference
```

---

## 19. Suggested Demo Story

### Act 1 — The problem

> A coffee shop is overwhelmed at peak time. The phone rings while staff are making drinks and serving customers. Nobody answers. The baseline is not another employee doing the task; the baseline is lost demand worth $0.

```text
Phone rings
   ↓
No answer
   ↓
Lost demand
```

### Act 2 — The agent

Demonstrate questions such as:

```text
How much is a Caramel Macchiato?
What coffees are under $3?
Which drinks are caffeine-free?
Do you sell Pumpkin Spice Latte?
```

Show that the agent is grounded in Azure AI Search and that quality is measured rather than assumed.

### Act 3 — The economics

```text
100 missed contacts
       ↓
60% AI-addressable
       ↓
measured agent quality
       ↓
successful interactions
       ↓
estimated conversion
       ↓
recovered contribution
       ↓
AI Value Multiple
```

Then change assumptions live:

```text
Conversion 30% → 10%
Inference cost 1x → 2x
Quality 95% → 80%
```

and show how the economics change.

---

## 20. Strongest Comparison — Agent A vs Agent B

Do not ask:

> Which agent uses fewer tokens?

Ask:

> **Which agent produces stronger economics?**

```text
Agent A
More tokens
Higher quality
Higher resolution
Higher recovered contribution

Agent B
Fewer tokens
Lower quality
Lower resolution
Lower recovered contribution
```

The lesson:

> **A more expensive agent can be economically superior if additional quality creates more value than the extra inference cost.**

That is the difference between **token-consumption optimization** and **token-margin optimization**.

---

## 21. Why We Do Not Need Ordering Logic

A real ordering system adds:

- payments,
- POS integration,
- inventory,
- order state,
- fulfillment,
- sensitive customer data.

None of that is needed to answer the tokenomics question.

For this project:

```text
Successful menu conversation
       ↓
modeled probability of purchase
       ↓
estimated economic outcome
```

is sufficient.

---

## 22. Proposed Economics Report Output

```text
CONTOSO COFFEE — AI ECONOMICS

MEASURED AI PERFORMANCE
──────────────────────────────────────
Evaluation cases                    20
Behavior pass rate                 95%
Scope adherence                   100%
Average input tokens               ...
Average output tokens              ...
Average inference cost             ...
Cost / successful resolution       ...

BUSINESS ASSUMPTIONS
──────────────────────────────────────
Missed contacts / day              100
AI eligible                         60%
Conversion                          20%
Average order                       $18
Contribution margin                 35%

ESTIMATED ECONOMICS
──────────────────────────────────────
Addressable contacts / day          ...
Successful interactions / day       ...
Estimated recovered orders / day    ...
Recovered revenue / month           ...
Recovered contribution / month      ...
AI inference cost / month            ...
AI Value Multiple                    ...x

SENSITIVITY
──────────────────────────────────────
10% conversion                       ...
20% conversion                       ...
30% conversion                       ...

BREAK-EVEN
──────────────────────────────────────
Minimum conversion required          ...%
```

---

## 23. How the Existing Agent Lifecycle Connects to Economics

```text
Evaluation
   ↓
Are our tokens producing correct behavior?

Optimizer
   ↓
Can we produce equal or better behavior more efficiently?

Monitoring
   ↓
Are quality, latency, and cost staying healthy?

Regression gates
   ↓
Did a proposed change damage value-producing behavior?

Tokenomics
   ↓
Is the entire system economically worth operating?
```

Tokenomics gives the Agent Development Lifecycle a common business objective.

---

## 24. Final Business Thesis

The business case is not:

> AI is cheaper than hiring another employee.

The stronger thesis is:

> **AI may economically serve demand that the business currently cannot serve at all.**

The tokenomics question is not:

> How cheaply can we generate an answer?

It is:

> **How much high-quality economic value can we create for every dollar of AI inference?**

And the optimization goal becomes:

> **Strong quality + recovered contribution + efficient inference = healthy token margins.**

---

## Recommended Project Scope

Keep the next tokenomics slice focused on:

```text
Measure token usage
        ↓
Measure agent quality
        ↓
Define transparent business assumptions
        ↓
Calculate recovered contribution
        ↓
Calculate AI inference cost
        ↓
Calculate AI Value Multiple
        ↓
Run bear/base/bull sensitivity
        ↓
Calculate break-even conversion
```

Do **not** build a real ordering system unless it later serves a separate learning objective.

The business case and economics belong together because they form one continuous story:

```text
Business problem
      ↓
Lost demand
      ↓
AI intervention
      ↓
Measured quality and cost
      ↓
Modeled recovered contribution
      ↓
Token economics
      ↓
Business decision
```
