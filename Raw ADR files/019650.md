# ADR 0001: Runtime Versions Selection

Status: Accepted  
Date: 2025-09-12

## Context

Rails 8.0 is stable (latest 8.0.2.1). Ecosystem gems (Devise, Sidekiq, Pundit, dotenv, pg) have announced/support compatibility with Rails 8.x. We are starting a new codebase with no legacy upgrade burden.

## Decision

Adopt latest stable versions at project start with pinned minor versions and security/bugfix auto-updates:
| Component | Version Strategy | Initial Pin |
|-----------|------------------|-------------|
| Ruby | Latest stable 3.3.x | 3.3.2 (update if 3.3.3 security) |
| Rails | 8.0.x pinned to ~> 8.0 | 8.0.2.1 |
| Postgres | 16.x | 16 |
| Redis | 7.x | 7.2 (image: redis:7.2-alpine) |
| Node (frontend) | Active LTS | 20.x |
| Sidekiq | 7.x | ~> 7.2 |
| Vite | Latest minor within major | ^5.x |

## Rationale

- Fresh greenfield → no need to straddle 7.x APIs.
- Rails 8 improvements and security patches already flowing.
- Ecosystem maturity confirmed.
- Using modern Ruby (3.3) yields better YJIT/PRISM parser performance.

## Constraints & Mitigations

| Risk                                    | Mitigation                                                                  |
| --------------------------------------- | --------------------------------------------------------------------------- |
| Hidden gem incompatibility emerges      | Add automated CI matrix; fallback patch monkey if urgent; reassess locking. |
| Breaking change in patch release (rare) | Use `~>` pessimistic versioning; review changelogs before bump.             |
| Railway build image lag                 | Supply explicit Dockerfile with correct toolchain.                          |

## Upgrade Policy

- Weekly Dependabot/Gemnasium review; auto-merge security patches.
- Quarterly review to lift minor pins (if any).
- Emergency patch (<24h) for CVEs scored >= 7.0.

## Implementation Tasks

1. Add `.ruby-version` with 3.3.2.
2. Gemfile specify `ruby "3.3.2"` and `rails '~> 8.0'`.
3. Dockerfile uses official `ruby:3.3.2-slim`.
4. Node version enforced via `.nvmrc` and `engines` in `package.json`.

## Alternatives Considered

- Rails 7.1 for extra conservative stability (rejected: lost time vs limited benefit).
- GoodJob to avoid Redis (rejected: performance & future scaling).

## Status Tracking

Revisit: 2026-01-15 or earlier if Rails 8.1 stable with compelling features.

## References

- Rails 8.0 changelog excerpt (user supplied).

---

Accepted.
