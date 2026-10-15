# ADR-0005: Server-side Language and Framework

## Status

Accepted

Date of decision: 2024-08-23

## Context and Problem Statement

The Private Rented Sector Database (PRSDB) will include web app component(s) - e.g. to serve the local authority,
landlord, and letting agent user journeys, and potentially machine-to-machine APIs.

What language and web framework should we use to develop those web app component(s)?

## Considered Options

* Java, Spring Boot, and Thymeleaf 
* Kotlin, Spring Boot, and Thymeleaf 
* Ruby, Rails, and ERB

## Decision Outcome

Kotlin, Spring Boot, and Thymeleaf, because Kotlin balances type safety with modern language ergonomics and does not
overly restrict the pool of technical talent; Spring Boot and Thymeleaf are essentially the “default” choices in the JVM
world.

## Pros and Cons of the Options

### Java, Spring Boot, and Thymeleaf

Java is a very mature, popular, statically typed, object-oriented programming language that runs on the Java Virtual
Machine (JVM). Spring Boot is the dominant web application framework for JVM languages. Thymeleaf is a templating engine
commonly used for server-side rendering (e.g. of HTML resources) with JVM applications.
* Good, because it is used in other MHCLG services.
* Good, because there is a relatively large market for developers with these skills (30% of professional developers
  responding to the Stack Overflow 2023 survey use Java, 14% use Spring Boot). 
* Good, because statically typed languages offer powerful tooling and can eliminate certain classes of errors at 
  compile-time. 
* Bad, because statically typed languages can be less flexible than dynamic languages, making e.g. prototyping
  potentially less rapid. 
* Bad, because Java can be verbose to work with (although more recent versions have gone some way to address this
  problem).

### Kotlin, Spring Boot, and Thymeleaf
* Kotlin is another JVM language, created more recently than Java, and aims to address some of the perceived problems
  with Java. It is interoperable with Java.
* Good, because it is used by other (modern) MHCLG services.
* Neutral, because although Kotlin is less well known than Java (10% of professional developers responding to the Stack
  Overflow 2023 survey) it is similar enough that developers with experience of Java should be able to learn it quickly.
* Good, because statically typed languages offer powerful tooling and can eliminate certain classes of errors at
  compile-time.
* Bad, because statically typed languages can be less flexible than dynamic languages, making e.g. prototyping
  potentially less rapid.
* Good, because Kotlin is less verbose to work with than Java.

### Ruby, Rails, and ERB

Ruby is a dynamically typed language with a focus on developer experience. Rails is by far the most popular web
application framework for Ruby. ERB is the default templating engine for Ruby / Rails (fulfilling a similar need to
Thymeleaf in the JVM world).
* Good, because it is used by other MHCLG services and within other government departments.
* Bad, because there is a relatively small market for developers with Ruby / Rails skills (7% of professional developers
  responding to the Stack Overflow 2023 survey use Ruby, 6% use Rails).
* Bad, because dynamically typed languages tend to offer less powerful tooling and cannot eliminate certain classes of
  errors ahead of run-time.
* Good, because dynamically typed languages lend themselves to rapid development of smaller scale work, e.g. prototypes.

## More Information

* Stack Overflow Survey 2023 results: https://survey.stackoverflow.co/2023/#most-popular-technologies-language-prof
* Review of the MHCLG technical landscape: [DLUHC Tech Landscape Review.docx](https://mhclg.sharepoint.com/:w:/s/PrivateRentedSector/EZp45cVALmBDl-MmTf5gd9cBajXyR87tPoGDom_OZFiMgg?e=GgSSh6)