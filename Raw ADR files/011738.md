# Design: Fix Hotspot and Interaction Conflicts

## Context

GameCreator provides Hotspot and Trigger components for interactions. When adding multiplayer support via Netcode for GameObjects, we created `NetworkHotspotExtension` and `LocalPlayerResolver` to bridge these systems. However, conflicting patterns emerged:

1. Adding NetworkTransform/NetworkObject to static scene objects
2. Using both GC Trigger and NetworkHotspotExtension without proper integration
3. Reflection-based patching that doesn't work with GameCreator's PropertyGet system
4. Unclear guidance on which pattern to use when

**Stakeholders:** Game designers using triggers, developers maintaining multiplayer code.

## Goals / Non-Goals

### Goals
- XP pickups work correctly for each player in multiplayer
- Doors and other shared interactions work for all players
- Clear pattern for each interaction type
- Editor validation catches common mistakes

### Non-Goals
- Changing GameCreator Core code (we can only extend)
- Supporting non-Netcode multiplayer backends
- Automatic migration of existing scenes (provide tooling only)

## Decisions

### Decision 1: Static vs Networked Objects

**Rule:** Only objects that need ownership, state sync, or movement should have NetworkObject.

| Object Type | NetworkObject | NetworkTransform | Why |
|-------------|---------------|------------------|-----|
| Static XP pickup | NO | NO | Each client detects locally, no sync needed |
| Synced one-time pickup | YES | NO | Server validates who collects first |
| Moving platform | YES | YES | Position must sync |
| Door | Depends | NO | State sync only if door animation syncs |

**Rationale:** NetworkObject adds overhead and complexity. Static scene objects don't need network identity.

### Decision 2: Trigger Execution Flow

**Pattern for local-only interactions (XP pickup):**
```
Player enters trigger
  → Trigger.OnTriggerEnter detects "Local Player" (via PropertyGetGameObject)
  → PropertyGetGameObject resolves to local player (new GetGameObjectLocalNetworkPlayer)
  → Trigger executes instructions locally
  → No network involvement needed
```

**Pattern for synced interactions (one-time chest):**
```
Player enters trigger
  → NetworkTriggerAdapter.OnTriggerEnter intercepts
  → Validates player is local owner
  → Sends RequestTriggerServerRpc(triggerId, clientId)
  → Server validates (not already consumed, valid player)
  → Server marks as consumed, broadcasts DestroyTriggerClientRpc
  → All clients destroy object, but ONLY requesting client executes instructions
```

### Decision 3: PropertyGetGameObject Injection

**Problem:** LocalPlayerResolver tries to set `m_Target` (PropertyGetGameObject) to a GameObject directly.

**Solution:** Create `GetGameObjectLocalNetworkPlayer` class that:
1. Extends `PropertyTypeGetGameObject`
2. Returns `LocalPlayerResolver.Instance.LocalPlayerObject`
3. Handles null gracefully during initialization

```csharp
[Serializable]
public class GetGameObjectLocalNetworkPlayer : PropertyTypeGetGameObject
{
    public override GameObject Get(Args args)
    {
        return LocalPlayerResolver.Instance?.LocalPlayerObject;
    }

    public override string String => "Local Network Player";
}
```

### Decision 4: NetworkHotspotExtension + Trigger Integration

When both components are present:
1. NetworkHotspotExtension takes control
2. Disables Trigger's direct event handling
3. Routes through `RequestInteraction()` → Server validation → Client execution
4. Only the validated client executes the Trigger's instructions

**Implementation:**
```csharp
// In NetworkHotspotExtension.Awake()
m_Trigger = GetComponent<Trigger>();
if (m_Trigger != null)
{
    // Disable Trigger's event subscription
    m_Trigger.enabled = false;  // Prevent auto-execution
    m_ManagedTrigger = true;
}

// In TriggerGameCreatorHotspotClientRpc()
if (m_ManagedTrigger && NetworkManager.Singleton.LocalClientId == interactorId)
{
    m_Trigger.Execute(LocalPlayerResolver.Instance.LocalPlayerObject);
}
```

## Risks / Trade-offs

### Risk: Breaking existing setups
**Mitigation:**
- Validation warnings, not errors
- Provide "Fix" buttons in Editor
- Document migration path
- Don't auto-modify scenes

### Risk: Performance of PropertyGetGameObject lookup
**Mitigation:**
- Cache LocalPlayerResolver.Instance reference
- Only resolve on spawn/respawn, not every frame

### Trade-off: Complexity vs Flexibility
**Decision:** Provide simple patterns for common cases (local pickup, synced pickup, door), allow advanced configuration for edge cases.

## Migration Plan

### Phase 1: Add new components (non-breaking)
1. Add `GetGameObjectLocalNetworkPlayer`
2. Add `NetworkTriggerAdapter`
3. Add Editor validation

### Phase 2: Fix existing scenes
1. Run validator on all scenes
2. Fix flagged issues
3. Test each scene

### Rollback
- New components are additive, can be removed
- Scene changes can be reverted via git

## Open Questions

1. **Q:** Should we auto-detect "Local Player" targets and swap to network-aware version?
   **A:** Yes, LocalPlayerResolver should do this on spawn.

2. **Q:** How to handle triggers that reference specific players by name/ID?
   **A:** Out of scope - those are advanced cases, document only.

3. **Q:** What about triggers on spawned prefabs (not scene objects)?
   **A:** Those need NetworkObject. Document as separate pattern.
