---
ADR #: 0701
Title: XPR Master Identity Architecture - Non-Custodial Multi-Chain Key Management
Date: 2025-11-09
Status: Proposed
Authors: UCF Governance / Multi-AI Collaboration (Claude Sonnet 4.5, ChatGPT-5 mini, Gemini)
---

# 1. Context

The Unified Conscious Evolution Framework requires a **unified identity layer** that enables users to interact with multiple blockchain ecosystems (XRPL, Metal Blockchain, Metal L2, Stellar) through a single, user-friendly identity while maintaining complete sovereignty over their cryptographic keys.

## Forces at Play

* **Multi-Chain Complexity**: Users face cognitive overload managing separate wallets, seed phrases, and private keys for each blockchain.
* **Self-Sovereignty Mandate**: UCF's constitutional principles require that users retain ultimate ownership and control of their digital identities and assets.
* **User Experience Gap**: Mainstream adoption requires simplification without compromising security.
* **Regulatory Clarity**: Non-custodial architecture avoids money transmitter licensing and custodial insurance requirements.
* **Interoperability Requirement**: The 3-token ecosystem (EXPLORER, REGEN, GUARDIAN) spans multiple chains and requires seamless cross-chain identity.
* **Migration Path to Self-Custody**: System must support eventual transition to Solid Pod-style full user control.

## Problem Statement

How do we enable users to manage multi-chain identities (XRPL, Metal, Metal L2, Stellar) through a single XPR Master Identity while ensuring:
1. **Zero custodial risk** (platform never controls plaintext keys)
2. **Maximum user sovereignty** (full key export at any time)
3. **Seamless UX** (one login, multi-chain access)
4. **Industry-standard compatibility** (BIP-39/BIP-44 compliance)
5. **Progressive decentralization** (smooth migration to Solid Pods)

## Constraints

* **Technical**: Must use industry-standard key derivation (BIP-39/BIP-44) for cross-wallet compatibility.
* **Security**: All private keys must be encrypted client-side; platform stores only ciphertext.
* **Business**: Must support testnet validation before mainnet deployment across all chains.
* **Compliance**: Non-custodial design must be verifiable for regulatory clarity.
* **Interoperability**: Must integrate with existing ADR-0601 XRPL WebAuth pattern.

# 2. Decision

We adopt the **XPR Master Identity Architecture** with **client-side encrypted key derivation** as the universal UCF standard for multi-chain identity management.

## Core Architecture Principles

### 1. Single Seed, Deterministic Derivation
- Users create a **single 12-word BIP-39 seed phrase** (XPR Master Identity)
- All blockchain-specific keys are **deterministically derived** using BIP-44 standard derivation paths
- Users can recover all chain identities from one seed phrase
- Cross-wallet compatibility ensured through industry standards

### 2. Non-Custodial, Client-Side Encryption
- Private keys are **never stored in plaintext** anywhere
- Encryption occurs **client-side** using a key derived from user passphrase
- Platform stores only **encrypted key bundles** (ciphertext)
- User passphrase is **never transmitted** to servers
- Export available at any time, enabling full sovereignty

### 3. WebAuthn-Enhanced Authentication
- **WebAuthn/Passkeys** provide biometric/hardware-backed authentication
- WebAuthn signature proves device ownership without exposing blockchain keys
- Encrypted key bundle decrypted **in browser memory only**
- Keys purged from memory after transaction signing
- Phishing-resistant, domain-bound credentials

## Technical Implementation

### BIP-39/BIP-44 Derivation Paths

```yaml
Master Seed (12-word BIP-39 phrase):
  - User-facing: "word1 word2 ... word12"
  - Never transmitted to platform
  - User responsibility to backup securely

Derivation Paths (BIP-44 Standard):
  XRPL:    m/44'/144'/0'/0/0
  Metal L2: m/44'/60'/0'/0/0   # EVM-compatible
  Stellar:  m/44'/148'/0'/0/0
  XPR:     m/44'/570'/0'/0/0   # XPR SLIP-44 coin type

Derived Keys:
  - Each chain key independently derived
  - Compromise of one chain does NOT cascade
  - Standard wallet recovery across ecosystems
```

