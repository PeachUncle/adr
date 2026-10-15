---
ADR #: 0703
Title: Progressive Decentralization Roadmap - Migration Path to Solid Pod Self-Custody
Date: 2025-11-09
Status: Proposed
Authors: UCF Governance / Multi-AI Collaboration (Claude Sonnet 4.5, ChatGPT-5 mini, Gemini)
---

# 1. Context

The XPR Master Identity architecture (ADR-0701) and Multi-Chain Account Stewardship model (ADR-0702) provide a **non-custodial but platform-assisted** approach to multi-chain identity management. However, UCF's ultimate vision is **full user sovereignty** via Solid Pod-style self-custody, where users control both their cryptographic keys and personal data storage without any platform dependency.

## Forces at Play

* **Sovereignty Vision**: UCF's constitutional mandate requires eventual elimination of platform intermediaries.
* **User Experience Gradient**: Immediate full self-custody creates barriers; gradual migration allows learning.
* **Technical Readiness**: Solid Pod infrastructure and multi-chain integration patterns still maturing.
* **Risk Management**: Abrupt migration could result in user key loss; phased approach reduces risk.
* **Platform Sustainability**: Need to balance user sovereignty with operational viability during transition.
* **Ecosystem Maturity**: Early-stage systems benefit from guided experiences; mature systems enable autonomy.
* **Regulatory Evolution**: Progressive decentralization maintains compliance while developing legal frameworks.

## Problem Statement

How do we design a **clear, phased migration path** from platform-assisted multi-chain identity (ADR-0701/0702) to full Solid Pod-style self-custody, ensuring users retain sovereignty at every stage while minimizing risk of key loss or service disruption?

## Constraints

* **User Safety**: Each phase must reduce platform trust while NOT increasing user risk of key loss.
* **Backward Compatibility**: Later phases must not break functionality for users in earlier phases.
* **Technical Feasibility**: Each phase must be implementable with current technology (no vaporware).
* **Economic Sustainability**: Platform must remain operationally viable through all phases.
* **Regulatory Compliance**: Each phase must maintain legal clarity regarding platform's non-custodial role.

# 2. Decision

We adopt a **4-Phase Progressive Decentralization Roadmap** spanning Q1 2026 through Q4 2026, with each phase reducing platform dependency while increasing user sovereignty.

## Four-Phase Architecture

### Phase 1: Platform Stewardship (Q1 2026)
**Status**: Foundation for XPR Master Identity

**Architecture**:
```yaml
Key Management:
  - Client-side encrypted key bundles (ADR-0701)
  - Platform stores ciphertext only
  - User passphrase never transmitted
  - Export available anytime

Transaction Flow:
  - Client signs transactions locally
  - Platform broadcasts only (no signing capability)

Platform Role:
  - Encrypted bundle storage (ciphertext)
  - Transaction broadcasting service
  - Account creation automation (ADR-0702)
  - User education and onboarding

User Sovereignty:
  - Full key ownership via encrypted bundle + export
  - Platform cannot access funds
  - Can leave platform anytime with full key export

Platform Trust Requirements:
  - Platform availability for transaction broadcasting
  - Platform storage reliability for encrypted bundles
  - Platform cannot steal funds (non-custodial)
  - Platform could censor transactions (broadcast refusal)
```

**Validation Milestones**:
- [ ] 100 users onboarded with encrypted key bundles
- [ ] Zero custodial incidents (platform never accesses plaintext keys)
- [ ] 95%+ user satisfaction with onboarding UX
- [ ] Key export successfully tested by 20+ users
- [ ] Transaction broadcasting service uptime > 99.5%

---

### Phase 2: Hybrid Custody with Multisig (Q2 2026)
**Status**: Planned - Reduces platform censorship risk

