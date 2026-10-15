## Title
UseCase responsibility

## Status
Draft

## Context
A use case is an entry point into a module with as purpose to perform an action on the domain. (write)

### <span style="color:#4863A0;">Responsibilities</span>
- looking up all necessary data (with sensible validations if expected data is missing)
- invoking the domain to elicit some change
- saving the result
- publish events as a result of the invoked action

A use case must never directly invoke another use case. 
If it seems a use case could be reused, then this is an indication we should consider promoting
the use case to a domain service, or push more logic into the domain.

### <span style="color:#4863A0;">UseCase as a RestController</span>
Because a use case is always some entry point must never directly invoke another use case,
it is good to implement as a rest controller. This reduces the mapping load by removing the need
for an additional controller layer.

### <span style="color:#4863A0;">UseCase as an EventListener</span>
When the domain needs to react on an event, this is also a usecase.
In general, it is advised the event listeners is an @ApplicationModuleListener so that
it is not part of the original transaction, and is temporally decoupled.

Especially when crossing the module boundary we should not participate in any ongoing transaction.
It would create a tight coupling which will become a pain if we want to move the other module
to another app. If it turns out we need this immediate consistency, then we should probably rethink
our module boundaries instead of resorting to a shared transaction.

<span style="color:#FF7900;">!!! It is possible a use case is both an event listener and a rest controller,
when some use case can be executed directly or based on an event.</span>

## Decision

A use case
- must never directly invoke another use case.
- can implement a rest API
- can listen to events using @ApplicationModuleListener (new tx + async).
- can listen to events using @EventListener within the same module, 
though think twice as it makes the code more difficult to follow.

## Compliance
An archunit test can validate no method annotated with just EventListener has an event argument from another module.

Other constraints will be checked by reviews.
## Notes
- Author: Gert Wijns
- Changelog:
    - 0.1 initial proposed version on 2025-01-12
