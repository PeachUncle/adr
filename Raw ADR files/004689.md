# ADR-001: DLL Injection Architecture (Original)

Status: Implemented (To Be Superseded)
Date: 2021-XX-XX (original), 2025-12-18 (documented)
Owner: robinsch (original)
Related Features: [ActionCam Original](../Features/actioncam-original.md)
Supersedes: N/A
Superseded by: ADR-002 (pending)

---

## Context

WoW 3.3.5a (build 12340) does not include the ActionCam feature from retail WoW. The ActionCam CVars like `cameraActionAngle`, `cameraTargetFocusEnemyEnable`, etc. were introduced in WoW 7.0.3 (Legion).

To bring ActionCam functionality to 3.3.5a, the original author needed to:
1. Add new CVars that don't exist in the client
2. Implement the camera logic that reads these CVars
3. Hook into the game's camera system

Pure Lua addons cannot do this — they can only use existing CVars and API functions.

---

## Decision

Use DLL injection to extend the WoW client with custom CVars and camera behavior.

Key points:

- Patcher.exe modifies Wow.exe to enable DLL loading
- Extensions.dll injects into the running process
- DLL registers new CVars and implements camera hooks
- Lua addon provides settings UI that calls SetCVar()

---

## Alternatives considered

### Pure Lua addon

- Pros: No DLL, no patcher, no AV issues, no server detection
- Cons: Cannot add new CVars, cannot access camera internals
- Rejected because: Impossible to implement ActionCam features without client modification

### Memory editing without DLL

- Pros: Possibly less detectable
- Cons: More fragile, harder to maintain, same AV issues
- Rejected because: DLL is more maintainable and extensible

### Modified MPQ data files

- Pros: No executable modification
- Cons: Cannot add runtime behavior, only static data
- Rejected because: Camera behavior is code, not data

---

## Consequences

### Positive

- Full ActionCam functionality works
- CVars behave like native CVars
- Lua addon can be simple (just UI)

### Negative / risks

- **Antivirus detection**: DLL injection is commonly flagged as malware
  - Mitigation: Users must add exception (poor UX)
- **Server detection**: Some servers detect memory modification
  - Mitigation: None reliable; risk of ban
- **Time bug**: Patcher corrupts something causing perpetual night
  - Mitigation: Unknown, need to investigate patcher
- **Complex installation**: 3 separate steps
  - Mitigation: Could create installer, but increases AV issues

---

## Impact

### Code

- Affected modules: Wow.exe (patched), Extensions.dll (loaded), ActionCam addon (UI)
- Boundaries: DLL handles camera, Lua handles settings
- Feature flags: None

### Data / configuration

- Schema changes: N/A
- Config: Custom CVars added at runtime
- Backwards compatibility: Not applicable

### Documentation

- Feature docs: [actioncam-original.md](../Features/actioncam-original.md)
- Testing docs: Manual testing required
- AGENTS.md: Added rules for DLL development

---

## Verification

### Objectives

- CVars registered and accessible via SetCVar/GetCVar
- Camera responds to CVar changes
- Settings persist via SavedVariables

### Test environment

- Environment: WoW 3.3.5a client + private server
- Data: Fresh install
- Dependencies: Patcher.exe, Extensions.dll

### Test commands

- build: `msbuild Extensions.sln /p:Configuration=Release`
- test: Manual in-game verification

### New or changed tests

| ID | Scenario | Level | Expected result | Notes |
| --- | --- | --- | --- | --- |
| TST-001 | DLL loads successfully | Manual | No crash on login | Check game starts |
| TST-002 | CVars accessible | Manual | /console cameraActionAngle returns value | Run in console |
| TST-003 | Camera responds | Manual | Camera angle changes | Adjust slider |

---

## Rollout and migration

- Migration steps: User runs patcher, copies DLL, copies addon
- Backwards compatibility: N/A (new feature)
- Rollback: Restore original Wow.exe from backup

---

## References

- External: [Reddit Discussion](https://www.reddit.com/r/wowservers/comments/ActionCam)
- Related: ADR-002 (improved architecture, pending)

---

## Filing checklist

- [x] File saved under `docs/ADR/ADR-001-dll-injection-architecture.md`
- [x] Status reflects real state (`Implemented`)
- [x] Links to related features filled in
