# ADR-0011: Integrate Environment Metadata with pytest-metadata

**Status**: Accepted
**Date**: 2025-10-24
**Decision Makers**: Georges Martin
**Related**: ADR-0003 (technology stack)

## Context

pytest-jux currently manages metadata in two separate systems:

### Current Metadata Architecture (v0.2.1)

**1. pytest-metadata (External Dependency)**:
- Installed as a required dependency (`pytest-metadata>=3.0`)
- Captures user-provided metadata via CLI (`--metadata key value`)
- Writes metadata to JUnit XML `<properties>` elements
- **Included in XMLDSig signature** (cryptographically bound)

**2. pytest_jux.metadata Module (Internal)**:
- `EnvironmentMetadata` dataclass captures:
  - hostname, username, platform
  - Python/pytest/pytest-jux versions
  - timestamp (ISO 8601, UTC)
  - Optional environment variables
- Stored as **separate JSON sidecar file** (`metadata/{hash}.json`)
- **NOT included in XMLDSig signature** (not cryptographically bound)

### The Problems

#### 1. Metadata Not Cryptographically Bound

```
reports/sha256_abc123.xml       # Signed with XMLDSig
metadata/sha256_abc123.json     # NOT signed, can be tampered with
```

**Security Issue**: Environment metadata (hostname, username, timestamp) can be modified without invalidating the signature, compromising provenance tracking.

#### 2. Two Storage Mechanisms

```xml
<!-- In signed XML (pytest-metadata) -->
<testsuites>
  <properties>
    <property name="ci_provider" value="GitLab CI"/>
    <property name="pipeline_id" value="12345"/>
  </properties>
  <ds:Signature>...</ds:Signature>
</testsuites>
```

```json
// In separate JSON (pytest_jux.metadata)
{
  "hostname": "ci-runner-01",
  "username": "gitlab-runner",
  "timestamp": "2025-10-24T12:34:56+00:00"
}
```

**Problem**: Duplicate storage mechanisms, files can become separated, provenance incomplete.

#### 3. Inconsistent Trust Model

- User metadata (via `--metadata`): ✅ Signed, trusted
- Environment metadata (via `pytest_jux.metadata`): ❌ Not signed, untrusted

**Problem**: System-captured metadata is LESS trusted than user-provided metadata, which is backwards.

#### 4. Documentation Confusion

Documentation (e.g., `docs/howto/add-metadata-to-reports.md`) explains that pytest-metadata is used but doesn't clarify why pytest-jux has its own metadata module.

### Why Two Systems Exist

Looking at the project history:
1. **Sprint 1-2**: Core signing functionality developed
2. **Sprint 3**: Configuration and storage added
3. `pytest_jux.metadata` created for environment capture
4. `pytest-metadata` added as dependency for user metadata
5. **Never integrated** - both systems coexist independently

## Decision

**Integrate pytest-jux environment metadata into pytest-metadata and remove JSON sidecar storage entirely.**

### What Changes

**1. Add `pytest_metadata` Hook to `plugin.py`**:

```python
def pytest_metadata(metadata: dict) -> None:
    """Add pytest-jux environment metadata to pytest-metadata.

    Captures environment metadata and injects it into pytest-metadata's
    dictionary. Uses "jux:" namespace prefix to avoid conflicts.
    User-provided metadata (CLI) takes precedence.
    """
    from pytest_jux.metadata import capture_metadata

    jux_meta = capture_metadata()

    # Add with "jux:" prefix if not already present
    if 'jux:hostname' not in metadata:
        metadata['jux:hostname'] = jux_meta.hostname
    if 'jux:username' not in metadata:
        metadata['jux:username'] = jux_meta.username
    if 'jux:platform' not in metadata:
        metadata['jux:platform'] = jux_meta.platform
    if 'jux:python_version' not in metadata:
        metadata['jux:python_version'] = jux_meta.python_version
    if 'jux:pytest_version' not in metadata:
        metadata['jux:pytest_version'] = jux_meta.pytest_version
    if 'jux:pytest_jux_version' not in metadata:
        metadata['jux:pytest_jux_version'] = jux_meta.pytest_jux_version
    if 'jux:timestamp' not in metadata:
        metadata['jux:timestamp'] = jux_meta.timestamp
```

**2. Remove JSON Sidecar Storage**:

From `storage.py`:
- Remove `store_report()` metadata parameter
- Remove `get_metadata()` method
- Remove `metadata/` directory handling
- Keep only XML report storage

**3. Simplify `pytest_sessionfinish` Hook**:

```python
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    # Load XML
    tree = load_xml(xml_path)

    # Sign if enabled (includes metadata properties)
    if jux_sign:
        tree = sign_xml(tree, key, cert)

    # Store XML only (metadata already embedded)
    if should_store_locally:
        storage.store_report(xml_content=xml_bytes, canonical_hash=canonical_hash)
```

**4. Keep `pytest_jux.metadata` Module**:

