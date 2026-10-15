---
status: accepted
date: 2025-10-03
deciders:
  - voder-dev-team
consulted:
  - security-team
  - platform-team
informed:
  - contributors
packages: '@voder/dev-config'
---

# ADR-0020: Supply-chain Audit & Registry-Mirror Policy with Vulnerability Acceptance Criteria

## Context and Problem Statement

The project needs to ensure that all dependencies are audited for vulnerabilities and installs are pulled from trusted mirrors to protect against malicious or unavailable registry endpoints. Additionally, we need clear criteria for when security vulnerabilities can be accepted as residual risk versus requiring immediate remediation.

## Decision Drivers

- Automated vulnerability scanning
- Failover registry-mirror support
- Reproducible, secure installs
- Risk-based vulnerability management
- Balance between security and operational continuity
- Clear criteria for vulnerability acceptance

## Considered Options

1. Zero-tolerance policy (block all vulnerabilities)
2. Severity-based blocking (moderate and above)
3. Risk-based acceptance with time limits and criteria
4. Manual review for all vulnerabilities

## Decision Outcome

Chosen option: "Require automated supply-chain audits with risk-based vulnerability acceptance criteria," because it provides continuous vulnerability detection, resilient dependency fetching, and practical risk management for operational continuity.

### Vulnerability Acceptance Criteria

**Vulnerabilities MAY be accepted as residual risk when ALL of the following conditions are met:**

1. **Age Criterion**: Vulnerability is less than 14 days old (from first detection date)
2. **Patch Availability**: No security patch is available from the package maintainer
3. **Documentation**: Vulnerability is formally documented as a security incident using the security incident template
4. **Risk Assessment**: Formal risk assessment completed and documented in the security incident
5. **Monitoring**: Periodic monitoring established for patch availability

**Outside of these criteria, we MUST:**

- Stop using the dependency (find alternative), OR
- Implement strong and effective controls to reduce residual risk to acceptable levels

**This policy applies to ALL dependencies regardless of whether they are:**

- Development dependencies or production dependencies
- Direct dependencies or transitive dependencies
- Critical, high, medium, or low severity vulnerabilities

### Security Incident Documentation Requirement

**Only unpatchable vulnerabilities that are accepted as residual risk MUST be documented as formal security incidents using:**

- Template: `prompt-assets/security-incident-template.md`
- Location: `docs/security-incidents/SECURITY-INCIDENT-{YYYY-MM-DD}-{brief-description}.{status}.md`
- Status tracking: DETECTED → INVESTIGATING → CONTAINED → RESOLVED → CLOSED

**Vulnerabilities that can be immediately patched do NOT require formal security incident documentation** - standard commit messages and change logs are sufficient.

### Consequences

- Good: Immediate alerts on high-severity vulnerabilities
- Good: Redundant registry endpoints for CI builds
- Good: Clear, time-bound criteria for vulnerability acceptance
- Good: Formal documentation of security decisions
- Good: Balance between security and operational needs
- Bad: Additional CI configuration and contributor onboarding
- Bad: Increased documentation overhead for security incidents
- Bad: Time pressure for vulnerability remediation

### Confirmation

**Technical Confirmation:**

- CI runs automated vulnerability scanning (`npm audit`)
- Project root contains registry-mirror configuration
- Security incident documentation process established

**Process Confirmation:**

- Vulnerability acceptance decisions documented in security incidents
- 14-day monitoring established for accepted vulnerabilities
- Alternative dependency evaluation process defined
- Risk mitigation controls assessment framework established
