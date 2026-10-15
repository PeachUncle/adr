# ADR-002: Database Schema Design

## Status
Accepted

## Context
The Recipe Keeper application needs to store complex recipe data including:
- Recipe metadata (title, rating, prep time, etc.)
- Variable-length ingredients lists with quantity, unit, and item
- Step-by-step directions
- Nutritional information
- Tags and categories
- User associations
- Recipe photos and metadata

The data structure needs to be flexible enough to handle recipes from various sources (manual entry, AI extraction, URL imports) while maintaining performance for search and filtering operations.

## Considered Options

### Option 1: Fully Normalized Relational Schema
```sql
recipes (id, title, rating, prep_time, cook_time, servings, difficulty, created_at, updated_at)
ingredients (id, recipe_id, quantity, unit, item, order)
directions (id, recipe_id, step, instruction)
nutrition (id, recipe_id, calories, protein, carbs, fat, fiber, sodium)
tags (id, name)
recipe_tags (recipe_id, tag_id)
```

**Pros:**
- Strict data integrity
- Efficient storage for large datasets
- Easy to query individual components
- Standard SQL operations

**Cons:**
- Complex queries for full recipe retrieval
- Multiple joins for recipe display
- Rigid structure for AI-extracted data
- Difficult to handle varying nutrition data

