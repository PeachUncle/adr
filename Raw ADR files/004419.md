---
ADR #: 0705
Title: Identity Recovery Mechanisms - Social Recovery and Guardian-Based Key Restoration
Date: 2025-11-09
Status: Proposed
Authors: UCF Governance / Multi-AI Collaboration (Claude Sonnet 4.5, ChatGPT-5 mini, Gemini)
---

# 1. Context

The XPR Master Identity architecture (ADR-0701) provides users with full sovereignty over their cryptographic keys through BIP-39 seed phrases and client-side encryption. However, the **fundamental trade-off of self-custody** is that key loss results in permanent loss of access to digital identities and assets. UCF must provide **opt-in recovery mechanisms** that balance sovereignty with practical safety nets for users who experience key loss.

## Forces at Play

* **Irrevocable Key Loss**: Users who lose both seed phrase and passphrase have NO recovery in pure self-custody model.
* **User Behavior Reality**: Studies show 20-30% of crypto users lose access to wallets due to lost keys.
* **Sovereignty vs. Safety**: Recovery mechanisms introduce trust assumptions, potentially compromising pure self-custody.
* **Social Trust**: Users naturally trust certain relationships (family, close friends, community members).
* **Time-Locked Recovery**: Delayed recovery windows allow legitimate users to reclaim access while detecting theft.
* **Regulatory Implications**: Recovery services may trigger custodial regulations if platform controls process.
* **Cross-Phase Compatibility**: Recovery mechanisms must work across all Progressive Decentralization phases (ADR-0703).

## Problem Statement

How do we provide **opt-in identity recovery mechanisms** that:
1. Enable users to restore access after key loss
2. Maintain UCF's sovereignty principles (user controls recovery, not platform)
3. Prevent malicious recovery attacks (impersonation, social engineering)
4. Work across multi-chain identities (XRPL, Stellar, Metal L2)
5. Integrate with Progressive Decentralization phases (ADR-0703)

## Constraints

* **Security**: Recovery mechanisms cannot create attack vectors that compromise non-recovering users.
* **Sovereignty**: Platform cannot unilaterally recover user identities (violates non-custodial mandate).
* **Usability**: Recovery process must be understandable and executable by non-technical users.
* **Privacy**: Recovery mechanisms should not require revealing sensitive personal information publicly.
* **Cost**: Recovery operations should not create prohibitive on-chain transaction costs.

# 2. Decision

We adopt a **tiered, opt-in recovery system** combining Social Recovery Guardians, Time-Locked Recovery, and Emergency Contact mechanisms, with different options available across Progressive Decentralization phases.

## Core Recovery Principles

### 1. Recovery is Opt-In, Never Default

```yaml
Default State:
  - No recovery mechanisms active
  - Pure self-custody (user's responsibility)
  - Key loss = permanent loss (as per blockchain standard)

Opt-In Process:
  - User explicitly chooses recovery mechanism(s)
  - User configures guardians, time locks, emergency contacts
  - User understands trade-offs (trust assumptions)
  - User can disable recovery mechanisms anytime
```

### 2. Multi-Tiered Recovery Options

```yaml
Tier 1: Backup Codes (No External Dependency)
  - User generates backup codes during identity creation
  - 6-8 single-use codes stored offline (printed, password manager)
  - Any backup code can decrypt key bundle
  - No trust assumptions; pure user responsibility
  - Recommended for: All users (Phase 1-4)

Tier 2: Emergency Contact Recovery (Trusted Individual)
  - User designates 1-3 emergency contacts
  - Emergency contact holds encrypted key shard
  - Recovery requires contact to provide shard + user email verification
  - Time-lock: 7-day waiting period before recovery executes
  - Recommended for: Phase 1-2 users (platform stewardship)

Tier 3: Social Recovery Guardians (Distributed Trust)
  - User designates 5-7 trusted individuals as guardians
  - Recovery requires M-of-N guardian approval (e.g., 3-of-5)
  - Each guardian holds encrypted key shard
  - Time-lock: 14-day waiting period before recovery executes
  - Recommended for: Phase 2-3 users (hybrid custody, MPC)

Tier 4: Smart Contract Time-Lock (On-Chain Recovery)
  - User configures on-chain recovery contract (Metal L2, Stellar)
  - Recovery key stored in smart contract with time-lock
  - User can trigger recovery, must wait time-lock period
  - During time-lock, user can cancel if recovery was fraudulent
  - Recommended for: Phase 3-4 users (progressive decentralization, Solid Pods)
```

