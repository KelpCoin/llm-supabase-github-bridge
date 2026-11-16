"""
Supplier Check Core — low overhead, deterministic, air-gap friendly
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import re


@dataclass
class SupplierInput:
    business_name: str
    nzbn: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


@dataclass
class SupplierResult:
    score: int
    risk: str
    findings: List[str]
    recommendations: List[str]


class SupplierCheck:
    NZBN_RE = re.compile(r"^\d{13}$")

    def run(self, data: SupplierInput) -> SupplierResult:
        findings: List[str] = []
        score = 65

        name = (data.business_name or "").strip()
        if len(name) < 2:
            findings.append("Business name missing or too short")
            score -= 25
        else:
            findings.append("Business name present")

        if data.nzbn:
            if self.NZBN_RE.match(data.nzbn.strip()):
                findings.append("NZBN format valid")
                score += 20
            else:
                findings.append("NZBN format invalid")
                score -= 20
        else:
            findings.append("No NZBN supplied")
            score -= 8

        if data.email and "@" in data.email:
            domain = data.email.split("@")[-1].lower()
            if domain in {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"}:
                findings.append("Free email domain")
                score -= 4
            else:
                findings.append("Custom email domain")
                score += 6

        if data.website:
            findings.append("Website provided")
            score += 5

        score = max(0, min(100, score))

        if score >= 75:
            risk = "low"
        elif score >= 45:
            risk = "medium"
        else:
            risk = "high"

        recs = []
        if not data.nzbn:
            recs.append("Request NZBN before any payment")
        if risk == "high":
            recs.append("Do not send funds until further verification")
        if risk != "low":
            recs.append("Consider additional documentation")

        return SupplierResult(
            score=score,
            risk=risk,
            findings=findings,
            recommendations=recs
        )
