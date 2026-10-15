# ADR-004: Repository Pattern for Data Access

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-001 (Inversify DI)](./ADR-001-inversify-dependency-injection.md), [ADR-012 (PostgreSQL)](./ADR-012-postgresql-supabase.md)

## Context

Sovren's data access layer was tightly coupled to Supabase client throughout the codebase:

- **Direct Database Coupling**: Services directly called `supabase.from('users').select()`
- **Scattered SQL**: Query logic duplicated across multiple files
- **Testing Difficulty**: Mocking Supabase client complex and brittle
- **Technology Lock-in**: Cannot switch databases without rewriting all services
- **No Query Optimization**: No centralized place for query tuning
- **Missing Business Logic**: Data access mixed with business logic

We needed a data access pattern that:
- Abstracts database implementation from business logic
- Provides clean interfaces for testing
- Centralizes query logic for optimization
- Enables database technology changes
- Supports caching and transaction management

## Decision

We will implement the **Repository Pattern** with interface-based abstractions for all data access.

**Implementation**:
```typescript
// Domain entity
interface User {
  id: string;
  email: string;
  publicKey: string;
  createdAt: Date;
}

// Repository interface
interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  findByPublicKey(publicKey: string): Promise<User | null>;
  create(user: Omit<User, 'id' | 'createdAt'>): Promise<User>;
  update(id: string, data: Partial<User>): Promise<User>;
  delete(id: string): Promise<void>;
  list(filters: UserFilters): Promise<User[]>;
}

// Concrete implementation
@injectable()
class SupabaseUserRepository implements IUserRepository {
  constructor(
    @inject(TYPES.Database) private db: SupabaseClient,
    @inject(TYPES.CacheService) private cache: ICacheService
  ) {}

  async findById(id: string): Promise<User | null> {
    // Check cache first
    const cached = await this.cache.get<User>(`user:${id}`);
    if (cached) return cached;

    // Query database
    const { data, error } = await this.db
      .from('users')
      .select('*')
      .eq('id', id)
      .single();

    if (error || !data) return null;

    const user = this.mapToEntity(data);

    // Cache result
    await this.cache.set(`user:${id}`, user, CACHE_TTL.user_profile);

    return user;
  }

  private mapToEntity(row: any): User {
    return {
      id: row.id,
      email: row.email,
      publicKey: row.public_key,
      createdAt: new Date(row.created_at)
    };
  }
}

// Service uses interface, not concrete implementation
@injectable()
class UserService {
  constructor(
    @inject(TYPES.UserRepository) private userRepo: IUserRepository
  ) {}

  async getUserProfile(id: string): Promise<UserProfile> {
    const user = await this.userRepo.findById(id);
    if (!user) throw new NotFoundError('User not found');

    return this.buildProfile(user);
  }
}
```

**Key Patterns**:
1. **Interface-Based**: All repositories define interface contracts
2. **Dependency Injection**: Repositories injected into services
3. **Entity Mapping**: Database rows mapped to domain entities
4. **Caching Integration**: Repositories handle caching transparently
5. **Transaction Support**: Repository methods support transactions

## Consequences

### Positive

1. **Testability**: Easy to mock repositories
   ```typescript
   const mockRepo: IUserRepository = {
     findById: jest.fn().mockResolvedValue(testUser),
     create: jest.fn(),
     // ...
   };

   const service = new UserService(mockRepo);
   ```

2. **Database Independence**: Can swap Supabase for PostgreSQL client
   - Create `PostgresUserRepository` implementing same interface
   - Change DI binding, no service code changes
   - Supports gradual migration strategies

3. **Centralized Queries**: All queries in one place
   - Easy to optimize slow queries
   - Consistent query patterns across app
   - Single place for caching logic

4. **Type Safety**: Strong typing for all data access
   - Compile-time errors for invalid queries
   - IntelliSense support for repository methods
   - No runtime query errors

5. **Business Logic Separation**: Clear boundaries
   - Repositories: Data access only
   - Services: Business logic only
   - Clean architecture principles

### Negative

1. **Boilerplate Code**: Need to create repository for each entity
   - Mitigation: Repository base class with common methods
   - Code generator for basic CRUD operations
   - Worth the long-term maintainability

2. **Learning Curve**: Team needs to understand pattern
   - Mitigation: Comprehensive documentation and examples
   - Standard pattern across industry

3. **Indirection**: Extra layer between service and database
   - Slight performance overhead (negligible)
   - Benefits outweigh minimal cost

4. **Generic Queries**: Hard to support arbitrary queries
   - Mitigation: Query builder methods for complex cases
   - Raw SQL escape hatch when needed

## Alternatives Considered

### 1. Active Record Pattern (like TypeORM entities)
**Pros**:
- Less boilerplate
- Entity methods feel natural

**Cons**:
- Couples domain model to database
- Hard to test (entities have DB dependencies)
- Limited flexibility for complex queries

**Why Rejected**: Tight coupling between domain and persistence violates clean architecture.

### 2. Direct Database Access
**Pros**:
- Simplest approach
- No abstraction overhead

**Cons**:
- Tight coupling to database technology
- Scattered queries across codebase
- Testing requires actual database
- No centralized optimization

**Why Rejected**: Doesn't scale as application grows. Makes testing and maintenance difficult.

### 3. ORMs (TypeORM, Prisma, Sequelize)
**Pros**:
- Automatic migrations
- Type-safe queries
- Active communities

**Cons**:
- Heavy dependencies
- Learning curve for ORM-specific APIs
- Performance overhead
- Lock-in to ORM patterns

**Why Rejected**: Repository pattern provides same benefits with less complexity and more control.

## Implementation Notes

**Repository Base Class**:
```typescript
abstract class BaseRepository<T, ID> {
  abstract findById(id: ID): Promise<T | null>;
  abstract create(data: Omit<T, 'id'>): Promise<T>;
  abstract update(id: ID, data: Partial<T>): Promise<T>;
  abstract delete(id: ID): Promise<void>;

  protected async withTransaction<R>(
    callback: (tx: Transaction) => Promise<R>
  ): Promise<R> {
    // Transaction handling
  }
}
```

**Pagination Support**:
```typescript
interface PaginationOptions {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  totalPages: number;
}

interface IUserRepository {
  list(
    filters: UserFilters,
    pagination: PaginationOptions
  ): Promise<PaginatedResult<User>>;
}
```

**Transaction Example**:
```typescript
class PaymentService {
  async processPayment(invoice: Invoice) {
    return await this.paymentRepo.transaction(async (tx) => {
      // Create payment record
      const payment = await this.paymentRepo.create(paymentData, tx);

      // Update user balance
      await this.userRepo.updateBalance(userId, amount, tx);

      // Record transaction
      await this.transactionRepo.create(transactionData, tx);

      return payment;
    });
  }
}
```

## Related Documentation

- [Repository Pattern Guide](/docs/development/backend-developer-guide.md#repository-pattern)
- [Data Access Architecture](/docs/architecture/diagrams/epic-005-data-access.mmd)
- [Database Schema](/docs/database/schema.md)
- [Testing Repositories](/docs/development/testing-guide.md#repositories)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
