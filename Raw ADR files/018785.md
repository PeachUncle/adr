# 5. Implement a queue system to wait for services to initialize

Date: 2019-02-25

## Attendees

- Apoorv Kansal
- Lucas Hills
- Adrian Evans
- David Allen
- Wayne See
- Levi Serebryanski
- Briana Coppard
- Timothy Patullock
- Nick Dawbarn
- Daniel Bradford
- Stefan Vizzari

## Status

Approved

## Context

The Embeddable Web Widget connects to many different services to support complex features. There are services such as Talk, Chat, Help Center and Submit Ticket.

As connecting and initializing these services take time during boot up, we must _queue_ any intention to use these services when they are not ready. For example, customers might use our Web Widget Javascript API to start up a chat session on page load. In its current form, the Web Widget will simply drop these API calls because the Chat service has not been intialized.

**_Considerations_**

We need to determine the content of each potential queue. In past, we have queued functions and their respective arguments and then simply fired those functions on flush. Given that we use Redux and we have an event stream (actions), we should ideally leverage the power of Redux and simply queue actions and then flush those actions back into Redux to continue certain workflows. If we queue functions, it will not be easy to determine which functions need to be queued as some functions might be anonymous.

**Option 1**

Use Redux Saga to implement queues when necessary. Essentially, we would run saga queues that listen into certain actions and are related to a service. We will continue to queue these actions until the service has been intialized (dispatch an `INITIALIZED` action or something similar) and then flush the queued actions back into redux. These flushed actions would be picked up by other sagas that will make API calls. Note that these sagas would have some sort of guard to ensure that they make API calls ONLY when the service has been initialized.

Advantages:

- Very easy to implement and maintain queues for a variety of different products. It simply requires creating new sagas and listening to certain actions.
- Easy to test.
- Queues up actions rather than function calls.
- Forces us to port over tightly coupled redux thunks action creators to sagas which simplifies the complexity in our action creators and separates application side effects into sagas and allow us to leverage more features of Redux-Saga.

Disadvantages:

- Requires porting over many of the existing action creators.
- More boilerplate code.

  **Option 2** (credit: Levi Serebryanski)

Create a custom queue middlware that will enqueue _thunks_ in various queues. Essentially, if the middlware receives a thunk and a service has not been intialized, it will simply put the thunk inside a _relevant_ queue. To determine whether the thunk needs to be queued and _where it should be queued_, the middleware will inspect the function name and potentially use redux state to see if the service has been initialized. Once the middleware receives a service initialized action, it will flush the _relevant_ queue, firing off the thunks.

Advantages:

- Affects existing action creators and calls to a small extent.
- Minimalistic and fairly general approach.

Disadvantages:

- Every returned thunk must be named so the middleware can inspect the name. This means that we will have to maintain function names in multiple places (action creators and middleware).
- Awkward workflow as we have action types for this exact same case.
- The middleware can have really complex conditional logic as we add more queues. It follows a putting in a bin pattern rather than listening pattern.
- Tightly coupled to `redux-thunk`. If we ever move to another framework, we will need to completely rewrite the queue system.

**Other Research**

- `redux-async-queue` was also investigated but this library is mainly focused on handling multiple actions of the same type sequentially in a queue order.
- We can interally wrap the inside of a thunk with an initializer check. If a service has not been initialized then we queue up the thunk in an external queue datastore. We could setup a middleware that will flush the queue when it received an initialized action.

## Decision

The team decided to choose option 2 due to its simplicity and general approach. Option 1 does lead us into a bigger conversation of whether we should migrate from Redux Thunk to Redux Saga which is out of scope for this ADR.

## Consequences

The changes documented here will be of a large scale and as a result it is expected that there will be regressions during development and testing on staging.
