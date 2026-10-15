# Design: Unity Asset Corruption Prevention System

## Context

Unity projects are uniquely vulnerable to asset corruption due to:
- Complex binary asset serialization formats
- Version-specific serialization schemas
- Git's text-based line ending transformations
- Large-scale asset interdependencies via GUIDs
- Third-party plugin compatibility issues

The MLCreator project experienced prefab corruption when using Unity 6 with GameCreator plugins designed for Unity 2021/2022. This design establishes a multi-layered defense system.

## Goals

### Primary Goals
- **Zero asset corruption incidents** after system deployment
- **100% detection rate** for Unity version mismatches
- **<15 minute recovery time** from detected corruption
- **<5 second overhead** for git operations (pre-commit validation)

### Non-Goals
- Automatic Unity version upgrades (requires manual intervention)
- Plugin auto-updating (compatibility verification only)
- Real-time Unity Editor monitoring (post-process only)
- Cross-project asset management (single project focus)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Prevention Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Git Hooks    │  │ Unity Config │  │ .gitattributes│     │
│  │ (pre-commit) │  │ (Force Text) │  │ (LF endings) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Detection Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Asset Health │  │ Console Log  │  │ GUID Validator│     │
│  │ Monitor      │  │ Scanner      │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Recovery Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Asset Backup │  │ Git History  │  │ Rollback     │     │
│  │ Snapshots    │  │ Recovery     │  │ Automation   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Orchestration│  │ Project Brain│  │ Serena Memory│     │
│  │ Quality Gates│  │ Monitoring   │  │ (Lessons)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Key Technical Decisions

### Decision 1: Git Pre-Commit Hooks vs CI/CD Validation

**Choice**: Git pre-commit hooks with CI/CD as backup

**Rationale**:
- **Speed**: Catches issues immediately before commit (fast feedback)
- **Local validation**: No dependency on remote CI/CD pipeline
- **Emergency bypass**: Can be overridden locally in genuine emergencies
- **Defense in depth**: CI/CD provides second validation layer

**Alternatives Considered**:
- **CI/CD only**: Too slow (minutes vs seconds), blocks entire team
- **IDE plugins**: Not all developers use same IDE
- **Manual checks**: Human error prone, not enforceable

**Trade-offs**:
- ✅ Fast feedback, local enforcement
- ❌ Developers can bypass hooks (mitigated by CI/CD backup)
- ❌ Requires installation on each machine

### Decision 2: Force Text Serialization vs Smart Binary Detection

**Choice**: Force Text serialization for all Unity assets

**Rationale**:
- **Git-friendly**: Text diffs enable meaningful code review
- **Merge conflict resolution**: Easier to resolve conflicts in text
- **Corruption detection**: Text format easier to validate
- **Unity 6 default**: Aligns with Unity's recommended approach

**Alternatives Considered**:
- **Binary serialization**: Smaller files, but opaque to version control
- **Mixed mode**: Complexity without clear benefits
- **Git LFS for all**: Expensive, loses diff capability

**Trade-offs**:
- ✅ Git-friendly, human-readable, merge-friendly
- ❌ Larger repository size (mitigated by Git LFS for truly large assets)
- ❌ Slightly slower Unity serialization (negligible in practice)

### Decision 3: Automated vs Manual Asset Recovery

**Choice**: Automated detection, semi-automated recovery with human confirmation

**Rationale**:
- **Safety**: Asset recovery is high-stakes, requires human judgment
- **Complexity**: Full automation requires perfect dependency tracking
- **Audit trail**: Human confirmation ensures accountability
- **Learning**: Manual steps help team understand asset relationships

**Alternatives Considered**:
- **Full automation**: Too risky, could propagate bad state
- **Fully manual**: Too slow, error-prone
- **AI-driven**: Insufficient training data for Unity asset dependencies

**Trade-offs**:
- ✅ Safety, accountability, learning opportunity
- ❌ Slower than full automation
- ❌ Requires trained team members

### Decision 4: Unity Version Enforcement Strategy

**Choice**: STRICT enforcement - block all commits with version mismatches

