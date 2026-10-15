# Use of Transactions in Use-Cases

Date: 2024-06-10

## Status

2024-06-10 accepted

## Context

In the development of our application, ensuring data consistency and integrity is paramount, especially when dealing with operations that span multiple tables or services. Our initial implementation of transaction management was confined to domain events within the aggregate repository and then propagated to the aggregate entity class. While this approach was functional for domain events, it lacked the flexibility to encompass other parts of use-cases within a single transaction, leading to potential inconsistencies in broader application operations.

This limitation prompted us to explore more comprehensive solutions for transaction management that could encapsulate the entirety of a use-case within a single transactional context. The goal was to find a method that would not only maintain data integrity across the application but also integrate seamlessly with our existing codebase without necessitating extensive modifications or complex testing scenarios.

After careful consideration, we decided to use the `@nestjs-cls/transactional` package. This package simplifies transaction management by automatically handling transactions within the context of use-cases only by adding single `@Transactional()` decorator. It ensures that all underlying queries, including those from nested method calls, run within a single transaction, thus maintaining data integrity and consistency across the entire scope of a use-case without the need for extensive boilerplate code.


## Decision

We have decided to use the `@nestjs-cls/transactional` package for managing transactions in our use-cases. This decision was made to minimize the impact on the existing codebase, reduce the complexity of implementing transaction management manually, and ensure that our application can maintain data integrity and consistency in a straightforward and effective manner.

Additionally, we considered other patterns and packages, such as:

- **Manual Transaction Management**: Directly managing transactions by obtaining and passing transaction objects. This approach was deemed too invasive and complex for our current architecture.
- **Repository Pattern**: Encapsulating the logic needed to access data sources. While this pattern is beneficial, it would require significant changes to our existing codebase and testing strategy.
- **Other ORM/Database Abstraction Layers**: Various ORMs and database abstraction layers offer built-in transaction management. However, these solutions did not offer the simplicity and ease of integration provided by `@nestjs-cls/transactional`.

## Consequences

- **Reduced Complexity**: By using `@nestjs-cls/transactional`, we avoid the complexity of manually managing transaction objects and reduce the risk of errors.
- **Ease of Testing**: This approach simplifies testing by abstracting the transaction management, allowing us to focus on the business logic.
- **Codebase Impact**: The decision minimizes the impact on the existing codebase, allowing for a smoother integration and adoption process.
- **Flexibility**: Should future requirements necessitate a different approach to transaction management, we may need to re-evaluate this decision and consider alternative strategies.

## References

- `@nestjs-cls/transactional` package documentation: [https://www.npmjs.com/package/@nestjs-cls/transactional](https://www.npmjs.com/package/@nestjs-cls/transactional)