# ADR-001: Vidking as Exclusive Video Provider

Status: Accepted
Date: 2024-12-18
Owner: Wyvern Stream Team
Related Features: [Core Streaming](file:///d%3A/COMPROG/Wyvern%20Stream/wyvern-stream/docs/Features/streaming.md)
Supersedes: N/A
Superseded by: N/A

> Usage: draft here first. Once accepted, save a copy as `docs/ADR/ADR-{{Number}}-{{short-kebab-title}}.md` (English, kebab-case) and keep the template unchanged.

---

## Context

Wyvern Stream needs a video delivery mechanism for streaming movies and TV shows. The primary options are torrent-based P2P streaming or HTTP embed providers. The system must support mobile devices (iOS/Android) and minimize liability and infrastructure costs.

---

## Decision

We will use **Vidking and compatible HTTP embed providers** (SuperEmbed, VidSrc, etc.) via iframe embedding. We explicitly reject torrent/P2P solutions.

Key points:

- Exclusive reliance on third-party HTTP embeds.
- No self-hosted video content.
- No P2P/BitTorrent protocols.
- "Sandbox removal" for iframes to allow third-party players to function.

---

## Alternatives considered

### Torrent/P2P (WebTorrent)

- Pros: Decentralized, high quality potential, no server costs.
- Cons: Incompatible with iOS (no WebRTC Data Channels), user liability (uploading), high latency startup.
- Rejected because: Mobile compatibility is a hard requirement; legal risks are higher for users.

### Self-Hosted Video

- Pros: Full control, custom player, reliability.
- Cons: Massive storage and bandwidth costs, legal liability.
- Rejected because: Cost and liability are prohibitive for this MVP.

---

## Consequences

### Positive

- Universal mobile/TV compatibility (standard HTML5 video).
- Zero infrastructure cost for video hosting.
- Clear legal boundary (linking/embedding vs hosting).

### Negative / risks

- Reliability depends on third-party providers (unreliable availability).
- Potential for intrusive ads (mitigated by selecting ad-blocker friendly providers).
- Security risk of removing iframe sandbox (mitigated by strict provider selection).

- Mitigation: Implement multi-provider fallback system (VideoPlayer component).

---

## Impact

### Code

- Affected modules / services: `src/components/player/VideoPlayer.tsx`
- New boundaries / responsibilities: Player component handles provider switching.
- Feature flags / toggles: None.

### Data / configuration

- Data model / schema changes: None (TMDB ID is the only key).
- Config changes: None.
- Backwards compatibility: N/A.

### Documentation

- Feature docs to update: `docs/Features/streaming.md`
- Testing docs to update: `docs/Testing/strategy.md` (mocking external iframes).
- Architecture docs to update: N/A.
- Notes for `AGENTS.md`: Mocks only for external third-party systems.

---

## Verification (Mandatory: describe how to test this decision)

### Objectives

- Prove that video plays on target devices (including iOS).
- Prove that fallback mechanism works when a provider fails.

### Test environment

- Environment: Local dev environment.
- Data and reset strategy: N/A.
- External dependencies: Real embed providers (SuperEmbed, VidSrc).

### Test commands

- build: `npm run build`
- test: `npm run test`
- format: `npx prettier --write .`

### New or changed tests

| ID | Scenario | Level (Unit / Int / API / UI) | Expected result | Notes / Data |
| --- | --- | --- | --- | --- |
| VID-001 | Load movie (Inception) | UI | Player loads, iframe has correct src | TMDB ID: 27205 |
| VID-002 | Switch provider | UI | Iframe src updates to new provider | |

### Regression and analysis

- Regression suites to run: Core Page tests.
- Static analysis: ESLint.
- Monitoring during rollout: Manual verification of provider uptime.

---

## Rollout and migration

- Migration steps: N/A (Greenfield).
- Backwards compatibility: N/A.
- Rollback: Revert to single provider if multi-provider fails (unlikely).

---

## References

- Issues / tickets: N/A
- Related ADRs: N/A

---

## Filing checklist

- [x] File saved under `docs/ADR/ADR-{{Number}}-{{short-kebab-title}}.md` (not in `docs/templates/`).
- [x] Status reflects real state (`Proposed`, `Accepted`, `Rejected`, `Superseded`).
- [x] Links to related features, tests, and ADRs are filled in.
