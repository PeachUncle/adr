<!-- Intent: Record terminology alignment decisions from early iterations so documentation and code use the same vocabulary. -->

# ADR-0002: Terminology Alignment for Capture and Organization

**Status:** Accepted  
**Date:** 2026-01-03  
**Deciders:** Will Conklin  
**Tags:** terminology, product, documentation

## Context

Early prototypes and documentation used multiple names for the same concepts (for example, `Thought`, `BrainDumpEntry`, and `CaptureEntry` were all referenced at different times). As the event-sourced capture model solidified, we introduced clearer responsibilities—capture, hand-off, suggestion, placement—but legacy terms remain in some notes and copy. We need a single vocabulary to reduce confusion during development, onboarding, and future migrations.

## Decision

Adopt the following canonical terms and phase out legacy names:

| Canonical term | Replaces | Rationale |
| --- | --- | --- |
| `CaptureEntry` | `Thought`, `BrainDumpEntry` | Aligns with “capture first” positioning and matches the SwiftData model that stores raw input. |
| `HandOffRequest` / `HandOffRun` | Early “AI request”/“AI attempt” phrasing | Distinguishes user intent (request) from execution attempts (runs) in the workflow. |
| `Suggestion` / `SuggestionDecision` | “AI proposal” / “acceptance” | Clarifies that AI output is advisory and that user responses are explicit decisions. |
| `Placement` | “Result mapping” / “destination record” | Represents where accepted suggestions land without overloading “result” terminology. |
| `Plan` | `Project` | Better reflects lightweight planning over heavyweight project management. |
| `ListEntity` / `ListItem` | Generic “List” / `Item` | Avoids ambiguity with SwiftUI Lists and conveys hierarchy between container and entry. |
| `CommunicationItem` | N/A (kept) | Name already matches its purpose (calls, emails, messages). |

Unchanged terms retained for consistency and completeness:

| Canonical term | Current usage | Rationale |
| --- | --- | --- |
| `Category` | Stable | Describes lightweight grouping for tasks; no conflicting aliases observed. |
| `Tag` | Stable | Common, user-friendly label semantics that align with many productivity tools. |
| `Task` | Stable | Represents actionable items; already aligned with capture-first language. |
| `VoiceRecordingService` | Stable | Accurately reflects responsibility for capture via audio; no competing names. |
| `CaptureWorkflowService` | Stable | Matches the workflow orchestration role already referenced across docs. |

Removed terms and concepts to avoid going forward:

| Deprecated term | Replacement | Rationale |
| --- | --- | --- |
| `Inbox` (as a destination or view name) | Use workflow states: capture → hand-off → decision → placement; present surfaced tasks by plan/tag/category instead of a generic inbox | The event-sourced flow already captures newly created items; an “inbox” label conflicts with the structured placement narrative and should be removed from code and copy. |
| `BrainDump` prefixes (e.g., `BrainDumpEntry`) | `CaptureEntry` | Consolidated to a single capture model; avoid mixed naming and ensure migrations map old references when encountered. |
| `Project` (for destination) | `Plan` | Aligns with lightweight planning semantics and avoids heavyweight project-management connotations. |
| Generic `List`/`Item` names | `ListEntity` / `ListItem` | Prevents confusion with SwiftUI `List` and clarifies hierarchy. |

## Consequences

- All future documentation, UI copy, and schema discussions should use the canonical names above; legacy terms should be treated as deprecated.
- When touching files that still reference legacy names, prefer renaming to the canonical vocabulary unless backward compatibility is required for migrations.
- New diagrams and architectural docs should keep capture → hand-off → suggestion → decision → placement as the workflow narrative.

## Alternatives Considered

- **Keep mixed terminology in early docs.** Rejected because it slows onboarding and introduces ambiguity when mapping UI copy to models.  
- **Adopt “Brain Dump” naming everywhere.** Rejected to avoid framing the product around a single capture mode and to keep language neutral for future non-brain-dump entry points.

## Implementation Notes

- Update onboarding, UI strings, and code comments opportunistically to remove legacy names.
- For migrations, treat any persisted `Thought`/`Project` references as legacy aliases for `CaptureEntry` and `Plan` respectively when encountered.
