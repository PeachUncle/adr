# ADR-004: Platform One Keycloak Integration for RBAC

**Status**: Accepted
**Date**: 2024-12-11
**Deciders**: Platform Architecture Team, Security Team

## Context

Aegis requires enterprise-grade authentication and role-based access control (RBAC) to support multi-tenant government deployments. Users have varying roles (OrgAdmin, ISSO, DevSecOps, Developer, Auditor) with different permission levels.

**Requirements**:

- NIST 800-53 IA-2: Identification and Authentication
- NIST 800-53 AC-2: Account Management
- NIST 800-53 AC-3: Access Enforcement
- NIST 800-53 AC-6: Least Privilege
- Multi-factor authentication (MFA) required for IL4+
- Integration with DoD PKI (CAC/PIV cards) for IL5
- SSO across Platform One ecosystem
- Support for 5 distinct roles with different permissions

**Constraints**:

- Must work with Platform One Big Bang deployment
- Government cloud environments (Azure Gov, AWS GovCloud)
- Cannot build custom auth system (security risk, compliance burden)

## Decision

We will integrate with **Platform One Keycloak** for authentication and RBAC:

### 1. Keycloak Configuration

**Platform One Keycloak Instance**:

- URL: `https://login.dso.mil`
- Realm: `baby-yoda` (Platform One standard realm)
- Protocol: OpenID Connect (OIDC)

**Client Configuration**:

```json
{
  "clientId": "aegis",
  "name": "Aegis DevSecOps Platform",
  "protocol": "openid-connect",
  "rootUrl": "https://aegis.dso.mil",
  "redirectUris": ["https://aegis.dso.mil/*", "http://localhost:3000/*"],
  "webOrigins": ["+"],
  "publicClient": false,
  "clientAuthenticatorType": "client-secret",
  "standardFlowEnabled": true,
  "directAccessGrantsEnabled": false,
  "serviceAccountsEnabled": true,
  "authorizationServicesEnabled": true,
  "attributes": {
    "pkce.code.challenge.method": "S256",
    "access.token.lifespan": "300",
    "sso.session.idle.timeout": "1800"
  }
}
```

### 2. Role Definitions

**Keycloak Realm Roles** (mapped to Aegis roles):

```yaml
roles:
  - name: aegis-org-admin
    description: 'Organization Administrator - Full tenant management'
    composite: false

  - name: aegis-isso
    description: 'Information System Security Officer - Compliance & audit'
    composite: false

  - name: aegis-devsecops
    description: 'DevSecOps Engineer - CI/CD and policy management'
    composite: false

  - name: aegis-developer
    description: 'Developer - Read-only evidence access'
    composite: false

  - name: aegis-auditor
    description: 'Auditor - Cross-tenant read-only (compliance review)'
    composite: false
```

**Permission Matrix**:

| Resource        | OrgAdmin | ISSO | DevSecOps | Developer | Auditor          |
| --------------- | -------- | ---- | --------- | --------- | ---------------- |
| Manage Users    | ✅       | ❌   | ❌        | ❌        | ❌               |
| Manage Projects | ✅       | ✅   | ✅        | ❌        | ❌               |
| View Evidence   | ✅       | ✅   | ✅        | ✅        | ✅ (all tenants) |
| Triage CVEs     | ✅       | ✅   | ✅        | ❌        | ❌               |
| Manage Policies | ✅       | ✅   | ✅        | ❌        | ❌               |
| Export POA&M    | ✅       | ✅   | ❌        | ❌        | ✅ (all tenants) |
| Deploy to Prod  | ✅       | ✅   | ✅        | ❌        | ❌               |
| View Audit Logs | ✅       | ✅   | ❌        | ❌        | ✅ (all tenants) |

### 3. Group-Based Role Assignment

Use Keycloak Groups to organize users by tenant:

```
/aegis
  /tenants
    /acme-corp
      - members (aegis-developer)
      - admins (aegis-org-admin)
      - security (aegis-isso)
      - engineers (aegis-devsecops)
    /dod-agency-x
      - members (aegis-developer)
      - admins (aegis-org-admin)
      - security (aegis-isso)
  /auditors
    - compliance-team (aegis-auditor)
```

