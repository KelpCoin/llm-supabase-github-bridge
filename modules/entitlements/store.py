"""
Simple Entitlement Store
Tracks what a customer has paid for / unlocked.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone
import uuid


@dataclass
class Entitlement:
    entitlement_id: str
    customer_ref: str
    product_id: str
    granted_at: str
    order_id: Optional[str] = None
    active: bool = True
    meta: Dict = field(default_factory=dict)


class EntitlementStore:
    def __init__(self):
        self._items: Dict[str, Entitlement] = {}
        # customer_ref -> set of product_ids
        self._index: Dict[str, Set[str]] = {}

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def grant(self, customer_ref: str, product_id: str, order_id: Optional[str] = None, **meta) -> Entitlement:
        eid = str(uuid.uuid4())[:12]
        ent = Entitlement(
            entitlement_id=eid,
            customer_ref=customer_ref,
            product_id=product_id,
            granted_at=self._now(),
            order_id=order_id,
            meta=meta
        )
        self._items[eid] = ent
        self._index.setdefault(customer_ref, set()).add(product_id)
        return ent

    def has(self, customer_ref: str, product_id: str) -> bool:
        return product_id in self._index.get(customer_ref, set())

    def list_for_customer(self, customer_ref: str) -> List[Entitlement]:
        return [e for e in self._items.values() if e.customer_ref == customer_ref and e.active]
