# ADR-018: Backend-Driven CamelCase API Contract

**Date**: 2025-06-25
**Status**: Accepted
**Author**: JP

## Context

This ADR supersedes [ADR-017](./ADR-017-Frontend-Backend-API-Data-Transformation-Strategy.md), which proposed a frontend-based data transformation layer. The implementation of ADR-017 proved to be fragile, introducing runtime errors and unnecessary complexity in the frontend codebase. The core problem remains the need for a consistent data contract between the Python backend (`snake_case`) and the TypeScript frontend (`camelCase`).

## Decision

**The backend API will be the single source of truth for the data contract and will serve all JSON responses with `camelCase` keys.**

This is achieved by implementing a `BaseModel` in Pydantic that all API response models will inherit from. This base model uses a `Config` class with an `alias_generator` to automatically convert Python `snake_case` field names to `camelCase` during JSON serialization.

### Example Pydantic Implementation:

```python
from pydantic import BaseModel
from humps import camelize

# Function to convert snake_case to camelCase for Pydantic aliases
def to_camel(string: str) -> str:
    return camelize(string)

# Base model with camelCase aliasing
class Base(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

# All other API models will inherit from Base
class MyApiResponse(Base):
    user_id: int
    user_name: str
    
# This will serialize to: {"userId": 1, "userName": "example"}
```

As a result of this backend change, the frontend's responsibility is simplified:
1.  **Remove all key transformation logic**: The `keysToCamel`, `keysToSnake`, and related utilities will be deleted from the frontend.
2.  **Consume `camelCase` directly**: All TypeScript interfaces and API client logic will be written to expect `camelCase` properties, matching the API's output directly.

## Consequences

### Positive:
-   ✅ **Robustness**: Eliminates an entire class of runtime transformation errors on the frontend.
-   ✅ **Simplicity**: Drastically simplifies the frontend API client and data handling logic.
-   ✅ **Clear Contract**: Creates a single, unambiguous source of truth for the data contract—the backend's Pydantic models.
-   ✅ **Maintainability**: Makes both the frontend and backend easier to reason about and maintain. New API endpoints automatically adhere to the contract.
-   ✅ **Standard Practice**: Aligning the API's output with the consumer's convention (JavaScript's `camelCase`) is a standard and recommended practice in web development.

### Negative:
-   ➖ **Minor Backend Overhead**: Adds a small dependency (`humps`) and a base model configuration to the backend. This is a negligible and worthwhile trade-off for the significant benefits.

## Implementation Plan

1.  **Update Backend**:
    -   Add `humps` to `backend/requirements.txt`.
    -   Create the `Base` Pydantic model in `backend/api/models.py`.
    -   Update all API models to inherit from `Base`.
    -   Verify with tests that all API endpoints now serve `camelCase` JSON.
2.  **Update Frontend**:
    -   Delete the key transformation utilities from `src/lib/utils.ts`.
    -   Remove the request/response transformation interceptors from the `axios` client in `src/lib/api.ts`.
    -   Ensure all TypeScript interfaces in `src/lib/api.ts` and components like `IdeationPage.tsx` use `camelCase` properties.
    -   Manually test the application to confirm that data is being fetched and displayed correctly.
3.  **Update Documentation**:
    -   Mark `ADR-017` as "Superseded" by this ADR.
    -   Update `docs/architecture/LLD-Solution-Architecture.md` to reflect this new, simpler data flow.

This decision establishes a more professional, stable, and maintainable architecture for the application. 