# ADR-004: Use Custom Attributes for Persona Assignment

**📊 Document Type**: Architectural Decision Record (ADR)  
**📖 Reading Time**: 10-15 minutes  
**⚖️ Status**: Accepted  
**👥 Audience**: Architects, backend developers

**🔗 Related Docs**:
- **Implementation**: `scripts/persona-config.js`, `scripts/auth.js`
- **Auth Summary**: [phase-0-5-foundation/PHASE-5-TASK-2-COMPLETION-SUMMARY.md](../phase-0-5-foundation/PHASE-5-TASK-2-COMPLETION-SUMMARY.md)
- **Related ADR**: [ADR-005](./ADR-005-dual-mode-authentication.md)
- **Backend Setup**: [phase-8-backend/AUTH-STRATEGY.md](../phase-8-backend/AUTH-STRATEGY.md)

**📍 Use This Doc When**:
- Understanding how personas are assigned
- Setting up Commerce backend for personas
- Implementing persona detection
- Making decisions about customer data structure

**Status**: Accepted

**Date**: 2024-11-15

**Decision Makers**: BuildRight Implementation Team

---

## Context

BuildRight needs to map Adobe Commerce customers to one of 5 personas (Sarah, Marcus, Lisa, David, Kevin) to provide personalized experiences. Each persona gets:
- A specific catalog view via CCDM
- Persona-specific UI and workflows
- Customized dashboard
- Relevant product recommendations

In production, when a customer logs in, we need to determine their persona. In Adobe Commerce, there are three potential mechanisms:

1. **Customer Groups** - Single assignment, used for pricing/tax
2. **Customer Segments** - Multiple, dynamic assignment for targeting/promotions
3. **Custom Attributes** - Flexible, persistent key-value storage on customer records

### Key Requirements
1. **Explicit Assignment**: Persona should be explicitly assigned, not inferred dynamically
2. **Persistent**: Assignment should persist across sessions
3. **Single Persona**: Each customer belongs to exactly one persona
4. **Production-Ready**: Must work with real Adobe Commerce
5. **Easy to Query**: Should be simple to retrieve during authentication
6. **Admin-Friendly**: Easy for admins to assign/update personas

### Research Findings

#### Customer Groups
- **Purpose**: Pricing and tax calculations
- **Cardinality**: Single assignment per customer
- **Use Cases**: Wholesale vs retail pricing
- **Persistence**: Permanent until changed
- **API**: Available via REST and GraphQL
- **Limitation**: Only ~10-20 groups typical, shared across all customers

#### Customer Segments
- **Purpose**: Marketing targeting and promotions
- **Cardinality**: Multiple segments per customer
- **Use Cases**: Dynamic targeting (e.g., "high-value customers")
- **Persistence**: Often recalculated based on rules
- **API**: Available via GraphQL
- **Limitation**: Not designed for explicit, permanent assignments

#### Custom Attributes
- **Purpose**: Flexible customer data storage
- **Cardinality**: Many attributes per customer
- **Use Cases**: Any custom business data
- **Persistence**: Permanent until changed
- **API**: Available via REST and GraphQL
- **Configuration**: Defined in Admin Panel
- **Flexibility**: Can store any data type (text, select, boolean, date, etc.)

---

## Decision

**We will use a custom attribute (`buildright_persona`) to store explicit persona assignments.**

### Attribute Configuration

**Attribute Code**: `buildright_persona`  
**Attribute Type**: Dropdown/Select  
**Scope**: Global  
**Required**: No (defaults to 'marcus' if not set)  
**Visible in Frontend**: No  
**Used in Product Listing**: No  

**Values**:
- `sarah` - Production Builder
- `marcus` - Commercial Project Manager
- `lisa` - Luxury Builder
- `david` - Deck Specialist
- `kevin` - Facilities Manager

### Primary Method with Fallbacks

**Primary**: Custom Attribute (`buildright_persona`)  
**Fallback 1**: Customer Group mapping  
**Fallback 2**: Customer Segment inference  
**Default**: Marcus (most versatile experience)

### Retrieval Strategy

```javascript
// In scripts/auth.js
async function getPersonaForCustomer(customerId) {
  try {
    // 1. Try custom attribute (primary)
    const persona = await getCustomAttributePersona(customerId);
    if (persona) return persona;
    
    // 2. Try customer group mapping (fallback)
    const personaFromGroup = await inferPersonaFromCustomerGroup(customerId);
    if (personaFromGroup) return personaFromGroup;
    
    // 3. Try customer segments (fallback)
    const personaFromSegments = await inferPersonaFromSegments(customerId);
    if (personaFromSegments) return personaFromSegments;
    
    // 4. Default
    return 'marcus';
    
  } catch (error) {
    console.error('[Auth] Error determining persona:', error);
    return 'marcus'; // Safe default
  }
}
```

---

## Consequences

### Positive Outcomes

✅ **Explicit and Clear**
- Persona assignment is explicit, not inferred
- No ambiguity about which persona a customer has
- Easy to see in Admin Panel

✅ **Persistent**
- Assignment persists across sessions
- Doesn't change unless explicitly updated
- Stored permanently in customer record

✅ **Single Persona**
- Each customer has exactly one persona
- No logic needed to resolve conflicts
- Simple to query and use

✅ **Flexible**
- Can add more personas easily (just add values)
- Can store additional attributes if needed
- Not constrained by Customer Group limitations

✅ **Admin-Friendly**
- Easy to view/edit in Admin Panel
- Can bulk import via CSV
- Can set during customer creation
- Can update via REST API

✅ **Query-Friendly**
- Simple REST API call: `GET /rest/V1/customers/:id`
- GraphQL: `customer { custom_attributes { attribute_code value } }`
- No complex logic needed

