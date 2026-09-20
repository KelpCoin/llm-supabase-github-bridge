-- Priority commercial offers aligned with DreamLedger money MVP (NZD).
-- Does not create Stripe prices; links optional via stripe_price_id later.
-- Test/experiment silo only until production silo ids are confirmed.

INSERT INTO silos (id, name, description)
VALUES
  ('dreamledger', 'DreamLedger', 'Primary commercial silo for storefront SKUs'),
  ('experiment', 'Experiment Silo', 'Default silo for bridge reference and local testing')
ON CONFLICT (id) DO NOTHING;

INSERT INTO offers (silo_id, title, description, amount_cents, currency, active, metadata)
VALUES
  (
    'dreamledger',
    'Billboard founding tile',
    'NZ$50 permanent founding tile placement. Highest contribution SKU when fulfilment is light.',
    5000,
    'nzd',
    true,
    '{"payment_link": "https://buy.stripe.com/9B66oH2rj3dz82jcR6dwc2x", "sku": "TILE-50-NZD", "priority": 1}'::jsonb
  ),
  (
    'dreamledger',
    'Commander diagnostic',
    'NZ$29 written first-pass Commander diagnostic. Template labour to <=20 min.',
    2900,
    'nzd',
    true,
    '{"payment_link": "https://buy.stripe.com/00w7sLaXP01n96nbN2dwc2l", "sku": "CMD-DIAG-29-NZD", "priority": 2}'::jsonb
  ),
  (
    'dreamledger',
    'Discord webhook kit',
    'NZ$79 narrow Stripe-to-Discord operational kit. High margin if digital delivery automated.',
    7900,
    'nzd',
    true,
    '{"sku": "DISCORD-KIT-79-NZD", "priority": 3}'::jsonb
  )
ON CONFLICT DO NOTHING;

-- Note: offers table has no natural unique on title; if re-run duplicates appear, dedupe manually or add unique(silo_id, title).
