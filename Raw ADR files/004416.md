---
ADR #: 0702
Title: Multi-Chain Account Stewardship - Operational Management Across Blockchain Ecosystems
Date: 2025-11-09
Status: Proposed
Authors: UCF Governance / Multi-AI Collaboration (Claude Sonnet 4.5, ChatGPT-5 mini, Gemini)
---

# 1. Context

The XPR Master Identity (ADR-0701) provides users with a unified cryptographic identity across multiple blockchains. However, **creating and managing accounts** on XRPL, Metal Blockchain, Metal L2, and Stellar requires chain-specific operational logic, reserve management, and transaction broadcasting. This ADR defines how the UCF platform acts as a **steward** (not custodian) for multi-chain account lifecycle management.

## Forces at Play

* **Multi-Chain Complexity**: Each blockchain has different account creation requirements, reserve minimums, and operational constraints.
* **User Experience**: Users expect seamless account provisioning without understanding blockchain-specific details.
* **Operational Costs**: Account creation on some chains requires initial funding (XRPL: 10 XRP reserve, Stellar: 1 XLM minimum balance).
* **Trustline Management**: The 3-token ecosystem (EXPLORER, REGEN, GUARDIAN) requires trustlines to be established on XRPL and Stellar.
* **Transaction Broadcasting**: Platform must broadcast user-signed transactions without holding private keys.
* **Cost Recovery**: Platform must manage operational expenses for account creation and transaction fees.
* **Scalability**: System must support thousands of users across multiple chains simultaneously.

## Problem Statement

How do we operationally manage multi-chain account lifecycles (creation, funding, trustline setup, transaction broadcasting) while maintaining the non-custodial architecture established in ADR-0701?

## Constraints

* **Security**: Platform NEVER holds plaintext private keys (see ADR-0701).
* **Financial**: Account creation costs must be managed sustainably (subsidy vs. user payment).
* **Technical**: Must handle chain-specific nuances (XRPL reserves, Stellar sponsorship, EVM gas).
* **Business**: Must support both testnet (free) and mainnet (cost management) environments.
* **Compliance**: Platform activity must be distinguishable from custodial services.

# 2. Decision

We adopt the **Multi-Chain Account Stewardship Model** where the platform algorithmically manages account lifecycles while users retain ultimate ownership through ADR-0701 encrypted key bundles.

## Core Stewardship Principles

### 1. Platform Role: Broadcaster, Not Custodian
- Platform **receives signed transactions** from client
- Platform **broadcasts to blockchain networks**
- Platform **NEVER signs transactions** (no key access)
- Platform **tracks account states** for UX optimization

### 2. Automated Account Provisioning
- Upon XPR Master Identity creation, platform automatically:
  - Creates XRPL account (if reserve funding available)
  - Creates Metal Blockchain account
  - Creates Metal L2 account (EVM-compatible)
  - Creates Stellar account (if minimum balance available)
- All accounts derived from user's master seed (ADR-0701)
- User retains full control via exported keys

### 3. Transparent Cost Management
- **Testnet**: Platform fully subsidizes all costs
- **Mainnet Phase 1 (Early Adopters)**: Platform subsidizes via grant model
- **Mainnet Phase 2 (Scale)**: User pays in fiat, platform converts and funds
- **Mainnet Phase 3 (Mature)**: Pooled reserve system with reclamation on export

## Technical Implementation

### Multi-Chain Account Creation Workflow

