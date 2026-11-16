"""
Document Extraction Service — minimal, local-first
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import hashlib
import re


@dataclass
class ExtractRequest:
    filename: str
    text: str
    content_type: str = "text/plain"


@dataclass
class ExtractResult:
    success: bool
    document_id: str
    fields: Dict[str, Any]
    summary: str
    warnings: List[str]


class DocumentExtractor:
    def run(self, req: ExtractRequest) -> ExtractResult:
        warnings: List[str] = []
        text = (req.text or "").strip()

        if not text:
            return ExtractResult(
                success=False,
                document_id="none",
                fields={},
                summary="No text content",
                warnings=["Empty document"]
            )

        doc_id = hashlib.sha256(f"{req.filename}:{text[:300]}".encode()).hexdigest()[:12]

        fields: Dict[str, Any] = {}
        lower = text.lower()

        if "invoice" in lower:
            fields["type"] = "invoice"
        elif "statement" in lower:
            fields["type"] = "statement"
        elif "contract" in lower or "agreement" in lower:
            fields["type"] = "contract"
        else:
            fields["type"] = "unknown"

        amounts = re.findall(r"\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?", text)
        if amounts:
            fields["amounts"] = amounts[:8]

        # Very light date detection
        dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
        if dates:
            fields["dates"] = dates[:5]

        summary = f"{fields.get('type', 'document')} · {len(fields)} field groups"

        return ExtractResult(
            success=True,
            document_id=doc_id,
            fields=fields,
            summary=summary,
            warnings=warnings
        )
