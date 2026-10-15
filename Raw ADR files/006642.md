# ADR-003: Azure AD Authentication for SQL Server

## Status

Accepted

## Date

2025-12-04

## Context

The patient portal stores PHI in Azure SQL Database. HIPAA requires strong authentication and access
controls. We need to decide between SQL authentication (username/password) and Azure AD authentication
for database access.

### Requirements

- HIPAA access control compliance
- Audit logging of all database access
- Integration with Azure RBAC
- No credential management in application code

### Considered Alternatives

1. **SQL Authentication only** - Username/password stored in Key Vault
2. **Azure AD Authentication only** - Managed identity, no credentials
3. **Mixed Mode** - Both SQL and Azure AD authentication
4. **Azure AD + MFA** - Interactive authentication for admin access

## Decision

We selected **Azure AD Authentication** with managed identity for the application:

| Approach      | Credentials in Code | Auditable | MFA Support |
| ------------- | ------------------- | --------- | ----------- |
| SQL Auth      | Via Key Vault       | Limited   | No          |
| Azure AD Only | None                | Full      | Yes         |
| Mixed Mode    | Via Key Vault       | Partial   | Optional    |

### Implementation

```bicep
// Azure AD administrator for SQL Server
resource sqlServerAdAdmin 'Microsoft.Sql/servers/administrators@2022-05-01-preview' = {
  parent: sqlServer
  name: 'ActiveDirectory'
  properties: {
    administratorType: 'ActiveDirectory'
    login: azureAdAdminLogin
    sid: azureAdAdminObjectId
    tenantId: tenant().tenantId
  }
}
```

### Connection String Pattern

```
Server=tcp:{server}.database.windows.net,1433;
Initial Catalog={database};
Authentication=Active Directory Managed Identity;
Encrypt=True;TrustServerCertificate=False;
```

### HIPAA Alignment

| HIPAA Control                | Implementation                       |
| ---------------------------- | ------------------------------------ |
| Unique User ID (164.312d)    | Azure AD principal for each user     |
| Automatic Logoff (164.312a3) | Azure AD token expiration            |
| Audit Controls (164.312b)    | Azure AD sign-in logs + SQL auditing |
| Authentication (164.312d)    | Azure AD MFA for admin access        |

## Consequences

### Positive

- No database credentials to manage or rotate
- Full Azure AD audit trail for all access
- Managed identity eliminates secret sprawl
- Consistent RBAC model across Azure resources

### Negative

- Requires Azure AD Premium for conditional access
- Slightly more complex initial setup
- Token-based auth has refresh overhead
- Emergency access requires break-glass procedure

### Mitigations

- Create dedicated SQL admin group in Azure AD
- Document break-glass procedure for emergencies
- Enable Azure AD diagnostic logging
- Test token refresh behavior under load

## References

- [Azure SQL Azure AD Auth](https://learn.microsoft.com/azure/azure-sql/database/authentication-aad-overview)
- [Managed Identity for Azure SQL](https://learn.microsoft.com/azure/azure-sql/database/authentication-azure-ad-user-assigned-managed-identity)
- [HIPAA Access Controls](https://www.hhs.gov/hipaa/for-professionals/security/guidance/access-control/index.html)
