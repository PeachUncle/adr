# ADR: Backend Language Selection

## Context
Selecting a backend framework for the AML system to ensure high performance, scalability, and efficient handling of API requests. The goal is to support the frontend effectively while enabling secure and scalable interactions within a microservices-based architecture.

## Problem Statement
The AML system needs a backend framework that facilitates rapid API development, is scalable, and is compatible with our chosen frontend and database technologies. The framework should be reliable, efficient for high-traffic environments, and adaptable to future functionality.

## Considered Options
- Express.js
- Django
- Spring Boot
  
## Decision Outcome Confirmation
After evaluating various backend frameworks, Express.js has been chosen as the backend framework for the AML system. Express.js is a minimal, flexible Node.js framework that is highly efficient for handling asynchronous requests, making it a strong choice for creating RESTful APIs. It aligns well with our JavaScript-based frontend (Next.js) and offers extensive flexibility and scalability in a microservices architecture.

## Consequences
Using Express.js enables seamless integration with the Node.js ecosystem, ensuring efficient API development and data handling. The lightweight and flexible nature of Express.js supports high scalability and adaptability for future expansions. Its compatibility with our chosen frontend and database systems reduces integration complexity and enhances development speed.

## Pros
- Lightweight and Fast: Express.js is designed for high performance and fast handling of asynchronous requests, which is essential for large-scale systems.
- JavaScript Consistency: Being a Node.js framework, Express.js allows for a unified JavaScript development environment across frontend and backend, enhancing development consistency.
- Microservices Support: Express.js's modularity and flexibility are ideal for microservices, allowing for isolated, manageable services.
- Extensive Ecosystem: As one of the most popular Node.js frameworks, Express.js offers numerous libraries and plugins to extend functionality.
  
## Cons
- Less Structure for Large Applications: Being minimalistic, Express.js requires additional effort to organize complex applications, which could increase development time for large systems.
- Manual Setup for Some Features: Unlike more opinionated frameworks, Express.js does not come with built-in solutions for features like ORM integration, requiring additional setup.
  
## Confirmations
We have confirmed Express.js as the backend framework for the AML system due to its performance, scalability, and compatibility with our chosen frontend and database solutions. This decision supports a consistent, adaptable, and high-performing backend that meets both current and projected needs.

## Pros and Cons of Options
**Django**
**Pros:**

- High-Level, Opinionated Framework: Django offers a "batteries-included" approach, simplifying development with built-in ORM, authentication, and admin panel.
- Security Features: Django has robust security features, making it ideal for systems with sensitive data.
- Python-Based: A good choice if the team is skilled in Python, with strong support for data processing tasks.
  
**Cons:**

- Lower Performance for High-Volume APIs: Compared to Node.js-based frameworks, Django may not perform as well in handling large numbers of concurrent requests.
- Less Ideal for Microservices: Django’s monolithic structure can be limiting in microservices architectures.
  
**Spring Boot**
**Pros:**

- Java-Based: Suitable for teams experienced with Java, Spring Boot offers powerful support for enterprise-grade applications.
- Comprehensive Framework: Spring Boot comes with built-in support for security, ORM, and microservices.
- Scalable and Reliable: Well-suited for handling complex and high-traffic applications, making it robust for scalable solutions.
  
**Cons:**

- Steeper Learning Curve: Spring Boot requires a greater setup and learning investment.
- Resource Intensive: Applications built with Spring Boot may require more resources, impacting hosting costs in some cases.



