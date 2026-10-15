# 6. CSS overrides

Date: 2019-05-14

## Attendees

- Briana Coppard
- Apoorv Kansal
- Lucas Hills
- Adrian Evans
- David Allen
- Wayne See
- Levi Serebryanski
- Timothy Patullock
- Nick Dawbarn
- Daniel Bradford
- Stefan Vizzari

## Status

Approved

## Context

The way we override styles inside the framework is very top heavy. We override for several things such as colour, settings and garden component overrides at the document level by injecting new styles directly into the DOM or by applying everything to one Styles Components ThemeProvider. This works for fairly simple use cases but since these styles are global it's hard to know about the potential side effects we might create when we modify them. Additionally when we need to handle different use cases we either need to create an entirely new global classname for one component or add conditional logic to our overrides, leading to extra complexity for something that should be simple.

I'll list two files where we have these overrides specified, this ADR goes beyond them but they are the worst offenders:

**gardenOverrides**

This file contains all overrides for every garden component. It's very large and contains a lot of conditional logic in order to inject colours correctly and differentiate between the different garden components. This is passed to a ThemeProvider that wraps our entire application and it overrides all garden components. This means when we add new components there might already be overrides applied to it and it's hard to track where they are coming from.

**util/color/styles**

This file contains a long string with css classes for our colours. This is injected into our iframe's DOM and is composed by lots of children in order to get the user colour and the calculated colours we generate for accessibility. It's extra hard to know what components are using this since it's handled in the css files and changing one could easily break something else in our codebase.

## Proposal

We override styles at the component level. Each element that needs a css override can be wrapped in another component that applies the overrides. This can be done via javascript or using styled components.

Advantages:

- Each component has completely isolated styles and won't be broken by a change further up in the tree.
- No more conditional logic inside our overrides.
- There would be less domain knowledge required to get styles to work. As all the style overrides are handled in the component itself you wouldn't need to know to go to specific global files to find it's overrides.

Disadvantages:

- Potentially lots more props being passed around with style variables in them, expecially for colours, unless we import directly from the mixer.
- More potential for duplicate styles.

## Alternatives

1. We could go with this approach for use cases where we have lots of conditional logic (such as buttons in gardenOverrides) and still allow globals for simple overrides that we believe will always be consistent (such as changing garden blue to grey). If conditional logic needs to be added then it should be moved to component overrides.

## Decision

Proposal accepted, to avoid the issue of having to pass down lots of props we will do the colour mixing inside the components as needed and only pass down the theme colours and any overwritten colours.

## Consequences

TBD
