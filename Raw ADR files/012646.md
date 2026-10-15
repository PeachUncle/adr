# ADR-5: ORM Abstraction for Database Operations

## Status
Accepted

## Date
2025-03-16

## Context
The Recipe Management System currently uses Prisma ORM for database operations due to its type safety, ease of use, and productivity benefits. However, there is a strategic plan to potentially migrate to Drizzle ORM or MikroORM in the future for reasons including:

- Performance considerations
- Bundle size optimization
- More flexible query capabilities
- Reduced dependency weight

Moving from one ORM to another presents significant challenges:
- Database access code is typically spread throughout the application
- Each ORM has different APIs and paradigms
- Migration would touch many files, increasing risk
- Features may not map directly between ORMs

While we could defer this concern, we want to design the system to minimize the future migration effort and risk.

## Decision
We will implement the Repository Pattern to abstract ORM-specific code from the rest of the application. Specifically:

1. Define repository interfaces for each domain entity (Recipe, Ingredient, etc.)
2. Create Prisma implementations of these repositories
3. Keep ORM-specific code isolated to repository implementations
4. Use dependency injection to provide repository instances to services

### Repository Interface Example

```typescript
// src/recipe/repositories/recipe.repository.ts
export interface RecipeRepository {
  findById(id: string): Promise<Recipe>;
  findAll(params: RecipeQueryParams): Promise<PaginatedResult<Recipe>>;
  create(data: CreateRecipeDto): Promise<Recipe>;
  update(id: string, data: UpdateRecipeDto): Promise<Recipe>;
  delete(id: string): Promise<void>;
  
  // Domain-specific methods
  findByIngredient(ingredientName: string): Promise<Recipe[]>;
  findByTags(tags: string[]): Promise<Recipe[]>;
  countByAuthor(authorId: string): Promise<number>;
}
```

### Prisma Implementation

```typescript
// src/recipe/repositories/prisma-recipe.repository.ts
@Injectable()
export class PrismaRecipeRepository implements RecipeRepository {
  constructor(private prisma: PrismaService) {}
  
  async findById(id: string): Promise<Recipe> {
    return this.prisma.recipe.findUnique({
      where: { id },
      include: { author: true }
    });
  }
  
  async findAll(params: RecipeQueryParams): Promise<PaginatedResult<Recipe>> {
    const { page, limit, search, tags } = params;
    const skip = (page - 1) * limit;
    
    const where = {
      ...(search && {
        OR: [
          { title: { contains: search, mode: 'insensitive' } },
          { description: { contains: search, mode: 'insensitive' } }
        ]
      }),
      ...(tags && { tags: { some: { name: { in: tags } } } })
    };
    
    const [data, total] = await Promise.all([
      this.prisma.recipe.findMany({
        where,
        skip,
        take: limit,
        include: { author: true }
      }),
      this.prisma.recipe.count({ where })
    ]);
    
    return {
      data,
      meta: {
        total,
        page,
        limit,
        pageCount: Math.ceil(total / limit)
      }
    };
  }
  
  // Other methods...
}
```

### Future Drizzle Implementation

```typescript
// src/recipe/repositories/drizzle-recipe.repository.ts
@Injectable()
export class DrizzleRecipeRepository implements RecipeRepository {
  constructor(private db: DrizzleService) {}
  
  async findById(id: string): Promise<Recipe> {
    const result = await this.db.query.recipes.findFirst({
      where: eq(recipes.id, id),
      with: { author: true }
    });
    
    if (!result) throw new NotFoundException(`Recipe with ID ${id} not found`);
    return result;
  }
  
  async findAll(params: RecipeQueryParams): Promise<PaginatedResult<Recipe>> {
    const { page, limit, search, tags } = params;
    const offset = (page - 1) * limit;
    
    let query = this.db.select().from(recipes);
    
    if (search) {
      query = query.where(
        or(
          like(recipes.title, `%${search}%`),
          like(recipes.description, `%${search}%`)
        )
      );
    }
    
    if (tags) {
      // Drizzle-specific implementation for tags filter
    }
    
    const [data, countResult] = await Promise.all([
      query.limit(limit).offset(offset).execute(),
      this.db.select({ count: count() }).from(recipes).execute()
    ]);
    
    const total = countResult[0].count;
    
    return {
      data,
      meta: {
        total,
        page,
        limit,
        pageCount: Math.ceil(total / limit)
      }
    };
  }
  
  // Other methods...
}
```

### Dependency Provision

```typescript
// src/recipe/recipe.module.ts
@Module({
  providers: [
    RecipeService,
    PrismaService,
    {
      provide: RecipeRepository,
      useClass: PrismaRecipeRepository
    }
  ],
  controllers: [RecipeController]
})
export class RecipeModule {}
```

## Alternatives Considered

### 1. Direct ORM Usage Throughout Codebase

Use Prisma directly in services and controllers.

**Pros:**
- Simpler implementation
- Less abstraction overhead
- Full access to ORM-specific features
- No additional conceptual layer

**Cons:**
- High coupling to Prisma
- Migration to Drizzle would require changes in many files
- Testing more difficult due to ORM coupling
- Higher risk of breaking changes when upgrading

### 2. Query Builder Abstraction

Use a query builder approach rather than full repositories.

**Pros:**
- More granular control over queries
- Potentially easier to map between ORMs
- More flexible query construction
- Potentially better performance

**Cons:**
- More boilerplate code
- Loss of some ORM benefits
- Less clear domain organization
- Still requires adapters for each ORM

### 3. Micro-ORM with Pluggable Drivers

Use or build a micro-ORM with interchangeable drivers.

**Pros:**
- Built-in abstraction
- Minimal code changes for ORM switch
- Single querying API
- More consistent behavior

**Cons:**
- Additional dependency or significant development effort
- Potential limitations compared to native ORMs
- May limit access to ORM-specific features
- Could become another maintenance burden

### 4. Database Service Layer

Create service classes that encapsulate database operations.

**Pros:**
- Familiar pattern for many developers
- Less strict than repository pattern
- Can leverage ORM-specific features
- Potentially simpler implementation

**Cons:**
- Less clear separation of concerns
- Might still leak ORM details into business logic
- Testing could be more complex
- Harder to enforce consistency

## Rationale

The Repository Pattern provides several advantages that align with our needs:

1. **Clear Separation**: ORM-specific code is isolated to repository implementations
2. **Domain Focus**: Repositories express domain operations, not just CRUD
3. **Testability**: Services can be tested with repository mocks
4. **Migration Path**: Switching ORMs requires changes only to repository implementations
5. **Consistency**: Repository pattern encourages consistent data access patterns

While this approach adds some abstraction overhead, the benefits for future maintainability and migration flexibility outweigh the costs. The Repository Pattern is also well-established in enterprise software, making it familiar to many developers.

The implementation allows us to leverage Prisma's strengths now while planning for a smooth transition to Drizzle in the future. This approach specifically addresses the project's requirement to support a future ORM migration with minimal disruption.

## Consequences

### Positive
- Clear migration path to Drizzle with minimal disruption
- Better testability through repository interfaces
- Improved separation of concerns
- Domain-focused data access operations
- Consistent querying patterns

### Negative
- Additional abstraction layer
- Some duplication of data structures
- Cannot fully leverage ORM-specific features without leaking abstraction
- Slightly increased development effort

### Neutral
- Need to maintain discipline in keeping ORM code isolated
- Repository methods must be designed to accommodate both ORMs' capabilities
- May need to evolve interfaces as requirements change

## Implementation Plan

1. **Phase 1**: Define core repository interfaces
