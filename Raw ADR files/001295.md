# ADR-0006: Incentive Emissions & Distribution Framework

## Status

Draft

## Context

With performance fee capture (ADR-0005) introduced via `FeeController`, the platform requires a structured emissions and distribution framework to:

1. **Allocate Protocol Revenue**: Distinguish treasury retention vs. user incentives.
1. **Bootstrap Liquidity**: Provide targeted emissions to attract sticky capital during growth phases.
1. **Align Stakeholder Interests**: Reward active participants (depositors, strategists, governors).
1. **Support Future Tokenization**: Create a modular path toward an eventual governance / utility token without premature commitment.

## Problem

Current fee flows terminate at a single `feeRecipient`. There is no mechanism for:

- Emissions schedules (decay, epochs, caps)
- Multi-sink distribution (treasury, stakers, R&D, reserves)
- Dynamic re-weighting based on performance or market conditions
- Transparent on-chain accounting of revenue vs. emissions

## Decision

Introduce a two-layer distribution architecture:

1. **FeeController (Layer 1 - Accrual & Authorization)**
   - Central fee intake from authorized strategies
   - Tracks per-strategy, per-token accruals
   - Emits structured events for analytics indexing

1. **DistributionSplitter (Layer 2 - Allocation Logic)**
   - Pull model: FeeController forwards funds to splitter
   - Configurable weighted allocations (e.g. Treasury 40%, Incentives 40%, Dev 15%, Reserve 5%)
   - Emission bucket exposes streaming / epoch release primitives

## Architecture

```text
Strategies --> FeeController --(forward)--> DistributionSplitter --> Sinks
                                                |                       |
                                                |                       ├─ Treasury (multisig)
                                                |                       ├─ IncentivePool (staking / future gauge)
                                                |                       ├─ Dev Funding (time-locked)
                                                |                       └─ Reserve (safety buffer)
```

## Distribution Model

| Sink | Default Weight | Release Model | Notes |
|------|----------------|---------------|-------|
| Treasury | 40% | Immediate | Sustains operations & audits |
| IncentivePool | 40% | Stream / Epoch | Boosts TVL & retention |
| Dev Funding | 15% | Time-locked | Aligns long-term delivery |
| Reserve | 5% | Accumulative | Risk buffer & emergency actions |

All weights use 1/1/1 MD029 compliant list style in code & docs.

## Emissions Governance

- **Weight Adjustments**: Owner (multisig) with timelock delay
- **Caps**: Maximum emission per epoch (guard against spikes)
- **Epoch Length**: Default 7 days (configurable)
- **Adaptive Reweighting (Future)**: Hook in performance KPIs (TVL growth, strategy yield) to adjust incentive allocation dynamically

## Contract Additions

1. `DistributionSplitter` (initial scope)
   - Storage: array of recipients + weights (sum = 10_000)
   - Function: `distribute(address token)` splits current balance
   - Admin: `updateRecipients(address[] recipients, uint256[] weights)`
   - Event: `Distribution(address token, uint256 total, address recipient, uint256 amount)` (emitted per recipient)

1. `EmissionScheduler` (deferred)
   - Optional layer to release IncentivePool tokens linearly per epoch
   - Prevents front-loaded reward extraction

## Analytics & Monitoring

Events consumed by off-chain indexer:

- `FeesAccrued(strategy, token, amount)` (FeeController)
- `FeesWithdrawn(recipient, token, amount)` (FeeController)
- `Distribution(token, total, recipient, amount)` (DistributionSplitter)

Derived Metrics:

- Net Protocol Revenue (fees - emissions)
- Emission Efficiency (TVL growth per emitted token unit)
- Sink Retention Ratio (unused incentive carryover)

## Alternatives Considered

1. **Direct Fee Splitting in Strategies**: Increases surface area & duplicates logic.
1. **Monolithic Controller**: Less modular; harder to evolve with token launch.
1. **Immediate Token Launch**: Premature; architecture-first approach reduces regulatory and complexity risk.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Misconfigured weights | Skewed incentives | Timelock + monitoring |
| Centralization early | Governance perception | Publish roadmap to progressive decentralization |
| Emission overspend | Unsustainable incentives | Epoch caps + analytics dashboards |
| Upgrade complexity | Distribution stagnation | Modular Layer 2 design |

## Rollout Plan

1. Deploy `FeeController` (scaffold complete in this phase)
1. Implement & deploy `DistributionSplitter`
1. Wire FeeController -> DistributionSplitter flow
1. Add analytics indexing & dashboard panels
1. Introduce EmissionScheduler (if required for token launch)

## Future Extensions

- Staking gauge integration for dynamic IncentivePool weighting
- DAO-controlled timelock governance
- Cross-chain fee aggregation
- Performance-based multiplier curves

## Status Tracking

- [ ] `FeeController` deployed
- [ ] `DistributionSplitter` implemented
- [ ] Distribution weights configurable & tested
- [ ] Emissions analytics live
- [ ] Scheduler module evaluated

## References

- ADR-0005 Fee Model Optimization & Distribution Strategy
- OpenZeppelin PaymentSplitter (inspiration for weight pattern)

---
*This ADR establishes the structured path from raw fee accrual to sustainable, governed emissions—enabling future tokenization without premature commitment.*
