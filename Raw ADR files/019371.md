# Framework

## Status

accepted (never-gonna-change) [^1]

## Context

Albeit minimalism has its charm we want some support for our project, namely DI, Controller-convenience and some basic
tools to set up and configure our REST-Api, Threads, etc.
Since we start on the green-field, we should go for something with a bit of future (#cloud-ready™/ #cloud-native™). This
rules out java
Spring and other reflection heavy bs-frameworks and puts [graalvm](https://www.graalvm.org/) into the focus.
Generally we aim for blazing fast build times, quick startup and zero unnecessary baggage, which is probably what every
framework
between here and the sun will promise us...

Since we already used more buzzwords than a CEO in his/her quarterly opening speech - we got to look at some tech now
to make up for that:

| Framework                                                           | Positive                            | Negative                                                                                                                                                                                     |
|---------------------------------------------------------------------|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Spring Native](https://github.com/spring-attic/spring-native) [^2] | they tried😅                        | Spring is already a mess. Adding a native compilation build step to it ain't gonna make it better. The only reason to go for this is, because you have to (a.k.a. 'for historic reasons'...) |
| [Micronaut](https://micronaut.io/)                                  | sounds like a great and fast option | might be a bit more spring-like according to this [article](https://digma.ai/quarkus-vs-micronaut/#micronaut)                                                                                |
| [Helidon](https://helidon.io/) [^3]                                 | sounds very minimalistic            | as all functional things - there might be a bit of a learning curve                                                                                                                          |
| [Quarkus](https://quarkus.io/)                                      | seems battle-proven                 | I am still wondering about Helidon; have to fight the urge to start a new side project...                                                                                                    |

## Decision

* Use quarkus as main framework.
* Use jackson & vavr.jackson for object-mapping
* Use yml (quarkus-config-yaml) for configs

## Consequences

| Profit/Price | Description                                                                                    |
|--------------|------------------------------------------------------------------------------------------------|
| PROFIT       | Quarkus & GraalVM is fast and uses less resources.                                             |
| PRICE        | Spring's `there is a framework for literally everything` doesn't apply to us.                  |
| PROFIT       | We have a solid foundation which feels clean and minimalistic.                                 |
| PRICE        | We might have to fiddle around with some quirks, because our stack is a bit more cutting-edge. |

### Footnotes

* [^1]: some things are so fundamental that they can't be changed without basically re-writing everything. be wary of
  people who claim this to be untrue
* [^2]: spring native is abandoned and now actually part of spring boot3+
* [^3]: earned its place on my todolist for things to check out later...