### Encryption Scheme

```yaml
User Passphrase:
  - Entered client-side (never transmitted)
  - Used to derive encryption key via PBKDF2
  - Minimum strength: 12 characters, entropy validation

Key Derivation Function:
  Algorithm: PBKDF2-SHA256
  Iterations: 100,000 (adjustable based on hardware)
  Salt: Cryptographically random, unique per user
  Output: 256-bit AES encryption key

Encryption:
  Algorithm: AES-256-GCM
  Authenticated encryption (integrity + confidentiality)
  Unique IV per encryption operation

Encrypted Key Bundle Structure:
  {
    "version": "1.0",
    "encrypted_data": "<base64-encoded-ciphertext>",
    "salt": "<hex-encoded-salt>",
    "iv": "<hex-encoded-initialization-vector>",
    "auth_tag": "<hex-encoded-authentication-tag>",
    "derivation_metadata": {
      "algorithm": "PBKDF2-SHA256",
      "iterations": 100000,
      "key_size": 256
    }
  }

Plaintext Bundle (decrypted client-side):
  {
    "master_seed": "<12-word-bip39-phrase>",
    "derived_keys": {
      "xrpl": {
        "seed": "sEdS...",
        "address": "rN7n...",
        "public_key": "0302...",
        "derivation_path": "m/44'/144'/0'/0/0"
      },
      "metal_l2": {
        "private_key": "0x1234...",
        "address": "0xABC...",
        "derivation_path": "m/44'/60'/0'/0/0"
      },
      "stellar": {
        "secret": "SBCDEF...",
        "address": "GABC...",
        "derivation_path": "m/44'/148'/0'/0/0"
      },
      "xpr": {
        "private_key": "5KAbc...",
        "address": "xpr123...",
        "derivation_path": "m/44'/570'/0'/0/0"
      }
    },
    "created_at": "2025-11-09T00:00:00Z",
    "version": "1.0"
  }
```

### Authentication Flow (WebAuthn-Enhanced)

```
┌─────────────────────────────────────────────────────────────┐
│                    Step 1: Registration                     │
└─────────────────────────────────────────────────────────────┘

1. User creates account with email/username
2. Platform prompts for WebAuthn registration
3. User authenticates via biometric/hardware key
4. WebAuthn credential stored in secure enclave

┌─────────────────────────────────────────────────────────────┐
│             Step 2: Master Identity Creation                │
└─────────────────────────────────────────────────────────────┘

Client-Side Operations:

5. Generate 12-word BIP-39 seed phrase
6. Display seed phrase to user (CRITICAL: backup required)
7. User confirms backup completion
8. Derive all chain-specific keys using BIP-44 paths
9. User creates strong passphrase (client-side input)
10. Derive encryption key from passphrase (PBKDF2)
11. Encrypt plaintext key bundle with AES-256-GCM
12. Send encrypted bundle to platform for storage

Server-Side Operations:

13. Store encrypted bundle in PostgreSQL
14. No access to plaintext keys (cannot decrypt)
15. Link encrypted bundle to user account

┌─────────────────────────────────────────────────────────────┐
│              Step 3: Login & Key Retrieval                  │
└─────────────────────────────────────────────────────────────┘

1. User authenticates via WebAuthn (biometric)
2. WebAuthn signature proves device ownership
3. Platform retrieves encrypted key bundle
4. User enters passphrase (client-side)
5. Derive decryption key from passphrase
6. Decrypt key bundle in browser memory
7. Keys available for transaction signing
8. Keys purged from memory after use/timeout

┌─────────────────────────────────────────────────────────────┐
│            Step 4: Transaction Signing (Example)            │
└─────────────────────────────────────────────────────────────┘

Client-Side:

1. Application requests transaction signature
2. Retrieve appropriate chain key from decrypted bundle
3. Sign transaction locally in browser
4. Purge key from memory
5. Send signed transaction to platform

Server-Side:

6. Receive signed transaction (no key exposure)
7. Validate transaction format
8. Broadcast to appropriate blockchain
9. Return transaction hash to client
```

