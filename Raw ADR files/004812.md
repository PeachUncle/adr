# ADR-005: Secrets Redaction Before Transmission

## Status

**Accepted** (2026-01-03)

## Context

When users operate in Burst mode and consent to external LLM API calls, Acode transmits source code context and prompts to third-party services. This creates a critical security risk: **accidental transmission of secrets**.

### Types of Secrets at Risk

1. **API Keys**: `OPENAI_API_KEY=sk-proj-...`, `ANTHROPIC_API_KEY=sk-ant-...`
2. **Passwords**: Database passwords, admin credentials
3. **Private Keys**: SSH keys, GPG keys, TLS certificates
4. **Tokens**: JWT tokens, OAuth tokens, session tokens
5. **Connection Strings**: Database URLs with embedded credentials
6. **Environment Variables**: Sensitive config in `.env` files

### Real-World Incidents

- GitHub scans detect millions of leaked secrets annually
- AWS keys committed to repos lead to $100K+ bills from abuse
- Database credentials in code enable data breaches
- API keys in prompts logged by LLM providers indefinitely

### Threat Model

**Attacker Goal**: Obtain secrets from Acode LLM prompts

**Attack Vectors**:
1. **LLM Provider Logging**: Provider logs prompts containing secrets
2. **Provider Breach**: Attacker compromises LLM provider, exfiltrates logs
3. **Insider Threat**: Provider employee accesses customer prompts
4. **Model Training**: Secrets inadvertently used in model training data
5. **Cache Exposure**: Secrets in cached responses

**Impact**: Credential compromise, unauthorized access, data breach, financial loss

## Decision

**Before ANY data is transmitted to external LLM APIs in Burst mode, all secrets must be redacted.**

### Redaction Principles

