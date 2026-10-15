# ADR-005: Authentication & Authorization

## Status

Accepted

## Date

2025-12-02

## Context

The Workflow Manager requires secure access control for:

1. **User Types**:
   - **Market Operations Team**: Internal Elia staff managing all tenants
   - **Tenant Users**: Company employees managing their own workflows
   - **Future**: Market participants via self-service portal

2. **Multi-Tenancy Requirements**:
   - Users belong to exactly one tenant (company)
   - Market Ops can access all tenants
   - Strict tenant isolation at data level
   - Users cannot see other tenants' data

3. **Authorization Levels**:
   - **Tenant Admin**: Manage users, create workflows
   - **Tenant Operator**: Execute workflow steps, view workflows
   - **Tenant Viewer**: Read-only access
   - **Market Ops**: Full access to all tenants

4. **Integration Constraints**:
   - Must integrate with existing Kong Dev Portal eventually
   - May need federation with tenant IDPs (future)
   - API authentication for background jobs
   - Session management for web UI

5. **Security Requirements**:
   - JWT-based authentication
   - Role-Based Access Control (RBAC)
   - Audit logging of all actions
   - Secure token storage
   - Token refresh mechanism

## Decision

We will implement a **JWT-based authentication system** with **Role-Based Access Control (RBAC)** and **PostgreSQL Row-Level Security (RLS)** for data isolation.

### Architecture Overview

```
┌──────────────┐
│    Client    │
│  (Browser)   │
└──────┬───────┘
       │ 1. Login (email/password)
       ▼
┌────────────────────────────────┐
│      Auth Endpoint             │
│  POST /auth/login              │
│  ┌──────────────────────────┐  │
│  │  1. Verify credentials   │  │
│  │  2. Generate JWT         │  │
│  │  3. Return access token  │  │
│  └──────────────────────────┘  │
└────────┬───────────────────────┘
         │ 2. Access token (JWT)
         ▼
┌────────────────────────────────┐
│       Client Storage           │
│  localStorage / sessionStorage │
└────────┬───────────────────────┘
         │ 3. API Request + JWT
         ▼
┌────────────────────────────────┐
│      API Gateway               │
│  ┌──────────────────────────┐  │
│  │  Auth Middleware         │  │
│  │  1. Extract JWT          │  │
│  │  2. Verify signature     │  │
│  │  3. Check expiration     │  │
│  │  4. Decode payload       │  │
│  │  5. Attach to request    │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  Tenant Middleware       │  │
│  │  1. Get tenant from JWT  │  │
│  │  2. Set RLS context      │  │
│  │  3. Enforce isolation    │  │
│  └──────────────────────────┘  │
│  ┌──────────────────────────┐  │
│  │  Authorization Check     │  │
│  │  1. Check permissions    │  │
│  │  2. Validate access      │  │
│  └──────────────────────────┘  │
└────────┬───────────────────────┘
         │ 4. Authorized request
         ▼
┌────────────────────────────────┐
│      GraphQL Resolvers         │
│  (with user context)           │
└────────────────────────────────┘
```

### JWT Payload Structure

```typescript
// JWT Payload
interface JWTPayload {
  // Standard claims
  sub: string; // User ID
  iss: string; // Issuer (workflow-manager)
  aud: string; // Audience (workflow-manager-api)
  iat: number; // Issued at (timestamp)
  exp: number; // Expiration (timestamp)

  // Custom claims
  tenantId: string; // Tenant/Company ID
  email: string; // User email
  name: string; // User name
  role: UserRole; // User role
  permissions: string[]; // Explicit permissions
}

type UserRole =
  | 'market_ops' // Market Operations (Elia staff)
  | 'tenant_admin' // Tenant administrator
  | 'tenant_operator' // Tenant operator
  | 'tenant_viewer'; // Tenant viewer (read-only)
```

### Database Schema

