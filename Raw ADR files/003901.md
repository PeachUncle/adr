---
scope: Jobberknoll (@jobberknoll/api)
date: 2024-12-23
deciders: "@tchojnacki"
informed: "@mlodybercik, @jakubzehner, @piterek130"
---

# Vertical partitioning of the Jobberknoll API package structure

## Context and Problem Statement

The architecture for `@jobberknoll/api` package proposed in the E2 architecture document used a horizontal partitioning of the structure, holding its components in separate directories based on their type (e.g. `controllers`, `contracts`, `middlewares`). As the internal and external controllers should be separate, the current structure leads to mixing of internal and external contracts in the same directory. The route handlers defined directly in the controlllers can quickly exceed the recommended size of a single file (a rough estimate of 300 lines of code for the external controller). Additionally, defining the route handlers in separate files from route definitions can lead to big change areas when modifying the API [^files] [^srp].

## Considered Options

- Keeping the horizontal slicing
- Moving to vertical package structure

## Decision Outcome

Chosen option: **Moving to vertical package structure**, because it allows for a better separation of concerns and will make the codebase more maintainable in the long run.

The changes are as follows:

- `contracts/dto` will be split into `int/contracts` and `ext/contracts`
- `controllers/*.ts` will be split into `shared/controller.ts`, `int/int-controller.ts` and `ext/ext-controller.ts`
- `contracts/routes` will be split into `int/routes` and `ext/routes`
- route handlers will be moved from controller files to route files
- `middlewares` and `helpers` will be moved into `shared`
- `mappers` will be temporarily removed with an option to reintroduce in `int/mappers` and `ext/mappers` if needed

Changes to Jobberknoll's architecture also apply to Feather.

### Consequences

- Good, because the codebase will be more maintainable and easier to expand.
- Good, because files which change together will be closer to each other.
- Good, because the Single Responsibility Principle will be easier to follow.
- Good, because the internal and external contracts will be more separated.
- Bad, because the initial refactoring will require changes in the codebase.
- Bad, because the new structure diverges from the E2 architecture document.

[^files]: https://kevinmahoney.co.uk/articles/files-that-change-together
[^srp]: https://en.wikipedia.org/wiki/Single_responsibility_principle