### Option 2: Document-Oriented (JSON) Schema
```sql
recipes (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  rating INTEGER,
  prep_time INTEGER,
  cook_time INTEGER,
  servings INTEGER,
  difficulty VARCHAR(50),
  recipe_data JSONB,  -- Contains ingredients, directions, nutrition
  tags TEXT[],
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

**Pros:**
- Flexible schema for varying data
- Single query for complete recipe
- Perfect for AI-extracted data
- Easy to evolve schema

**Cons:**
- Less structured data validation
- Harder to query specific ingredient
- Potential for data inconsistency
- PostgreSQL-specific features

### Option 3: Hybrid Approach
```sql
recipes (
  id UUID PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  photo_url TEXT NOT NULL,
  prep_time INTEGER,
  cook_time INTEGER,
  servings INTEGER,
  difficulty VARCHAR(50),
  ingredients JSONB NOT NULL,
  directions JSONB NOT NULL,
  nutrition JSONB,
  tags TEXT[],
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

**Pros:**
- Structured metadata for querying
- Flexible JSON for complex data
- Good balance of flexibility and structure
- Optimized for application use cases

**Cons:**
- Mixed paradigm complexity
- Some PostgreSQL-specific features
- Requires careful JSON schema design

## Decision

We chose **Option 3: Hybrid Approach** with structured metadata and JSONB columns for complex data.

### Rationale

1. **Performance**: Single table queries for recipe display are faster than multiple joins
2. **Flexibility**: JSONB allows for varying ingredient counts and nutrition data
3. **AI Integration**: Easy to store variable AI-extracted data without schema changes
4. **Search**: PostgreSQL's JSONB indexing supports efficient ingredient searches
5. **Evolution**: Schema can evolve without migrations for JSON data
6. **Validation**: Application-level validation provides flexibility while maintaining data quality

## Schema Design

### Main Recipe Table
```sql
CREATE TABLE recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  photo_url TEXT NOT NULL,
  prep_time INTEGER CHECK (prep_time >= 0),
  cook_time INTEGER CHECK (cook_time >= 0),
  servings INTEGER CHECK (servings > 0),
  difficulty VARCHAR(50) CHECK (difficulty IN ('easy', 'medium', 'hard')),
  ingredients JSONB NOT NULL,
  directions JSONB NOT NULL,
  nutrition JSONB,
  tags TEXT[],
  source_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### JSON Schema Definitions

#### Ingredients Format
```json
[
  {
    "quantity": "2",
    "unit": "cups",
    "item": "all-purpose flour"
  },
  {
    "quantity": "1",
    "unit": "tsp",
    "item": "salt"
  }
]
```

#### Directions Format
```json
[
  {
    "step": 1,
    "instruction": "Preheat oven to 350°F (175°C)"
  },
  {
    "step": 2,
    "instruction": "Mix dry ingredients in a large bowl"
  }
]
```

#### Nutrition Format
```json
{
  "calories": 250,
  "protein": 8,
  "carbohydrates": 35,
  "fat": 10,
  "fiber": 3,
  "sodium": 300,
  "sugar": 5
}
```

### Indexes for Performance
```sql
-- Full-text search on title and ingredients
CREATE INDEX idx_recipes_fulltext ON recipes USING gin(to_tsvector('english', title || ' ' || ingredients));

-- Ingredient search
CREATE INDEX idx_recipes_ingredients ON recipes USING gin(ingredients);

-- Tag search
CREATE INDEX idx_recipes_tags ON recipes USING gin(tags);

-- Common filters
CREATE INDEX idx_recipes_difficulty ON recipes(difficulty);
CREATE INDEX idx_recipes_cook_time ON recipes(cook_time);
CREATE INDEX idx_recipes_rating ON recipes(rating);
CREATE INDEX idx_recipes_created_at ON recipes(created_at);

-- User recipes
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
```

## Consequences

### Positive
- **Single Query Performance**: Complete recipe retrieval in one query
- **Flexible Data Structure**: Can handle varying ingredient counts and nutrition data
- **AI Integration**: Easy to store AI-extracted data without schema changes
- **Search Capabilities**: PostgreSQL's JSONB indexing enables efficient searches
- **Schema Evolution**: JSON data can evolve without database migrations
- **Type Safety**: Prisma generates TypeScript types for the schema

### Negative
- **PostgreSQL Dependency**: JSONB is PostgreSQL-specific
- **JSON Validation**: Requires application-level validation for JSON structure
- **Complex Queries**: Some queries on JSON data are more complex than SQL
- **Storage Overhead**: JSON storage has some overhead compared to normalized data
- **Learning Curve**: Developers need to understand JSONB operations

### Neutral
- **Migration Complexity**: Future schema changes require careful planning
- **Backup/Restore**: JSON data requires special consideration in backups
- **Analytics**: External analytics tools may need special JSON handling

## Implementation Details

### Prisma Schema
```prisma
model Recipe {
  id          String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  userId      String   @map("user_id") @db.Uuid
  title       String   @db.VarChar(255)
  rating      Int?     @db.Integer
  photoUrl    String   @map("photo_url")
  prepTime    Int?     @map("prep_time")
  cookTime    Int?     @map("cook_time")
  servings    Int?
  difficulty  String?  @db.VarChar(50)
  ingredients Json
  directions  Json
  nutrition   Json?
  tags        String[]
  sourceUrl   String?  @map("source_url")
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")
  
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("recipes")
}
```

### TypeScript Types
```typescript
interface Recipe {
  id: string;
  userId: string;
  title: string;
  rating?: number;
  photoUrl: string;
  prepTime?: number;
  cookTime?: number;
  servings?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  ingredients: Ingredient[];
  directions: Direction[];
  nutrition?: Nutrition;
  tags: string[];
  sourceUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### Validation Rules
- **Ingredients**: Must be non-empty array with required fields
- **Directions**: Must be non-empty array with sequential steps
- **Nutrition**: Optional but validated when present
- **Tags**: Maximum 10 tags, each max 50 characters
- **Rating**: Must be between 1 and 5 if provided

## Related ADRs
- [ADR-001: Technology Stack Selection](./001-technology-stack.md)
- [ADR-003: AI Service Integration](./003-ai-integration.md)

## Review Date
This decision should be reviewed if:
- Performance issues arise with JSON queries
- Need for complex relational queries increases
- Migration to different database becomes necessary
- JSON schema becomes too complex to maintain