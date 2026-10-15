# Messenger Animations

Date: 2020-09-10

## Attendees

Lucas Hills
Alex Robinson
Kari Matthews
Levi Serebryanski
Tim Patullock
Adrian Yong

## Status

Approved

## Context

The new Messenger will have quite a few animations. We need to decide on an approach for how to handle them. Examples of animations in new Messenger:

- Messenger frame opening/closing
- Launcher icons transitioning between opened and closed
- Message bubbles appearing
- Message bubble tails appearing/disappearing
- Message receipts appearing/disappearing

To try and get good coverage for the various requirements this ADR is focussing on testing using the MessageBubble component.

### Requirements

- Unmounting animated components. e.g. removing the send receipts
- Stepped animations. e.g. showing the triagle after the message bubble
- Need to be able to customise the bezier curve
- Disabling animations easily. i.e. when the messageLog is first opened, existing messages shouldn't be animated.

|                            | Keyframes                                   | ReactTransitionGroup                                 | Framer                            |
| -------------------------- | ------------------------------------------- | ---------------------------------------------------- | --------------------------------- |
| Unmounting and animations  | Can kinda hack it with hooks and setTimeout | `exiting` and `exited` styles                        | takes an `exit` prop              |
| Stepped animations         | delays                                      | delays                                               | delays                            |
| Easy disabling             | ?                                           | can adjust `appear` based on if the message is read? | `AnimatePresence initial={false}` |
| Can inspect with dev tools | Yes                                         | ?                                                    | ?                                 |

### Useful references

- [POC code](https://github.com/zendesk/embeddable_framework/pull/4091)
- [This discussion on an RFC](https://github.com/reactjs/rfcs/issues/128)
- [Design logs slide](https://docs.google.com/presentation/d/1s9uugdil8bs54rvdix9grevajmxlmpqrhquf5m1ya6k/edit?ts=5f3b9e17#slide=id.g8064c92a1b_0_17)
- [The Zendesk standard curve](https://docs.google.com/document/d/1CSnVhas2l0h9c_oSTSNqBD-WYQ2Q8kQXe0f0IEuquIw/edit)

## Possible approaches

### 1. ReactTransitionGroup, like the classic Web Widget

#### Pros

- More consistent with the classic web widget.
- Uses a library just for the hard bit
- Small package size

#### Cons

- The docs kinda suck. Examples are limited.

### 2. An animation library

#### a. Framer

[Framer](https://www.framer.com/api/motion)

Framer gives us an [AnimatePresence](https://www.framer.com/api/motion/animate-presence/) component that handles exit animations.

##### Pros

- Ease of use, seems to cover our use-cases really well.
- The docs are excellent.
- Should speed up initial development.

##### Cons

- Package size: 91.22 KB Parsed. 28.18 Gzipped. The API docs do have a guide on reducing bundle size [here](https://www.framer.com/api/motion/guide-reduce-bundle-size/).

#### b. Spring.io

[Spring](https://www.react-spring.io/)

##### Pros

- Widely used

##### Cons

- Hard to customise the bezier curve

### 3. Custom approach using keyframes + somehow handling unmount events

#### Pros

- No increase in package size.
- All the logic will be in our code. No hunting through library docs/code trying to figure out what's actually going on.
- May be easier to use with dev tools?

#### Cons

- Possibly more effort upfront.
- We need to rolll our own solution for handling animation as components unmount.

## Decision

We have chosen to go ahead with (2a) Framer for now. Every option comes with its own pros and cons and the decision really could have gone any way. The team is under a very tight deadline at the moment, and Framer seems like the option that would allow us to ship quickly. It also promises a good developer experience.

## Consequences

We will (at least temporarily) increase our package size. We intend to revist this decision in a few months to assess if the chosen approach is meeting our needs.