## Technical Implementation

### Tier 1: Backup Codes

```yaml
Implementation:

During Identity Creation (ADR-0701):
  1. User generates BIP-39 seed phrase (12 words)
  2. User creates passphrase for encryption
  3. Platform offers backup code generation
  4. User opts in (or declines)

Backup Code Generation:
  1. Generate 8 cryptographically random codes (16 characters each)
  2. Derive encryption keys from each backup code using PBKDF2
  3. Encrypt master seed phrase with each key (8 copies)
  4. Display codes to user ONE TIME ONLY
  5. User must save codes offline (print, write down, password manager)
  6. Codes never stored on platform (user responsibility)

Recovery Process:
  1. User initiates "Recover Identity" flow
  2. User enters ONE backup code
  3. Code used to decrypt master seed phrase
  4. Backup code marked as used (single-use)
  5. User creates new passphrase
  6. Identity recovered

Security Characteristics:
  - No trust assumptions (user has full control)
  - Single point of failure (if all codes lost, recovery impossible)
  - Resistant to online attacks (codes never transmitted)
  - Vulnerable to physical theft (if codes not secured)

Database Schema:
  -- No codes stored on platform (user responsibility)
  -- Only track whether user opted in

  ALTER TABLE xpr_identity_bundles
  ADD COLUMN backup_codes_generated BOOLEAN DEFAULT FALSE;
  ADD COLUMN backup_codes_generated_at TIMESTAMP WITH TIME ZONE;
  ADD COLUMN backup_codes_used_count INTEGER DEFAULT 0;
```

### Tier 2: Emergency Contact Recovery

```yaml
Implementation:

Configuration:
  1. User designates 1-3 emergency contacts (email addresses)
  2. Platform generates encrypted key shards using Shamir's Secret Sharing
  3. Each emergency contact receives encrypted shard via secure email
  4. Emergency contact must acknowledge receipt and accept responsibility

Shamir's Secret Sharing:
  - Master seed split into N shares
  - Recovery requires M shares (M-of-N threshold)
  - Example: 2-of-3 (any 2 contacts can recover)
  - Shares encrypted with contact-specific keys

Emergency Contact Responsibilities:
  - Store encrypted shard securely
  - Verify user identity before providing shard
  - Report suspicious recovery requests

Recovery Process:
  1. User initiates "Emergency Recovery" flow
  2. User verifies identity via email (link sent to registered email)
  3. Platform notifies all emergency contacts
  4. User must contact M emergency contacts directly
  5. Contacts provide their shards to platform (or directly to user)
  6. Time-lock period begins (7 days)
  7. During time-lock:
     - User receives daily email reminders
     - Original email account can cancel recovery
  8. After 7 days, shards combined to recreate master seed
  9. User regains access and must create new passphrase

Attack Prevention:
  - Attacker needs to compromise user email + M emergency contacts
  - Time-lock allows legitimate user to cancel fraudulent recovery
  - Emergency contacts verify user identity (phone call, video chat)

Database Schema:
  CREATE TABLE emergency_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_email VARCHAR(255) NOT NULL,
    encrypted_shard TEXT NOT NULL,
    shard_index INTEGER NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_user_contact UNIQUE (user_id, contact_email)
  );

  CREATE TABLE recovery_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recovery_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    time_lock_ends_at TIMESTAMP WITH TIME ZONE,
    shards_collected INTEGER DEFAULT 0,
    shards_required INTEGER NOT NULL,
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,

    CONSTRAINT valid_recovery_type CHECK (
      recovery_type IN ('emergency_contact', 'social_guardian', 'smart_contract')
    ),
    CONSTRAINT valid_status CHECK (
      status IN ('pending', 'time_locked', 'completed', 'cancelled', 'failed')
    )
  );
```

### Tier 3: Social Recovery Guardians

