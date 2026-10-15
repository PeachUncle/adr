# AS2 Structure Used Internally with an External Translation Library

## Decision Group

* TD - Technology Decision
* Proposed | 2024-11-17

## Problem/Issue

We need a strategy to handle object formatting in the context of ActionItems, particularly how to deal with field names in Activity Streams 2.0 (AS2) objects that have more specific names in our domain. For example, the `name` field in AS2 maps to the `Title` of an ActionItem in our context. The challenge is to maintain clarity and consistency in our domain while ensuring the flexibility of AS2 compliance.

## Decision

Implement a client library to handle the translation from the Task Management context to the BienOblige (AS2) context, maintaining the AS2 context throughout the BienOblige system. This library will provide a clear interface for translation, encapsulating the complexity of mapping between domain-specific terms and AS2 terms.

## Considered Alternatives

* Using the ActionItem naming internally and translating dynamically for the wire

## Arguments

### Pro

* **Flexibility**: Allows for internal models to leverage the flexibility and extensibility of the AS2 specifications.
* **Clarity**: Maintains a single terminology within internal systems, improving developer understanding.
* **Speed of Development**: Reduces the time to market for the initial release of the product by allowing developers to focus on a single terminology.
* **Encapsulation**: The client library encapsulates the translation logic, keeping it separate from the core business logic. There is no need to translate between contexts every time we go to/from the wire or to/from disk.

### Con

* **Complexity**: Introduces an additional component that needs to be developed, maintained, and integrated into the existing system.
* **Performance Overhead**: Translation operations might introduce latency, especially with complex or large datasets.
* **Consistency and Versioning**: Requires mechanisms to ensure consistent translations and manage versions of the library to prevent conflicts.
* **Scope**: One library would be required for each language or SDK that needs to integrate with the system.

## Related decisions

N/A

## Extends

N/A

## Related requirements

N/A
