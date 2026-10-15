# ADR 002: Database Architecture Evolution

## Status
Accepted

## Context
The Corner Shop application requires a database solution that can:
- Store product inventory data
- Track sales transactions
- Support basic reporting
- Be easily deployed and maintained
- Scale with growing business needs
- Support concurrent access
- Ensure data consistency
- Provide transaction management

## Decision Evolution

### Phase 1: MongoDB as Primary Database
Initially, we chose MongoDB as our primary database technology because:
- Flexible schema design allows for easy modifications to data models
- Document-based storage aligns well with our object-oriented codebase
- Excellent performance for read/write operations
- Native support for JSON-like documents
- Easy horizontal scaling
- Strong community support and documentation
- Good integration with .NET through MongoDB.Driver

### Phase 2: Dual Database Architecture
We evolved to implement dual database support:
1. MongoDB as primary NoSQL database
   - Document-based storage
   - Flexible schema
   - Good performance for read operations
   - Easy horizontal scaling
   - Native .NET driver support

2. Entity Framework Core with SQLite as relational database
   - Relational data model
   - ACID transactions
   - Built-in .NET integration
   - Lightweight and portable
   - No separate server required

## Alternatives Considered

### SQL Server
- Pros:
  - Strong ACID compliance
  - Familiar to many developers
  - Built-in data validation
- Cons:
  - More rigid schema
  - Higher resource requirements
  - More complex deployment

### SQLite (Standalone)
- Pros:
  - Simple deployment
  - No server required
  - Good for small applications
- Cons:
  - Limited scalability
  - Not suitable for concurrent access
  - Limited reporting capabilities

## Consequences

### Positive
- Flexibility in data storage
- Better performance for different use cases
- Data redundancy
- Easy switching between databases
- Simple deployment (especially SQLite)
- ACID compliance through EF Core
- Scalability through MongoDB
- Built-in .NET integration

### Negative
- Increased complexity in data synchronization
- Need to maintain two database implementations
- Potential consistency issues
- More complex testing requirements
- Additional development overhead
- Need for conflict resolution strategies

## Implementation Notes
- Using MongoDB.Driver 3.4.0 for .NET integration
- Using Entity Framework Core 6.0 with SQLite
- Implementing data validation in the application layer
- Using Docker for consistent deployment
- Implementing proper error handling for database operations
- Automatic synchronization between databases
- Transaction management through EF Core
- Conflict resolution strategy in place 