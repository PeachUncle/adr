# ADR-002: Frontend Architecture Design Choice

**Status:** Accepted

**Date:** December 2025

**Last Review Date:** January 2026

## Context

Before starting this project, I had several goals, but one of the main ones was to try as many new technologies, approaches, and architectures as possible (not only on the frontend but also on the backend). Later, through practice, I would learn from my mistakes and, most importantly, draw my own conclusions—invaluable experience that I could experience firsthand, not just read about in articles. Choosing this path, I realized that at some point, I would need to abandon my previous decisions in favor of something more suitable and meaningful.

## What I Tried: FSD

When choosing an architectural approach for the frontend project, I initially had little choice (let's be honest, there aren't many of them). I was already familiar with classic modular architecture, but I was interested in trying out FSD (Feature-Sliced Design). Beyond the hype surrounding this architectural methodology, I was drawn to their ideas for reducing coupling and increasing cohesion by introducing the following rules and concepts:

-   Separating domain entities and features into separate layers;
-   Introducing restrictions related to cross-imports at the layer level;
-   Introducing a public API that would prohibit (accidental) imports into modules that shouldn't use them.

The ideas themselves sound quite interesting on paper. Furthermore, these rules can be controlled at the linter level (which they did), making it easier to avoid accidentally breaking them.
So, without much hesitation, I decided to give it a try. And here's what I ultimately came up with:

1. In practice, this methodology isn't as well implemented as it sounds in theory.
   For example, compared to the Clean Architecture on backend (an implementation I'm not particularly proud of, but that's not the point), I had a lot of questions about FSD, like "Where should I put this code, and what's the best way to organize this feature?". Despite the relatively short set of rules, they don't provide a clear understanding of what should be done and how. Fortunately, FSD has good documentation, with good examples, and, more importantly, an active community that generates a large number of YouTube videos, both from major conferences and from ordinary tech bloggers. Unfortunately, this led to other problems, which are discussed in the points below.

2. (Partial) abandonment of one's own rules to address other methodology issues.
   For example, first we say "we prohibit cross-imports at the layer level," then we say "let's allow them, but only at the entity level." On the one hand, compromises in development are usually normal, and it's simply one of the stages of product development (or methodology, in this case). But on the other hand, what should seemingly be strict and clear (like a clean architecture on the backend) ultimately becomes fuzzy and contradictory. The example above is not the only exception. Then I encountered the fact that by distributing entities and features across layers, I can't use them in just one (!) page, which ultimately reduces everything to a classic modular architecture. It turns out that I was trying to follow one methodology, but relying on its new rules, I followed another. And although I rather like the idea of ​​co-location, what should I do when I have another page with these co-located entities and features? Refactor? If you're writing code alone, remembering everything you've done, and you don't have deadlines, this might work, but not in other cases.

3. If we have a rule that entities and features can only contain reusable code, aren't these layers an additional complexity that the FSD should address? And let's not forget about widgets layer, which are a composite of entities and features. Ultimately, all three layers look like a slightly more structured "common" folder. This is a very rough assumption, but in abstract terms, it looks something like this.

To summarize. Perhaps this structure works well for some specific projects with specific domains, but it seems to me (at least for now, and I might change my mind) that the FSD is a particular type of modular architecture with additional rules (or rather, ideas), some of which are well suited to most projects. But not all.

## What We Learned

From the FSD experiment, we're keeping:

-   Public API pattern (barrel files) for module boundaries
-   Restriction of cross-imports between layers
-   Separation of domain entities from infrastructure code
-   Shared layer for reusable non-business code
-   Co-location principle for page-specific code

We're abandoning:

-   Rigid layer hierarchy (entities/features/widgets)
-   Overly strict import rules that don't fit real-world scenarios

## Decision

We adopt a **custom three-layer architecture** that takes the best ideas from FSD while avoiding its pitfalls:

```
shared → domain → app
```

### Core Principles

-   **SOLID**
-   **Low Coupling and High Cohesion** from GRASP
-   **KISS, DRY, YAGNI** with caveats (e.g., WET code principle from Dan Abramov — don't create abstractions ahead of time)
-   **Co-location:** page-specific code lives with its page
-   **Unidirectional dependencies:** shared → domain → app

### Layer Overview

| Layer     | Purpose                                               | Import Rule                               |
| --------- | ----------------------------------------------------- | ----------------------------------------- |
| `shared/` | Non-business logic (UI-kit, hooks, utils)             | Importable anywhere                       |
| `domain/` | Shareable business logic (entities, state, providers) | Importable in app/, infrastructure, tests |
| `app/`    | Next.js App Router pages with co-located code         | Not importable (except tests)             |

### Enforcement

Import rules are enforced via **dependency-cruiser** in the pre-commit hook, ensuring architectural violations are caught before code is committed.

## Consequences

### Positive

-   Clear, enforceable boundaries between layers
-   Flexibility for page-specific code without over-engineering
-   Familiar modular structure with added discipline

### Negative

-   Requires discipline to decide when code should move from `app/` to `domain/`
-   Custom approach means less community documentation compared to established methodologies

## Related Documents

-   **[Frontend Architectural Design](../architecture/frontend-architectural-design.md)** — Detailed specification of project structure, import rules, and enforcement
-   **[Permission System](../architecture/permission-system.md)** — Permission system architecture