**Rationale**:
- **Corruption prevention**: Version mismatches are primary corruption cause
- **Consistency**: Ensures entire team uses same Unity version
- **Plugin compatibility**: Simplifies plugin compatibility management
- **Clear expectations**: No ambiguity about supported versions

**Alternatives Considered**:
- **Warning only**: Too easy to ignore, doesn't prevent issues
- **Major version match**: Allows minor version drift, still risky
- **No enforcement**: Current state, proven inadequate

**Trade-offs**:
- ✅ Complete corruption prevention from version drift
- ❌ Strict requirement may slow team onboarding
- ❌ Requires coordination for Unity version upgrades

### Decision 5: Integration with Orchestration System

**Choice**: Full integration as mandatory quality gate

**Rationale**:
- **Enforcement**: Orchestration ensures no bypass of validation
- **Consistency**: Aligns with project's orchestration architecture
- **Monitoring**: Leverages existing monitoring infrastructure
- **Memory**: Serena memory preserves lessons learned

**Alternatives Considered**:
- **Standalone system**: Fragmented, easier to bypass
- **Manual process**: Not reliable at scale
- **Optional validation**: Defeats prevention purpose

**Trade-offs**:
- ✅ Enforceable, consistent, integrated monitoring
- ❌ Depends on orchestration system (acceptable given project architecture)
- ❌ Cannot be fully disabled (feature, not bug)

## Component Specifications

### Git Pre-Commit Hook

**Location**: `.git/hooks/pre-commit`
**Language**: PowerShell (cross-platform via pwsh)
**Execution Time Budget**: <5 seconds

**Validation Sequence**:
```powershell
1. Verify Unity version matches ProjectVersion.txt (6000.2.13f1)
2. Scan staged .prefab/.asset/.mat files for corruption signatures
3. Validate .meta files exist for all staged Unity assets
4. Check for GUID conflicts or missing references
5. Parse Unity Editor logs for recent errors (last 24h)
```

**Corruption Signatures**:
- Invalid YAML syntax (unmatched brackets, malformed structure)
- Missing Unity file header (`%YAML 1.1`, `%TAG !u!`)
- Truncated files (incomplete GameObject definitions)
- Null/empty serialized fields without explicit null markers

**Performance Optimization**:
- Only scan staged files (not entire project)
- Cache validation results for 5 minutes
- Parallel validation for multiple files
- Skip validation for non-Unity files

### Asset Health Monitor

**Location**: `.project-brain/monitors/asset-health.py`
**Schedule**: Daily at 2 AM (off-hours), on-demand via CLI
**Language**: Python 3.10+

**Monitoring Checks**:
```python
1. Full project scan for corrupted assets
2. Unity console log parsing (last 24 hours)
3. .meta file integrity validation
4. GUID reference validation (detect broken links)
5. Plugin compatibility verification
6. Asset dependency graph generation
```

**Alert Triggers**:
- Any corrupted asset detected → Critical alert
- Unity version mismatch → Critical alert
- Missing .meta files → High alert
- Broken GUID references → Medium alert
- Plugin compatibility issues → Low alert

**Output Artifacts**:
- `asset-health-report.json` (structured data)
- `asset-health-report.md` (human-readable)
- `asset-dependency-graph.json` (for recovery planning)

### Unity Configuration

**ProjectSettings/EditorSettings.asset**:
```yaml
Asset Serialization:
  Mode: Force Text
  Line Ending Mode: Unix (LF)
  Visible Meta Files: Enabled

Version Control:
  Mode: Visible Meta Files
  Semantic Merge Tool: UnityYAMLMerge
```

**.gitattributes**:
```
# Unity YAML files - Force LF, text diff
*.prefab text eol=lf
*.asset text eol=lf
*.mat text eol=lf
*.unity text eol=lf
*.anim text eol=lf
*.controller text eol=lf
*.meta text eol=lf

# Unity binary files - Git LFS
*.cubemap filter=lfs diff=lfs merge=lfs -text
*.unitypackage filter=lfs diff=lfs merge=lfs -text

# Large assets - Git LFS
*.fbx filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.psd filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
```

### Backup & Recovery System

