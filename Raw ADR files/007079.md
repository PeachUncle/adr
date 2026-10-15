# ADR-001: Use Adobe Commerce Dropins for Core Commerce Functions

**Status**: Accepted

**Date**: 2024-11-15

**Decision Makers**: BuildRight Implementation Team

---

## Context

BuildRight requires core e-commerce functionality including:
- User authentication and session management
- Account/profile management
- Shopping cart operations
- Product display (PDP)
- Checkout flow
- Order management

We need to decide whether to build these components from scratch using custom JavaScript or leverage Adobe Commerce Storefront Dropins, which are pre-built, reusable UI components designed for headless Adobe Commerce storefronts.

### Key Constraints
1. **Timeline**: Must deliver persona-driven demo in reasonable timeframe
2. **Adobe Ecosystem**: Should integrate seamlessly with Adobe Commerce backend
3. **Maintainability**: Need production-ready, secure commerce logic
4. **Flexibility**: Must support persona-specific customization
5. **Demo + Production**: Must work for both demo mode and production deployment

### Research Findings
- Adobe provides 8 native dropins via NPM packages
- Dropins include built-in Adobe Commerce API integration
- Dropins support customization via "slots" system
- Dropins use Adobe's design token system
- Dropins emit standardized events for inter-component communication
- Documentation available at Experience League

---

## Decision

**We will use Adobe Commerce Storefront Dropins for core commerce functions.**

### Dropins We WILL Use:

| Dropin | Package | Purpose |
|--------|---------|---------|
| **Auth** | `@dropins/storefront-auth` | Login, logout, session management |
| **Account** | `@dropins/storefront-account` | Profile, addresses, preferences |
| **Cart** | `@dropins/storefront-cart` | Cart operations, quantity updates |
| **PDP** | `@dropins/storefront-pdp` | Product detail display |
| **Checkout** | `@dropins/storefront-checkout` | Checkout flow |
| **Order** | `@dropins/storefront-order` | Order history, tracking |

### Dropins We Will NOT Use:

| Dropin | Package | Reason for Exclusion |
|--------|---------|---------------------|
| **Payment Services** | `@dropins/storefront-payment-services` | Client prefers custom payment gateway integration |
| **Personalization** | `@dropins/storefront-personalization` | BuildRight uses custom persona system, not Adobe Target |

### Custom Components (EDS Blocks):
For BuildRight-specific features, we'll build custom EDS blocks:
- Template selector (Sarah)
- Project wizard (Marcus)
- Package builder (Lisa)
- Deck wizard (David)
- Restock dashboard (Kevin)

---

## Consequences

### Positive Outcomes

✅ **Faster Development**
- Pre-built components save 3-4 weeks of development time
- Focus effort on persona-specific features, not commodity commerce logic

✅ **Production-Ready**
- Battle-tested authentication and cart logic
- Security best practices built-in
- Handles edge cases (session expiry, concurrent cart updates, etc.)

✅ **Adobe Commerce Integration**
- Native integration with Adobe Commerce APIs
- Automatic handling of customer groups, pricing, inventory
- Works seamlessly with ACO/CCDM when connected

✅ **Maintained by Adobe**
- Regular security updates
- Bug fixes handled upstream
- New features added over time

✅ **Consistent UX**
- Follows Adobe's design system
- Familiar patterns for Adobe Commerce users
- Professional appearance out-of-the-box

✅ **Customization Support**
- Slots system allows targeted customization
- Can override styling with CSS
- Event system enables integration with custom logic

### Negative Outcomes

⚠️ **Less Flexibility**
- Some behaviors may be harder to customize
- Must work within dropin constraints
- May need workarounds for non-standard requirements

⚠️ **External Dependency**
- Tied to Adobe's release cycle for updates
- Breaking changes in new versions require migration
- Cannot fix bugs ourselves (must wait for Adobe)

⚠️ **Learning Curve**
- Team must learn dropin APIs and patterns
- Documentation may have gaps
- Debugging third-party code is harder

⚠️ **Bundle Size**
- Each dropin adds to JavaScript bundle size
- May impact initial page load performance
- Need to optimize lazy loading

⚠️ **Demo Mode Complexity**
- Dropins expect real Adobe Commerce backend
- Must create comprehensive mock services
- Need to simulate all API responses accurately

---

## Alternatives Considered

### Alternative 1: Build Custom JavaScript from Scratch

**Approach**: Write all commerce logic ourselves using vanilla JavaScript or a framework.

**Pros**:
- Complete control over all functionality
- No external dependencies
- Easier to customize for specific requirements
- Smaller bundle size (only what we need)

**Cons**:
- 3-4 weeks additional development time
- Need to implement authentication security ourselves
- Must maintain all commerce logic indefinitely
- Higher risk of bugs and security issues
- Reinventing the wheel for commodity features

**Why Rejected**: Time-to-market is critical, and we'd be reimplementing well-solved problems.

---

### Alternative 2: Use Generic Headless Commerce Library

**Approach**: Use a framework-agnostic commerce library (e.g., Commerce.js, Snipcart).

**Pros**:
- More flexible than Adobe's dropins
- Potentially better documentation
- Active open-source communities

**Cons**:
- Not optimized for Adobe Commerce
- Would need custom integration layer for Adobe Commerce APIs
- Doesn't understand Adobe-specific concepts (customer groups, CCDM, etc.)
- Less suitable for Adobe ecosystem demos

**Why Rejected**: Not designed for Adobe Commerce, would create integration burden.

---

### Alternative 3: Mix of Dropins and Custom Components

**Approach**: Use dropins for some features, custom code for others (e.g., use dropin for cart, custom code for PDP).

**Pros**:
- Balance flexibility and speed
- Use dropins where they fit well
- Custom code where needs are unique

**Cons**:
- Inconsistent UX between dropin and custom areas
- Need to maintain integration between the two
- More complex architecture
- Harder to reason about data flow

**Why Rejected**: Adds architectural complexity without clear benefit. We chose to use dropins where appropriate and EDS blocks for BuildRight-specific features, but keep them cleanly separated.

---

## Implementation Notes

### Demo Mode Strategy
For demo mode, we'll:
1. Create mock services that simulate Adobe Commerce APIs
2. Configure dropins to point to mock endpoints
3. Ensure mock responses match real API structure
4. Store session data in localStorage/sessionStorage

### Production Migration Path
To move to production:
1. Update dropin configuration with real Adobe Commerce endpoints
2. Remove demo mode toggles
3. Configure authentication with real Adobe Commerce instance
4. Connect to real ACO service
5. Test with real customer data

### Customization Approach
- Use dropin slots for targeted UI customization
- Override design tokens for consistent BuildRight branding
- Listen to dropin events for integration with custom features
- Wrap dropins in EDS blocks where needed for consistency

---

## Related Decisions

- [ADR-002: Use EDS Blocks for Content-Driven Components](./ADR-002-use-eds-blocks-for-content.md) - Explains when to use EDS blocks vs dropins
- [ADR-003: Mock ACO Service Architecture](./ADR-003-mock-aco-service.md) - How we'll mock the backend for demos
- [ADR-005: Dual-Mode Authentication](./ADR-005-dual-mode-authentication.md) - How auth works in demo vs production

---

## References

- [Adobe Commerce Storefront SDK Documentation](https://experienceleague.adobe.com/developer/commerce/storefront/sdk/)
- [Dropin Architecture Documentation](../DROPIN-ARCHITECTURE.md)
- [Block vs Dropin Decision Matrix](../BLOCK-VS-DROPIN-MATRIX.md)

---

**Last Updated**: November 15, 2024

