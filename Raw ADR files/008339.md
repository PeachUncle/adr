---
# Configuration for the Jekyll template "Just the Docs"
parent: Decisions
nav_order: 100
title: Date Picker Widget / UI
status: accepted
date: 2024-05-25 when the decision was last updated

# These are optional elements. Feel free to remove any of them.
# status: {proposed | rejected | accepted | deprecated | … | superseded by [ADR-0005](0005-example.md)}
# date: {YYYY-MM-DD when the decision was last updated}
# deciders: {list everyone involved in the decision}
# consulted: {list everyone whose opinions are sought (typically subject-matter experts); and with whom there is a two-way communication}
# informed: {list everyone who is kept up-to-date on progress; and with whom there is a one-way communication}
---
<!-- we need to disable MD025, because we use the different heading "ADR Template" in the homepage (see above) than it is foreseen in the template -->
<!-- markdownlint-disable-next-line MD025 -->
# {short title of solved problem and solution}

## Context and Problem Statement

Practically, the designs were accepted from the start of the UI designing / wireframe. However, designing the date picker's looks gave a bit of a dylemma considering the fact that the default dropdown menu isn't very appealing, while getting a full on custom designs seemed to need a lot of efforts we couldn't afford the time of. This especially is going to cause issues integrating it with the skeleton code.

<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* The default dropdown menu isn't very appealing.
* A full custom design isn't feasible.

## Considered Options

* Allocating more time in order to actually implement the full custom design.
* Try a middle-ground with only using CSS to design it.

## Decision Outcome

Chosen option: "Try a middle-ground with only using CSS to design it.", because
it seems to be the option that is time-efficient, yet still produces a relatively good quality product.

### Other Option: Allocating more time in order to actually implement the full custom design.

Our other option of just working more on it in order to have a fully custom design.

* Good, because it shows more work and results in a better overall product.
* Bad, because it will take a lot longer for seemingly little benefit.
* Bad, because it complicates the integration process to the main code.

<!-- This is an optional element. Feel free to remove. -->
## More Information

The design was supposed to be done by Sarena. However, due to personal issues, the design was instead done by the UI / skeleton code team.

