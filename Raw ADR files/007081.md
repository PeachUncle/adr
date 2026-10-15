# ADR-003: Mock ACO Service with CCDM Simulation

**Status**: Accepted

**Date**: 2024-11-15

**Decision Makers**: BuildRight Implementation Team

---

## Context

BuildRight is a demonstration of Adobe Commerce Optimizer (ACO) capabilities, specifically the **Composable Catalog Data Model (CCDM)**. CCDM allows:
- Multiple catalog views per storefront
- Policy-based product filtering
- Triggered policies based on customer context
- Progressive catalog filtering (e.g., deck wizard)
- Customer-group-specific pricing

The `buildright-aco` repository **has access to a real ACO instance** and ingests product data via ACO API. However, for **frontend development** (`buildright-eds`), we need a mock service to enable rapid iteration without GraphQL calls to ACO during development.

### Key Requirements
1. **Accurate Simulation**: Mock must behave like real ACO
2. **Demo-Ready**: Must convincingly demonstrate CCDM capabilities
3. **Production Migration Path**: Easy to swap mock for real ACO GraphQL
4. **Persona Support**: Must handle 5 different persona experiences
5. **API Compatibility**: Mock API should match real ACO API signatures
6. **Data Consistency**: Mock reads same data structure that's in real ACO

### Research Findings
- ACO is Adobe's backend service for catalog optimization
- **CCDM = Composable Catalog Data Model** (NOT "Customer-Centric Data Management")
- CCDM core concepts:
  - **Catalog Views**: Different product sets for different contexts
  - **Policies**: Rules that determine product visibility
  - **Triggered Policies**: Policies activated by customer attributes
  - **Catalog Sources**: Origin of product data
  - **Price Books**: Customer-group-specific pricing

### Why Mock for Frontend?
- **Real ACO exists** in `buildright-aco` with real data ingestion
- **Frontend needs mock** to develop without ACO GraphQL dependency
- **Mock reads same data files** generated for ACO ingestion
- **Production path**: Replace mock with ACO GraphQL queries

---

## Decision

**We will create a mock ACO service that accurately simulates CCDM behavior for demo purposes.**

### Mock Service Architecture

**File**: `scripts/aco-service.js`

The mock service will:

1. **Simulate Catalog Views**
   - Define 5 catalog views (one per persona)
   - Each view has a curated product list
   - Views are triggered by customer attributes

2. **Simulate Policies**
   - Base policies for customer group access
   - Triggered policies based on project context (e.g., deck wizard)
   - Progressive filtering policies

3. **Simulate Pricing**
   - Customer-group-specific price books
   - Volume tier pricing
   - Promotional pricing

4. **Match Real ACO API**
   - Same method signatures
   - Same request/response structure
   - Same error handling patterns
   - Simulated network latency

### Mock API Methods

```javascript
// Get user context (persona, customer group, attributes)
await acoService.getUserContext(userId);

// Get products with CCDM filtering
await acoService.getProducts({
  filters: {},
  userContext: {},
  policy: 'deck-materials',
  limit: 24,
  offset: 0
});

// Get pricing for products
await acoService.getPricing({
  productIds: ['sku123'],
  customerGroup: 'premium',
  quantity: 10
});

// Get catalog view for persona
await acoService.getCatalogView('sarah-production-builder');

// Apply triggered policy
await acoService.applyPolicy('progressive-deck-filter', { deckSize: 'large' });
```

### Data Storage

**File**: `data/mock-aco-data.json`

```json
{
  "catalogViews": {
    "sarah-production-builder": {
      "id": "sarah-production-builder",
      "name": "Production Builder Catalog",
      "description": "Curated for high-volume residential builders",
      "productSkus": ["..."],
      "policies": ["base-access", "volume-pricing"]
    }
  },
  "policies": {
    "deck-materials": {
      "type": "triggered",
      "triggerAttributes": ["project_type"],
      "filterRules": [...]
    }
  },
  "priceBooks": {
    "premium": {
      "discountPercent": 15,
      "volumeTiers": [...]
    }
  }
}
```

---

## Consequences

### Positive Outcomes

✅ **Realistic Demo**
- Demonstrates ACO capabilities convincingly
- Shows CCDM filtering in action
- Presents persona-specific catalogs
- Displays customer-group pricing

✅ **Development Without Backend**
- Can develop and test without ACO instance
- Faster iteration cycles
- No dependency on backend team
- Complete control over demo scenarios

✅ **Production Migration Path**
- Mock API matches real ACO API
- Easy swap: just change endpoint configuration
- Same request/response structure
- Minimal code changes needed

✅ **Testability**
- Can test edge cases easily
- Predictable behavior
- Can simulate errors and latency
- Fast test execution

✅ **Demo Flexibility**
- Can showcase specific scenarios
- Can create "perfect" demo data
- Easy to add new demo scenarios
- No concerns about backend state

### Negative Outcomes

⚠️ **Not 100% Real**
- May not capture all ACO edge cases
- Could diverge from real ACO behavior over time
- Demo data is static, not dynamic

