# 5. Aggregate saving convention

Date: 2024-02-11

## Status

2024-02-11 accepted

## Context

We are planning to use DDD for most of the code that contains domain logic. When an aggregate is saved in a repository, we need a way to persist changes that were made since it was loaded. There are many ways to do that, with the most common being:

1. Add getters for every field and use them to get all aggregate fields.
2. Add `getSnapshot` method which returns all of the aggregate data with no behaviors.
3. Make aggregate an ORM model and use its change tracking mechanism to detect what has changed.
4. Make aggregate return events for every change and use them for persisting changes.

The first point is the easiest one to do, however, it breaks encapsulation. Ideally, an aggregate should expose only necessary data, keeping all of its fields and internal details private by default. Keeping them private encourages keeping as much logic in the aggregate itself, instead of just pulling data from it and storing logic outside of it.

The second point is very similar to the first one, but it's a slight improvement - we can get all of the data from the aggregate but without any behaviors. It's also easier to hide an internal structure of the aggregate, as a snapshot is using only plain objects instead of entities or value objects.

The third option is theoretically the simplest one. Aggregate fields can still be kept private and with a change tracking mechanism, it's not necessary to manually check what has changed or to send an update with all of the aggregate fields. However, it also limits the internal aggregate design to what can be mapped by the ORM of choice and may require adding ORM annotations to domain entities and value objects.

The last one introduces the most changes and requires the most work to do. For every change that can happen in the aggregate, a domain event must be created that contains all of the information about the change. For every event that was published by the aggregate, a repository makes the necessary changes to the database, either by changing the ORM model or by creating a dedicated SQL query. On the upside, it simplifies aggregate unit tests a lot without breaking encapsulation, as we can simply compare published events with expected events. It's also the only reasonable option if we ever want to store an aggregate using event sourcing.

## Decision

We'll use the approach of creating a new domain event for every aggregate change and use them in a repository to persist changes. We're not using the ORM in the project and we feel that simplification of aggregate unit tests is worth the extra effort.

## Consequences

- It will be easy to unit test aggregates.
- We will have to create a lot of domain events for every aggregate change.
- Since most changes from events can be mapped to a simple database update, it fits nicely with using a query builder instead of an ORM.
