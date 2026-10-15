# ADR-002: EPUB Pattern Analyzer Architecture

## Status
Proposed

## Context

The `synth_data_gen` library generates synthetic test data based on patterns documented in [`docs/epub_formatting_analysis_report.md`](../epub_formatting_analysis_report.md). However, users need:

1. **Pattern verification** - Check if a given EPUB uses patterns the library can generate
2. **Gap identification** - Discover patterns not yet supported
3. **Workflow for additions** - Add new patterns verified from real-world EPUBs
4. **Round-trip validation** - Verify generated EPUBs match their intended pattern specifications

The analysis report was created via LLM analysis of real EPUBs. We need tooling to:
- Programmatically detect these same patterns
- Compare detection results against the documented patterns
- Enable human-in-the-loop validation for new pattern discovery

## Decision

Implement an **EPUB Pattern Analyzer** with three components:

### 1. Pattern Registry

A structured catalog of all supported patterns with their detection signatures and constraints.

```python
# synth_data_gen/analyzer/registry.py
from dataclasses import dataclass
from typing import List, Dict, Optional, Set

@dataclass
class PatternDefinition:
    """Definition of a single detectable pattern."""
    id: str                           # e.g., "footnotes_same_page_taylor"
    category: str                     # e.g., "notes_system"
    description: str
    detection_signature: Dict         # CSS selectors, tag patterns, etc.
    source_examples: List[str]        # Real EPUBs where this was observed
    epub_versions: List[int]          # Compatible EPUB versions [2] or [2, 3] or [3]
    requires: Set[str]                # Pattern dependencies
    conflicts_with: Set[str]          # Mutually exclusive patterns
    generator_config: Dict            # Config to generate this pattern

@dataclass
class PatternConstraint:
    """Constraint relationship between patterns."""
    constraint_type: str              # "requires", "conflicts", "implies"
    source_pattern: str
    target_pattern: str
    reason: str

class PatternRegistry:
    """Registry of all supported patterns with constraint modeling."""

    def __init__(self):
        self.patterns: Dict[str, PatternDefinition] = {}
        self.constraints: List[PatternConstraint] = []
        self._load_patterns()

    def get_pattern(self, pattern_id: str) -> PatternDefinition:
        ...

    def get_patterns_by_category(self, category: str) -> List[PatternDefinition]:
        ...

    def validate_pattern_combination(self, pattern_ids: List[str]) -> List[str]:
        """Returns list of constraint violations for the given combination."""
        ...

    def get_compatible_patterns(self, pattern_id: str) -> Set[str]:
        """Returns patterns compatible with the given pattern."""
        ...
```

**Pattern Constraint Examples:**
```yaml
constraints:
  - type: "conflicts"
    source: "navdoc_*"
    target: "epub2_only"
    reason: "Navigation Documents require EPUB3"

  - type: "requires"
    source: "epub3_semantic_notes"
    target: "epub3_container"
    reason: "epub:type attributes require EPUB3 namespace"

  - type: "implies"
    source: "dual_footnote_system"
    target: "separate_notes_file"
    reason: "Editor notes typically in separate file"
```

### 2. EPUB Analyzer

Parses EPUBs and detects which patterns they use.

```python
# synth_data_gen/analyzer/epub_analyzer.py
from dataclasses import dataclass
from typing import List, Dict, Set
from pathlib import Path

@dataclass
class PatternMatch:
    """A detected pattern match in an EPUB."""
    pattern_id: str
    matched: bool
    evidence: List[str]               # Specific elements/files that matched
    location: str                     # Where in the EPUB

@dataclass
class AnalysisResult:
    """Complete analysis of an EPUB file."""
    epub_path: Path
    epub_version: int
    detected_patterns: List[PatternMatch]
    unknown_patterns: List[Dict]      # Patterns not in registry

    def get_coverage_report(self) -> Dict:
        """Returns {category: [matched_patterns]}"""
        ...

    def get_unrecognized_elements(self) -> List[Dict]:
        """Returns elements that didn't match any known pattern."""
        ...

class EpubAnalyzer:
    """Analyzes EPUB files to detect formatting patterns."""

    def __init__(self, registry: PatternRegistry):
        self.registry = registry

    def analyze(self, epub_path: Path) -> AnalysisResult:
        """Analyze an EPUB and return detected patterns."""
        ...

    def analyze_batch(self, epub_dir: Path) -> List[AnalysisResult]:
        """Analyze multiple EPUBs."""
        ...
```

