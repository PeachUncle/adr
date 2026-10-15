# ADR-056: Auto-Housekeeping CI Enforcement

## Status

Proposed

## Decision

Add CI check for housekeeping post-change (Rule 058) - mandatory rules_audit.py/share.sync/forest regen after every change/PR.

## Context

The original documentation synchronization rule (009-documentation-sync.mdc) was minimal and didn't enforce comprehensive housekeeping practices. Agents and developers lacked clear guidance on:

- Rule numbering continuity validation (rules_audit.py)
- Documentation synchronization requirements (share.sync)
- Forest overview regeneration (generate_forest.py)
- Pre-PR verification checklists
- Automated verification and drift detection

This led to inconsistent housekeeping practices and potential governance gaps across the development team.

## Decision

Enhance housekeeping requirements with Rule 058 (Auto-Housekeeping Post-Change) requiring mandatory execution after every change/PR:

1. **Rule Audit Execution**: `rules_audit.py` validates rule numbering and documentation sync
2. **Share Directory Sync**: `make share.sync` ensures documentation synchronization
3. **Forest Regeneration**: `generate_forest.py` rebuilds project overview from current state
4. **Always-Applied Enforcement**: No exceptions to housekeeping requirements
5. **Fail-Closed Design**: Operations fail if housekeeping skipped with critical error logs

## Implementation Details

### CI Integration

```yaml
# .github/workflows/ci.yml - Add to existing CI
- name: Housekeeping Validation
  run: |
    python3 scripts/rules_audit.py
    make share.sync
    python3 scripts/generate_forest.py
```

### Pre-commit Hook Integration

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run housekeeping validation
python3 scripts/rules_audit.py
make share.sync
python3 scripts/generate_forest.py

# Check if any files changed (indicates housekeeping was needed)
if git diff --quiet --exit-code; then
    echo "✅ Housekeeping completed successfully"
else
    echo "❌ Housekeeping modified files - please review and commit changes"
    exit 1
fi
```

### PR Template Integration

```markdown
<!-- .github/pull_request_template.md -->

## Housekeeping Verification

- [ ] `rules_audit.py` executed successfully
- [ ] `make share.sync` completed without errors
- [ ] `generate_forest.py` updated project overview
- [ ] No unexpected file modifications from housekeeping

## Evidence

**Rules Audit Output:**
```
[rules_audit] PASS - Rules numbering contiguous, docs updated
```

**Share Sync Output:**
```
[update_share] OK — share/ refreshed (2/15 files updated)
```

