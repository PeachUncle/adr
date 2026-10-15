## Context

Phase I.2 introduces the Logic Stream, which extracts (Code → DOT) training pairs from real-world Finite State Machine (FSM) libraries. This is architecturally distinct from the Documentation Stream (Phase I.1), which scraped static HTML examples.

**Key Challenges:**
1. **Execution Safety**: Running arbitrary Python code from third-party repositories requires sandboxing to prevent malicious code execution, network access, or filesystem damage.
2. **Library Diversity**: Different FSM libraries use different APIs (`.to_dot()`, `.graph()`, `.visualize()`), parameter signatures, and internal representations.
3. **Static Analysis Complexity**: Detecting FSM patterns requires parsing Abstract Syntax Trees (ASTs) and handling various coding patterns (class-based, configuration-based, decorator-based).
4. **License Compliance**: Must track and verify licensing for every source repository to ensure dataset legal safety.

**Stakeholders:**
- Dataset consumers: Researchers fine-tuning models on CODE_TO_DOT task
- Model training pipeline: Depends on schema consistency across data streams
- Security reviewers: Concerned with arbitrary code execution risks

## Goals / Non-Goals

### Goals
- Extract 100-500 high-quality (Code → DOT) training pairs from FSM libraries
- Support `python-statemachine` and `transitions` libraries initially
- Ensure >90% DOT compilation success rate
- Maintain strict JSONL schema compatibility with Documentation Stream
- Provide both CLI and optional TUI interfaces matching existing scraper UX
- Track license metadata for all extracted examples

### Non-Goals
- **Not** building a general-purpose Python code analyzer (focused only on FSM patterns)
- **Not** supporting all FSM libraries (start with 2 most popular Python libraries)
- **Not** handling dynamic state generation requiring complex runtime contexts
- **Not** analyzing Ruby/JavaScript FSM libraries in initial release (future work)
- **Not** creating a new sandboxing framework (use existing tools: subprocess isolation, Docker, or RestrictedPython)

## Decisions

### Decision 1: Static Analysis Tool
**Choice:** Use Python's built-in `ast` module (not tree-sitter or astroid)

**Rationale:**
- Zero additional dependencies
- Sufficient for detecting class inheritance and decorator patterns
- Fast and well-documented
- Already in stdlib, no version compatibility issues

**Alternatives Considered:**
- `astroid`: More powerful but heavyweight dependency
- `tree-sitter-python`: Requires compilation, overkill for this use case
- `inspect` module: Requires importing code (security risk)

### Decision 2: Execution Sandbox
**Choice:** Subprocess isolation with timeout + resource limits (no Docker initially)

**Rationale:**
- Lighter weight than Docker for simple cases
- Can enforce timeout and memory limits via subprocess
- Easier to integrate in CI/CD and local development
- Future: Add optional Docker mode for paranoid security

**Implementation:**
```python
subprocess.run(
    [sys.executable, "-c", fsm_code],
    timeout=30,
    capture_output=True,
    env={"PYTHONPATH": "..."}  # isolated env
)
```

**Alternatives Considered:**
- Docker containers: More secure but adds operational complexity
- RestrictedPython: Incomplete protection, can be bypassed
- Virtual machines: Overkill for this use case

**Risks:**
- Subprocess isolation is not foolproof (can still access local filesystem)
- Mitigation: Run in disposable temporary directory, monitor for suspicious activity

### Decision 3: Library Support Priority
**Choice:** Python-first, Ruby later

**Target Libraries (Priority Order):**
1. `python-statemachine` (most popular, clean API)
2. `transitions` (widely used, good DOT export)
3. `aasm` (Ruby, future work if time permits)

**Rationale:**
- Python ecosystem has better tooling for static analysis
- Target audience is Python-focused ML community
- Can expand to other languages after proving concept

### Decision 4: DOT Export Method Discovery
**Choice:** Use heuristic method detection (try common names in order)

**Method Resolution Order:**
1. `.to_dot()`
2. `.graph()`
3. `.visualize(return_string=True)`
4. Check library documentation for custom methods