**Architecture**:
```yaml
Key Management:
  - User holds 2 keys: Mobile key + Backup key
  - Platform holds 1 key: Service key
  - 2-of-3 multisig required for transactions

Multisig Scheme:
  XRPL:
    - MultiSign account setup
    - SignerList with 3 signers
    - Quorum: 2 signatures required

  Stellar:
    - Account thresholds (medium: 2, high: 2)
    - 3 signers with weight 1 each

  Metal L2 (EVM):
    - Gnosis Safe smart contract
    - 2-of-3 multisig wallet
    - User controls 2 keys

Transaction Flow:
  Normal Operations (User + Platform):
    1. User signs transaction with mobile key
    2. Platform auto-signs with service key (convenience)
    3. Transaction requires 2 signatures → Executes

  Platform Offline/Censorship:
    1. User signs with mobile key
    2. User signs with backup key (self-custody override)
    3. Transaction requires 2 signatures → Executes (no platform needed)

  Platform Compromise:
    1. Attacker compromises platform key
    2. User does NOT sign → Transaction cannot execute (still need 2 of 3)

Platform Role:
  - 1-of-3 multisig signer (convenience)
  - Transaction indexing and history
  - User interface and analytics

User Sovereignty:
  - Can execute transactions without platform (using 2 personal keys)
  - Platform cannot censor (user can override)
  - Platform cannot steal (only 1 of 3 keys)

Platform Trust Requirements:
  - Platform provides convenient auto-signing
  - Platform does NOT have unilateral control
  - User must safeguard 2 keys (increased responsibility)
```

**Key Distribution**:
```yaml
Mobile Key:
  - Stored in device secure enclave (iOS Keychain, Android KeyStore)
  - Unlocked via biometric (Face ID, fingerprint)
  - Used for daily transactions

Backup Key:
  - Encrypted with user passphrase
  - Stored in user's password manager or written down
  - Used only if mobile key lost or platform censoring

Platform Service Key:
  - Stored in platform HSM (Hardware Security Module)
  - Automatically signs after user signature verified
  - Can be revoked by user (replaced with 3rd user key)
```

**Migration from Phase 1**:
```yaml
Migration Process:
  1. User initiates "Upgrade to Multisig" in platform UI
  2. Client generates mobile key and backup key
  3. User backs up backup key (verified before proceeding)
  4. Platform creates multisig account on each active chain
  5. User transfers assets from Phase 1 single-sig to Phase 2 multisig
  6. Phase 1 account can be closed or retained as legacy
  7. User verification level updated to Phase 2

Backward Compatibility:
  - Phase 1 users can remain on single-sig indefinitely
  - Phase 2 is opt-in upgrade
  - Both systems supported simultaneously
```

**Validation Milestones**:
- [ ] Multisig implementation tested on all chains (XRPL, Stellar, Metal L2)
- [ ] 20 users successfully migrate from Phase 1 to Phase 2
- [ ] Successful user-only transaction (2 user keys, no platform) demonstrated
- [ ] Platform key revocation process validated
- [ ] User education materials (multisig benefits, key management) published

---

### Phase 3: MPC Gradual Handoff (Q3 2026)
**Status**: Planned - Platform key share diminishes over time

**Architecture**:
```yaml
Key Management:
  - Multi-Party Computation (MPC) threshold signatures
  - User key share: Initially 40%, increases to 80% over time
  - Platform key share: Initially 60%, decreases to 20% over time
  - Threshold: 60% required to sign

MPC Implementation:
  Technology: FROST (Flexible Round-Optimized Schnorr Threshold) or GG20
  Supported Chains:
    - XRPL: Via adapter (convert MPC signature to ECDSA)
    - Stellar: Native support for threshold signatures
    - Metal L2: Smart contract integration

Key Share Evolution:
  Month 1-2:
    - User share: 40%
    - Platform share: 60%
    - User + Platform = 100% (both needed)

  Month 3-4:
    - User share: 55%
    - Platform share: 45%
    - User alone can sign (55% > threshold)
    - Platform alone cannot sign (45% < threshold)

  Month 5-6:
    - User share: 70%
    - Platform share: 30%
    - User has increasing control

  Month 6+:
    - User share: 80%
    - Platform share: 20%
    - User overwhelmingly controls keys
    - Platform provides convenience only

Transaction Flow:
  Early (User share < 60%):
    1. User initiates transaction
    2. User's MPC share computes partial signature
    3. Platform's MPC share computes partial signature
    4. Combined signature submitted to blockchain

  Later (User share > 60%):
    1. User initiates transaction
    2. User's MPC share alone sufficient for signature
    3. Platform's share optional (for analytics/indexing)
    4. User has full signing autonomy

Platform Role:
  - Diminishing key share (60% → 20% over 6 months)
  - Transaction history and analytics
  - Backup coordination (for users who opt in)

User Sovereignty:
  - Increasing unilateral signing power
  - No UX change (seamless transition)
  - Can request accelerated handoff (immediate 80% share)

Platform Trust Requirements:
  - Initially: Platform required for signatures (user < 60%)
  - Later: Platform optional (user > 60%)
  - Eventually: Platform largely decorrelation from security model
```

