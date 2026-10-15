# Use AWS CLI for Infrastructure Validation (Tier 4)

**Date:** 2025-12-22

## Context

The Locus project implements a multi-tier validation pipeline to ensure code quality and infrastructure reliability. Tier 4 (Infrastructure Audit) requires deployment testing of the CloudFormation Infrastructure-as-Code template (`locus-stack.yaml`) in a real AWS environment to validate:

- CloudFormation syntax is correct and deployable
- AWS quota limits are not exceeded
- IAM policies have correct capabilities
- S3 bucket with Object Lock is created successfully
- IAM user and access keys are generated correctly
- All stack outputs are available for runtime use

**The Problem:**
When designing Tier 4 infrastructure validation, we needed to choose between:
1. Using a dedicated CloudFormation testing tool (TaskCat)
2. Using AWS-native CLI commands directly

TaskCat appeared to be a reasonable choice initially but presented significant challenges:
- **Unmaintained:** Last updated ~2023, no active development
- **Dependency Conflicts:** Would introduce massive Python dependency hell (PyYAML 4.x vs 5.x, jsonschema conflicts)
- **Python Version Locking:** Would lock the project to Python 3.10, preventing use of Python 3.11+
- **Over-engineered:** Designed for complex, multi-region testing scenarios; our stack is simple and single-region
- **Abstraction Layer:** Creates a wrapper over AWS APIs rather than using them directly

## Decision

We will **use AWS CLI native CloudFormation commands** for infrastructure validation (Tier 4), implemented as a shell script (`scripts/audit_infrastructure.sh`) that:

1. Deploys the CloudFormation stack using `aws cloudformation deploy`
2. Validates stack status with `aws cloudformation describe-stacks`
3. Verifies all required outputs are present
4. Automatically cleans up using `aws cloudformation delete-stack`
5. Uses trap-based cleanup to guarantee deletion even on failure or interrupt (Ctrl+C)

The script runs **locally only** (requires real AWS credentials) and is manually executed by developers before submitting infrastructure changes.

## Consequences

### Positive

- **No Python Dependency Conflicts:** Removes all dependency version constraints; works with Python 3.11, 3.12, 3.13, or any future version
- **AWS-Native:** Uses AWS-provided tools, not third-party abstractions; simpler mental model for developers
- **Lower Maintenance Burden:** AWS CLI is actively maintained by AWS and receives regular security updates
- **Easier to Debug:** Standard AWS CLI commands are well-documented and familiar to AWS users
- **Simpler to Understand:** Direct API integration means less "magic" happening under the hood
- **Flexible:** Developers can easily extend the script with custom validation logic using standard AWS CLI commands
- **Aligned with Infrastructure Philosophy:** Embraces "use what AWS provides" rather than adding abstraction layers

### Negative

- **Manual Execution Only:** Requires developers to run the script locally; not suitable for automated CI/CD (due to AWS credential requirements)
- **Requires AWS Credentials:** Developers must have valid AWS credentials configured to run infrastructure validation
- **No Cost Tracking:** Unlike TaskCat, there's no built-in cost estimation or tracking (not a concern for single test stack)
- **Multi-Region Testing Not Built-In:** Would require custom script extensions for multi-region testing in future phases (acceptable for Phase 0)

### Risks

- **Developer Overhead:** Developers must remember to run the validation before submitting infrastructure changes (mitigated by clear documentation and pre-commit hooks in future)
- **AWS Credential Exposure:** Requires developers to have AWS credentials locally; mitigated by using IAM roles and least-privilege access
- **Stack Cleanup Failures:** If AWS CloudFormation API is slow or unavailable, stack cleanup might timeout (mitigated by clear error messages and manual cleanup instructions)

## Alternatives Considered

### TaskCat (Rejected)

**Why:** TaskCat is a dedicated CloudFormation testing tool that handles multi-region deployments, cost estimation, and complex testing scenarios.

**Reasons for Rejection:**
- **Unmaintained:** Last update ~2023; no active development or Python 3.11+ support
- **Dependency Hell:** Would introduce PyYAML 4.x vs 5.x conflicts, jsonschema version conflicts, and docker version issues
- **Over-Engineered:** Designed for complex multi-region testing; our simple single-region stack doesn't justify the complexity
- **Philosophy Mismatch:** Adds abstraction layer over AWS APIs rather than using AWS-native tools directly
- **Cost:** Introduces Python dependency management complexity with no proportional benefit

### cfn-lint Only (Rejected)

**Why:** cfn-lint is a CloudFormation linter that validates template syntax and best practices.

**Reasons for Rejection:**
- **Static Analysis Only:** Cannot validate actual AWS deployment (quota limits, permissions, resource creation)
- **Incomplete Validation:** Misses real-world issues that only appear during actual deployment
- **Not Sufficient:** Doesn't fulfill the Tier 4 requirement of "actual AWS environment validation"

### Container Isolation (Rejected)

**Why:** Run TaskCat and other tools in separate containers to avoid dependency conflicts.

**Reasons for Rejection:**
- **Excessive Complexity:** Adds Docker complexity for a simple validation task
- **Difficult CI/CD Setup:** Harder to manage in GitHub Actions without significant workflow changes
- **Overkill:** The root problem (unmaintained TaskCat) remains; containers don't fix it
- **Steeper Learning Curve:** Developers need to understand container concepts

---

## Related Decisions

- **ADR: Pure Kotlin Domain Layer** - Establishes preference for clean architecture and avoiding third-party abstractions
- **ADR: Tracer Bullet MVP** - Phase 0 focuses on simple, end-to-end validation rather than complex multi-region testing

## Future Considerations

- **Multi-Region Testing:** If Phase 1+ requires multi-region infrastructure validation, the AWS CLI script can be extended to loop over multiple regions
- **Cost Estimation:** If AWS cost tracking becomes important, we could integrate AWS Cost Explorer API or similar tools
- **CI/CD Integration:** If we need automated infrastructure validation in CI/CD, we could use temporary AWS credentials via OIDC token exchange (GitHub Actions feature)
- **Advanced Validation:** Could extend script to perform additional checks (security group rules, Lambda functions, etc.) using AWS CLI

## Sign-Off

**Decision Maker:** Project Team (informed by dependency analysis and multi-tier validation pipeline design)

**Approved:** Yes

**Rationale Summary:** AWS CLI is the simplest, most maintainable approach for Phase 0 infrastructure validation. It eliminates dependency conflicts, supports modern Python versions, and aligns with AWS-native design principles. The local-only execution model is acceptable for Phase 0; future phases can extend this approach as needed.
