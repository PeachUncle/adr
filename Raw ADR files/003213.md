# ADR-022: Choice of Azure AD B2C for Authentication

**Date:** 2025-10-09

**Status:** Accepted

## Context

The PlumbingPOC application requires user authentication with support for email/password login and OAuth providers (Google, Microsoft). The current Supabase Auth provides these features with seamless integration to Row Level Security (RLS). For the Azure migration, we need an authentication service that maintains security, supports multiple identity providers, and integrates well with Azure Database for PostgreSQL RLS policies.

## Decision

We will use **Azure Active Directory B2C (Azure AD B2C)** as the authentication and identity management solution. This provides:

1. **Multi-Provider Support**: Email/password and OAuth (Google, Microsoft, Facebook)
2. **JWT Token Management**: Industry-standard JWT tokens for API authentication
3. **Scalability**: Handles user registration, password reset, and account management
4. **Security**: Enterprise-grade security with Azure AD integration
5. **Cost Effectiveness**: Pay-per-use model suitable for low-traffic applications

## Implementation Details

### Azure AD B2C Configuration

**Tenant Setup:**
```json
{
  "tenantName": "plumbingpoc.onmicrosoft.com",
  "countryCode": "CA",
  "location": "Canada Central",
  "sku": {
    "name": "Premium P1",
    "tier": "Premium"
  }
}
```

**Identity Providers Configuration:**
```json
{
  "identityProviders": [
    {
      "type": "Google",
      "clientId": "google-client-id",
      "clientSecret": "google-client-secret"
    },
    {
      "type": "Microsoft",
      "clientId": "microsoft-client-id",
      "clientSecret": "microsoft-client-secret"
    },
    {
      "type": "Local",
      "signInNameType": "Email"
    }
  ]
}
```

### User Flows

**Sign-in/Sign-up User Flow:**
```json
{
  "name": "B2C_1_signin_signup",
  "userFlowType": "SignInOrSignUp",
  "userFlowTypeVersion": 1,
  "identityProviders": ["Google", "Microsoft", "Local"],
  "attributes": ["email", "givenName", "surname"],
  "claims": ["email", "givenName", "surname", "sub"]
}
```

**Password Reset User Flow:**
```json
{
  "name": "B2C_1_password_reset",
  "userFlowType": "PasswordReset",
  "userFlowTypeVersion": 1
}
```

### Frontend Integration (MSAL)

**MSAL Configuration:**
```typescript
// packages/frontend/src/lib/azureAuth.ts
import { PublicClientApplication, Configuration } from '@azure/msal-browser';

const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: `https://plumbingpoc.b2clogin.com/plumbingpoc.onmicrosoft.com/B2C_1_signin_signup`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);
```

**Authentication Hook:**
```typescript
// packages/frontend/src/hooks/useAzureAuth.ts
import { useMsal } from '@azure/msal-react';
import { useState, useEffect } from 'react';

export function useAzureAuth() {
  const { instance, accounts, inProgress } = useMsal();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    if (accounts.length > 0) {
      const account = accounts[0];
      setUser({
        id: account.localAccountId,
        email: account.username,
      });

      // Fetch additional profile data from API
      fetchProfile(account.localAccountId);
    }
  }, [accounts]);

  const login = async () => {
    await instance.loginPopup({
      scopes: ['openid', 'profile', 'email'],
    });
  };

  const logout = () => {
    instance.logoutPopup();
  };

  return { user, profile, login, logout, loading: inProgress !== 'none' };
}
```

### Backend Integration

**JWT Token Validation:**
```typescript
// packages/backend/api/middleware/azureAuthMiddleware.js
import jwt from 'jsonwebtoken';