**Snapshot Strategy**:
- **Before Unity upgrades**: Full project snapshot
- **Before plugin updates**: Plugin-specific asset backup
- **Daily automated**: Incremental backup of changed assets
- **On-demand**: Manual snapshot via CLI

**Snapshot Storage**:
```
.unity-backups/
├── snapshots/
│   ├── 2025-11-25_pre-upgrade/
│   │   ├── manifest.json
│   │   └── assets/
│   └── 2025-11-24_daily/
├── meta-backups/
│   └── 2025-11-25/
└── recovery-logs/
```

**Recovery Procedure**:
```bash
1. Detect corrupted asset (via monitoring or manual report)
2. Generate asset dependency graph
3. Identify recovery candidates from git history or snapshots
4. Preview recovery impact (what files will be restored)
5. Human confirmation required
6. Execute recovery
7. Validate recovered assets in Unity Editor
8. Document incident in Serena memory
```

## Plugin Compatibility Management

**GameCreator Plugin Matrix**:
```yaml
Behavior.ActionPlan@1.1.3:
  unity_6_compatible: UNKNOWN (testing required)
  workaround: Use git history recovery if prefabs fail
  contact: support@gamecreator.io
  priority: HIGH (currently blocking)

Shooter.Weapons@1.1.4:
  unity_6_compatible: TESTING
  status: Materials modified, prefabs intact
  priority: MEDIUM

Other Plugins:
  [To be documented during implementation]
```

**Verification Process**:
1. Contact GameCreator support about Unity 6 compatibility
2. Test each plugin individually in isolated Unity 6 project
3. Document compatibility status and workarounds
4. Create plugin upgrade/replacement plan if incompatible
5. Track compatibility in project brain

## Integration with Orchestration

**Quality Gate Integration**:
```json
{
  "pre_execution_gates": {
    "asset_health_check": {
      "enabled": true,
      "blocking": true,
      "script": ".project-brain/monitors/asset-health.py --quick-scan"
    },
    "unity_version_check": {
      "enabled": true,
      "blocking": true,
      "required_version": "6000.2.13f1"
    }
  }
}
```

**Orchestration Workflow Steps**:
- **Step 3 (Rule Validation)**: Add Unity version validation
- **Step 6 (Pre-Execution Gates)**: Add asset health check
- **Step 9 (Post-Execution Gates)**: Validate no new corruption introduced
- **Step 11 (Context Update)**: Store asset health metrics in Serena memory

## Risks & Mitigation

### Risk 1: Performance Impact on Git Operations

**Risk**: Pre-commit hooks slow down commits unacceptably
**Probability**: Medium
**Impact**: High (developer productivity)

**Mitigation**:
- Optimize hook to only scan staged files
- Implement result caching (5 minute TTL)
- Parallel file validation
- Emergency bypass procedure documented
- Monitor performance and adjust thresholds

### Risk 2: False Positives Block Valid Commits

**Risk**: Overly aggressive validation rejects valid assets
**Probability**: Medium
**Impact**: Medium (developer frustration)

**Mitigation**:
- Comprehensive testing before rollout
- Clear error messages with resolution steps
- Emergency bypass procedure (with audit logging)
- Feedback mechanism for false positive reporting
- Iterative tuning based on real-world usage

### Risk 3: GameCreator Plugin Incompatibility

**Risk**: Plugins fundamentally incompatible with Unity 6
**Probability**: Low-Medium
**Impact**: High (blocks development)

**Mitigation**:
- Immediate contact with GameCreator support
- Research alternative solutions/plugins
- Consider Unity version downgrade if critical path
- Document workarounds for known issues
- Parallel development track on compatible Unity version

### Risk 4: Recovery Procedure Complexity

**Risk**: Recovery procedures too complex for team to execute
**Probability**: Low
**Impact**: High (prolonged downtime)

**Mitigation**:
- Create step-by-step playbooks with screenshots
- Practice recovery drills quarterly
- Designate recovery champions on team
- AI assistant integration for guided recovery
- Escalation path to Unity experts if needed

### Risk 5: Git LFS Cost and Complexity

