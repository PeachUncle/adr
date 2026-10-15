# ADR-002: Adapter Architecture and Graph Naming Patterns

**Status:** Accepted
**Date:** 2025-10-31
**Author:** Ada "Bridgekeeper" (Architecture)
**Context:** Post-migration cleanup and architecture standardization

---

## Context

After completing the graph migration (consciousness-infrastructure_* → mind-protocol_*) and implementing the facade architecture pattern, we need to document the adapter layer patterns that have emerged. These patterns affect:

1. **Graph Name Resolution** - How we reference FalkorDB graphs
2. **WriteGate Enforcement** - Cross-layer write protection
3. **Adapter Layering** - Hexagonal architecture boundaries
4. **Service Configuration** - How services discover and connect to graphs

## Decision

We standardize on the following architectural patterns:

### 1. Centralized Graph Name Resolution

**Pattern:** All graph name generation goes through `orchestration/config/graph_names.py:GraphNameResolver`

**Rationale:**
- Single source of truth for naming conventions
- Easy to change naming schemes globally
- Type-safe graph name generation
- Clear separation between org base and citizen graphs

**Implementation:**
```python
from orchestration.config.graph_names import resolver

# ❌ BAD (hardcoded):
n2_graph = "mind-protocol"
graph_name = f"mind-protocol_{citizen}"

# ✅ GOOD (resolver):
n2_graph = resolver.org_base()  # → "mind-protocol"
graph_name = resolver.citizen("felix")  # → "mind-protocol_felix"
```

**Graph Naming Convention:**
- **L1 (Citizens):** `mind-protocol_{citizen_name}` via `resolver.citizen(name)`
- **L2 (Organization):** `mind-protocol` via `resolver.org_base()`
- **L3 (Ecosystem):** `ecosystem` (constant)
- **L4 (Protocol):** `protocol` (constant)

### 2. WriteGate Namespace Enforcement

**Pattern:** Graph write operations must declare their target namespace via `@write_gate` decorator

**Rationale:**
- Prevents accidental cross-layer writes (e.g., writing L1 data to L2 graph)
- Provides telemetry on write permission violations
- Enforces architectural boundaries at runtime

**Implementation:**
```python
from orchestration.libs.write_gate import write_gate, namespace_for_graph

# Static namespace:
@write_gate(f"L2:{resolver.org_base()}")
def upsert_org_node(..., ctx=None):
    # Requires ctx={"ns": "L2:mind-protocol"}
    ...

# Dynamic namespace via callable:
@write_gate(lambda self, scope, **_: self._namespace_for_scope(scope))
async def scoped_write(self, scope, ..., ctx=None):
    # Namespace computed at call time
    ...
```

**Namespace Format:** `L{level}:{graph_name}`
- `L1:mind-protocol_felix` (personal graph)
- `L2:mind-protocol` (organizational graph)
- `L3:ecosystem` (ecosystem graph)
- `L4:protocol` (protocol graph)

**Auto-mapping:** `namespace_for_graph(graph_name)` automatically determines level from graph name pattern

### 3. Hexagonal Adapter Layering

**Pattern:** Consciousness logic separated from infrastructure via ports/adapters

**Layers:**
1. **Domain** (`consciousness/engine/`) - Pure consciousness logic, no dependencies
2. **Ports** (`consciousness/ports/`) - Interfaces (EnginePort, ConfigPort, etc.)
3. **Adapters** (`orchestration/adapters/`) - Infrastructure implementations
   - `api/` - REST/WebSocket APIs
   - `storage/` - FalkorDB persistence
   - `ws/` - WebSocket broadcasting
4. **Services** (`orchestration/services/`) - Cross-cutting concerns (economy, health, etc.)

**Dependency Flow:**
```
Domain ← Ports ← Adapters → Infrastructure
  ↓
  Pure functions, testable in isolation
```

