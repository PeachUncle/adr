# ADR 0007: ESLint 9 Upgrade Guard

**Status:** Accepted  
**Date:** 2025-09-11

## Context

ESLint 9 introduces significant breaking changes, including the removal of deprecated APIs and configuration changes that could break existing tooling. The Next.js ecosystem, specifically `eslint-config-next`, has not yet fully migrated to support ESLint 9.

Current state analysis:
- Project uses ESLint flat config (`eslint.config.mjs`) with modern patterns
- Dependencies include `eslint-config-next` which requires ESLint 8.x compatibility
- Premature upgrade to ESLint 9 would break CI/CD pipeline and development workflows
- No immediate business value in upgrading until ecosystem support is available

## Decision

We will **defer ESLint 9 upgrade** until the Next.js ecosystem provides full compatibility, specifically:

### 1. Upgrade Prerequisites
- `eslint-config-next` officially supports ESLint 9
- All related ESLint plugins in our stack support ESLint 9
- Next.js documentation confirms ESLint 9 compatibility

### 2. Dependency Management Strategy
- **Block automatic ESLint major version updates** in dependency management tools
- Add `eslint` to dependency update ignore lists or pin to `^8.x`
- Monitor ecosystem compatibility through quarterly reviews

### 3. Documentation Requirements
- Track ESLint 9 migration in project issues with label `blocked:eslint9`
- Maintain upgrade timeline and compatibility checklist
- Document current ESLint configuration dependencies

### 4. Monitoring and Review Process
- **Quarterly assessment** of ecosystem compatibility status
- Review `eslint-config-next` release notes for ESLint 9 support announcements
- Test ESLint 9 compatibility in isolated branch when prerequisites are met

## Implementation

### Renovate Configuration
If using Renovate for dependency management:

```json
{
  "packageRules": [
    {
      "matchPackageNames": ["eslint"],
      "matchUpdateTypes": ["major"],
      "enabled": false,
      "description": "Block ESLint 9 until eslint-config-next compatibility - see ADR 0007"
    }
  ]
}
```

### GitHub Dependabot Configuration
If using Dependabot:

```yaml
# .github/dependabot.yml
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    ignore:
      - dependency-name: "eslint"
        update-types: ["version-update:semver-major"]
```

### Project Issue Tracking
Create tracking issue with:
- Label: `blocked:eslint9`
- Title: "Upgrade to ESLint 9 when ecosystem supports it"
- Checklist of compatibility requirements
- Links to relevant ecosystem tracking issues

### Manual Override Process
If urgent ESLint 9 upgrade becomes necessary:
1. Create dedicated branch for testing
2. Document breaking changes and workarounds
3. Update this ADR with new decision rationale
4. Obtain team approval for ecosystem-ahead upgrade

## Quality Gates

### Before ESLint 9 Upgrade
- [ ] `eslint-config-next` officially supports ESLint 9
- [ ] All ESLint plugins in dependency tree support ESLint 9
- [ ] Next.js documentation confirms compatibility
- [ ] Test migration in isolated environment
- [ ] Update CI/CD pipeline configurations
- [ ] Team training on any new ESLint 9 patterns

### During Migration
- [ ] Run full test suite with new ESLint version
- [ ] Verify Storybook and development server functionality
- [ ] Test build process with updated linting
- [ ] Validate editor integrations (VS Code, etc.)
- [ ] Update documentation and team guidelines

### Post-Migration
- [ ] Monitor for new ESLint-related issues
- [ ] Update dependency management rules
- [ ] Share lessons learned with team
- [ ] Update this ADR to reflect successful migration

## Risk Assessment

### Risks of Premature Upgrade
- **CI/CD Pipeline Breakage**: Incompatible rules could fail builds
- **Development Workflow Disruption**: Editor integrations might break
- **Time Investment**: Manual fixes for ecosystem incompatibilities
- **Maintenance Burden**: Custom workarounds for missing features

### Risks of Delayed Upgrade
- **Security Vulnerabilities**: Missing security fixes in newer ESLint versions
- **Technical Debt**: Growing gap between current and latest tooling
- **Developer Experience**: Missing new ESLint 9 features and improvements
- **Ecosystem Lag**: Falling behind on modern development practices

### Mitigation Strategies
- **Regular Monitoring**: Quarterly ecosystem compatibility reviews
- **Security Patches**: Apply security fixes within ESLint 8.x range
- **Parallel Testing**: Test ESLint 9 in isolated branches
- **Communication**: Keep team informed of upgrade timeline

## Alternatives Considered

### 1. Immediate Upgrade with Workarounds
**Rejected**: High risk of breaking changes without clear ecosystem support

### 2. Custom ESLint Configuration
**Rejected**: Would require maintaining custom rules and losing Next.js optimizations

### 3. Migrate to Alternative Linters
**Rejected**: ESLint is industry standard; migration costs outweigh benefits

### 4. Pin to ESLint 8 Indefinitely
**Rejected**: Would accumulate technical debt and security vulnerabilities

## Success Metrics

### Compatibility Assessment
- **Ecosystem Support**: Official announcements from `eslint-config-next`
- **Community Adoption**: Multiple successful migration reports
- **Tooling Integration**: Editor and CI tool compatibility confirmed

### Migration Success
- **Zero Breaking Changes**: Existing linting rules continue to work
- **Performance Maintained**: No degradation in linting performance
- **Team Productivity**: No disruption to development workflow

### Long-term Benefits
- **Security Posture**: Access to latest ESLint security features
- **Developer Experience**: Improved error messages and performance
- **Ecosystem Alignment**: Compatibility with latest tooling

## References

- [ESLint 9 Migration Guide](https://eslint.org/docs/latest/use/migrate-to-9.0.0)
- [Next.js ESLint Configuration](https://nextjs.org/docs/basic-features/eslint)
- [ESLint Flat Config Documentation](https://eslint.org/docs/latest/use/configure/configuration-files-new)
- [eslint-config-next Repository](https://github.com/vercel/next.js/tree/canary/packages/eslint-config-next)

## Consequences

### Positive
- **Stability**: Prevents CI/CD pipeline disruption from premature upgrades
- **Predictability**: Clear criteria for when upgrade should occur
- **Risk Management**: Systematic approach to ecosystem dependency management
- **Team Alignment**: Clear communication of upgrade timeline and rationale

### Negative
- **Technical Debt**: Growing gap between current and latest ESLint version
- **Security Exposure**: Potential delay in receiving latest security fixes
- **Feature Gap**: Missing access to new ESLint 9 improvements
- **Maintenance Overhead**: Need to monitor ecosystem compatibility

### Mitigation
- **Regular Reviews**: Quarterly assessment prevents indefinite deferral
- **Security Monitoring**: Track ESLint security advisories for backports
- **Parallel Testing**: Maintain upgrade readiness through testing
- **Clear Criteria**: Objective prerequisites prevent subjective delays

---

**Decision Date**: 2025-09-11  
**Responsible**: Frontend Architecture Team  
**Review Date**: 2025-12-11 (Quarterly)  
**Next Review Focus**: eslint-config-next ESLint 9 compatibility status
