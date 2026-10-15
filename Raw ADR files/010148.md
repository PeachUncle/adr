# ADR-001: ATLAS Integration (Documentation + Audit Sentinel)

**Status:** Proposed → Adopted  
**Date:** 2025-10-22  
**Owners:** @kaizencycle (Steward), JADE / EVE / ZEUS / HERMES / ATLAS  
**Scope:** Civic OS mono + Labs (4 / 6 / 7) + OAA-API-Library + Civic-Protocol-Core

## 1) Context

Civic OS operates a poly-agent governance loop (JADE, EVE, ZEUS, HERMES) with Labs providing APIs:
- Lab7 (OAA Hub) — learning/memory fabric & agent skills
- Lab4 (Reflections) — Wins/Blocks/TomorrowIntent cycles
- Lab6 (Citizen Shield) — identity/security & GI gating
- Civic-Protocol-Core — ledger/attestation primitives
- OAA-API-Library — schemas, adapters, capsules (.gic)

We need a fifth sentinel—ATLAS—to:
- normalize repo metadata & specs,
- audit integrity across services,
- publish a machine-readable "health + ethics" view,
- enable cross-model collaboration (Claude/DeepSeek/GPT).

## 2) Decision

Adopt ATLAS as the Documentation & Audit Intelligence layer with a stable API surface:
- Canonical endpoint namespace in Lab7:
  - `GET /api/atlas/audit` — integrity snapshot
  - `GET /api/atlas/catalog` — services & specs index
  - `POST /api/atlas/attest` — submit signed attestations
  - `GET /api/atlas/capsules` — list latest .gic capsules
  - `POST /api/atlas/capsules/verify` — schema/merkle/signature check
- Each service exposes an atlas manifest at:
  - `/.civic/atlas.manifest.json` (served or vendored)
- All outputs include GI score, Virtue Accord refs, and ledger anchors.

## 3) Consequences
- ✅ Uniform, inspectable audit surface for humans + AIs
- ✅ Easier cross-repo navigation & health checks
- ✅ Consistent provenance for .gic capsules
- ⛔ Adds lightweight work to maintain manifests
- ⛔ Requires GI gate and Shield headers on POSTs

## 4) Architecture (high level)

```
[Lab4 Reflections]    \
[Lab6 Shield]          \        +--> ledger://… attests
[Lab7 OAA Hub] ---------> ATLAS API ----+
[Civic-Protocol-Core]  /                 \
[OAA-API-Library]     /                   +--> .gic capsules index/verify
```

ATLAS aggregates reads from services, emits capsule + audit metadata, and writes attestations to the ledger via Civic-Protocol-Core.

## 5) Responsibilities
- **ATLAS:** documentation synthesis, audit snapshots, capsule verify
- **JADE:** logic & signature checks (ed25519)
- **EVE:** reflection metrics & drift notes
- **ZEUS:** quorum + change approvals
- **HERMES:** transmission logs & anomaly reports

## 6) API Contract (v1)

### 6.1 GET /api/atlas/audit

Returns the current Civic OS integrity view.

```json
{
  "cycle": "C-109",
  "timestamp": "2025-10-22T12:34:56Z",
  "gi_score": 0.972,
  "virtue_accords": ["Virtue Accord v1", "Yautja Kernel v1"],
  "services": [
    {"name":"lab7-oaa","status":"healthy","version":"1.3.2","hash":"b665ba8"},
    {"name":"lab4-reflections","status":"healthy","version":"1.2.1","hash":"910b67a"},
    {"name":"lab6-shield","status":"degraded","version":"0.9.8","hash":"2cae11"}
  ],
  "ledger_ref": "ledger://atlas/audit/0x42a9",
  "capsules_latest": ["sha256:…9d7c","sha256:…11aa"]
}
```

### 6.2 GET /api/atlas/catalog

Lists repos, OpenAPI links, and atlas.manifest locations.

```json
{
  "repos": [
    {"name":"OAA-API-Library","url":"https://github.com/kaizencycle/OAA-API-Library","manifest":"/.civic/atlas.manifest.json"},
    {"name":"lab7-proof","url":"https://github.com/kaizencycle/lab7-proof","manifest":"/.civic/atlas.manifest.json"}
  ]
}
```

### 6.3 POST /api/atlas/attest

Body: signed attestation by JADE/EVE/OWNER; Shield verifies GI ≥ policy.

Response:

