# ADR-002: Solid Pods for Cross-Government Data Sharing

## Status

**Accepted**

## Context

Wayfinder needs to display profile data (names, roles, skills, team memberships) for people across multiple government departments. This is a common challenge for any cross-government digital service.

### The Core Problem

Cross-government data sharing faces three competing concerns:

1. **Departments want sovereignty** - "We own our staff data"
2. **Users want portability** - "I shouldn't re-enter my info everywhere"
3. **Services want integration** - "We need data from multiple departments"

These concerns traditionally create political friction that stalls projects.

### Options Considered

#### Option 1: Central Database

A single database owned by one department or GDS.

| Aspect | Assessment |
|--------|------------|
| Technical complexity | Low |
| Political complexity | **Very High** |
| Data ownership | Contentious - who controls it? |
| Scaling | Single team becomes bottleneck |
| Trust model | All departments must trust the owner |

**Failure mode**: Projects stall in governance discussions about who owns the database, who pays for it, and who's responsible for breaches.

#### Option 2: Point-to-Point APIs

Each department exposes APIs, consumers integrate individually.

| Aspect | Assessment |
|--------|------------|
| Technical complexity | **Very High** (N×M integrations) |
| Political complexity | Medium |
| Data ownership | Clear - each dept owns theirs |
| Scaling | Every new consumer = new integrations |
| Trust model | Bilateral agreements |

**Failure mode**: Integration burden grows quadratically. Each new service needs agreements with every department. Different API styles create maintenance burden.

#### Option 3: Solid Pods (Selected)

Each department runs a Pod server. Services read from Pods using standard protocols.

| Aspect | Assessment |
|--------|------------|
| Technical complexity | Medium (standard protocol) |
| Political complexity | **Low** |
| Data ownership | Clear - each dept owns their Pod |
| Scaling | Add departments without changing Wayfinder |
| Trust model | No trust required - read public data |

**Success factor**: Sovereignty without silos.

## Decision

Use W3C Solid Pods as the data architecture for cross-government profile data.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        WAYFINDER                            │
│                   (reads, never stores)                     │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │  DWP    │   │  HMRC   │   │  Home   │   │  NHSE   │
    │  Pods   │   │  Pods   │   │ Office  │   │  Pods   │
    │         │   │         │   │  Pods   │   │         │
    └─────────┘   └─────────┘   └─────────┘   └─────────┘
    pods.dwp.     pods.hmrc.    pods.ho.      pods.nhse.
    gov.uk        gov.uk        gov.uk        gov.uk
```

### Key Properties

1. **No central database** - Wayfinder is stateless for profile data
2. **Department sovereignty** - Each runs their own Pod server
3. **Standard protocol** - W3C Solid specification, not custom APIs
4. **Graceful degradation** - Works with partial Pod availability
5. **Future-proof** - Any Solid app can use the same Pods

## Consequences

### Positive

- **Political friction eliminated**: No debates about who owns the central database
- **Clear accountability**: Department X's data problem = Department X's responsibility
- **Reduced coordination**: New departments just set up a Pod, no Wayfinder changes
- **User empowerment**: People can update their own profiles directly
- **Ecosystem benefits**: Other Solid apps get free access to the data
- **Standards-based**: W3C specification, not vendor lock-in

### Negative

- **Learning curve**: Teams need to understand Solid concepts
- **Infrastructure per department**: Each needs to run (or procure) a Pod server
- **Consistency challenges**: No central enforcement of data quality
- **Authentication complexity**: Solid-OIDC for private data

### Mitigations

| Risk | Mitigation |
|------|------------|
| Learning curve | Provide setup guides, reference implementations |
| Infrastructure burden | CSS is simple to deploy; could offer hosted option |
| Data consistency | Define shared vocabularies (FOAF, vCard) |
| Auth complexity | Start with public profiles, add auth incrementally |

## The Strategic Win

The hardest part of cross-government systems is rarely the code - it's getting agreement on data ownership and governance. Solid sidesteps this entirely:

> "You want our data in your database? That's a 6-month governance process."
>
> vs.
>
> "You want to read our public Pod? Here's the URL."

Once a department has a Pod server running, **any** Solid-compatible application can use it - not just Wayfinder. The investment compounds across the ecosystem.

## Implementation Phases

### Phase 1: Demo (Current)
- Local CSS server simulating multiple departments
- Public profiles only (no authentication)
- Proves the architecture works

### Phase 2: Pilot
- Single real department runs a Pod server
- Wayfinder reads from production Pod
- Validate operational model

### Phase 3: Expansion
- Additional departments onboard
- Shared vocabulary governance established
- Authentication for private data

### Phase 4: Ecosystem
- Other services consume the same Pods
- Self-service profile editing
- Cross-government Solid infrastructure

## References

- [W3C Solid Protocol](https://solidproject.org/TR/protocol)
- [Solid for Enterprise](https://solidproject.org/for-enterprise)
- [Inrupt (Enterprise Solid)](https://www.inrupt.com/)
- [Government API Design Guidance](https://www.gov.uk/guidance/gds-api-technical-and-data-standards)
- [ADR-001: Pod Proxy Pattern](./ADR-001-solid-pod-proxy-pattern.md)