**Rationale:**
- Different libraries use different method names
- Better than hard-coding per library (more extensible)
- Fallback to manual configuration file for edge cases

### Decision 5: License Compliance Strategy
**Choice:** Allowlist OSI-approved licenses only, skip uncertain cases

**Allowed Licenses:**
- MIT, Apache-2.0, BSD-3-Clause, BSD-2-Clause
- ISC, MPL-2.0
- GPL-3.0, LGPL-3.0 (with proper attribution)

**Forbidden/Skip:**
- AGPL (copyleft concerns)
- Proprietary/unlicensed
- Unclear licenses

**Implementation:**
- Use `licensee` Python package or manual LICENSE file parsing
- Log skipped repositories for manual review

### Decision 6: Context Extraction Strategy
**Choice:** Capture complete class definition or configuration block (max 2000 chars)

**What to Include:**
- Class definition with docstrings (for class-based FSMs)
- Configuration dictionary/builder (for config-based FSMs)
- Import statements if relevant to understanding

**What to Exclude:**
- Test code, helper methods unrelated to FSM
- Large bodies of business logic
- Comments explaining usage (keep only structural docstrings)

**Rationale:**
- Model needs enough context to understand state structure
- But too much context dilutes the signal
- 2000 chars ≈ 50-70 lines of code (reasonable context window)

## Risks / Trade-offs

### Risk 1: Arbitrary Code Execution
**Severity:** HIGH  
**Mitigation:**
- Subprocess isolation with timeout
- Run in temporary directory with cleanup
- Monitor resource usage (CPU, memory)
- Consider Docker isolation for production runs
- Manual review of initial repository list

### Risk 2: Low Yield from Repositories
**Severity:** MEDIUM  
**Impact:** May extract fewer examples than expected (target: 100-500)  
**Mitigation:**
- Curate high-quality repository list (manual vetting)
- Focus on repos with examples/, tests/, docs/ directories
- Supplement with synthetic generation if needed
- Accept that quality > quantity

### Risk 3: Library API Changes
**Severity:** LOW  
**Impact:** `.to_dot()` methods may change signatures over time  
**Mitigation:**
- Pin library versions in test fixtures
- Document supported version ranges
- Design extractor to handle multiple method signatures

### Risk 4: Performance on Large Codebases
**Severity:** MEDIUM  
**Impact:** Processing large repos (>10k files) may be slow  
**Mitigation:**
- Pre-filter by file extension and imports before AST parsing
- Parallel processing with multiprocessing pool (4-8 workers)
- Cache successful extractions by file hash
- Early exit on non-FSM files

## Migration Plan

**N/A** - This is a new capability, no existing data to migrate.

**Integration Steps:**
1. Develop and test FSM parser independently
2. Validate output against JSONL schema
3. Run on curated repository list
4. Merge `logic-stream.jsonl` with existing `documentation-stream.jsonl` for unified dataset
5. Run deduplication pass to remove any cross-stream duplicates

**Rollback:**
- No impact on existing Documentation Stream
- Can simply exclude Logic Stream data if quality is insufficient

## Open Questions

1. **Should we extract FSM code that doesn't have `.to_dot()` but could be manually converted?**
   - Initial answer: No, stick to libraries with native DOT export
   - Future: Could use teacher LLM to generate DOT from FSM code

2. **How to handle FSMs that require database connections or external services to instantiate?**
   - Initial answer: Skip them, log as "requires_dependencies"
   - Future: Mock common dependencies (SQLAlchemy, Django ORM)

3. **Should we include test code that instantiates FSMs?**
   - Initial answer: Yes, test code often has simpler, cleaner FSM examples
   - Tag with `source: test` for potential filtering later

4. **How to attribute original authors in dataset?**
   - Include repository URL in `source` field
   - Add optional `attribution` field with repository owner and license
   - Generate LICENSES.txt manifest for dataset repository

5. **Should we support FSM libraries in other languages (Ruby, JavaScript)?**
   - Initial answer: Python only for Phase I.2
   - Ruby/JS: Evaluate based on Phase I.2 success and dataset size needs
