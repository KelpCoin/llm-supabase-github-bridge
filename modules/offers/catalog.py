"""
Simple Product Catalog
Central place for the current monetizable offers.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Product:
    product_id: str
    name: str
    price_nzd: float
    description: str
    delivery_sla: str = "Within 24 hours"
    active: bool = True
    category: str = "digital"


class ProductCatalog:
    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._seed()

    def _seed(self):
        """Current DreamLedger offers"""
        defaults = [
            Product("doc-extract", "Document Extraction", 5.0,
                    "Fast structured extraction from documents"),
            Product("supplier-check", "Supplier Check", 19.0,
                    "NZ-focused legitimacy and red-flag scan"),
            Product("deck-diagnostic", "Commander Deck Diagnostic", 29.0,
                    "Actionable analysis and upgrade suggestions"),
            Product("profit-audit", "Seller Profit Audit", 29.0,
                    "Clear view of margins and leakage"),
        ]
        for p in defaults:
            self._products[p.product_id] = p

    def get(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)

    def list_active(self) -> List[Product]:
        return [p for p in self._products.values() if p.active]

    def add(self, product: Product):
        self._products[product.product_id] = product
