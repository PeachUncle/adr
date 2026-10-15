# ADR-002: Correlation ID Strategy

**Status:** Proposed
**Date:** 2025-12-30
**WorkId:** P-CFCORE-LOGGING-CONSOLIDATION
**Authors:** ContextForge QSE Agent
**Decision Context:** Unify three existing correlation ID patterns into a single strategy with clear precedence rules for CLI → Runtime → Plugin propagation per CF-133.

---

## Problem

Multiple correlation ID patterns exist across the codebase:

1. **ContextVar pattern** (`src/unified_logging/core.py`): Uses `contextvars.ContextVar` for thread/async-safe propagation
2. **RuntimeBuilder pattern** (`cf_core/logger_provider.py`): Explicit binding via `RuntimeBuilder.with_correlation_id()`
3. **Environment variable pattern** (`python/services/unified_logger.py`): Reads `CF_SESSION_ID`, `CF_TRACE_ID`

Without a unified strategy:
- Correlation ID may differ between components in the same session
- PowerShell → Python handoff loses correlation
- MCP servers generate new IDs instead of inheriting from CLI
- Debugging cross-component issues becomes difficult

---

## Forces & Constraints

- **Thread/async safety**: Must work in sync, threaded, and async contexts
- **Cross-language bridge**: PowerShell scripts must share correlation with Python
- **MCP server pattern**: Existing `RuntimeBuilder` API must remain functional
- **Immutability within session**: Once bound to a plugin, correlation ID should not change
- **Performance**: Resolution should be O(1), no database lookups
- **Fallback chain**: Must always produce a valid ID, even if no context available
- **CF-133 compliance**: Session correlation rules from ContextForge framework

---

## Decision

Implement a unified correlation ID strategy with the following precedence:

```
1. ContextVar override    (highest priority - explicit scoping)
2. Environment variable   (cross-language bridge)
3. Auto-generated UUID    (fallback guarantee)
```

### Resolution Algorithm

```python
from contextvars import ContextVar
import os
import uuid

_CORRELATION_VAR: ContextVar[str | None] = ContextVar("cf_correlation_id", default=None)

def get_correlation_id() -> str:
    """
    Resolve correlation ID with defined precedence.

    Resolution order:
    1. ContextVar (explicit scope via correlation_context())
    2. UNIFIED_LOG_CORRELATION environment variable
    3. CF_SESSION_ID environment variable (PowerShell bridge)
    4. CF_TRACE_ID environment variable (cross-language trace)
    5. Auto-generated UUID4 (always succeeds)
    """
    # 1. ContextVar takes highest priority
    if (ctx := _CORRELATION_VAR.get()) is not None:
        return ctx

    # 2. Explicit correlation override
    if (unified := os.environ.get("UNIFIED_LOG_CORRELATION")):
        return unified

    # 3. PowerShell session bridge
    if (session := os.environ.get("CF_SESSION_ID")):
        return session

    # 4. Cross-language trace
    if (trace := os.environ.get("CF_TRACE_ID")):
        return trace

    # 5. Fallback: generate new UUID
    return uuid.uuid4().hex
```

### Context Manager for Explicit Scoping

```python
from contextlib import contextmanager

@contextmanager
def correlation_context(correlation_id: str):
    """
    Establish correlation ID scope for nested operations.

    All logging within this context will use the provided correlation_id,
    regardless of environment variables.

    Usage:
        with correlation_context("user-request-123"):
            logger.info("processing")  # correlation_id="user-request-123"
            await async_operation()    # Same correlation_id inherited
    """
    token = _CORRELATION_VAR.set(correlation_id)
    try:
        yield
    finally:
        _CORRELATION_VAR.reset(token)
```

### RuntimeBuilder Integration (MCP Servers)

```python
class RuntimeBuilder:
    """Preserved API for MCP server compatibility."""

    def __init__(self):
        self._correlation_id: str | None = None

    def with_correlation_id(self, correlation_id: str) -> "RuntimeBuilder":
        """Bind correlation ID for this runtime instance."""
        self._correlation_id = correlation_id
        return self

    def build(self) -> "Runtime":
        """Create runtime with bound correlation."""
        return Runtime(
            correlation_id=self._correlation_id or get_correlation_id()
        )

class Runtime:
    """Runtime instance with immutable correlation binding."""

    def __init__(self, correlation_id: str):
        self._correlation_id = correlation_id

    def logger(self, plugin_id: str) -> structlog.BoundLogger:
        """Get logger for plugin with inherited correlation."""
        return get_logger(plugin_id).bind(
            correlation_id=self._correlation_id,
            plugin_id=plugin_id
        )
```