Purpose changes:
- ✅ Still captures environment metadata
- ✅ Still used by `pytest_metadata` hook
- ❌ No longer writes JSON files
- ✅ Can still be imported by users for custom use

### Result in JUnit XML

```xml
<testsuites>
  <properties>
    <!-- User-provided metadata (--metadata CLI) -->
    <property name="ci_provider" value="GitLab CI"/>
    <property name="pipeline_id" value="12345"/>

    <!-- Auto-injected by pytest-jux -->
    <property name="jux:hostname" value="ci-runner-01"/>
    <property name="jux:username" value="gitlab-runner"/>
    <property name="jux:platform" value="Linux-5.15.0"/>
    <property name="jux:python_version" value="3.11.4"/>
    <property name="jux:pytest_version" value="8.4.2"/>
    <property name="jux:pytest_jux_version" value="0.2.1"/>
    <property name="jux:timestamp" value="2025-10-24T12:34:56+00:00"/>
  </properties>
  <!-- test cases -->
  <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
    <!-- Signature covers ALL properties including jux:* metadata -->
  </ds:Signature>
</testsuites>
```

## Alternatives Considered

### 1. Keep Both Systems (Status Quo)

**Pros**:
- No changes required
- Existing code works

**Cons**:
- ❌ Metadata not cryptographically bound
- ❌ Duplicate storage mechanisms
- ❌ Files can become separated
- ❌ Confusing architecture

**Decision**: Rejected - security and architectural issues

### 2. Sign JSON Sidecar Files Separately

Create separate XMLDSig signatures for JSON files.

**Pros**:
- Metadata becomes signed
- Minimal code changes

**Cons**:
- ❌ Two separate signatures to verify
- ❌ More complex verification workflow
- ❌ Still have file separation risk
- ❌ JSON XMLDSig is non-standard

**Decision**: Rejected - increases complexity

### 3. Embed Metadata in XML as Custom Elements

```xml
<testsuites>
  <jux:metadata xmlns:jux="https://jux.dev/schema">
    <jux:hostname>ci-runner-01</jux:hostname>
    <jux:timestamp>2025-10-24T12:34:56+00:00</jux:timestamp>
  </jux:metadata>
  <ds:Signature>...</ds:Signature>
</testsuites>
```

**Pros**:
- Metadata signed
- Clear separation from test properties
- Custom namespace

**Cons**:
- ❌ Non-standard JUnit XML extension
- ❌ May break JUnit XML parsers
- ❌ Duplicate functionality of `<properties>`

**Decision**: Rejected - breaks standard

### 4. Integrate with pytest-metadata (Chosen)

**Pros**:
- ✅ Metadata cryptographically bound (in signature)
- ✅ Standard JUnit XML `<properties>` schema
- ✅ Single source of truth (XML file)
- ✅ No file separation risk
- ✅ Simpler storage (XML only)
- ✅ Compatible with JUnit XML parsers

**Cons**:
- Breaking change (removes JSON sidecar feature)
- Need to update documentation
- Need to update tests

**Decision**: Accepted - best security and architecture

## Consequences

### Positive

1. **Cryptographic Provenance**: ALL metadata (user + environment) cryptographically bound
2. **Simplified Storage**: One file per report (`reports/{hash}.xml`) instead of two
3. **Reduced Complexity**: Single metadata system, not two
4. **Better Trust Model**: System metadata as trusted as user metadata
5. **Standard Compliance**: Uses JUnit XML `<properties>` as intended
6. **Smaller Codebase**: Less code in `storage.py`

### Negative

1. **Breaking Change**: JSON sidecar files no longer created
2. **Migration Required**: Existing JSON files need migration
3. **Documentation Updates**: All docs referencing JSON sidecars need updates

### Neutral

1. **pytest_jux.metadata Module Remains**: Still useful for capture logic
2. **Storage Directory Structure**: Still uses `reports/` directory

## Migration Impact

### For Existing Users (v0.2.1 → v0.3.0)

**Breaking Change**: JSON sidecar files no longer created.

**Before (v0.2.1)**:
```
~/.local/share/jux/
├── reports/sha256_abc123.xml
└── metadata/sha256_abc123.json  # ← No longer created
```

**After (v0.3.0)**:
```
~/.local/share/jux/
└── reports/sha256_abc123.xml  # Contains metadata in <properties>
```

**Migration Script** (provided in Sprint 7):

```bash
#!/bin/bash
# migrate-metadata.sh - Migrate JSON sidecar files

for json_file in ~/.local/share/jux/metadata/*.json; do
  hash=$(basename "$json_file" .json)
  xml_file="~/.local/share/jux/reports/${hash}.xml"

  if [[ -f "$xml_file" ]]; then
    echo "Migrated metadata for $hash (already in XML)"
    # JSON file can be deleted
  else
    echo "WARNING: Orphaned metadata file: $json_file"
  fi
done
```

### For jux-cache Command

