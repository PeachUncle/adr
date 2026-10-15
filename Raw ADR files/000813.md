# 005 - Choice of CQRS and Unit of Work Pattern for Business Process Changes

**Reporter:** Rafał Karaś

## Context

The decision pertains to the architectural approach to data management in the project. The optimal project structure is crucial for effectively handling business processes and transactions.

## Considered Options

- **Option #1** - Use of the CQRS pattern (Command Query Responsibility Segregation).
- **Option #2** - Implementation of the Unit of Work pattern for consistent transaction management during the storage of business processes.

## Decision

After a thorough analysis of the available options, the decision has been made to go with **Option #1**, which is the use of the CQRS pattern along with **Option #2**, which is the implementation of the Unit of Work pattern for consistent transaction management.

This decision is based on the following reasons:
1. **CQRS:** Separating responsibilities between queries and commands allows for more flexible and efficient data management, following the Single Responsibility Principle.
2. **Unit of Work Pattern:** It enables consistent transaction management during the storage of business processes, ensuring data integrity and facilitating diagnostics in case of transactional issues.

Potential issues related to performance and scalability will be monitored, and the approach can be adjusted according to the project's needs.

## Expected result

Adopting both the CQRS and Unit of Work patterns will enable efficient data management while ensuring consistency and data integrity during the storage of business processes.

Impact on:
- **Organization:** It will enable flexible data management depending on the type of operation.
- **Standardization:** It will safeguard the project from issues related to maintaining consistency during storage processes.
- **Concrete Solution:** It will provide a comprehensive approach to data management, considering both efficiency and data integrity.

Potential negative consequences:
- The need for adaptation for individuals who have not worked with the CQRS and Unit of Work patterns before.

## Links

- [MediatR](https://github.com/jbogard/MediatR)
- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Unit of Work Pattern](https://martinfowler.com/eaaCatalog/unitOfWork.html)