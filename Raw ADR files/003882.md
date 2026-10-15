# ADR-0001: Offline-by-default and non-OCR PDF policy

- **Status**: Accepted
- **Date**: 2025-10-02
- **Authors**: Core maintainers
- **Related docs**: Project Brief (scope/DoD), Product Context (purpose/problems/personas)

## Context

The v0.1.0 release must be:

- **Private and predictable** for job seekers running the agent locally (no data egress).
- **Deterministic and testable**, enabling stable CI and reproducible results.
- **Lightweight**, avoiding heavy dependencies (GPU/large models/complex pipelines).

Typical JDs arrive as `.txt` or `.pdf`. Some PDFs are **text-based** (selectable/copiable text), others are **scanned images** (require OCR). Supporting OCR early would add dependencies, complexity, and potential accuracy noise that hurt the initial reliability.

## Decision

1. **Offline by default**

   - The CLI runs without network calls.
   - No external services or telemetry are contacted by default.
   - Minimal local logs are kept in `memory/log.json`.

2. **PDFs must contain selectable text**

   - v0.1.0 accepts `.txt` and **text-extractable** `.pdf`.
   - **Scanned PDFs (image-only)** are **not supported** in this version.

3. **Clear error messages and guidance**

   - If a PDF has no extractable text, the agent returns:
     `ERROR: Could not extract text from PDF (page X).`
     Guidance: “Provide a native/text PDF or export the JD as `.txt`.”

4. **User-facing documentation**

   - README and Project Brief explain the offline default and the non-OCR constraint.
   - Product Context clarifies why this constraint exists (privacy, simplicity, reliability).

5. **Future opt-ins (not implemented in v0.1.0)**
   - We may add **explicit flags** to enable network features (e.g., `--enable-network`) and/or OCR (`--enable-ocr`) in later versions, behind clear consent and separate dependencies.

## Consequences

### Positive

- **Privacy by design**: no unintentional data egress.
- **Determinism**: simpler tests and reproducible outcomes.
- **Lower complexity**: faster onboarding and smaller footprint.
- **Clear UX**: users know upfront what works and what doesn’t.

### Negative

- **No OCR**: scanned PDFs are rejected; users must convert to `.txt` or provide a native/text PDF.
- **No online augmentation**: cannot enrich or validate content with external services by default.

## Alternatives considered

- **Always-online mode** (LLM or web APIs): rejected for privacy, cost, and determinism concerns in v0.1.0.
- **Bundled OCR (e.g., Tesseract/PaddleOCR)**: postponed; increases dependencies, adds noise and non-determinism.
- **Hybrid default (online when available)**: rejected; implicit network access can surprise users and complicate testing.

## Scope

- Applies to **v0.1.0** and any minor updates until an explicit ADR revises this policy.
- Affects CLI behavior, error messaging, docs, and tests.

## Implementation notes (v0.1.0)

- **CLI flags**: `--jd`, `--profile`, `--out`, `--verbose` (no network/OCR flags yet).
- **PDF parsing**: use a text-extraction library; if extraction fails, emit the standard error and exit with code `1`.
- **Logging**: append minimal run metadata to `memory/log.json` (timestamp, input types, outcome).
- **Docs**: Project Brief → "Assumptions & constraints"; README → "Supported formats" and "Limitations".

## Testing & metrics

- Unit tests for:
  - `.txt` JD path (happy path).
  - `.pdf` with real text (happy path).
  - `.pdf` scanned/image-only (asserts the expected error).
- Track (locally, anonymized):
  - Time-to-result (TTR).
  - PDF extraction error rate.

## Security & privacy

- Offline by default ensures **no JD/profile leaves the user’s machine**.
- No telemetry or remote calls without explicit future opt-in.

## Backwards compatibility

- Future additions (OCR or network) must be **opt-in** and keep offline mode as the default.
- Changing the default (e.g., to online) requires a new ADR and a major/minor version bump as appropriate.

## Review / When to revisit

Revisit this ADR if:

- Mais que 20% of reported PDFs fail due to non-text content (sustained signal).
- Community requests strongly favor OCR or online augmentation.
- We introduce an **experimental** `--enable-ocr` or `--enable-network` feature.
