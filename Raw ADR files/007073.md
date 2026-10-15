# ADR 008: OpenAPI Contract Testing Strategy

**Status:** Accepted

**Date:** 2024-11-12

**Updated:** 2024-12-03

**Related:** [ADR-014: Laravel-First Strategy](014-laravel-first-strategy.md)

---

## Context

With API-first development (ADR-002) and Laravel as primary backend (ADR-014), we must ensure the implementation matches the OpenAPI specification exactly. Contract testing provides:
- Verification that Laravel API matches OpenAPI spec
- Frontend can trust the API structure
- Framework-agnostic validation (useful if adding future implementations)
- Automated documentation validation

Without verification, implementations could drift from specification causing:
- Frontend bugs due to unexpected responses
- Inconsistent behavior
- Outdated documentation
- Breaking changes without notice

---

## Decision

**Implement automated contract tests that validate Laravel backend against the OpenAPI specification.**

### Testing Approach

1. **Contract Tests in Laravel Backend**
   ```
   tests/
   └── Contract/
       ├── AuthContractTest.php
       ├── ClientContractTest.php
       ├── QuoteContractTest.php
       └── ...
   ```

2. **Validation Library**
   - **Laravel**: `spectator/spectator` package (primary)
   - Framework-agnostic approach allows future implementations to use:
     - **Symfony**: `openapi-psr7-validator`
     - **Next.js**: `openapi-validator-middleware`

3. **CI/CD Integration**
   - Contract tests run on every PR
   - Must pass before merge
   - Block deployment if failing

4. **Test Structure**
   ```php
   public function test_list_clients_matches_contract(): void
   {
       $response = $this->getJson('/api/v1/clients');
       
       $response->assertStatus(200)
           ->assertValidRequest()    // Request matches spec
           ->assertValidResponse();  // Response matches spec
   }
   ```

---

## Consequences

### Positive
- ✅ Guaranteed API consistency
- ✅ Automated verification
- ✅ Catches drift early
- ✅ Frontend developers trust any backend
- ✅ Documentation is always current
- ✅ Refactoring confidence

### Negative
- ⚠️ Initial setup time
- ⚠️ Must maintain OpenAPI spec
- ⚠️ Tests can be brittle
- ⚠️ Adds to test suite time

---

## Implementation

### Test Coverage Required
- ✅ All endpoints (100%)
- ✅ All status codes (200, 201, 400, 401, 404, 422, 500)
- ✅ Request validation
- ✅ Response validation
- ✅ Required fields
- ✅ Optional fields
- ✅ Data types
- ✅ Enums

### Example (Laravel + Spectator)
```php
use Spectator\Spectator;

class ClientContractTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        Spectator::using('openapi.yaml');
    }

    public function test_create_client_matches_contract(): void
    {
        $response = $this->postJson('/api/v1/clients', [
            'name' => 'Test Client',
            'email' => 'test@example.com',
        ]);

        $response->assertValidRequest()
            ->assertValidResponse(201);
    }

    public function test_validation_errors_match_contract(): void
    {
        $response = $this->postJson('/api/v1/clients', [
            'name' => '', // Invalid
        ]);

        $response->assertValidRequest()
            ->assertValidResponse(422);
    }
}
```

---

## Alternatives Considered

**Manual Testing**: Rejected - error-prone, time-consuming  
**Integration Tests Only**: Rejected - don't verify contract compliance  
**Postman Tests**: Rejected - not automated in CI/CD  
**No Verification**: Rejected - defeats multi-implementation purpose

---

**Related:** ADR-002 (API-first approach this enables)