```yaml
Trigger Event: XPR Master Identity created (ADR-0701)

Automation Flow:
  1. Retrieve user's derived public addresses from identity service
  2. Check if accounts already exist on each chain
  3. For each chain, execute creation logic:

XRPL Account Creation:
  Prerequisites:
    - User's derived XRPL address (from encrypted bundle metadata)
    - Platform issuer account with sufficient XRP balance
    - Reserve requirement: 10 XRP base + 2 XRP per trustline

  Process:
    1. Check if address already exists on XRPL
    2. If not exists:
       a. Create Payment transaction from platform issuer
       b. Send 16 XRP to user's address (10 base + 6 for 3 trustlines)
       c. Broadcast transaction
       d. Wait for confirmation (1-2 ledgers)
       e. Update database: user.xrpl_account_funded = true
    3. Notify user of successful account creation

  Error Handling:
    - Insufficient platform balance → Queue for manual review
    - Transaction failed → Retry with exponential backoff (max 3 attempts)
    - Address already funded → Skip, mark as complete

Metal Blockchain Account Creation:
  Prerequisites:
    - User's derived Metal address
    - No initial funding required (accounts exist implicitly)

  Process:
    1. Validate derived address format
    2. Record address in database
    3. No on-chain transaction needed (account exists upon first use)
    4. Update database: user.metal_account_created = true

Metal L2 (EVM) Account Creation:
  Prerequisites:
    - User's derived EVM address
    - Platform gas reserve in METAL token

  Process:
    1. Validate EVM address format (0x...)
    2. Optionally send initial gas funding (e.g., 0.1 METAL)
    3. Record address in database
    4. Update database: user.metal_l2_account_funded = true

  Cost Model:
    - Early adopters: Free gas subsidy
    - Scale phase: User pays equivalent fiat for gas funding

Stellar Account Creation:
  Prerequisites:
    - User's derived Stellar address
    - Platform sponsor account with XLM balance
    - Minimum balance: 1 XLM base + 0.5 XLM per trustline

  Process:
    1. Check if address exists on Stellar network
    2. If not exists:
       a. Create CreateAccount operation from platform sponsor
       b. Fund with 2.5 XLM (1 base + 1.5 for 3 trustlines)
       c. Submit transaction to Stellar
       d. Wait for confirmation
       e. Update database: user.stellar_account_funded = true
    3. Optionally use Stellar sponsorship protocol (future enhancement)

  Error Handling:
    - Similar to XRPL logic
```

### Multi-Chain Cost Model

```yaml
Chain-Specific Reserves & Costs:

XRPL:
  Base Reserve: 10 XRP (~$5-15 USD at typical prices)
  Per-Trustline: 2 XRP
  Required Trustlines: 3 (EXPLORER, REGEN, GUARDIAN)
  Total Initial Cost: 16 XRP (~$8-24 USD)

  Platform Funding Options:
    Option A (Grant Model - Phase 1):
      - Platform subsidizes full 16 XRP
      - User receives account ready to use
      - Cost reclaimed if user exports keys (optional)

    Option B (User Payment - Phase 2):
      - User pays $10 USD via fiat payment processor
      - Platform converts to XRP and funds account
      - Excess returned as EXPLORER tokens

    Option C (Pooled Reserve - Phase 3):
      - Platform maintains pooled XRP reserve
      - Allocates 16 XRP to user account
      - Upon key export, user must return 16 XRP to pool
      - Creates economic incentive to stay in ecosystem

Stellar:
  Base Reserve: 1 XLM (~$0.10-0.30 USD)
  Per-Trustline: 0.5 XLM
  Required Trustlines: 3
  Total Initial Cost: 2.5 XLM (~$0.25-0.75 USD)

  Platform Funding:
    - Phase 1-2: Fully subsidized (low cost)
    - Phase 3: May request user contribution if XLM price increases significantly

Metal Blockchain:
  Account Creation: Free (no reserve requirement)
  Initial Gas: Optional (0.01-0.1 METAL for first transactions)

  Platform Funding:
    - Testnet: Free
    - Mainnet: Minimal subsidy or user-paid gas prefund

Metal L2 (EVM):
  Account Creation: Free (exists implicitly)
  Initial Gas: 0.1 METAL (~$0.05-0.50 USD depending on token price)

  Platform Funding:
    - Early users: Subsidized
    - Scale: User pays for gas prefund

Total Platform Cost Per User (Mainnet, Grant Model):
  XRPL: $8-24 USD
  Stellar: $0.25-0.75 USD
  Metal L2: $0.05-0.50 USD
  Total: ~$8.30-25.25 USD per user

Sustainability Strategy:
  - Phase 1 (0-100 users): Full subsidy via grant funding
  - Phase 2 (100-1000 users): Mixed (subsidized + user payment option)
  - Phase 3 (1000+ users): Primarily user-paid with pooled reserve system
  - Revenue from transaction fees (future) offsets operational costs
```

