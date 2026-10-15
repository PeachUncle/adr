# 8. Routing in the widget

Date: 2019-06-07

## Attendees

- Briana Coppard
- Apoorv Kansal
- Lucas Hills
- Adrian Evans
- David Allen
- Levi Serebryanski
- Timothy Patullock
- Nick Dawbarn
- Daniel Bradford
- Stefan Vizzari

## Status

Approved

## Terms

Embed: A Zendesk channel that's shown within the widget. Examples would be Chat, Talk and Help Center

## Context

Routing inside the Widget is currently very complex and spread out around the codebase. It uses the `activeEmbed` state to switch between embeds and each embed has a different way to handle its own screen state, so the implementation isn’t consistent across Embeds.

The way we handle going back is hard coded depending on the state of the widget. This isn’t scalable as it relies on knowing about each embeds behaviour and needs to be manually updated for each new embed that’s added.

We want to add proper routing to the codebase to simplify this logic and allow for a more extensible future.

## Possible Approaches

### 1. Build our own routing

We could build our own routing into redux. We already have most of the state needed inside Redux, we could adapt that to fit with routing. We have already been pushing for routing inside Redux by introducing things like screen state.

We would need to have reducers for our routing logic and some action creators to update the routes. The main challenge with this approach is that reducers should not contain complex logic and do not know about application state outside their scope. Therefore, we would need to handle the decisions on where to go next inside an action creator or middleware and broadcast that to the reducer.

Advantages:

- We are not relying on any third party libraries. There wouldn't be any unexpected side effects a library could cause.
- More control if we need to add or change something about the behaviour.
- All our routing logic could be easily traced to the routes reducers and we can see the actions in our redux logs.
- It does match what already exists within our codebase and is less to learn for current team members.

Disadvantages:

- More logic for us to handle in Redux, right now it is already very complex and this is just moving that complexity around.
- More specific knowledge needed to learn our codebase as it is not a React standard.
- Breaks our redux guidelines because we would need to have a bunch of update_route actions.
- We would need to build and maintain new features as they're needed.

### 2. Use React Router for routing

We can use the React Router library to handle routing. We would need to restructure the codebase to fit with its style and create `Page` components to use as the base components for routing, and add some `Routing` components. This would abstract away the routing logic from Redux and into these components.

Advantages:

- React router is a library built for routing, it would likey be able to handle any issue we encounter in the future.
- All routing state would be removed from our application. We wouldn't need to store it anywhere, React Router would handle it.
- We have some conventions to follow when rebuilding our codebase to allow for routing.
- History comes for free, no need to track it and compute `back` navigation action behaviour ourselves.
- It supports our goal to modularize our codebase and split up components
- Is the standards for routing in React and has a community around it

Disadvantages:

- Less control, the logic is abstracted away from us.
- If there is a feature we need that doesn't exist within React Router it will be harder to introduce.
- It is built for browsers so there might be weird side effects using it in an iframe.
- Routing logic is more spread out. Child components can change the route, it's not centralized.

### 3. Using another routing library

There don't seem to be any other JavaScript routing libraries that deal with React that are as feature complete at React Router. A possible alternative, Reach router, is currently being integrated into React Router and all other options are more simplistic.

## Decision

We will use React Router for routing inside the Web Widget, starting with routing at the Embeds level and then introducing it to the entire widget.

## Consequences

- React router adds 1.83 KB gzipped to our package size.
