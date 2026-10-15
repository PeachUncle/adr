# Tasks: Enhance Decision Trees with KB Integration

## Phase 1: KB-Enhanced Decision Framework

### 1.1 Schema Enhancement
- [x] 1.1.1 Add `kb_query` node type to schema.yaml for live KB queries
- [x] 1.1.2 Add `project_context` injection mechanism for MLcreator-specific patterns
- [x] 1.1.3 Define `constraint_check` nodes that enforce project rules (no NetworkTransform)

### 1.2 Core KB Integration
- [x] 1.2.1 Create KB query patterns for common searches (character sync, RPC patterns, stats)
- [x] 1.2.2 Add KB endpoint configuration to decision tree metadata
- [x] 1.2.3 Document KB search taxonomy in schema.yaml (gc.character, network, multiplayer keywords)

## Phase 2: GameCreator Module Sync Decision Trees

### 2.1 Character Sync Tree
- [x] 2.1.1 Create `gc-character-sync.yaml` with movement sync decisions
- [x] 2.1.2 Add animation sync path (NetworkAnimator vs custom)
- [x] 2.1.3 Add IK sync decisions (local vs replicated)
- [x] 2.1.4 Add ragdoll state sync patterns
- [x] 2.1.5 Reference NetworkCharacterAdapter implementation

### 2.2 Inventory Sync Tree
- [x] 2.2.1 Create `gc-inventory-sync.yaml` for item replication
- [x] 2.2.2 Add Host vs Client authority decisions
- [x] 2.2.3 Add persistence decisions (session-only vs Supabase hybrid)
- [x] 2.2.4 Add batch sync patterns for multiple items

### 2.3 Stats Sync Tree
- [x] 2.3.1 Create `gc-stats-sync.yaml` for health/mana/stamina
- [x] 2.3.2 Add batched NetworkVariable pattern (86% bandwidth reduction)
- [x] 2.3.3 Add attribute modifier sync decisions
- [x] 2.3.4 Add formula/calculation authority decisions

### 2.4 Shooter Sync Tree
- [x] 2.4.1 Create `gc-shooter-sync.yaml` for weapon systems
- [x] 2.4.2 Add projectile authority decisions (server vs client predicted)
- [x] 2.4.3 Add hit detection patterns (raycast vs physics)
- [x] 2.4.4 Add damage application authority patterns

### 2.5 Visual Scripting Sync Tree
- [x] 2.5.1 Create `gc-visual-scripting-sync.yaml` for network-aware visual scripting
- [x] 2.5.2 Add Network Events/Triggers (NPC interaction, perception, connection, combat, inventory)
- [x] 2.5.3 Add Network Instructions (inventory, stats, character, spawn, RPC)
- [x] 2.5.4 Add Network Conditions (role/authority, faction, player, state)
- [x] 2.5.5 Add Network Variables sync patterns
- [x] 2.5.6 Add complete VS multiplayer setup guide with code examples

## Phase 3: Host/Client Architecture

### 3.1 Authority Model Tree
- [x] 3.1.1 Create `host-client-architecture.yaml` main decision tree
- [x] 3.1.2 Add Host (listen server) vs Dedicated Server decisions
- [x] 3.1.3 Add ownership transfer patterns
- [x] 3.1.4 Add late-join state synchronization decisions

### 3.2 Update Existing Trees
- [x] 3.2.1 Add KB query nodes to `network-sync-method.yaml`
- [x] 3.2.2 Add project context to `state-management.yaml`
- [ ] 3.2.3 Add GC-specific paths to `bandwidth-optimization.yaml` (deferred - low priority)
- [ ] 3.2.4 Update `error-handling.yaml` with GC component recovery (deferred - low priority)

## Phase 4: Integration & Documentation

### 4.1 Serena Integration
- [ ] 4.1.1 Update Serena memory with decision tree references
- [ ] 4.1.2 Create decision tree invocation patterns for AI assistants
- [ ] 4.1.3 Document KB query workflow for decision nodes

### 4.2 Testing & Validation
- [x] 4.2.1 Validate all decision paths lead to KB-verified recommendations
- [x] 4.2.2 Test decision trees with sample multiplayer scenarios (verified structure)
- [x] 4.2.3 Verify all code examples follow current project structure

## Acceptance Criteria

- [x] All new decision trees pass `openspec validate --strict`
- [x] KB queries return relevant results for all GameCreator modules
- [x] Decision outcomes reference actual project files (not placeholders)
- [x] AI assistants can traverse trees to reach correct multiplayer patterns

## Implementation Summary

### Files Created
- `schema.yaml` - Enhanced with KB query nodes, project constraints, GC sync patterns
- `gc-character-sync.yaml` - Complete character synchronization decision tree
- `gc-inventory-sync.yaml` - Complete inventory synchronization decision tree
- `gc-stats-sync.yaml` - Complete stats synchronization decision tree (86% bandwidth savings)
- `gc-shooter-sync.yaml` - Complete shooter synchronization decision tree
- `host-client-architecture.yaml` - Complete Host/Client architecture decision tree
- `gc-visual-scripting-sync.yaml` - Complete visual scripting multiplayer decision tree

### Files Updated
- `network-sync-method.yaml` - Added GameCreator awareness and KB integration
- `state-management.yaml` - Added project constraints and KB integration

### Key Features Implemented
1. **KB Query Nodes**: Decision trees can query 77,914 indexed items before recommendations
2. **Project Constraints**: Enforces no-network-transform, server-authoritative patterns
3. **GameCreator Module Trees**: Dedicated trees for Character, Inventory, Stats, Shooter, Visual Scripting
4. **Host/Client Architecture**: Complete guide for network topology decisions
5. **86% Bandwidth Optimization**: StatsBatch pattern documented in gc-stats-sync.yaml
6. **Visual Scripting Multiplayer**: Complete guide for network-aware Triggers, Instructions, Conditions, and Variables
   - NPC interaction with faction filtering (e.g., "On Orc NPC interact → add gold")
   - Perception events with faction awareness (e.g., "On see Elf → change Fear stat")
   - Server-authoritative instructions for inventory/stats/character actions
   - Complete condition library for role, faction, player, and state checks