**Risk**: Git LFS introduces storage costs or complexity
**Probability**: Low
**Impact**: Medium (cost, workflow disruption)

**Mitigation**:
- Start with conservative LFS rules (only truly large files)
- Monitor storage usage and adjust thresholds
- Document LFS setup procedures clearly
- Consider alternative storage if costs become issue
- Gradual rollout to test impact

## Migration Plan

### Phase 1: Assessment (Week 1)
1. Complete asset health scan of current state
2. Create baseline metrics (corruption count, affected assets)
3. Backup current project state
4. Test recovery procedures on non-critical assets

### Phase 2: Git Configuration (Week 1-2)
1. Implement .gitattributes rules
2. Create pre-commit hook
3. Test on isolated branch
4. Document developer setup procedures

### Phase 3: Monitoring System (Week 2)
1. Implement asset health monitor
2. Integrate with project brain
3. Configure alerts
4. Test with known good/bad assets

### Phase 4: Documentation (Week 2-3)
1. Create incident response playbook
2. Document recovery procedures
3. Create developer onboarding guide
4. Add to AI assistant critical context

### Phase 5: Team Rollout (Week 3)
1. Announce changes to team
2. Conduct training session
3. Monitor first week closely
4. Collect feedback and iterate

### Phase 6: Orchestration Integration (Week 4)
1. Add quality gates to orchestration
2. Test end-to-end workflow
3. Enable monitoring integration
4. Document orchestration procedures

## Rollback Strategy

If the system causes unacceptable issues:

1. **Immediate**: Disable pre-commit hooks (remove execute permission)
2. **Short-term**: Revert .gitattributes and ProjectSettings changes
3. **Long-term**: Restore from backup snapshot
4. **Analysis**: Conduct post-mortem to identify issues
5. **Iteration**: Address issues and attempt rollout again

**Rollback Triggers**:
- >5 second git commit overhead
- >10% false positive rate
- Team productivity impact >20%
- Unresolvable compatibility issues

## Open Questions

1. **GameCreator Unity 6 Compatibility**:
   - When will GameCreator officially support Unity 6?
   - Are there beta versions available for testing?
   - What are recommended workarounds?

2. **Git LFS Hosting**:
   - Should we use GitHub LFS, Git LFS server, or alternative?
   - What are storage cost projections?
   - Who manages LFS infrastructure?

3. **Team Training**:
   - What is team's current Git proficiency level?
   - How much training time can we allocate?
   - Who will be recovery procedure champions?

4. **Unity Version Upgrade Cadence**:
   - How often should we upgrade Unity versions?
   - What triggers a version upgrade decision?
   - What is approval process for version changes?

5. **CI/CD Integration**:
   - Do we have CI/CD pipeline for Unity builds?
   - Should we add asset validation to CI/CD?
   - What is our testing infrastructure?

These questions should be answered before implementation begins.

## Success Metrics

**Primary Metrics**:
- Asset corruption incidents: 0 per quarter (target)
- Unity version violations blocked: 100% detection rate
- Recovery time: <15 minutes from detection to resolution
- Git operation overhead: <5 seconds average

**Secondary Metrics**:
- False positive rate: <5%
- Developer satisfaction: >80% approval
- Documentation completeness: 100% coverage
- Training completion: 100% of team

**Monitoring Dashboard**:
```
Unity Asset Health Dashboard
├── Current Status: ✅ Healthy / ⚠️ Warning / 🚨 Critical
├── Assets Scanned: [count] / [total]
├── Corruption Incidents: [count this week/month/quarter]
├── Unity Version: 6000.2.13f1 (✅ Compliant)
├── Plugin Compatibility: [X/Y compatible]
├── Last Health Check: [timestamp]
└── Recent Incidents: [list of last 5]
```

## Conclusion

This design establishes a comprehensive, multi-layered defense against Unity asset corruption. By combining prevention (git hooks, Unity config), detection (monitoring), and recovery (backups, procedures), we create a resilient system that protects project integrity while maintaining developer productivity.

The integration with the orchestration system ensures consistent enforcement, while the documentation and training ensure team capability. Success metrics and monitoring provide continuous feedback for improvement.
