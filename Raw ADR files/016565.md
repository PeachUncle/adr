# ADR-016: Documentation Link Validation Strategy

**Status:** Accepted  
**Date:** 2025-09-21  
**Supersedes:** None  
**Superseded by:** None  

## Context

The ServiceNow-OpenShift integration project maintains extensive documentation including 15 ADRs, comprehensive guides, and technical references. This documentation contains numerous external links to ServiceNow documentation, OpenShift resources, security standards, and technical specifications. A comprehensive link validation analysis revealed significant issues:

- **24 broken external links (11.7%)** affecting critical references
- **18 warning links (8.7%)** with timeout or accessibility issues  
- **Multiple ServiceNow documentation timeouts** impacting core ADR references
- **Broken internal links** due to file reorganization and missing documentation

These broken links undermine documentation credibility, create poor user experience, and can mislead developers implementing the system. The analysis was conducted using MCP (Model Context Protocol) tools, specifically the `documcp` server's `check_documentation_links_documcp` function, which provided comprehensive validation across 48 documentation files.

## Decision

We will implement a **comprehensive link validation strategy** using MCP tools and establish ongoing maintenance processes to ensure documentation link integrity:

### **1. MCP-Based Link Validation Framework**

**Primary Tool**: `documcp` MCP server with `check_documentation_links_documcp`
- **External Link Validation**: HTTP status checking with timeout handling
- **Internal Link Validation**: File system verification for relative links
- **Anchor Link Validation**: Fragment identifier verification within documents
- **Comprehensive Reporting**: Detailed analysis with categorized issues and recommendations

**Validation Configuration**:
```yaml
validation_settings:
  check_external_links: true
  check_internal_links: true  
  check_anchor_links: true
  timeout_ms: 5000
  max_concurrent_checks: 3
  output_format: detailed
```

### **2. Link Quality Standards**

**External Link Requirements**:
- **Prefer Official Documentation**: Use official vendor documentation over blog posts
- **Stable URLs**: Avoid links with version numbers or temporary paths
- **Fallback References**: Provide alternative sources for critical concepts
- **Archive-Friendly**: Use links that are likely to remain stable long-term

**Internal Link Requirements**:
- **Relative Paths**: Use relative paths for internal documentation references
- **File Existence Verification**: Ensure all referenced files exist
- **Consistent Structure**: Follow established documentation hierarchy

### **3. Automated Validation Process**

**CI/CD Integration**:
```bash
# Link validation in documentation build process
./docs/scripts/validate-links.sh --fail-on-broken --report-format=json
```

**Regular Monitoring**:
- **Weekly Automated Checks**: Scheduled link validation runs
- **Pull Request Validation**: Link checking for documentation changes
- **Quarterly Comprehensive Reviews**: Full documentation link audit

### **4. Issue Resolution Workflow**

**Broken Link Response**:
1. **Immediate**: Replace with working alternative if available
2. **Short-term**: Update to current official documentation
3. **Long-term**: Consider archiving critical external content locally

**ServiceNow Documentation Strategy**:
- **Community Links**: Prefer ServiceNow Community over docs.servicenow.com for stability
- **Multiple Sources**: Provide both official docs and community references
- **Version-Agnostic**: Use links that work across ServiceNow versions

## Rationale

### **Why MCP Tools?**

1. **Comprehensive Analysis**: MCP tools provide detailed validation beyond simple HTTP checks
2. **Integration Capability**: Seamless integration with existing development workflows
3. **Structured Output**: Machine-readable results for automated processing
4. **Extensibility**: Can be enhanced with additional validation rules and checks

### **Why This Approach?**

1. **Proactive Quality**: Prevents broken links from reaching users
2. **Automated Maintenance**: Reduces manual effort in link maintenance
3. **User Experience**: Ensures reliable documentation for developers
4. **Professional Standards**: Maintains high-quality documentation standards

### **Evidence-Based Decision**

The validation analysis revealed specific patterns:
- **ServiceNow docs.servicenow.com**: High timeout rate, needs alternative approach
- **Official Vendor Sites**: Generally reliable (Keycloak, OpenShift, OWASP)
- **Blog Posts and Articles**: Higher failure rate, need careful selection
- **Internal Links**: Issues primarily from file reorganization

## Consequences

### **Positive Consequences**

