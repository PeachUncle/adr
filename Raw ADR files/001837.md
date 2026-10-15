---
# Configuration for the Jekyll template "Just the Docs"
parent: Decisions
nav_order: 100
title: ADR-002-Indentity Framework Adoption
# These are optional elements. Feel free to remove any of them.
status: proposed
date: 2025-10-12
decision-makers: Peter Carroll
# consulted: {list everyone whose opinions are sought (typically subject-matter experts); and with whom there is a two-way communication}
# informed: {list everyone who is kept up-to-date on progress; and with whom there is a one-way communication}
has_toc: true
---

<!-- we need to disable MD025, because we use the different heading "ADR Template" in the homepage (see above) than it is foreseen in the template -->
<!-- markdownlint-disable-next-line MD025 -->

**Title:** ADR-002-Identity Framework Adoption  
**Problem:** User Authentication and Authorization  
**Solution:** Microsoft IdentityFrameworkCore

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [{title of option 1}](#title-of-option-1)
  - [{title of other option}](#title-of-other-option)
- [More Information](#more-information)

## Context and Problem Statement

The application needs to provide a framework to authenticate users and also through the use of Roles, authorize users

<!-- This is an optional element. Feel free to remove. -->

## Decision Drivers

- Security
- Solid solution to security
- Roles

## Considered Options

- IdentityFrameworkCore
- Windows Authentication
- Extenal Providers

## Decision Outcome

Chosen option: IdentityFrameworkCore, because only option, which meets k.o. criterion decision driver.

<!-- This is an optional element. Feel free to remove. -->

### Consequences

- Good, because the framework provides a solid, proven system that fully integrates with AspNetCore applications.
- Bad, because forced database design

<!-- This is an optional element. Feel free to remove. -->

### Confirmation

{Describe how the implementation of/compliance with the ADR can/will be confirmed. Are the design that was decided for and its implementation in line with the decision made? E.g., a design/code review or a test with a library such as ArchUnit can help validate this. Not that although we classify this element as optional, it is included in many ADRs.}

<!-- This is an optional element. Feel free to remove. -->

## Pros and Cons of the Options

### {title of option 1}

<!-- This is an optional element. Feel free to remove. -->

{example | description | pointer to more information | …}

- Good, because {argument a}
- Good, because {argument b}
<!-- use "neutral" if the given argument weights neither for good nor bad -->
- Neutral, because {argument c}
- Bad, because {argument d}
- … <!-- numbers of pros and cons can vary -->

### {title of other option}

{example | description | pointer to more information | …}

- Good, because {argument a}
- Good, because {argument b}
- Neutral, because {argument c}
- Bad, because {argument d}
- …

<!-- This is an optional element. Feel free to remove. -->

## More Information

{You might want to provide additional evidence/confidence for the decision outcome here and/or document the team agreement on the decision and/or define when/how this decision the decision should be realized and if/when it should be re-visited. Links to other decisions and resources might appear here as well.}
