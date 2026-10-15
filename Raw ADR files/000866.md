# 002 - Auth: Device-Bound Tokens and Refresh Rotation

- Status: Accepted
- Date: 2025-11-30
- Deciders: Backend team
- References:
  - Backend auth requirements: `.kiro/specs/backend-authentication/requirements.md`
  - Technical Blueprint §5 (Authentication)

## Context

- We need short-lived access tokens (24h) and device-bound refresh tokens (30d) that can be revoked per device.
- Clients provide a UUID `deviceId` on login; refresh requests must include a matching device ID to prevent token replay across devices.
- Refresh tokens must be stored hashed and rotated/revoked on password reset/account disable or when rotating sessions.

## Decision

- Use HS256 JWTs signed with `JWT_SECRET`, issuer `JWT_ISSUER`, audience `JWT_AUDIENCE`.
- Access tokens: 24h TTL, include `sub`, `deviceId`, role claims; validated on every request.
- Refresh tokens: 30d TTL, include `jti`, `sub`, `deviceId`; stored hashed in `RefreshToken` with unique `(userId, deviceId)` and revocation metadata. TTLs are defaults, driven by `JWT_ACCESS_TTL`/`JWT_REFRESH_TTL`.
- Services:
  - `AuthService.login`: validates credentials + device UUID, issues access + refresh, persists hashed refresh via `upsertForDevice`.
  - `RefreshService.refresh`: validates signature/iss/aud/exp + device binding, touches `lastUsed`, rotates on demand, revokes prior `jti` when rotating.
  - Revocation helpers: `revokeByDevice`, `revokeAllForUser` for password reset/account disable flows.
- Endpoints:
  - `POST /api/auth/login` (requires email, password, `deviceId` UUID) -> access/refresh tokens + expirations.
  - `POST /api/auth/refresh` (requires refresh token, optional deviceId for enforcement, optional rotate flag) -> new access token; optional new refresh.
- Secrets: `JWT_SECRET` must be high-entropy (>=32 bytes), stored in a secrets manager (never in repo), enforced at startup, and rotated via a controlled process; leakage invalidates token integrity and rotations will invalidate existing tokens (clients must re-auth).

## Consequences

- Sessions are constrained per device; replayed refresh tokens on other devices are rejected (`device-mismatch`).
- Secret rotation invalidates existing tokens; clients must re-auth.
- Revocation is efficient via indexes on `(userId, deviceId)` and `expiresAt`; rotation links prior `jti` via `replacedByJti`.
- Logs/tests enforce redaction of passwords, hashes, and raw tokens to avoid leakage.
