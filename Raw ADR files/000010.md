# 2. Use Pull Requests and ADRs for Async Decision Making

Date: 2023-03-23

## Status

Accepted

Amends [1. Record architecture decisions](0001-record-architecture-decisions.md)

## Context

The community expressed the problem of not understanding some past decisions and the need of a scalable communication pattern. In this RFC we offer an initial process and structure that we can improve. We will not go into details like how the content is styled or written.   
The design must consider the followings:
- the community members are from different companies, countries and even time zones
- the design should not hinder the thinking and collaboration process

## Decision

- We will use ADR pull requests (PR) similar to an RFC process to collaborate on a architecture decision or design.
- We will define guidelines in addition to existing ones mentioned in [1. Record architecture decisions](0001-record-architecture-decisions.md) 

### Format of an ADR

- The title must be in imperative form. e.g.:
    - Use Lit to develop the OpenSCD
    - Avoid JavaScript
    - Deploy to Github Pages
- An ADR must have one of the following status:
  - `Accepted`: the decision has been accepted
  - `Superseded by [XY]`: the decision has been overwritten by another one
- An ADR can have additional status information:
  - `Supersedes [XY]`: in additional to "accepted" we can indicate which previous ADR we
  overwrite, if any
  - `Amends [XY]` / `Amended by [XY]`: A decision can have additional information to another one
    > **Note:** We do not have a dedicated `Draft` or `Rejected` status because until 
    > the pull request is not merge the ADR is in draft status and
    > if the pull request is rejected te ADR is also rejected
- An ADR must contain:
  - **Date**: when the decision has been made
  - **Status**: see above
  - **Context**: Describe the context and problem statement, e.g., in free form using two to three sentences or in the form of an illustrative story.
    We recommend to include not just the the goal but also non-goals to make it clear which problems we are solving and which we are not.
  - **Decision**: The decision or approach to solve the problem including diagrams and examples.
  - **Consequences**: What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.
- An ADR can contain:
  - **Options:** A brief list of considered options.
  - **Option Details:** If it is necessary to go into details of some or each options do it in a different sections in order to keep the glanceability of options.
  - **Validation:** You can include ways to validate and test if the design worked as intended.
  - **More Information:** Any more sections and information you think is needed to provide for a better understanding.


ADR Template:
```txt
# X. <Title>

Date: yyyy-MM-dd

## Status

{Accepted | Superseded by [XY]}
{Supersedes [XY] | Amends [XY] | Amends by [XY]}

## Context

The issue motivating this decision, and any context that influences or constrains the decision.

## Decision

The change that we're proposing or have agreed to implement.

## Consequences

What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.

```


### Format of the Pull Request

- The title must be the title of the ADR prefixed with `ADR: `. e.g.:
  - ADR: Use Lit to develop OpenSCD
  - ADR: Avoid JavaScript
  - ADR: Deploy to Github Pages
  > **Note:** This helps to easily separate ADR pull request from normal ones
- The description of the pull request must contain:
  - A link or links to the rendered files
- The description of the pull request can contain:
  - **Target Review Date**: We would like to decide latest until this date. Format: `yyyy-MM-dd`; e.g.: 2023-03-08
  - **Questions:** You can already include questions and draw the reviewers attention to some point you need more feedback about


## Prior Art
- [Squarespace's RFC ↗](https://static1.squarespace.com/static/56ab961ecbced617ccd2461e/t/5d792e5a4dac4074658ce64b/1568222810968/Squarespace+RFC+Template.pdf)   
- [GitHub's MADR ↗](https://github.com/adr/madr/blob/main/docs/decisions/adr-template.md)   
- [A Structured RFC Process ](https://philcalcado.com/2018/11/19/a_structured_rfc_process.html)↗   


## Consequences

With the pull request and ADRs we will increase the understating of decisions 
and make the decision process more transparent and async. With this we hope
to include more members of the community.