# Avoid lazy loading child entities

* Deciders: jbarnett, cwood, mheyes
* Date: 07-02-2020

## Context and Problem Statement

Lazy loading allows deferred fetch of child entities on first access as long as the same transaction in which the parent entity was fetched is still open.

Should this functionality be used?

## Considered Options

1. Always use this feature
2. Use this feature when child entities may not always be needed
3. Avoid using this feature 

## Decision Outcome

Chosen option: 3

Lazy loading is a 'leaky abstraction' which requires the consumer to know which fields are lazily loaded, otherwise they risk causing a `LazyInitializationException `. 
This pollutes the model layer with database level concerns (i.e. how is the data being fetched). 

For example this will error assuming `Bar` is a field of `Foo` which is lazy loaded.
```java
var foo = fooRepository.findById(1);
foo.getBar(); // throws LazyInitializationException
```
This is because `findById` runs in its own transaction, and the subsequent call to `getBar()` has no open transaction to perform the lazy fetch in.

In more realistic scenarios where access to the lazy field is far from the fetch site (e.g. a template tries to get a value on a entity passed in from a controller fetched from a service), this can become very error prone.

It is possible to simply scope the entire controller handler to a single transaction, however this is bad practice as it requires database connections to be held open for long amounts of time (including template rendering) which can slow performance, delay writes and exhaust the connection pool. 
Doing this is also not very semantic as it does not clearly define where the transacting boundaries are from a service point of view.

In the case where child entities are not needed, a DTO/view object should be used instead, fetched by a Spring Data JPA Projection. 
This solves the issues lazy loading creates as all the required fields are resolved in 1 go at initial fetch time, and the consumer does not need to know what fields they can access at what time. Any fields on the DTO/view can safely be accessed at any time.  

While this does require slightly more code and more design thought, it provides the  performance benefits of lazy loading without the drawbacks.

