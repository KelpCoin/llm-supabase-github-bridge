# DreamLedger / Agent Bridge — Low-Overhead Modules

These modules are designed for:

- Minimal runtime overhead
- Almost zero Human-in-the-Loop (HIL)
- Local-first / air-gap friendly execution
- Clean, reusable interfaces

## Modules

| Module | Purpose |
|--------|--------|
| `airgap` | Lightweight isolation + attestation runner |
| `low_hil` | Fire-and-forget job runner with almost no state |
| `supplier_check` | Deterministic NZ supplier legitimacy scoring |
| `document_extract` | Simple local document field extraction |

## Quick Usage

```python
from modules.airgap import AirGap, IsolationLevel
from modules.supplier_check import SupplierCheck, SupplierInput
from modules.low_hil import LowHILRunner, Job

air = AirGap(IsolationLevel.STRICT)
check = SupplierCheck()

def do_check():
    return check.run(SupplierInput(
        business_name="Example Ltd",
        nzbn="1234567890123"
    ))

result = air.run(do_check)
print(result.success, result.attestation, result.result)
```

## Design Principles

- No heavy frameworks
- No required network calls
- Deterministic where possible
- Easy to run inside stricter isolation later (containers, seccomp, etc.)
