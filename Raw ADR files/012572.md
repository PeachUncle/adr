## Context
Nospeak has several hardcoded default endpoints spread across the client (Svelte) and core logic (TypeScript). Deployments need to change these defaults without rebuilding the app, especially for containerized environments.

SvelteKit/Vite `import.meta.env.PUBLIC_*` variables are build-time, which does not satisfy “runtime without rebuild”. The Node adapter provides a long-running server process that can read `process.env` at runtime and expose configuration to the browser via an API endpoint.

## Goals / Non-Goals

### Goals
- Provide a single central “defaults” model for all hardcoded relay/server endpoints.
- Allow operators to override defaults via environment variables, applied on server restart.
- Ensure strict scheme validation:
  - Relays: `wss://` only.
  - Server origins: `https://` only.
- Keep the endpoint same-origin (no CORS) and return only non-sensitive values.
- Always provide a full config object (env overrides merged with built-in defaults).

### Non-Goals
- Live reload of configuration without restarting the server/container.
- Full runtime configurability for Android static builds (no Node server available).
- Changing any user settings semantics (users can still override relays and Blossom servers in Settings).

## Decisions

### Decision: Use `/api/runtime-config` as the delivery mechanism
- The Node server reads environment variables via `process.env`.
- The browser client fetches the effective config from `/api/runtime-config` at startup.
- The app then uses this runtime config for all default endpoints.

### Decision: Client uses getters/store, not exported constants
Hardcoded defaults are currently exported as module-level constants. To allow runtime overrides to take effect after the client fetches config, consumers must read from a store/getter rather than from a static `const`.

### Decision: Validation and fallback rules
- If an env var is absent → use built-in defaults.
- If an env var is present but invalid (wrong scheme, empty list after parsing) → log a warning (implementation stage) and fall back to built-in defaults.
- Lists are comma-separated, trimmed, deduplicated while preserving the first occurrence.

## Runtime Configuration Keys
- `NOSPEAK_DISCOVERY_RELAYS`: comma-separated `wss://` relay URLs.
- `NOSPEAK_DEFAULT_MESSAGING_RELAYS`: comma-separated `wss://` relay URLs.
- `NOSPEAK_SEARCH_RELAY`: single `wss://` relay URL.
- `NOSPEAK_BLASTER_RELAY`: single `wss://` relay URL.
- `NOSPEAK_DEFAULT_BLOSSOM_SERVERS`: comma-separated `https://` server origins.
- `NOSPEAK_WEB_APP_BASE_URL`: single `https://` origin.
- `NOSPEAK_ROBOHASH_BASE_URL`: single `https://` origin.

## Security and Privacy Considerations
- `/api/runtime-config` MUST NOT expose secrets (no keys, tokens, or user data).
- All returned values are public endpoint URLs.
- Same-origin only reduces accidental cross-site exposure.
- Strict scheme rules reduce downgrade risk (`ws://`, `http://`) and avoid mixed-content issues.

## Platform Considerations
- Node server build: full runtime config support.
- Android/static build: no server; defaults remain built-in (and any existing build-time configuration continues to work where applicable).

## Deployment Notes
Docker Compose overrides are supported because the Node server reads `process.env` at runtime. Changes require container restart/recreate.
