"""
Pricing & Offer Engine
Low-overhead helpers for charm pricing, anchoring, and offer presentation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class PricePoint:
    amount_nzd: float
    label: str = ""
    is_recommended: bool = False
    anchor_text: Optional[str] = None   # e.g. "Normally $49"


@dataclass
class Offer:
    product_id: str
    name: str
    prices: List[PricePoint]
    description: str = ""
    delivery: str = "Digital delivery within 24h"

    def recommended(self) -> Optional[PricePoint]:
        for p in self.prices:
            if p.is_recommended:
                return p
        return self.prices[0] if self.prices else None


class PricingEngine:
    """
    Tiny helper for consistent pricing display and psychology.
    No external calls.
    """

    def charm(self, amount: float) -> float:
        """Convert to charm price (e.g. 20 -> 19)"""
        if amount >= 10 and amount == int(amount):
            return amount - 1
        return amount

    def format_nzd(self, amount: float) -> str:
        if amount == int(amount):
            return f"NZ${int(amount)}"
        return f"NZ${amount:.2f}"

    def build_anchor_line(self, real: float, anchor: float) -> str:
        return f"Normally {self.format_nzd(anchor)} → Today {self.format_nzd(real)}"

    def make_simple_offer(
        self,
        product_id: str,
        name: str,
        price: float,
        anchor: Optional[float] = None,
        description: str = ""
    ) -> Offer:
        pp = PricePoint(
            amount_nzd=price,
            label="Standard",
            is_recommended=True,
            anchor_text=self.build_anchor_line(price, anchor) if anchor else None
        )
        return Offer(
            product_id=product_id,
            name=name,
            prices=[pp],
            description=description
        )
