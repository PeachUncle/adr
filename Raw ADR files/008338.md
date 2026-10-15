---
# Configuration for the Jekyll template "Just the Docs"
parent: Decisions
nav_order: 100
title: Sleep Widget
status: accepted 
date: 2024-05-26 when the decision was last updated

# These are optional elements. Feel free to remove any of them.
# status: {proposed | rejected | accepted | deprecated | … | superseded by [ADR-0005](0005-example.md)}
# date: {YYYY-MM-DD when the decision was last updated}
# deciders: {list everyone involved in the decision}
# consulted: {list everyone whose opinions are sought (typically subject-matter experts); and with whom there is a two-way communication}
# informed: {list everyone who is kept up-to-date on progress; and with whom there is a one-way communication}
---
<!-- we need to disable MD025, because we use the different heading "ADR Template" in the homepage (see above) than it is foreseen in the template -->
<!-- markdownlint-disable-next-line MD025 -->
# Sleep Widget Solution

## Context and Problem Statement
For developers, tracking sleep time is helpful to understanding and improving their concentration and productivity. Through the Sleep Widget, we will develop a feature that allows them to easily track their sleep time.

<!-- This is an optional element. Feel free to remove. -->
## Decision Drivers

* Intuitive UI Design.
* Appropriate form to be displayed in the pop-up screen that appears when the sleep button is pressed.

## Considered Options

* Horizontal slidebar and five options of sleep hours.
* Vertival slidebar and five options of sleep hours.

## Decision Outcome

We choose option 2, as our pop-up screen was a vertical rectangle so that vertical slidebar was more suitable. Additonally, we added a emoji to the right-slide of each sleep-hour option, which makes the UI more intuitive.

<!-- This is an optional element. Feel free to remove. -->
### Consequences

* Good, because it is consistent as one function within the entire application.
* Bad, because implementing a vertical slidebar was not trivial problem in html and css, so that the source code became a little complicated.