**Group Attributes**:

```json
{
  "name": "acme-corp-admins",
  "path": "/aegis/tenants/acme-corp/admins",
  "attributes": {
    "tenantId": ["550e8400-e29b-41d4-a716-446655440000"],
    "tenantSlug": ["acme-corp"]
  },
  "realmRoles": ["aegis-org-admin"]
}
```

### 4. JWT Token Claims

Keycloak JWT includes custom claims for Aegis:

```json
{
  "sub": "f:12345678-1234-1234-1234-123456789012:user@acme-corp.com",
  "email": "user@acme-corp.com",
  "name": "John Doe",
  "preferred_username": "jdoe",
  "email_verified": true,

  "realm_access": {
    "roles": ["aegis-org-admin", "offline_access"]
  },

  "resource_access": {
    "aegis": {
      "roles": ["org-admin"]
    }
  },

  "aegis": {
    "tenantId": "550e8400-e29b-41d4-a716-446655440000",
    "tenantSlug": "acme-corp",
    "role": "ORG_ADMIN"
  },

  "iat": 1702306800,
  "exp": 1702307100,
  "iss": "https://login.dso.mil/realms/baby-yoda"
}
```

**Custom Claim Mapper** (Keycloak configuration):

```javascript
// Protocol Mapper: Tenant ID
const group = user
  .getGroups()
  .find((g) => g.path.startsWith('/aegis/tenants/'));
if (group) {
  token.setOtherClaims('aegis', {
    tenantId: group.attributes.tenantId[0],
    tenantSlug: group.attributes.tenantSlug[0],
    role: mapKeycloakRoleToAegisRole(user.realmRoles),
  });
}
```

### 5. Backend JWT Verification (Node.js)

```typescript
import { expressjwt } from 'express-jwt';
import jwksRsa from 'jwks-rsa';

// JWT verification middleware
export const requireAuth = expressjwt({
  secret: jwksRsa.expressJwtSecret({
    cache: true,
    rateLimit: true,
    jwksRequestsPerMinute: 5,
    jwksUri:
      'https://login.dso.mil/realms/baby-yoda/protocol/openid-connect/certs',
  }),

  audience: 'aegis',
  issuer: 'https://login.dso.mil/realms/baby-yoda',
  algorithms: ['RS256'],

  getToken: (req) => {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }
    return null;
  },
});

// Extract Aegis-specific claims
export function getAegisContext(req: Request): AegisContext {
  const token = req.auth as JWTPayload;

  return {
    userId: token.sub,
    email: token.email,
    name: token.name,
    tenantId: token.aegis?.tenantId,
    tenantSlug: token.aegis?.tenantSlug,
    role: token.aegis?.role as UserRole,
    isAuditor: token.realm_access?.roles?.includes('aegis-auditor') ?? false,
  };
}

// RBAC decorator for GraphQL resolvers
export function Authorized(roles: UserRole[]) {
  return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
    const originalMethod = descriptor.value;

    descriptor.value = function (...args: any[]) {
      const context = args[1]; // GraphQL context
      const userRole = context.aegis.role;

      if (!roles.includes(userRole)) {
        throw new UnauthorizedException(
          `Role '${userRole}' not authorized to access '${propertyKey}'`
        );
      }

      return originalMethod.apply(this, args);
    };

    return descriptor;
  };
}
```

**Usage in GraphQL Resolver**:

```typescript
@Resolver()
export class ProjectResolver {
  @Query(() => [Project])
  @Authorized([UserRole.ORG_ADMIN, UserRole.ISSO, UserRole.DEVSECOPS])
  async projects(@Ctx() context: AegisContext): Promise<Project[]> {
    return await this.projectService.findByTenant(context.tenantId);
  }

  @Mutation(() => Project)
  @Authorized([UserRole.ORG_ADMIN])
  async createProject(
    @Arg('input') input: CreateProjectInput,
    @Ctx() context: AegisContext
  ): Promise<Project> {
    return await this.projectService.create(input, context.tenantId);
  }
}
```

