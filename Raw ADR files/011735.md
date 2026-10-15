# Design: Refactor Unity Editor Tools

## Context

The MLCreator project has accumulated 22 custom Unity Editor scripts over development. These scripts provide various tooling for multiplayer setup, documentation management, build optimization, and project utilities. However, organic growth has led to:

- Inconsistent code patterns and naming
- Duplicate functionality across scripts
- Some scripts that are no longer used
- Missing documentation and error handling

### Stakeholders
- **Developers**: Need reliable, discoverable editor tools
- **AI Assistants**: Need clear code structure for assistance
- **Build Pipeline**: Needs optimized compile times

## Goals / Non-Goals

### Goals
1. **Reduce script count** by consolidating related functionality
2. **Improve code quality** with consistent patterns
3. **Enhance discoverability** through organized menu structure
4. **Remove dead weight** by deleting unused scripts
5. **Document everything** with XML documentation

### Non-Goals
- Creating new editor tools (out of scope)
- Changing tool functionality (maintain compatibility)
- Refactoring third-party editor scripts in Plugins/
- Modifying runtime code

## Decisions

### Decision 1: Directory Structure

**What**: Organize editor scripts into functional subdirectories

**Structure**:
```
Assets/Editor/
├── _archive/                    # Deprecated scripts (not compiled)
├── Build/                       # Build and optimization tools
│   ├── BuildPipeline.cs        # Consolidated build tools
│   └── AssetOptimizer.cs       # Asset optimization
├── Documentation/               # Foam and doc management
│   └── FoamBatchTagger.cs      # Documentation tagging
├── Multiplayer/                 # Network and multiplayer setup
│   ├── MultiplayerSceneSetup.cs # Consolidated scene setup
│   └── BatchNetworkSceneProcessor.cs
├── Tools/                       # Specialized tools
│   ├── IconGenerator/          # Icon generation suite
│   └── Buildings_Creator/      # Building creation tools
├── Utilities/                   # General utilities
│   ├── HotReloadHandler.cs     # VS Code integration
│   ├── PerformanceSettings.cs  # Runtime settings
│   └── TriggerAnalyzerAndRenamer.cs
├── CodeAssistant/              # Code management tools
│   ├── NamespaceReferenceManager.cs
│   └── SchemaAutoUpdater.cs
├── BatchProcessing/            # Overnight/batch tasks
│   └── OvernightTaskProcessor.cs
└── EditorMenuPaths.cs          # Central menu path management
```

**Why**: Logical grouping improves navigation and understanding.

**Alternatives considered**:
- Flat structure: Rejected (poor organization at scale)
- Feature-based grouping: Rejected (tools are cross-feature)

### Decision 2: Namespace Convention

**What**: Use hierarchical namespaces matching directory structure

**Pattern**: `MLCreator.Editor.{Category}`

**Examples**:
- `MLCreator.Editor` - Root namespace for general utilities
- `MLCreator.Editor.Multiplayer` - Multiplayer tools
- `MLCreator.Editor.Build` - Build pipeline tools
- `MLCreator.Editor.Documentation` - Documentation tools

**Why**: Clear namespace hierarchy aids code navigation and prevents conflicts.

### Decision 3: Menu Path Centralization

**What**: All menu items defined in `EditorMenuPaths.cs`

**Why**:
- Single source of truth for menu structure
- Easy to reorganize without touching individual scripts
- Consistent priority and ordering
- Prevents duplicate/conflicting menu items

**Implementation**:
```csharp
// In EditorMenuPaths.cs
public const string MULTIPLAYER_SETUP = ROOT + "Multiplayer/Scene Setup/";

// In individual scripts
[MenuItem(EditorMenuPaths.MULTIPLAYER_SETUP + "Configure Scene")]
```

### Decision 4: Consolidation Strategy

**What**: Merge scripts with overlapping functionality

**Targets**:
1. `SceneSpawnSetup.cs` + `SetupMultiplayerForScene.cs` → `MultiplayerSceneSetup.cs`
2. `BuildOptimizationConfigurator.cs` + `BuildSizeOptimizer.cs` → Keep separate but coordinate

**Why**: Reduces code duplication and user confusion.

**Risk**: Breaking existing workflows
**Mitigation**: Maintain backward-compatible menu items

### Decision 5: Deprecation Process

**What**: Three-stage deprecation for removed scripts

**Stages**:
1. **Mark**: Add `[Obsolete("message")]` attribute
2. **Archive**: Move to `_archive/` folder (excluded from compilation)
3. **Delete**: Remove after one release cycle

**Why**: Graceful transition prevents workflow disruption.

## Risks / Trade-offs

### Risk 1: Breaking Menu Shortcuts
- **Risk**: Users may have memorized menu paths
- **Likelihood**: Medium
- **Impact**: Low (minor inconvenience)
- **Mitigation**: Add redirect menu items pointing to new locations

### Risk 2: Script Dependencies
- **Risk**: Consolidation may break inter-script references
- **Likelihood**: Low (most scripts are independent)
- **Impact**: Medium (compile errors)
- **Mitigation**: Thorough dependency analysis before changes

### Risk 3: Hidden Functionality Loss
- **Risk**: Removing scripts may delete used functionality
- **Likelihood**: Low (usage analysis performed)
- **Impact**: High (broken workflows)
- **Mitigation**: Archive rather than delete, comprehensive testing

## Migration Plan

### Phase 1: Audit (Non-destructive)
1. Analyze all scripts
2. Document dependencies
3. Create classification report
4. **Rollback**: N/A (no changes made)

### Phase 2: Consolidation
1. Create new consolidated scripts
2. Copy functionality from source scripts
3. Test consolidated scripts
4. Update menu paths
5. **Rollback**: Delete new scripts, restore originals

### Phase 3: Cleanup
1. Move deprecated scripts to `_archive/`
2. Delete truly dead scripts
3. Update documentation
4. **Rollback**: Restore from git history

### Phase 4: Validation
1. Full compile test
2. Menu verification
3. Functional testing
4. **Rollback**: Git revert if issues found

## Open Questions

1. **FoamBatchTagger complexity**: At 1400+ lines, should this be split into multiple files?
   - Recommendation: Assess during audit phase

2. **HotReloadHandler location**: Should this be in a separate package for reuse?
   - Recommendation: Keep in project for now, consider extraction later

3. **IconGenerator suite**: Should the 4 files be consolidated?
   - Recommendation: Keep separate (clear separation of concerns)

4. **Test coverage**: Should we add automated tests for editor tools?
   - Recommendation: Out of scope for this refactor, but document as future work
