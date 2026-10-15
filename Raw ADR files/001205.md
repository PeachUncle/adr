# ADR-013: Staging Environment Strategy

**Status**: Proposed  
**Date**: 2025-12-27  
**Deciders**: James (Owner)  
**Technical Story**: Safe production deployments

## Context and Problem Statement

Currently TaskMan-v2 has only two environments:
- Development (localhost)
- Production (planned)

This creates deployment risk - changes go directly from dev to prod without integration testing in a production-like environment.

## Decision Drivers

* **Deployment Risk** - Catch issues before production
* **Cost** - Additional infrastructure expense
* **Complexity** - Maintenance overhead
* **Auth Testing** - Verify Auth0 integration
* **Data Isolation** - Separate from production data

## Decision Outcome

**Chosen option: Railway Preview Environments**, leveraging Railway's built-in PR preview feature.

### Implementation

```yaml
# Railway.json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "numReplicas": 1,
    "healthcheckPath": "/health"
  },
  "environments": {
    "staging": {
      "DATABASE_URL": "${{ STAGING_DATABASE_URL }}",
      "AUTH0_DOMAIN": "${{ STAGING_AUTH0_DOMAIN }}"
    }
  }
}
```

### Environment Matrix

| Environment | Database | Auth0 Tenant | URL |
|-------------|----------|--------------|-----|
| Development | Local SQLite | None | localhost:8002 |
| Staging | Railway PostgreSQL | Auth0 Dev | staging.taskman.app |
| Production | Railway PostgreSQL | Auth0 Prod | taskman.app |

### Positive Consequences

* Automatic PR previews
* Isolated staging database
* Auth0 dev tenant for testing
* Zero additional cost (Railway free tier)

### Negative Consequences

* Staging data resets on each deploy
* Need separate Auth0 tenant config

## Auth0 Configuration

```yaml
# Auth0 Tenants
Production:
  domain: taskman.us.auth0.com
  audience: https://api.taskman.app

Staging:
  domain: taskman-dev.us.auth0.com
  audience: https://staging.api.taskman.app
```

## Links

* [Railway Environments](https://docs.railway.app/develop/environments)
* [Auth0 Multiple Tenants](https://auth0.com/docs/get-started/auth0-overview/create-tenants)
