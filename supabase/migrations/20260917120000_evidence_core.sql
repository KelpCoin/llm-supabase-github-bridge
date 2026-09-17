-- Core evidence schemas for LLM-Supabase-GitHub bridge
-- Compatible with Supabase (Postgres 15+) and local Postgres.
-- Local-first: these tables work offline; sync / webhook ingestion happens when online.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Silos (strict isolation)
CREATE TABLE IF NOT EXISTS silos (
  id          text PRIMARY KEY,               -- e.g. 'mtg', 'happyhomarid', 'amplissa'
  name        text NOT NULL,
  description text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Agents / actors that produce or consume evidence
CREATE TABLE IF NOT EXISTS agents (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text NOT NULL UNIQUE,
  kind        text NOT NULL CHECK (kind IN ('llm', 'human', 'script', 'ci', 'webhook', 'oracle')),
  silo_id     text REFERENCES silos(id),
  metadata    jsonb NOT NULL DEFAULT '{}',
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Immutable evidence events (append-only log)
CREATE TABLE IF NOT EXISTS evidence_events (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id        uuid NOT NULL,                 -- groups related events into one fossil later
  agent_id      uuid REFERENCES agents(id),
  silo_id       text NOT NULL REFERENCES silos(id),
  event_type    text NOT NULL,                 -- e.g. 'offer_created', 'payment_received', 'fulfilment_complete', 'oracle_verdict'
  payload       jsonb NOT NULL DEFAULT '{}',
  content_hash  text NOT NULL,                 -- SHA-256 of canonical payload
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_evidence_events_run_id ON evidence_events(run_id);
CREATE INDEX IF NOT EXISTS idx_evidence_events_silo ON evidence_events(silo_id);
CREATE INDEX IF NOT EXISTS idx_evidence_events_type ON evidence_events(event_type);

-- Economic events (Stripe-centric, no custom rails)
CREATE TABLE IF NOT EXISTS economic_events (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id                uuid NOT NULL,
  silo_id               text NOT NULL REFERENCES silos(id),
  stripe_payment_intent text,                  -- pi_...
  stripe_charge         text,                  -- ch_...
  stripe_customer       text,                  -- cus_... (must be external)
  stripe_checkout_session text,                -- cs_...
  amount_cents          bigint NOT NULL CHECK (amount_cents >= 0),
  currency              text NOT NULL DEFAULT 'nzd',
  is_external_customer  boolean NOT NULL DEFAULT false,
  is_test_mode          boolean NOT NULL DEFAULT true,
  status                text NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded', 'disputed')),
  raw_stripe_event      jsonb,                 -- full webhook payload for audit
  created_at            timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_economic_events_run_id ON economic_events(run_id);
CREATE INDEX IF NOT EXISTS idx_economic_events_stripe_pi ON economic_events(stripe_payment_intent);

-- Fossils: content-addressed immutable packages
CREATE TABLE IF NOT EXISTS fossils (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id          uuid NOT NULL UNIQUE,
  silo_id         text NOT NULL REFERENCES silos(id),
  package_hash    text NOT NULL,               -- SHA-256 of entire fossil content
  parent_fossil_id uuid REFERENCES fossils(id),
  content         jsonb NOT NULL,              -- full package: events, economic, delivery, metadata
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fossils_silo ON fossils(silo_id);
CREATE INDEX IF NOT EXISTS idx_fossils_hash ON fossils(package_hash);

-- Truth Oracle verdicts
CREATE TABLE IF NOT EXISTS oracle_verdicts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  fossil_id       uuid NOT NULL REFERENCES fossils(id),
  run_id          uuid NOT NULL,
  verdict         text NOT NULL CHECK (verdict IN ('PASS', 'FAIL', 'INCONCLUSIVE')),
  reason          text NOT NULL,
  adjudicator     text NOT NULL DEFAULT 'truth-oracle',
  rules_version   text NOT NULL DEFAULT '1.0',
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_oracle_verdicts_fossil ON oracle_verdicts(fossil_id);
CREATE INDEX IF NOT EXISTS idx_oracle_verdicts_verdict ON oracle_verdicts(verdict);

-- Minimal offers (for agentic commerce experiments)
CREATE TABLE IF NOT EXISTS offers (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  silo_id     text NOT NULL REFERENCES silos(id),
  title       text NOT NULL,
  description text,
  amount_cents bigint NOT NULL CHECK (amount_cents > 0),
  currency    text NOT NULL DEFAULT 'nzd',
  stripe_price_id text,                        -- optional link to Stripe Price
  active      boolean NOT NULL DEFAULT true,
  metadata    jsonb NOT NULL DEFAULT '{}',
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- RLS scaffolding (enable and tighten in production)
ALTER TABLE silos ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE economic_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE fossils ENABLE ROW LEVEL SECURITY;
ALTER TABLE oracle_verdicts ENABLE ROW LEVEL SECURITY;
ALTER TABLE offers ENABLE ROW LEVEL SECURITY;

-- Seed a default silo for experiments (remove or restrict in production)
INSERT INTO silos (id, name, description)
VALUES ('experiment', 'Experiment Silo', 'Default silo for bridge reference and local testing')
ON CONFLICT (id) DO NOTHING;