```yaml
Implementation:

Configuration:
  1. User nominates 5-7 trusted guardians (UCF community members)
  2. Guardians must have verification level >= 2 (XRPL verified)
  3. Guardians must have reputation score >= 500
  4. Platform generates N encrypted shards (one per guardian)
  5. Recovery threshold: M-of-N (e.g., 3-of-5, 4-of-7)
  6. Guardians receive notification and must accept role

Guardian Selection Criteria:
  - Trusted relationships (friends, family, community members)
  - Geographically distributed (reduces collusion risk)
  - Diversified relationships (not all from same social circle)
  - High reputation scores (trusted community members)

Guardian Responsibilities:
  - Safeguard encrypted shard
  - Verify user identity before approving recovery
  - Coordinate with other guardians to prevent collusion
  - Report suspicious recovery requests

Recovery Process:
  1. User initiates "Social Recovery" flow
  2. User verifies identity via multi-factor (email + SMS + government ID upload)
  3. Platform notifies all guardians
  4. User must convince M guardians to approve recovery
  5. Guardians verify user identity independently:
     - Video call with user
     - Security questions
     - Coordination among guardians to confirm legitimacy
  6. Each guardian submits approval + encrypted shard
  7. Once M approvals received, time-lock begins (14 days)
  8. During time-lock:
     - All guardians notified of pending recovery
     - Any guardian can flag as suspicious (halts recovery)
     - User receives daily reminders
  9. After 14 days, shards combined to recreate master seed
  10. User regains access and must create new passphrase
  11. Guardians receive notification of successful recovery

Attack Prevention:
  - Requires compromising M guardians simultaneously
  - 14-day time-lock allows detection of fraudulent recovery
  - Guardians coordinate to verify user identity
  - Any guardian can halt recovery if suspicious
  - Geographic distribution reduces collusion risk

Reputation Impact:
  - Guardian approves legitimate recovery: +50 reputation
  - Guardian approves fraudulent recovery: -500 reputation (if proven)
  - Guardian correctly flags suspicious request: +100 reputation

Database Schema:
  CREATE TABLE social_recovery_guardians (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    guardian_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    encrypted_shard TEXT NOT NULL,
    shard_index INTEGER NOT NULL,
    accepted BOOLEAN DEFAULT FALSE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT no_self_guardian CHECK (user_id != guardian_user_id),
    CONSTRAINT unique_user_guardian UNIQUE (user_id, guardian_user_id),
    CONSTRAINT guardian_verified CHECK (
      (SELECT identity_verification_level FROM users WHERE id = guardian_user_id) >= 2
    )
  );

  CREATE TABLE guardian_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recovery_request_id UUID NOT NULL REFERENCES recovery_requests(id) ON DELETE CASCADE,
    guardian_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    approved BOOLEAN NOT NULL,
    verification_notes TEXT,
    flagged_as_suspicious BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_guardian_per_request UNIQUE (recovery_request_id, guardian_user_id)
  );
```

### Tier 4: Smart Contract Time-Lock Recovery

```yaml
Implementation:

Configuration:
  1. User deploys recovery smart contract on Metal L2 or Stellar
  2. User generates recovery key pair (separate from master keys)
  3. Recovery private key encrypted and stored in smart contract
  4. Time-lock period configured (e.g., 30 days)
  5. User holds recovery trigger key (separate 12-word phrase)

Smart Contract Logic (Metal L2 - Solidity):

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract XPRIdentityRecovery {
    address public owner;
    bytes public encryptedRecoveryKey;
    uint256 public timeLockPeriod;
    uint256 public recoveryInitiatedAt;
    bool public recoveryActive;

    event RecoveryInitiated(address indexed owner, uint256 unlockTime);
    event RecoveryCancelled(address indexed owner);
    event RecoveryCompleted(address indexed owner);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    constructor(bytes memory _encryptedRecoveryKey, uint256 _timeLockDays) {
        owner = msg.sender;
        encryptedRecoveryKey = _encryptedRecoveryKey;
        timeLockPeriod = _timeLockDays * 1 days;
        recoveryActive = false;
    }

    function initiateRecovery() external {
        // Anyone can initiate recovery (user with recovery trigger key)
        require(!recoveryActive, "Recovery already active");
        recoveryActive = true;
        recoveryInitiatedAt = block.timestamp;
        emit RecoveryInitiated(owner, block.timestamp + timeLockPeriod);
    }

    function cancelRecovery() external onlyOwner {
        // Only original owner can cancel (proves they still have access)
        require(recoveryActive, "No active recovery to cancel");
        recoveryActive = false;
        recoveryInitiatedAt = 0;
        emit RecoveryCancelled(owner);
    }

    function completeRecovery() external view returns (bytes memory) {
        // After time-lock, return encrypted recovery key
        require(recoveryActive, "No active recovery");
        require(
            block.timestamp >= recoveryInitiatedAt + timeLockPeriod,
            "Time-lock period not yet passed"
        );
        return encryptedRecoveryKey;
    }

    function updateRecoveryKey(bytes memory _newEncryptedRecoveryKey) external onlyOwner {
        encryptedRecoveryKey = _newEncryptedRecoveryKey;
    }
}
```