**Implementation:**
```python
# Domain (pure logic):
class EnergyDynamics:
    @staticmethod
    def compute_diffusion(graph: Graph, ...) -> Dict[str, float]:
        # Pure function, no I/O
        ...

# Port (interface):
class EnginePort(ABC):
    @abstractmethod
    async def inject_stimulus(self, text: str) -> None: ...

# Adapter (infrastructure):
class ConsciousnessEngineAdapter(EnginePort):
    def __init__(self, graph_store: FalkorDBGraphStore):
        self.engine = ConsciousnessEngineV2(...)

    async def inject_stimulus(self, text: str) -> None:
        await self.engine.inject_stimulus(text)
```

### 4. Service Configuration Pattern

**Pattern:** Services use `EconomySettings` / `CoreSettings` dataclasses with environment variable fallbacks

**Rationale:**
- Testable configuration (inject settings in tests)
- Environment variable override support
- Type-safe configuration with validation
- Centralized defaults

**Implementation:**
```python
from orchestration.core.settings import settings

# Access centralized settings:
graph_name = settings.N2_GRAPH_NAME  # Uses resolver internally
redis_url = settings.REDIS_URL

# Service-specific settings:
from orchestration.services.economy.settings import EconomySettings

economy_settings = EconomySettings(
    org_id=os.getenv("ECONOMY_ORG_ID", resolver.org_base()),
    l2_graph=os.getenv("ECONOMY_L2_GRAPH", resolver.org_base())
)
```

---

## Consequences

### Positive

1. **Maintainability:** Single source of truth for graph naming - change once, apply everywhere
2. **Safety:** WriteGate prevents cross-layer write bugs at runtime
3. **Testability:** Hexagonal architecture enables isolated domain testing
4. **Clarity:** Clear boundaries between domain logic and infrastructure
5. **Flexibility:** Easy to swap infrastructure (e.g., different graph DB) without touching domain

### Negative

1. **Indirection:** Must import `resolver` in every file that needs graph names (vs direct strings)
2. **Learning Curve:** Developers must understand port/adapter pattern
3. **Decorator Overhead:** WriteGate adds runtime check cost (mitigated by decorator caching)

### Migration Effort

**Completed (2025-10-31):**
- ✅ 9 orchestration files migrated to use resolver
- ✅ WriteGate namespace logic updated for new naming convention
- ✅ Graph migration completed (consciousness-infrastructure_* → mind-protocol_*)

**Remaining:**
- 23 hardcoded references (documentation/comments only, non-functional)

---

## Related Decisions

- **ADR-001:** Migrate to Full Facade Architecture (in progress)
- **Graph Migration:** Simplified naming convention (completed 2025-10-31)
- **L4 Protocol Migration:** L4_ prefixing for protocol-level schemas (completed 2025-10-31)

---

## References

**Implementation Files:**
- `orchestration/config/graph_names.py` - Resolver implementation
- `orchestration/libs/write_gate.py` - WriteGate decorator + namespace mapping
- `orchestration/core/settings.py` - Core settings with resolver integration
- `orchestration/adapters/ws/websocket_server.py` - Adapter layer example

**Documentation:**
- `citizens/SYNC.md` - Migration history and status
- `docs/MIGRATION_PLAN_FACADE_FULL.md` - Facade migration plan

---

## Implementation Checklist

For new services/scripts:
- [ ] Use `resolver.citizen(name)` / `resolver.org_base()` instead of hardcoded strings
- [ ] Add `@write_gate()` to any function that modifies graph data
- [ ] Pass `ctx={"ns": namespace_for_graph(graph_name)}` to all write operations
- [ ] Use `settings.N2_GRAPH_NAME` instead of hardcoded "mind-protocol"
- [ ] Import from `orchestration/config/graph_names import resolver` at module level
- [ ] For multi-scope services, implement `_namespace_for_scope(scope)` helper

---

**Acceptance Criteria:**
- ✅ All new code uses resolver pattern
- ✅ All write operations protected by WriteGate
- ✅ No hardcoded graph names in functional code (comments/docs OK)
- ✅ Namespace violations logged as telemetry events

**Approved by:** Ada "Bridgekeeper", Nicolas Reynolds
**Date:** 2025-10-31
