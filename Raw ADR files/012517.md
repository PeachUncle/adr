# Choosing the Backend Language for the Banking Core System
- Status: accepted
- Deciders: @hansen1904
- Date: 2024-12-08

## Context and Problem Statement
We need to select the most appropriate programming language for developing the core banking system of Nordic Bank. The language must meet our requirements for security, performance, maintainability, and scalability. The decision is critical as it will affect the future development and operation of the system.

## Decision Drivers
- Security: The language must support secure coding practices and offer robust security features.
- Performance: The language must deliver high performance to handle large volumes of transactions efficiently.
- Maintainability: The language must be easy to maintain, with a strong ecosystem and community support.
- Scalability: The language must support scalable architecture to accommodate future growth.
- Developer Expertise: The language must align with the current skills and expertise of our development team.

## Considered Options
- C#
- Go

## Decision Outcome
Chosen option: "Go", because it is designed for concurrency and performance, making it highly efficient. It has a simple syntax, which can lead to faster development and easier maintenance. Additionally, it is backed by a strong community and has growing support.

### Positive Consequences
- High performance and scalability, capable of handling large volumes of transactions.
- Simple syntax, leading to faster development and easier maintenance.
- Strong support for concurrency, making it well-suited for modern, scalable applications.
- Growing community support and ecosystem.

### Negative Consequences
- Relatively new compared to C#, which might lead to a steeper learning curve for some team members.

## Pros and Cons of the Options

### C#
- **Pros**:
    - Offers strong security features.
    - Has a robust framework with .NET.
    - Integrates well with Microsoft products and services.
- **Cons**:
    - May have higher runtime memory consumption compared to more lightweight languages.
    - Development environment setup can be more complex, especially on non-Windows platforms.

### Go
- **Pros**:
    - Designed for concurrency and performance, making it highly efficient.
    - Simple syntax, which can lead to faster development and easier maintenance.
    - Backed by a strong community and has growing support.