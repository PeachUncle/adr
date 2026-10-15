# Test 2 scoring approach
Date: 2025-03-10

## Context
Long-form architecture submissions for test 2 are graded by Certifiable Inc. These are substantial documents
containing a mix of textual and diagrammatic content.

This ADR considers different approaches that can be taken to use AI to grade submissions.  

Consideration is given to:
- Avoiding bias toward answers that are superficially similar
- Ensuring high quality/confidence across a number of different "lenses", or ways of viewing a problem
- Producing an output that minimises human effort in digesting/integrating inputs to final scoring
- Providing meaningful feedback to submitters beyond just a score

## Decision
The option to grade from different viewpoints has been chosen, providing discrete areas
of scoring. Detail can be found in section 2 below.

## Options Considered

Different options are considered.  In addition to the details given each of the
options also include the following:

- All scores are accompanied by the rationale for that score
- LLMs scoring submissions are furnished with general details outlining industry best software architecture practices
- A random sample of gradings are also reviewed by experts, to verify that the scoring process is functioning correctly
- Technological difficulties in grading mixed-media submissions are addressed by requesting that diagrams are submitted using diagram-as-code
compatible formats such as Mermaid

1. Similarity to ‘known good’ submissions

Submissions are compared to a body of expert-selected, high scoring previous submissions for this case study and scored for similarity. An answer that is very similar to previously scored 'known good' answers will be graded more highly than an answer that shares little similarity.

### Indicative prompt

```
Grade the following architecture for a <use case summary> for similarity to these architectures. ...
```

### Pros

- Transparent grading process
- Having only one scoring process provides a single point of maintenance/modification - fewer moving parts etc.

### Cons

Risk of bias toward irrelevant factors.  For example - if most architectures use, say, an AWS platform, the scoring could prejudice submissions 
using a different platform such as GCP.

2. Grading from different viewpoints

Models grade submissions from a series of points of view, which are then combined to form an overall score.

### Indicative prompt

```
Grade the following architecture from the point of view of <role>: ...
```

`<Role>` being an iteration of, for example:
- A security expert, looking for minimal threat surface for attacks, reduced likelihood of over-permissioning users, etc
- A software engineer tasked with implementing the system, looking for inconsistencies or ambiguities.
- A commercial stakeholder, looking for financial regulatory compliance consideration - privacy, tipping-off, accessibility etc.
- A product expert, looking to ensure the architecture can support the functional requirements specified

### Pros

- Each grading module has a single responsibility
- Bias is reduced as it is not assessing based on similarity to other successful submissions, however carefully chosen to represent a range of approaches
- Gradings are easier to explain because they relate to discrete areas of concern
- The individual viewpoints are tweakable independently [1]
- Allows different weightings to be applied to different viewpoints, based on the particular case study [2]

[1] For example, if a prominent new piece of data privacy legislation was introduced (GDPR 2? god help us), that particular agent could be the target for the updates instead of a monolithic system

[2] For example, an architecture that targets a POC might have a lower bar for an infra/devops expert than a 24x7, high volume app architecture - and scoring should factor in the relative importance of each viewpoint to the overall solution.

### Cons

As the submission and the supporting information are are processed for each viewpoint, 5 viewpoints would result in approximately  5 times the number of tokens processed, so may have a cost implication

## Consequences

The grading from multiple points of view makes the grading process easier to review and allows for a more heterogenous set of accepted answers.

### Risks

The approach is still not foolproof against marking-down innovative solutions, grading context should include clauses to identify controversial choices that are well explained and flag these for human review.
