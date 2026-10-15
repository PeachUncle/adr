% ADR-0005: Fee Model Optimization & Distribution Strategy

# ADR-0005: Fee Model Optimization & Distribution Strategy

Status: Proposed  
Date: 2025-09-01  
Supersedes: None  
Superseded-By: None

## Context

The platform currently implements a simple performance fee (e.g. 1% of realized yield) at harvest time. Phase 6 introduces Aave integration, expanded strategy mix, and institutional readiness. Fee mechanics must:

- Support differentiated fee tiers per strategy class (base / advanced / premium)  
- Allow protocol-level management fee (annualized on TVL, streamed or accrued)  
- Provide optional rebalancing / optimization transaction fees (anti-spam & revenue)  
- Route fees into a standardized accounting module for transparency & audit  
- Enable future distribution: treasury, buyback, safety fund, incentive emissions  
- Preserve user trust via verifiable on-chain accounting & emission schedules

Constraints & considerations:

1. Smart contract complexity must not inflate attack surface.  
1. Gas overhead for fee accounting must remain <3% of core operation costs.  
1. Regulatory & audit posture favors understandable, parameter-bound fee logic.  
1. Multi-strategy aggregation must prevent double charging & clarify attribution.  
1. Future tokenization or points system should plug into unified fee ledger.

## Decision

Establish a modular Fee Controller Layer with explicit roles & standardized events.

Core elements:

1. FeeController (upgradeable or governed) holds global parameters & destinations.  
1. Strategy Adapters emit raw yield events; FeeController calculates + records fees.  
1. Unified Fee Ledger (struct / mapping) indexed by (strategy, feeType, epoch).  
1. Distribution Splitter: configurable basis points routing (treasury / safety / incentives).  
1. Management Fee accrual: linear per-block/second accumulator redeemable at harvest / checkpoint.  
1. Rebalancing Fee (optional): charged only if operation increases net TVL efficiency vs threshold.  
1. Emission Hooks (future): optional interface IFeeEmissionSink to stream portions to incentives contract.  
1. Governance-controlled parameter caps (e.g. maxMgmtFeeBps <= 200 = 2%).

Fee Types (enumeration): PERFORMANCE, MANAGEMENT, REBALANCE, INCENTIVE_DISTRIBUTION (derived), OTHER (extensible).

## Architecture Overview

```text
PortfolioManager
  ├─ StrategyAdapter (Uniswap / Curve / Compound / Aave)
  │    └─ reports yield -> FeeController.assessPerformance()
  ├─ RebalanceEngine -> FeeController.assessRebalanceFee()
  └─ TVLAccountant -> FeeController.accrueManagementFee()

FeeController
  ├─ parameters (struct FeeParams)
  ├─ mapping ledger[(strategy)(feeType)(epoch)] => FeeRecord
  ├─ distributeFees(FeeBatch) -> DistributionSplitter
  └─ emission hook (optional)

DistributionSplitter
  ├─ splits fees to: Treasury, SafetyFund, IncentiveVault
  └─ emits FeeDistributed events
```

## Data Structures (Illustrative)

```solidity
struct FeeParams {
  uint16 performanceFeeBps;     // per strategy or default
  uint16 managementFeeBpsAnnual; // applied to average TVL
  uint16 rebalanceFeeBps;        // optional, success-based
  uint16 maxSlippageBps;         // guardrail for value extraction
  address distributionSplitter;
}

struct FeeRecord {
  uint128 accrued;    // total unpaid
  uint128 distributed; // lifetime
  uint64  lastUpdate; // timestamp for mgmt accrual
}
```

## Event Model

| Event | Purpose |
|-------|---------|
| FeeAccrued(strategy, feeType, amount, epoch) | Accounting transparency |
| FeeDistributed(destination, feeType, amount) | Routing audit trail |
| ManagementAccrual(strategy, tvl, delta, amount) | Continuous accrual trace |
| FeeParamsUpdated(param, oldValue, newValue) | Governance traceability |

## Security & Risk Mitigations

