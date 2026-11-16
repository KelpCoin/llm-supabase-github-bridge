"""
Low-HIL / Low-Overhead Job Runner
Fire-and-forget style helpers with almost no human intervention required.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import time
import uuid


@dataclass
class Job:
    name: str
    fn: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    timeout_s: float = 30.0


@dataclass
class JobResult:
    job_id: str
    name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class LowHILRunner:
    """
    Extremely lightweight runner.
    No queues, no external deps, minimal state.
    Ideal for local-first / air-gapped execution.
    """

    def __init__(self):
        self.history: List[JobResult] = []

    def run(self, job: Job) -> JobResult:
        job_id = str(uuid.uuid4())[:8]
        start = time.time()

        try:
            out = job.fn(*job.args, **job.kwargs)
            duration = (time.time() - start) * 1000
            res = JobResult(
                job_id=job_id,
                name=job.name,
                success=True,
                result=out,
                duration_ms=round(duration, 2)
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            res = JobResult(
                job_id=job_id,
                name=job.name,
                success=False,
                error=str(e),
                duration_ms=round(duration, 2)
            )

        self.history.append(res)
        # Keep history small
        if len(self.history) > 100:
            self.history = self.history[-50:]
        return res

    def run_many(self, jobs: List[Job]) -> List[JobResult]:
        return [self.run(j) for j in jobs]