---

## Rationale

### Why ContextVar Has Highest Priority

ContextVar provides:
- **Thread isolation**: Each thread has independent value
- **Async inheritance**: Child tasks inherit parent's value automatically
- **Explicit scoping**: `correlation_context()` makes scope visible in code
- **No global mutation**: Unlike environment variables

Environment variables are fallback because:
- They're process-global (no isolation)
- Mutation affects all threads/tasks
- But they're the only cross-language bridge available

### Why Keep RuntimeBuilder Pattern

The RuntimeBuilder pattern is used by existing MCP servers:
- Provides explicit, immutable binding
- Plugin loggers can't accidentally change correlation
- Well-established API in production

Rather than deprecate, we integrate:
- RuntimeBuilder calls `get_correlation_id()` if no explicit ID
- Once bound, the Runtime's correlation is immutable
- Plugins get loggers with inherited correlation

### Why UUID as Final Fallback

Always generating a valid ID means:
- No null checks required in log processors
- Log events always correlatable (even if to "orphan" session)
- Easier debugging of misconfigured contexts

---

## Alternatives Considered

### Alternative 1: Environment Variable Only

**Approach:** Use only `CF_SESSION_ID` for all correlation.

**Rejected because:**
- No thread isolation in multithreaded code
- Async tasks would share same value inappropriately
- Can't scope correlation to specific code blocks

### Alternative 2: Database-Backed Session Registry

**Approach:** Store active sessions in database, lookup by session ID.

**Rejected because:**
- Adds I/O latency to every log call
- Requires database availability
- Over-engineered for the problem (Complex Solution Bias)

### Alternative 3: Thread-Local Storage

**Approach:** Use `threading.local()` instead of ContextVar.

**Rejected because:**
- Doesn't work with async/await
- ContextVar is the modern Python standard
- Async is heavily used in MCP servers

---

## Consequences

### Positive

- **Single resolution function**: All code calls `get_correlation_id()`
- **Cross-language support**: PowerShell sets env vars, Python respects them
- **Explicit scoping**: `correlation_context()` makes scope visible
- **MCP compatibility**: RuntimeBuilder continues working
- **No breaking changes**: All existing patterns still work

### Negative

- **Multiple sources of truth**: Correlation can come from 4+ places
- **Precedence learning curve**: Developers must understand resolution order
- **Testing complexity**: Must test all precedence combinations

### Neutral

- **Migration effort**: Existing code works unchanged but should migrate to new API
- **Documentation need**: Resolution order must be clearly documented

---

## Thread Pool Context Propagation

**Critical:** ContextVar does NOT automatically propagate to ThreadPoolExecutor workers. Explicit context copying is required.

**The Problem:**
```python
# INCORRECT ASSUMPTION - ContextVar lost in ThreadPoolExecutor
with correlation_context("user-123"):
    with ThreadPoolExecutor() as executor:
        executor.submit(some_function)  # ❌ some_function sees None
```

**Required Pattern:**
```python
import contextvars
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

def submit_with_context(
    executor: ThreadPoolExecutor,
    fn: Callable,
    *args: Any,
    **kwargs: Any
):
    """
    Submit callable to executor with current context copied.

    This ensures ContextVar values (including correlation_id) are
    inherited by worker threads.

    Example:
        with correlation_context("request-123"):
            with ThreadPoolExecutor(max_workers=4) as executor:
                future = submit_with_context(executor, process_item, item)
    """
    ctx = contextvars.copy_context()
    return executor.submit(ctx.run, fn, *args, **kwargs)
```

