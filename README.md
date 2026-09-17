# LLM ↔ Supabase ↔ GitHub Bridge

Minimal reference implementation for a **local-first, offline-capable, air-gap friendly** agentic system that hybridises with cloud (GitHub Actions + Supabase) for durability, CI, billing evidence, and multi-agent coordination.

**North star:** Verified external economic activity that survives an independent evidence chain. Architecture and green CI are necessary but never sufficient.

## Design Principles

- **Local-first / offline-first**: Core logic, evidence packaging, and Truth Oracle adjudication can run without network. Supabase CLI + local Postgres or embedded SQLite/Postgres for air-gap mode.
- **GitHub as durable control plane**: Source of truth for code, schemas, migrations, Actions workflows, and public fossils. Cloud is the stronger hand for verification and distribution; local is the stronger hand for IP and air-gap.
- **One hand washes the other**: Local agents produce evidence → push to GitHub / Supabase when online → Actions + MCP agents verify, ledger, and monetise → results flow back.
- **No reinvention**: Use official Stripe, official Supabase MCP + GitHub Integration, standard Postgres, standard GitHub Actions. Only the evidence contract and silo boundaries are proprietary IP.
- **Evidence over claims**: Every commercial claim must be backed by a fossil (immutable package with hash, Stripe refs, delivery proof, run_id).

## Quick Start (Hybrid)

1. Clone this repo.
2. `supabase init` (or use existing project) and apply `supabase/migrations/`.
3. Configure Stripe webhook endpoint (see `docs/stripe.md`).
4. Wire MCP client to your Supabase project (see `docs/mcp.md`).
5. Push to GitHub → Actions run migrations, verification, and evidence gates.
6. For pure local/air-gap: run the same SQL against local Postgres and use the offline scripts in `scripts/`.

## Structure

```
supabase/
  migrations/          # Evidence + billing schemas (Postgres)
docs/
  evidence-contract.md # Canonical evidence rules
  stripe.md            # Official Stripe integration notes
  mcp.md               # MCP wiring
  local-first.md       # Offline / air-gap mode
.github/workflows/     # Cloud control plane
scripts/               # Local + hybrid runners
```

## Current Focus

- Evidence schemas (immutable events, fossils, economic truth)
- Stripe webhook → evidence ledger (no custom payment rails)
- GitHub Actions as the always-on verifier
- MCP surface for LLM agents
- Local-first packaging so IP stays under your control

See `docs/evidence-contract.md` and the migration files for the living schema.

## License / IP

Public reference for the bridge pattern. Proprietary business logic, private datasets, credentials, and silo-specific rules stay in private repos / local storage. This repo is the shared, auditable skeleton.
