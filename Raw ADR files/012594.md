# KDD-001: Multi tenant support

- _Date_: 3 August 2023
- _Deciders_: James, Andrei
- _Status_: DECIDED
- _Outcome_: Single Tenant

## Context

The notifications service will be used to send alert for mSupply customers, stock alerts, cold chain notifications etc.
It could be designed in such away that it could be used to for multiple organisations from a single instance.
An example of this might be if we wanted to run a cloud service which cold chain could immediately use via the internet without customer instances being exposed to the internet.

Assumption: If we needed to have a centralised system, it could potentially proxy connections to customer databases, rather than explicity redeveloping the tool?

## Options

<!-- Copy and paste Option X into Option 1, Option 2, etc depending how many options you have -->

### 1. Multi tenant

A multi tenant system would need to have the following features:

- User roles and permissions based on tenant or organisation
- Tenant specific configuration (different databases perhaps?)

_Pros:_

- Wouldn't have to retro fit this later if required

_Cons:_

- If we design the system to allow for usage from multiple tenants, things such as user roles and permissions checking needs to be more complicated.
- Development work could be slower and code more complex

### 2. Single Tenant

The system would be kept as simple as possible, initially all users who have configuration access would get full access to the system.
We don't need to hide data from different users etc.

_Pros:_

- Development is not encumbered by complex permissions checks

_Cons:_

- Retrofitting this later could be difficult

## Decision

The decision was made in favor of **option 2 Single Tenant**.

We don't yet understand what kinds of permissions and restrictions might be required in the system.
Trying to design this without requirements might be more of a burden than a future value.

## Consequences

We may required a significant amount of refactoring if a multi tenant use case is required