### Database Schema Updates

```sql
-- New table for encrypted key bundles
CREATE TABLE xpr_identity_bundles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  encrypted_data TEXT NOT NULL,  -- Base64 encoded ciphertext
  salt VARCHAR(64) NOT NULL,      -- Hex encoded
  iv VARCHAR(32) NOT NULL,        -- Hex encoded
  auth_tag VARCHAR(32) NOT NULL,  -- Hex encoded
  derivation_algorithm VARCHAR(32) DEFAULT 'PBKDF2-SHA256',
  derivation_iterations INTEGER DEFAULT 100000,
  key_size INTEGER DEFAULT 256,
  version VARCHAR(10) DEFAULT '1.0',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_accessed_at TIMESTAMP WITH TIME ZONE,

  -- Security constraints
  CONSTRAINT one_bundle_per_user UNIQUE (user_id),
  CONSTRAINT valid_derivation_algorithm CHECK (
    derivation_algorithm IN ('PBKDF2-SHA256', 'Argon2id')
  ),
  CONSTRAINT valid_iterations CHECK (derivation_iterations >= 100000),
  CONSTRAINT valid_key_size CHECK (key_size IN (256, 512))
);

-- Index for efficient user lookups
CREATE INDEX idx_xpr_bundles_user_id ON xpr_identity_bundles(user_id);

-- Audit log for key bundle access
CREATE TABLE xpr_identity_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  action VARCHAR(50) NOT NULL,  -- 'created', 'accessed', 'exported', 'updated'
  ip_address INET,
  user_agent TEXT,
  success BOOLEAN NOT NULL,
  failure_reason TEXT,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT valid_action CHECK (
    action IN ('created', 'accessed', 'exported', 'updated', 'deleted')
  )
);

CREATE INDEX idx_audit_user_timestamp ON xpr_identity_audit_log(user_id, timestamp DESC);
CREATE INDEX idx_audit_action ON xpr_identity_audit_log(action);

-- Update users table to track identity verification level
ALTER TABLE users ADD COLUMN IF NOT EXISTS identity_verification_level INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS xpr_identity_created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS active_chains TEXT[] DEFAULT '{}';

-- Verification levels: 0=None, 1=XPR Created, 2=XRPL Verified, 3=Multi-Chain Active, 4=Self-Custody
ALTER TABLE users ADD CONSTRAINT valid_verification_level CHECK (
  identity_verification_level BETWEEN 0 AND 4
);
```

### API Endpoints

