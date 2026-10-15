# ADR-031: Choice of Secrets Detection Implementation with Pre-commit Hooks

**Date:** 2025-10-13

**Status:** Decided & Implemented

## Context

The PlumbingPOC project handles sensitive data including API keys, database credentials, and user authentication tokens. During development, there was an incident where hardcoded secrets were nearly committed to the repository. We needed a robust, automated solution to prevent accidental secret leaks while allowing legitimate code patterns like environment variable references and variable assignments.

The initial implementation used a custom Python pre-commit hook, but this required ongoing maintenance of secret patterns and whitelisting logic. As a common security need, we sought a more professional, maintainable solution.

## Decision

We will use **detect-secrets** (by Yelp) integrated with the **pre-commit framework** for automated secrets detection, **combined with our enhanced custom Python hook** for dual-layer protection. This provides both industry-standard comprehensive scanning and our tailored logic for specific API key patterns.

The solution consists of:

- **detect-secrets**: Professional tool with 20+ secret types, entropy analysis, and baseline management
- **Custom Python Hook**: Enhanced with key-specific whitelisting for precise control over API keys vs generic terms
- **pre-commit framework**: Orchestrates both systems with additional code quality checks
- **Baseline management**: Tracks existing secrets to prevent false positives

## Implementation

Both detection systems run automatically on every commit:

### detect-secrets Configuration
```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
      exclude: ^(package-lock\.json|\.secrets\.baseline)$
```

### Custom Python Hook Configuration
```yaml
- repo: local
  hooks:
    - id: custom-secrets-scan
      name: Custom secrets scanner (legacy Python hook)
      entry: python3
      language: system
      files: .*
      pass_filenames: false
      args:
        - .githooks/pre-commit
```

### Key-Specific Whitelisting Logic

The custom hook implements sophisticated whitelisting:

- **Specific API Keys** (GEMINI_API_KEY, OPENAI_API_KEY, etc.): Strict - no variable name whitelisting
- **Generic Terms** (PASSWORD, SECRET, TOKEN): Permissive - allows variable names like `adminPassword`
- **Safe Patterns**: Environment variables, config objects, function calls, and placeholder brackets

## Consequences

*   **Pros:**
    *   **Dual-Layer Protection**: Both professional tool AND custom logic provide maximum security
    *   **Professional Security**: Industry-standard detect-secrets used by major companies
    *   **Comprehensive Coverage**: 20+ secret types + custom API key patterns
    *   **Precise Control**: Key-specific whitelisting prevents false positives
    *   **Automatic Updates**: New secret patterns added as they're discovered
    *   **Baseline Management**: Tracks existing secrets to avoid false positives
    *   **Performance**: Optimized scanning with baseline caching
    *   **Integration**: Works seamlessly with existing pre-commit workflows
    *   **Additional Checks**: Includes trailing whitespace, YAML validation, and large file detection

*   **Cons:**
    *   **Complexity**: Running two systems requires coordination
    *   **Maintenance**: Both systems need updates and monitoring
    *   **Learning Curve**: Understanding both baseline management and custom logic
    *   **Performance**: Slightly slower with dual scanning
    *   **Configuration Complexity**: Managing two different detection systems

*   **Security Benefits:**
    *   **Maximum Protection**: Two independent systems catch different threat patterns
    *   **Proactive Prevention**: Catches secrets before they reach the repository
    *   **Pattern Recognition**: Entropy analysis + custom regex patterns
    *   **Comprehensive Scanning**: Checks all file types, not just code files
    *   **Audit Trail**: Baseline + custom logic provide complete visibility

*   **Maintenance Benefits:**
    *   **Best of Both Worlds**: Professional tool + tailored custom logic
    *   **Community Support**: Active development and security updates for detect-secrets
    *   **Standard Tooling**: Familiar to security teams and auditors
    *   **Flexible Updates**: Can update either system independently

## Alternatives Considered

*   **Custom Python Hook Alone (Original Implementation)**:
    *   **Pros**: Full control, tailored to our specific patterns, no external dependencies
    *   **Cons**: High maintenance burden, limited secret pattern coverage, manual updates required
    *   **Outcome**: **COMBINED** - Used alongside detect-secrets for dual-layer protection

*   **detect-secrets Alone**:
    *   **Pros**: Professional tool, comprehensive coverage, automatic updates
    *   **Cons**: Generic patterns might miss project-specific issues, less control over whitelisting
    *   **Outcome**: **COMBINED** - Used alongside custom hook for maximum security

*   **GitLeaks**:
    *   **Pros**: Popular Go-based scanner, fast performance, extensive secret patterns
    *   **Cons**: More complex setup, less integration with pre-commit framework
    *   **Rejected**: detect-secrets has better pre-commit integration

*   **TruffleHog**:
    *   **Pros**: Most comprehensive scanning, includes git history analysis
    *   **Cons**: Overkill for pre-commit use case, slower performance
    *   **Rejected**: Better suited for CI/CD pipelines than pre-commit hooks

*   **Git-Secrets (AWS)**:
    *   **Pros**: AWS-backed, good pattern coverage
    *   **Cons**: Limited to git, fewer secret types than detect-secrets
    *   **Rejected**: Less comprehensive than detect-secrets

## Usage Guidelines

### For Developers:
- Run `pre-commit run --all-files` to test hooks locally
- Update baseline with `detect-secrets scan --baseline .secrets.baseline` after legitimate changes
- Use `<REDACTED>` in code when documenting secret usage

### For CI/CD:
- Include pre-commit checks in pipeline
- Monitor for new secret patterns requiring baseline updates
- Regular baseline audits to ensure no secrets have been inadvertently added

### For Security Team:
- Review baseline changes during code reviews
- Monitor detect-secrets releases for new capabilities
- Conduct periodic secret audits using the baseline as a reference

## Related Documentation

- [detect-secrets documentation](https://github.com/Yelp/detect-secrets)
- [pre-commit framework](https://pre-commit.com/)
- Project security guidelines in `docs/SECURITY.md`
