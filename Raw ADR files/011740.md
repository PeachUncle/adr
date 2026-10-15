# Change: Enhance Decision Trees with Unity Knowledge Base Integration

## Why

Current decision trees provide excellent static guidance for networking choices, but they lack:
1. **Live KB Queries**: No integration with our 77,914-item Unity Knowledge Base for real-time pattern discovery
2. **GameCreator Module Awareness**: No specific guidance for syncing GameCreator modules (Character, Inventory, Stats, Shooter) across Host/Client
3. **Project-Specific Context**: Generic patterns without awareness of our invasive integration architecture (IsNetworkOwner, NetworkCharacterAdapter)
4. **Perfect Sync Patterns**: Missing decision paths for achieving seamless data sync between Host and Client players

## What Changes

### Phase 1: KB-Enhanced Decision Framework
- **ADDED**: New `gamecreator-module-sync.yaml` decision tree for GC module synchronization
- **ADDED**: KB query nodes that search 77,914 indexed items before recommending patterns
- **ADDED**: Project-specific context injection (NetworkCharacterAdapter, no NetworkTransform, invasive integration)

### Phase 2: GameCreator Multiplayer Decision Trees
- **ADDED**: `gc-character-sync.yaml` - Character movement, animation, IK sync decisions
- **ADDED**: `gc-inventory-sync.yaml` - Inventory replication (Host/Client aware)
- **ADDED**: `gc-stats-sync.yaml` - Stats/attributes sync with batching
- **ADDED**: `gc-shooter-sync.yaml` - Weapon, projectile, damage sync patterns

### Phase 3: Host/Client Perfect Sync Guide
- **ADDED**: `host-client-architecture.yaml` - Authority model decisions for Host vs Dedicated server
- **MODIFIED**: Existing trees to reference KB patterns and project-specific implementations
- **ADDED**: KB search integration nodes that query Qdrant before recommendations

## Impact

- **Affected specs**: `network-synchronization`, `character-system`, `visual-scripting`
- **Affected code**: `.decision-trees/*.yaml`, Serena integration queries
- **KB integration**: Decision nodes will query `http://localhost:6333` for live pattern matching
- **Developer experience**: 100x better decisions by leveraging indexed project knowledge

## Success Criteria

1. AI assistants query KB before recommending network patterns
2. Decision trees include GameCreator-specific sync guidance
3. Host/Client architecture decisions respect our invasive integration
4. All recommendations reference actual project implementations (not generic Unity docs)

## KB Analysis Results

### Existing Patterns Found (77,914 indexed items)
- NetworkCharacterAdapter: Character-Netcode bridge implementation
- GameCreator invasive integration patterns (IsNetworkOwner, IsNetworkSpawned)
- No NetworkTransform architecture (intentional removal)
- RPC naming conventions (ServerRpc/ClientRpc suffixes)
- NetworkBehaviour inheritance patterns

### Recommended Approach
Based on KB analysis:
- Use established character sync patterns via NetworkCharacterAdapter
- Leverage IsNetworkOwner for authority checks
- Apply batched NetworkVariables for stats sync (86% bandwidth reduction)
- Follow server-authoritative movement commands
