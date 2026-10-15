# ADR 006: CI/CD with GitHub Actions

**Date**: 2026-01-13  
**Status**: Accepted

## Context

The application needs automated testing and deployment. Options:

1. **GitHub Actions** - Native to GitHub
2. **GitLab CI** - GitLab's CI/CD
3. **Jenkins** - Self-hosted CI/CD
4. **AWS CodePipeline** - AWS-native CI/CD

## Decision

**Use GitHub Actions for the entire CI/CD pipeline.**

Pipeline stages:
```
┌────────┐   ┌────────┐   ┌─────────────┐   ┌────────┐
│  Lint  │ → │  Test  │ → │ Build+Push  │ → │ Deploy │
└────────┘   └────────┘   └─────────────┘   └────────┘
     │            │              │               │
 Spotless    JUnit/Vitest   Docker images    SSH to EC2
 ESLint      PostgreSQL     ghcr.io          docker compose
```

## Consequences

### Pros
- **Free for public repos**: Unlimited minutes
- **Native integration**: No external service needed
- **Simple syntax**: YAML-based, easy to understand
- **Docker support**: Build and push images easily
- **Secrets management**: Built-in encrypted secrets

### Cons
- **Vendor lock-in**: Tied to GitHub
- **Limited parallelism**: 20 concurrent jobs (free tier)
- **No self-hosted caching**: Slower than self-hosted runners

## Pipeline Structure

```yaml
# .github/workflows/ci.yml
jobs:
  lint-backend:     # Spotless + ErrorProne
  lint-frontend:    # ESLint + Prettier
  test-backend:     # JUnit (needs PostgreSQL service)
  test-frontend:    # Vitest
  build-and-push-*: # Docker build → ghcr.io
  deploy:           # SSH → docker compose up
```

## Deployment Strategy

```bash
# On EC2 via SSH
docker pull ghcr.io/owner/starter-backend:$SHA
docker pull ghcr.io/owner/starter-frontend:$SHA
docker compose down
docker compose up -d
```

**Downtime**: ~30-60 seconds during deployment

## Required Secrets

| Secret | Purpose |
|--------|---------|
| `EC2_HOST` | EC2 public IP |
| `EC2_USER` | SSH user (ec2-user) |
| `EC2_SSH_KEY` | Private key for SSH |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `JWT_SECRET` | JWT signing key |
| `CORS_ALLOWED_ORIGINS` | Allowed origins |
| `GRAFANA_PASSWORD` | Grafana admin password |
| `RESEND_API_KEY` | Email API key |

## Future Improvements

- **Blue-green deployment**: Zero-downtime using two sets of containers
- **Rollback**: Automatic rollback on health check failure
- **Staging environment**: Deploy to staging before production
- **Performance tests**: Add k6 or similar load testing

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build-Push Action](https://github.com/docker/build-push-action)