```yaml
POST /api/identity/create:
  Description: Create XPR Master Identity with encrypted key bundle
  Request:
    encrypted_bundle:
      encrypted_data: string (base64)
      salt: string (hex)
      iv: string (hex)
      auth_tag: string (hex)
      derivation_metadata: object
  Response:
    identity_id: uuid
    created_at: timestamp
    verification_level: 1
  Security:
    - Rate limit: 1 request per user lifetime
    - Audit logged: Yes
    - Authentication: Required (WebAuthn)

GET /api/identity/bundle:
  Description: Retrieve encrypted key bundle for client-side decryption
  Request: None (user authenticated via session)
  Response:
    encrypted_bundle: object (same structure as create)
    created_at: timestamp
    last_accessed_at: timestamp
  Security:
    - Rate limit: 10 requests per minute
    - Audit logged: Yes
    - Authentication: Required (WebAuthn + session)

POST /api/identity/export:
  Description: Export encrypted key bundle for user backup/migration
  Request:
    export_format: 'json' | 'encrypted_file'
    include_metadata: boolean
  Response:
    export_data: object | file_download
    export_timestamp: timestamp
    warning: "Store this securely. Anyone with this file and your passphrase can access all your blockchain identities."
  Security:
    - Rate limit: 3 requests per hour
    - Audit logged: Yes (HIGH priority)
    - Authentication: Required (WebAuthn + re-authentication)
    - Email notification: Sent to user

POST /api/identity/verify-chain:
  Description: Verify ownership of specific chain address (extends ADR-0601)
  Request:
    chain: 'xrpl' | 'metal' | 'stellar' | 'metal_l2'
    verification_proof: object (chain-specific)
  Response:
    verified: boolean
    verification_level: integer (updated)
    active_chains: string[]
  Security:
    - Audit logged: Yes
    - Authentication: Required

DELETE /api/identity/bundle:
  Description: Delete encrypted bundle from platform (user taking full self-custody)
  Request:
    confirmation: "I understand this action cannot be undone"
    exported: boolean (must be true)
  Response:
    deleted: boolean
    final_export: object (one last copy provided)
  Security:
    - Rate limit: Irreversible action
    - Audit logged: Yes (CRITICAL priority)
    - Authentication: Required (WebAuthn + email confirmation code)
    - Requires verification_level >= 3
```

### Client-Side Library Requirements

```javascript
// Recommended libraries for client-side implementation

// Key derivation and BIP-39/BIP-44
import * as bip39 from 'bip39';
import { BIP32Factory } from 'bip32';
import * as ecc from 'tiny-secp256k1';

// Chain-specific key handling
import * as rippleKeypairs from 'ripple-keypairs';      // XRPL
import { Keypair as StellarKeypair } from 'stellar-sdk'; // Stellar
import { Wallet as EthersWallet } from 'ethers';         // Metal L2 (EVM)

// Encryption
import { AES, enc, PBKDF2, lib } from 'crypto-js';

// WebAuthn
import { startRegistration, startAuthentication } from '@simplewebauthn/browser';

// Example: Generate Master Identity
async function generateMasterIdentity(userPassphrase) {
  // 1. Generate BIP-39 mnemonic
  const mnemonic = bip39.generateMnemonic(128); // 12 words

  // 2. Derive seed from mnemonic
  const seed = await bip39.mnemonicToSeed(mnemonic);

  // 3. Create BIP-32 root
  const bip32 = BIP32Factory(ecc);
  const root = bip32.fromSeed(seed);

  // 4. Derive chain-specific keys
  const xrplNode = root.derivePath("m/44'/144'/0'/0/0");
  const metalNode = root.derivePath("m/44'/60'/0'/0/0");
  const stellarNode = root.derivePath("m/44'/148'/0'/0/0");

  // 5. Create plaintext bundle
  const plaintextBundle = {
    master_seed: mnemonic,
    derived_keys: {
      xrpl: {
        seed: rippleKeypairs.deriveKeypair(xrplNode.privateKey.toString('hex')).seed,
        address: rippleKeypairs.deriveAddress(xrplNode.publicKey.toString('hex')),
        derivation_path: "m/44'/144'/0'/0/0"
      },
      metal_l2: {
        private_key: metalNode.privateKey.toString('hex'),
        address: new EthersWallet(metalNode.privateKey.toString('hex')).address,
        derivation_path: "m/44'/60'/0'/0/0"
      },
      // ... stellar, xpr similar structure
    },
    created_at: new Date().toISOString(),
    version: '1.0'
  };

  // 6. Encrypt with user passphrase
  const salt = lib.WordArray.random(32);
  const key = PBKDF2(userPassphrase, salt, {
    keySize: 256/32,
    iterations: 100000
  });

  const iv = lib.WordArray.random(16);
  const encrypted = AES.encrypt(
    JSON.stringify(plaintextBundle),
    key,
    { iv: iv, mode: mode.GCM }
  );

  // 7. Return encrypted bundle for platform storage
  return {
    encrypted_data: encrypted.ciphertext.toString(enc.Base64),
    salt: salt.toString(enc.Hex),
    iv: iv.toString(enc.Hex),
    auth_tag: encrypted.tag.toString(enc.Hex),
    derivation_metadata: {
      algorithm: 'PBKDF2-SHA256',
      iterations: 100000,
      key_size: 256
    }
  };
}
```

