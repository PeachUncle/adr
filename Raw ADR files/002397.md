# 5. Use dotnet core for backend services

Date: 2023-05-21

## Status

Accepted

## Context

A language and framework is needed for backend services.

.NET Core offers a robust and mature framework for building microservices. It provides a wide range of libraries and
tools that facilitate the development of scalable and high-performance applications. With its performance optimizations
and efficient memory management, .NET Core can handle the demanding requirements of Kwetter's backend services.

Java is a widely-used language for building backend applications, including microservices. However, the decision to not
choose Java for Kwetter was based on the expertise of the development team. If the team lacks experience and proficiency
in Java, it could lead to longer development cycles and potentially impact the quality and maintainability of the
codebase. By leveraging .NET Core, which the team is well-versed in, Kwetter can ensure faster development cycles and a
higher level of code quality.

Python, on the other hand, is known for its simplicity and ease of use. However, it may not be the most performant
option for Kwetter's backend microservices. Python's interpreted nature and Global Interpreter Lock (GIL) can introduce
limitations in terms of scalability and concurrent execution. Given Kwetter's need for handling a large number of
concurrent requests and ensuring optimal performance, Python might not provide the desired level of performance required
for the platform.

## Decision

.NET Core was chosen for Kwetter's backend microservices due to its strong features and capabilities that align with the
platform's requirements. The decision to choose .NET Core was made after considering other options, such as Java and
Python, and taking into account the expertise of the development team and performance considerations.

## Consequences

By choosing .NET Core for Kwetter's backend microservices, the development team can leverage their existing expertise
and experience with the framework. This results in a reduced learning curve and improved productivity. Additionally,
.NET Core's performance optimizations and scalability features enable Kwetter to handle high loads and scale efficiently
as the user base grows.
