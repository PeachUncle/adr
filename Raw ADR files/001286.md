# Incident Module Description

* Status: accepted
* Deciders: Alejandro Garcia Prada
* Date: 2025-11-01

## Context and Problem Statement

The company needs to manage the incidents that are sent to the system admins. Examples of this incidents are not delivered products or a track fault. This module is located in the business logic tier, but we have to concrete it's inner composition

## Decision Drivers

* RF-09 Reportar incidencias

## Considered Options

* 0005-1-Factory-Pattern
* 0005-2-Builder-Pattern

## Decision Outcome

Chosen option: "0005-2-Builder-Pattern", because it provides a clearer and more flexible way to construct complex incident objects.

It is expected that incidents will evolve to include more parameters, optional fields, and conditional configurations, rather than an ever-growing number of incident types.

The Builder Pattern better supports this scenario, as it allows for progressive construction of objects without the need for multiple constructors or excessive subclassing.

### Positive Consequences

* The creation of incidents becomes more maintainable and extensible as new parameters or optional fields are added over time.
* It keeps the construction process modular and decoupled from the representation, improving flow readability and maintainability.
* It prevents the proliferation of multiple constructors or subclasses for each incident variant, reducing complexity in the long term.

### Negative Consequences

* It adds an extra abstraction layer, which can be unnecessary when incident creation is simple. A Factory Pattern would provide a more direct solution.
* It requires multiple steps to create an object, which increases verbosity.

## Pros and Cons of the Options

### 0005-1-Factory Pattern

The Factory Pattern is a creational design pattern that provides an interface for creating objects in a superclass but allows subclasses to alter the type of objects that will be created.

Instead of instantiating classes directly, you delegate that responsibility to a factory that decides which class to instantiate depending on some logic.

In this concrete case, we would have a superclass that create the incidents and two subclasses for each incident type. 

More info: https://refactoring.guru/design-patterns/creational-patterns

* Good, because it centralizes object creation logic.
* Good, because it supports the Open/Closed Principle (you can add new types without modifying the inner class).
* Good, because it decouples class that uses objects from the class that instantiates them.
* Bad, because it can lead to an increase in the number of classes (if increasing the type of incidents or related "products").
* Bad, because it for very simple creation logic, it can add unnecessary abstraction.

## 0005-2-Builder-Pattern

The Builder Pattern is a creational design pattern that separates the construction of a complex object from its representation, allowing the same construction process to create different types or configurations of objects.

Instead of passing all parameters to a constructor or relying on subclasses, the Builder provides step-by-step methods to configure and assemble an object. This makes object creation flexible, especially when many optional or conditional parameters are involved.

In this concrete case, we would have a builder class responsible for constructing incident objects. Each builder could configure incidents differently depending on the client type (e.g., customer or driver), while following the same overall construction process.

More info: https://refactoring.guru/design-patterns/builder

* Good, because it separates the process of constructing an object from the way that object is represented.
* Good, because it makes the flow more readable and flexible, especially when the object being created has many optional or dependent parameters.
* Good, because it allows the same construction process to produce different representations or configurations of the object.
* Bad, because it introduces additional complexity and increases the number of classes, which can make the system heavier.
* Bad, because if not properly organized, it can lead to redundant or repetitive builder logic.
* Bad, because it provides little benefit for simple objects or cases where only a few parameters are needed.

