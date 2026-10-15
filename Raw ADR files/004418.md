---
ADR #: 0704
Title: Token-Gated Access Control (TGAC) - Governance Rights via 3-Token Ecosystem
Date: 2025-11-09
Status: Proposed
Authors: UCF Governance / Multi-AI Collaboration (Claude Sonnet 4.5, ChatGPT-5 mini, Gemini)
---

# 1. Context

The Unified Conscious Evolution Framework implements a **3-token ecosystem** (EXPLORER, REGEN, GUARDIAN) to align governance participation with demonstrated value contribution. Token holdings must translate to specific access permissions across all Implementation Labs while maintaining UCF's principles of opt-in membership, transparency, and regenerative incentives.

## Forces at Play

* **Governance Alignment**: Token holdings should reflect genuine participation, not financial speculation.
* **Anti-Plutocracy**: Prevent "token whales" from dominating governance through sheer capital.
* **Regenerative Incentives**: REGEN token rewards ecosystem health contributions (Proof-of-Regeneration).
* **Guardian Oversight**: GUARDIAN token holders provide treasury oversight and emergency governance.
* **Cross-Lab Consistency**: Access control rules must work uniformly across all Implementation Labs.
* **Multi-Chain Reality**: Tokens exist on XRPL and Stellar; verification must span chains.
* **Sybil Resistance**: Prevent single actors from creating multiple identities to gain disproportionate power.
* **Progressive Engagement**: Entry-level participants (EXPLORER) should have meaningful but limited rights.

## Problem Statement

How do we implement a **token-gated access control system** that:
1. Maps token holdings to specific governance permissions
2. Works consistently across multi-chain ecosystem (XRPL, Stellar, Metal L2)
3. Integrates with XPR Master Identity (ADR-0701) verification levels
4. Prevents plutocracy while rewarding genuine contribution
5. Provides clear progression path from EXPLORER → REGEN → GUARDIAN

## Constraints

* **Technical**: Must verify token balances across multiple chains in real-time.
* **Security**: Token holdings cannot be easily faked or manipulated.
* **Business**: Must support both testnet (free token distribution) and mainnet (earned tokens).
* **Compliance**: Must align with securities regulations (tokens as utility, not securities).
* **Interoperability**: Must integrate with ReputationEngine, EthicalAPI, Culture Lab systems.

# 2. Decision

We adopt a **Hybrid Token-Gated Access Control (TGAC)** system combining token holdings with identity verification levels and reputation scoring to determine governance permissions.

## Core TGAC Principles

### 1. Three-Token Utility Model

```yaml
EXPLORER Token:
  Purpose: Onboarding and basic participation
  Issuance: Granted upon identity verification (ADR-0601)
  Typical Holdings: 100-1000 EXPLORER per early adopter
  Utility:
    - Culture Lab discussion access
    - Non-binding governance polls
    - Proposal viewing
    - Community event participation

REGEN Token:
  Purpose: Regenerative action rewards (Proof-of-Regeneration)
  Issuance: Earned through validated ecosystem health contributions
  Typical Holdings: 1-100 REGEN (harder to earn)
  Utility:
    - Binding governance votes
    - Proposal submission
    - ReputationEngine score multiplier
    - Access to regenerative funding pools
    - Validator node operation (future)

GUARDIAN Token:
  Purpose: Treasury oversight and emergency governance
  Issuance: Elected by REGEN holders; requires sustained contribution
  Typical Holdings: 1-10 GUARDIAN (very limited supply)
  Utility:
    - Treasury spending approval (>$10k)
    - Emergency protocol changes
    - Constitution amendment proposals
    - Veto power on malicious proposals
    - DAO treasury multisig signer
```

### 2. Token Holdings as Necessary But Not Sufficient

**Formula**:
```
Access Granted = (Token Holdings >= Threshold)
                 AND (Verification Level >= Required)
                 AND (Reputation Score >= Minimum)
```

**Example**:
```yaml
Action: Submit Governance Proposal

Requirements:
  Token Holdings: >= 10 REGEN
  Verification Level: >= 2 (XRPL verified via ADR-0601)
  Reputation Score: >= 500

Evaluation:
  User A:
    - Holds 20 REGEN ✓
    - Verification Level 2 ✓
    - Reputation 300 ✗
    - Result: DENIED (insufficient reputation despite token holdings)

  User B:
    - Holds 15 REGEN ✓
    - Verification Level 1 ✗
    - Reputation 600 ✓
    - Result: DENIED (must complete XRPL verification)

  User C:
    - Holds 12 REGEN ✓
    - Verification Level 3 ✓
    - Reputation 850 ✓
    - Result: GRANTED
```

