---
# Configuration for the Jekyll template "Just the Docs"
parent: Decisions
nav_order: 100
title: Skeleton Code for Final Project
status: accepoted
date: 2024-05-13

---
<!-- we need to disable MD025, because we use the different heading "ADR Template" in the homepage (see above) than it is foreseen in the template -->
<!-- markdownlint-disable-next-line MD025 -->
# Skeleton Code for Final Project

## Context and Problem Statement

For our final project, we have decided to implement a skeleton code which would follow the basic structure of our application. Since our team is really big (10 people), we need to ensure consistent code quality, smooth integration of individual contributions, and efficient collaboration. Hence, we must set a foundation that achieves these goals while accommodating future changes and enhancements.


<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* Time constraints: We need a strategy that is the most efficient and reduces redundancy.
* Consistency: Each individual's effort should be consistent with one another. That is difficult to implement if all 10 members are trying to reproduce the same UI in different ways.
* Productivity: We need to be productive and utilize our resources efficiently. It would not be the best decision to let multiple people work on the same thing.
* Delegation: It will become easier to delegate subtasks if a few people are working on the skeleton code and the rest are working on other components.

## Considered Options

* Let each person start from scratch
* Develop a minimal skeleton code
  

## Decision Outcome

Chosen option: "Develop a minimal skeleton code", because
there's nothing much you can change in that phase, it mainly focusing on one thing. Hence, removing it would be the best option.

<!-- This is an optional element. Feel free to remove. -->
### Consequences

* Good, because it provides a consistent code structure and style from the start.
* Good, because it simplifies the integration of individual contributions, reducing merge conflicts and integration issues.
* Good, because it allows a flexible foundation that can be easily extended and modified as the project evolves.
* Bad, because the skeleton code might impose constraints that might push us to make changes to the requirements set at the beginning.