### 3. Human-in-the-Loop Workflow

A CLI-driven workflow for discovering and validating new patterns.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Pattern Discovery Workflow                      │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Analyze EPUB
┌─────────────────────────────────────────────────────────────────────┐
│ $ synth-analyze discover new_book.epub                              │
│                                                                      │
│ Analyzing: new_book.epub                                             │
│ EPUB Version: 3                                                      │
│                                                                      │
│ Detected Known Patterns:                                             │
│   ✓ ncx_nested (ToC)                                                │
│   ✓ h1_h6_standard (Headers)                                        │
│   ✓ page_markers_calibre (Page Numbers)                             │
│                                                                      │
│ Unrecognized Elements Found:                                         │
│   ⚠ notes_system: Novel pattern detected                            │
│     - Reference: <sup data-note="fn1">†</sup>                        │
│     - Location: chapter_1.xhtml:42                                   │
│     - Similar to: footnotes_same_page (60% match)                   │
│                                                                      │
│ Writing candidates to: candidates.yaml                               │
└─────────────────────────────────────────────────────────────────────┘

Step 2: Human Review (candidates.yaml)
┌─────────────────────────────────────────────────────────────────────┐
│ # candidates.yaml - HUMAN REVIEW REQUIRED                            │
│                                                                      │
│ candidates:                                                          │
│   - id: "candidate_001"                                              │
│     category: "notes_system"                                         │
│     detected_signature:                                              │
│       reference_pattern: 'sup[data-note]'                           │
│       marker_style: "symbol"                                         │
│       note_location: "same_file"                                     │
│     evidence:                                                        │
│       - file: "chapter_1.xhtml"                                      │
│         line: 42                                                     │
│         element: '<sup data-note="fn1">†</sup>'                      │
│       - file: "chapter_2.xhtml"                                      │
│         line: 87                                                     │
│         element: '<sup data-note="fn2">*</sup>'                      │
│     similar_patterns:                                                │
│       - id: "footnotes_same_page"                                    │
│         difference: "uses data-note attr instead of href"           │
│                                                                      │
│     # === HUMAN INPUT BELOW ===                                      │
│     decision: "new_pattern"  # Options: new_pattern, variant, skip  │
│     pattern_name: "footnotes_data_attr"                              │
│     description: "Footnotes using data-note attribute (no link)"    │
│     constraints:                                                     │
│       requires: []                                                   │
│       conflicts_with: ["epub2_only"]  # data-* is HTML5             │
└─────────────────────────────────────────────────────────────────────┘

Step 3: Validate and Add
┌─────────────────────────────────────────────────────────────────────┐
│ $ synth-analyze add-patterns candidates.yaml                         │
│                                                                      │
│ Processing candidates.yaml...                                        │
│                                                                      │
│ candidate_001: footnotes_data_attr                                   │
│   ✓ Detection signature valid                                        │
│   ✓ No constraint conflicts                                          │
│   ✓ Added to registry                                                │
│                                                                      │
│ Generating round-trip validation...                                  │
│   Creating test EPUB with pattern: footnotes_data_attr               │
│   Re-analyzing generated EPUB...                                     │
│   ✓ Pattern detected in generated output                             │
│                                                                      │
│ Pattern successfully added!                                          │
│ Updated: synth_data_gen/analyzer/patterns/notes_system.yaml          │
└─────────────────────────────────────────────────────────────────────┘
```

### 4. Round-Trip Validation

Ensures the library can correctly generate and detect its own patterns.

```python
# synth_data_gen/analyzer/validation.py
def round_trip_validate(pattern_id: str, registry: PatternRegistry) -> bool:
    """
    1. Get generator config for pattern
    2. Generate an EPUB using that config
    3. Analyze the generated EPUB
    4. Verify the pattern is detected
    """
    pattern = registry.get_pattern(pattern_id)

    # Generate
    epub_path = generate_data(config_obj={
        "file_types": [{
            "type": "epub",
            "count": 1,
            **pattern.generator_config
        }]
    })[0]

    # Analyze
    analyzer = EpubAnalyzer(registry)
    result = analyzer.analyze(epub_path)

    # Verify
    detected_ids = [m.pattern_id for m in result.detected_patterns if m.matched]
    return pattern_id in detected_ids