Recovery Process:
  1. User loses master seed phrase but has recovery trigger key
  2. User calls `initiateRecovery()` on smart contract
  3. Time-lock begins (e.g., 30 days)
  4. Smart contract emits event, user notified
  5. During time-lock:
     - If user finds original keys, call `cancelRecovery()`
     - Otherwise, wait for time-lock to expire
  6. After time-lock, user calls `completeRecovery()`
  7. Smart contract returns encrypted recovery key
  8. User decrypts recovery key using recovery trigger phrase
  9. Recovery key used to recreate master seed phrase
  10. User regains access

Attack Prevention:
  - Attacker must steal recovery trigger key
  - 30-day time-lock gives user time to notice and cancel
  - Original owner can always cancel fraudulent recovery
  - On-chain transparency (all actions logged)

Cost Considerations:
  - Contract deployment: ~$5-20 USD (one-time)
  - Recovery initiation: ~$0.50-2 USD
  - Recovery cancellation: ~$0.50-2 USD
  - Recovery completion: ~$0.50-2 USD

Database Schema:
  CREATE TABLE smart_contract_recovery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chain VARCHAR(20) NOT NULL,
    contract_address VARCHAR(100) NOT NULL,
    time_lock_period_days INTEGER NOT NULL,
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    recovery_initiated_at TIMESTAMP WITH TIME ZONE,
    recovery_cancelled_at TIMESTAMP WITH TIME ZONE,
    recovery_completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT valid_chain CHECK (chain IN ('metal_l2', 'stellar')),
    CONSTRAINT valid_time_lock CHECK (time_lock_period_days BETWEEN 7 AND 90)
  );
```

## Integration with Progressive Decentralization (ADR-0703)

```yaml
Recovery Options by Phase:

Phase 1 (Platform Stewardship):
  Available:
    - Tier 1: Backup Codes (recommended for all)
    - Tier 2: Emergency Contact Recovery
  Rationale: Platform assists with recovery coordination

Phase 2 (Hybrid Custody - Multisig):
  Available:
    - Tier 1: Backup Codes
    - Tier 2: Emergency Contact Recovery
    - Tier 3: Social Recovery Guardians
  Rationale: Multisig naturally supports M-of-N guardian model

Phase 3 (MPC Gradual Handoff):
  Available:
    - Tier 1: Backup Codes
    - Tier 3: Social Recovery Guardians
    - Tier 4: Smart Contract Time-Lock
  Rationale: MPC shares can be recovered via social guardians

Phase 4 (Solid Pod Self-Custody):
  Available:
    - Tier 1: Backup Codes (user manages in Solid Pod)
    - Tier 3: Social Recovery Guardians (coordinated via Solid Pod)
    - Tier 4: Smart Contract Time-Lock (fully on-chain)
  Rationale: Platform-free recovery mechanisms only
```

## User Education & Recovery Testing

```yaml
Mandatory Recovery Drills:

Verification Level Advancement Requirements:
  Level 1 → Level 2:
    - User must verify they've backed up seed phrase
    - User must acknowledge recovery options
    - Optional: Complete recovery drill (test backup code)

  Level 2 → Level 3:
    - User must configure at least one recovery mechanism
    - User must complete recovery drill successfully
    - User receives "Recovery Prepared" badge

