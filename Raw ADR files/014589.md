# Architectural Decision Record: Technology Stack Selection

## Status

Accepted (unanymously, i'm the only dev)

## Date

2025-05-30

## Context

When starting the Proletariat Budget application, we needed to select a technology stack that would provide a solid foundation for building a reliable, maintainable, and scalable financial management system. The key components of this stack include:

1. Backend programming language and framework
2. Database management system
3. Frontend framework

We needed to consider factors such as:
- Development speed and efficiency
- Cross-platform compatibility
- Performance characteristics
- Team expertise and learning curve
- Long-term maintainability
- Cloud deployment options
- Community support and ecosystem

## Decision

We have decided to use the following technology stack:

1. **Backend**: Go (Golang)
2. **Database**: MySQL
3. **Frontend**: Angular (version 19+)

## Rationale

### Go (Golang) for Backend

1. **Simplicity**: Go's straightforward syntax and minimal feature set reduce cognitive overhead and make the codebase more approachable for new developers.

2. **Cross-platform Compatibility**: Go compiles to native binaries for multiple architectures (x86, ARM, etc.) without dependencies, making deployment flexible across different environments.

3. **Plugin Architecture**: Go's plugin system allows for modular code organization and potential runtime extensions, supporting a more adaptable application structure.

4. **Development Speed**: Go's fast compilation, built-in testing framework, and straightforward concurrency model accelerate the development cycle.

5. **Performance**: Go's compiled nature and efficient garbage collection provide excellent performance characteristics for API services.

6. **Strong Standard Library**: Go's comprehensive standard library reduces dependency on third-party packages for common functionality.

### MySQL for Database

1. **Cross-platform Availability**: MySQL runs on virtually all operating systems and architectures, aligning with our cross-platform goals.

2. **Simplicity**: MySQL offers a straightforward setup, administration, and query language that reduces operational complexity.

3. **Cloud Compatibility**: Using MySQL allows us to seamlessly migrate to Amazon Aurora DB on AWS if needed, without changing our application code due to compatible adapters in Go.

4. **Maturity and Reliability**: MySQL is a battle-tested database with decades of production use across countless applications.

5. **Transactional Support**: MySQL's ACID compliance ensures data integrity for financial transactions.

6. **Scalability Options**: MySQL provides various replication and clustering options to scale as our user base grows.

### Angular (v19+) for Frontend

1. **Standalone Components**: Angular 19+ supports standalone components, reducing boilerplate and enabling more modular code organization.

2. **Reactive Resources**: Angular's reactive approach, particularly with newer features like signals and reactive resources, provides elegant handling of API calls, loading states, and response caching.

3. **Type Safety**: Angular's TypeScript foundation aligns with our emphasis on type safety across the stack.

4. **Comprehensive Framework**: Angular provides a complete solution including routing, forms, HTTP client, and testing tools, reducing the need to evaluate and integrate separate libraries.

5. **Long-term Support**: Google's backing and Angular's predictable release schedule provide confidence in long-term maintenance.

6. **Enterprise Readiness**: Angular's architecture is well-suited for large-scale applications with complex business logic.

## Consequences

### Positive

1. **Consistent Development Experience**: All three technologies emphasize strong typing and structured development approaches.

2. **Deployment Flexibility**: The stack can be deployed on-premises or in various cloud environments with minimal adjustments.

3. **Performance**: Both Go and Angular are known for good performance characteristics, and MySQL can be optimized for our specific use cases.

4. **Maintainability**: All three technologies have clear conventions and patterns that promote maintainable code.

5. **Scalability**: Each component of the stack has proven scaling capabilities for growing applications.

### Negative

1. **Learning Curve**: Team members unfamiliar with any of these technologies will need time to become proficient.

2. **Ecosystem Integration**: Some third-party tools or libraries might not integrate as seamlessly across this specific stack compared to more common combinations.

3. **Operational Complexity**: Managing MySQL at scale requires database administration expertise that the team may need to develop.

4. **Angular Updates**: Angular's frequent release cycle requires ongoing attention to keep the frontend updated.

## Alternatives Considered

### Backend Alternatives

1. **Node.js/Express**: Would provide JavaScript consistency across the stack but lacks Go's performance characteristics and type safety.

2. **Java/Spring**: Offers robust enterprise features but has a steeper learning curve and more verbose development process.

3. **Python/Django or Flask**: Would enable rapid development but might face performance challenges at scale compared to Go. Also, the dev does not know Python :)

### Database Alternatives

1. **PostgreSQL**: Offers more advanced features than MySQL but might be more complex for our current needs.

2. **MongoDB**: Would provide schema flexibility but cloud providers for this are way more expensive, and the footprint to start an instance is larger than MySQL.

3. **SQLite**: Would be simpler and way more faster, but the adapter would only work for this database while MySQL would also work for cloud providers like AWS or GCP.

### Frontend Alternatives

1. **React**: Offers a larger ecosystem and more flexibility but requires more decisions about additional libraries and architecture.

2. **Vue.js**: Provides a gentler learning curve but lacks some of Angular's built-in features for enterprise applications.

3. **Svelte**: Offers excellent performance but has a smaller ecosystem and less enterprise adoption.

## Implementation Notes

1. **API Design**: We'll use OpenAPI specifications to define the contract between our Go backend and Angular frontend.

2. **Database Access**: We'll use a clean repository pattern in Go to abstract database operations, making potential future database migrations easier.

3. **Frontend State Management**: We'll leverage Angular's reactive resources and signals for state management rather than introducing additional libraries.

4. **Deployment Strategy**: We'll containerize the application components for consistent deployment across environments.

## References

- [Go Documentation](https://golang.org/doc/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Angular Documentation](https://angular.io/docs)
- [AWS Aurora DB Compatibility](https://aws.amazon.com/rds/aurora/mysql-features/)