# Autonomous Cloud Map

Purpose: document the existing control path for autonomous local semantic work without introducing a second orchestrator.

## Control path

1. Existing supervisor creates or receives bounded work.
2. `control_bridge_notes` is the durable handoff surface.
3. `claim_local_gpu_bridge_note` leases eligible work to `local-gpu`.
4. Local GPU worker calls LM Studio on the operator-owned machine.
5. Worker returns structured semantic output through `complete_control_bridge_note`.
6. Existing reconciliation/evidence machinery remains authoritative for economic claims.
7. Supabase Cron runs the local-GPU dispatcher every minute.

## Authority boundary

AUTO: inspection, classification, summarisation, bounded generation, testing, telemetry, stale-work handling.

HUMAN_GATE: spending, secrets, consequential public release, mass external communications, legal commitments, destructive infrastructure, and promotion of economic claims to verified.

## Non-goals

This map does not create a second scheduler, payment ledger, economic truth table, or autonomous external outreach system.

## Local dependency

The cloud control plane cannot start a process on the operator's Windows/GPU machine. LM Studio/llmster and the local worker must be running there. The cloud side queues and leases work; the local machine performs inference.

## Failure semantics

A successful worker process or LLM response is not a payment, fulfillment, or verified outcome. Revenue remains governed by the existing economic evidence chain.