**Before**:
```bash
$ jux-cache list
Report: sha256_abc123
  Hostname: ci-runner-01  # From JSON sidecar
  Timestamp: 2025-10-24T12:34:56+00:00
```

**After**:
```bash
$ jux-cache list
Report: sha256_abc123
  jux:hostname: ci-runner-01  # From XML properties
  jux:timestamp: 2025-10-24T12:34:56+00:00
```

**Implementation**: Update `jux-cache` to read metadata from XML `<properties>` instead of JSON.

### For jux-inspect Command

Already reads from XML - no changes needed.

## Documentation Updates

### Files to Update

1. **docs/adr/README.md**: Add ADR-0011
2. **docs/howto/add-metadata-to-reports.md**: Remove JSON sidecar references
3. **docs/reference/storage.md**: Update storage structure
4. **CLAUDE.md**: Update metadata architecture section
5. **README.md**: Update quick start if needed

### Key Documentation Changes

**Before**:
> "Metadata is stored in two places: XML properties (user metadata) and JSON sidecars (environment metadata)"

**After**:
> "All metadata is stored in JUnit XML `<properties>` elements and cryptographically signed with XMLDSig"

## Implementation Checklist

- [ ] Add `pytest_metadata()` hook to `plugin.py`
- [ ] Remove metadata parameter from `storage.store_report()`
- [ ] Remove `storage.get_metadata()` method
- [ ] Remove `metadata/` directory handling
- [ ] Update `pytest_sessionfinish` to not capture separate metadata
- [ ] Update `jux-cache` to read metadata from XML properties
- [ ] Update `test_plugin.py` integration tests
- [ ] Update `test_storage.py` (remove JSON tests)
- [ ] Add `test_metadata_integration.py` for pytest_metadata hook
- [ ] Update all documentation
- [ ] Create migration script
- [ ] Update CHANGELOG.md

## Testing Strategy

### Unit Tests

**New Tests** (`tests/test_metadata_integration.py`):
```python
def test_pytest_metadata_hook_adds_jux_metadata(pytester):
    """Test that pytest_metadata hook injects jux metadata."""
    result = pytester.runpytest("--junit-xml=report.xml")

    # Parse XML
    tree = etree.parse("report.xml")
    properties = tree.xpath("//properties/property")

    # Verify jux:* properties exist
    prop_names = [p.get("name") for p in properties]
    assert "jux:hostname" in prop_names
    assert "jux:timestamp" in prop_names
    assert "jux:platform" in prop_names
```

**Updated Tests**:
- `test_storage.py`: Remove JSON sidecar tests
- `test_plugin.py`: Verify metadata in XML, not JSON

### Integration Tests

```bash
# End-to-end test
pytest tests/ \
  --junit-xml=report.xml \
  --jux-sign \
  --jux-key=test_key.pem \
  --metadata ci_build 12345

# Verify metadata in XML
jux-inspect report.xml | grep "jux:hostname"
jux-inspect report.xml | grep "ci_build"

# Verify signature includes metadata
jux-verify report.xml --cert=test_cert.pem
```

## Success Criteria

1. ✅ All metadata (user + environment) in XML `<properties>`
2. ✅ All metadata cryptographically signed
3. ✅ No JSON sidecar files created
4. ✅ `pytest_metadata` hook properly injects jux metadata
5. ✅ CLI precedence works (user metadata not overridden)
6. ✅ All tests pass
7. ✅ Documentation updated

## Timeline

- **2025-10-24**: ADR created and accepted
- **Sprint 7**: Implementation (v0.3.0)
  - Week 1: Code changes and tests
  - Week 2: Documentation and migration scripts
- **Target Release**: v0.3.0 (minor version - breaking change)

## Security Implications

### Improved Security

1. **Provenance Integrity**: Environment metadata now signed
2. **Tamper Detection**: Any metadata modification invalidates signature
3. **Chain of Trust**: Complete audit trail from test execution to report

### No Security Regressions

- Signature verification unchanged
- Canonicalization unchanged
- Key management unchanged

## References

### Internal

- **ADR-0003**: Technology stack (pytest-metadata dependency)
- **Sprint 3 Plan**: Original metadata and storage implementation
- **docs/howto/add-metadata-to-reports.md**: User documentation

### External

- [pytest-metadata Documentation](https://github.com/pytest-dev/pytest-metadata)
- [JUnit XML Schema](https://github.com/windyroad/JUnit-Schema) - `<properties>` element
- [XMLDSig Specification](https://www.w3.org/TR/xmldsig-core/) - What gets signed

---

**Conclusion**: Integrating environment metadata with pytest-metadata eliminates architectural duplication, ensures all metadata is cryptographically signed, and simplifies storage to a single XML file per report. This improves security, reduces complexity, and aligns with standard JUnit XML practices.

**Adopted**: 2025-10-24
**Author**: Georges Martin
**Impact**: Medium (breaking change, but improves security and simplifies architecture)
**Effort**: Medium (code changes, test updates, documentation)
