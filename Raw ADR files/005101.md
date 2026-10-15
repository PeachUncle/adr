# ADR 0003: Delivery Pulse, Story Preview, and Pulse Increment

- Status: Accepted (spec v0.3.0 / naming v0.0.3)
- Date: 2025-10-04

## Context

Earlier documentation referenced a daily cadence focused solely on merge-ready increments. Enterprises adopting agentic teams asked for:
- Automation-aware language that still maps to Scrum.
- Clear expectations for per-story demos before marking work Done.
- Alignment of change request gates with performance guardrails.

## Decision

1. **Adopt Delivery Pulse as the daily cadence.**
   - Automated overnight pulse generates summaries, runs tests/scans, and prepares a Pulse Increment demo build.
   - Human sync (10–15 minutes) inspects the automated output, surfaces impediments, and agrees on next steps.
2. **Introduce Story Preview artifact.**
   - Every Story requires a runnable demo (preview environment or local recipe) and evidence (tests, scans, rollback notes) before it can be marked Done.
   - Story Preview lives with the Change Request so reviewers—human or AI—can inspect it asynchronously.
3. **Introduce Pulse Increment artifact.**
   - Daily aggregate demo build of merged, green work. Prefer automated publication ahead of the human Delivery Pulse.
   - Serves as the baseline for transparency, stakeholder updates, and early regression detection.
4. **Add Performance Budget and WIP Limits guidance.**
   - Performance-sensitive changes MUST show they respect agreed budgets at CR/DoD gates.
   - Organizations SHOULD define WIP limits (e.g., ≤3 active stories per team/agent) to maintain flow.

## Consequences

- Repo-wide vocabulary now references Delivery Lead, Delivery Pulse, Story Preview, and Pulse Increment.
- Conformance levels include evidence for Story Previews and Pulse Increments.
- Templates and checklists call out Performance Budget verification and WIP policy knobs.
- Historical references remain only in archived specs.

## Related Documents

- [Spec v0.3.0](../specs/spec.v0.3.0.md)
- [Enterprise-friendly naming v0.0.3](../naming/enterprise-friendly-naming.v0.0.3.md)
- [Conformance](../conformance.md)

---

This work is licensed under CC BY-SA 4.0.
