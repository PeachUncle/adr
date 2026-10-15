# ADR: Unify agent UI into main Next.js app (Worker backend separate)

- Date: 2026-01-04
- Status: Proposed
- Owners: (you)

## Context
There are currently two “apps” living in this repo:

1) The shipping Next.js app (regex generator + snippets)
2) A standalone agent chat UI + backend runtime that are not wired into the Next.js UI

The goal is to **unify the UI** so the agent experience is just another route within the main Next.js app (Cloudflare Pages), while deploying the **agent backend as a separate Cloudflare Worker service**.

Observed in the current workspace:

- The Next route exists but renders nothing: [src/app/new-agent-app/page.tsx](../src/app/new-agent-app/page.tsx) is empty.
- The agent chat UI exists as a standalone React app under [src/agent-pages/app.tsx](../src/agent-pages/app.tsx) and [src/agent-pages/client.tsx](../src/agent-pages/client.tsx).
- The agent backend exists as a Cloudflare Worker-style entrypoint exporting `fetch()` and using `routeAgentRequest`: [src/agent-logic/server.ts](../src/agent-logic/server.ts).
- The main app is Next.js 15 and is deployed via Cloudflare Pages tooling (`@cloudflare/next-on-pages`): [package.json](../package.json).
- There is no Worker deployment config in the repo (no `wrangler.toml` found), so the agent backend has no clear deployment path yet.
- The agent code references dependencies that are not currently declared in `package.json` (e.g. `agents`, `ai`, `@ai-sdk/gateway`, `@daytonaio/sdk`, `@phosphor-icons/react`). Integration will surface missing dependency/build errors.

### Key design tensions
1. **Runtime mismatch**
   - The Next app is Cloudflare Pages + Edge runtime oriented.
   - The agent backend looks like a Cloudflare Worker/Durable Objects architecture (connection lifecycle hooks, scheduled cleanup).
   - The sandbox tool uses `process.env.SANDBOX_API_KEY` and Daytona SDK, which may require Node.js compatibility (unclear in Workers).

2. **Module path collisions**
   - `tsconfig.json` defines `@/* -> src/*`.
   - The agent UI imports `@/components/...` and `@/providers/...`, but those paths currently resolve to the main app components/providers, not `src/agent-pages/*`.

3. **Layout/CSS expectations**
   - The main app’s global layout always renders header/footer/container: [src/app/layout.tsx](../src/app/layout.tsx).
   - The agent UI expects to control theme classes and likely wants a full-bleed chat layout.
   - `src/agent-pages/client.tsx` imports `./styles.css`, but there is no `src/agent-pages/styles.css` file, so the agent UI will not build as-is.

## Decision

### Unify UI; deploy backend separately
- The agent chat UI becomes a Next.js route (e.g. `/new-agent-app`) within the existing app.
- The agent backend remains a separate Cloudflare Worker service (and likely uses Durable Objects / whatever the `agents` runtime requires).
- The Next.js app uses a **same-origin proxy/rewrite** to reach the Worker, so browser code does not need CORS handling or a different base URL.

Rationale:
- The backend entrypoint is already written like a Worker handler: [src/agent-logic/server.ts](../src/agent-logic/server.ts).
- Unifying UI reduces duplication (routing, auth, deploy surface) while keeping the backend in the runtime it appears to be designed for.

Tradeoffs:
- Requires a Worker deploy + per-environment routing configuration.
- Requires a deliberate convergence plan to avoid two parallel component systems living forever.

Non-goals (for the first slices):
- Perfectly merging design systems / refactoring every agent UI component into the existing site components.
- Re-hosting `routeAgentRequest` inside Next route handlers.

## Phased implementation plan

### Phase 0 — Inventory + alignment (half-day)
**Goal:** remove unknowns before wiring.

Slices:
- Confirm the Worker deployment plan (service name, environments, base URL).
- Decide the Next→Worker routing strategy (recommended: same-origin rewrite).

Deliverables:
- Minimal deployment doc for the agent backend (even if local-only first).
- A “known env var list” with where each secret lives.

Doubts to resolve:
- Does `agents` require Durable Objects bindings? If yes, what bindings and names?
- Can Daytona SDK run in the Worker runtime you’re targeting?

### Phase 1 — Unify UI mount (render agent UI inside Next)
**Goal:** `/new-agent-app` renders the agent chat UI inside the Next.js app.