### Trustline Automation

```yaml
Trustlines Required (XRPL & Stellar):
  - EXPLORER token (onboarding reward token)
  - REGEN token (regenerative action rewards)
  - GUARDIAN token (governance participation)

XRPL Trustline Creation:
  Trigger: After account funded and user completes first XRPL verification (ADR-0601)

  Process:
    1. Client-side: User decrypts key bundle (ADR-0701)
    2. Client-side: User signs TrustSet transactions for 3 tokens
       - TrustSet for EXPLORER (issuer: platform XRPL address)
       - TrustSet for REGEN (issuer: platform XRPL address)
       - TrustSet for GUARDIAN (issuer: platform XRPL address)
    3. Client sends signed transactions to platform
    4. Platform broadcasts to XRPL
    5. Platform validates trustlines established
    6. Database update: user.xrpl_trustlines_active = true

  UX Consideration:
    - User shown single "Enable Tokens" button
    - Behind the scenes: 3 signed transactions batched
    - Estimated time: 4-6 seconds (2 ledgers per tx)

Stellar Trustline Creation:
  Similar process to XRPL:
    - ChangeTrust operations for 3 asset types
    - Signed client-side, broadcasted by platform
    - Confirmation tracked in database

  Note: Stellar supports trustline sponsorship (future optimization)
```

### Transaction Broadcasting Service

```yaml
Service: Transaction Broadcaster (Non-Custodial)

Purpose:
  - Receive signed transactions from clients
  - Validate transaction format (not signature - already done client-side)
  - Broadcast to appropriate blockchain network
  - Track transaction status and confirmation
  - Return transaction hash/result to client

API Endpoint: POST /api/transactions/broadcast

Request:
  chain: 'xrpl' | 'metal' | 'metal_l2' | 'stellar'
  signed_transaction: string (chain-specific format)
  transaction_type: 'payment' | 'trustline' | 'contract_call' | 'governance_vote'
  user_metadata: object (optional, for analytics)

Response:
  transaction_hash: string
  status: 'pending' | 'confirmed' | 'failed'
  confirmation_time: number (estimated seconds)
  block_number: number (for EVM chains)
  ledger_index: number (for XRPL/Stellar)

Implementation Logic:
  1. Validate request (authenticated user, rate limits)
  2. Parse signed transaction (chain-specific)
  3. Basic validation (format, not expired, gas/fee present)
  4. Submit to blockchain network RPC endpoint
  5. Store transaction record in database for tracking
  6. Return immediate response with transaction hash
  7. Background job: Poll for confirmation
  8. Webhook/WebSocket: Notify client when confirmed

Security:
  - Rate limiting: 100 transactions per user per hour
  - Size limits: Max 1KB transaction payload
  - Validation: Ensure transaction is actually signed (platform cannot forge)
  - Audit logging: All broadcasts logged for compliance
  - No signature verification (platform doesn't have public keys to verify)

Error Handling:
  - Network unavailable → Queue for retry
  - Transaction rejected (low gas, etc.) → Return error to client
  - Nonce conflict → Advise client to increment nonce
  - Rate limit exceeded → Return 429 status
```

### Database Schema for Account Stewardship

