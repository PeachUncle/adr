---
status: accepted
date: 2025-10-02
decision-makers: [Development Team]
consulted: []
informed: [Project Stakeholders]
---

# Use Environment Variables for All Secrets and Credentials

## Context and Problem Statement

During development, applications require various API keys, tokens, and other sensitive credentials to integrate with third-party services. These credentials must be managed securely to prevent unauthorized access while maintaining developer productivity and deployment automation.

The recent security incident (SECURITY-INCIDENT-2025-09-30-hardcoded-secrets) revealed that hardcoded credentials in source code create significant security risks, including potential unauthorized service access and API quota abuse.

## Decision Drivers

- Prevent credential exposure in version control systems
- Enable secure development workflow without compromising productivity
- Support automated deployment while maintaining security
- Comply with security best practices for credential management
- Facilitate credential rotation without code changes
- Enable different credential sets for different environments

## Considered Options

- Environment variables with `.env` files excluded from version control
- External credential management services (AWS Secrets Manager, HashiCorp Vault)
- Encrypted credential files in version control
- Hardcoded credentials with access restrictions

## Decision Outcome

Chosen option: "Environment variables with `.env` files excluded from version control", because it provides the best balance of security, simplicity, and developer productivity for our current scale and requirements.

### Consequences

- Good, because credentials are never committed to version control
- Good, because different environments can use different credential sets
- Good, because credential rotation requires no code changes
- Good, because widely supported across deployment platforms
- Bad, because requires manual environment setup for new developers
- Bad, because credentials are stored in plaintext on deployment systems
- Neutral, because requires documentation and training for proper usage

### Confirmation

Implementation compliance will be confirmed through:

- Pre-commit hooks that scan for potential credential patterns
- Automated secret scanning in CI/CD pipeline
- Regular security audits of environment configuration
- Code review requirements for environment variable usage

## Pros and Cons of the Options

### Environment variables with `.env` files excluded from version control

Standard approach using environment variables for configuration with local `.env` files for development that are explicitly excluded from version control.

- Good, because prevents credential exposure in git history
- Good, because widely supported by deployment platforms
- Good, because enables environment-specific configuration
- Good, because simple to implement and understand
- Good, because supports credential rotation without code changes
- Bad, because requires manual setup for each developer
- Bad, because credentials stored in plaintext on systems
- Neutral, because requires proper `.gitignore` configuration

### External credential management services

Using dedicated services like AWS Secrets Manager or HashiCorp Vault for credential storage and retrieval.

- Good, because provides centralized credential management
- Good, because supports advanced features like automatic rotation
- Good, because credentials are encrypted at rest and in transit
- Good, because provides audit trails for credential access
- Bad, because adds significant complexity to development workflow
- Bad, because requires additional infrastructure and cost
- Bad, because overkill for current project scale
- Bad, because adds external dependencies for development

### Encrypted credential files in version control

Storing credentials in encrypted files that are committed to version control.

- Good, because credentials travel with the code
- Good, because no manual environment setup required
- Bad, because encryption keys must be managed separately
- Bad, because all developers need access to decryption keys
- Bad, because credential rotation requires code commits
- Bad, because git history contains encrypted credentials
- Bad, because increases complexity without significant benefit

### Hardcoded credentials with access restrictions

Embedding credentials directly in code with repository access controls.

- Good, because simple for development
- Good, because no environment setup required
- Bad, because credentials exposed to anyone with repository access
- Bad, because credentials stored in git history permanently
- Bad, because credential rotation requires code changes
- Bad, because violates security best practices
- Bad, because creates security audit failures

## More Information

This decision implements the recommendations from security incident SECURITY-INCIDENT-2025-09-30-hardcoded-secrets and establishes a foundation for secure credential management across all project environments.

The implementation should include:

- Comprehensive `.env.example` templates for all required credentials
- Clear documentation on credential management procedures
- Pre-commit hooks and CI/CD scanning to prevent credential exposure
- Regular security audits to verify compliance

Future enhancements may include migration to external credential management services as the project scales and security requirements evolve.