**Forest Generation Output:**
```
[generate_forest] Updated docs/forest/overview.md with 58 active rules
```
```

## Consequences

### Positive

- **Governance Integrity**: Single source of truth across all environments
- **Developer Productivity**: Automated checks prevent manual oversight
- **Consistency**: Standardized housekeeping reduces cognitive load
- **Audit Trail**: Complete history of rule and documentation changes
- **Fail-Safe Design**: Critical errors prevent governance gaps

### Negative

- **Process Overhead**: More comprehensive housekeeping requirements add time
- **Learning Curve**: New contributors need to understand housekeeping standards
- **Automation Complexity**: Implementing automated enforcement adds technical debt
- **Performance Impact**: Comprehensive housekeeping may slow development workflow

### Risks

- **Rule Complexity**: Overly complex housekeeping may be ignored or misunderstood
- **Enforcement Challenges**: Always-applied rules require robust tooling
- **Housekeeping Drift**: Manual processes may still allow inconsistencies
- **Developer Resistance**: Additional requirements may slow development velocity

## Alternatives Considered

### Option 1: Minimal Enhancement

- **Pro**: Less disruptive, maintains existing workflow
- **Con**: Doesn't address core housekeeping consistency issues
- **Decision**: Insufficient for production safety requirements

### Option 2: External CI Tool

- **Pro**: Purpose-built tooling, better automation
- **Con**: Additional dependency, integration complexity, cost
- **Decision**: Internal solution preferred for consistency with existing rules

### Option 3: Selective Enforcement

- **Pro**: Granular control over when housekeeping applies
- **Con**: Inconsistent enforcement, complexity
- **Decision**: Always-applied provides clarity and consistency

### Option 4: Housekeeping as Code

- **Pro**: Version control integration, automated validation
- **Con**: Requires significant infrastructure changes
- **Decision**: Too disruptive, defer to future phase

## Testing Strategy

### Housekeeping Validation

- **Syntax Checking**: Ensure all housekeeping scripts execute correctly
- **File Modification Testing**: Verify expected files are updated appropriately
- **CI Integration Testing**: Automated validation in CI environment
- **Pre-commit Hook Testing**: Local development workflow validation

### Rule Audit Testing

- **Numbering Validation**: Automated rule number continuity checks
- **Documentation Sync**: Cross-reference validation between rules and docs
- **Forest Generation**: Automated overview regeneration verification

### Share Sync Testing

- **File Comparison**: SHA-256 content comparison accuracy
- **Manifest Parsing**: JSON manifest structure validation
- **Preview Generation**: Head file generation for large exports

## Performance Characteristics

### Development Workflow Impact

- **Pre-commit Checks**: ~15 seconds for full housekeeping validation
- **CI Execution**: ~30 seconds for comprehensive housekeeping
- **Local Development**: ~5 seconds for individual housekeeping commands
- **Forest Regeneration**: ~2 seconds automatic execution

### Automation Benefits

- **Time Savings**: Automated validation prevents manual review delays
- **Error Prevention**: Early detection of housekeeping gaps
- **Consistency**: Standardized processes reduce cognitive load
- **Scalability**: Rules apply uniformly across team size

## Future Considerations

### Advanced Automation

- **Change Detection**: Real-time identification of housekeeping requirements
- **Incremental Updates**: Only run housekeeping for modified components
- **Parallel Execution**: Optimize housekeeping performance
- **Status Caching**: Cache housekeeping results for faster re-validation

### Tooling Enhancements

- **IDE Integration**: Housekeeping checks in development environment
- **Status Dashboard**: Housekeeping completion and health metrics
- **Automated Remediation**: Self-healing housekeeping gaps
- **Smart Filtering**: Only run relevant housekeeping based on changes

### Process Refinement

- **Housekeeping Templates**: Standardized checklists and procedures
- **Training Materials**: Onboarding guides for housekeeping standards
- **Community Standards**: External contributor housekeeping requirements
- **Performance Optimization**: Faster housekeeping execution

## Implementation Requirements

### Immediate Actions

1. **Rule Creation**: Deploy Rule 058 with comprehensive requirements
2. **ADR Documentation**: Create ADR-056 with implementation details
3. **CI Integration**: Add housekeeping checks to existing CI workflows
4. **Pre-commit Hooks**: Implement local housekeeping validation
5. **PR Templates**: Update templates with housekeeping verification sections
6. **Documentation Updates**: Reflect new housekeeping requirements in AGENTS.md

### Validation Steps

1. **Rule Syntax**: Verify .mdc file parses correctly
2. **CI Execution**: Test housekeeping in CI environment
3. **Pre-commit Testing**: Validate local development workflow
4. **PR Template Testing**: Ensure template sections work correctly
5. **Documentation Verification**: Confirm all docs reflect new requirements

### Rollback Plan

- **Rule Reversion**: Remove Rule 058 if issues arise
- **ADR Status Change**: Mark ADR-056 as rejected
- **CI Reversion**: Restore previous CI configuration
- **Hook Removal**: Disable pre-commit housekeeping validation
- **Template Reversion**: Restore previous PR template

## Related ADRs

- ADR-013: Comprehensive documentation synchronization enhancement
- ADR-017: Agent documentation presence enforcement
- ADR-019: Forest governance & phase gate system

## Related Rules

- Rule 027: Docs sync gate (housekeeping includes docs sync)
- Rule 055: Auto-docs sync pass (housekeeping enforces this)
- Rule 017: Agent docs presence (housekeeping validates coverage)