1. **Improved Documentation Quality**: Reliable links enhance user trust and experience
2. **Reduced Maintenance Burden**: Automated validation catches issues early
3. **Better User Experience**: Developers can rely on documentation references
4. **Professional Standards**: High-quality documentation reflects project maturity
5. **Proactive Issue Detection**: Problems identified before users encounter them

### **Negative Consequences**

1. **Additional CI/CD Time**: Link validation adds time to build processes
2. **Maintenance Overhead**: Requires ongoing attention to validation results
3. **False Positives**: Some valid links may be flagged due to temporary issues
4. **Tool Dependency**: Reliance on MCP tools for validation functionality

### **Risk Mitigation**

1. **Timeout Handling**: Configure appropriate timeouts to balance thoroughness and speed
2. **Retry Logic**: Implement retry mechanisms for temporary failures
3. **Manual Override**: Allow manual approval for known-good links that fail validation
4. **Fallback Validation**: Multiple validation methods for critical links

## Implementation

### **Phase 1: Immediate Fixes (Week 1)**

**Critical Broken Links**:
```markdown
# Replace broken links identified in validation report
- Vault: https://www.vaultproject.io/ → https://developer.hashicorp.com/vault
- Keycloak: Update installation guide references
- ServiceNow: Replace timeout-prone links with community alternatives
```

**Internal Link Fixes**:
- Create missing README files
- Update relative path references
- Verify all cross-references

### **Phase 2: Automation Setup (Week 2)**

**CI/CD Integration**:
```yaml
# .github/workflows/documentation.yml
- name: Validate Documentation Links
  run: |
    cd docs
    npx @documcp/cli check-links --config .link-validation.yml
```

**Validation Script**:
```bash
#!/bin/bash
# docs/scripts/validate-links.sh
set -euo pipefail

echo "🔍 Validating documentation links..."
cd "$(dirname "$0")/.."

# Run MCP link validation
documcp check_documentation_links_documcp \
  --documentation_path="content" \
  --check_external_links=true \
  --check_internal_links=true \
  --output_format=detailed \
  --max_concurrent_checks=3

echo "✅ Link validation complete"
```

### **Phase 3: Monitoring and Maintenance (Ongoing)**

**Regular Validation**:
- **Weekly**: Automated link health checks
- **Monthly**: Comprehensive validation reports
- **Quarterly**: Full documentation review and cleanup

**Alert System**:
- **Slack/Email Notifications**: For broken link detection
- **GitHub Issues**: Automatic issue creation for persistent problems
- **Dashboard**: Link health monitoring dashboard

### **Phase 4: Documentation Standards (Week 3)**

**Updated CONTRIBUTING.md**:
```markdown
## Link Validation Requirements

Before submitting documentation changes:

1. Run link validation: `./docs/scripts/validate-links.sh`
2. Fix any broken links identified
3. Ensure new external links follow quality standards
4. Test internal links in local build
```

**ADR Template Updates**:
```markdown
## External References

When adding external references to ADRs:
- ✅ Use official documentation when available
- ✅ Provide fallback references for critical concepts  
- ✅ Validate links before submission
- ❌ Avoid blog posts for critical technical references
```

## Related ADRs

- **ADR-013**: PDI Workaround Strategy - Contains ServiceNow documentation references affected by link issues
- **ADR-014**: Business Rules Over Flow Designer - References ServiceNow documentation that experienced timeouts
- **ADR-003**: Centralized Configuration - Contains multiple broken external references identified in validation

## References

### **Validation Results**
- `docs/content/reference/link-validation-report.md` - Comprehensive validation analysis
- **MCP Tool Used**: `documcp` server `check_documentation_links_documcp` function
- **Analysis Date**: 2025-09-21
- **Files Analyzed**: 48 documentation files
- **Links Validated**: 206 total links

### **External Standards**
- [W3C Link Checker Guidelines](https://www.w3.org/Tools/linkchecker/) - Web link validation standards
- [Documentation Best Practices](https://www.writethedocs.org/guide/writing/docs-principles/) - Documentation quality guidelines
- [Markdown Link Validation](https://github.com/tcort/markdown-link-check) - Industry standard practices

### **Tools and Implementation**
- **MCP Documentation Server**: Primary validation tool
- **GitHub Actions**: CI/CD integration platform
- **Link Validation Scripts**: Custom automation for project-specific needs

---

**This ADR establishes the foundation for maintaining high-quality, reliable documentation through systematic link validation and maintenance processes.**