Slices:
1. Replace the standalone SPA entrypoint with a Next page.
   - Treat [src/agent-pages/client.tsx](../src/agent-pages/client.tsx) as legacy “ReactDOM mount” code; in a unified app, Next pages own rendering.
2. Establish an explicit “agent UI namespace” to stop alias collisions.
   - Add a dedicated TS alias (example: `@agent-ui/*` → `src/agent-pages/*`).
   - Update imports inside the agent UI from `@/components/...` → `@agent-ui/components/...` and `@/providers/...` → `@agent-ui/providers/...`.
3. Fix CSS entrypoints.
   - Decide where the agent UI styles come from. Options:
     - A) Create the missing `src/agent-pages/styles.css`, OR
     - B) Remove that import and rely on the main app’s [styles.css](../styles.css) + Tailwind tokens.
4. Layout decision.
   - If the agent chat should not show the marketing chrome, add a route-group layout (e.g. `src/app/(agent)/layout.tsx`) that omits header/footer/container.

Rationale:
- Gets the “two app” problem solved early: one router, one deployment for UI.

Tradeoffs:
- You will temporarily have two UI component sets (existing app + agent UI). That’s acceptable if Phase 2 converges them.

### Phase 2 — Converge UI primitives (reduce “two design systems”)
**Goal:** progressively replace agent-only UI primitives with the existing app’s primitives, reducing long-term maintenance.

Slices (do in small PRs):
1. Choose convergence direction:
   - Recommended: keep the app’s existing primitives under `src/components/ui/*` as canonical.
2. Replace low-risk pieces first:
   - Buttons, inputs, cards, textarea.
3. Keep agent-only components when specialized:
   - Tool invocation cards, chat message layout, markdown rendering.

Rationale:
- Prevents permanent duplication while keeping early delivery fast.

Tradeoffs:
- Slightly more churn; do this after Phase 1 renders successfully.

### Phase 3 — Stand up the agent backend locally (backend-only vertical slice)
**Goal:** ensure `routeAgentRequest` works end-to-end without the Next UI.

Slices:
1. Add Worker dev config.
   - Add `wrangler.toml` (or equivalent) and minimal local dev instructions.
2. Add environment configuration.
   - `AI_GATEWAY_API_KEY` is required by the backend.
   - `SANDBOX_API_KEY` is required for sandbox tools (but note the runtime mismatch: current code reads from `process.env`).
3. Confirm endpoints and expected paths.
   - The UI uses `useAgent({ agent: "chat" })` and `useAgentChat(...)`, which will hit whatever `agents` expects under the hood.
   - Validate these endpoints are reachable and streamed responses work.

Doubts to resolve:
- What exact HTTP paths does `agents/react` call for `agent: "chat"`? (Confirm via browser devtools network panel once Phase 1 is mounted.)

Rationale:
- Avoids debugging UI + backend simultaneously.

Tradeoffs:
- Requires Worker tooling and local multi-process dev.

### Phase 4 — Connect unified Next UI to backend via same-origin proxy (first true E2E slice)
**Goal:** user can chat with the agent from `/new-agent-app`.

Slices:
1. Choose same-origin routing.
   - Add Next rewrites to send the `agents` client paths to the Worker dev/prod URL.
   - Keep the browser believing it’s talking to the Next origin.
2. Verify streaming.
   - Confirm `SUBAGENT_STATUS_DATA_PART_TYPE` events arrive and render.
3. Confirm stop/abort behavior.
   - UI’s Stop action should abort the stream and avoid double tool-result sends.

Rationale:
- Same-origin avoids CORS and keeps the client simple.

Tradeoffs:
- Slightly more infra/config complexity (rewrites per environment).

### Phase 5 — Harden and productize (stabilization)
**Goal:** reduce operational and architectural risk.

Slices:
- Runtime hardening:
  - Decide how sandbox execution runs in production (Worker-compatible? separate Node service? feature-flagged?).
- Dependency hygiene:
  - Add missing deps to `package.json` (or isolate agent code into its own package/workspace if it grows).
- UX integration:
  - Add a header link to `/new-agent-app` in [src/components/Header.tsx](../src/components/Header.tsx) if intended to be discoverable.
- Monitoring:
  - Log model usage already tracked in agent state; decide where it should surface.

## Work breakdown (simple checklist)

