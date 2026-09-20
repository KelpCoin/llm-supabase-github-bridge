# Agent ping protocol (bridge ↔ DreamLedger)

**Purpose:** One LLM leaves kinetic state for another (GitHub or Supabase) without chat continuity.

## When you finish a session

1. Write or update a handoff in **KelpCoin/DreamLedger** `AGENT_BUS/HANDOFF-YYYY-MM-DD-*.md`  
2. Update `AGENT_BUS/PING_PONG_BALLS.json` if a ball’s status or `verified_external_revenue_nzd` changed  
3. If bridge economic truth changed, update `docs/figure-eight-status.json` here  
4. Never set `verified_external_revenue_nzd` from test-mode Stripe  

## When you start a session

1. Read DreamLedger `AGENT_BUS/README.md` → latest figure-eight + money handoffs  
2. Read `PING_PONG_BALLS.json` — pick **one** ball  
3. Read this repo `docs/figure-eight-status.json` + `docs/evidence-contract.md`  
4. Do not invent a parallel evidence schema  

## Money-specific pings

| Event | GitHub agent does | Supabase agent does |
|-------|-------------------|---------------------|
| Payment link confirmed live | Note in AGENT_BUS | — |
| Webhook received | — | Insert `economic_events` (signed, idempotent) |
| Fulfilment done | Store proof path in repo or point to URL | Attach delivery hash to fossil content |
| Oracle PASS | Update balls + figure-eight status | Write `oracle_verdicts` |

## Anti-patterns

- Completing local-gpu jobs while worker offline  
- Claiming revenue from green CI alone  
- Mixing silos (e.g. MTG evidence into unrelated line)  
- Treating PHINHAVEN play clears as economic events  
