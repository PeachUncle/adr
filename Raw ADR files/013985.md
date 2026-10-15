# ADR-005: Discovery Mechanism

## Status

Accepted (Revised)

## Context

When sending a ping to `@bob/other.ping`, we need to discover:

1. Which server handles `other.ping`
2. The server's public key (for server-to-server auth)
3. Bob's public keys (for signature verification)

### Previous Decision

Originally stored both server and user keys in DNS TXT records.

### Problem

DNS doesn't scale for per-user data. Large providers (Google, Microsoft) can't have millions of DNS records for each user.

## Decision

- **Server discovery**: DNS SRV and TXT records
- **User keys**: Fetched via RPC from the server

## DNS Records (Server Level)

For domain `acme.ping`:

```dns
; Server discovery
_ping._tcp.acme.ping. 300 IN SRV 10 1 443 ping.acme.ping.

; Server public key (for server-to-server auth)
_ping._tcp.acme.ping. 300 IN TXT "pk=ed25519:base64..."
```

### SRV Record

```
_ping._tcp.<domain>. SRV <priority> <weight> <port> <host>
```

Provides: host and port for the Ping server.

### TXT Record

```
_ping._tcp.<domain>. TXT "pk=<algorithm>:<base64-public-key>"
```

Provides: server's public key for authenticating server-to-server requests.

## User Keys (Via RPC)

User keys are fetched from the server using the `keys` RPC method:

```
POST /
Content-Type: application/ping

<meta>
id: req123
from: @bob/other.ping
method: keys
params:
  address: @alice
</meta>
```

Response:

```
<meta>
from: @acme.ping
in-reply-to: req123
</meta>

<body type="yaml">
keys:
  - kty: OKP
    crv: Ed25519
    kid: laptop
    x: base64url-public-key...
  - kty: OKP
    crv: Ed25519
    kid: phone
    x: base64url-public-key...
</body>
```

### Key Format

JWK (RFC 7517) for interoperability.

## Discovery Flow

To verify a message from `@alice/acme.ping`:

```
1. Query _ping._tcp.acme.ping SRV → host, port
2. Query _ping._tcp.acme.ping TXT → server public key
3. Connect to server
4. RPC: method: keys, params: { address: @alice }
5. Server returns Alice's keys
6. Verify message signature against her keys
```

## Rationale

### Why DNS for Server, RPC for Users?

| What | Storage | Why |
|------|---------|-----|
| Server location | DNS SRV | Standard, cached, one per domain |
| Server key | DNS TXT | One per domain, simple |
| User keys | RPC | Scales to millions, easy to update |

### Why Not User Keys in DNS?

| Problem | Details |
|---------|---------|
| Scale | Can't have millions of DNS records |
| Update latency | DNS TTL delays key updates |
| Management | DNS is for admins, not users |

### Why Not .well-known?

| Approach | Pros | Cons |
|----------|------|------|
| DNS | Standard, cached | Less flexible |
| .well-known | HTTP-based | Extra roundtrip, endpoint to maintain |
| RPC | Uses existing endpoint | Requires connection first |

We use DNS for server discovery (standard), then RPC for everything else (consistent).

## Key Caching

Clients should cache user keys with reasonable TTL:

- Cache keys after fetching
- Re-fetch on signature verification failure
- Respect cache headers if provided

## Consequences

- One DNS query provides server location + server key
- User keys fetched on-demand via RPC
- Scales to any number of users per domain
- Key updates are immediate (no DNS propagation)
- Servers must implement `keys` RPC method
