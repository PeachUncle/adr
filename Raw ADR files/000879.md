# Leveraging `Context` in AS2 Objects for Enhanced Clarity and Flexibility

## Decision Group

* TD - Technology Decision
* Proposed | 2024-12-05

## Problem/Issue

The Activity Streams 2.0 (AS2) specification from the W3C leaves the definition of the `Context` field intentionally vague, raising questions about its optimal use in representing activities and objects. The primary challenge is determining the most effective way to leverage the `Context` field to ensure clarity, consistency, and flexibility in the representation of activities and objects within the task management system.

## Decision

We decided to specify the `Context` at the top-level `Activity` object only, ensuring it encompasses all domains common to the internal objects supported by the system. This approach is intended to reduce redundancy, simplify the structure of AS2 objects, and provide a clear and consistent context for all subordinate objects. The `Context` field will typically include references to three namespaces:

* The AS2 namespace for standard Activity Pub/Activity Stream operations.
* The Bien Oblige namespace for custom objects specific to task management.
* The [schema.org](http://schema.org) namespace for representing target objects upon which actions can be performed.

Additionally, the system will allow users the flexibility to add custom namespaces or reference additional standard namespaces as needed when they create or update ActionItems.

## Considered Alternatives

* Ignoring/not specifying the `Context` field in AS2 objects.
* Specifying the `Context` for each individual object within the `Activity`.
* Restricting the `Context` to a fixed set of namespaces without allowing user-defined namespaces.

## Arguments

### Pro

* **Reduces Redundancy:** By declaring the `Context` at the `Activity` level for all objects, it prevents the repetition of context information across multiple objects.
* **Maintans Standards Compliance:** This approach is compatible with our [Project Principles](../../Principles.md) by maintaining strict adherence to our best understanding of the W3C specification.
* **Enhances Flexibility and Extensibility:** Allowing for the inclusion of custom namespaces and additional standard namespaces enables the system to adapt to diverse user needs and future integrations.
* **Maintains Consistency:** Ensuring consistent usage of namespaces helps avoid conflicts and ensures correct interpretation across different implementations.

### Con

* **Potential for Overgeneralization:** Specifying the `Context` at the top-level only could potentially overlook the nuanced differences between objects if not carefully managed.
* **Potential for Confusion**: Since the ideas behind the `Context` are not fully standardized, there is a risk that users may misunderstand or misuse this field, or for it to cause confusion and inconsistency in the system. To effectively leverage this approach, clear documentation and a thorough understanding of how the `Context` field operates are essential for all users and developers.

## Related Decisions

N/A

## Extends

N/A

## Related Requirements

N/A
