"""
Simple Revenue Ledger
Tracks verified external revenue with almost zero overhead.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


@dataclass
class LedgerEntry:
    entry_id: str
    amount_nzd: float
    product_id: str
    order_id: Optional[str]
    source: str                  # "stripe", "manual", etc.
    recorded_at: str
    note: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)


class SimpleLedger:
    def __init__(self):
        self.entries: List[LedgerEntry] = []

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def record(
        self,
        amount_nzd: float,
        product_id: str,
        source: str = "stripe",
        order_id: Optional[str] = None,
        note: str = "",
        **meta
    ) -> LedgerEntry:
        entry = LedgerEntry(
            entry_id=str(uuid.uuid4())[:10],
            amount_nzd=amount_nzd,
            product_id=product_id,
            order_id=order_id,
            source=source,
            recorded_at=self._now(),
            note=note,
            meta=meta
        )
        self.entries.append(entry)
        return entry

    def total(self) -> float:
        return sum(e.amount_nzd for e in self.entries)

    def total_by_product(self) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for e in self.entries:
            out[e.product_id] = out.get(e.product_id, 0.0) + e.amount_nzd
        return out

    def count(self) -> int:
        return len(self.entries)