**MPC Security Model**:
```yaml
Threshold Signature Scheme:
  - t-of-n threshold: 60% of combined shares required
  - User share increases from 40% → 80%
  - Platform share decreases from 60% → 20%
  - User crosses independence threshold at 60%

Key Refresh Protocol:
  - Monthly key refresh (shares regenerated without changing address)
  - User share increases automatically
  - Platform share decreases automatically
  - Seamless to user (no action required)

Compromise Scenarios:
  Early Phase (User 40%):
    - User compromised alone: Funds safe (need 60%)
    - Platform compromised alone: Funds safe (need 60%)
    - Both compromised: Funds at risk (100% > 60%)

  Late Phase (User 70%):
    - User compromised: Funds at risk (70% > 60%)
    - Platform compromised: Funds safe (30% < 60%)
    - User responsibility increases with control
```

**Migration from Phase 2**:
```yaml
Migration Process:
  1. User initiates "Upgrade to MPC" in platform UI
  2. Platform generates initial MPC shares (40% user, 60% platform)
  3. User's mobile key becomes seed for user MPC share
  4. MPC signing infrastructure deployed
  5. User tests MPC signature (with platform)
  6. Assets migrated to MPC-controlled addresses
  7. Monthly automatic key refresh begins

Backward Compatibility:
  - Phase 2 multisig continues to work
  - Phase 3 is opt-in upgrade
  - Users can remain on Phase 2 indefinitely
```

**Validation Milestones**:
- [ ] MPC implementation (FROST or GG20) integrated
- [ ] Testnet validation on all chains
- [ ] Automated key refresh protocol operational
- [ ] 10 users successfully using MPC signing
- [ ] User achieves 60% threshold and successfully signs without platform
- [ ] Security audit of MPC implementation completed

---

### Phase 4: Solid Pod Full Self-Custody (Q4 2026)
**Status**: Planned - Complete sovereignty, platform optional

**Architecture**:
```yaml
Key Management:
  - User's Solid Pod becomes single source of truth
  - Encrypted key vault stored in user's pod
  - Platform reads from user's pod (with permission)
  - User can revoke platform access entirely

Solid Pod Structure:
  pod_root/
    private/
      crypto/
        encrypted_key_vault.json    # ADR-0701 encrypted bundle
        derivation_metadata.json    # BIP-44 paths, etc.
        transaction_history/        # User-owned history
        preferences.json            # User settings

    public/
      identity/
        did.json                    # W3C Decentralized Identifier
        verifiable_credentials/     # VCs for reputation, etc.

    acl/
      platform_permissions.ttl      # What platform can access

Access Control:
  - User grants platform READ-ONLY access to encrypted key vault
  - Platform cannot decrypt (no passphrase)
  - Platform can request user to sign transactions (via WebAuthn prompt)
  - User can revoke access anytime

Transaction Flow:
  1. User visits platform (or any compatible client)
  2. Platform requests read permission from user's Solid Pod
  3. User grants temporary permission
  4. Platform retrieves encrypted key vault (ciphertext)
  5. User enters passphrase client-side (never sent)
  6. Keys decrypted in browser memory
  7. User signs transaction
  8. Platform broadcasts (if user permits)
  9. OR user broadcasts directly via Solid Pod integration

Platform Role:
  - Convenient UI and analytics (optional)
  - No required role in key management
  - User can use ANY compatible client (not locked to platform)

User Sovereignty:
  - Complete data ownership (keys in their pod)
  - Complete control (can revoke platform access)
  - Portable (can switch to different platforms)
  - Censorship-resistant (can broadcast via own infrastructure)

Platform Trust Requirements:
  - ZERO trust required
  - Platform is convenience layer only
  - User can operate entirely independently
```