```sql
-- libs/database/src/postgres/migrations/001_auth_schema.sql

-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('market_ops', 'tenant_admin', 'tenant_operator', 'tenant_viewer')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'locked')),
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Refresh tokens
CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  revoked_at TIMESTAMPTZ
);

-- Audit log
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  tenant_id UUID REFERENCES tenants(id),
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT,
  details JSONB,
  ip_address TEXT,
  user_agent TEXT,
  occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permissions (for fine-grained control)
CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  resource_type TEXT NOT NULL,
  action TEXT NOT NULL
);

CREATE TABLE role_permissions (
  role TEXT NOT NULL,
  permission_id UUID NOT NULL REFERENCES permissions(id),
  PRIMARY KEY (role, permission_id)
);

-- Indexes
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_tenant ON audit_log(tenant_id);
CREATE INDEX idx_audit_log_occurred_at ON audit_log(occurred_at);

-- Row-Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Market Ops can see all users
CREATE POLICY market_ops_users ON users
  FOR ALL
  TO market_ops_role
  USING (true);

-- Tenant users can only see users in their tenant
CREATE POLICY tenant_users_isolation ON users
  FOR SELECT
  TO app_role
  USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

### Authentication Implementation

```typescript
// apps/api/src/auth/auth.service.ts

import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

export class AuthService {
  private readonly JWT_SECRET = process.env.JWT_SECRET!;
  private readonly JWT_EXPIRATION = '1h';
  private readonly REFRESH_TOKEN_EXPIRATION = '7d';

  constructor(
    private userRepository: UserRepository,
    private refreshTokenRepository: RefreshTokenRepository
  ) {}

  async login(email: string, password: string): Promise<LoginResult> {
    // 1. Find user by email
    const user = await this.userRepository.findByEmail(email);
    if (!user) {
      throw new AuthenticationError('Invalid credentials');
    }

    // 2. Verify password
    const validPassword = await bcrypt.compare(password, user.passwordHash);
    if (!validPassword) {
      throw new AuthenticationError('Invalid credentials');
    }

    // 3. Check user status
    if (user.status !== 'active') {
      throw new AuthenticationError('Account is not active');
    }

    // 4. Generate tokens
    const accessToken = this.generateAccessToken(user);
    const refreshToken = await this.generateRefreshToken(user);

    // 5. Update last login
    await this.userRepository.updateLastLogin(user.id);

    return {
      accessToken,
      refreshToken,
      user: this.sanitizeUser(user),
    };
  }

  async refresh(refreshToken: string): Promise<RefreshResult> {
    // 1. Hash and find refresh token
    const tokenHash = this.hashToken(refreshToken);
    const storedToken = await this.refreshTokenRepository.findByHash(tokenHash);

    if (!storedToken || storedToken.revokedAt || storedToken.expiresAt < new Date()) {
      throw new AuthenticationError('Invalid refresh token');
    }

    // 2. Get user
    const user = await this.userRepository.findById(storedToken.userId);
    if (!user || user.status !== 'active') {
      throw new AuthenticationError('User not found or inactive');
    }

    // 3. Generate new access token
    const accessToken = this.generateAccessToken(user);

    return {
      accessToken,
      user: this.sanitizeUser(user),
    };
  }

  async logout(userId: string, refreshToken: string): Promise<void> {
    // Revoke refresh token
    const tokenHash = this.hashToken(refreshToken);
    await this.refreshTokenRepository.revokeByHash(tokenHash);
  }

  private generateAccessToken(user: User): string {
    const payload: JWTPayload = {
      sub: user.id,
      iss: 'workflow-manager',
      aud: 'workflow-manager-api',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour
      tenantId: user.tenantId,
      email: user.email,
      name: user.name,
      role: user.role,
      permissions: await this.getUserPermissions(user),
    };

    return jwt.sign(payload, this.JWT_SECRET, { algorithm: 'HS256' });
  }

  private async generateRefreshToken(user: User): Promise<string> {
    const token = generateSecureToken();
    const tokenHash = this.hashToken(token);

    await this.refreshTokenRepository.create({
      userId: user.id,
      tokenHash,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    });

    return token;
  }

  private async getUserPermissions(user: User): Promise<string[]> {
    // Get permissions for user's role
    return await this.userRepository.getPermissions(user.role);
  }

  private sanitizeUser(user: User): PublicUser {
    const { passwordHash, ...publicUser } = user;
    return publicUser;
  }

