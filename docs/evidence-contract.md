# Evidence Contract (Canonical)

Status: ACTIVE

## Governing Metric

Verified external economic activity that survives the evidence chain.

Not commits. Not architecture. Not green CI alone.

## Core Loop

```
DEMAND → OFFER → CUSTOMER → PAYMENT → FULFILMENT → EVIDENCE → FOSSIL → TRUTH ORACLE → VERIFIED REVENUE → REPEAT
```

## Economic Truth Rules

1. **EXTERNAL_CUSTOMER required** for Level 2/3 economic proof.
2. Self-payment, test cards, internal transfers, refund loops, and synthetic traffic **never** count as external revenue.
3. Missing payment reference (Stripe PaymentIntent / Charge / Checkout Session id), delivery evidence, or complete fossil → **FAIL** or **INCONCLUSIVE**.
4. Architecture success, CI green, or deployment success **never** overrides missing economic evidence.
5. Revenue claims remain NZ$0 (or equivalent) until independently evidenced and adjudicated.

## Control Planes

| Plane        | Role |
|--------------|------|
| **Truth Oracle** | Canonical economic adjudicator. PASS / FAIL / INCONCLUSIVE from evidence only. |
| **Gauntlet**     | Adversarial gate. Rejects weak, contaminated, incomplete, or non-reproducible claims. |
| **Elohim**       | Evidence refinement. Improves packages while preserving provenance; never manufactures evidence. |
| **CI / Actions** | Compiles, verifies silo boundaries, runs ecosystem gate, emits machine-readable proof before promotion. |
| **Local runner** | Offline packaging + adjudication when air-gapped. |

## Fossil Requirements

A fossil is an immutable, content-addressed package:

- Unique `run_id` (UUID or content hash)
- Timestamp (UTC)
- Actor / agent identity
- Silo identifier (strict isolation)
- Stripe references (payment_intent_id, charge_id, customer_id if external)
- Delivery / fulfilment evidence (hashes, URLs, receipts)
- Hash of the entire package (SHA-256)
- Optional parent fossil links for chains

Fossils are append-only. Updates create new fossils that reference the previous one.

## Silo Policy

Commercial data, offers, customer evidence, and automation state **must not** leak across silos.

Examples of silos that remain separated: MTG / HappyHomarid / CollectorsCoast vs Amplissa/adult vs any other business line.

## Automation vs Human Gates

Machine may autonomously:
- Discover, score, cluster, compile, verify, package evidence, monitor, ledger, report, deterministic fulfilment.

Human approval required for:
- Material spending
- Strategic pivots
- Sensitive external actions
- Public posting (default gated)
- Irreversible legal / reputational decisions

## Success Definition

Only fossils that the Truth Oracle marks **PASS** with an external customer and complete Stripe + delivery chain contribute to verified revenue.