### 3. Anti-Plutocracy Mechanisms

```yaml
Quadratic Voting:
  Standard Vote: 1 REGEN = 1 vote
  Quadratic Vote: Voting power = sqrt(REGEN holdings)

  Example:
    User with 100 REGEN:
      Standard: 100 votes
      Quadratic: 10 votes (sqrt(100))

    User with 10,000 REGEN:
      Standard: 10,000 votes (100x more power)
      Quadratic: 100 votes (only 10x more power)

  Impact: Reduces power of large token holders by 90%+

Reputation Weighting:
  Final Vote Weight = Quadratic Token Vote × Reputation Multiplier

  Reputation Multiplier Tiers:
    0-299 points: 0.5x (new users have reduced weight)
    300-599 points: 1.0x (established users)
    600-899 points: 1.2x (trusted contributors)
    900+ points: 1.5x (core community members)

  Example:
    User with 100 REGEN, 850 reputation:
      Token vote: sqrt(100) = 10
      Multiplier: 1.2x
      Final weight: 10 × 1.2 = 12 votes

Vote Decay (Time-Based):
  Fresh votes: 100% weight
  After 90 days: 80% weight (encourages active participation)
  After 180 days: 60% weight
  After 365 days: 40% weight

  Refreshed by: Any governance participation (voting, proposals, discussion)

Maximum Individual Power Cap:
  No single identity can represent > 5% of total governance power

  Enforcement:
    - If user exceeds cap, excess tokens still held but don't count for voting
    - Encourages distribution of tokens to allies (coalition building)
    - Prevents single-point-of-failure governance capture
```

## Technical Implementation

### Multi-Chain Token Balance Verification

```yaml
Service: TokenBalanceAggregator

Purpose: Query user's token holdings across all active chains

Implementation:
  1. Receive request for user's token balances
  2. Retrieve user's multi-chain addresses (from ADR-0701 identity)
  3. Query each chain in parallel:
     - XRPL: GET account trustline balances
     - Stellar: GET account asset balances
     - Metal L2: GET ERC-20 balances (if tokens bridged)
  4. Aggregate total holdings per token type
  5. Cache results (5-minute TTL for performance)
  6. Return aggregated balances

API Endpoint: GET /api/tokens/balances/:user_id

Response:
  {
    "user_id": "uuid",
    "updated_at": "2025-11-09T12:34:56Z",
    "balances": {
      "EXPLORER": {
        "total": "1000.00",
        "by_chain": {
          "xrpl": "800.00",
          "stellar": "200.00"
        }
      },
      "REGEN": {
        "total": "45.50",
        "by_chain": {
          "xrpl": "45.50"
        }
      },
      "GUARDIAN": {
        "total": "0.00",
        "by_chain": {}
      }
    },
    "cache_expires_at": "2025-11-09T12:39:56Z"
  }

Performance Optimization:
  - Background job: Pre-cache balances for active users every 5 minutes
  - WebSocket subscriptions: Real-time updates when balances change
  - Database replica: Token balance snapshots for historical queries

Error Handling:
  - Chain RPC unavailable → Use cached balance (with staleness warning)
  - Conflicting balances → Conservative approach (use minimum)
  - Timeout → Return partial data (with disclaimer)
```

### Permission Matrix

