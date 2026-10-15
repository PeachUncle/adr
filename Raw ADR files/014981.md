
# ADR-0: The ADR Process

## Status

**Status:** Active

**Proposed by:** Michalis Bogdanos

**Authored by:** Michalis Bogdanos

## Context

_What is the issue that we're seeing that is motivating this decision or change?_ 

With this record, I'm establishing the ADR process. 

Inspired by the material at https://github.com/joelparkerhenderson/architecture-decision-record.  

## Decision

_What is the change that we're proposing and/or doing?_ 

This initial record defines the format of each ADR and the process of establishing and updating them.

The valid statuses are:
- `In review`
- `Active`
- `Superseded`

A new ADR starts with the `In review` status, when it is committed. 

The code is `ADR-X` where `X` is the number of the previous `Active` ADR, incremented by 1.

If it is declined during the review process, the PR shall be declined. This means that declined ADRs shall not make it 
into the main development branch. 

If it is accepted during the review process, the status must be updated to `Active` and the PR shall be merged. 

`Active` ADRs can be superseded by newer ADRs. In this case, the status shall be updated on the same PR where the new 
ADR is set in effect. A `Superseded` ADR shall mention which ADR supersedes it. The superseding ADR must also mention 
the superseded ADR. Those mentions are done using only the ADR code. 
No other updates are allowed on `Active` ADRs. 

Ideally, the author(s) should be different from the people who proposed an ADR.
This implies that at least two people must be involved in the preparation of any ADR, before it reaches the review 
step. The proposing person pitches the idea and the author evaluates and writes it down.

## Consequences

_What becomes easier or more difficult to do because of this change?_

Having ADRs helps establish well-documented architecture and implementation decisions. 
This can be extended to include other areas like the development process. 
There will be a standard way of presenting and documenting all this information.

### Pros 

_List the advantages of the decision here._

- You can track all decisions within the repository. 
- Standardised documentation.

### Cons

_List the disadvantages of the decision here._

- More text!
