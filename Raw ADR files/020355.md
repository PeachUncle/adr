# 11. Environment-Specific Profiles

Date: 2025-12-22

## Status

Accepted

## Context

The WinvestCo trading platform consists of 11 microservices that require different configurations across development, Docker/local testing, staging, and production environments. Key configuration differences include:

- **Database connections**: Local PostgreSQL vs. container hostnames vs. managed databases
- **Security secrets**: Development placeholders vs. production-grade secrets
- **Logging levels**: Debug/verbose for development vs. minimal for production
- **Trace sampling**: Full sampling for debugging vs. reduced sampling for production cost
- **Connection pools**: Conservative settings for dev vs. aggressive for production load
- **Payment provider**: Razorpay test keys vs. live keys
- **Trade execution**: Mock execution engine vs. real broker connections

Previously, configuration relied on environment variables with fallback defaults, which led to:
- Production secrets accidentally being committed as "defaults"
- Inconsistent configuration across services
- Difficulty onboarding new developers
- No clear separation between environments

## Decision

Implement Spring Boot profiles for environment-specific configuration:

### Profile Hierarchy

```
application.yml              # Common configuration (service name, virtual threads, etc.)
├── application-dev.yml      # Local development (localhost, debug logging)
├── application-docker.yml   # Docker Compose environment (container hostnames)
├── application-staging.yml  # Pre-production (env vars required, validation mode)
└── application-prod.yml     # Production (strict settings, no defaults for secrets)
```

### Environment Templates

```
.env.dev       # Development defaults (safe to use as-is)
.env.staging   # Staging placeholders (requires CI/CD secrets)
.env.prod      # Production placeholders (requires secrets management)
```

### Configuration Matrix

| Setting | dev | docker | staging | prod |
|---------|-----|--------|---------|------|
| Database URL | localhost | postgres:5432 | ${env} | ${env} |
| DDL-Auto | update | update | validate | none |
| Logging | DEBUG | INFO | INFO | WARN |
| Trace Sampling | 100% | 100% | 50% | 10% |
| Secrets | hardcoded dev | env with fallback | env required | env required |

## Consequences

### Positive

- **Clear separation**: Each environment has explicit, documented configuration
- **Fail-fast in production**: Missing required env vars cause startup failure
- **Developer experience**: `mvn spring-boot:run -Dspring-boot.run.profiles=dev` just works
- **Security**: Production never has fallback defaults for sensitive values
- **Consistency**: All 11 services follow the same profile structure

### Negative

- **More files**: 48 new profile files (4 profiles × 12 services)
- **Maintenance overhead**: Profile changes must be applied across all services
- **Learning curve**: New developers must understand profile activation

### Mitigations

- Document profile usage in README
- Consider Spring Cloud Config for centralized configuration in future
- Keep `application.yml` minimal, move all environment-specific values to profiles

## Usage

```bash
# Local development
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Docker Compose (already configured in docker-compose.yml)
docker-compose up

# Staging/Production (set via deployment configuration)
java -jar service.jar --spring.profiles.active=prod
```