## Integration with ADR-0601 (XRPL WebAuth)

The XPR Master Identity architecture **extends and enhances** ADR-0601:

1. **ADR-0601 flow remains unchanged** for XRPL-specific authentication
2. **XPR Master Identity provides the XRPL keys** that are verified via challenge/verify
3. **Verification success updates identity_verification_level** from 1 (XPR created) to 2 (XRPL verified)
4. **Multi-chain expansion** follows the same challenge/verify pattern for each chain
5. **Session tokens include identity context** (verification level, active chains, token holdings)

```yaml
Enhanced Session Token Claims:
  {
    "user_id": "uuid",
    "xpr_identity": "rN7n...",
    "verification_level": 2,
    "active_chains": ["xrpl", "metal_l2"],
    "token_holdings": {
      "EXPLORER": 1000,
      "REGEN": 50,
      "GUARDIAN": 0
    },
    "reputation_score": 850,
    "culture_lab_tier": "contributor",
    "iat": 1699564800,
    "exp": 1699568400
  }
```

# 3. Consequences

## Positive Consequences

* **Zero Custodial Risk**: Platform never controls user funds; no regulatory burden as money transmitter
* **Maximum Sovereignty**: Users can export keys at any time; true self-custody
* **Simplified UX**: One identity, multi-chain access; mainstream adoption barrier removed
* **Industry Standard Compatibility**: BIP-39/BIP-44 compliance enables cross-wallet recovery
* **Security Best Practices**: Client-side encryption, WebAuthn, authenticated encryption (AES-GCM)
* **Progressive Decentralization**: Clear migration path to Solid Pod full self-custody
* **Interoperability**: Seamlessly extends ADR-0601 XRPL WebAuth pattern
* **Auditability**: Comprehensive audit logging without exposing sensitive key material
* **Phishing Resistance**: WebAuthn credentials are domain-bound and cannot be phished

## Negative Consequences

* **Passphrase Management Burden**: Users must securely manage passphrase; loss = permanent key loss
* **Increased Client Complexity**: Browser must handle key derivation, encryption, signing
* **Recovery Complexity**: 12-word seed phrase backup is critical; user education required
* **Performance Overhead**: PBKDF2 100k iterations adds latency (~500ms on average hardware)
* **Browser Compatibility**: Requires modern browsers with WebAuthn and crypto API support
* **No Account Recovery**: If user loses both seed phrase and passphrase, funds are irrecoverable
* **Custom Implementation**: Not using turnkey solutions (Magic, Web3Auth) requires more development

## Neutral Consequences

* **Database Storage Increase**: Encrypted bundles add ~2-4KB per user
* **Client-Side Library Dependencies**: Requires BIP-39, BIP-32, chain-specific crypto libraries
* **User Education Requirement**: Must teach seed phrase security, passphrase strength
* **Multi-Stage Onboarding**: Identity creation requires more steps than traditional signup

# 4. Alternatives Considered

## Alternative A: Custodial Multi-Chain Wallet (Magic, Web3Auth)

**Description**: Use third-party custodial wallet service that manages keys via MPC or delegated key management.

**Pros**:
- Extremely simple UX (email/social login)
- No user passphrase management
- Account recovery available

