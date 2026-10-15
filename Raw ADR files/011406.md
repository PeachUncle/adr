# ADR 003: Recipe-Based Meal Creation

## Status

Proposed

## Context

The meal planner currently only supports adding individual foods to meals. Users need the ability to:

1. Create meals through text descriptions
2. Create meals from full recipes with ingredients and instructions
3. Create meals by scanning barcodes of ingredients and specifying portions

## Decision

We will extend the system to support recipe-based meals through these architectural changes:

### 1. Data Model Extensions

```typescript
interface RecipeIngredient {
  food: Food;
  amount: number;
  unit: ServingSizeUnit;
}

interface Recipe {
  id: string;
  name: string;
  description?: string;
  ingredients: RecipeIngredient[];
  instructions: string[];
  servings: number;
  totalNutrition: NutritionInfo;
  category: CategoryType;
  meal: MealType[];
}
```

### 2. New Service Layer Components

- RecipeService for managing recipes
- Recipe to MealSelection converter
- Enhanced UPC scanning service for ingredients

### 3. API Extensions

- `/api/recipes/` endpoints for CRUD operations
- `/api/recipes/convert` for converting recipes to MealSelections
- Enhanced `/api/upc/` endpoint for ingredient lookup

### 4. UI Components

New components in `src/components/features/recipes/`:

- RecipeEditor
- RecipeIngredientScanner
- RecipeConverter

## Consequences

### Positive

- More flexible meal creation options
- Better support for complex meals
- Improved user experience for meal planning
- Reusable recipe components

### Negative

- Increased system complexity
- Need to maintain compatibility with existing meal structure
- Additional storage requirements for recipes

### Mitigations

- Clear separation of concerns between recipe and meal components
- Strong typing to ensure data consistency
- Comprehensive testing of conversion logic

## Implementation Plan

1. Create new types and database schemas
2. Implement core recipe service
3. Add API endpoints
4. Create UI components
5. Integrate with existing meal planner

## Technical Details

### Recipe to MealSelection Conversion

Recipes will be converted to MealSelections by:

1. Analyzing ingredient categories
2. Calculating nutritional totals
3. Distributing ingredients into appropriate food categories
4. Creating composite foods when needed

### Barcode Scanning Integration

The existing UPC scanning will be enhanced to:

1. Support multiple scans per recipe
2. Store ingredient relationships
3. Calculate portion-based nutrition

## Testing Strategy

1. Unit tests for conversion logic
2. Integration tests for recipe creation flows
3. E2E tests for barcode scanning
4. Performance testing for recipe operations
