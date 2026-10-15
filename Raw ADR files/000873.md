# ADR-006: Frontend Resilience and i18n Improvements

## Status
Proposed

## Context
During the development of the Bid Calculation Tool, several areas for improvement have been identified that would 
enhance the maintainability, scalability, and user experience of the application:

1. **Hardcoded English strings**: The application currently has hardcoded English text throughout the frontend, 
making internationalization difficult.

2. **Manual DTO synchronization**: Frontend DTOs are manually maintained copies of backend DTOs, creating a risk of
inconsistency and requiring manual updates when backend contracts change.

3. **Frontend coupling to fee structure**: The frontend is tightly coupled to specific fee types (BasicBuyerFee, 
SellerSpecialFee, etc.), making it fragile when new fee types are added or existing ones are modified.

## Decision

### For Production Implementation (Future Enhancements)

#### 1. Internationalization (i18n)
- Implement Vue i18n for dynamic language support
- Replace all hardcoded strings with translation keys
- Structure: `$t('bidCalculation.form.vehiclePrice')` instead of `"Vehicle Price"`
- Support multiple languages (EN, FR initially)

#### 2. DTO Generation and Synchronization
- Use OpenAPI/Swagger generation as single source of truth
- Backend DTOs drive frontend types automatically
- Options considered:
  - **Option A**: Generate TypeScript types from OpenAPI spec at build time
  - **Option B**: Create shared DTO package published to private npm registry
  - **Option C**: Code generation using tools like `swagger-codegen` or `openapi-generator`

**Recommended approach**: Option A (OpenAPI generation)
- Less infrastructure overhead than private npm registry
- Automatic synchronization on build
- Type safety guaranteed at compile time

#### 3. Dynamic Fee Structure
- Modify backend response to include dynamic fee breakdown
- Frontend renders fees generically from array structure
- Benefits:
  - Adding new fee strategies doesn't require frontend changes
  - Fee names, descriptions, and values come from backend
  - Future-proof against business rule changes

## Implementation Plan

### Phase 1: Dynamic Fee Structure (Implemented Now)
```typescript
// Backend response structure
interface BidCalculationResponseDto {
  vehiclePrice: number;
  vehicleType: string;
  totalCost: number;
  feeBreakdown: FeeBreakdownItem[];
}

interface FeeBreakdownItem {
  name: string;
  displayName: string;
  amount: number;
  description?: string;
}
```

### Phase 2: DTO Generation (Next Release)
- Set up build pipeline with OpenAPI TypeScript generation
- Remove manual DTO definitions
- Implement type checking in CI/CD

### Phase 3: Internationalization (Future Release)
- Install and configure Vue i18n
- Extract all strings to translation files
- Implement language switching UI

## Consequences

### Positive
- **Maintainability**: Reduced coupling between frontend and backend
- **Scalability**: Easy to add new languages and fee types
- **Type Safety**: Automatic DTO synchronization prevents runtime errors
- **Developer Experience**: Single source of truth for contracts

### Negative
- **Initial Complexity**: Setup overhead for generation pipeline
- **Build Dependencies**: Frontend build depends on backend OpenAPI spec
- **Learning Curve**: Team needs to understand i18n patterns

## Implementation Notes

For the current coding challenge submission, we're implementing Phase 1 (Dynamic Fee Structure) as it provides immediate
value and demonstrates architectural thinking without over-engineering the solution.

Future phases could be implemented based on product requirements and team capacity.

## References
- [Vue i18n Documentation](https://vue-i18n.intlify.dev/)
- [OpenAPI TypeScript Generator](https://github.com/ferdikoomen/openapi-typescript-codegen)
- [ADR-001: Project Structure](./001-project-structure-and-technology-stack.md)
