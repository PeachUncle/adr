# ADR-0024: Desktop Plugin Decoupling Architecture

**Date**: 2025-11-08  
**Status**: ACCEPTED  
**Context**: Desktop shell upgrade to mirror web version architecture  
**Deciders**: Architecture team  

---

## Problem

The desktop shell (RenderX.Shell.Avalonia) is being built as a thin host to mirror the web version's architecture. However, the current implementation has **hardcoded plugin controls** in MainWindow.axaml.cs:

```csharp
var canvasControl = new CanvasControl();           // HARDCODED
var controlPanelControl = new ControlPanelControl(); // HARDCODED
```

This creates **tight coupling** between the shell and plugins, violating the thin-host pattern:

1. **Adding a plugin** requires modifying shell code
2. **Changing a plugin** requires rebuilding the shell
3. **Plugins cannot be deployed independently**
4. **Violates parity with web version** which uses dynamic loading

---

## Decision

Implement **manifest-driven plugin decoupling** for the desktop shell, mirroring the web version's architecture:

### Web Version Pattern (Reference)
```typescript
// PanelSlot.tsx - Generic slot loader
const manifest = await getPluginManifest();
const entry = manifest.plugins.find(p => p.ui?.slot === slot);
const mod = await import(entry.ui.module);
const Exported = mod[entry.ui.export];
```

### Desktop Version Pattern (Required)
```csharp
// SlotContainer.cs - Generic slot loader
var manifest = await pluginLoader.LoadManifestAsync();
var plugin = manifest.plugins.FirstOrDefault(p => p.ui?.slot == SlotName);
var assembly = Assembly.Load(plugin.ui.assembly);
var type = assembly.GetType(plugin.ui.type);
var control = (Control)Activator.CreateInstance(type);
this.Child = control;
```

---

## Architecture

### Layer 1: Thin Host (Shell)
- **MainWindow.axaml** - 6 empty slots (no hardcoded controls)
- **MainWindow.axaml.cs** - Generic slot initialization (no plugin imports)

### Layer 2: Plugin Loader (Generic)
- **IPluginLoader** - Interface for plugin discovery and loading
- **PluginLoader** - Implementation using reflection
- **SlotContainer** - Generic Avalonia control that loads plugins

### Layer 3: Plugins (External)
- **RenderX.Plugins.Canvas.dll** - Canvas plugin
- **RenderX.Plugins.ControlPanel.dll** - Control panel plugin
- **RenderX.Plugins.Library.dll** - Library plugin
- **RenderX.Plugins.Header.dll** - Header plugins

### Layer 4: SDK Services (DI)
- **IEventRouter** - Event pub/sub
- **IConductorClient** - Sequence orchestration
- **ILogger** - Logging infrastructure

---

## Plugin Manifest

### plugin-manifest.json
```json
{
  "plugins": [
    {
      "id": "CanvasPlugin",
      "ui": {
        "slot": "canvas",
        "assembly": "RenderX.Plugins.Canvas",
        "type": "RenderX.Plugins.Canvas.CanvasControl"
      },
      "runtime": {
        "assembly": "RenderX.Plugins.Canvas",
        "type": "RenderX.Plugins.Canvas.CanvasPlugin",
        "method": "Register"
      }
    }
  ]
}
```

---

## Roslyn Analyzer Rules

### SHELL001: Thin-Host Architecture
- Shell must NOT import from `RenderX.Shell.Avalonia.Core.Conductor/**`
- Shell must NOT import from `RenderX.Shell.Avalonia.Core.Events/**`
- All SDK services must come from DI

### SHELL002: Plugin Decoupling
- MainWindow.axaml.cs must NOT import from `RenderX.Shell.Avalonia.UI.Views`
- MainWindow.axaml.cs must NOT directly instantiate plugin controls
- All plugins must be loaded via `IPluginLoader` and manifest

**Enforcement**: Build fails if rules are violated.

---

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Adding Plugin** | Modify shell + rebuild | Update manifest + deploy |
| **Changing Plugin** | Modify shell + rebuild | Deploy new plugin |
| **Plugin Isolation** | ❌ Tightly coupled | ✅ Fully decoupled |
| **Parity with Web** | ❌ Different pattern | ✅ Identical pattern |
| **Independent Deployment** | ❌ No | ✅ Yes |

---

## Implementation Steps

### Phase 1: Create Plugin Loader Infrastructure
- [ ] Create `IPluginLoader` interface
- [ ] Create `PluginLoader` implementation
- [ ] Create `SlotContainer` control
- [ ] Register in DI container

### Phase 2: Update plugin-manifest.json
- [ ] Add assembly mappings for all plugins
- [ ] Add type mappings for all plugin controls
- [ ] Add runtime handler mappings

### Phase 3: Refactor MainWindow
- [ ] Replace hardcoded controls with SlotContainers
- [ ] Update MainWindow.axaml.cs to use plugin loader
- [ ] Remove all plugin control imports

### Phase 4: Extract Plugins
- [ ] Move CanvasControl to RenderX.Plugins.Canvas.dll
- [ ] Move ControlPanelControl to RenderX.Plugins.ControlPanel.dll
- [ ] Move LibraryControl to RenderX.Plugins.Library.dll
- [ ] Move HeaderControls to RenderX.Plugins.Header.dll

### Phase 5: Verify Parity
- [ ] Desktop loads plugins dynamically
- [ ] Desktop has same UI layout as web
- [ ] Desktop has same event routing as web
- [ ] Desktop has same conductor execution as web

---

## Parity with Web Version

| Component | Web | Desktop |
|-----------|-----|---------|
| **Manifest** | plugin-manifest.json | plugin-manifest.json |
| **Slot Container** | PanelSlot.tsx | SlotContainer.cs |
| **Dynamic Loading** | `import()` | `Assembly.Load()` |
| **Type Resolution** | `mod[export]` | `assembly.GetType()` |
| **Instance Creation** | React component | `Activator.CreateInstance()` |
| **Plugin Isolation** | ✅ Full | ✅ Full |

---

## Consequences

### Positive
- ✅ Full parity with web version
- ✅ Plugins can be added/removed without shell rebuild
- ✅ Plugins can be deployed independently
- ✅ Clear separation of concerns
- ✅ Enforced by Roslyn analyzer at compile time

### Negative
- ⚠️ Requires plugin extraction (moving controls to separate assemblies)
- ⚠️ Requires IPluginLoader implementation
- ⚠️ Requires SlotContainer implementation

---

## References

- **DESKTOP_VS_WEB_ARCHITECTURE_PARITY.md** - Complete architecture comparison
- **DESKTOP_DECOUPLING_ARCHITECTURE.md** - Detailed implementation strategy
- **ARCHITECTURE_RULES_FOR_AGENTS.md** - Strict rules for future agents
- **ADR-0015** - Thin-host architecture constraints

---

## Approval

- [ ] Architecture team
- [ ] Development team
- [ ] QA team

---

**Status**: ACCEPTED  
**Implementation**: In progress  
**Enforcement**: Roslyn analyzer (SHELL002)