```yaml
Core Permissions by Token Type:

READ_PUBLIC_CONTENT:
  Description: View public proposals, discussions, documentation
  Requirements:
    Tokens: None
    Verification: 0 (anonymous allowed)
    Reputation: 0

PARTICIPATE_CULTURE_LAB:
  Description: Post in Culture Lab discussions, react to content
  Requirements:
    Tokens: >= 1 EXPLORER
    Verification: >= 1 (XPR identity created)
    Reputation: >= 0

VOTE_NON_BINDING:
  Description: Participate in community polls (non-binding)
  Requirements:
    Tokens: >= 10 EXPLORER
    Verification: >= 2 (XRPL verified)
    Reputation: >= 100

VOTE_BINDING:
  Description: Vote on binding governance proposals
  Requirements:
    Tokens: >= 1 REGEN
    Verification: >= 2 (XRPL verified)
    Reputation: >= 300

SUBMIT_PROPOSAL:
  Description: Submit new governance proposal
  Requirements:
    Tokens: >= 10 REGEN
    Verification: >= 2 (XRPL verified)
    Reputation: >= 500

VALIDATE_REGENERATION:
  Description: Validate Proof-of-Regeneration submissions (earn REGEN)
  Requirements:
    Tokens: >= 50 REGEN
    Verification: >= 3 (multi-chain active)
    Reputation: >= 700

APPROVE_TREASURY_SPENDING_SMALL:
  Description: Approve treasury spending < $1,000 USD
  Requirements:
    Tokens: >= 100 REGEN
    Verification: >= 3
    Reputation: >= 800

APPROVE_TREASURY_SPENDING_LARGE:
  Description: Approve treasury spending > $10,000 USD
  Requirements:
    Tokens: >= 1 GUARDIAN
    Verification: >= 3
    Reputation: >= 900

EMERGENCY_GOVERNANCE:
  Description: Emergency protocol changes, malicious proposal veto
  Requirements:
    Tokens: >= 5 GUARDIAN
    Verification: >= 4 (progressive decentralization participant)
    Reputation: >= 950

PROPOSE_CONSTITUTION_AMENDMENT:
  Description: Propose changes to UCF Constitution
  Requirements:
    Tokens: >= 3 GUARDIAN
    Verification: >= 5 (full self-custody)
    Reputation: >= 900
    Additional: Requires co-signers (2 other GUARDIAN holders)
```

### Session Token Claims Structure

```yaml
Enhanced JWT Claims (extends ADR-0601):

{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "xpr_identity": {
    "primary_address": "rN7n7otQDd6FczFgLdlqtyMVrn3NnrcVc",
    "verification_level": 3,
    "active_chains": ["xrpl", "metal_l2", "stellar"]
  },
  "token_holdings": {
    "EXPLORER": 1000.00,
    "REGEN": 45.50,
    "GUARDIAN": 0.00,
    "last_updated": "2025-11-09T12:34:56Z"
  },
  "reputation": {
    "score": 850,
    "tier": "trusted_contributor",
    "multiplier": 1.2
  },
  "permissions": [
    "READ_PUBLIC_CONTENT",
    "PARTICIPATE_CULTURE_LAB",
    "VOTE_NON_BINDING",
    "VOTE_BINDING",
    "SUBMIT_PROPOSAL",
    "VALIDATE_REGENERATION"
  ],
  "governance_power": {
    "raw_token_votes": 45.50,
    "quadratic_votes": 6.75,
    "reputation_weighted_votes": 8.10,
    "capped_at_5_percent": false
  },
  "culture_lab_tier": "contributor",
  "iat": 1699564800,
  "exp": 1699568400
}

Session Token Refresh:
  - Permissions recalculated every 5 minutes
  - Token balances refreshed from chain
  - Reputation score updated
  - If holdings change significantly, user session updated
```

### Permission Enforcement Middleware

```javascript
// Example: Express.js middleware for TGAC

const requirePermission = (permission) => {
  return async (req, res, next) => {
    const user = req.session.user;

    // 1. Decode JWT and extract claims
    const claims = decodeJWT(req.headers.authorization);

    // 2. Check if token is stale (> 5 minutes old)
    const tokenAge = Date.now() - claims.iat * 1000;
    if (tokenAge > 300000) { // 5 minutes
      // Refresh token balances and permissions
      claims = await refreshUserPermissions(user.id);
    }

    // 3. Check if user has required permission
    if (!claims.permissions.includes(permission)) {
      return res.status(403).json({
        error: 'Insufficient permissions',
        required: permission,
        current_permissions: claims.permissions,
        hint: determineWhatUserNeedsForPermission(claims, permission)
      });
    }

    // 4. Log permission check (audit trail)
    await logPermissionCheck({
      user_id: user.id,
      permission: permission,
      granted: true,
      timestamp: new Date()
    });

    // 5. Attach claims to request for downstream use
    req.userClaims = claims;
    next();
  };
};

// Usage in routes
app.post('/api/governance/proposals',
  requirePermission('SUBMIT_PROPOSAL'),
  async (req, res) => {
    // User has verified permission to submit proposal
    const proposal = await createProposal(req.body, req.userClaims);
    res.json(proposal);
  }
);

// Helper: Determine what user needs to gain permission
function determineWhatUserNeedsForPermission(claims, permission) {
  const requirements = PERMISSION_REQUIREMENTS[permission];
  const deficiencies = [];

  const totalREGEN = claims.token_holdings.REGEN;
  const totalGUARDIAN = claims.token_holdings.GUARDIAN;

  if (totalREGEN < requirements.tokens.REGEN) {
    deficiencies.push({
      type: 'tokens',
      token: 'REGEN',
      current: totalREGEN,
      required: requirements.tokens.REGEN,
      shortfall: requirements.tokens.REGEN - totalREGEN
    });
  }

  if (totalGUARDIAN < (requirements.tokens.GUARDIAN || 0)) {
    deficiencies.push({
      type: 'tokens',
      token: 'GUARDIAN',
      current: totalGUARDIAN,
      required: requirements.tokens.GUARDIAN,
      message: 'GUARDIAN tokens are earned through election by REGEN holders'
    });
  }

  if (claims.xpr_identity.verification_level < requirements.verification) {
    deficiencies.push({
      type: 'verification',
      current_level: claims.xpr_identity.verification_level,
      required_level: requirements.verification,
      next_step: getVerificationLevelNextStep(claims.xpr_identity.verification_level)
    });
  }

  if (claims.reputation.score < requirements.reputation) {
    deficiencies.push({
      type: 'reputation',
      current: claims.reputation.score,
      required: requirements.reputation,
      shortfall: requirements.reputation - claims.reputation.score,
      suggestions: getReputationBoostSuggestions()
    });
  }

  return deficiencies;
}
```

