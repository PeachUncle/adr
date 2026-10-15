# ADR-003: Airgapped Mode Permanence

## Status

**Accepted** (2026-01-03)

## Context

Airgapped mode is designed for environments with complete network isolation:

1. **Classified Government Systems**: Top Secret/SCI networks with physical air gaps
2. **Critical Infrastructure**: SCADA systems, nuclear plants, power grids
3. **High-Security Corporate**: Financial trading floors, R&D labs
4. **Compliance-Mandated**: Environments where network access is legally prohibited

These environments have a fundamental security requirement: **once a system enters air-gapped mode, it must never establish network connectivity**.

### Security Model

The security model of air-gapped environments assumes:
- **Physical Isolation**: No network cables connected
- **Policy Enforcement**: Software enforces no network usage
- **Audit Trail**: Any attempt to enable network is logged
- **Irreversibility**: Cannot "undo" air-gapped mode programmatically

If Acode allowed switching from Airgapped mode to LocalOnly or Burst mode, it would violate this security model. An attacker who gains code execution could:
1. Switch Acode from Airgapped to Burst mode
2. Exfiltrate data via "legitimate" Acode network calls
3. Bypass air-gap protections

### User Scenarios

**Scenario 1: Classified Development**
- Developer works on classified codebase
- System is permanently air-gapped (no network cable)
- Acode must respect this permanence

**Scenario 2: Temporary Air-Gap (Out of Scope)**
- Developer on airplane without Wi-Fi
- Wants to work offline temporarily
- This is NOT the Airgapped mode use case (should use LocalOnly offline)

## Decision

**Airgapped mode is permanent and irreversible for the lifetime of the Acode process.**

Once Acode is started in Airgapped mode (via `--mode=airgapped` or config), it:
- **Cannot** switch to LocalOnly mode
- **Cannot** switch to Burst mode
- **Cannot** enable network access through any mechanism
- **Must** be restarted to change modes

### Implementation

1. **Mode Transition Validation**:
   - ModeMatrix does not allow transitions out of Airgapped
   - Attempting to switch modes from Airgapped throws an error

2. **Configuration Lock**:
   - Airgapped mode set via CLI flag or config file
   - Cannot be changed at runtime
   - Persisted configuration is ignored if contradicts startup mode

3. **Audit Logging**:
   - Any attempt to switch from Airgapped is logged as critical security event
   - Logs include timestamp, user, attempted target mode

4. **Process Restart Required**:
   - To exit Airgapped mode, user must terminate Acode process
   - Restart with different mode (LocalOnly or Burst)
   - Clear workflow that can be audited

### Contrast with Other Modes

| Transition | Allowed? | Rationale |
|------------|----------|-----------|
| LocalOnly → Burst | ✅ Yes | User consents to cloud access |
| Burst → LocalOnly | ✅ Yes | Reducing permissions is safe |
| Airgapped → LocalOnly | ❌ **No** | Security model violation |
| Airgapped → Burst | ❌ **No** | Security model violation |
| LocalOnly → Airgapped | ⚠️ Discouraged | Requires restart for clarity |

## Consequences

### Positive

1. **Security Model Integrity**
   - Aligns with air-gap security principles
   - Cannot be bypassed programmatically
   - Auditors can verify permanence

2. **Compliance Assurance**
   - Meets classified environment requirements
   - Satisfies zero-trust policies
   - Reduces certification risk

3. **Clear User Contract**
   - "Airgapped means airgapped, period"
   - No ambiguity about network access
   - User cannot accidentally enable network

4. **Audit Trail Clarity**
   - Mode transitions are explicit (process restart)
   - Logs show mode for entire process lifetime
   - Forensic analysis simplified

5. **Attack Surface Reduction**
   - Eliminates "mode switch" attack vector
   - No runtime toggle to exploit
   - Immutable security posture

### Negative

1. **Reduced Flexibility**
   - User cannot "try out" Airgapped mode easily
   - Must restart to change modes
   - Inconvenient for testing

2. **Workflow Disruption**
   - Restarting Acode loses session state
   - Active tasks interrupted
   - May frustrate users who misselect mode

3. **Documentation Burden**
   - Must clearly communicate permanence
   - Requires prominent warnings in UI/docs
   - Support burden for confused users

4. **Testing Complexity**
   - Automated tests must spawn new process per mode
   - Cannot toggle modes in same test run
   - Integration test setup more complex

## Alternatives Considered

### 1. Allow Airgapped → LocalOnly with Confirmation

**Description**: Permit switching from Airgapped to LocalOnly with explicit user confirmation dialog

**Rejected Because**:
- Confirmation dialogs can be automated (UI automation tools)
- Violates security model of air-gapped environments
- Creates "escape hatch" that shouldn't exist
- Classified systems cannot accept "user confirmation" as security control

### 2. Time-Locked Airgapped (1 Hour Minimum)

**Description**: Once Airgapped, must remain for at least 1 hour before switching

**Rejected Because**:
- Arbitrary time limit doesn't address security concerns
- After 1 hour, same vulnerability exists
- Adds complexity without solving problem
- Time-based security is weak security

### 3. All Modes Permanent (No Runtime Switching)

**Description**: Make all mode transitions require process restart

**Rejected Because**:
- Too restrictive for LocalOnly ↔ Burst use case
- User consent workflow (Burst) is legitimate use case
- Reduces usability unnecessarily
- Only Airgapped has security model requiring permanence

### 4. Hardware-Verified Air-Gap

**Description**: Check for physical network interface presence

**Rejected Because**:
- Hardware detection unreliable (virtual machines, USB)
- Out of scope for software tool
- Cannot programmatically verify physical air-gap
- False sense of security

### 5. Reversible with Admin Password

**Description**: Allow Airgapped exit if admin provides password

**Rejected Because**:
- Passwords can be compromised
- Admin might not be available
- Adds authentication complexity
- Defeats purpose of automatic enforcement

## Related Constraints

- **HC-02**: No network access in Airgapped mode
- **HC-07**: Fail-safe to LocalOnly on error (exception: cannot fail-safe FROM Airgapped)

## Related ADRs

- [ADR-002: Three Operating Modes](adr-002-three-operating-modes.md)
- [ADR-001: No External LLM API by Default](adr-001-no-external-llm-default.md)

## Implementation Notes

See:
- Task 001.a: ModeMatrix transition validation
- Future Epic 2: Mode switching validation logic
- CONSTRAINTS.md: HC-02 enforcement details

### Code Example

```csharp
// Pseudo-code for mode transition validation
public bool CanTransitionTo(OperatingMode currentMode, OperatingMode targetMode)
{
    if (currentMode == OperatingMode.Airgapped)
    {
        // Airgapped mode is permanent - no transitions allowed
        AuditLogger.LogCritical("Attempt to exit Airgapped mode blocked",
                                new { currentMode, targetMode });
        return false;
    }

    // LocalOnly ↔ Burst transitions allowed
    return true;
}
```

## Review History

- **2026-01-03**: Proposed by Security Team
- **2026-01-03**: Accepted by Architecture, Security, Compliance
- **Security Rationale**: Permanence is required for classified environment certification

## Notes

This decision is critical for Acode's security posture in high-security environments. Changing this decision would require extensive security review and potentially disqualify Acode from classified deployments.

Users who want temporary offline usage should use LocalOnly mode (which works offline) rather than Airgapped mode.
