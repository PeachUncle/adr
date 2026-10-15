# ADR-0003: Implement Git Hooks for Quality Gate Enforcement

## Status
**Proposed**

## Context

The AgenticOps Value Train™ relies on consistent quality standards and proper workflow compliance to function effectively. Current challenges include:

- Inconsistent commit message formats that break automated phase tracking
- Code quality variations due to missing linting enforcement
- Large files accidentally committed to repository history
- YAML header inconsistencies in session context files
- Manual validation processes that are skipped under pressure

Without automated quality gates, the Value Train's automation and traceability features become unreliable, and technical debt accumulates rapidly.

## Decision

We will implement comprehensive git hooks to enforce quality gates at multiple points in the development workflow:

### Pre-commit Hooks
1. **Commit Message Validation**: Enforce `#complete phase:<id>` format for phase tracking
2. **YAML Header Validation**: Ensure session context files have proper front-matter structure  
3. **File Size Limits**: Prevent files >5MB from entering git history (encourage Git LFS)
4. **Code Formatting**: Run linting tools (flake8, black, isort) on Python files
5. **Path Reference Validation**: Check `@docs/` and other path references are valid

### Pre-push Hooks
1. **Test Execution**: Run full test suite before allowing push to remote
2. **Build Validation**: Ensure `make ci` passes locally before push
3. **Branch Naming**: Validate branch follows `phase/<description>` convention

### Implementation Approach
- Use `.pre-commit-config.yml` for standardized hook management
- Provide clear setup instructions in documentation
- Include bypass mechanisms for emergency situations
- Integrate with existing CI/CD pipeline for consistency

## Consequences

### Positive
- **Automated Quality**: Consistent enforcement without human intervention
- **Early Detection**: Catch issues before they enter repository history
- **Workflow Compliance**: Ensure Value Train tracking mechanisms function correctly
- **Reduced Debugging**: Prevent common issues from reaching shared branches
- **Documentation Accuracy**: Ensure path references and YAML headers remain valid

### Negative
- **Developer Friction**: Additional steps in commit/push workflow
- **Setup Complexity**: Developers must install and configure pre-commit tools
- **False Positives**: Hooks may occasionally block legitimate commits
- **Emergency Overrides**: Need escape hatches for urgent fixes

### Neutral
- **Tool Dependency**: Adds dependency on pre-commit framework
- **Maintenance Overhead**: Hooks require updates as standards evolve

## Rationale

Git hooks were chosen over alternatives because they:

1. **Catch Issues Early**: Problems detected before they enter shared history
2. **Enforce Standards**: Automated compliance with Value Train requirements
3. **Developer Education**: Immediate feedback teaches correct practices
4. **Integration Friendly**: Works seamlessly with existing Git workflows
5. **Customizable**: Can be tailored to specific project needs

### Alternatives Considered
- **CI-Only Validation**: Too late in process, issues already in history
- **IDE Integration**: Not all developers use same tools
- **Manual Code Review**: Inconsistent and doesn't scale

### Implementation Strategy
1. Start with basic commit message validation
2. Add code formatting and file size checks
3. Implement test execution and build validation
4. Monitor for issues and adjust rules as needed

## Related Decisions
- Supports ADR-0001 (AgenticOps Value Train adoption) by ensuring workflow compliance
- Enables ADR-0002 (Auto-Pilot) by providing quality guarantees for autonomous operation
- Will integrate with session context management approach (future ADR)

## References
- [Pre-commit Framework](https://pre-commit.com/) for hook implementation
- [Value Train Alignment Plan](../../value-train-alignment-plan.md) - CRD-B tasks
- [Git Workflow Rules](../../rules/git-workflow.md) for current standards
- [Planning Tasks](../../planning-tasks.md) for linting requirements