### Database Schema for TGAC

```sql
-- Token holdings cache (updated every 5 min)
CREATE TABLE user_token_holdings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_type VARCHAR(20) NOT NULL,
  amount DECIMAL(20, 8) NOT NULL,
  chain VARCHAR(20) NOT NULL,
  last_verified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  block_number BIGINT,

  CONSTRAINT valid_token_type CHECK (
    token_type IN ('EXPLORER', 'REGEN', 'GUARDIAN')
  ),
  CONSTRAINT valid_chain CHECK (
    chain IN ('xrpl', 'stellar', 'metal_l2', 'aggregated')
  ),
  CONSTRAINT unique_user_token_chain UNIQUE (user_id, token_type, chain)
);

CREATE INDEX idx_holdings_user ON user_token_holdings(user_id);
CREATE INDEX idx_holdings_token ON user_token_holdings(token_type);
CREATE INDEX idx_holdings_verified ON user_token_holdings(last_verified_at DESC);

-- Governance power calculations (cached)
CREATE TABLE user_governance_power (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  raw_token_votes DECIMAL(20, 8),
  quadratic_votes DECIMAL(20, 8),
  reputation_multiplier DECIMAL(5, 2),
  final_voting_power DECIMAL(20, 8),
  capped_at_max BOOLEAN DEFAULT FALSE,
  last_calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT one_power_record_per_user UNIQUE (user_id)
);

CREATE INDEX idx_governance_power_user ON user_governance_power(user_id);
CREATE INDEX idx_governance_power_final ON user_governance_power(final_voting_power DESC);

-- Permission grants audit log
CREATE TABLE permission_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  permission VARCHAR(100) NOT NULL,
  granted BOOLEAN NOT NULL,
  denial_reason TEXT,
  user_token_holdings JSONB,
  user_verification_level INTEGER,
  user_reputation_score INTEGER,
  checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_permission_checks_user ON permission_checks(user_id);
CREATE INDEX idx_permission_checks_permission ON permission_checks(permission);
CREATE INDEX idx_permission_checks_time ON permission_checks(checked_at DESC);

-- Governance vote records
CREATE TABLE governance_votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proposal_id UUID NOT NULL REFERENCES governance_proposals(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  vote_choice VARCHAR(20) NOT NULL,  -- 'approve', 'reject', 'abstain'
  voting_power_used DECIMAL(20, 8),
  raw_tokens_held DECIMAL(20, 8),
  reputation_score INTEGER,
  verification_level INTEGER,
  voted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  vote_decay_applied DECIMAL(5, 2) DEFAULT 1.0,

  CONSTRAINT valid_vote_choice CHECK (
    vote_choice IN ('approve', 'reject', 'abstain')
  ),
  CONSTRAINT one_vote_per_user_proposal UNIQUE (user_id, proposal_id)
);

CREATE INDEX idx_votes_proposal ON governance_votes(proposal_id);
CREATE INDEX idx_votes_user ON governance_votes(user_id);
CREATE INDEX idx_votes_time ON governance_votes(voted_at DESC);
```