Recovery Drill Process:
  1. User initiates "Test Recovery" (sandbox mode)
  2. User pretends they've lost access
  3. User completes chosen recovery mechanism
  4. User successfully recovers test identity
  5. User gains confidence in recovery process
  6. User receives reputation bonus (+25 points)

Educational Materials:
  - "Why Backup Codes Matter" guide
  - "Choosing Recovery Guardians" best practices
  - "Understanding Time-Locks" explainer video
  - "Recovery Drill Walkthrough" tutorial

Recovery Statistics Dashboard:
  - % of users with recovery mechanisms configured
  - Most popular recovery tier
  - Average recovery drill success rate
  - Recovery request volume and success rate
```

## Security Considerations & Attack Vectors

```yaml
Attack Vector Analysis:

Social Engineering (Guardian Impersonation):
  Attack: Attacker impersonates user to guardians
  Mitigations:
    - Guardians verify identity via video call
    - Guardians coordinate to compare verification methods
    - 14-day time-lock allows real user to intervene
    - Reputation penalties for approving fraudulent recovery

Collusion (Multiple Guardians Compromised):
  Attack: Attacker compromises M guardians
  Mitigations:
    - Geographic distribution reduces simultaneous compromise risk
    - High reputation requirement for guardians (harder to compromise)
    - Time-lock allows detection
    - User can designate guardians from different social circles

Emergency Contact Compromise:
  Attack: Attacker compromises user email + M emergency contacts
  Mitigations:
    - Requires multi-factor compromise (email + contacts)
    - Time-lock period (7 days)
    - Email notifications allow cancellation

Smart Contract Exploit:
  Attack: Attacker finds vulnerability in recovery contract
  Mitigations:
    - Security audit before deployment
    - Open-source contract code (community review)
    - Time-lock allows user to cancel
    - User can deploy new contract if vulnerability found

Phishing (Fake Recovery Flow):
  Attack: Attacker creates fake recovery site to steal backup codes
  Mitigations:
    - Domain verification (WebAuthn, SSL certificates)
    - User education on official recovery URLs
    - Platform never asks for backup codes (user enters offline)
