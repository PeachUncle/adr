# 2. Implement a communications layer into Embeddable Framework

Date: 2017-11-22

## Attendees

- Aaron Cottrell
- Adrian Evans
- Briana Coppard
- Ryan Seddon
- Terence Liew

## Status

Accepted

## Context

The company is moving forward with its focus to bring omnichannels and a proactive service to its customers over the coming year. One of the goals is to have Web Push (IPM) integrate more closely with the Web Widget (currently Embeddable Framework) in order to create a more seamless experience between the products. However since Web Push is not located inside the Web Widget like its prior revision therefore it is necessary to design an approach for multiple products to communicate. The team communicated with Outbound Melbourne (Bunjil) to determine two options to support the focus.

**Considerations**

- Subscribed embeds would be subjected into a priority queue on a "first come, first served" basis to provide a means of conflict resolution when deciding the state of which embeds should render or the order of them. This mitigates users from being overwhelmed or distracted by multiple elements on a page.

- In due time a framework will be created to provide interfaces that would allow users to create constructs that make up an embed which will be compatible in integration with the Web Widget.

**Option 1**

The Web Widget would expose APIs that Web Push could leverage in order determine when to surface itself and subtly hide the Web Widget.

Advantages:

- Easy to implement
- High velocity

Disadvantages:

- Extending functionalities to other embeds would be difficult

**Option 2**

The Web Widget would undergo an architectural change and have some of its state as well as logic extracted onto a different repository. The Web Widget would subscribe to the new project named Embeddable Framework which implements a publish-subscribe pattern that mediates events between embeds.

Advantages:

- Scalable to allow multiple embeds to communicate with each other
- Decoupling logic between Embeddable Framework and Web Widget

Disadvantages:

- Will be a challenging task and naturally take longer to implement
- May likely introduce regressions

## Decision

It was decided that 'Option 2' would be accepted.
The option presented is attractive because of the aforementioned scalability benefits as the number of subscribers
increases. In addition it serves as a good foundation to bundle the creation of embeds onto the newly defined
project.

## Consequences

The changes documented here will be of a large scale and as a result it is expected that there will be regressions during development and testing on staging.
