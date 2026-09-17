# Local-First, Offline-First, Air-Gap Compatible

Your system is local-first. The cloud (GitHub + Supabase) is a durability and verification layer, not the source of truth for IP.

## How the Hands Wash Each Other

| Local (strong for IP / air-gap) | Cloud (strong for durability / verification) |
|--------------------------------|----------------------------------------------|
| Evidence packaging             | GitHub Actions verification + fossils        |
| Truth Oracle adjudication      | MCP agents + Supabase ledger                 |
| Offline offer experiments      | Stripe reconciliation when online            |
| Private schemas / silo rules   | Public reference skeleton (this repo)        |
| Air-gapped runs                | Hybrid sync of verified fossils              |

## Recommended Local Stack

1. **Postgres** (or SQLite for pure offline experiments) with the same migration SQL.
2. **Supabase CLI** (`supabase start`) for local Auth, Storage, Edge Functions if desired.
3. Scripts in `scripts/` that:
   - Create run_ids
   - Append evidence_events
   - Package fossils (hash the content)
   - Run a local Truth Oracle (simple rule engine that implements the contract)
4. When network is available:
   - `git push` fossils / new migrations
   - Sync economic_events with Stripe API
   - Let GitHub Actions re-adjudicate and promote

## Air-Gap Mode

- No outbound network from the agent runtime.
- All Stripe interactions happen later via a controlled online reconciler that only promotes verified external payments.
- Fossils are content-addressed; they can be transferred via USB / secure channel and still validate.

## Hybrid Workflow Example

1. Local agent creates an offer and records an evidence_event (offline).
2. Customer pays via Stripe Checkout (online path).
3. Webhook lands in Supabase → economic_event row.
4. Local or CI process packages a fossil linking the offline evidence + Stripe event.
5. Truth Oracle (local or Actions) issues PASS only if all rules are satisfied.
6. Verified revenue is the only number that appears in daily briefings.

This keeps intellectual property local while using the cloud for the hard parts of verification, distribution, and multi-agent coordination.
