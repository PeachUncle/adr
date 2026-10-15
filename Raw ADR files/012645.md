# ADR-4: Extended JSON Schema for Advanced Form Controls

## Status
Accepted

## Date
2025-03-16

## Context
The Recipe Management System requires complex form inputs beyond basic text fields, numbers, and dropdowns. In particular, we need specialized controls for:

1. **Ingredient Selection**: Typeahead/autocomplete fields for selecting ingredients from a database
2. **Unit Conversion**: Fields that handle measurement unit conversion
3. **Step Reordering**: Drag-and-drop interface for cooking steps
4. **Tag Management**: Token input for recipe categories
5. **Rich Text**: Formatted instructions with support for emphasis, lists, etc.
6. **Conditional Fields**: Fields that appear based on other selections
7. **Dependent Dropdowns**: Options that change based on related selections

Our schema-driven form architecture (ADR-2) is based on JSON Schema, which provides excellent support for validation but has limited features for describing UI requirements. Standard JSON Schema focuses primarily on data structure and validation rules, not presentation.

We need to extend our schema approach to communicate these rich UI requirements to the frontend while maintaining the benefits of schema-driven forms.

## Decision
We will extend the JSON Schema standard with custom UI properties through a dedicated `uiSchema` object, and implement these extensions via a custom decorator:

1. Create a `UIHint` decorator that attaches UI-specific metadata to DTO properties
2. Include a separate `uiSchema` object alongside the standard schema in API responses
3. Implement specialized frontend renderers for each custom widget type
4. Support rich interaction patterns including typeahead, drag-and-drop, and conditional display

### UIHint Decorator Implementation

```typescript
export function UIHint(options: any) {
  return (target: any, key: string) => {
    if (!target.uiSchema) {
      target.uiSchema = {};
    }
    target.uiSchema[key] = options;
  };
}
```

### Example DTO with UI Hints

```typescript
export class CreateRecipeIngredientDto {
  @IsString()
  @MinLength(2)
  @UIHint({ 
    widget: 'autocomplete',
    label: 'Ingredient',
    dataSource: '/api/ingredients/search',
    queryParam: 'q',
    minChars: 2,
    debounceMs: 300,
    order: 1
  })
  name: string;

  @IsNumber()
  @Min(0)
  @UIHint({ 
    widget: 'number',
    label: 'Amount',
    order: 2
  })
  amount: number;

  @IsString()
  @UIHint({ 
    widget: 'select',
    label: 'Unit',
    options: [
      { label: 'Grams (g)', value: 'g' },
      { label: 'Kilograms (kg)', value: 'kg' },
      { label: 'Milliliters (ml)', value: 'ml' },
      // other options...
    ],
    order: 3
  })
  unit: string;
}
```

### Schema API Response Format

```json
{
  "schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "minLength": 2
      },
      "amount": {
        "type": "number",
        "minimum": 0
      },
      "unit": {
        "type": "string"
      }
    },
    "required": ["name"]
  },
  "uiSchema": {
    "name": {
      "widget": "autocomplete",
      "label": "Ingredient",
      "dataSource": "/api/ingredients/search",
      "queryParam": "q",
      "minChars": 2,
      "debounceMs": 300,
      "order": 1
    },
    "amount": {
      "widget": "number",
      "label": "Amount",
      "order": 2
    },
    "unit": {
      "widget": "select",
      "label": "Unit",
      "options": [
        { "label": "Grams (g)", "value": "g" },
        { "label": "Kilograms (kg)", "value": "kg" },
        { "label": "Milliliters (ml)", "value": "ml" }
      ],
      "order": 3
    }
  }
}
```

### Frontend Renderer Registration

