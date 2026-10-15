# ADR 003: Presence-as-Intent Philosophy

## Status
Accepted

## Context
Entity definitions need clear semantics about what is required vs. optional, public vs. private, mutable vs. immutable. Developers often make mistakes with default behaviors leading to security issues (public-by-default APIs, nullable-by-default fields).

## Decision
Adopt "Presence-as-Intent" philosophy where:
1. **Present = Active/Intentional**
2. **Absent = Safest Default**

### Principle: Safest Defaults
- Fields are **required** unless `.optional()`
- Fields are **not null** unless `.optional()`
- Operations are **protected** unless entity specifies `.protected: false`
- Relations create foreign keys (not just logical links)

### Rationale
Developers must **opt-in** to potentially dangerous behaviors:
- Making data optional (can be null)
- Making APIs public (security risk)
- Skipping validation

## Examples

### 1. Field Nullability
```typescript
// WRONG - implicit nullable (dangerous)
email: text()  // can be null? unclear!

// RIGHT - explicit intent
email: text().required()  // never null ✓
email: text().optional()  // can be null, INTENTIONAL ✓
```

### 2. API Protection
```typescript
// Default: everything protected (safest)
defineEntity('User', {
  fields: { email: text() },
  // protected: 'all' is implicit
})

// Opt-in to public access
defineEntity('BlogPost', {
  fields: { title: text() },
  protected: 'write',  // list/get public, mutations protected
})
```

### 3. Soft Delete
```typescript
// Opt-in to soft delete (keep data)
defineEntity('Order', {
  fields: { total: number() },
  behaviors: {
    softDelete: true,  // deletedAt field added
  }
})

// Default: hard delete (data removed)
```

## Consequences

### Positive
- **Security by default** - APIs are protected unless opted out
- **Data integrity** - Fields are required unless made optional
- **Explicit intent** - Code clearly shows what's intentional vs. default
- **Prevents common bugs** - Null pointer errors caught at definition time

### Negative
- More verbose for truly public APIs (must write `protected: false`)
- Differs from some ORMs (Prisma, Sequelize use nullable-by-default)
- Learning curve for developers from other systems

### Neutral
- Aligns with TypeScript's strictness (`strictNullChecks`)
- Similar to Rust's "explicit over implicit" philosophy

## Alternatives Considered

### 1. Permissive Defaults (Rejected)
```typescript
// Fields nullable by default
email: text()  // can be null

// APIs public by default
defineEntity('User', { ... })  // all CRUD public
```

**Rejected**: Security vulnerabilities, data integrity issues

### 2. Explicit Everything (Rejected)
```typescript
// Force explicit on everything
email: text().required().notNull().mutable()
```

**Rejected**: Too verbose, poor DX

## Migration Guide

For developers from other systems:

### From Prisma
```prisma
// Prisma (optional by default)
model User {
  email String?  // nullable
}
```

```typescript
// Archetype (required by default)
defineEntity('User', {
  fields: {
    email: text().optional()  // explicitly nullable
  }
})
```

### From Sequelize
```javascript
// Sequelize (nullable by default)
email: {
  type: DataTypes.STRING,
  allowNull: true
}
```

```typescript
// Archetype
email: text().optional()
```

## References
- Inspired by Rust's ownership system (explicit intent)
- Aligns with "Secure by Default" principle
- TypeScript's `strictNullChecks` philosophy
