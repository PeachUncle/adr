# ADR-0011: Age Encryption for Secrets

## Status

Accepted

Date: 2024-11-05

## Context

The Agent Stack Controller requires API keys for multiple LLM providers (Claude, OpenAI, Google). These secrets need to be:

- Stored securely to prevent accidental exposure
- Easy to use in development
- Safe to commit to version control (in encrypted form)
- Simple to manage without complex infrastructure
- Shareable among team members
- Rotatable when compromised

Traditional approaches like environment variables alone are insufficient because:
- `.env` files are often accidentally committed
- No encryption at rest
- Difficult to share securely
- No audit trail

## Decision

We will use [age](https://github.com/FiloSottile/age) encryption for managing secrets in the Agent Stack Controller.

The system will:
1. Store plaintext secrets in `.env` (gitignored)
2. Encrypt secrets to `.env.age` using age
3. Commit only `.env.age` to version control
4. Provide `asc secrets` commands for encryption/decryption
5. Auto-decrypt on `asc up` if needed
6. Store age keys in `~/.asc/age.key` (never committed)

## Consequences

### Positive

- **Simple**: age is a simple, modern encryption tool
- **Secure**: Strong encryption (ChaCha20-Poly1305)
- **Git-safe**: Encrypted files safe to commit
- **No infrastructure**: No key management servers needed
- **Team-friendly**: Easy to share public keys
- **Auditable**: Git history shows when secrets changed
- **Automatic**: Transparent encryption/decryption
- **Cross-platform**: Works on Linux, macOS, Windows

### Negative

- **Additional dependency**: Requires age binary
- **Key management**: Users must backup their age keys
- **Learning curve**: Team needs to understand age
- **No key rotation**: Changing keys requires re-encryption
- **Single point of failure**: Lost key = lost secrets

### Neutral

- **Manual key distribution**: Public keys shared out-of-band
- **File-based**: Secrets stored in files, not environment

## Alternatives Considered

### Alternative 1: git-crypt

**Description:** Use git-crypt for transparent encryption in git

**Pros:**
- Transparent encryption/decryption
- Integrated with git
- Supports multiple users
- Automatic on git operations

**Cons:**
- More complex setup
- Requires GPG keys
- Less portable
- Harder to debug
- Opaque to users

**Why not chosen:** Too complex for our needs, GPG dependency

### Alternative 2: HashiCorp Vault

**Description:** Use Vault for centralized secret management

**Pros:**
- Enterprise-grade security
- Centralized management
- Audit logging
- Dynamic secrets
- Access control

**Cons:**
- Requires running Vault server
- Complex setup
- Overkill for local development
- Network dependency
- Additional infrastructure

**Why not chosen:** Too heavy for a local development tool

### Alternative 3: SOPS (Secrets OPerationS)

**Description:** Use Mozilla SOPS for encrypted files

**Pros:**
- Supports multiple backends (age, GPG, KMS)
- Partial encryption (only values)
- Good for YAML/JSON
- Mature tool

**Cons:**
- More complex than age
- Requires backend configuration
- Overkill for simple .env files
- Additional abstraction layer

**Why not chosen:** More complexity than needed, age is sufficient

### Alternative 4: Environment Variables Only

**Description:** Use environment variables without encryption

**Pros:**
- Simple
- No additional tools
- Standard practice
- Works everywhere

**Cons:**
- No encryption at rest
- Easy to accidentally expose
- Hard to share securely
- No version control
- No audit trail

**Why not chosen:** Insufficient security, too easy to leak

## Implementation Notes

### File Structure

```
project/
├── .env              # Plaintext secrets (gitignored)
├── .env.age          # Encrypted secrets (committed)
├── .env.example      # Template (committed)
└── ~/.asc/age.key    # User's age key (never committed)
```

### Commands

```bash
# Encrypt secrets
asc secrets encrypt

# Decrypt secrets
asc secrets decrypt

# Check status
asc secrets status

# Rotate key
asc secrets rotate
```

### Automatic Decryption

When running `asc up`:
1. Check if `.env` exists
2. If not, check if `.env.age` exists
3. If yes, decrypt automatically
4. Proceed with startup

### Key Generation

On first run of `asc init`:
1. Check if `~/.asc/age.key` exists
2. If not, generate new age key pair
3. Store private key in `~/.asc/age.key` (0600 permissions)
4. Display public key for sharing

### Team Collaboration

```bash
# Share your public key
asc secrets status  # Shows public key

# Encrypt for multiple recipients
age -r <pubkey1> -r <pubkey2> -o .env.age .env

# Each team member can decrypt with their key
asc secrets decrypt
```

## References

- [age - A simple, modern encryption tool](https://github.com/FiloSottile/age)
- [age specification](https://age-encryption.org/)
- [Security Best Practices](../security/SECURITY_BEST_PRACTICES.md)
- [Secrets Management Implementation](../../internal/secrets/secrets.go)

## Revision History

- 2024-11-05: Initial version
- 2024-11-06: Added automatic decryption on startup
