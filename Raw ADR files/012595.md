# KDD-002: Parameters

- _Date_: 30 Oct 2023
- _Deciders_: James, Andrei, Craig
- _Status_: DECIDED
- _Outcome_: Option 1 Parameter Sets

## Context

Notification configs need to have some kind of parameters to customise the notifications. They're used for SQL based recipients (queried from the datasource) and for the template.

Different approachs could be taken to this with different trade offs.

As an example problem, we'll imagine we want to send a notification relating to last store sync times.

Some users will only be associated with a single store, while others might be associated with 100's of stores.

We want to be able to send a notification to each user with the last sync time for each store they are associated with.

We'll assume 3 users and 2 stores.

| User | Store |
| ---- | ----- |
| A    | 1     |
| A    | 2     |
| B    | 1     |
| C    | 2     |

User A wants notificaitons for both stores, User B only wants notifications for store 1, and User C only wants notifications for store 2.

## Options

### 1. Parameter Sets

This approach means that each notification configuration can have multiple sets of parameters. The system will loop over each parameter set and generate a notification for each one.

Loop through each set of parameters
For each set of parameters
Run any associated queries
Query for any sql recipients for parameter set
For each recipient
Render template with query data & recipient data

The result of this approach would be that each matching recipient would get a notification for each parameter set.

> User A will get two notifications, one for each store. User B will get one notification for store 1, and User C will get one notification for store 2.

_Pros:_

- Simplish, no need for user based parameters
- Allows a single user to receive multiple notifications
- Already working in a code branch

_Cons:_

- All parameter sets need to be defined upfront, can't dynamically add a new store for example
- Users might get a lot of notifications (for example if you have a notification per store and a user is subscribed to all stores)

### 2. User Driven

This approach means that each notification configuration will have a single set of parameters. These parameters will be used to query for recipients and to retrieve user related parameters which can then be user to query data and render the template.

Query for recipients based on the parameters
For each recipient
Run any associated queries with config parameters plus and recipient specific parameters
Render template with query data & recipient data

The result of this approach would be that each matching recipient would get a single notification for each configuration

> All users get a single notification, the template and queries would need to be written in a way that allows for multiple stores to be included in the notification, either but looping over the data or by using a group by.

_Pros:_

- Allows for dynamic parameters (for example a new store is added, a user can subscribe to that store using a tag?)
- Each user receives a single notification per config so shouldn't get spammed with notifications

_Cons:_

- A user can only receive one notification (mostly a good thing!)
- Templates & queries need to be more complex, for example if you want to have a summary of stores, rather than just info for a single store, how do you you specify the parameter user joins?
- Not clear exactly how we'd get parameters from a user query?
  Do non sql recipients have parameters too?

### 3. Combination

This combined option 1 & 2 parameter sets and user based parameters

Loop through each set of parameters
For each set of parameters
Query for recipients based on the parameters
For each recipient
Run any associated queries with config parameters plus and recipient specific parameters
Render template with query data & recipient data

The result of this approach would be that each matching recipient would get a single notification for each parameters set they match with.

_Pros:_

- The most flexible approach

_Cons:_

- Pretty much all of the cons from above, plus additional complexity!
- Complex to implement, test and debug

## Decision

PROPOSED: The decision was made in favor of **option 1 Parameter Sets**.

Parameter sets can be extended in the future to query for their parameters, so we can have dynamic parameters in the future using this approach.
Receiving multiple notifications can be a good thing, and people who are expected to receive multiple reports can use email filters to arrange them if desired.

This approach is already implemented, and we don't have budget for a re-architecting at this time.

## Consequences

It may be more difficult to implement user based parameters in future without breaking existing reports.