- Parameter caps enforced in code (immutable upper bounds).  
- Access control via Roles: GOVERNANCE, OPERATOR (limited), PAUSER.  
- DistributionSplitter disallows unknown destinations; whitelist enforced.  
- Reentrancy guards on distribution & accrual functions.  
- Rate-limiting on mgmt fee accrual updates (e.g. min interval).  
- Upgradability (if used) restricted to governance timelock with delay.  
- Comprehensive invariant tests: sum(distributions) <= total accrued; no negative deltas.

## Gas Considerations

- O(1) state writes per accrual / distribution (packed structs).  
- Management fee accrual uses lazy checkpoint: compute `(t - lastUpdate) * rate * tvl / YEAR`.  
- Avoid loops over strategies: each strategy triggers its own accrual on touch.  
- Distribution batching: aggregate fees then split once per harvest/rebalance.

Target overhead: <3% added gas to deposit / harvest; <5k gas for a rebalancing fee assessment.

## Governance Controls

- setPerformanceFee(strategy, bps) (capped)  
- setGlobalManagementFee(bps)  
- setRebalanceFee(bps)  
- setDistributionSplits(treasuryBps, safetyBps, incentiveBps) (sum = 10000)  
- pauseFeeType(feeType)  
- rescueAccidentalToken(token)

## Implementation Plan (Phased)

1. Phase 6 (Current): Implement FeeController (performance + management) + DistributionSplitter.  
1. Phase 6 Mid: Integrate strategy adapters to call assessPerformance() at harvest.  
1. Phase 6 End: Add management fee accrual & settlement at harvest/rebalance touch points.  
1. Post-Launch: Enable rebalancing fee (if cost/benefit positive) and emission hooks.  
1. Future ADR: Tokenomics / Incentive Emissions (ties into IFeeEmissionSink).

## Metrics & Observability

- FeeTakeRate: feesCollected / grossYield (per strategy, rolling 7d)  
- ManagementAPRImpact: mgmtFees / averageTVL annualized  
- EffectiveNetAPY: grossAPY - feeDrag  
- DistributionCoverage: safetyFund inflow vs target buffer  
- RebalanceFeeJustification: gasSavedUSD vs rebalanceFeeUSD

Expose metrics via off-chain indexer & on-chain events ingestion into analytics dashboard.

## Alternatives Considered

1. Embed all fee logic in each Strategy (rejected: duplication, inconsistent).  
1. Single flat protocol fee on harvest only (rejected: inflexible, no mgmt revenue).  
1. Token emission only (no fees) model (rejected: unsustainable, dilution risk).  
1. Complex dynamic fee curves (deferred: adds risk & audit complexity; revisit after launch).

## Rationale

Centralization of fee logic reduces audit surface duplication and enables protocol-wide policy changes with minimal strategic friction. A ledgered model provides traceability essential for institutional adoption and downstream tokenomics.

## Consequences

Positive: Transparent accounting, governance agility, future-proofing for emissions.  
Negative: Additional contract + storage writes.  
Risk: Misconfiguration could erode user net yield (mitigated via caps & monitoring).

## Testing Strategy

- Unit: fee accrual math, boundary caps, pause mechanics.  
- Property: accrual monotonicity, invariant total distributed <= accrued.  
- Integration: harvest → fee accrual → distribution flows across all strategies.  
- Gas: measure added overhead vs baseline (target <3%).

## Future Enhancements

- Epoch-based fee windows with time-weighted performance.  
- Dynamic fee modulation based on utilization / volatility.  
- Cross-chain fee aggregation & bridging strategy.  
- On-chain proof-of-reserve for safety fund coverage.  
- Streaming management fees (Superfluid / L2) vs discrete accrual.

## Follow-ups

- ADR-0006 (potential): Incentive Emissions & Tokenomics Integration.  
- ADR-0007 (potential): Cross-Chain Fee Settlement Architecture.

## Status Tracking

| Component | Status |
|-----------|--------|
| FeeController skeleton | ⏳ Planned |
| DistributionSplitter | ⏳ Planned |
| Performance fee integration | ⏳ Planned |
| Management fee accrual | ⏳ Planned |
| Rebalance fee gating | 💤 Deferred |
| Emission hook | 💤 Deferred |

Last updated: 2025-09-01