**W3C Decentralized Identifier (DID) Integration**:
```yaml
DID Document (did.json in user's pod):
  {
    "@context": "https://www.w3.org/ns/did/v1",
    "id": "did:xpr:rN7n7otQDd6FczFgLdlqtyMVrn3NnrcVc",
    "verificationMethod": [
      {
        "id": "did:xpr:rN7n...#key-xrpl",
        "type": "EcdsaSecp256k1VerificationKey2019",
        "controller": "did:xpr:rN7n...",
        "blockchainAccountId": "xrpl:rN7n7otQDd6FczFgLdlqtyMVrn3NnrcVc"
      },
      {
        "id": "did:xpr:rN7n...#key-metal",
        "type": "EcdsaSecp256k1VerificationKey2019",
        "controller": "did:xpr:rN7n...",
        "blockchainAccountId": "eip155:1:0xABC..."
      },
      {
        "id": "did:xpr:rN7n...#key-stellar",
        "type": "Ed25519VerificationKey2020",
        "controller": "did:xpr:rN7n...",
        "blockchainAccountId": "stellar:GABC..."
      }
    ],
    "service": [
      {
        "id": "did:xpr:rN7n...#solid-pod",
        "type": "SolidPodStorage",
        "serviceEndpoint": "https://user-pod.solidcommunity.net/"
      }
    ]
  }

Verifiable Credentials (stored in pod):
  - ReputationEngine score attestations
  - Token holdings proofs
  - Governance participation history
  - Culture Lab membership tier
  - Portable across platforms
```

**Migration from Phase 3**:
```yaml
Migration Process:
  1. User creates Solid Pod (platform provides guided setup)
  2. User's encrypted key bundle migrated to pod
  3. User's transaction history exported to pod
  4. User configures access control (which apps can read)
  5. Platform switches to "read from pod" mode
  6. User validates transactions still work
  7. User can optionally delete keys from platform (full independence)

Backward Compatibility:
  - Phase 3 MPC continues to work
  - Phase 4 is opt-in migration
  - Platform supports both models simultaneously
```

**Validation Milestones**:
- [ ] Solid Pod integration implemented
- [ ] W3C DID specification adopted for XPR identities
- [ ] Verifiable Credentials for reputation/governance implemented
- [ ] 5 users successfully migrate to Solid Pod self-custody
- [ ] User successfully uses multiple platforms with single Solid Pod
- [ ] User successfully revokes platform access and operates independently
- [ ] Public documentation: "How to fully exit Brother Nature platform"

---

## Cross-Phase Feature Matrix

```yaml
Feature Comparison Across Phases:

Key Storage:
  Phase 1: Platform (encrypted)
  Phase 2: Platform (encrypted) + User (2 keys)
  Phase 3: MPC (shares with platform)
  Phase 4: User Solid Pod (100% ownership)

Transaction Signing:
  Phase 1: User only (client-side)
  Phase 2: 2-of-3 multisig (user 2 keys OR user 1 + platform)
  Phase 3: MPC threshold (starts joint, becomes user-only)
  Phase 4: User only (via pod-stored keys)

Platform Dependency:
  Phase 1: Required for broadcasting
  Phase 2: Optional (user can override)
  Phase 3: Diminishing (user gains independence at 60%)
  Phase 4: Zero (platform fully optional)

Censorship Resistance:
  Phase 1: Low (platform can refuse broadcast)
  Phase 2: Medium (user can use 2 personal keys)
  Phase 3: High (user has majority control)
  Phase 4: Maximum (user broadcasts independently)

User Responsibility:
  Phase 1: Moderate (backup seed phrase + passphrase)
  Phase 2: High (manage 3 keys)
  Phase 3: High (safeguard MPC share as it grows)
  Phase 4: Maximum (full self-custody)

Ease of Use:
  Phase 1: Easiest (minimal key management)
  Phase 2: Moderate (multisig complexity abstracted)
  Phase 3: Easiest (no UX change despite increased control)
  Phase 4: Moderate (Solid Pod setup required)

Recovery Options:
  Phase 1: Seed phrase + passphrase
  Phase 2: Any 2 of 3 keys
  Phase 3: User MPC share (+ social recovery option)
  Phase 4: Seed phrase + Solid Pod backup
```