```

## Implementation Plan

### Phase 1: Pattern Registry
1. Define `PatternDefinition` and `PatternConstraint` dataclasses
2. Extract patterns from existing `epub_components/` code
3. Create YAML-based pattern definitions with constraints
4. Implement constraint validation logic

### Phase 2: EPUB Analyzer
1. Implement EPUB parsing (reuse ebooklib)
2. Create pattern detection logic based on CSS selectors and tag patterns
3. Build `AnalysisResult` reporting

### Phase 3: CLI & Workflow
1. Create `synth-analyze` CLI command
2. Implement `discover` subcommand for unknown pattern detection
3. Implement `add-patterns` subcommand with round-trip validation
4. Create `candidates.yaml` format for human review

### Phase 4: Integration
1. Add round-trip tests to CI
2. Create coverage reports comparing detected vs documented patterns
3. Compare analyzer results against `epub_formatting_analysis_report.md`

## Directory Structure

```
synth_data_gen/
├── analyzer/                    # New module
│   ├── __init__.py
│   ├── registry.py             # PatternRegistry, PatternDefinition
│   ├── epub_analyzer.py        # EpubAnalyzer, AnalysisResult
│   ├── validation.py           # Round-trip validation
│   ├── cli.py                  # synth-analyze command
│   └── patterns/               # Pattern definitions (YAML)
│       ├── toc_styles.yaml
│       ├── notes_systems.yaml
│       ├── header_patterns.yaml
│       ├── page_markers.yaml
│       └── constraints.yaml
```

## Example Pattern Definition (YAML)

```yaml
# synth_data_gen/analyzer/patterns/notes_systems.yaml
patterns:
  footnotes_same_page_taylor:
    category: "notes_system"
    description: "Same-page footnotes with <p class='footnote'> (Taylor style)"
    source_examples:
      - "Charles Taylor - Hegel"
    epub_versions: [2, 3]
    detection_signature:
      reference:
        selector: "sup.calibre20 > a[id^='p'][id*='-fn']"
        pattern: "pX-fnY"
      note_text:
        selector: "p.footnote"
        location: "same_file"
        has_backlink: true
    requires: []
    conflicts_with: []
    generator_config:
      notes_config:
        type: "footnotes"
        location: "same_page"
        reference_style: "numeric"
        note_class: "footnote"

  dual_system_symbols:
    category: "notes_system"
    description: "Dual system: symbols (†) for author, numbers for editor"
    source_examples:
      - "Hegel - Philosophy of Right"
    epub_versions: [2, 3]
    detection_signature:
      author_notes:
        selector: "sup > a > em:contains('†'), sup > a > em:contains('*')"
        location: "same_file"
      editor_notes:
        selector: "sup > a[href*='part00']:not(:has(em))"
        location: "different_file"
    requires: []
    conflicts_with:
      - "single_note_system"
    generator_config:
      notes_config:
        type: "dual"
        author_marker_style: "symbol"
        editor_marker_style: "numeric"
        author_location: "same_page"
        editor_location: "endnotes_file"
```

## Consequences

### Positive
- **Verifiable patterns**: Every pattern can be tested via round-trip validation
- **Extensible**: New patterns follow documented workflow with human oversight
- **Constraint-aware**: Prevents invalid pattern combinations
- **Traceability**: Patterns link back to source EPUBs and analysis report
- **No false confidence**: Human review required for new patterns (not AI-driven scoring)

### Negative
- **Manual effort**: Human review required for each new pattern
- **Detection limits**: CSS selector-based detection may miss complex patterns
- **Maintenance**: Pattern definitions need updates as EPUB standards evolve

### Mitigations
- Batch multiple candidates for efficient human review
- Document detection limitations per pattern
- Use semantic matching where CSS selectors insufficient

## Related

- [`docs/epub_formatting_analysis_report.md`](../epub_formatting_analysis_report.md) - Source patterns from LLM analysis
- [ADR-001: Combinatoric Test Generation](ADR-001-combinatoric-test-generation.md) - Feature catalog this builds on
- [`synth_data_gen/generators/epub_components/`](../../synth_data_gen/generators/epub_components/) - Existing generation code to extract patterns from