```sql
-- Multi-chain account tracking
CREATE TABLE user_blockchain_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  chain VARCHAR(20) NOT NULL,
  address VARCHAR(100) NOT NULL,
  funded BOOLEAN DEFAULT FALSE,
  funding_tx_hash VARCHAR(100),
  funding_amount DECIMAL(20, 8),
  funding_cost_usd DECIMAL(10, 2),
  trustlines_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  funded_at TIMESTAMP WITH TIME ZONE,

  CONSTRAINT valid_chain CHECK (
    chain IN ('xrpl', 'metal', 'metal_l2', 'stellar', 'xpr')
  ),
  CONSTRAINT unique_user_chain UNIQUE (user_id, chain)
);

CREATE INDEX idx_accounts_user_id ON user_blockchain_accounts(user_id);
CREATE INDEX idx_accounts_chain ON user_blockchain_accounts(chain);
CREATE INDEX idx_accounts_funded ON user_blockchain_accounts(funded);

-- Transaction broadcasting log
CREATE TABLE broadcasted_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  chain VARCHAR(20) NOT NULL,
  transaction_hash VARCHAR(100) NOT NULL,
  transaction_type VARCHAR(50),
  status VARCHAR(20) DEFAULT 'pending',
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  confirmed_at TIMESTAMP WITH TIME ZONE,
  failed_at TIMESTAMP WITH TIME ZONE,
  failure_reason TEXT,
  confirmation_block BIGINT,
  gas_used DECIMAL(20, 8),

  CONSTRAINT valid_chain CHECK (
    chain IN ('xrpl', 'metal', 'metal_l2', 'stellar')
  ),
  CONSTRAINT valid_status CHECK (
    status IN ('pending', 'confirmed', 'failed', 'cancelled')
  )
);

CREATE INDEX idx_tx_user_id ON broadcasted_transactions(user_id);
CREATE INDEX idx_tx_hash ON broadcasted_transactions(transaction_hash);
CREATE INDEX idx_tx_status ON broadcasted_transactions(status);
CREATE INDEX idx_tx_submitted ON broadcasted_transactions(submitted_at DESC);

-- Trustline tracking
CREATE TABLE user_trustlines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  chain VARCHAR(20) NOT NULL,
  asset_code VARCHAR(20) NOT NULL,  -- 'EXPLORER', 'REGEN', 'GUARDIAN'
  issuer_address VARCHAR(100) NOT NULL,
  limit_amount DECIMAL(20, 8),
  established BOOLEAN DEFAULT FALSE,
  establishment_tx_hash VARCHAR(100),
  established_at TIMESTAMP WITH TIME ZONE,

  CONSTRAINT valid_chain CHECK (chain IN ('xrpl', 'stellar')),
  CONSTRAINT valid_asset CHECK (asset_code IN ('EXPLORER', 'REGEN', 'GUARDIAN')),
  CONSTRAINT unique_user_chain_asset UNIQUE (user_id, chain, asset_code)
);

CREATE INDEX idx_trustlines_user ON user_trustlines(user_id);
CREATE INDEX idx_trustlines_established ON user_trustlines(established);

-- Platform operational costs tracking
CREATE TABLE platform_operational_costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  operation_type VARCHAR(50) NOT NULL,  -- 'account_funding', 'gas_subsidy', 'transaction_fee'
  chain VARCHAR(20) NOT NULL,
  amount_native DECIMAL(20, 8),  -- Amount in chain's native currency
  amount_usd DECIMAL(10, 2),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  transaction_hash VARCHAR(100),
  incurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  funding_phase VARCHAR(20),  -- 'subsidy', 'user_paid', 'pooled'

  CONSTRAINT valid_operation CHECK (
    operation_type IN ('account_funding', 'gas_subsidy', 'transaction_fee', 'trustline_setup')
  ),
  CONSTRAINT valid_chain CHECK (
    chain IN ('xrpl', 'metal', 'metal_l2', 'stellar')
  )
);

CREATE INDEX idx_costs_operation ON platform_operational_costs(operation_type);
CREATE INDEX idx_costs_chain ON platform_operational_costs(chain);
CREATE INDEX idx_costs_date ON platform_operational_costs(incurred_at DESC);
```

### Operational Monitoring & Alerts

```yaml
Critical Metrics to Monitor:

Platform Reserve Balances:
  Alert Thresholds:
    XRPL Balance:
      - Warning: < 500 XRP
      - Critical: < 100 XRP
    Stellar Balance:
      - Warning: < 100 XLM
      - Critical: < 50 XLM
    Metal L2 Balance:
      - Warning: < 10 METAL
      - Critical: < 5 METAL

  Actions:
    - Warning: Email platform admins
    - Critical: Pause new account creation, page on-call engineer

Account Creation Success Rate:
  Metric: (Successful creations / Total attempts) per chain
  Target: > 95%
  Alert: < 90% over 1-hour window

Transaction Broadcasting Latency:
  Metric: Time from client submission to blockchain confirmation
  Targets:
    - XRPL: < 5 seconds (p95)
    - Stellar: < 6 seconds (p95)
    - Metal L2: < 15 seconds (p95)
  Alert: p95 > 2x target for 10 minutes

Cost Per User Onboarded:
  Metric: Sum of all funding costs / number of users
  Budget:
    - Phase 1: $25 USD (acceptable for grants)
    - Phase 2: $15 USD (optimization target)
    - Phase 3: $5 USD (user contribution model)
  Alert: Phase average exceeds budget by 20%

Failed Transaction Rate:
  Metric: (Failed broadcasts / Total broadcasts) per chain
  Target: < 5%
  Alert: > 10% over 1-hour window
```

