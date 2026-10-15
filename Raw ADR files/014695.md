# ADR-0013: Build and Dependency Manager

## Status

Accepted

Date of decision: 2024-09-20

## Context and Problem Statement

The Kotlin web app will have dependencies (i.e. 3rd party libraries). Our source code will need compiling and then
packaging with these libraries, ready for execution. How will we manage these dependencies and orchestrate this build
process?

## Considered Options

* Maven
* Gradle with Kotlin
* Gradle with Groovy

## Decision Outcome

Gradle with Kotlin, because it means the build configuration uses the same language as the application, and because it
is the most common choice for Kotlin projects (both globally and within MHCLG).

## Pros and Cons of the Options

### Maven

Maven is an extremely mature and popular build manager for the Java ecosystem (including JVM languages like Kotlin). It
uses XML based configuration to describe dependencies and the build process. It is the most popular build tool for Java.

* Good, because it is widely adopted, particular in the Java world
* Good, because it has a long track record
* Neutral, because working with XML can sometimes be awkward

### Gradle with Kotlin

Gradle is a slightly new alternative to Maven, performing similar functions but by providing a DSL (domain specific
language) rather than XML. This can make editing the configuration simpler and allows for extensibility. Gradle provides
a Kotlin DSL. It is the most popular build tool for Kotlin projects.

* Good, because it is widely adopted, particularly in the Kotlin world
* Good, because it is mature (though less so than Maven)
* Good, because the build configuration can be written in a Kotlin DSL, i.e. the same language as the application code
* Good, because it is the build tool of choice for other Kotlin projects within MHCLG

### Gradle with Groovy

Gradle also offers a Groovy DSL. This is the original DSL language.

As with Gradle for Kotlin, but...

* Bad, because Groovy introduces another language into the project without any benefit

## More Information

* [JetBrains Dev Ecosystem 2023 survey – Kotlin build system](https://www.jetbrains.com/lp/devecosystem-2023/kotlin/#kotlin_build_system)
* [JetBrains Dev Ecosystem 2023 survey – Java build system](https://www.jetbrains.com/lp/devecosystem-2023/java/#java_buildsystem)
* [MHCLG eip-ero-notifications-api Gradle Kotlin build file](https://github.com/communitiesuk/eip-ero-notifications-api/blob/main/build.gradle.kts)
* [MHCLG delta-auth-service Gradle Kotlin build file](https://github.com/communitiesuk/delta-auth-service/blob/main/auth-service/build.gradle.kts)
* [MHCLG eip-ero-register-checker-api Gradle Kotlin build file](https://github.com/communitiesuk/eip-ero-register-checker-api/blob/main/build.gradle.kts)
* [MHCLG eip-ero-print-api Gradle Kotlin build file](https://github.com/communitiesuk/eip-ero-print-api/blob/main/build.gradle.kts)
* [MHCLG eip-ero-ems-api Gradle Kotlin build file ](https://github.com/communitiesuk/eip-ero-ems-integration-api/blob/main/build.gradle.kts)