⚠️ **Maintenance Burden**
- Must keep mock in sync with real ACO API changes
- Need to update when ACO adds new features
- Must maintain mock data quality

⚠️ **Risk of Misrepresentation**
- Could show features that don't exist
- Might oversimplify complex ACO behavior
- Demo might not reflect production performance

⚠️ **No Real Integration Testing**
- Can't test actual ACO connection until production
- May discover integration issues late
- Mock might miss authentication/authorization complexities

---

## Alternatives Considered

### Alternative 1: Use Hardcoded Data Per Page

**Approach**: Hardcode product lists directly in each page/component.

**Pros**:
- Simplest approach
- No mock service needed
- Fast to implement

**Cons**:
- No simulation of ACO behavior
- Can't demonstrate CCDM filtering
- Hard to show triggered policies
- Difficult to change demo scenarios
- No clear production migration path

**Why Rejected**: Doesn't demonstrate ACO capabilities at all. Defeats the purpose of the demo.

---

### Alternative 2: Connect to Real ACO Sandbox

**Approach**: Set up a real ACO instance for development.

**Pros**:
- 100% accurate ACO behavior
- Tests real integration
- No mock maintenance

**Cons**:
- Requires ACO instance access (may not be available)
- Depends on backend team for setup/changes
- Slower iteration (network calls, backend state)
- Demo data harder to control
- May have usage costs

**Why Rejected**: No guaranteed access to ACO during development. Would slow down iteration significantly.

---

### Alternative 3: Generic Mock Server (e.g., JSON Server)

**Approach**: Use a generic API mocking tool.

**Pros**:
- Quick to set up
- Standard tooling
- No custom code needed

**Cons**:
- Can't simulate CCDM logic (policies, triggered filtering)
- Just returns static JSON, no dynamic behavior
- Doesn't teach us how ACO actually works
- Hard to simulate progressive filtering

**Why Rejected**: Too simplistic. Can't capture CCDM's dynamic behavior.

---

## Implementation Details

### Mock Service Interface

```javascript
class ACOService {
  constructor(options = {}) {
    this.mode = options.mode || 'demo'; // 'demo' or 'production'
    this.endpoint = options.endpoint || '/mock-aco';
    this.latency = options.latency || 300; // Simulate network delay
  }
  
  async getUserContext(userId) {
    if (this.mode === 'demo') {
      return this._mockGetUserContext(userId);
    } else {
      return this._realGetUserContext(userId);
    }
  }
  
  async getProducts(params) {
    if (this.mode === 'demo') {
      return this._mockGetProducts(params);
    } else {
      return this._realGetProducts(params);
    }
  }
  
  // ... other methods
}
```

### CCDM Simulation Logic

**Catalog View Selection**:
```javascript
function selectCatalogView(userContext) {
  const { persona, customerGroup } = userContext;
  
  // Map persona to catalog view
  const viewMap = {
    'sarah': 'production-builder-catalog',
    'marcus': 'commercial-pm-catalog',
    'lisa': 'luxury-builder-catalog',
    'david': 'deck-specialist-catalog',
    'kevin': 'facilities-manager-catalog'
  };
  
  return catalogViews[viewMap[persona]];
}
```

**Triggered Policy Application**:
```javascript
function applyTriggeredPolicy(catalogView, policyName, context) {
  const policy = policies[policyName];
  
  if (!policy || policy.type !== 'triggered') {
    return catalogView.products;
  }
  
  // Apply filter rules based on context
  return catalogView.products.filter(product => {
    return policy.filterRules.every(rule => {
      return evaluateRule(rule, product, context);
    });
  });
}
```

### Production Swap Strategy

To swap to production ACO:

1. Update service configuration:
   ```javascript
   const acoService = new ACOService({
     mode: 'production',
     endpoint: 'https://aco.adobe.io/api/v1'
   });
   ```

2. Add real ACO authentication
3. No changes to calling code
4. Same API interface

---

## Validation Strategy

To ensure mock accurately represents ACO:

1. **Review ACO Documentation**
   - Validate API signatures match
   - Confirm CCDM concepts are correct
   - Check response structures

2. **Stakeholder Review**
   - Have Adobe ACO team review mock behavior
   - Validate demo scenarios
   - Confirm CCDM simulation is accurate

3. **Regular Sync**
   - Monitor ACO API changes
   - Update mock when ACO evolves
   - Document any known deviations

---

## Related Decisions

- [ADR-001: Use Adobe Commerce Dropins](./ADR-001-use-dropins-for-commerce.md) - Dropins will call ACO service
- [ADR-004: Custom Attributes for Personas](./ADR-004-custom-attributes-for-personas.md) - How personas map to catalog views

---

## References

- [Mock ACO API Specification](../MOCK-ACO-API-SPEC.md)
- [Adobe Commerce Optimizer Documentation](https://experienceleague.adobe.com/docs/commerce-admin/systems/catalog-management.html)
- [CCDM Research Notes](../PHASE-0-RESEARCH-AND-DECISIONS.md#step-4-design-mock-aco-service)

---

**Last Updated**: November 15, 2024