```

# 3. Consequences

## Positive Consequences

* **Reduced Key Loss Impact**: Users have safety net if they lose seed phrase
* **User Confidence**: Knowing recovery exists increases adoption (even if unused)
* **Social Trust Leverage**: Utilizes existing trust relationships (guardians)
* **Flexible Options**: Users choose recovery mechanism matching their trust model
* **Time-Lock Security**: Delays allow detection and cancellation of fraudulent recovery
* **Cross-Phase Compatibility**: Recovery mechanisms evolve with decentralization phases
* **Reputation Integration**: Guardians incentivized to act honestly
* **Educational Value**: Recovery drills teach users about key management

## Negative Consequences

* **Trust Assumptions Introduced**: Recovery mechanisms require trusting guardians/contacts
* **Complexity**: Multiple tiers may confuse users about which to choose
* **Guardian Burden**: Requires guardians to accept responsibility and verify identities
* **Social Engineering Risk**: Attackers may impersonate users to guardians
* **Platform Coordination**: Tiers 2-3 require platform to coordinate (until Phase 4)
* **On-Chain Costs**: Smart contract recovery requires gas fees
* **False Sense of Security**: Users may be less careful with keys if recovery exists

## Neutral Consequences

* **Database Growth**: Guardian and recovery request tables accumulate records
* **Support Load**: Recovery requests require manual review and support assistance
* **Time Investment**: Recovery drills and guardian coordination take user time

# 4. Alternatives Considered

## Alternative A: No Recovery Mechanisms (Pure Self-Custody)

**Description**: Provide no recovery options; users entirely responsible for key safety.

**Pros**:
- Simplest architecture (no recovery logic)
- Purest sovereignty model
- No trust assumptions introduced
- No attack vectors via recovery mechanisms

**Cons**:
- **20-30% user key loss rate** (industry standard)
- Barrier to mainstream adoption
- Catastrophic for users who lose keys
- Contradicts UCF's accessibility principles

**Rejection Reason**: Unacceptable user experience; mainstream adoption requires safety nets.

## Alternative B: Platform-Controlled Recovery (Centralized)

**Description**: Platform holds master recovery key; can restore user access on request.

**Pros**:
- Easiest recovery process (user just asks platform)
- High success rate
- No guardian coordination needed

**Cons**:
- **Violates non-custodial architecture** (platform controls keys)
- Single point of failure (platform compromise = all users at risk)
- Regulatory risk (custodial service)
- Contradicts UCF sovereignty principles

**Rejection Reason**: Fundamentally incompatible with ADR-0701 non-custodial mandate.

## Alternative C: Biometric Recovery (Proof-of-Humanity)

**Description**: User's biometric data used to recover keys via zero-knowledge proofs.

**Pros**:
- No guardians needed (user's own biometrics)
- High security (biometrics hard to steal)
- User-friendly (fingerprint/face scan)

**Cons**:
- **Privacy violation** (biometric data storage concerns)
- Centralization risk (biometric database)
- Technology immaturity (ZK biometric proofs experimental)
- Accessibility issues (users without biometric devices)
- Permanent compromise if biometrics leaked (can't change fingerprints)

**Rejection Reason**: Privacy risks and technology immaturity; reserved for future exploration.

## Alternative D: Account Abstraction with Seedless Wallets

**Description**: Use ERC-4337 account abstraction; no seed phrases required; social recovery built-in.

**Pros**:
- State-of-the-art recovery mechanisms
- No seed phrase management burden
- Industry-proven (used by major wallets)

**Cons**:
- **EVM-only** (doesn't work on XRPL or Stellar)
- Requires smart contract deployment per user (cost)
- Vendor dependency (relies on specific infrastructure)
- Not compatible with BIP-39/44 standard (ADR-0701)

**Rejection Reason**: Incomplete solution (only 1 of 4 chains); conflicts with BIP-39 standard; reserved as potential Metal L2 enhancement.

# 5. Federation of Labs Promotion Pipeline

| Attribute | Value |
| :--- | :--- |
| **Originating Lab:** | EHDC (Pillar IV) - Ecosystem Health-Derived Currency |
| **Lab Feature/PR:** | Lab 2: Multi-Chain Integration - Identity Recovery Framework |
| **Promotion Rationale:** | All Implementation Labs require practical recovery mechanisms to reduce key loss risk and improve mainstream adoption. Tiered approach balances sovereignty (user choice) with safety (recovery options). Social recovery leverages UCF community trust networks. Integration with Progressive Decentralization (ADR-0703) ensures recovery mechanisms evolve with platform independence. Multi-AI collaboration validated security considerations and guardian coordination feasibility. |
| **Validation Status:** | Conceptual; Testnet validation required before promotion to Accepted |
| **Related ADRs:** | ADR-0701 (XPR Master Identity - Seed phrase foundation), ADR-0703 (Progressive Decentralization - Phase-specific recovery), ADR-0704 (TGAC - Guardian reputation requirements) |
| **Multi-AI Review:** | ✅ Claude Sonnet 4.5, ✅ ChatGPT-5 mini, ✅ Gemini (2025-11-09) |

## Validation Milestones

**Tier 1 (Backup Codes)**:
- [ ] Testnet: Backup code generation and storage
- [ ] Testnet: 10 users successfully recover using backup codes
- [ ] Mainnet: Recovery drill completion rate > 80%

**Tier 2 (Emergency Contacts)**:
- [ ] Testnet: Emergency contact shard distribution
- [ ] Testnet: 5 users successfully recover via emergency contacts
- [ ] Testnet: Time-lock cancellation validated
- [ ] Mainnet: Zero fraudulent recoveries

**Tier 3 (Social Guardians)**:
- [ ] Testnet: Guardian nomination and acceptance
- [ ] Testnet: 3 users successfully recover via social guardians
- [ ] Testnet: Suspicious recovery correctly flagged by guardian
- [ ] Mainnet: Guardian reputation system operational

**Tier 4 (Smart Contract)**:
- [ ] Testnet: Smart contract deployment and recovery
- [ ] Security audit of recovery contract code
- [ ] Mainnet: 2 users successfully recover via smart contract
- [ ] Mainnet: Zero contract exploits

**Overall**:
- [ ] User education materials published
- [ ] Recovery drill integrated into verification flow
- [ ] Security audit of all recovery mechanisms
- [ ] Zero unauthorized access incidents
- [ ] Status: Promotion to "Accepted"
