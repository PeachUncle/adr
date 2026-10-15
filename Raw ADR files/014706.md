# ADR-0027: Non-deterministic Journey Support

## Status

Accepted

Date of decision: 2025-03-20

## Context and Problem Statement

Users of the Private Rented Sector Database will need to complete a range of multi-page forms, like landlord registration 
or compliance. We represent multi-page forms as journeys, with each one consisting of an ordered collection of reachable 
steps. Related steps are grouped into tasks. Step order is determined by a journey's iterator, which uses each step's 
`isSatisfied` and `nextAction` methods to determine what step (if any) comes next. At the moment, journeys can only be 
deterministic, i.e. steps can only be completed in one order (given the user's answers). However, steps that don't depend 
on each other could be completed in any order if we supported non-deterministic journeys.

Should we support non-deterministic journeys and if so, how?

## Considered Options

* Yes, by using DFS to order steps
* Yes, by making tasks iterable
* Yes, by making journeys iterate one task at a time
* No

## Decision Outcome

No, because the product owner has decided that at this time, the benefit of being able to complete multi-page forms in 
different orders isn't worth the cost of the effort it will take to implement. We will re-consider supporting 
non-deterministic journeys once all the journeys have been implemented.

## Pros and Cons of the Options

### Yes, by using DFS to order steps

If we keep track of the `reachableActions` from each step, we can refactor the reachable step iterator to order them via 
a depth-first search.

* Good, because we'll be able to support journeys that are non-deterministic at the step level.
* Good, because this doesn't change the definition of tasks and journeys.
* Bad, because supporting completely non-deterministic journeys has proven to be quite complicated, due to uncertainty 
over the variety of edge cases it introduces.
* Neutral, because we can maintain support for deterministic journeys by assuming a step's `nextAction` is in its 
`reachableActions` by default.
* Neutral, because we can use an always-satisfied nominal step to set initial `reachableActions`.

### Yes, by making tasks iterable

We could move the reachable step iterator from the journey level to the task level. This would result in tasks being
accessible in any order, but the steps within them being deterministic.

* Good, because we'll be able to support journeys that are non-deterministic at the task level.
* Bad, because we won't be able to support journeys that are non-deterministic at the step level.
* Bad, because this changes the definition of tasks and journeys.
* Neutral, because task level non-determinism is much less complicated to support than complete non-determinism.

### Yes, by making journeys iterate one task at a time

We can set the reachable step iterator's initial step to be the start of the task the user is currently working on. This
would result in tasks being accessible in any order, but the steps within them being deterministic.

* Good, because we'll be able to support journeys that are non-deterministic at the task level.
* Good, because this doesn't change the definition of tasks and journeys.
* Bad, because we won't be able to support journeys that are non-deterministic at the step level.
* Bad, because we would logically be iterating through tasks without defining them as iterable.
* Neutral, because task level non-determinism is much less complicated to support than complete non-determinism.

### No

We can enforce an arbitrary ordering on independent steps so journeys remain deterministic.

* Good, because we won't have to put effort into implementing non-deterministic journeys.
* Bad, because non-deterministic journeys will have to be implemented deterministically.
* Neutral, because we can re-visit the idea of implementing non-deterministic journeys later down the line, when we
have more clarity over how we want them to behave.

## More Information

* This [pull request](https://github.com/communitiesuk/prsdb-webapp/pull/281) contains our first attempt at using DFS to implement non-deterministic journeys.