```typescript
// Example of registering custom renderers
const renderers = [
  ...materialRenderers, // Base renderers
  
  // Custom renderers
  { tester: (schema, uischema) => uischema.widget === 'autocomplete', 
    renderer: AutocompleteField },
  
  { tester: (schema, uischema) => uischema.widget === 'rich-text', 
    renderer: RichTextField },
  
  { tester: (schema, uischema) => uischema.widget === 'reorderable-array', 
    renderer: ReorderableArrayField }
];
```

## Alternatives Considered

### 1. Standard JSON Schema Only

Restrict ourselves to standard JSON Schema without extensions.

**Pros:**
- Follows established standards
- Better compatibility with third-party libraries
- No custom implementation needed
- Clear separation between data validation and UI

**Cons:**
- Limited expressiveness for UI requirements
- Frontend would need additional configuration
- No way to specify complex controls like autocomplete
- Multiple sources of UI configuration

### 2. Separate UI Schema Objects

Store UI hints in completely separate objects from data schemas.

**Pros:**
- Cleaner separation of concerns
- More flexibility in UI description
- Could support multiple UI variations
- More aligned with some libraries like react-jsonschema-form

**Cons:**
- Two separate schemas to maintain
- Potential synchronization issues
- More complex API responses
- Harder to ensure fields match

### 3. Custom Frontend Components Only

Implement custom components without schema guidance.

**Pros:**
- Maximum flexibility for UI implementation
- No schema extension needed
- Potentially better UX
- Direct control over all aspects

**Cons:**
- No structured metadata about fields
- Harder to maintain consistency
- More frontend development effort
- Less systematic approach

### 4. Form-Specific Backend Endpoints

Create specialized endpoints that return form configuration.

**Pros:**
- Highly optimized for each form
- Could include contextual data
- Potentially better performance
- More direct backend control

**Cons:**
- Less consistent approach
- More endpoints to maintain
- Less reuse of validation logic
- Higher maintenance burden

## Rationale

The extended JSON Schema approach with UI hints provides several significant advantages:

1. **Single Source of Truth**: Both validation and UI requirements come from the backend
2. **Structured Metadata**: UI hints are organized in a consistent, predictable way
3. **Type Safety**: TypeScript ensures correct UI hint properties
4. **Flexibility**: Custom renderers can interpret hints as needed
5. **Progressive Enhancement**: Basic forms work without custom renderers, but are enhanced when available

This approach addresses the specific requirements for complex recipe forms while maintaining the benefits of our schema-driven architecture. It allows us to handle specialized inputs like ingredient autocomplete fields while keeping a consistent approach to form generation.

The use of a separate `uiSchema` object (rather than extending the core schema) maintains compatibility with standard JSON Schema validation while adding the UI capabilities we need. This pattern is also used by libraries like react-jsonschema-form, making it familiar to developers.

## Consequences

### Positive
- Rich, interactive forms with specialized controls
- Consistent approach to form definition
- Backend control over form presentation
- Support for complex scenarios like autocomplete
- Better user experience for recipe entry

### Negative
- Non-standard extension of JSON Schema
- Custom implementation required
- Frontend renderers needed for each widget type
- More complex schema generation

### Neutral
- Need to document custom UI properties
- Frontend needs to understand the uiSchema format
- May need to evolve as requirements change

## Implementation Plan

1. **Phase 1**: Core implementation
   - Create UIHint decorator
   - Extend schema generation to include UI hints
   - Update schema endpoints to return uiSchema

2. **Phase 2**: Basic custom renderers
   - Implement renderers for common widgets (select, number, etc.)
   - Create DynamicForm component to use renderers
   - Document renderer API

3. **Phase 3**: Advanced renderers
   - Implement autocomplete renderer with API integration
   - Add drag-and-drop support for arrays
   - Implement conditional field rendering

4. **Phase 4**: Complex scenarios
   - Add support for dependent dropdowns
   - Implement rich text editing
   - Create specialized array controls for ingredients and steps

5. **Phase 5**: Optimization
   - Implement caching for autocomplete suggestions
   - Add performance optimizations
   - Improve accessibility of custom renderers
