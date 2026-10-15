---
ADR: 0001
author: matmair
status: "proposed"
created: "2025-04-21"
decided: "2025-10-23"
date: "2025-10-23"
type: "governance"
---

# Use Markdown Architectural Decision Records

{adr}`-`

## Context and Problem Statement

We want to record architectural decisions made in this project independent whether decisions concern the architecture ("architectural decision record"), the code, the design, the governance of the project, the ecosystem or other fields.
Which format and structure should these records follow?

## Considered Options

* [MADR](https://adr.github.io/madr/) 4.0.0 – The Markdown Architectural Decision Records
* IEEE 42010 – Recommended Practice for Architectural Description of Software-Intensive Systems
* Y-Statements

## Decision Outcome

Chosen option: "MADR 4.0.0", because

* Implicit assumptions should be made explicit.
  Design documentation is important to enable people understanding the decisions later on.
  See also ["A rational design process: How and why to fake it"](https://doi.org/10.1109/TSE.1986.6312940).
* The MADR format is lean and fits our general docs style.
* MADR seems to have wide(ish) adoption

The fontmatter header is adjusted similar to [DEPs](https://github.com/django/deps).

## Structure

Decision records should be stored in the `docs/adr` directory.
The file name should be the decision number and a short description of the decision.
The file name should be in lowercase and use hyphens to separate words.
The file name should not contain spaces or special characters.

In the header of the file should be frontmatter with the following fields.

| Name    | Options | Description |
| -------- | ------- | ----------- |
| ADR  | number of the {term}`ADR`, e.g., 0001 | The number of the ADR. This should be a unique number for each ADR. |
| author  | GitHub user name | The author of the ADR. This should be a reference to the author, e.g., the name and GitHub user name. |
| status  | proposed, rejected, accepted, deprecated, superseded by ADR-*** | The status of the ADR. See the details [below](#status-lifecycle) |
| created | YYYY-MM-DD | The date when the ADR was proposed. This should be in ISO 8601 format |
| decided | YYYY-MM-DD | The date when the ADR was decided on. This should be in ISO 8601 format. |
| date    | YYYY-MM-DD | The date when the ADR was last updated. This should be in ISO 8601 format. |
| type    | architecture, design, code, governance, ecosystem | The type of the ADR. This should be a short description of the type of the ADR. |

### Status Lifecycle

| Status    | Description |
| --------- | ----------- |
| proposed  | The ADR is proposed and not yet accepted. |
| accepted  | The ADR is accepted and implemented. |
| rejected  | The ADR is rejected and not implemented. |
| deprecated | The ADR is deprecated and not implemented. |
| superseded by ADR-*** | The ADR is superseded by another ADR. This should be a reference to the other ADR. |

### Types

| Type        | Description |
| ----------- | ----------- |
| architecture | The ADR is an architectural decision. This might be related to deployment, general components or intended usage |
| design      | The ADR is a design decision. This relates to the appearance and UX of InvenTree components |
| code        | The ADR is a code decision. This regards specific programming patterns or style decisions |
| governance  | The ADR is a governance decision. This regards how project internal processes work |
| ecosystem   | The ADR is an ecosystem decision. |