## Integration with UCF Components

### ReputationEngine Integration

```yaml
Reputation Score Contributions:

Identity Verification:
  - XPR identity created (Level 1): +50 points
  - XRPL verified (Level 2): +100 points
  - Multi-chain active (Level 3): +150 points
  - Progressive decentralization (Level 4): +200 points
  - Full self-custody (Level 5): +250 points

Governance Participation:
  - Vote on binding proposal: +10 points
  - Submit proposal (accepted): +50 points
  - Submit proposal (rejected): -5 points
  - Validate PoR submission: +20 points

Community Contributions:
  - Culture Lab quality post: +5 points
  - Educational content created: +25 points
  - Code contribution merged: +100 points

Token Earning (not buying):
  - Earn 1 REGEN token: +30 points
  - Earn 1 GUARDIAN token: +100 points

Reputation Decay:
  - No activity for 90 days: -10% reputation
  - No activity for 180 days: -25% reputation
  - No activity for 365 days: -50% reputation
```

### EthicalAPI Integration

```yaml
Consent Flows for TGAC:

Token Balance Querying:
  - First time: "Allow UCF to query your token balances on XRPL, Stellar, and Metal L2?"
  - User grants permission (stored in consent database)
  - Future queries automatic (until revoked)

Governance Participation:
  - "Your vote will use [X] voting power based on [Y] REGEN tokens and [Z] reputation score"
  - User confirms understanding before vote cast
  - Transparency in power calculation

Permission Escalation:
  - "You are attempting to submit a proposal, which requires 10 REGEN tokens"
  - "You currently have 8 REGEN. Would you like guidance on earning more?"
  - User guided rather than simply denied

Data Sharing:
  - "Share your token holdings with [External Platform]?"
  - User explicit consent required
  - Revocable at any time
```

### Culture Lab Integration

```yaml
Culture Lab Membership Tiers (TGAC-Based):

Observer (0 EXPLORER):
  - Read-only access
  - Cannot post or react
  - Cannot vote on community matters

Participant (1+ EXPLORER):
  - Can post in discussions
  - Can react to content
  - Can vote in non-binding polls

Contributor (10+ EXPLORER + 1+ REGEN):
  - All Participant rights
  - Can create new discussion threads
  - Can propose Culture Lab initiatives

Trusted Contributor (50+ REGEN + 600+ reputation):
  - All Contributor rights
  - Can moderate discussions (flag spam)
  - Can mentor new participants
  - Culture Lab initiative funding eligibility

Core Member (5+ GUARDIAN + 900+ reputation):
  - All Trusted Contributor rights
  - Can propose Culture Lab governance changes
  - Can represent Culture Lab in cross-lab coordination
  - Emergency moderation powers (ban malicious actors)
```

# 3. Consequences

## Positive Consequences

* **Clear Progression**: Users understand path from EXPLORER → REGEN → GUARDIAN
* **Anti-Plutocracy**: Quadratic voting and reputation weighting prevent token whale dominance
* **Regenerative Alignment**: REGEN tokens must be earned, not bought, aligning incentives
* **Multi-Chain Compatibility**: Works across XRPL, Stellar, Metal L2 seamlessly
* **Transparent Calculations**: Users see exactly how voting power is calculated
* **Sybil Resistance**: Verification levels + reputation prevent fake identity spam
* **Granular Permissions**: 10+ permission levels enable nuanced access control
* **Auditability**: All permission checks logged for governance transparency

## Negative Consequences

* **Complexity**: Multi-factor permission checks (tokens + verification + reputation) harder to understand
* **Performance Overhead**: Real-time multi-chain balance queries add latency
* **Cache Staleness Risk**: 5-minute cache could show outdated balances
* **Token Price Manipulation**: If tokens become tradable, could incentivize speculation
* **Barrier to Entry**: New users with 0 EXPLORER cannot participate (by design, but exclusionary)
* **Calculation Opacity**: Quadratic voting + reputation + decay formula may confuse users
* **Governance Gridlock Risk**: If GUARDIAN tokens too concentrated, could block progress

## Neutral Consequences

* **Database Growth**: Permission check logs accumulate over time (requires archival strategy)
* **API Dependency**: Relies on blockchain RPC endpoints being available
* **Token Distribution**: Requires active token distribution mechanisms (PoR validation, rewards)