1. **Fail-Safe**: If secret detection fails, block transmission (don't send)
2. **Conservative**: Prefer false positives (redact non-secrets) over false negatives (miss secrets)
3. **Transparent**: Log what was redacted (but not the secret itself)
4. **Irreversible**: Once redacted, original value cannot be recovered from transmitted data
5. **Defense-in-Depth**: Multiple layers of detection

### Secrets to Detect and Redact

#### High-Entropy Strings

Patterns likely to be secrets:
- Base64 strings longer than 32 characters
- Hex strings longer than 32 characters
- Random-looking alphanumeric strings (entropy > threshold)

#### Named Patterns

Known secret formats:
- `AKIA[0-9A-Z]{16}` - AWS Access Key ID
- `sk-[a-zA-Z0-9]{48}` - OpenAI API Key
- `sk-ant-[a-zA-Z0-9-]{95}` - Anthropic API Key
- `ghp_[a-zA-Z0-9]{36}` - GitHub Personal Access Token
- `glpat-[a-zA-Z0-9]{20}` - GitLab Personal Access Token
- `xox[baprs]-[a-zA-Z0-9-]+` - Slack tokens
- `-----BEGIN [A-Z ]+ PRIVATE KEY-----` - Private keys

#### Environment Variables

Common secret variable names:
- `*_API_KEY`, `*_SECRET`, `*_PASSWORD`, `*_TOKEN`
- `DATABASE_URL`, `CONN_STRING`, `PRIVATE_KEY`
- `AWS_SECRET_ACCESS_KEY`, `GITHUB_TOKEN`

#### File Patterns

Files likely to contain secrets:
- `.env`, `.env.local`, `.env.production`
- `credentials.json`, `secrets.yml`
- `id_rsa`, `id_ed25519`, `*.pem`, `*.key`

### Redaction Implementation

```python
# Pseudo-code

def redact_secrets(text: str) -> tuple[str, list[RedactionEvent]]:
    """
    Redact secrets from text before transmission.

    Returns:
        (redacted_text, redaction_events)
    """
    redacted = text
    events = []

    # High-entropy detection
    for match in find_high_entropy_strings(text):
        redacted = redacted.replace(match, "[REDACTED:HIGH_ENTROPY]")
        events.append(RedactionEvent("high_entropy", match_position))

    # Named patterns
    for pattern_name, regex in SECRET_PATTERNS.items():
        for match in regex.finditer(redacted):
            redacted = redacted.replace(match.group(), f"[REDACTED:{pattern_name}]")
            events.append(RedactionEvent(pattern_name, match.start()))

    # Environment variable values
    for var_name in SENSITIVE_VAR_NAMES:
        if f"{var_name}=" in redacted:
            # Redact value after =
            redacted = re.sub(
                f"{var_name}=.*?($|\\s)",
                f"{var_name}=[REDACTED:ENV_VAR]\\1",
                redacted
            )
            events.append(RedactionEvent("env_var", var_name))

    return redacted, events
```

### Redaction Markers

Redacted content replaced with descriptive markers:
- `[REDACTED:AWS_KEY]` - AWS access key redacted
- `[REDACTED:API_KEY]` - Generic API key redacted
- `[REDACTED:PRIVATE_KEY]` - Private key redacted
- `[REDACTED:HIGH_ENTROPY]` - High-entropy string redacted

Markers preserve context for LLM (knows a key was there) without leaking secret.

### User Notification

When secrets are redacted:
1. **Log Event**: Audit log records what was redacted (type, position, not value)
2. **User Warning**: CLI displays warning: "Warning: 3 secrets redacted from prompt"
3. **Transmission Blocked**: If secrets detected, optionally block transmission entirely (user configurable)

## Consequences

### Positive

1. **Prevents Secret Leaks**
   - Secrets not transmitted to LLM providers
   - Reduces risk of credential compromise
   - Protects against provider breaches

2. **Compliance Support**
   - GDPR Article 32 (security measures)
   - PCI DSS (no clear-text passwords)
   - SOC2 CC6.1 (logical access security)

3. **Defense-in-Depth**
   - Additional layer beyond access controls
   - Catches secrets even if user forgets
   - Mitigates human error

4. **Audit Trail**
   - Logs show redaction events
   - Can prove secrets were protected
   - Forensic investigation supported

5. **User Trust**
   - Demonstrates commitment to security
   - Reduces fear of accidental leaks
   - Encourages Burst mode adoption

### Negative

1. **False Positives**
   - May redact non-secrets (high entropy code)
   - Could break LLM context
   - User might need to manually review/override

2. **Performance Impact**
   - Scanning adds latency to API calls
   - Regex matching computationally expensive
   - May need optimization for large codebases

3. **Maintenance Burden**
   - Must update secret patterns regularly
   - New secret formats emerge (new API providers)
   - Entropy thresholds may need tuning

4. **False Negatives**
   - Novel secret formats might evade detection
   - Obfuscated secrets might pass through
   - Perfect detection impossible

5. **Reduced LLM Quality**
   - Redacted context may reduce LLM accuracy
   - Missing credentials affect debugging help
   - User might disable feature if frustrating

## Alternatives Considered

### 1. No Redaction (User Responsibility)

**Description**: Trust users to not include secrets in transmitted code

**Rejected Because**:
- Users make mistakes
- Secrets often embedded in files (.env, config)
- No defense against human error
- Violates principle of least privilege

### 2. Prompt User for Confirmation Before Sending

**Description**: Show user exactly what will be sent, require confirmation

**Rejected Because**:
- Too disruptive (every API call needs confirmation)
- Users develop "confirmation bias" and click through
- Doesn't scale to large contexts (thousands of lines)
- Users might not notice secrets in large text

### 3. Block Transmission Entirely if Secrets Detected

**Description**: Abort API call if any secret detected, force user to fix

**Rejected Because**:
- Too restrictive (false positives block legitimate use)
- Frustrating user experience
- Redaction approach more flexible
- User can review and override if needed

### 4. Encrypt Secrets Instead of Redacting

**Description**: Replace secrets with encrypted version, decrypt after LLM response

**Rejected Because**:
- LLM provider still sees plaintext (defeats purpose)
- Encryption doesn't prevent leaks if provider logs
- Added complexity without security benefit
- Redaction simpler and more secure

### 5. Client-Side Scanning Only (No Enforcement)

**Description**: Warn user about potential secrets, but don't block/redact

**Rejected Because**:
- Users might ignore warnings
- No guarantee of protection
- Weak security control
- Enforcement required per HC-04

## Related Constraints

- **HC-04**: Secrets redacted before transmission

## Related ADRs

- [ADR-004: Burst Mode Consent](adr-004-burst-mode-consent.md)
- [ADR-001: No External LLM API by Default](adr-001-no-external-llm-default.md)

## Implementation Notes

### Future Enhancements

- **Custom Secret Patterns**: Allow users to define organization-specific secret patterns
- **Machine Learning Detection**: Train model to detect novel secret formats
- **Integration with Secret Managers**: Fetch known secrets from HashiCorp Vault, AWS Secrets Manager
- **Visual Diff**: Show user before/after redaction in GUI

### Epic 9 Implementation

Secret redaction will be implemented in Epic 9 (Safety, Policy Engine, Secrets Hygiene):
- `ISecretScanner` interface
- Regex pattern library
- Entropy calculator
- Redaction engine
- Audit logging integration

See:
- Epic 9: Secret scanning implementation
- Task 003: Threat model (includes secret exposure threat)
- CONSTRAINTS.md: HC-04 enforcement details

### Testing Requirements

- **Unit Tests**: Each secret pattern must have tests
- **False Positive Tests**: Known non-secrets must not be redacted
- **False Negative Tests**: All secret types must be detected
- **Performance Tests**: Scanning must complete within 100ms for typical files
- **Integration Tests**: End-to-end transmission with redaction verified

## Review History

- **2026-01-03**: Proposed by Security Team
- **2026-01-03**: Accepted by Architecture, Security, Product
- **Security Review**: Confirmed aligns with industry best practices (GitHub Secret Scanning, GitGuardian)

## Notes

This ADR establishes Acode's secret redaction requirements. The implementation will evolve as new secret formats emerge and detection techniques improve.

Users with highly sensitive secrets should still prefer LocalOnly mode over Burst mode with redaction. Redaction is a safety net, not a primary security control.

**Priority**: High (required before Burst mode can be safely used)
