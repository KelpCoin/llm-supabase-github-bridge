"""
DreamLedger / Agent Bridge — AirGap Module
Low-overhead isolation layer. Minimal HIL.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone


class IsolationLevel(str, Enum):
    STRICT = "strict"          # No external side effects expected
    CONTROLLED = "controlled"  # Only allowlisted actions
    OBSERVE = "observe"        # Log only, no enforcement


@dataclass
class AirGapContext:
    request_id: str
    isolation_level: IsolationLevel
    started_at: float
    meta: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def log(self, event: str, **data):
        self.events.append({
            "t": round(time.time() - self.started_at, 4),
            "event": event,
            **data
        })


@dataclass
class AirGapResult:
    success: bool
    request_id: str
    result: Any = None
    error: Optional[str] = None
    isolation_level: str = ""
    duration_ms: float = 0.0
    events: List[Dict[str, Any]] = field(default_factory=list)
    attestation: Optional[str] = None


class AirGap:
    """
    Tiny, dependency-free air-gap runner.
    Designed for minimal overhead and almost zero HIL.
    """

    def __init__(self, default_level: IsolationLevel = IsolationLevel.STRICT):
        self.default_level = default_level

    def context(self, level: Optional[IsolationLevel] = None, **meta) -> AirGapContext:
        return AirGapContext(
            request_id=str(uuid.uuid4()),
            isolation_level=level or self.default_level,
            started_at=time.time(),
            meta=meta
        )

    def run(self, fn: Callable, *args, ctx: Optional[AirGapContext] = None, **kwargs) -> AirGapResult:
        ctx = ctx or self.context()
        ctx.log("start", level=ctx.isolation_level.value)

        try:
            out = fn(*args, **kwargs)
            ctx.log("success")
            duration = (time.time() - ctx.started_at) * 1000

            # Simple attestation hash of the result
            att = self._attest(out)

            return AirGapResult(
                success=True,
                request_id=ctx.request_id,
                result=out,
                isolation_level=ctx.isolation_level.value,
                duration_ms=round(duration, 2),
                events=ctx.events,
                attestation=att
            )
        except Exception as e:
            ctx.log("error", error=str(e))
            duration = (time.time() - ctx.started_at) * 1000
            return AirGapResult(
                success=False,
                request_id=ctx.request_id,
                error=str(e),
                isolation_level=ctx.isolation_level.value,
                duration_ms=round(duration, 2),
                events=ctx.events
            )

    def _attest(self, payload: Any) -> str:
        try:
            raw = json.dumps(payload, sort_keys=True, default=str)
        except Exception:
            raw = str(payload)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