## Integration Points

### With ADR-0701 (XPR Master Identity)

```yaml
Integration Flow:
  1. User creates XPR Master Identity (ADR-0701)
  2. Encrypted key bundle stored with derived addresses
  3. Platform retrieves public addresses (no key access needed)
  4. Platform initiates multi-chain account creation (this ADR)
  5. User receives notification: "Your accounts are ready!"
  6. User can now sign transactions client-side (ADR-0701)
  7. Platform broadcasts signed transactions (this ADR)

Data Sharing:
  - ADR-0701 provides: Derived public addresses per chain
  - ADR-0702 uses: Public addresses for account funding
  - ADR-0702 provides: Account funded status for UX
  - ADR-0701 uses: Funded status to enable transaction UI
```

### With ADR-0601 (XRPL WebAuth)

```yaml
Integration Flow:
  1. User's XRPL account created and funded (this ADR)
  2. User initiates XRPL verification (ADR-0601)
  3. Challenge/verify flow succeeds (ADR-0601)
  4. Verification success triggers trustline automation (this ADR)
  5. User can now receive EXPLORER/REGEN/GUARDIAN tokens

Verification Level Updates:
  - Account created but not verified: Level 1
  - XRPL verified (ADR-0601): Level 2
  - Multi-chain verified: Level 3
  - Solid Pod migration: Level 4
```

### With ADR-0704 (Token-Gated Access Control)

```yaml
Integration Flow:
  - Trustlines established → User can receive governance tokens
  - Token balances → Used for TGAC authorization checks
  - Account verification levels → Gate certain operations
  - Transaction broadcasting → Enables governance voting
```

# 3. Consequences

## Positive Consequences

* **Seamless UX**: Users get multi-chain accounts automatically without blockchain knowledge
* **Non-Custodial Maintained**: Platform never holds keys, only broadcasts signed transactions
* **Cost Transparency**: Clear cost model with phased approach from subsidy to user payment
* **Operational Monitoring**: Comprehensive metrics prevent service degradation
* **Regulatory Clarity**: Distinguishable from custodial services (broadcast-only role)
* **Trustline Automation**: Users don't need to understand trustlines; handled automatically
* **Error Recovery**: Retry logic and alerts ensure high account creation success rate
* **Financial Sustainability**: Phased cost model enables long-term platform viability

## Negative Consequences

* **Operational Costs**: Platform bears $8-25 USD per user in Phase 1 (grant-dependent)
* **Complexity**: Multi-chain automation requires maintaining integrations with 4+ blockchains
* **Failure Modes**: If blockchain network is unavailable, account creation delayed
* **Reserve Lock-Up**: Platform must maintain significant reserves in XRP, XLM, METAL
* **Chain-Specific Bugs**: Each blockchain has unique quirks requiring specialized handling
* **Monitoring Overhead**: Requires 24/7 monitoring of reserve balances and success rates
* **User Expectations**: Automated accounts may create expectation of "free" blockchain access

## Neutral Consequences

* **Database Growth**: Each user adds 4+ records (one per chain) to account tracking tables
* **Transaction Volume**: Platform broadcasts all user transactions (increased RPC costs)
* **Competitive Landscape**: Model differs from most Web3 apps (which use custodial or self-managed wallets)

# 4. Alternatives Considered

## Alternative A: User Self-Funds All Accounts

**Description**: Users must manually fund each blockchain account; platform provides guidance only.

**Pros**:
- Zero platform operational costs
- Users already familiar with self-funding in crypto

**Cons**:
- **Massive UX barrier** (users must acquire XRP, XLM, METAL separately)
- High abandonment rate (70%+ expected based on Web3 onboarding data)
- Contradicts "seamless multi-chain" vision
- Excludes users without existing crypto holdings

