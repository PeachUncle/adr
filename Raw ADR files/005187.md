# ADR-00002: OIDC-Agnostic Authentication Architecture

## Status
**Accepted** - 2024-09-28

## Context
The AGoat Publisher system needs to support authentication with multiple identity providers while maintaining flexibility for future provider additions. The system must support both existing providers (Azure AD, Cognito) and any future OIDC-compliant providers without requiring code changes.

## Decision
Implement an OIDC-agnostic Customer Identity and Access Management (CIAM) system that:
- Uses generic OIDC-compliant database schema
- Stores provider-specific data in JSONB fields
- Supports multiple instances of the same provider type
- Implements PKCE and state parameters for security
- Provides automatic token refresh capabilities
- Preserves user state during authentication flows

## Rationale
1. **Provider Flexibility**: OIDC standard compliance ensures compatibility with any OIDC provider
2. **Future-Proofing**: Generic schema allows adding new providers without database migrations
3. **Multi-Instance Support**: Different environments (dev, staging, prod) can use separate provider instances
4. **Security**: PKCE and state parameters provide modern OAuth2 security
5. **User Experience**: State preservation ensures seamless user experience
6. **Maintainability**: Single codebase handles all OIDC providers

## Consequences

### Positive
- **Flexibility**: Easy to add new OIDC providers
- **Security**: Modern OAuth2 security practices
- **Scalability**: Supports multiple provider instances
- **User Experience**: Seamless authentication flow
- **Maintainability**: Single authentication codebase
- **Standards Compliance**: Full OIDC compliance

### Negative
- **Complexity**: More complex initial implementation
- **Learning Curve**: Team needs to understand OIDC standards
- **Testing**: More test scenarios for different providers
- **Configuration**: More complex provider configuration

## Implementation Details

### Database Schema
```sql
-- Core CIAM system configuration
CREATE TABLE ciam_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_name VARCHAR(50) NOT NULL UNIQUE,
    provider_type VARCHAR(50) DEFAULT 'oidc',
    jwks_url TEXT,
    issuer_url TEXT,
    authorization_endpoint TEXT,
    token_endpoint TEXT,
    -- Provider instance identification
    provider_instance_id VARCHAR(100),
    provider_environment VARCHAR(50),
    provider_region VARCHAR(50),
    provider_domain VARCHAR(255),
    is_default_for_type BOOLEAN DEFAULT FALSE,
    -- Provider-specific configuration
    provider_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User-CIAM mapping
CREATE TABLE user_ciam_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    ciam_system_id UUID NOT NULL REFERENCES ciam_systems(id),
    oidc_subject VARCHAR(255) NOT NULL,
    provider_instance_id VARCHAR(100),
    provider_environment VARCHAR(50),
    token_issuer TEXT,
    is_current_ciam BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Key Features
1. **Provider Discovery**: Automatic OIDC discovery endpoint support
2. **Token Management**: Secure token storage with hashing
3. **State Preservation**: Return URL preservation during authentication
4. **Multi-Instance**: Support for multiple provider instances
5. **Automatic Refresh**: Background token refresh capabilities

### Security Measures
- PKCE implementation for all OAuth2 flows
- State parameter validation for CSRF protection
- Token hashing before database storage
- Secure session management
- Comprehensive audit logging

## References
- [OIDC Specification](https://openid.net/connect/)
- [OAuth2 PKCE RFC](https://tools.ietf.org/html/rfc7636)
- [Technical Implementation: OIDC-Agnostic CIAM](../../technical-implementation/authentication/oidc-agnostic-ciam.md)
- [Authentication Requirements](../../requirements-and-user-stories/final-functional/authentication-requirements.md)
- [Security Requirements](../../requirements-and-user-stories/final-nonfunctional/security-requirements.md)