### UI wiring
- [x] Create Next page component for `/new-agent-app` that renders the chat UI.
- [x] Add a Next-only wrapper that provides `Providers` for the chat UI.
- [x] Resolve `@/*` import collisions by introducing a dedicated alias (`@agent-ui/*`). *(Not needed - imports already work correctly)*
- [x] Fix missing stylesheet import for agent UI. *(Not needed - uses globals.css)*
- [x] Decide whether agent page uses global header/footer or a dedicated layout. *(Uses dedicated layout without header/footer)*
- [ ] Plan convergence: gradually replace `src/agent-pages/components/*` primitives with `src/components/ui/*` where feasible.

### Backend wiring
- [x] Add Worker deployment config (`wrangler.jsonc`) and environment variable setup.
- [x] Add local dev story (`wrangler dev`, env vars, endpoints). See [docs/agent-backend-local-dev.md](../docs/agent-backend-local-dev.md)
- [x] Confirm streaming + persistent connection requirements. *(Uses agents library WebSocket connections)*
- [x] Resolve `SANDBOX_API_KEY` access pattern for the runtime you deploy to. *(Uses process.env with nodejs_compat flag)*

### Edge proxy / routing
- [x] Decide the proxy path prefix (e.g. `/agents/*` or what the client actually calls). *(`/agents/*` and `/check-open-ai-key`)*
- [ ] In production on Pages: configure Cloudflare **Worker Routes** for that prefix on the Pages hostname to send traffic to the agent Worker.
- [x] For local dev only (optional): use Next rewrites if you are not exercising WebSockets. *(Configured in next.config.mjs)*
- [ ] Confirm production routing on Cloudflare Pages works as intended (including WebSocket upgrades if used).

## Consequences

### Positive
- Fastest path to proving value: a thin E2E slice can land early.
- Preserves the agent backend’s intended architecture (connection-aware, session cleanup).

### Negative / Risks
- Requires additional infra/config (Worker deploy + rewrites/proxy).
- Potential runtime incompatibility: Daytona sandbox and/or parts of the `agents` runtime may not work where you plan to deploy.
- Build failures likely until dependencies are added and import paths are disambiguated.

## WebSocket & Durable Objects notes (Cloudflare Pages)

This section is here because the agent runtime code behaves like it expects a connection-oriented backend (see `onConnect` / `onClose` and scheduled cleanup in [src/agent-logic/server.ts](../src/agent-logic/server.ts)). If the `agents` library uses WebSockets (or other upgrade-based transports), routing must be designed so upgrades work reliably.

### Recommended production routing (same origin, WS-safe)

Goal: the browser talks to a single origin (your Pages domain), but traffic for the agent backend is handled by the separate Worker service.

Recommended approach:
- Configure **Cloudflare Worker Routes** on the same hostname as Pages, for an agent path prefix, e.g.:
   - `https://<your-pages-domain>/agents/*` → agent Worker
   - (use the actual path prefix that the `agents/react` client calls)

Why this is recommended:
- Worker routing happens at Cloudflare’s edge and supports WebSocket upgrade semantics.
- The browser sees a single origin, so you avoid CORS and you keep cookies/session behavior straightforward.
- You avoid having Next.js “pretend” to proxy a WebSocket, which is the common failure mode.

### What not to do
- Avoid implementing the agent backend behind a Next.js API route proxy (e.g. `src/app/api/agents/*`) if the client uses WebSockets or other upgrade flows.
- Avoid a “fetch proxy” in a Pages Function that forwards to the Worker service. That can work for plain HTTP, but is not a correct WS reverse proxy.

### Durable Objects (DO) concerns and checklist

The `agents` runtime may require DOs (or something equivalent) for per-session state, connection tracking, and cleanup scheduling.

Checklist:
- Confirm whether `agents` requires Durable Objects. If yes:
   - Define the DO class/binding names in the Worker’s deployment config (`wrangler.toml`).
   - Confirm the `routeAgentRequest(request, env)` call receives the DO bindings it expects.
   - Validate session stickiness (a session should consistently resolve to the same DO instance).

Operational notes:
- The agent code schedules cleanup based on active connections; if connections are not tracked correctly (e.g. due to routing through an incompatible proxy), you can get premature session deletion.
- If you expect long-lived tabs, validate behavior when the client disconnects/reconnects (your current grace period is 5 minutes).

## Open questions
- Where should the agent backend live in prod (same Cloudflare account, separate service name, custom domain)?
- Does `agents` require Durable Objects bindings, and what are the binding names/config?
- Is sandbox execution required for MVP? If not, can we feature-flag sandbox tools off until runtime is sorted?
- Should `/new-agent-app` be public, or gated behind a feature flag similar to `suggest_tab`?
