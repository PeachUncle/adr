# ADR-006: Encryption and Signatures

## Status

Accepted (Revised)

## Context

Security is critical for a messaging protocol. We need to address:

- Transport security
- Message authenticity (preventing spoofing)
- Optional end-to-end encryption for sensitive messages

## Decision

- **Transport encryption**: TLS 1.3 mandatory
- **Message signatures**: Ed25519 mandatory
- **End-to-end encryption**: MLS optional

## Layer 1: Transport Encryption (Required)

TLS 1.3 mandatory for all connections:

- Server-to-server: HTTPS
- Client-to-server: HTTPS/WSS
- No plaintext ever

This protects messages in transit.

## Layer 2: Message Signatures (Required)

Every message is signed by the sender:

```
<meta>
id: msg123
from: @alice/acme.ping
to: @bob/other.ping
timestamp: 2024-01-03T10:00:00Z
signature: ed25519:a1b2c3d4...
</meta>

Message body here.
```

### How It Works

1. Alice's client signs the message with her private key
2. Bob's server fetches Alice's public keys via RPC (`method: keys`)
3. Verifies signature against any of her registered keys
4. Rejects if no key matches

### What This Solves

| Problem | Solution |
|---------|----------|
| Spoofing | Can't fake a `from` address |
| Tampering | Message can't be modified |
| Non-repudiation | Alice provably sent it |

### What's Signed

The signature covers:
- All meta fields (excluding the `signature` field itself)
- The body content

Canonical form: meta content + newline + body content, UTF-8 encoded.

## Layer 3: End-to-End Encryption (Optional)

For sensitive messages, full E2E so even servers can't read the body.

### Recommended: MLS (Messaging Layer Security)

- IETF standard (RFC 9420)
- Designed for federated/group messaging
- Forward secrecy
- Scales to groups

```
<meta>
id: msg123
from: @alice/acme.ping
to: @bob/other.ping
timestamp: 2024-01-03T10:00:00Z
signature: ed25519:a1b2c3d4...
encryption: mls
key-id: abc123
</meta>

[encrypted blob]
```

Only Bob's client can decrypt. Servers just route the blob.

### Alternative

Simpler NaCl box encryption for 1:1 messages if MLS is too heavy.

## Signature Algorithm

**Ed25519** chosen for:

- Fast signing and verification
- Small signatures (64 bytes)
- Small keys (32 bytes public)
- Widely supported
- No configuration needed (unlike RSA key sizes)

## Multi-Key Verification

When a user has multiple keys (e.g., laptop, phone):

1. Fetch all keys for the sender via `keys` RPC method
2. Try verifying signature against each key
3. Accept if ANY key matches
4. Reject only if NO keys match

This supports multi-device use without requiring key coordination.

## Rationale

### Why Mandatory Signatures?

Email's biggest security failure is spoofing. Anyone can send email claiming to be anyone. By requiring signatures at the protocol level:

- No unsigned messages accepted
- Spoofing eliminated by design
- Trust is cryptographic, not policy-based

### Why Optional E2E?

- Not all messages need E2E (newsletters, receipts)
- E2E adds complexity for clients
- Server-side features (search, AI agents) need readable messages
- Users should choose their security level

## Consequences

- All servers must implement Ed25519 verification
- All clients must implement Ed25519 signing
- Public keys fetched via RPC (not DNS)
- E2E encryption available but not required
- Spam prevention through cryptographic identity
