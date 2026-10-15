# 3. Batch Reanalyze Implementation

Date: 2026-01-02

## Status

Proposed

## Context

We want batch reanalysis of all registered analysis sets. The current code structure:

```
aina (CLI entry)
  └── aina_lib/cli.py
        └── cmd_analyze()
              ├── Database lookup/registration
              ├── Staleness callback setup
              ├── analyze_repos() → returns analysis_json
              ├── Write JSON to ~/.aina/analysis/{name}.json
              ├── generate_analysis_index()
              └── Print summary
```

`analyze_repos()` in `analysis.py` already supports:
- `on_progress` callback for output control
- `on_staleness_warning` callback for interactive prompts

Key implementation questions:
1. Where does batch orchestration logic live?
2. How to share common logic between single and batch modes?
3. How to suppress output for `--quiet` mode?
4. How to collect results for the summary report?

## Decision

### 1. Batch orchestration stays in cli.py

The batch loop lives in `cmd_analyze()`, not in `analysis.py`.

**Rationale:**
- `cli.py` handles user-facing concerns (output formatting, prompts, flags)
- `analysis.py` handles single-analysis concerns (repo discovery, cloc, git stats)
- Batch orchestration is a CLI concern - how many times to run analysis
- Keeps `analysis.py` focused on "analyze one set" without batch complexity

### 2. Extract helper function in cli.py

Create `_run_single_analysis(name, path, interactive, quiet)` helper:

```python
def _run_single_analysis(name, path, interactive=True, quiet=False):
    """Run analysis for a single set. Returns (success, stats_or_error) tuple."""

    on_progress = None if quiet else print

    def on_staleness(infos, count):
        if not quiet:
            print(f">>> {count} repo(s) behind remote")
        if interactive:
            input(">>> Press Enter to continue...")

    try:
        analysis_json = analyze_repos(name, path,
            on_staleness_warning=on_staleness,
            on_progress=on_progress)

        # Write JSON
        output_path = Path.home() / '.aina' / 'analysis' / f'{name}.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(analysis_json, f, indent=2)

        return True, analysis_json['stats']
    except Exception as e:
        return False, str(e)
```

**Rationale:**
- Encapsulates the single-analysis workflow
- Returns structured result for aggregation
- Parameterizes interactive/quiet behavior
- `cmd_analyze()` calls this for single mode
- Batch loop calls this repeatedly

### 3. cmd_analyze handles both modes

```python
def cmd_analyze(name, path, db_path, all_sets=False, yes=False, quiet=False):
    if all_sets:
        return _analyze_all(db_path, yes, quiet)
    else:
        return _analyze_single(name, path, db_path, yes, quiet)
```

**Rationale:**
- Single entry point for analyze command
- Flag combinations handled in one place
- Avoids separate `cmd_reanalyze` function

### 4. Result collection for summary

Store results as list of dicts during batch:

```python
results = []
for analysis_set in sets:
    success, data = _run_single_analysis(...)
    results.append({
        'name': analysis_set['name'],
        'success': success,
        'stats': data if success else None,
        'error': data if not success else None
    })
```

Format as table at end of batch run.

### 5. Index generation timing

- **Single mode:** Call `generate_analysis_index()` immediately after analysis (current behavior)
- **Batch mode:** Call `generate_analysis_index()` once at end of batch

**Rationale:** `generate_analysis_index()` scans all `*.json` files in the analysis directory and rebuilds the index from scratch. Calling per-set during batch is redundant I/O.

### 6. Quiet mode implies non-interactive

When `--quiet` is specified, `--yes` behavior is automatic:
- No per-set output during analysis
- No staleness prompts
- Only final summary printed

**Rationale:** A prompt appearing during "quiet" operation contradicts user expectation. Explicit `--yes` without `--quiet` remains useful for full output without prompts.

## Consequences

**Positive:**
- Clean separation: cli.py handles orchestration, analysis.py handles single-set logic
- `analyze_repos()` unchanged - stable interface
- Result collection enables rich summary report
- `on_progress` callback naturally handles quiet mode

**Negative:**
- `cmd_analyze()` grows more complex with flag handling
- Need to validate mutual exclusion: `--all` with `name` argument is an error

**Neutral:**
- Helper function `_run_single_analysis` is internal to cli.py (underscore prefix)

## Implementation Checklist

1. Add `--all`, `--yes`, `--quiet` flags to argparse in `aina`
2. Extract `_run_single_analysis()` helper in cli.py
3. Modify `cmd_analyze()` to accept new flags and branch on `all_sets`
4. Implement `_analyze_all()` with loop, result collection, and summary
5. Update `__init__.py` exports (signature change for `cmd_analyze`)
6. Add tests for batch mode in test_commands.py