**Cons**:
- **Violates UCF sovereignty principles** (keys controlled by third party)
- Vendor lock-in (difficult to migrate away)
- Regulatory risk (custodial services face increasing regulation)
- Honeypot risk (centralized key storage)
- Trust assumption (must trust provider's security)

**Rejection Reason**: Fundamentally incompatible with UCF's self-sovereignty mandate.

## Alternative B: Separate Wallets Per Chain (No Master Identity)

**Description**: Users manage independent wallets for each blockchain; no unified identity.

**Pros**:
- Maximum security isolation (one compromise doesn't affect others)
- No custom implementation (use native wallets)
- Users already familiar with this model

**Cons**:
- **Terrible UX** (cognitive overload, 4+ seed phrases to manage)
- Barrier to mainstream adoption
- Complexity in governance (which wallet votes?)
- Difficult cross-chain coordination
- High risk of user error (lost seed phrases)

**Rejection Reason**: Unacceptable UX barrier for mainstream adoption; defeats purpose of unified framework.

## Alternative C: Server-Side MPC with Social Recovery

**Description**: Keys split between user device, platform server, and trusted guardians using multi-party computation.

**Pros**:
- Good balance of security and UX
- Social recovery possible (guardians can help)
- No single point of failure

**Cons**:
- Platform still holds key share (partial custodial risk)
- Complex cryptographic implementation (audit required)
- Dependent on external guardian availability
- Regulatory ambiguity (is platform a custodian?)
- No clear migration path to full self-custody

**Rejection Reason**: Better than Alternative A, but still requires platform trust. Reserved for potential future enhancement (ADR-0705 Recovery Mechanisms).

## Alternative D: Hardware Wallet Requirement

**Description**: Mandate users have Ledger/Trezor hardware wallet for all operations.

**Pros**:
- Maximum security (keys never on internet-connected device)
- Industry-proven security model
- Clear custody model (user owns hardware)

**Cons**:
- **Massive adoption barrier** ($50-200 hardware cost)
- Excludes users without resources
- Still requires separate wallets per chain on most devices
- Complex setup for non-technical users
- Contradicts UCF accessibility principles

**Rejection Reason**: Unacceptable barrier to entry; excludes economically disadvantaged users.

# 5. Federation of Labs Promotion Pipeline

| Attribute | Value |
| :--- | :--- |
| **Originating Lab:** | EHDC (Pillar IV) - Ecosystem Health-Derived Currency |
| **Lab Feature/PR:** | Lab 2: Multi-Chain Integration - XRPL/XPR Master Identity Prototype |
| **Promotion Rationale:** | All Implementation Labs require unified identity across blockchain ecosystems. The 3-token economy (EXPLORER, REGEN, GUARDIAN) spans XRPL, Metal Blockchain, Metal L2, and Stellar. Multi-AI collaboration (Claude Sonnet 4.5, ChatGPT-5 mini, Gemini) validated this architecture as strategically sound and technically feasible. This pattern becomes the universal UCF standard for self-sovereign multi-chain identity. |
| **Validation Status:** | Testnet validation required before promotion to Accepted |
| **Related ADRs:** | ADR-0601 (XRPL WebAuth), ADR-0702 (Multi-Chain Stewardship), ADR-0704 (Token-Gated Access Control) |
| **Multi-AI Review:** | ✅ Claude Sonnet 4.5, ✅ ChatGPT-5 mini, ✅ Gemini (2025-11-09) |

## Validation Milestones

- [ ] Testnet: Master identity creation (BIP-39 seed generation)
- [ ] Testnet: Client-side encryption/decryption (AES-256-GCM)
- [ ] Testnet: Multi-chain key derivation (XRPL, Metal L2, Stellar)
- [ ] Testnet: WebAuthn registration and authentication
- [ ] Testnet: Key export and recovery simulation
- [ ] Testnet: Integration with ADR-0601 XRPL verification
- [ ] Mainnet: Limited beta (10 users)
- [ ] Mainnet: Expanded rollout (100 users)
- [ ] Security: Penetration testing
- [ ] Security: Cryptographic audit
- [ ] Status: Promotion to "Accepted"
