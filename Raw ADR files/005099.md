# ADR 0001: Planning & Delivery Flow (Delivery Lead + Developers)

- Status: Accepted (updated terminology in spec v0.3.0)
- Earlier vocabulary is preserved in archived documents; current work uses the Delivery Lead, Product Owner, and Developers terminology throughout.

## Context

Repository renamed from `airnub/agentic-agile` to `airnub/agentic-delivery-framework` to emphasize a vendor-neutral methodology. We still need safe, auditable agentic development that maps onto Sprints, keeps execution inside governed workspace runtimes, and aligns with enterprise governance.

## Decision

Adopt a **planning & delivery flow** architecture anchored by Delivery Lead, Product Owner, and Developers:

- **Delivery Lead** operates outside the workspace runtime, steers Sprint events (Planning, Delivery Pulse, Review, Retro), manages workspace runtime lifecycle, and enforces CR-first governance including Performance Budget checks when applicable.
- **Product Owner** maintains the Product Goal and Product Backlog, collaborates on Story Previews, and accepts outcomes during Sprint Review.
- **Developers** work inside the workspace runtime to implement Stories via Change Requests. They produce Story Previews before a Story is marked Done and contribute to the daily Pulse Increment.
- **Change Request Gates** provide layered assurance: CI/tests, QA verification, security review, automated review, required human approvals, and Performance Budget verification before merge.

## Diagrams
- Historical diagrams: [Mermaid overview flow (GitHub-centric)](../profiles/github/adf-overview-flow.mmd), [Mermaid sequence (GitHub-centric)](../profiles/github/adf-sequence.mmd).
- Neutral diagrams (preferred): [Mermaid overview flow](../diagrams/adf-overview-neutral.mmd), [Mermaid planning & delivery sequence](../diagrams/adf-sequence-neutral.mmd).

```mermaid
sequenceDiagram
  %% Agentic Delivery Framework — Planning & Delivery Sequence (Neutral)
  participant DL as Delivery Lead (outside runtime)
  participant PO as Product Owner
  participant WM as Work Management System (Sprint)
  participant WR as Workspace Runtime
  participant DEV as Developers (workspace)
  participant CRG as Change Request Gates

  DL->>WM: Facilitate Sprint Planning & set Sprint Goal
  PO->>WM: Order PBIs for Sprint Backlog
  DL->>WR: Create/Resume Workspace Runtime (warm starts, secrets)
  DL->>DEV: Brief Developers; confirm WIP limits & DoD
  DEV->>WR: git switch -c feat/&lt;story&gt;
  DEV->>CRG: Open Change Request ("Closes &lt;story&gt;") with Story Preview
  CRG->>CRG: CI/Tests | QA | Security | Automated | Human | Performance Budget
  alt All gates pass
    CRG->>WR: Merge to protected branch (Increment meets DoD)
    DL->>WM: Update Sprint board & telemetry
  else Any gate fails
    CRG->>DEV: Feedback & failing checks
    DEV->>WR: Iterate fixes on branch
  end
  DL->>DEV: Delivery Pulse — review Pulse Increment & next actions
  DL->>WM: Sprint Review & plan next Sprint
```

_Figure: Sequence diagram documents how the Delivery Lead, Product Owner, and Developers collaborate through Story Previews, Pulse Increment, and CR gates._

## Alternatives Considered

- **Managed cloud agents** (single-vendor IDEs or hosted sandboxes): faster to start, but limited environment control, portability, and governance alignment.
- **Local developer machines**: unsafe and non-reproducible for autonomous edits.
- **Single big agent run (waterfall)**: poor feedback loops; hard to govern or apply WIP limits.

## Consequences

- **Pros**: safety (no unmanaged edits), transparent Story Previews and Pulse Increments, governance through change request gates, model choice via open APIs, reproducible environments, enterprise naming alignment.
- **Cons**: orchestration costs (workspace runtime minutes, warm starts, secrets). Mitigate with idle shutdowns, budgets, telemetry, and Delivery Pulse inspections per [Conformance L3](../conformance.md).

---

This work is licensed under CC BY-SA 4.0.