  private hashToken(token: string): string {
    return crypto.createHash('sha256').update(token).digest('hex');
  }
}
```

### Authentication Middleware

```typescript
// apps/api/src/middleware/auth.middleware.ts

import { FastifyRequest, FastifyReply } from 'fastify';
import jwt from 'jsonwebtoken';

export async function authMiddleware(request: FastifyRequest, reply: FastifyReply) {
  // 1. Extract token from Authorization header
  const authHeader = request.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    reply.code(401).send({ error: 'Missing or invalid authorization header' });
    return;
  }

  const token = authHeader.substring(7);

  try {
    // 2. Verify JWT
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload;

    // 3. Check expiration
    if (payload.exp < Math.floor(Date.now() / 1000)) {
      reply.code(401).send({ error: 'Token expired' });
      return;
    }

    // 4. Attach user to request
    request.user = {
      id: payload.sub,
      tenantId: payload.tenantId,
      email: payload.email,
      name: payload.name,
      role: payload.role,
      permissions: payload.permissions,
    };
  } catch (error) {
    reply.code(401).send({ error: 'Invalid token' });
    return;
  }
}
```

### Tenant Isolation Middleware

```typescript
// apps/api/src/middleware/tenant.middleware.ts

export async function tenantMiddleware(request: FastifyRequest, reply: FastifyReply) {
  if (!request.user) {
    reply.code(401).send({ error: 'Authentication required' });
    return;
  }

  // Set PostgreSQL session variable for Row-Level Security
  if (request.user.role !== 'market_ops') {
    await db.query('SET LOCAL app.current_tenant = $1', [request.user.tenantId]);
  }
  // Market Ops has access to all tenants, no restriction
}
```

### Authorization Decorators

```typescript
// apps/api/src/auth/decorators.ts

export function RequirePermission(permission: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const context = args[2] as GraphQLContext; // GraphQL context

      if (!context.user.permissions.includes(permission)) {
        throw new ForbiddenError(`Missing permission: ${permission}`);
      }

      return originalMethod.apply(this, args);
    };

    return descriptor;
  };
}

export function RequireRole(...roles: UserRole[]) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const context = args[2] as GraphQLContext;

      if (!roles.includes(context.user.role)) {
        throw new ForbiddenError(`Requires one of roles: ${roles.join(', ')}`);
      }

      return originalMethod.apply(this, args);
    };

    return descriptor;
  };
}

// Usage in resolvers
export const tenantResolvers = {
  Mutation: {
    @RequireRole('market_ops', 'tenant_admin')
    createTenant: async (parent, args, context) => {
      // Only market_ops or tenant_admin can create tenants
    },

    @RequirePermission('workflow:execute')
    executeStep: async (parent, args, context) => {
      // Requires specific permission
    }
  }
};
```

### Permission System

```sql
-- Seed default permissions
INSERT INTO permissions (name, description, resource_type, action) VALUES
  ('workflow:create', 'Create new workflows', 'workflow', 'create'),
  ('workflow:read', 'View workflows', 'workflow', 'read'),
  ('workflow:execute', 'Execute workflow steps', 'workflow', 'execute'),
  ('workflow:pause', 'Pause workflows', 'workflow', 'pause'),
  ('workflow:resume', 'Resume workflows', 'workflow', 'resume'),
  ('workflow:rollback', 'Rollback workflows', 'workflow', 'rollback'),
  ('workflow:delete', 'Delete workflows', 'workflow', 'delete'),
  ('tenant:create', 'Create tenants', 'tenant', 'create'),
  ('tenant:update', 'Update tenants', 'tenant', 'update'),
  ('tenant:delete', 'Delete tenants', 'tenant', 'delete'),
  ('user:create', 'Create users', 'user', 'create'),
  ('user:update', 'Update users', 'user', 'update'),
  ('user:delete', 'Delete users', 'user', 'delete');

-- Assign permissions to roles
INSERT INTO role_permissions (role, permission_id)
SELECT 'market_ops', id FROM permissions; -- Market Ops has all permissions

INSERT INTO role_permissions (role, permission_id)
SELECT 'tenant_admin', id FROM permissions WHERE resource_type IN ('workflow', 'user');

