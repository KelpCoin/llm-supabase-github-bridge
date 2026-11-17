"""
Fulfilment Tracker
Records the critical paid loop: payment → entitlement → delivery → receipt.
Designed for low overhead and clear evidence.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid


class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    ENTITLED = "entitled"
    DELIVERED = "delivered"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class DeliveryRecord:
    method: str
    reference: str
    delivered_at: str
    notes: str = ""


@dataclass
class Order:
    order_id: str
    product_id: str
    customer_ref: str
    amount_nzd: float
    status: OrderStatus
    created_at: str
    paid_at: Optional[str] = None
    entitled_at: Optional[str] = None
    delivered_at: Optional[str] = None
    delivery: Optional[DeliveryRecord] = None
    meta: Dict[str, Any] = field(default_factory=dict)


class FulfilmentTracker:
    """
    In-memory + serialisable fulfilment tracker.
    Replace the dict store with Supabase/SQLite later.
    """

    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create(self, product_id: str, customer_ref: str, amount_nzd: float, **meta) -> Order:
        oid = str(uuid.uuid4())[:12]
        order = Order(
            order_id=oid,
            product_id=product_id,
            customer_ref=customer_ref,
            amount_nzd=amount_nzd,
            status=OrderStatus.CREATED,
            created_at=self._now(),
            meta=meta
        )
        self._orders[oid] = order
        return order

    def mark_paid(self, order_id: str, payment_ref: str = "") -> Optional[Order]:
        order = self._orders.get(order_id)
        if not order:
            return None
        order.status = OrderStatus.PAID
        order.paid_at = self._now()
        if payment_ref:
            order.meta["payment_ref"] = payment_ref
        return order

    def mark_entitled(self, order_id: str) -> Optional[Order]:
        order = self._orders.get(order_id)
        if not order:
            return None
        order.status = OrderStatus.ENTITLED
        order.entitled_at = self._now()
        return order

    def mark_delivered(self, order_id: str, method: str, reference: str, notes: str = "") -> Optional[Order]:
        order = self._orders.get(order_id)
        if not order:
            return None
        order.status = OrderStatus.DELIVERED
        order.delivered_at = self._now()
        order.delivery = DeliveryRecord(
            method=method,
            reference=reference,
            delivered_at=order.delivered_at,
            notes=notes
        )
        return order

    def complete(self, order_id: str) -> Optional[Order]:
        order = self._orders.get(order_id)
        if not order:
            return None
        order.status = OrderStatus.COMPLETE
        return order

    def get(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def list_by_status(self, status: OrderStatus) -> List[Order]:
        return [o for o in self._orders.values() if o.status == status]