## Governance Implications

```yaml
Verification Levels Updated:

Level 0: Anonymous
  - No XPR identity
  - Read-only access

Level 1: XPR Identity Created (Phase 1)
  - Encrypted bundle created
  - Can receive EXPLORER tokens
  - Basic governance participation

Level 2: XRPL Verified (Phase 1 + ADR-0601)
  - Challenge/verify completed
  - Can vote on proposals
  - Can hold REGEN tokens

Level 3: Multi-Chain Active (Phase 1-2)
  - Accounts on all chains active
  - Can hold GUARDIAN tokens
  - Treasury oversight participation
  - May include Phase 2 multisig upgrade

Level 4: Progressive Decentralization Participant (Phase 3)
  - MPC threshold signatures
  - Enhanced reputation multiplier (1.2x)
  - Advanced governance rights

Level 5: Full Self-Custody (Phase 4)
  - Solid Pod migration complete
  - Maximum reputation multiplier (1.5x)
  - Emergency governance powers
  - Constitution amendment proposals
```

# 3. Consequences

## Positive Consequences

* **Clear Migration Path**: Users understand journey from guided onboarding to full sovereignty
* **Risk Mitigation**: Phased approach prevents abrupt key loss; users learn gradually
* **Regulatory Clarity**: Each phase maintains non-custodial architecture with decreasing platform role
* **Competitive Advantage**: No other ecosystem offers this level of progressive sovereignty
* **User Education**: Phases align with increasing user crypto literacy
* **Platform Sustainability**: Platform remains valuable (UX, analytics) even in Phase 4
* **True Decentralization**: Achieves UCF's sovereignty vision without compromising UX
* **Backward Compatibility**: Users can remain in any phase indefinitely (no forced upgrades)

## Negative Consequences

* **Development Complexity**: Must maintain 4 different architecture phases simultaneously
* **User Confusion Risk**: Some users may not understand phase differences
* **Testing Overhead**: Each phase requires comprehensive security audits
* **MPC Implementation Risk**: Phase 3 requires advanced cryptography (FROST/GG20)
* **Solid Pod Dependency**: Phase 4 success depends on Solid ecosystem maturity
* **Support Complexity**: Platform must support users across all phases
* **Migration Fatigue**: Users may resist upgrading through multiple phases

## Neutral Consequences

* **Phased Timeline**: Full sovereignty not achieved until Q4 2026 (9-month journey)
* **Ecosystem Fragmentation**: Users distributed across phases creates complexity
* **Documentation Volume**: Each phase requires comprehensive guides

# 4. Alternatives Considered

## Alternative A: Immediate Full Self-Custody (No Platform Stewardship)

**Description**: Skip Phase 1-3; require users to use Solid Pods from day one.

**Pros**:
- Maximum sovereignty immediately
- No platform trust required
- Simplest architecture (one model only)

**Cons**:
- **Massive UX barrier** (Solid Pod setup complex for non-technical users)
- Abandonment rate likely > 80%
- Excludes mainstream adoption
- No gradual learning curve

**Rejection Reason**: Contradicts UCF's accessibility principles; creates barrier to entry too high for current Web3 maturity.

## Alternative B: No Migration Path (Stay on Phase 1 Forever)

