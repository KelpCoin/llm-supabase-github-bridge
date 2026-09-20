#!/usr/bin/env python3
"""Offline fossil package stub — air-gap friendly.

Builds a JSON fossil skeleton from local inputs. Does NOT contact Stripe.
Promote to verified only after live Stripe reconciliation + oracle rules.

Usage:
  python scripts/package_fossil_stub.py --run-id UUID --silo dreamledger \\
    --amount-cents 5000 --currency nzd --pi pi_xxx --cs cs_xxx \\
    --external true --test-mode false --out ./out/fossil.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_canonical(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--silo", default="dreamledger")
    p.add_argument("--amount-cents", type=int, required=True)
    p.add_argument("--currency", default="nzd")
    p.add_argument("--pi", default="", help="payment_intent id")
    p.add_argument("--cs", default="", help="checkout session id")
    p.add_argument("--customer", default="")
    p.add_argument("--external", default="false")
    p.add_argument("--test-mode", default="true")
    p.add_argument("--fulfilment-note", default="")
    p.add_argument("--out", default="fossil.json")
    args = p.parse_args()

    external = args.external.lower() in ("1", "true", "yes")
    test_mode = args.test_mode.lower() in ("1", "true", "yes")

    content = {
        "run_id": args.run_id,
        "silo_id": args.silo,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "economic": {
            "amount_cents": args.amount_cents,
            "currency": args.currency,
            "stripe_payment_intent": args.pi or None,
            "stripe_checkout_session": args.cs or None,
            "stripe_customer": args.customer or None,
            "is_external_customer": external,
            "is_test_mode": test_mode,
            "status": "succeeded",
        },
        "fulfilment": {"note": args.fulfilment_note},
        "rules": {
            "counts_as_verified_revenue": external and not test_mode and bool(args.pi or args.cs),
            "evidence_contract": "1.0",
        },
    }
    content["package_hash"] = sha256_canonical({k: v for k, v in content.items() if k != "package_hash"})

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(content, indent=2), encoding="utf-8")
    print(f"Wrote {out} hash={content['package_hash']}")
    if not content["rules"]["counts_as_verified_revenue"]:
        print("NOTE: counts_as_verified_revenue=false (test mode, missing ids, or not external)")


if __name__ == "__main__":
    main()
