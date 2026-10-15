# ADR-004: Burst Mode Requires Consent

## Status

**Accepted** (2026-01-03)

## Context

Burst mode allows users to access powerful external LLM APIs (OpenAI, Anthropic, Google AI) when local models are insufficient. However, this introduces data transmission risks:

1. **Unintended Data Exfiltration**: User might forget Burst mode is active and transmit sensitive code
2. **Compliance Violations**: GDPR/SOC2 require explicit consent for data processing
3. **Accidental Exposure**: Third-party APIs log prompts, creating data retention concerns
4. **Trust Erosion**: Silent data transmission violates Acode's privacy-first principle

### Legal Requirements

- **GDPR Article 7**: Consent must be "freely given, specific, informed and unambiguous"
- **GDPR Article 13**: Users must be informed about data processing before it occurs
- **SOC2 CC6.2**: Access permissions must be reviewed and approved
- **CCPA**: Consumers must have ability to opt-in to data sharing

### User Scenarios

**Scenario 1: Complex Refactoring**
- Developer needs GPT-4 for complex refactoring
- Temporarily enables Burst mode
- Consents to sending code to OpenAI
- After refactoring, returns to LocalOnly

**Scenario 2: Emergency Bug Fix**
- Production bug, need Claude Opus help
- Enable Burst, consent to data sharing
- Fix bug quickly
- Disable Burst after emergency

**Scenario 3: Open Source Project**
- Public codebase, no privacy concern
- Enables Burst mode permanently
- Consents once per session
- Doesn't need to re-consent for public code

## Decision

**Burst mode requires explicit, session-scoped consent before ANY external LLM API call.**

### Consent Properties

1. **Explicit**: User must actively consent (checkbox, CLI flag, not implicit)
2. **Informed**: User shown what data will be transmitted and to which provider
3. **Specific**: Consent granular per provider (OpenAI, Anthropic, etc.)
4. **Session-Scoped**: Consent expires when Acode process terminates
5. **Revocable**: User can revoke consent mid-session (switches to LocalOnly)

### Implementation

#### CLI Consent Flow

```bash
# User enables Burst mode
$ acode --mode=burst

[Acode] Burst mode enables external LLM APIs. This will transmit code to third-party services.

Providers available:
  - OpenAI (gpt-4, gpt-3.5-turbo)
  - Anthropic (claude-3-opus, claude-3-sonnet)
  - Google AI (gemini-pro)

Data transmitted:
  - Source code context
  - User prompts
  - File names and paths

Consent to external API usage? [yes/no]: yes

[Acode] Consent granted. External APIs enabled for this session.
[Acode] To revoke, use: acode --mode=localonly
```

#### Programmatic Consent

- **Consent Token**: Generated when user consents
- **Token Validation**: Checked before every external API call
- **Token Expiry**: Expires when process terminates
- **Token Storage**: In-memory only (never persisted to disk)

### What Requires Consent

| Operation | Requires Consent? | Rationale |
|-----------|-------------------|-----------|
| External LLM API call | ✅ Yes | Transmits code/prompts |
| Local model (Ollama) | ❌ No | No data leaves machine |
| LAN model (vLLM on 192.168.x.x) | ❌ No | Stays within local network |
| GitHub API call | ⚠️ Debatable | Not LLM, but is external |
| Package registry | ⚠️ Debatable | Not AI-related |

**Decision**: Consent applies only to LLM API calls initially. Future ADR may expand scope.

### Consent Scope

**Per-Session**: Consent is valid for the lifetime of the Acode process
- User doesn't re-consent for every API call (too disruptive)
- Consent resets when Acode restarts
- Clear workflow: consent once, work, terminate

**Not Persistent**: Consent is NEVER saved to config files
- User must actively consent each session
- Prevents "set and forget" mode
- Ensures ongoing awareness

## Consequences

### Positive

1. **Legal Compliance**
   - GDPR Article 7 satisfied (explicit consent)
   - SOC2 CC6.2 satisfied (access approval)
   - CCPA opt-in requirement met

2. **User Awareness**
   - User explicitly knows when data transmitted
   - Clear prompt explains what's shared
   - Cannot accidentally exfiltrate data