**Description**: Keep encrypted bundle + platform broadcasting as permanent architecture.

**Pros**:
- Simplest development (one architecture maintained)
- Users already comfortable with model
- Proven UX (similar to Web2 password managers)

**Cons**:
- **Violates UCF sovereignty vision**
- Platform dependency permanent
- Censorship risk remains
- No path to true decentralization

**Rejection Reason**: Fundamentally incompatible with UCF's constitutional mandate for user sovereignty.

## Alternative C: Skip MPC Phase, Jump to Solid Pods

**Description**: Phase 1 → Phase 2 (multisig) → Phase 4 (Solid Pods), skip MPC.

**Pros**:
- Simpler (one less phase)
- MPC complex cryptography avoided
- Faster to full sovereignty

**Cons**:
- Large jump from multisig to Solid Pods (user readiness gap)
- MPC provides smoothest UX during transition (Phase 3 advantage lost)
- Less gradual learning curve

**Rejection Reason**: MPC Phase 3 provides the **smoothest user experience** during critical transition from platform dependency to independence. The gradual key share increase (40% → 80%) happens automatically without user action, while multisig → Solid Pod requires manual migration.

## Alternative D: Different Timeline (Slower or Faster)

**Description**: Extend timeline to 18-24 months OR compress to 3-6 months.

**Pros (Slower)**:
- More time for user education
- Less development pressure
- More gradual adoption

**Cons (Slower)**:
- Delays sovereignty achievement
- Competitive disadvantage (other projects may leapfrog)

**Pros (Faster)**:
- Quicker to full decentralization
- Less legacy system maintenance

**Cons (Faster)**:
- Increased user confusion
- Higher risk of key loss incidents
- Insufficient time for security audits

**Rejection Reason**: 9-month timeline (Q1-Q4 2026) balances urgency with safety. Each phase gets ~3 months for development, testing, and user migration.

# 5. Federation of Labs Promotion Pipeline

| Attribute | Value |
| :--- | :--- |
| **Originating Lab:** | EHDC (Pillar IV) - Ecosystem Health-Derived Currency |
| **Lab Feature/PR:** | Lab 2: Multi-Chain Integration - Progressive Decentralization Architecture |
| **Promotion Rationale:** | UCF's constitutional vision requires ultimate user sovereignty while maintaining practical usability during ecosystem maturity. This phased roadmap provides clear path from platform-assisted onboarding (necessary for mainstream adoption) to full Solid Pod self-custody (constitutional mandate). Multi-AI collaboration validated approach as strategically sound. |
| **Validation Status:** | Conceptual; Phase 1 testnet validation in progress |
| **Related ADRs:** | ADR-0701 (XPR Master Identity - Phase 1 foundation), ADR-0702 (Multi-Chain Stewardship - Phase 1 operations), ADR-0705 (Identity Recovery - Cross-phase mechanisms) |
| **Multi-AI Review:** | ✅ Claude Sonnet 4.5, ✅ ChatGPT-5 mini, ✅ Gemini (2025-11-09) |

## Validation Milestones

**Phase 1 (Q1 2026)**:
- [ ] 100 users onboarded
- [ ] Zero custodial incidents
- [ ] Key export validated
- [ ] 95%+ user satisfaction

**Phase 2 (Q2 2026)**:
- [ ] Multisig on all chains
- [ ] 20 users migrated
- [ ] User-only transaction (no platform) validated
- [ ] Platform key revocation tested

**Phase 3 (Q3 2026)**:
- [ ] MPC implementation audited
- [ ] 10 users on MPC
- [ ] User achieves 60% threshold
- [ ] Automated key refresh operational

**Phase 4 (Q4 2026)**:
- [ ] Solid Pod integration complete
- [ ] 5 users fully self-custodial
- [ ] W3C DID/VC implementation
- [ ] Platform independence validated

**Overall**:
- [ ] Each phase security audited
- [ ] Migration guides published
- [ ] Zero key loss incidents
- [ ] Status: Promotion to "Accepted"
