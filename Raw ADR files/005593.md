# ADR-001: FHIR Types and Generic Client Design

## Status
Accepted

## Context
The intake application needs to interact with an Aidbox FHIR server for patient management. We need type-safe TypeScript definitions for FHIR resources and a client API that is both developer-friendly and maintainable.

## Decision
We will use auto-generated FHIR R4 type definitions and implement a generic client API with resource type inference.

## Rationale

### Type Safety & Developer Experience
- **Auto-generated types**: Use comprehensive FHIR R4 types generated from official schemas
- **Type inference**: Client methods automatically infer return types from resource type strings
- **IntelliSense support**: Full autocomplete for resource types and properties
- **Compile-time validation**: Catch FHIR-related errors at build time

### API Design
- **Generic over specific**: Single `search<T>()` and `read<T>()` methods instead of resource-specific methods
- **Resource type mapping**: `ResourceTypeMap` enables type inference from string literals
- **Raw FHIR responses**: Return native FHIR Bundle format to preserve pagination links

### Maintainability  
- **DRY principle**: One implementation handles all 150+ FHIR resource types
- **Future-proof**: New FHIR resources automatically supported without code changes
- **No manual type maintenance**: Types are generated and should not be manually edited

## Implementation Details

### Generic Client Methods
```typescript
async search<T extends keyof ResourceTypeMap>(
  resourceType: T,
  params?: Record<string, string>
): Promise<Bundle<ResourceTypeMap[T]>>

async read<T extends keyof ResourceTypeMap>(
  resourceType: T,
  id: string
): Promise<ResourceTypeMap[T]>
```

### Usage Pattern
```typescript
// Type inferred as Bundle<Patient>
const patients = await aidbox.search('Patient', { name: 'John' });

// Access resources from bundle using non-null assertion
const patientList = patients.entry?.map(entry => entry.resource!) || [];

// Type inferred as Patient
const patient = await aidbox.read('Patient', '123');
```

## Usage Guidelines

### Working with Bundles
```typescript
// Recommended: Use non-null assertion (!) for Bundle entries
const patients = bundle.entry?.map(entry => entry.resource!) || [];

// Read single resource
const patient = await aidbox.read('Patient', 'patient-123');
```

## File Structure
```
src/types/fhir/
├── index.ts              # Main exports and ResourceTypeMap
├── Patient.ts            # Patient resource type
├── Bundle.ts             # Bundle resource type  
└── ...                   # 150+ other FHIR resource types
```

## References
- [FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [Aidbox FHIR API Documentation](https://docs.aidbox.app/)
- [FHIR Schema Codegen](https://github.com/fhir-schema/fhir-schema-codegen)