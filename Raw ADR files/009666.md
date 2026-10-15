# PHP Frameworks Architectural Decision Record

* Status: accepted
* Date: 2024-11-17 
* Decision-Makers: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz
* Consulted: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz
* Informed: Oliver Sennett-Neilson, Conner Bowen, Harris Fiaz

## Context and Problem Statement

The Advanced Media Library (AML) system is required to allow users to search, borrow, and return media, manage accounts, and check branch availability for media. A robust and reliable framework for the web application is necessary to ensure scalability, performance, and maintainability.

After evaluating various options, Laravel and CodeIgniter emerged as the most suitable candidates for this project.

## Decision Drivers

* Scalability: Support anticipated user growth with a scalable backend framework.
* Authentication: Implement token-based authentication for improved performance and security.
* Performance: Reduce server-side overhead with client-stored authentication tokens.
* Maintainability: Use built-in tools and a modular structure to simplify debugging and future updates.

## Considered Options

### 1. Laravel
* Modern framework with MVC structure.
* Built-in tools for routing, authentication, and database management.

### 2. CodeIgniter
* Lightweight framework with basic libraries.
* Less feature-rich but simple and easy to use.

## Decision Outcome

Chosen option: Laravel

Justification:
Laravel's extensive built-in tools and scalability features make it ideal for a large-scale project like AML. Its compatibility with SQL and support for token authentication allows us to build a robust system with minimal redundant coding. While Laravel has a steeper learning curve, its modularity and strong community support mitigate this challenge, ensuring a long-term maintainable solution.

## Consequences

Good:
* Scalable architecture to handle anticipated user growth.
* Enhanced performance with client-side token authentication.
* Improved data security through built-in features like encryption and CSRF protection.
* Modular design simplifies debugging and testing.

Bad:
* Steeper learning curve for team members unfamiliar with Laravel.
* Strict MVC structure may add complexity in the initial stages.

## Confirmation

The implementation will be validated through:
* Code Reviews: Ensure Laravel's features are used optimally.
* Performance Testing: Verify scalability and load handling under peak conditions.
* Security Audits: Confirm proper implementation of Laravel's authentication and security features.
* Developer Feedback: Regular reviews to address challenges arising from the learning curve.

## Pros and Cons of the Options

### Laravel
* Good: Scalable, secure, and feature-rich with a large community and extensive documentation.
* Neutral: Steeper learning curve mitigated by strong community support.
* Bad: Heavier than lightweight frameworks like CodeIgniter.

### CodeIgniter
* Good: Lightweight and fast, with minimal resource overhead.
* Neutral: Limited features that can be extended with third-party libraries.
* Bad: Lacks modular structure, making testing and scaling difficult.

## More Information

References:
1. [Laravel Official Documentation](https://laravel.com/docs)
2. [Comparison of Laravel and CodeIgniter](https://www.geeksforgeeks.org/difference-between-laravel-and-codeigniter/)
3. [Token-Based Authentication in Laravel](https://laravel.com/docs/8.x/passport)