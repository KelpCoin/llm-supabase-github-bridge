# Local Peer

This is the durable offline fallback peer for the existing cloud control plane.

It uses SQLite with WAL mode, content hashes, durable jobs, capability manifests, evidence receipts, policy snapshots, and a reconciliation log.

The local peer may create/test/allocate work under cached policy. Local evidence is always `UNVERIFIED` until the existing cloud Evidence/Truth path independently establishes the claim.

This is a fallback and cache layer, not a replacement economic ledger and not a second cloud orchestrator.

## Run

`python workers/local-peer/local_peer.py`

Set `LOCAL_PEER_HOME` to choose the persistent local directory.

## Reconciliation contract

Pending operations are exposed by `pending_reconciliation()`. A future sync adapter may upload those operations idempotently using `operation_id` and `payload_sha256`, then mark them applied only after cloud acknowledgement.