**Rejection Reason**: Unacceptable barrier to mainstream adoption; defeats purpose of simplified onboarding.

## Alternative B: Third-Party Account Abstraction (e.g., Alchemy, Biconomy)

**Description**: Use ERC-4337 account abstraction for gasless transactions and account management.

**Pros**:
- Established solutions with proven track record
- Supports gasless transactions (platform pays)
- Smart contract wallet features (social recovery, spending limits)

**Cons**:
- **Only works on EVM chains** (Metal L2, not XRPL or Stellar)
- Vendor dependency and lock-in
- Smart contract deployment cost per user
- Still requires addressing XRPL/Stellar separately
- Not compatible with standard BIP-44 derivation

**Rejection Reason**: Incomplete solution (only 1 of 4 chains); introduces vendor dependency; reserved as potential Metal L2 enhancement only.

## Alternative C: On-Demand Account Creation (Lazy Initialization)

**Description**: Don't create accounts until user actually needs to transact on specific chain.

**Pros**:
- Reduced upfront costs (only fund chains user actually uses)
- More capital-efficient for platform

**Cons**:
- **Delayed UX** (user must wait when first using a chain)
- Complexity in tracking which chains are initialized
- Governance participation gated by account creation step
- User confusion ("Why can't I vote? Oh, I need to activate my account first...")

**Rejection Reason**: Introduces friction at critical moments (governance votes, token claims); better to proactively provision during onboarding when user expects delays.

## Alternative D: Require Initial Fiat Payment from All Users

**Description**: Charge $10 USD during signup to fund all blockchain accounts.

**Pros**:
- Immediate cost recovery; platform breaks even
- Creates "skin in the game" (reduces spam accounts)
- Sustainable from day one

**Cons**:
- **Barrier to entry** for economically disadvantaged users
- Contradicts UCF accessibility principles
- Payment processor fees (15-30% for small amounts)
- Regulatory complexity (payment processing, refunds)
- Reduces experimentation ("I just want to try it, not pay $10")

**Rejection Reason**: Violates UCF's commitment to accessibility; Phase 1 grant model allows initial adoption before transitioning to cost recovery.

# 5. Federation of Labs Promotion Pipeline

| Attribute | Value |
| :--- | :--- |
| **Originating Lab:** | EHDC (Pillar IV) - Ecosystem Health-Derived Currency |
| **Lab Feature/PR:** | Lab 2: Multi-Chain Integration - Account Stewardship Service |
| **Promotion Rationale:** | All Implementation Labs require operational account management across blockchain ecosystems. This pattern enables seamless user onboarding while maintaining non-custodial architecture. The phased cost model (subsidy → user payment → pooled reserve) provides sustainable path from grant-funded pilot to self-sustaining operation. Multi-AI collaboration validated operational feasibility and cost modeling. |
| **Validation Status:** | Testnet validation required before promotion to Accepted |
| **Related ADRs:** | ADR-0701 (XPR Master Identity), ADR-0601 (XRPL WebAuth), ADR-0704 (Token-Gated Access Control) |
| **Multi-AI Review:** | ✅ Claude Sonnet 4.5, ✅ ChatGPT-5 mini, ✅ Gemini (2025-11-09) |

## Validation Milestones

- [ ] Testnet: XRPL account creation and funding (automated)
- [ ] Testnet: Stellar account creation and funding (automated)
- [ ] Testnet: Metal L2 account creation (automated)
- [ ] Testnet: Trustline automation (XRPL, Stellar)
- [ ] Testnet: Transaction broadcasting service (all chains)
- [ ] Testnet: Reserve balance monitoring and alerts
- [ ] Testnet: Cost tracking and reporting
- [ ] Mainnet: Limited beta (10 users, grant-funded)
- [ ] Mainnet: Phased cost model implementation (user payment option)
- [ ] Mainnet: Pooled reserve system (Phase 3)
- [ ] Operational: 95%+ account creation success rate over 30 days
- [ ] Operational: Reserve balances maintained above critical thresholds
- [ ] Status: Promotion to "Accepted"
