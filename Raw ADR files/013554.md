# 1. Use Kotlin For Production Code

## Status
Accepted

## Context
Java 17 has improved the programmer experience but Kotlin, in our opinion, provides a better one.

## Decision
We will use [Kotlin](https://kotlinlang.org/) to develop the production modules. Test will use Java, primarily due to some complexity in getting Cucumber and Kotlin to play nicely together.

## Consequences
Kotlin has many features baked into the language that require extra libraries to accomplish in Java, e.g. Lombok. Fewer dependencies means fewer upgrade headaches in the future.