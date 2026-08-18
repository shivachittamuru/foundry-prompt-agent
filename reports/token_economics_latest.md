# Contoso Coffee — Token Economics Report

Generated from evaluation run `20260818204234`.

> This report combines measured AI performance with explicit business assumptions.
> Business outcomes are modeled estimates, not proven production revenue.

## Executive Summary

The Contoso Coffee agent is evaluated as a demand-recovery system rather than
a labor-replacement system.

The business question is:

> **Can AI economically recover customer demand that would otherwise go unserved?**

The primary economics metric is:

**AI Value Multiple = Recovered Contribution / AI Inference Cost**

For this run:

- Behavior success rate: **90.0%**
- Cost per interaction: **$0.008022**
- Cost per successful resolution: **$0.008914**
- Estimated recovered contribution/month: **$1,701.00**
- Estimated AI inference cost/month: **$14.44**
- AI Value Multiple: **117.8x**
- Break-even conversion rate: **0.25%**

---

## 1. Measured AI Performance

These values came from the actual agent and Foundry evaluation run.

| Metric | Measured value |
|---|---:|
| Evaluation cases | 10 |
| Behavior success rate | 90.0% |
| Tokens per interaction | 2,417.3 |
| Cost per interaction | $0.008022 |
| Cost per successful resolution | $0.008914 |

These values are **measured**, not business assumptions.

---

## 2. Business Assumptions

| Assumption | Value |
|---|---:|
| Missed contacts/day | 100 |
| AI-eligible rate | 60% |
| Conversion rate | 30% |
| Average order value | $10.00 |
| Contribution margin | 35% |
| Operating days/month | 30 |

These values are illustrative assumptions and should be replaced with
observed business data in a real pilot.

---

## 3. Estimated Demand-Recovery Funnel

```text
Missed contacts/day
        100
          ↓
AI-addressable
        60.0
          ↓
Successfully served
        54.0
          ↓
Estimated recovered orders
        16.2
```

---

## 4. Conversion Sensitivity

The measured AI run is held fixed and only the conversion assumption varies.

| Conversion rate | Recovered contribution/month | AI inference cost/month | AI Value Multiple |
|---|---:|---:|---:|
| 5% | $283.50 | $14.44 | 19.6x |
| 10% | $567.00 | $14.44 | 39.3x |
| 20% | $1,134.00 | $14.44 | 78.5x |
| 30% | $1,701.00 | $14.44 | 117.8x |

Break-even for this run occurs at a conversion rate of
**0.25%**.
