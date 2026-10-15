# ADR-005: Implement Zod for Runtime Validation

## Status

**Accepted** - December 2024

## Context

TypeScript provides compile-time type checking, but cannot validate data at runtime. The API receives data from external sources (HTTP requests, databases, external APIs) that need validation to ensure:

- Data matches expected schema
- Required fields are present
- Data types are correct
- Values are within acceptable ranges
- Protection against malformed or malicious input

We need a validation solution that:
- Works seamlessly with TypeScript
- Provides clear error messages
- Has minimal performance overhead
- Supports complex validation rules
- Can infer TypeScript types from schemas

## Decision

We will use **Zod** for runtime data validation throughout the application.

### Usage Areas

1. **API Request Validation**: Validate all incoming request data
2. **Database Operations**: Validate data before persistence
3. **External API Responses**: Validate third-party API responses
4. **Configuration**: Validate environment variables and config

### Implementation Pattern

```typescript
// Define schema
export const createReceiptSchema = z.object({
  merchant: z.string().min(1).max(200),
  date: z.coerce.date(),
  total: z.number().nonnegative(),
  currency: z.enum(['USD', 'EUR', 'BRL']),
  tags: z.array(z.string()).max(20).default([]),
});

// Infer TypeScript type
export type CreateReceiptInput = z.infer<typeof createReceiptSchema>;

// Validate data
const validatedData = createReceiptSchema.parse(requestBody);
```

## Consequences

### Positive

- **Type Safety**: Automatic TypeScript type inference from schemas
  ```typescript
  type CreateReceiptInput = z.infer<typeof createReceiptSchema>;
  // TypeScript knows all fields and their types
  ```

- **Runtime Safety**: Catches invalid data at runtime
  ```typescript
  // Throws clear error if validation fails
  const data = schema.parse(untrustedData);
  ```

- **Clear Error Messages**: Detailed validation errors
  ```json
  {
    "issues": [
      {
        "path": ["total"],
        "message": "Expected number, received string"
      }
    ]
  }
  ```

- **Composable**: Schemas can be composed and reused
  ```typescript
  const lineItemSchema = z.object({ /* ... */ });
  const receiptSchema = z.object({
    lineItems: z.array(lineItemSchema),
  });
  ```

- **Transformations**: Can transform data during validation
  ```typescript
  z.coerce.date()  // Converts string to Date
  z.string().transform(s => s.toLowerCase())
  ```

- **Performance**: Fast validation with minimal overhead
- **No Decorators**: Works without experimental TypeScript features
- **Zero Dependencies**: Lightweight library

### Negative

- **Learning Curve**: Team needs to learn Zod API
- **Schema Maintenance**: Schemas need to be kept in sync with types
- **Bundle Size**: Adds ~11KB to bundle (acceptable for backend)
- **Error Handling**: Requires wrapping in try-catch blocks

### Neutral

- **Verbose for Complex Schemas**: Complex validations require more code
- **Not a Serialization Library**: Focused only on validation

## Implementation Guidelines

### 1. Request Validation in Controllers

```typescript
export const createReceipt = async (req: Request, res: Response) => {
  try {
    // Validate request body
    const validatedData = createReceiptSchema.parse(req.body);
    
    // Use validated data
    const receipt = await receiptService.create(req.user.uid, validatedData);
    
    res.status(201).json({ status: 'success', data: { receipt } });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({
        status: 'error',
        message: 'Validation failed',
        errors: error.errors,
      });
    }
    throw error;
  }
};
```

### 2. Environment Variable Validation

```typescript
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  PORT: z.coerce.number().default(3000),
  FIREBASE_PROJECT_ID: z.string().min(1),
  OPENAI_API_KEY: z.string().min(1),
});

export const config = envSchema.parse(process.env);
```

### 3. Database Response Validation

```typescript
const receiptSchema = z.object({
  id: z.string().uuid(),
  userId: z.string(),
  merchant: z.string(),
  // ...
});

const receipt = receiptSchema.parse(docSnapshot.data());
```

### 4. Query Parameters Validation

```typescript
export const receiptQuerySchema = z.object({
  startDate: z.coerce.date().optional(),
  limit: z.coerce.number().int().positive().max(100).default(20),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

const query = receiptQuerySchema.parse(req.query);
```

## Best Practices

### Schema Organization

```typescript
// models/receipt.validation.ts
export const lineItemSchema = z.object({ /* ... */ });
export const createReceiptSchema = z.object({ /* ... */ });
export const updateReceiptSchema = createReceiptSchema.partial();

// Type exports
export type LineItem = z.infer<typeof lineItemSchema>;
export type CreateReceiptInput = z.infer<typeof createReceiptSchema>;
```

### Error Handling

```typescript
function handleValidationError(error: z.ZodError) {
  return {
    status: 'error',
    message: 'Validation failed',
    errors: error.errors.map(err => ({
      field: err.path.join('.'),
      message: err.message,
    })),
  };
}
```

### Reusable Schemas

```typescript
// Common patterns
const uuidSchema = z.string().uuid();
const emailSchema = z.string().email();
const dateSchema = z.coerce.date();
const currencySchema = z.enum(['USD', 'EUR', 'BRL']);

// Compose into larger schemas
const userSchema = z.object({
  id: uuidSchema,
  email: emailSchema,
  createdAt: dateSchema,
});
```

## Alternatives Considered

1. **Joi**
   - Pros: Mature, feature-rich
   - Cons: Doesn't infer TypeScript types, larger bundle size
   - Reason rejected: Zod's TypeScript integration is superior

2. **Yup**
   - Pros: Popular, similar API to Joi
   - Cons: TypeScript support is not as good as Zod
   - Reason rejected: Zod provides better type inference

3. **class-validator**
   - Pros: Decorator-based, works with classes
   - Cons: Requires experimental decorators, more boilerplate
   - Reason rejected: Zod is simpler and more functional

4. **ajv (JSON Schema)**
   - Pros: JSON Schema standard, very fast
   - Cons: Separate type definitions needed
   - Reason rejected: Zod's integrated types are more convenient

5. **io-ts**
   - Pros: Excellent TypeScript support
   - Cons: Steeper learning curve, more verbose
   - Reason rejected: Zod is more approachable

## Performance Considerations

Zod validation overhead is minimal:
- Simple schema: ~0.01ms
- Complex schema: ~0.1ms
- Acceptable for API validation

For extreme performance needs:
- Cache parsed schemas
- Use `.safeParse()` for non-throwing validation
- Consider schema pre-compilation (future optimization)

## Migration Strategy

To migrate from manual validation to Zod:

1. Start with new endpoints
2. Gradually add schemas to existing endpoints
3. Replace manual validation checks
4. Remove redundant type guards
5. Update tests to use schemas

## References

- [Zod Documentation](https://zod.dev/)
- [Zod GitHub Repository](https://github.com/colinhacks/zod)
- [TypeScript Validation Comparison](https://github.com/colinhacks/zod#comparison)