```json
{"accepted": true, "ledger_ref":"ledger://attest/0x77ab", "gi":0.958}
```

### 6.4 GET /api/atlas/capsules

Returns the last N .gic capsule IDs + metadata.

```json
{
  "items":[
    {"id":"sha256:…6f4a","kind":"memory","owner":"michael.gic","gi":0.96,"created":"2025-10-22T12:09:00Z"}
  ]
}
```

### 6.5 POST /api/atlas/capsules/verify

Body: capsule (YAML/JSON).
Response: `{ ok: true, errors: [] }` (uses @civic/oaa-memory).

## 7) Atlas Manifest (required per service)

`/.civic/atlas.manifest.json` (served statically or generated):

```json
{
  "service": "lab7-oaa",
  "version": "1.3.2",
  "git": {"sha":"b665ba8","repo":"https://github.com/kaizencycle/lab7-proof"},
  "openapi": "/openapi.json",
  "health": "/healthz",
  "atlas": { "audit": "/api/atlas/audit" },
  "capsules": "/api/atlas/capsules",
  "gi_policy": {"threshold": 0.95}
}
```

## 8) Security & Policy
- All POSTs must include:
  - `X-GI-Score`: >= policy.threshold
  - `X-Sig`: ed25519(base64url) over request body
  - `X-Key-Id`: did:web:<domain>#owner
- Citizen Shield enforces:
  - deny on gi < threshold,
  - deny tools not in ruleset,
  - log to ledger for every accept/deny.

## 9) Rollout Plan
1. **Phase A (Lab7)**
   - Implement routes above (FastAPI/Flask).
   - Publish `/.civic/atlas.manifest.json`.
   - Wire @civic/oaa-memory capsule verify.
2. **Phase B (Lab4, Lab6)**
   - Expose their manifests; add health → ATLAS.
3. **Phase C (Ledger)**
   - Persist audit + attest entries with Merkle linkage.
4. **Phase D (CI/CD)**
   - In GitHub Actions: call `/api/atlas/verify` pre-deploy.
   - Fail build if gi < threshold or verify fails.

## 10) Acceptance Criteria
- `GET /api/atlas/audit` returns 200 with non-empty services list.
- `POST /api/atlas/capsules/verify` accepts a signed sample capsule and returns `{ok:true}`.
- GI gate rejects a request with gi < threshold.
- A ledger ref is created for each accepted attestation.

## 11) Metrics
- `atlas_gi_current`, `atlas_gi_min`, `atlas_errors_total`,
- `capsules_verified_total`, `attests_accepted_total`,
- P95 latency for `/api/atlas/*`.

## 12) Failure Modes & Mitigations
- Drift between services → ZEUS triggers quorum; ATLAS returns degraded.
- Signature mismatch → deny + ledger alert via HERMES.
- Ledger write outage → queue attestations; mark audit pending-ledger.

## 13) Open Questions
- Should ATLAS also mint a daily organization capsule automatically at clock-out?
- Do we require dual signatures (JADE+EVE) on all attest writes?
- Versioning: pin capsule.schema to v1 or allow negotiated minor updates?

---

## Appendix A — Sample FastAPI routes (Lab7)

```python
# app/routes/atlas.py
from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timezone
from oaa_memory import verify_capsule  # wrapper for @civic/oaa-memory

router = APIRouter(prefix="/api/atlas", tags=["atlas"])

GI_MIN = 0.95

@router.get("/audit")
def audit():
    return {
        "cycle": "C-109",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gi_score": 0.972,
        "virtue_accords": ["Virtue Accord v1","Yautja Kernel v1"],
        "services": [
            {"name":"lab7-oaa","status":"healthy","version":"1.3.2","hash":"b665ba8"}
        ],
        "ledger_ref": "ledger://atlas/audit/pending",
        "capsules_latest": []
    }

@router.post("/capsules/verify")
def capsules_verify(capsule: dict):
    v = verify_capsule(capsule, min_gi=GI_MIN, require_signers=["OWNER"])
    if not v["ok"]:
        raise HTTPException(status_code=400, detail=v["errors"])
    return {"ok": True, "errors": []}
```

### Smoke test

```bash
curl -s http://localhost:8000/api/atlas/audit | jq .
```

---

**Decision accepted.** Proceed with Phase A in Lab7 and open tracking issue:
CIVIC-OS#ADR-001: Implement ATLAS endpoints + manifests + CI gate.