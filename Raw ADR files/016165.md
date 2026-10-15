# Use Architectural Decision Records

## Context
In the course of developing an application it is common for certain architectural decisions to be made. Historically, these decisions are transferred by word of mouth or kept in a document store, like Confluence, for example. However, in either case the decisions are either hard to find or completely lost to time.

## Decision
We will use the Lightweight Architectural Decision Records (ADRs) as recommended by [ThoughtWorks](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records) and defined by Michael Nygard in [Documenting Architecture Decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions). However, in addition to using the standard sections (_Context, Decision, Status_ and _Consequences_),  we will also make use of a _Rationale_ section as advocated by [Paulo Merson](https://github.com/pmerson/ADR-template) in order to better capture the all important "why?" that drove the decision.

All ADRs will be stored in the /documentation/adr directory of the project's source. The ADRs will be named adr-`number`-`title`.md, where `number` is a four digit sequential number showing the order of decisions and `title` is a hyphenated title of the decision. ADRs will be written in Markdown, following the same format of this document and as described in the links above.

ADRs will start with the status of `Proposed` and moved to `Accepted` once the stakeholders agree on the decision. If an ADR is no longer valid because of follow-up decisions and findings, the status will be changed to `Deprecated`. If it needs to be replaced by a newer decision, the status will be changed to `Superseded` and its body will contain a link to the ADR that replaces it. ADRs that superseded an existing ADR will also contain links back to the ADRs it replaces.

## Rationale
- ADRs are a standard way of documenting significant decisions in the project's source, making them highly accessible in the very context where they have the most relevance.
- ADRs encourage brevity without sacrificing meaningful content.
- ADRs have a level of simplicity that makes them easy to write in a small amount of time and easy to consume.
- ADRs provide enough structure to encourage consistency while being flexible enough to address all cases.

## Status
**Accepted**

## Consequences
- Developers can efficiently reference an historical record of decisions, answering questions about _why_ things were done in a particular way.
- Developers can augment the historical record with little effort.

However...
- ADRs don't solve the problem of recognizing _when_ to add an ADR.
- Since ADRs are not working code, they can too easily be sacrificed to save time, diminishing the value of the historical record.
- Our ADRs are available to a narrow audience. Michael Nygard says that ADRs should be accessible to an audience that includes "project managers, client stakeholders, and others who don't live in version control like the development team does." But this can be resolved by developing a way to display ADRs along with any other documentation in UI Applications of one kind or another, be it a new EMR, new Housekeeping or something else.
