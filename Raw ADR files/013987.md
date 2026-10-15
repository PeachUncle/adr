# ADR-007: Identity and Keys

## Status

Accepted

## Context

We needed to decide:

1. What constitutes identity in Ping?
2. How do addresses relate to identity?
3. How do users manage multiple devices?
4. Where are keys stored and discovered?

## Decision

- **Key-based identity**: Public key IS identity
- **Addresses as aliases**: `@alice/acme.ping` resolves to keys
- **Multi-key support**: One identity can have multiple keys (like GitHub SSH keys)
- **Server hosts keys**: User keys fetched via RPC, not DNS

## Identity Model

### Key IS Identity

Your public key is your cryptographic identity. It cannot be spoofed, forged, or transferred.

### Address as Alias

Addresses are human-friendly aliases that resolve to keys:

```
@alice/acme.ping  →  [laptop-key, phone-key, tablet-key]
```

Like DNS maps domain names to IP addresses, Ping maps addresses to public keys.

### Why Not Address-Based Identity?

| Approach | Problem |
|----------|---------|
| Address = Identity | Tied to domain forever. Domain dies = identity dies. |
| Key = Identity | Portable. Can prove ownership cryptographically. |

## Multi-Key Support

### Like GitHub SSH Keys

One user can have multiple keys:

```yaml
keys:
  - kty: OKP
    crv: Ed25519
    kid: laptop
    x: key1...
  - kty: OKP
    crv: Ed25519
    kid: phone
    x: key2...
  - kty: OKP
    crv: Ed25519
    kid: work
    x: key3...
```

### Benefits

| Benefit | Details |
|---------|---------|
| Multi-device | Each device has own key |
| Revocation | Revoke one key without affecting others |
| No sync needed | Don't need to copy private keys between devices |
| Loss recovery | Lose one device, others still work |

## Key Storage and Discovery

### DNS vs Server

| Storage | What |
|---------|------|
| DNS TXT | Server public key (for server-to-server auth) |
| Server (via RPC) | User public keys |

### Why Not User Keys in DNS?

DNS doesn't scale for per-user data. Google can't have millions of DNS records for each user.

### Key Lookup Flow

```
1. Query DNS for server: _ping._tcp.acme.ping
2. Connect to server
3. RPC: method: keys, params: { address: @alice }
4. Server returns Alice's keys (JWK format)
```

### Key Format

JWK (RFC 7517) for interoperability:

```yaml
keys:
  - kty: OKP
    crv: Ed25519
    kid: laptop
    x: base64url-encoded-public-key
```

## Rationale

### Why Key-Based Identity?

| Alternative | Problem |
|-------------|---------|
| Email-style (address = identity) | Domain lock-in, no portability |
| Phone-based | Requires phone, privacy issues |
| Username/password | Not cryptographic, can be stolen |
| Key-based | Cryptographically verifiable, portable |

### Why Multiple Keys?

Single key model requires:
- Syncing private key across devices (risky)
- OR using one device only (impractical)

Multi-key model:
- Each device generates own key
- All keys linked to same identity
- Revoke compromised keys independently

### Comparison to Other Systems

| System | Identity Model |
|--------|----------------|
| Email | Address = identity (domain lock-in) |
| Signal | Phone number = identity |
| Nostr | Single key = identity (sync problem) |
| GitHub SSH | Multiple keys per account |
| SimpleX | No identity, only per-conversation queues |
| **Ping** | Multiple keys, address as alias |

### Considered: Key-Per-Relationship Model

We considered a model where each relationship gets a unique key:

```
Alice gives Bob: alice-bob-key
Alice gives Carol: alice-carol-key
```

**Potential benefits:**
- Leak tracing (spam on Bob's key = Bob leaked it)
- Granular revocation (cut off Bob without affecting Carol)
- Privacy (harder to correlate relationships)

**Why rejected:**
- Mandatory signatures already prevent spoofing
- If anyone can request a key, you're back to managing incoming requests anyway
- Adds significant UX complexity for marginal benefit
- Block-by-key achieves similar control with less complexity

SimpleX Chat uses this model (no user IDs, only per-conversation queues), but for Ping the complexity wasn't justified given cryptographic identity already solves the core problems.

## Consequences

- Public keys are the source of truth for identity
- Addresses are convenient aliases, not identity itself
- Users can have multiple keys (one per device)
- Keys stored on user's server, fetched via RPC
- Key revocation is per-key, not per-identity
- Migration possible by proving key ownership
