# ADR-3: Schema-Driven Form Management

## Status
Accepted

## Date
2025-03-16

## Context
Our recipe management system requires numerous forms (20+) for various operations including:

- Recipe creation and editing
- Ingredient management
- Cooking steps sequencing
- Recipe imports from various sources
- Profile and preference settings
- Multi-step workflows

Each of these forms has specific validation requirements, UI presentation needs, and complex interdependencies. Maintaining consistency between frontend validation and backend requirements is critical to ensure data integrity and user experience.

Traditional approaches would require duplicating validation logic between frontend and backend, leading to potential inconsistencies and maintenance challenges. As the application grows, these challenges would multiply.

## Decision
We will implement a schema-driven form architecture with the following characteristics:

1. Define form schemas on the backend using TypeScript classes with decorators
2. Extend JSON Schema with UI-specific properties through custom decorators
3. Expose schemas through dedicated API endpoints
4. Generate dynamic forms on the frontend based on these schemas
5. Implement client-side validation matching server-side rules
6. Support advanced form controls including autocomplete, multi-select, and conditional fields

### Implementation Details

#### Backend
```typescript
// Custom decorator for UI hints
export function UIHint(options: any) {
  return (target: any, key: string) => {
    if (!target.uiSchema) {
      target.uiSchema = {};
    }
    target.uiSchema[key] = options;
  };
}

// DTO with validation and UI hints
export class CreateRecipeDto {
  @IsString()
  @MinLength(3)
  @UIHint({ 
    widget: 'text',
    label: 'Recipe Title',
    placeholder: 'Enter recipe title',
    order: 1
  })
  title: string;

  @IsOptional()
  @IsString()
  @UIHint({ 
    widget: 'autocomplete',
    label: 'Main Ingredient',
    dataSource: '/api/ingredients/search',
    order: 2
  })
  mainIngredient?: string;
}
```

#### Schema Endpoint
```typescript
@Controller('schemas')
export class SchemaController {
  constructor(private readonly schemaService: SchemaService) {}

  @Get(':domain/:operation')
  getSchema(
    @Param('domain') domain: string,
    @Param('operation') operation: string
  ) {
    return this.schemaService.getSchema(domain, operation);
  }
}
```

#### Frontend Form Generation
```jsx
const DynamicForm = ({ domain, operation, onSubmit }) => {
  const [schema, setSchema] = useState(null);
  
  useEffect(() => {
    const loadSchema = async () => {
      const { data } = await schemaApi.getSchema(domain, operation);
      setSchema(data);
    };
    
    loadSchema();
  }, [domain, operation]);
  
  if (!schema) return <div>Loading form...</div>;
  
  return (
    <JsonForms
      schema={schema.schema}
      uiSchema={schema.uiSchema}
      renderers={renderers}
      onChange={handleChange}
      onSubmit={onSubmit}
    />
  );
};
```

## Alternatives Considered

### 1. Hardcoded Frontend Forms
Each form would be manually created and maintained on the frontend.

**Pros:**
- Direct control over the UI and validation
- Potentially better UX customization
- No schema generation/parsing overhead

**Cons:**
- Duplication of validation logic between frontend and backend
- High maintenance burden for 20+ forms
- Potential inconsistencies as requirements change
- Poor scalability as new forms are added

### 2. Frontend-Defined Schemas
Schemas would be defined and maintained on the frontend.

**Pros:**
- Frontend has full control over form generation
- Potentially faster development workflow
- Less backend complexity

**Cons:**
- No single source of truth for validation rules
- Potential inconsistencies between frontend and backend validation
- Duplication of validation logic
- Harder to enforce server-side requirements

### 3. Generated Forms from TypeScript Types
Use TypeScript types to auto-generate forms.

**Pros:**
- Type safety throughout the stack
- Reduced duplication
- Automatic updates when types change

**Cons:**
- Limited UI hints and customization
- Less flexible for complex forms
- Tight coupling to TypeScript
- Poor support for validation beyond types

### 4. Third-Party Form Builder
Use a standalone form builder product.

**Pros:**
- Visual design tools
- Less development time
- Built-in validation

**Cons:**
- External dependency
- Potential integration challenges
- May not support all custom requirements
- Potential vendor lock-in

## Rationale
The schema-driven approach provides several significant advantages:

1. **Single Source of Truth**: Validation rules are defined once on the backend
2. **Consistency**: Frontend and backend validation remain in sync
3. **Maintainability**: Changes to validation rules are automatically reflected in forms
4. **Scalability**: Adding new forms requires minimal effort
5. **Flexibility**: Supports complex validation rules and UI requirements
6. **Developer Experience**: Clear separation of concerns between data requirements and UI

While this approach requires more initial setup than hardcoded forms, the long-term benefits for a system with 20+ forms are substantial. The maintenance burden is significantly reduced, and the risk of validation inconsistencies is minimized.

The extended JSON Schema approach also provides flexibility for UI customization while maintaining the benefits of schema-driven validation.

## Consequences

### Positive
- Reduced duplication of validation logic
- Easier maintenance for multiple forms
- Consistent user experience across forms
- Faster development of new forms
- Automatic documentation of data requirements
- Better testing capabilities

### Negative
- Initial setup complexity
- Learning curve for developers
- Potential performance overhead from schema parsing
- Some edge cases may require custom solutions
- UI flexibility somewhat constrained by schema approach

### Neutral
- Need for custom extensions to JSON Schema
- Frontend rendering components need to understand extended schema properties
- Some complex forms may need additional customization

## Implementation Plan
1. Define core schema extension framework
2. Implement schema generation from DTO classes
3. Create schema API endpoints
4. Develop frontend form generation components
5. Add support for custom form controls
6. Implement client-side validation
7. Add caching for schema responses