### 6. Frontend OIDC Integration (React)

```typescript
import { AuthProvider, useAuth } from 'react-oidc-context';

const oidcConfig = {
  authority: 'https://login.dso.mil/realms/baby-yoda',
  client_id: 'aegis',
  client_secret: process.env.REACT_APP_KEYCLOAK_CLIENT_SECRET,
  redirect_uri: `${window.location.origin}/callback`,
  post_logout_redirect_uri: window.location.origin,
  scope: 'openid profile email',
  response_type: 'code',

  // PKCE for additional security
  code_challenge_method: 'S256',
};

function App() {
  return (
    <AuthProvider {...oidcConfig}>
      <AegisApp />
    </AuthProvider>
  );
}

function AegisApp() {
  const auth = useAuth();

  if (auth.isLoading) {
    return <LoadingSpinner />;
  }

  if (!auth.isAuthenticated) {
    return <LoginPage onLogin={() => auth.signinRedirect()} />;
  }

  return (
    <ApolloProvider client={createApolloClient(auth.user?.access_token)}>
      <Router>
        <Dashboard />
      </Router>
    </ApolloProvider>
  );
}
```

### 7. Audit Logging (NIST 800-53 AU-2)

Log all authentication events:

```typescript
export async function logAuthEvent(event: AuthEvent): Promise<void> {
  await db.auditLog.create({
    data: {
      eventType: event.type, // 'LOGIN' | 'LOGOUT' | 'TOKEN_REFRESH' | 'PERMISSION_DENIED'
      userId: event.userId,
      tenantId: event.tenantId,
      ipAddress: event.ipAddress,
      userAgent: event.userAgent,
      success: event.success,
      errorMessage: event.error,
      metadata: {
        requestedResource: event.resource,
        requestedAction: event.action,
      },
      timestamp: new Date(),
    },
  });
}
```

## Consequences

### Positive

✅ **Enterprise SSO**: Users authenticated once for all Platform One apps
✅ **MFA Support**: Keycloak supports TOTP, SMS, CAC/PIV cards
✅ **Compliance**: Meets NIST 800-53 IA-2, AC-2, AC-3 requirements
✅ **Centralized Management**: ISSOs manage users in Keycloak console
✅ **Battle-tested**: Keycloak used across DoD Platform One ecosystem
✅ **Flexible RBAC**: Easy to add new roles without code changes

### Negative

❌ **External Dependency**: Aegis depends on Keycloak availability
❌ **Configuration Complexity**: Initial Keycloak setup requires expertise
❌ **Token Refresh**: Frontend must handle token expiration (5-minute lifetime)
❌ **Network Latency**: JWT verification adds 10-50ms per request

### Neutral

⚖️ **Migration Path**: Can migrate to alternative OIDC provider if needed
⚖️ **Local Development**: Requires running Keycloak locally or using shared dev instance

## Alternatives Considered

### Alternative 1: Custom auth system (username/password + JWT)

**Rejected**: Security risk (rolling own crypto). No MFA. Does not meet NIST 800-53 requirements.

### Alternative 2: Auth0 or Okta (commercial SaaS)

**Rejected**: Not FedRAMP authorized. Vendor lock-in. Data residency concerns for government cloud.

### Alternative 3: AWS Cognito or Azure AD B2C

**Rejected**: Vendor lock-in (cloud-specific). Does not integrate with Platform One ecosystem.

## Implementation Notes

- M3 implementation (Weeks 12-16)
- Keycloak client registration via Platform One Party Bus
- Test with local Keycloak instance in development
- Production: Platform One managed Keycloak
- Session timeout: 30 minutes idle, 8 hours maximum

## References

- [Platform One Keycloak Docs](https://docs-bigbang.dso.mil/latest/packages/keycloak/docs/)
- [NIST 800-53 Rev 5: IA-2 (Identification and Authentication)](https://csrc.nist.gov/Projects/risk-management/sp800-53-controls/release-search#!/control?version=5.1&number=IA-2)
- [OpenID Connect Specification](https://openid.net/specs/openid-connect-core-1_0.html)
- [RFC 7519: JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