export function validateAzureToken(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.substring(7);
  try {
    // Verify token with Azure AD B2C public keys
    const decoded = jwt.verify(token, getAzurePublicKey(), {
      issuer: `https://plumbingpoc.b2clogin.com/${process.env.AZURE_TENANT_ID}/v2.0/`,
      audience: process.env.AZURE_CLIENT_ID,
    });

    req.user = {
      id: decoded.sub,
      email: decoded.email,
      name: decoded.name,
    };

    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Database RLS Integration

**PostgreSQL RLS Policies with Azure AD B2C:**
```sql
-- Custom function to extract user ID from JWT
CREATE OR REPLACE FUNCTION auth.jwt()
RETURNS jsonb
LANGUAGE sql
STABLE
AS $$
  SELECT current_setting('request.jwt.claims', true)::jsonb;
$$;

-- RLS policies using JWT claims
CREATE POLICY "Users can view their own requests"
ON requests FOR SELECT
USING (auth.jwt() ->> 'sub' = user_id::text);

CREATE POLICY "Users can insert their own requests"
ON requests FOR INSERT
WITH CHECK (auth.jwt() ->> 'sub' = user_id::text);

CREATE POLICY "Admins can view all requests"
ON requests FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_profiles
    WHERE id::text = auth.jwt() ->> 'sub'
    AND role = 'admin'
  )
);
```

## Consequences

### Positive

*   **Feature Complete**: Supports all required authentication methods
*   **Scalable**: Handles user management at enterprise scale
*   **Secure**: Industry-standard security with Azure AD foundation
*   **Flexible**: Supports custom user attributes and policies
*   **Integrated**: Deep integration with Azure ecosystem
*   **Cost Effective**: Pay-per-use model for low-traffic applications

### Negative

*   **Complexity**: More complex setup than Supabase Auth
*   **Learning Curve**: Requires understanding of Azure AD concepts
*   **Configuration**: Extensive configuration required for user flows
*   **Vendor Lock-in**: Azure-specific service and pricing
*   **Token Management**: Manual JWT validation in backend

### Mitigation Strategies

**Setup Complexity:**
- Use Azure portal wizards for initial configuration
- Follow Microsoft's comprehensive documentation
- Consider using Azure CLI for infrastructure as code

**Development Experience:**
- Implement comprehensive error handling for auth flows
- Create reusable authentication hooks and utilities
- Document authentication flows for future developers

**Testing:**
- Implement automated tests for authentication flows
- Test all identity providers thoroughly
- Validate token expiration and refresh scenarios

## Alternatives Considered

### Azure Active Directory (Azure AD)

**Pros:**
- Tightly integrated with Azure ecosystem
- Advanced enterprise features
- Lower cost for basic authentication

**Cons:**
- Designed for organizational accounts, not consumer applications
- Complex setup for external user authentication
- Not suitable for B2B2C scenarios

**Decision:** Rejected due to consumer application requirements

### Auth0

**Pros:**
- Feature-rich authentication platform
- Excellent developer experience
- Flexible pricing and deployment options

**Cons:**
- Additional vendor beyond Azure ecosystem
- Higher cost for small applications
- Another service to manage and monitor

**Decision:** Rejected to maintain Azure ecosystem consistency

### Firebase Authentication

**Pros:**
- Simple setup and excellent developer experience
- Good integration with mobile applications
- Generous free tier

**Cons:**
- Google ecosystem lock-in
- Less enterprise features than Azure AD B2C
- Not Azure native

**Decision:** Rejected due to Azure migration goals

### Supabase Auth (Continued)

**Pros:**
- Familiar and well-integrated with current stack
- Simple RLS integration with auth.uid()
- Good developer experience

**Cons:**
- Fixed cost regardless of usage
- Less enterprise features and compliance
- Vendor lock-in concerns

**Decision:** Rejected due to cost optimization goals

## Related Decisions

- ADR-001: Choice of Backend Platform (Supabase → Azure)
- ADR-021: Choice of Azure Database for PostgreSQL
- ADR-023: Choice of Azure SignalR Service for Real-time Features

## Success Metrics

### Technical Metrics
- [ ] All identity providers (Google, Microsoft, Email) working
- [ ] JWT tokens properly validated in backend
- [ ] RLS policies correctly filtering data by user
- [ ] Password reset and account management functional

### User Experience Metrics
- [ ] Login/logout flows smooth and intuitive
- [ ] Social login options clearly presented
- [ ] Error messages helpful and actionable
- [ ] Account creation process streamlined

### Security Metrics
- [ ] Tokens properly validated and not expired
- [ ] Secure token storage in frontend
- [ ] Proper logout clears all session data
- [ ] Password policies enforced

### Performance Metrics
- [ ] Authentication requests < 2 seconds
- [ ] Token refresh seamless in background
- [ ] No authentication-related errors in production
- [ ] Memory usage within application limits

## Future Considerations

**Scaling Up:**
- Implement Azure AD Premium features for advanced security
- Add multi-factor authentication (MFA)
- Implement conditional access policies

**Advanced Features:**
- Custom user attributes and claims
- Integration with Azure AD for enterprise users
- Social identity provider expansion

**Compliance:**
- SOC 2 Type II certification
- GDPR compliance features
- HIPAA compliance for healthcare applications

---

**Note:** Azure AD B2C is ideal for consumer-facing applications requiring multiple authentication methods. For enterprise-only applications, consider Azure AD instead.
