# Stripe Integration (No Reinvented Rails)

Use **official Stripe** only. This bridge records evidence; it does not replace Stripe Checkout, Billing, or Tax.

## Recommended Flow

1. Create Products / Prices in Stripe Dashboard (or via API).
2. Use Stripe Checkout Session or Payment Intent from your agent / Edge Function / local script.
3. Configure a Stripe webhook endpoint that points to:
   - Supabase Edge Function, **or**
   - A GitHub Actions workflow_dispatch / repository_dispatch that receives the event (via a thin relay), **or**
   - A simple public endpoint that inserts into `economic_events`.
4. The webhook handler must:
   - Verify the Stripe signature (`Stripe-Signature` header).
   - Extract `payment_intent`, `charge`, `customer`, `amount`, `currency`, `livemode`.
   - Decide `is_external_customer` (reject or flag known test/self customers).
   - Insert a row into `economic_events` with the full raw event in `raw_stripe_event`.
   - Optionally emit an `evidence_events` row and later package a fossil.

## Official Libraries

- Node: `stripe` (npm)
- Python: `stripe`
- Deno / Supabase Edge: use the official Stripe Deno port or fetch + crypto verification.

Never store full card numbers. Never invent your own payment tokens.

## Local / Air-Gap Mode

- Record intended economic events offline as pending fossils.
- When online, reconcile against Stripe API (`stripe.paymentIntents.retrieve`, etc.) and only promote to verified once Stripe confirms succeeded + external customer.
- Test mode events are always `is_test_mode = true` and never count toward verified revenue.

## Minimal Webhook Handler Sketch (Supabase Edge Function style)

```ts
// functions/stripe-webhook/index.ts (skeleton)
import Stripe from 'https://esm.sh/stripe@...';

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, { apiVersion: '2024-...' });
const endpointSecret = Deno.env.get('STRIPE_WEBHOOK_SECRET')!;

Deno.serve(async (req) => {
  const sig = req.headers.get('Stripe-Signature')!;
  const body = await req.text();
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, endpointSecret);
  } catch (err) {
    return new Response(`Webhook Error: ${err.message}`, { status: 400 });
  }

  if (event.type === 'checkout.session.completed' || event.type === 'payment_intent.succeeded') {
    // extract ids, amount, customer, livemode
    // insert into economic_events via Supabase client
    // emit evidence_event
  }

  return new Response(JSON.stringify({ received: true }), { status: 200 });
});
```

Full implementation belongs in your private project or in a later PR to this reference once secrets handling is decided.

## Security

- Webhook secret in Supabase secrets / GitHub Secrets only.
- RLS on `economic_events` so only service role or specific agents can write.
- Never expose Stripe secret keys to LLM agents; give them only the ability to create Checkout Sessions via a controlled Edge Function.
