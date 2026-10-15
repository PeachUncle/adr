# ADR-024: Choice of Service Organization Strategy for Multi-Platform Support

**Date:** 2025-10-09

**Status:** Decided & Implemented

## Context

The PlumbingPOC backend includes external service integrations (email via Resend, SMS via Twilio) that will be incrementally migrated to Azure Communication Services during the Azure migration. We needed to decide on a service organization strategy that supports:

1. **Current single-provider usage** (Resend for email, Twilio for SMS)
2. **Future multi-provider support** (Azure Communication Services)
3. **Incremental migration** (gradual replacement of providers)
4. **Clean maintainability** (easy to understand and modify)

## Decision

We will maintain a **flat service organization** in `packages/backend/api/services/` with individual service files, rather than nested provider-specific directories. This approach supports incremental migration while keeping the codebase simple and maintainable.

### Current Structure (Implemented)
```
packages/backend/api/services/
├── email/
│   └── resend/
│       ├── client.js    # Email service (Resend implementation)
│       └── index.js     # Clean exports
└── sms/
    └── twilio/
        ├── client.js    # SMS service (Twilio implementation)
        └── index.js     # Clean exports
```

### Future Structure (When Multiple Providers Needed)
```
packages/backend/api/services/
├── emailService.js    # Email service (Azure Communication Services)
├── smsService.js      # SMS service (Azure Communication Services)
├── email/
│   ├── resend.js      # Legacy Resend client (if needed)
│   └── azure.js       # Azure Communication Services client
└── sms/
    ├── twilio.js      # Legacy Twilio client (if needed)
    └── azure.js       # Azure Communication Services client
```

## Key Principles

1. **Incremental Migration Support**: Services can be updated individually without directory restructuring
2. **Single Responsibility**: Each service file handles one communication channel
3. **Provider Abstraction**: Business logic doesn't know about specific providers
4. **Future-Proof**: Easy to add nested structure when multiple providers are needed simultaneously

## Implementation

### Current Implementation
- `packages/backend/api/services/email/resend/client.js`: Handles all email operations using Resend API
- `packages/backend/api/services/sms/twilio/client.js`: Handles all SMS operations using Twilio API
- Clean, focused APIs with error handling and environment configuration
- Organized by service type and provider for clear multi-platform support

### Migration Strategy
1. **Phase 1**: Update `emailService.js` to use Azure Communication Services
2. **Phase 2**: Update `smsService.js` to use Azure Communication Services
3. **Phase 3**: If multiple providers needed, create nested structure with legacy clients

## Consequences

### Positive
- **Simple Maintenance**: Flat structure is easy to understand and modify
- **Incremental Migration**: Can update services one at a time
- **Clean APIs**: Well-defined service interfaces
- **No Over-Engineering**: Only add complexity when multiple providers are actually needed

### Negative
- **Potential Future Refactor**: May need directory restructuring if multiple providers required
- **Less Explicit**: Provider choice is implicit in service implementation

### Implementation Timeline
- **Current**: Flat structure implemented and working
- **Migration**: Service-by-service updates (no structural changes needed)
- **Future**: Nested structure only if multiple providers required simultaneously

## Alternatives Considered

### Option A: Immediate Nested Structure (Rejected)
```
services/
├── email/
│   └── resend/
│       └── client.js
└── sms/
    └── twilio/
        └── client.js
```
**Rejected because**: Over-engineering for current single-provider needs. Would require immediate restructuring for no current benefit.

### Option B: Service Registry Pattern (Deferred)
```
services/
├── registry.js        # Service factory/registry
├── email.js          # Email service interface
├── sms.js            # SMS service interface
└── providers/        # Provider implementations
    ├── resend.js
    ├── twilio.js
    └── azure.js
```
**Deferred because**: Adds unnecessary abstraction complexity. Current flat structure is sufficient for incremental migration.

## Related Decisions

- ADR-019: Single Repository Strategy for Azure POC
- ADR-020: Azure Static Web Apps for Frontend Hosting
- ADR-021: Azure Database for PostgreSQL
- ADR-022: Azure AD B2C for Authentication
- ADR-023: Backend Configuration Architecture

## Success Criteria

- [x] Services work with current providers (Resend, Twilio)
- [x] Clean, maintainable service interfaces
- [x] Easy to update individual services for Azure migration
- [x] No unnecessary directory complexity
- [x] Future-ready for multi-provider scenarios
