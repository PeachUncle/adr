# ADR-002: Three Operating Modes

## Status

**Accepted** (2026-01-03)

## Context

Acode needs to serve multiple user personas with different security, privacy, and capability requirements:

1. **Individual Developers**: Want privacy but occasionally need cloud AI power
2. **Enterprise Users**: Strict data control policies, compliance requirements
3. **Classified Environments**: Air-gapped networks, zero external connectivity
4. **Open Source Contributors**: Public code, less privacy concern
5. **Security Researchers**: Need transparency and auditability

A single operating mode cannot satisfy all these requirements. Too restrictive frustrates users who consent to cloud usage. Too permissive violates enterprise security policies.

### Requirements

- **Clear Security Posture**: Users must understand exactly what network access is permitted
- **Compliance Alignment**: Modes must map to compliance requirements (GDPR, SOC2, etc.)
- **No Ambiguity**: Each mode's constraints must be unambiguous
- **Fail-Safe**: Default mode must be most restrictive
- **Simple Mental Model**: Users should easily understand mode differences

## Decision

**Acode will have exactly three operating modes: LocalOnly, Burst, and Airgapped.**

### Mode Definitions

#### LocalOnly (Default)

**Scope**: Local network only (localhost + LAN)
**Primary Use Case**: Daily development with privacy guarantees
**Network Access**:
- ✅ Localhost (127.0.0.1, ::1) - for Ollama, vLLM
- ✅ LAN (192.168.x.x, 10.x.x.x) - for local infrastructure
- ❌ External network - blocked
- ❌ External LLM APIs - hard blocked (HC-01)

**Model Providers**: Ollama, vLLM, local inference only

#### Burst

**Scope**: External network with consent
**Primary Use Case**: Complex tasks requiring powerful cloud models
**Network Access**:
- ✅ Localhost
- ✅ LAN
- ✅ External network - with consent (HC-03)
- ⚠️ External LLM APIs - with per-session consent

**Model Providers**: Ollama, vLLM, plus OpenAI, Anthropic, Google AI (with consent)

#### Airgapped

**Scope**: No network access whatsoever
**Primary Use Case**: Classified environments, air-gapped systems
**Network Access**:
- ❌ Localhost - blocked (HC-02)
- ❌ LAN - blocked
- ❌ External network - blocked
- ❌ All network - completely disabled

**Model Providers**: Pre-loaded embeddings, no live inference (future capability)

### Why Exactly Three?

1. **Two Modes Insufficient**: LocalOnly + External doesn't serve air-gapped users
2. **Four+ Modes Too Complex**: Granular modes (e.g., "LAN only", "Localhost only") create confusion
3. **Tri-Modal Clarity**: Three modes map to clear user intent:
   - "Keep it local" → LocalOnly
   - "I consent to cloud" → Burst
   - "Absolutely no network" → Airgapped
4. **Industry Patterns**: Matches security level classifications (Unclassified, Confidential, Secret/Top Secret)

### Implementation

- **Enum**: `OperatingMode { LocalOnly = 0, Burst = 1, Airgapped = 2 }`
- **Mode Matrix**: 3 modes × 26 capabilities = 78 permission entries
- **Default**: LocalOnly (enum value 0)
- **Transitions**: LocalOnly ↔ Burst allowed, Airgapped is permanent (ADR-003)

## Consequences

### Positive

1. **Clear Security Boundaries**
   - Each mode has unambiguous network permissions
   - No "gray areas" in constraints
   - Auditors can verify compliance per mode

2. **Serves All User Personas**
   - Privacy-conscious: LocalOnly
   - Pragmatic: Burst when needed
   - Classified: Airgapped

3. **Simple Mental Model**
   - Three options easy to understand
   - Modes named for their primary characteristic
   - Documentation can be concise

4. **Compliance Mapping**
   - LocalOnly: GDPR compliant by default
   - Burst: Consent-based (GDPR Article 7)
   - Airgapped: Classified system compliant

5. **Future-Proof**
   - Can add capabilities within modes
   - Mode structure stable even as features grow
   - Clear extension point for new constraints

### Negative

1. **Cannot Satisfy Edge Cases**
   - Some users might want "LAN only, no localhost"
   - No mode for "some external APIs but not others"
   - Trade granularity for simplicity

2. **Burst Mode Ambiguity**
   - "Burst" name doesn't obviously mean "cloud with consent"
   - Could be confused with performance/speed
   - Requires user education

3. **Airgapped Mode Limitations**
   - No live model inference at all
   - Severely limited functionality
   - May not be viable until pre-loaded models supported

4. **Migration Complexity**
   - Switching modes mid-session requires workflow restart
   - Cannot gradually escalate permissions
   - All-or-nothing within each mode

## Alternatives Considered

### 1. Two Modes (Local vs. Cloud)

**Description**: LocalOnly (default) and Cloud (all external)

**Rejected Because**:
- Doesn't serve air-gapped users
- "Cloud" mode too broad (all external access)
- Doesn't distinguish between localhost and external
- Misses enterprise LAN use cases

### 2. Four Modes (None, Localhost, LAN, External)

**Description**: Granular network scoping

**Rejected Because**:
- Too complex for average user
- Hard to name modes clearly
- Doesn't align with security models
- Over-engineering for current needs

### 3. Permission-Based (No Modes)

**Description**: Per-capability permissions (user grants each individually)

**Rejected Because**:
- Requires complex permission UI
- Too many decisions for user
- Doesn't map to compliance requirements
- Hard to audit ("which permissions are enabled?")

### 4. Five Modes (Add "LAN Only")

**Description**: LocalOnly, LAN, Burst, Airgapped, Offline

**Rejected Because**:
- Overlap between LocalOnly and LAN
- "Offline" redundant with Airgapped
- Diminishing returns on granularity
- Violates "as simple as possible" principle

### 5. Single Mode (Always LocalOnly)

**Description**: No mode selection, always most restrictive

**Rejected Because**:
- Doesn't serve users who consent to cloud
- Eliminates legitimate Burst use cases
- Too restrictive for open-source projects
- Reduces Acode utility unnecessarily

## Related Constraints

- **HC-01**: No external LLM API in LocalOnly mode
- **HC-02**: No network access in Airgapped mode
- **HC-03**: Consent required for Burst mode
- **HC-07**: Fail-safe to LocalOnly on error

## Related ADRs

- [ADR-001: No External LLM API by Default](adr-001-no-external-llm-default.md)
- [ADR-003: Airgapped Mode Permanence](adr-003-airgapped-permanence.md)
- [ADR-004: Burst Mode Consent](adr-004-burst-mode-consent.md)

## Implementation Notes

See:
- Task 001.a: Mode Matrix with 78 mode-capability entries
- `src/Acode.Domain/Modes/OperatingMode.cs`: Enum definition
- `src/Acode.Domain/Modes/ModeMatrix.cs`: Permission lookups

## Review History

- **2026-01-03**: Proposed by Architecture Team
- **2026-01-03**: Accepted by Security, Product, Engineering
- **Rationale**: Tri-modal design strikes balance between simplicity and flexibility

## Notes

This ADR intentionally limits the number of modes to three. Future feature requests for "LAN only" or "specific API only" modes should be rejected unless compelling evidence suggests the tri-modal model is fundamentally insufficient.

If a fourth mode is ever added, this ADR should be superseded with a new ADR explaining why three modes proved inadequate.
