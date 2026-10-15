# Backend Framework

* Status: Accepted
* Deciders: Habib Ullah, Casey Cheung, Rami Kotaiche
* Date: 2024-10-14

Technical Story: The backend requires a framework that efficiently handles operations for requests, database interactions, and other server-side logic.

## Context and Problem Statement

We need a light yet powerful backend framework to manage the demands of real-time data updates across platforms.

## Decision Drivers

* Real-Time Data Handling: Must be able to manage asynchronous operations efficiently
* Scalability: Must be able to handle an increasing number of users and data demands
* Performance: Lightweight runtime for fast response times.

## Considered Options

* Node.js
* Spring Boot (Java)

## Decision Outcome

Chosen option: "Node.js", because Node.js was chosen due to its asynchronous architecture, which is great for real-time updates and concurrent requirements. It is lightweight which ensures better performance for handling server-side logic and requests.

### Positive Consequences

* Lightweight and scalable.
* Supports asynchronous I/O operations, ideal for real-time updates.

### Negative Consequences

* Can be challenging for CPU-intensive tasks.
* Relatively new compared to more backend technologies.

## Pros and Cons of the Options

### Node.js

A JavaScript runtime for building server-side applications.

* Good, because - Extensive library support.
- Asynchronous, non-blocking I/O model supports scalability.
* Bad, because - Relatively new compared to other backend solutions.
- Challenges with CPU-intensive workloads.

### Spring Boot

A Java-based framework for building large scale applications.

* Good, because - Robust and ideal for large-scale applications.
- Strong support for microservices architecture.
* Bad, because - High memory consumption and slower startup time.
- Steeper learning curve.

## Links

* Node.js. (n.d.). Node.js documentation. Retrieved October 14, 2024, from https://nodejs.org
* Spring. (n.d.). Spring Boot documentation. Retrieved October 14, 2024, from https://spring.io/projects/spring-boot
* Stack Overflow. (2024). Node.js vs. Spring Boot discussions. Stack Overflow. Retrieved October 14, 2024, from https://stackoverflow.com