✅ **Production-Ready**
- Standard Adobe Commerce functionality
- Well-documented APIs
- Used by many implementations

### Negative Outcomes

⚠️ **Requires Configuration**
- Must create custom attribute in Adobe Commerce
- Needs admin access to configure
- Adds setup step during deployment

⚠️ **Not Dynamic**
- Persona doesn't automatically update based on behavior
- Requires manual assignment or signup flow
- Could become stale if business changes

⚠️ **Additional API Call**
- Need to fetch customer data to get attribute
- Slight performance overhead
- Need to cache to avoid repeated calls

---

## Alternatives Considered

### Alternative 1: Use Customer Groups Exclusively

**Approach**: Map personas directly to customer groups (e.g., "Production Builder Group").

**Pros**:
- No custom attribute needed
- Already used for pricing
- Single source of truth
- Simple to query

**Cons**:
- Customer Groups are primarily for pricing/tax
- Limited to ~20 groups (shared with other uses)
- Conflates pricing logic with persona logic
- Less flexible (can't add metadata)
- Misuse of intended purpose

**Why Rejected**: Customer Groups are for pricing, not persona assignment. Using them for personas conflates concerns and limits flexibility.

---

### Alternative 2: Use Customer Segments Exclusively

**Approach**: Create segments for each persona, check which segments customer belongs to.

**Pros**:
- Can use dynamic rules
- Built-in Admin UI
- Can target with promotions

**Cons**:
- Customer can belong to multiple segments (need conflict resolution)
- Segments are designed for dynamic targeting, not explicit assignment
- More complex to query
- May recalculate over time
- Not designed for single, persistent assignment

**Why Rejected**: Segments are for dynamic targeting, not explicit assignment. Multiple segment membership creates complexity.

---

### Alternative 3: Store in External Database

**Approach**: Maintain persona assignments in separate database, key by customer email/ID.

**Pros**:
- Complete control
- Can add any metadata
- Not constrained by Adobe Commerce

**Cons**:
- Additional infrastructure
- Sync issues between systems
- More complex architecture
- Not visible in Admin Panel
- Requires custom API

**Why Rejected**: Adds unnecessary complexity. Adobe Commerce already provides the mechanism we need.

---

### Alternative 4: Infer from Business Attributes

**Approach**: Determine persona dynamically based on custom attributes (business_type, project_scale, etc.).

**Pros**:
- No explicit persona assignment needed
- Persona can change as attributes change
- More "intelligent" system

**Cons**:
- Inference logic could be wrong
- Customer can't override if logic is incorrect
- More complex to debug
- Persona could change unexpectedly
- Harder to predict experience

**Why Rejected**: Too magical. Better to have explicit assignment with option to change. However, we DO use inference during **sign-up** to suggest initial persona.

---

## Implementation Details

### Setting the Attribute

**Option 1: Admin Panel**
1. Navigate to Customers > All Customers
2. Select customer
3. Click "Account Information"
4. Find "BuildRight Persona" dropdown
5. Select persona
6. Save

**Option 2: REST API** (during signup or import)
```javascript
POST /rest/V1/customers

{
  "customer": {
    "email": "sarah@example.com",
    "firstname": "Sarah",
    "lastname": "Mitchell",
    "custom_attributes": [
      {
        "attribute_code": "buildright_persona",
        "value": "sarah"
      },
      {
        "attribute_code": "business_type",
        "value": "Residential Builder"
      }
    ]
  }
}
```

**Option 3: CSV Import**
```csv
email,firstname,lastname,buildright_persona,business_type
sarah@example.com,Sarah,Mitchell,sarah,Residential Builder
```

### Retrieving the Attribute

**REST API**:
```javascript
async function getCustomAttributePersona(customerId) {
  const response = await fetch(`/rest/V1/customers/${customerId}`);
  const customer = await response.json();
  
  const personaAttr = customer.custom_attributes?.find(
    attr => attr.attribute_code === 'buildright_persona'
  );
  
  return personaAttr?.value || null;
}
```

**GraphQL**:
```graphql
query {
  customer {
    email
    firstname
    lastname
    custom_attributes {
      attribute_code
      value
    }
  }
}
```

### Sign-Up Flow Integration

During sign-up (see AUTH-STRATEGY.md):

1. User fills out business profile (Step 2)
2. System runs `determinePersonaFromAttributes()`
3. Shows preview of determined persona (Step 3)
4. On account creation, sets `buildright_persona` attribute
5. User sees personalized experience immediately

---

## Customer Group Mapping (Fallback)

If custom attribute is not set, we can infer from customer group:

| Customer Group | Inferred Persona |
|----------------|------------------|
| Production Builder (Premium) | sarah |
| Commercial Contractor (Premium) | marcus |
| Luxury Builder (Premium Plus) | lisa |
| Deck Specialist (Standard) | david |
| Facilities Manager (Basic) | kevin |
| General (Default) | marcus |

---

## Related Decisions

- [ADR-003: Mock ACO Service](./ADR-003-mock-aco-service.md) - How persona maps to catalog view
- [ADR-005: Dual-Mode Authentication](./ADR-005-dual-mode-authentication.md) - How auth retrieves persona

---

## References

- [Authentication Strategy Documentation](../AUTH-STRATEGY.md)
- [Adobe Commerce REST API - Customers](https://developer.adobe.com/commerce/webapi/rest/use-rest/customer-setup/)
- [Adobe Commerce Custom Attributes](https://experienceleague.adobe.com/docs/commerce-admin/customers/customer-accounts/attributes/attribute-properties.html)

---

**Last Updated**: November 15, 2024

