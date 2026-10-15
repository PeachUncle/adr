# 9. How we will store runtime updates

Date: 2025-05-27

## Status

Accepted

## Context

Our project structure is build on top of immutable classes, that means that any kind of modification
that user request force us to recreate the instance of the project in memory. We need a easy way to
modify the runtime state, reduced nesting of the objects (to simplify the re-creation of the instance)
and support LIVE DATA manipulations.

1. We need LiveData wrapper on top of the TemplateDocument that will hide the complexity of modifying the runtime data
2. We need an easy way to modify the runtime state.

Possible implementations:
- compose business logic wrapper with helper methods, that will hide and control how the data will be cloned and modified;
- compose "history" of changes, that stored as separated collection and act as middle layer that asked fot runtime value first (like runtime cache, or proxy);

## Decision

1. Immutable classes are perfect for serialization/deserialization tasks. So we will keep them.
2. Avoid NULL in immutable classes. Use empty collections and default values.
3. Use packages for structuring the project classes
4. Use Builder pattern and `.copy()` with immutable classes. Use extension methods for immutable classes to build this logic in favor of chain-of-calls code pattern.
5. Avoid deep hierarchy of immutable classes, try to keep it in 2-3 levels. 
6. Create Add/Remove methods for mutating collections.
7. Create Helper for reducing the code for Update operation in collections.

## Consequences

- use pattern `with${PropertyName}(...)` for naming the methods that doing a property modification. Method should return a new instance of class with applied modifications.
- use patterns `add${Collection}` `remove${Collection}` for adding/removing elements from collections.
- use pattern `with{Collection}(item, ...)` and Unit `apply { ... }`
- use pattern `with{Collection}(ID, ...)` and Unit `apply { ... }`
- all collection items should have ID field (id they are not represented by primitive data types, like string or int, etc)
- added kotlin test dependency
- added robolectric dependency for unit testing, mock Android classes for unit tests
- `./gradlew test -t` run in continuous mode with watching file system changes
- rollback to the initial version of the Template is problematic. As workaround can be used metadata to store the original settings of the template.