INSERT INTO role_permissions (role, permission_id)
SELECT 'tenant_operator', id FROM permissions WHERE resource_type = 'workflow' AND action IN ('create', 'read', 'execute', 'pause', 'resume');

INSERT INTO role_permissions (role, permission_id)
SELECT 'tenant_viewer', id FROM permissions WHERE resource_type = 'workflow' AND action = 'read';
```

### Audit Logging

```typescript
// apps/api/src/audit/audit.service.ts

export class AuditService {
  constructor(private auditRepository: AuditRepository) {}

  async log(event: AuditEvent): Promise<void> {
    await this.auditRepository.create({
      userId: event.userId,
      tenantId: event.tenantId,
      action: event.action,
      resourceType: event.resourceType,
      resourceId: event.resourceId,
      details: event.details,
      ipAddress: event.ipAddress,
      userAgent: event.userAgent,
    });
  }
}

// Middleware to automatically audit GraphQL operations
export function auditMiddleware(request: FastifyRequest, reply: FastifyReply) {
  const originalSend = reply.send;

  reply.send = function (payload: any) {
    // Log successful operations
    if (reply.statusCode < 400) {
      auditService.log({
        userId: request.user?.id,
        tenantId: request.user?.tenantId,
        action: request.body?.operationName || 'unknown',
        resourceType: 'graphql',
        resourceId: extractResourceId(request.body),
        details: {
          query: request.body?.query,
          variables: request.body?.variables,
        },
        ipAddress: request.ip,
        userAgent: request.headers['user-agent'],
      });
    }

    return originalSend.call(this, payload);
  };
}
```

## Consequences

### Positive

1. **Security**
   - JWT stateless authentication
   - Row-Level Security for data isolation
   - Fine-grained permissions
   - Complete audit trail

2. **Scalability**
   - No session storage needed
   - Stateless authentication
   - Horizontal scaling ready

3. **Developer Experience**
   - Simple token-based auth
   - Decorators for authorization
   - Type-safe user context

4. **Multi-Tenancy**
   - Automatic tenant isolation via RLS
   - Market Ops override capability
   - Clear tenant boundaries

5. **Flexibility**
   - Permission-based access control
   - Role-based defaults
   - Extensible for new roles

### Negative

1. **Token Revocation**
   - Cannot invalidate JWTs before expiration
   - Need refresh token revocation
   - Short-lived tokens recommended

2. **Token Size**
   - JWT can become large with many permissions
   - Sent with every request
   - Network overhead

3. **Refresh Complexity**
   - Need refresh token management
   - Rotation strategy
   - Storage requirements

4. **RLS Performance**
   - PostgreSQL RLS has overhead
   - Need to set session variable per request
   - May impact complex queries

### Mitigation Strategies

1. **Token Management**
   - Short-lived access tokens (1 hour)
   - Refresh tokens with rotation
   - Token revocation list for critical events

2. **Performance**
   - Cache permissions in JWT
   - Minimize JWT payload
   - Connection pooling for RLS

3. **Monitoring**
   - Failed login attempts
   - Token refresh patterns
   - Suspicious activity detection

4. **Security Hardening**
   - HTTPS only
   - Secure token storage
   - CSRF protection
   - Rate limiting

## Future Considerations

### Identity Federation (Phase 2)

```typescript
// Support for external IDPs
interface FederatedAuth {
  saml2: {
    enabled: boolean;
    idpMetadataUrl: string;
  };
  oidc: {
    enabled: boolean;
    issuer: string;
    clientId: string;
  };
}
```

### MFA Support (Phase 3)

```typescript
interface MFAConfig {
  enabled: boolean;
  methods: ('totp' | 'sms' | 'email')[];
  required: boolean;
}
```

### Kong Integration (Phase 2)

- Use Kong as API Gateway
- Delegate auth to Kong
- JWT validation at gateway level

## Related ADRs

- ADR-001: Hybrid Database Architecture (PostgreSQL + MongoDB)
- ADR-002: Hybrid Modular Monorepo Structure
- ADR-004: GraphQL API Architecture

## References

- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [PostgreSQL Row-Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