# 4. Alternatives Considered

## Alternative A: Simple Token-Gated (No Reputation)

**Description**: Permissions based solely on token holdings; ignore verification levels and reputation.

**Pros**:
- Simplest to implement
- Fastest performance (no complex calculations)
- Easy to understand

**Cons**:
- **Plutocracy risk** (rich token holders dominate)
- No Sybil resistance (multiple identities with small token amounts)
- Doesn't reward genuine contribution (tokens can be bought)
- Contradicts UCF regenerative principles

**Rejection Reason**: Violates UCF's anti-plutocracy and regenerative alignment mandates.

## Alternative B: Reputation-Only (No Tokens)

**Description**: Permissions based solely on reputation score; tokens are purely symbolic.

**Pros**:
- Fully merit-based (reputation must be earned)
- No plutocracy risk
- Strong Sybil resistance

**Cons**:
- **Defeats purpose of 3-token economy** (tokens become meaningless)
- Hard to bootstrap (no tokens to distribute initially)
- Reputation can be gamed (spam contributions for points)
- No economic alignment with ecosystem health

**Rejection Reason**: Undermines EHDC's token-based economic model and regenerative incentives.

## Alternative C: NFT-Based Access (Replace Tokens)

**Description**: Use non-fungible tokens (NFTs) to represent membership tiers; abandon fungible tokens.

**Pros**:
- Clear tier boundaries (you have "Contributor NFT" or you don't)
- No fractional token amounts to calculate
- Tradable membership (secondary markets)

**Cons**:
- **Binary access** (no gradual progression)
- Harder to implement voting power granularity
- NFT speculation could create exclusionary pricing
- Doesn't align with regenerative continuous contribution model

**Rejection Reason**: UCF governance requires nuanced voting power (quadratic, reputation-weighted); binary NFT tiers too coarse.

## Alternative D: Proof-of-Humanity Only (No Tokens/Reputation)

**Description**: One human = one vote, verified via Proof-of-Humanity protocol.

**Pros**:
- Perfect equality (1 person = 1 vote)
- Strong Sybil resistance (biometric verification)
- Simple to understand

**Cons**:
- **Ignores contribution levels** (passive member = core contributor)
- No incentive for regenerative actions
- Privacy concerns (biometric data)
- Centralization risk (Proof-of-Humanity registry)
- Contradicts UCF's opt-in and pseudonymous participation options

**Rejection Reason**: Violates UCF privacy principles and doesn't reward contribution levels.

# 5. Federation of Labs Promotion Pipeline

| Attribute | Value |
| :--- | :--- |
| **Originating Lab:** | EHDC (Pillar IV) - Ecosystem Health-Derived Currency |
| **Lab Feature/PR:** | Lab 2: 3-Token Governance Model - TGAC Implementation |
| **Promotion Rationale:** | All Implementation Labs require consistent access control tied to contribution levels. The 3-token ecosystem (EXPLORER, REGEN, GUARDIAN) provides universal framework for progressive engagement. Hybrid approach (tokens + verification + reputation) prevents plutocracy while enabling nuanced permissions. Multi-AI collaboration validated anti-plutocracy mechanisms and permission granularity. |
| **Validation Status:** | Testnet validation required before promotion to Accepted |
| **Related ADRs:** | ADR-0701 (XPR Master Identity - Verification levels), ADR-0702 (Multi-Chain Stewardship - Token distribution), ADR-0601 (XRPL WebAuth - Verification trigger) |
| **Multi-AI Review:** | ✅ Claude Sonnet 4.5, ✅ ChatGPT-5 mini, ✅ Gemini (2025-11-09) |

## Validation Milestones

- [ ] Testnet: 3-token issuance on XRPL and Stellar
- [ ] Testnet: Multi-chain balance aggregation (< 1 second latency)
- [ ] Testnet: Quadratic voting calculation validated
- [ ] Testnet: Reputation multiplier integration with ReputationEngine
- [ ] Testnet: 20 test users with varying token/reputation levels
- [ ] Testnet: Permission matrix enforcement (all 10+ permissions)
- [ ] Mainnet: Limited beta (50 users)
- [ ] Mainnet: First binding governance vote using TGAC
- [ ] Mainnet: First GUARDIAN election
- [ ] Audit: Security review of permission enforcement logic
- [ ] Audit: Economic analysis of quadratic voting + reputation weighting
- [ ] Status: Promotion to "Accepted"