**Alternative - Pre-bind:**
```python
from functools import partial

def bind_correlation(fn: Callable) -> Callable:
    """Pre-bind current correlation to function for later execution."""
    correlation_id = get_correlation_id()

    def wrapper(*args, **kwargs):
        with correlation_context(correlation_id):
            return fn(*args, **kwargs)
    return wrapper

# Usage:
with ThreadPoolExecutor() as executor:
    bound_fn = bind_correlation(process_item)
    executor.submit(bound_fn, item)  # ✅ Correlation preserved
```

**Testing Requirement:**
Phase 1 implementation must include integration test validating ThreadPoolExecutor context inheritance using the `submit_with_context()` pattern.

---

## Subprocess Context Propagation

**Critical:** Neither ContextVar nor environment variables automatically propagate to subprocesses unless explicitly passed.

**Required Pattern:**
```python
import os
import subprocess
from pathlib import Path

def spawn_correlated_subprocess(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Spawn subprocess with correlation ID inherited via environment.

    The correlation_id is passed via UNIFIED_LOG_CORRELATION env var
    to ensure child process logs are correlated with parent.

    Example:
        spawn_correlated_subprocess(["python", "worker.py", "--task", "T-001"])
    """
    env = os.environ.copy()
    env["UNIFIED_LOG_CORRELATION"] = get_correlation_id()

    return subprocess.run(
        cmd,
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        **kwargs
    )
```

**Cross-Language Bridge:**
This pattern enables Python parent → Python subprocess correlation. For PowerShell → Python:
```powershell
# PowerShell side
$env:CF_SESSION_ID = "session-abc123"
python child_script.py

# Python child automatically picks up CF_SESSION_ID per precedence order
```

---

## Python Version Requirements

**Minimum:** Python 3.11+

**Rationale:**
- **asyncio.create_task context inheritance:** Python 3.11 changed behavior (PEP 567) to automatically copy ContextVar values to spawned tasks
- **Pre-3.11 behavior:** ContextVar values NOT inherited by create_task - requires manual context copying

**Compatibility Check:**
Phase 1 implementation must enforce Python 3.11+ in `pyproject.toml`:
```toml
[project]
requires-python = ">=3.11"
```

**Migration Note:**
Existing code running Python 3.10 must upgrade before adopting cf_core.logging. Document in migration guide.

---

## Implementation Steps

1. **Create `cf_core/logging/correlation.py`**
   - Implement `_CORRELATION_VAR` ContextVar
   - Implement `get_correlation_id()` with precedence
   - Implement `correlation_context()` context manager
   - Implement `set_correlation_id()` for rare direct mutation

2. **Update `cf_core/logging/core.py`**
   - Import and use `get_correlation_id()` in log processors
   - Ensure every log event includes `correlation_id` field

3. **Move `RuntimeBuilder`/`Runtime` to `cf_core/logging/runtime.py`**
   - Update to use new `get_correlation_id()` for default
   - Preserve immutable binding behavior

4. **Add integration tests**
   - Test all 4 precedence levels
   - Test async inheritance
   - Test thread isolation
   - Test RuntimeBuilder integration

5. **Update documentation**
   - Add precedence diagram to developer docs
   - Update PowerShell bridge documentation

---

## Acceptance Criteria

- [ ] `get_correlation_id()` returns correct ID per precedence
- [ ] `correlation_context()` scopes ID correctly across async boundaries
- [ ] ContextVar override takes priority over environment variables
- [ ] RuntimeBuilder pattern continues working for MCP servers
- [ ] All log events include `correlation_id` field
- [ ] Unit tests cover all precedence combinations
- [ ] Integration test validates PowerShell → Python flow

---

## Open Questions

1. **Should we emit warning when falling back to UUID?**
   - Pro: Helps identify misconfigured sessions
   - Con: Noisy in development environments
   - **Decision:** Defer, add config flag if needed

2. **Max correlation ID length?**
   - UUID4 hex is 32 chars
   - User-provided could be longer
   - **Decision:** Accept any string, document recommended max (64 chars)

---

## Related Documents

- PRD: `docs/prd/PRD-CFCORE-LOGGING.md`
- ADR-003: Evidence Bundle Compliance
- CF-133: Session correlation rules (ContextForge framework)
- Design Prompt: `docs/prompts/cf-core-centralized-logging-design.prompt.md`

---

**Version:** 1.0.0 (Proposed)
**Next Review:** After Phase 1 implementation
