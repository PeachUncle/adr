# ADR-005: Secret Management Encryption Architecture

## Status
Revised (supersedes previous version)

## Context
Following ADR-002, ADR-003, and ADR-004, we need to define a comprehensive encryption architecture that ensures end-to-end encryption (E2EE) while maintaining flexibility in authentication methods and supporting technical clients. Based on implementation experience and industry standards review, we've revised our approach to key management and identity.

## Decision

### 1. Core Encryption Strategy

#### 1.1 Key Hierarchy
This ADR builds on ADR-009 (Key Derivation Architecture) and crypto-spec.md:

1. Authentication & Protection Layer
   - User Credentials → Master Key (PBKDF2)
   - Used for both authentication and key protection
   - Rotates with password changes
   - Protected in memory, never stored

2. Identity Layer
   - Long-term stable KeyPair
   - Protected by Master Key
   - Revocation rather than rotation
   - Trust anchor for system

3. Data Protection Layer
   - Random DEK generation
   - Envelope-based distribution
   - Support for authorized rotation

#### 1.2 Authentication Layer (Pluggable)
* Support for OAuth/OIDC providers (e.g., Keycloak, Zitadel)
* Enterprise SSO integration
* Handles user authentication, MFA, session management
* Master Key derivation for authentication proof
* Independent from key protection layer

#### 1.3 Encryption Layer
* Independent encryption credentials
* Client-side encryption/decryption using crypto-spec structures
* Zero-knowledge architecture - server never has access to:
  - Plaintext secrets
  - Encryption keys
  - Private keys

### 2. Key Management

#### 2.1 Initial Setup
1. User completes authentication
2. User provides encryption password
3. Generate PBKDF2 salt and derive Master Key
4. Generate long-term KeyPair
5. Generate DEK for KeyPair protection
6. Create Envelope for DEK using Master Key encryption
7. Encrypt private key using DEK
8. Clear sensitive material from memory
9. Store encrypted private key, public key, DEK and envelope

#### 2.2 Server Storage
The server stores:
- User authentication details
- PBKDF2 parameters for Master Key
- Encrypted private key metadata
- Public key from KeyPair
- Encrypted private key
- Key state information

### 3. DEK and Envelope Management

#### 3.1 Core Concepts
* DEK (Data Encryption Key):
  - Primary entity for data protection
  - Random AES-256 key generation
  - Single DEK can have multiple envelopes
  - Manages overall key lifecycle

* Envelope:
  - DEK encrypted using an encryption provider
  - Agnostic to encryption method (MasterKey, PublicKey, etc)
  - Contains encryption provider identification
  - Independent state management
  - References parent DEK

#### 3.2 Encryption Provider Identification
* Encryption providers must identify themselves:
  ```go
  type Encrypter interface {
      Encrypt(data []byte) (*Ciphertext, error)
      ID() string  // Identifies the encryption provider
  }
  ```
* ID references may point to different entity types:
  - User records for password-based encryption
  - KeyPair records for public key encryption
  - External KMS provider records

#### 3.3 Access Management
* Each recipient has individual envelope
* DEK remains unchanged
* Access control through envelope state
* Clear revocation process
* Support for emergency access

### 4. Technical Client Access

#### 4.1 Client Authentication & Key Protection
* Based on proven PKI patterns
* Requires:
  - Client identification
  - High entropy credentials
  - Clear key protection strategy

#### 4.2 Client Key Management
* Generate and protect long-term KeyPair
* Use DEK and Envelope pattern for KeyPair protection
* Clear revocation process

### 5. Secret Management

### 5. Secret Management
* Each secret protected by unique DEK
* DEK wrapped in envelopes using authorized encryption providers
* Original secret unchanged during sharing
* Access managed through envelope states
* Independent revocation per envelope
* Clear audit trail for all operations

### 6. Security Requirements

#### 6.1 Memory Protection
* Clear sensitive data after use
* No serialization of raw key material
* Secure memory wiping
* Memory encryption where possible
* Prevent key material swapping

#### 6.2 Error Handling
Must follow error handling requirements from crypto-spec:
* Use constant-time comparisons
* Clear sensitive data on errors
* Generic error messages
* Rate limiting on critical operations

## Consequences

### Positive
* Clear separation of authentication and key protection
* Stable cryptographic identities
* Simple and robust key hierarchy
* Strong E2EE guarantees
* Proven cryptographic approaches
* Support for both user and technical clients
* Comprehensive security model
* Explicit recipient identification
* Clean DEK/Envelope relationship

### Negative
* Password changes require re-encryption of KeyPair
* Master Key must be carefully protected in memory
* Need robust authentication flow

## Notes
* Consider backup procedures for key material
* Document emergency procedures
* Regular security audits required
* Need clear revocation procedures
* Define recovery processes

## References
* crypto-spec.md - Core cryptographic specifications
* ADR-009 - Key Derivation Architecture
* ADR-002 - Secret management model
* ADR-003 - Input processing
* ADR-004 - Service architecture
