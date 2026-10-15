# ADR 0002: Reframe ADF as a Vendor-Neutral Methodology

- Status: Accepted
- Date: 2025-10-04
- Update (2025-10-04): Spec v0.3.0 transitions to Delivery Lead / Product Owner / Developers vocabulary while keeping this ADR for history.

## Context

The initial ADF documentation emphasized GitHub-specific services (Projects, Codespaces, Copilot Code Review, CodeQL). Organizations requested guidance that preserved governance while allowing alternative platforms. To grow adoption, we need a neutral methodology specification with optional platform mappings.

## Decision

- Reposition ADF as a vendor-neutral methodology with the Delivery Lead, Product Owner, and Developers accountabilities as the neutral core.
- Introduce [conformance.md](../conformance.md) to define L1–L3 requirements using RFC 2119/8174 language.
- Create [profiles/overview.md](../profiles/overview.md) and profile directories to map neutral terminology to specific platforms (initially GitHub).
- Preserve historical documents and diagrams while adding neutral equivalents.
- Link platform implementations (e.g., `adf-github-suite`) separately from the core methodology.

## Alternatives Considered

1. **Maintain GitHub-only framing** — rejected because it limits enterprise adoption and complicates cross-platform governance.
2. **Fork into platform-specific repos without a central methodology** — rejected because it fragments guidance and obscures shared principles.
3. **Abstract terminology without profiles** — rejected because practitioners still need concrete mappings to execute.

## Consequences

- Documentation now distinguishes between normative methodology content and informative platform profiles.
- Future platform support can iterate independently via profiles and RFCs.
- Contributors must follow the governance + RFC process when proposing normative updates or new profiles.
- Implementations reference companion repositories instead of embedding vendor-specific automation in the spec.

---

This work is licensed under CC BY-SA 4.0.
