# Monetization Modules

Low-overhead building blocks for turning DreamLedger tools into paid products.

## Modules

| Module | Purpose |
|--------|--------|
| `pricing` | Charm pricing, anchoring, offer presentation |
| `fulfilment` | Tracks payment → entitlement → delivery → complete |
| `entitlements` | What a customer has unlocked |
| `ledger` | Simple verified revenue log |
| `offers` | Product catalog (current NZ$5 / NZ$19 / NZ$29 offers) |

## Typical Paid Loop

```python
from modules.offers import ProductCatalog
from modules.fulfilment import FulfilmentTracker
from modules.entitlements import EntitlementStore
from modules.ledger import SimpleLedger
from modules.pricing import PricingEngine

catalog = ProductCatalog()
tracker = FulfilmentTracker()
entitlements = EntitlementStore()
ledger = SimpleLedger()
pricing = PricingEngine()

# 1. Customer pays for supplier-check
product = catalog.get("supplier-check")
order = tracker.create(product.product_id, customer_ref="user_123", amount_nzd=product.price_nzd)

# 2. Payment confirmed (e.g. from Stripe webhook)
tracker.mark_paid(order.order_id, payment_ref="pi_abc")

# 3. Grant entitlement
tracker.mark_entitled(order.order_id)
entitlements.grant("user_123", product.product_id, order_id=order.order_id)

# 4. Deliver result
tracker.mark_delivered(order.order_id, method="email", reference="msg_456")
tracker.complete(order.order_id)

# 5. Record revenue
ledger.record(product.price_nzd, product.product_id, order_id=order.order_id, source="stripe")

print("Total verified revenue:", ledger.total())
```

These modules stay local-first and air-gap friendly. Swap the in-memory stores for Supabase tables when you are ready.
