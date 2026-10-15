# Design: KB-Enhanced Decision Trees for GameCreator Multiplayer

## Context

MLcreator is a Unity multiplayer project using:
- **Unity Netcode for GameObjects** (v2.7.0)
- **GameCreator 2** modules (Character, Inventory, Stats, Shooter)
- **Invasive Integration Pattern** (direct GC source modifications)
- **Unity Knowledge Base** (77,914 indexed items in Qdrant)

Current decision trees provide generic networking guidance but lack:
1. Project-specific architecture enforcement
2. GameCreator module awareness
3. Live KB queries for pattern discovery
4. Host/Client role differentiation

## Goals / Non-Goals

### Goals
- Integrate decision trees with Unity KB for intelligent recommendations
- Create GameCreator-specific sync decision trees
- Enforce project architecture (no NetworkTransform, IsNetworkOwner pattern)
- Guide Host/Client sync decisions for all GC modules

### Non-Goals
- Replace Unity documentation (reference, don't duplicate)
- Auto-generate code (provide patterns, not implementations)
- Support non-GameCreator Unity projects (MLcreator specific)

## Decisions

### Decision 1: KB Query Node Type

**What**: Add `kb_query` node type that queries Qdrant before recommendations

**Why**: Enables decision trees to leverage 77,914 indexed items for context-aware guidance

**Structure**:
```yaml
- id: "check-existing-patterns"
  type: "kb_query"
  content: "Searching KB for existing character sync implementations..."
  query:
    endpoint: "http://localhost:6333"
    collection: "unity_project_kb"
    search_terms: ["NetworkCharacterAdapter", "character sync", "IsNetworkOwner"]
    filters:
      kind: ["class", "method"]
      assembly_name: ["MLCreator_Multiplayer.Runtime"]
  on_results:
    found: "use-existing-pattern"
    not_found: "create-new-pattern"
```

### Decision 2: Project Context Injection

**What**: Inject MLcreator-specific constraints into all decision paths

**Why**: Prevents recommendations that violate architecture (e.g., suggesting NetworkTransform)

**Implementation**:
```yaml
project_context:
  constraints:
    - id: "no-network-transform"
      description: "NetworkTransform intentionally removed from character prefabs"
      enforcement: "error"
      alternative: "Use NetworkCharacterAdapter for character sync"

    - id: "invasive-integration"
      description: "GameCreator source is modified, use IsNetworkOwner pattern"
      pattern: "character.IsNetworkOwner"

    - id: "server-authoritative"
      description: "All gameplay actions use ServerRpc pattern"
      pattern: "[ServerRpc] methods for actions"
```

### Decision 3: GameCreator Module Trees

**What**: Create dedicated decision trees per GC module

**Why**: Each module has unique sync requirements

**Trees**:
| Tree | Purpose | Key Decisions |
|------|---------|---------------|
| `gc-character-sync.yaml` | Movement, animation, IK | Ownership, authority, prediction |
| `gc-inventory-sync.yaml` | Items, equipment | Persistence, batch sync, transactions |
| `gc-stats-sync.yaml` | Health, attributes | Batching, formulas, modifiers |
| `gc-shooter-sync.yaml` | Weapons, projectiles | Hit detection, damage authority |

### Decision 4: Host/Client Role Awareness

**What**: All trees consider Host vs Client vs Dedicated Server roles

**Why**: Authority and sync patterns differ based on network role

**Pattern**:
```yaml
- id: "check-network-role"
  type: "question"
  content: "What is your network topology?"
  options:
    - label: "Host (Listen Server)"
      description: "One player is server and client"
      context:
        is_host: true
        authority: "host-player"
      next: "host-sync-pattern"

    - label: "Dedicated Server"
      description: "Separate server, all players are clients"
      context:
        is_host: false
        authority: "dedicated-server"
      next: "dedicated-sync-pattern"

    - label: "Client Only"
      description: "Pure client connecting to remote server"
      context:
        is_client: true
        authority: "remote-server"
      next: "client-sync-pattern"
```

## Risks / Trade-offs

### Risk 1: KB Dependency
- **Risk**: Decision trees fail if KB unavailable
- **Mitigation**: Fallback to static recommendations when KB offline
- **Detection**: Check `http://localhost:6333/healthz` before KB queries

### Risk 2: Maintenance Burden
- **Risk**: Multiple trees to maintain across GC module updates
- **Mitigation**: Modular design with shared patterns, automated validation
- **Trade-off**: Accepted for better developer guidance

### Risk 3: Over-Prescription
- **Risk**: Trees too rigid, don't allow valid alternatives
- **Mitigation**: Include "Advanced" paths for experienced developers
- **Design**: Questions guide, outcomes recommend (not mandate)

## Migration Plan

### Phase 1 (Week 1)
1. Extend schema.yaml with kb_query and project_context
2. Create gc-character-sync.yaml (most critical)
3. Add KB integration to existing network-sync-method.yaml

### Phase 2 (Week 2)
1. Create remaining GC module trees
2. Add host-client-architecture.yaml
3. Update Serena memory with decision tree references

### Phase 3 (Week 3)
1. Validate all trees with sample scenarios
2. Document AI assistant usage patterns
3. Create decision tree quick reference guide

### Rollback
- Trees are additive - existing functionality unchanged
- Remove new YAML files to rollback
- No code changes required

## Open Questions

1. **KB Query Caching**: Should decision trees cache KB results? (Initial: No, always fresh)
2. **Visual Rendering**: Should trees render as interactive HTML? (Deferred to future)
3. **Telemetry**: Should we track which paths developers take? (Deferred to future)
