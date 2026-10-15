# Change completionMethod to an Array for Flexible Task Closure

## Decision Group

TD - Technology Decision

Proposed | 2024-10-29

## Problem/Issue

The current implementation of `bienoblige:completionMethod` allows only a single value, limiting the flexibility in defining how a task can be considered complete. This results in the need for combination statuses like `bienoblige:ExpiredOrAllChildrenCompleted`, which complicates the system and could lead to a combinatorial explosion of such statuses.

## Decision

To enhance flexibility and reduce complexity, we have decided to change the `bienoblige:completionMethod` to an array. This will allow multiple completion methods to be specified for a single task. Additionally, we will introduce a new completion option, `bienOblige:ParentCompleted`, to facilitate the automatic closure of child tasks when their parent task is closed.

## Considered Alternatives

* Maintaining the current single-value implementation.
* Creating more combination statuses to cover new closure scenarios.
* Implementing a separate configuration outside of `bienoblige:completionMethod` to handle complex closure conditions.

## Arguments

### Pro

* *Increased Flexibility*: Allows for specifying multiple ways a task can be completed without needing to predefine combinations.
* *Simplicity and Clarity*: Eliminates the need for combination statuses, making the system easier to understand and work with.
* *Extensibility*: New completion methods can easily be added in the future as new requirements arise.
* *Enhanced Task Hierarchy Management*: The `bienOblige:ParentCompleted` option simplifies the management of parent-child task relationships.

### Con

* *Implementation Complexity*: The logic to evaluate multiple completion methods may be more complex.
* *Potential for Conflicts*: There might be scenarios where multiple specified completion methods conflict with each other.
* *User and Developer Training*: Updating documentation and training users and developers on the new system might require additional effort.

## Related decisions

N/A

## Extends

N/A

## Related requirements

N/A