3. **Trust Maintained**
   - Transparent about data handling
   - User retains control
   - Aligns with privacy-first principle

4. **Audit Trail**
   - Consent events logged
   - Can prove compliance during audits
   - Forensic investigation supported

5. **Revocable**
   - User can switch back to LocalOnly
   - Consent not permanent
   - Respects changing user preferences

### Negative

1. **Workflow Disruption**
   - Extra step to enable Burst mode
   - Prompt may interrupt flow
   - Users might find annoying

2. **Consent Fatigue**
   - Re-consenting every session tedious for frequent users
   - Temptation to make persistent consent
   - Balance security vs. usability

3. **Implementation Complexity**
   - Must track consent state
   - Validate consent before each API call
   - Error handling for missing consent

4. **Potential Bypasses**
   - User might script auto-consent
   - Third-party tools could inject consent
   - Requires secure consent mechanism

5. **UX Challenge**
   - Must design clear consent UI
   - Balance information vs. brevity
   - Different UI for CLI vs. (future) GUI

## Alternatives Considered

### 1. Persistent Consent (Save to Config)

**Description**: Save consent to `~/.acode/config.yml` so user doesn't re-consent

**Rejected Because**:
- Creates "set and forget" mode
- User might forget Burst mode enabled
- Less secure than session-scoped
- Harder to audit ("when did consent happen?")
- Doesn't align with GDPR "ongoing awareness" principle

### 2. Per-Action Consent

**Description**: Prompt for consent before every LLM API call

**Rejected Because**:
- Extremely disruptive to workflow
- Prompt fatigue leads to blind acceptance
- Not practical for interactive AI coding
- Session-scoped consent sufficient

### 3. No Consent (Burst Mode Implicit)

**Description**: Enabling Burst mode implicitly consents to data transmission

**Rejected Because**:
- Not "explicit" consent per GDPR
- User might enable Burst mode without understanding
- Lacks transparency
- Violates privacy-first principle

### 4. Consent with Password

**Description**: Require password entry to grant consent

**Rejected Because**:
- Adds complexity without security benefit
- Password can be scripted
- Doesn't improve consent quality
- Over-engineering for this use case

### 5. Hardware Token Consent

**Description**: Require physical hardware token (YubiKey) for consent

**Rejected Because**:
- Too restrictive for most users
- Hardware dependency unrealistic
   - Expensive (users need to buy tokens)
- Out of scope for software tool
- Over-engineering for consent mechanism

## Related Constraints

- **HC-03**: Consent required for Burst mode
- **HC-01**: No external LLM API in LocalOnly mode (no consent needed)

## Related ADRs

- [ADR-001: No External LLM API by Default](adr-001-no-external-llm-default.md)
- [ADR-002: Three Operating Modes](adr-002-three-operating-modes.md)
- [ADR-005: Secrets Redaction](adr-005-secrets-redaction.md)

## Implementation Notes

### Future Enhancements

- **Per-Provider Consent**: Allow user to consent to OpenAI but not Anthropic
- **Data Minimization**: Show exactly what code will be sent before transmission
- **Consent Dashboard**: UI to view active consents, revoke individually
- **Consent Logging**: Detailed audit log of consent grants/revocations

### Epic 2 Implementation

Consent mechanism will be implemented in Epic 2 (CLI + Agent Orchestration):
- `IConsentManager` interface
- Session-scoped consent token
- Validation before each external API call
- Logging of consent events

See:
- Epic 2: CLI implementation
- Task 002: Configuration contract (consent settings)
- CONSTRAINTS.md: HC-03 enforcement details

## Review History

- **2026-01-03**: Proposed by Security and Legal Teams
- **2026-01-03**: Accepted by Architecture, Security, Product
- **Legal Review**: Confirmed GDPR/CCPA compliance

## Notes

This ADR establishes the foundation for Acode's data transmission consent model. The session-scoped approach balances security (no persistent consent) with usability (no per-action prompts).

If user feedback suggests session-scoped consent is too burdensome, a future ADR could propose a "trusted environment" mode for open-source projects where persistent consent is acceptable. However, default behavior must remain session-scoped.
