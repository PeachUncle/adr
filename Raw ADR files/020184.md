# ADR 001: Decision to Use Nygard-style ADRs

## Status

Accepted

## Context

This project is a new initiative and is intended to serve as a reference for other teams and projects in the future. Given this purpose, it is critical that we document our architectural decisions from the very beginning. By doing so, we not only ensure that future contributors can understand the rationale behind our decisions but also provide a living blueprint of how decisions should be approached for similar projects.

For this reason, we are adopting Architecture Decision Records (ADRs) in the style outlined by Michael Nygard. Nygaard's ADRs offer a simple and effective method for recording key architectural choices, focusing on capturing the *why* of each decision, not just the *what*. This aligns perfectly with the needs of a reference project, where clarity, rationale, and future-proofing are essential from the outset.

### Why Start ADRs Immediately

1. **Foundation for Reference**: As a reference project, we are creating patterns for others to follow. Recording decisions as they happen will offer a transparent view into the architectural thinking behind this system, enabling other teams to make informed decisions or adapt our rationale to their context.

2. **Prevent Future Gaps**: Architectural decisions made early in a project are often the most impactful. Starting ADRs immediately ensures we do not miss documenting critical decisions that set the direction for the system’s evolution.

3. **Consistency**: This project will likely serve as a base for many other teams. ADRs will help us create a clear and consistent structure for how decisions are made and documented across multiple teams and systems, setting a high standard for future projects.

### Nygard's Arguments

Michael Nygard advocates for ADRs for several reasons, all of which apply here:

- **Preserve Decision Rationale**: The reasons for choosing a particular approach are easily lost over time, but ADRs capture this rationale so that future team members—or in this case, other teams—can understand the thinking behind key choices.

- **Enable Architectural Evolution**: Systems evolve, and ADRs serve as a log of architectural decisions that can be reviewed and updated as the project changes, ensuring the architecture grows in a coherent and intentional way.

- **Promote Transparency and Accountability**: By clearly documenting decisions, the team fosters a sense of accountability. Everyone understands the reasoning and has a reference for future improvements or adjustments.

In his original Cognitect article where he introduced ADRs, Nygard emphasized how lightweight but structured records can prevent architectural "drift" and confusion. You can read the article here: [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) to understand the full rationale behind this practice.

## Decision

We will use Nygaard-style ADRs from the very beginning of this project to document all major architectural decisions. These will:
- Be uniquely numbered and stored in a dedicated `docs/decisions/` directory within the repository.
- Follow a clear structure with sections for Context, Decision, and Consequences.
- Remain concise, focusing on capturing the decision rationale rather than excessive detail.

## Consequences

- **Positive**:
	- We will establish a clear record of architectural decisions that can serve as a reference for future contributors and other projects.
	- New team members will be able to quickly onboard by reviewing the decisions and their rationale.
	- The project will remain consistent in its architecture, reducing the risk of unnecessary rewrites or architectural drift.

- **Negative**:
	- There will be an initial overhead in creating and maintaining ADRs, but this is balanced by the long-term value they provide.

- **Unknowns**:
	- It remains to be seen how often ADRs will need to be revisited or updated as the project evolves.
