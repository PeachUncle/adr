# Implement meta-events generically

## Status

Accepted

## Context

Meta-events in the MIDI standard are a way of indicating non-note information within a MIDI file. Palestrina includes some of the meta-events as available at the beginning of a Melody or at the beginning or end of a note within that Melody, or at specific ticks or offsets from these locations.

It is necessary to provide a clear interface to allow end users to create these meta-events, and three questions arise related to it:
- Do we wish to provide a separate method for each type of meta-event?
- What syntax do we wish to provide for adding meta-events?
- Do we wish to provide separate methods for adding a single meta-event and adding multiple ones?

For the first question, it is far from clear that significant value would be added by doing adding separate methods for each type of meta-event, given that each method call would still require the same amount of contextual information from the end user, and given that adding many separate methods to both Melody and MelodyMember would likely increase the number of test cases. However, given that MIDI meta-events represent two different types of entity (a text message associated with a specific MIDI tick and a change of some kind to MIDI output), there may be value in separating these types of event.

For the second question, the existing implementation allows two different argument formats for adding a generic meta-event:
```
.withEvent(eventName, eventValue?, { at?, offset? }?)
.withEvent({ event: eventName, value?: eventValue, at?: eventExactTick, offset?: eventOffset })
```

For typical simple use cases the first syntax is probably best; it's clear and straightforward for an end user.
When cases get more complicated (eg: adding multiple events from an array), the second syntax is clearly superior.

For the third question, multiple cases have arisen where being able to add multiple meta-events in one call allows chaining that would otherwise not be possible (see Water for some good examples).

## Decision

- We will create two types of ways to add a meta-event, one for generic meta-events and one for text meta-events.
- We will support both one-and three-argument calls.
- We will create a method for adding one meta-event and one for adding zero or more meta-events.

## Consequences

- Clear documentation will be required for how to add meta-events.
- MelodyMembers will have six meta-event-related methods associated with them.
- Melodies will call these methods.
- Existing music will require little changes.
