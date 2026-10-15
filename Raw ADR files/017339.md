# ADR-007: Micropayment Precision Issue

## Status
**Status**: Identified  
**Date**: 2025-08-18  
**Deciders**: Development Team  
**Supersedes**: None

## Context
During testing of the MeteredAccess contract, we identified a critical issue with micropayment calculations. The problem occurs due to integer division in Solidity, where small rates per unit result in micropayments that are truncated to zero or below the minimum threshold.

### Problem Details
- **Rate per unit**: 0.1 ETH per second
- **Consumption**: 60 seconds
- **Expected payment**: 6 ETH
- **Actual payment**: 0.000000000000000006 ETH (truncated due to division by 1e18)

### Root Cause
The calculation `(consumption * ratePerUnit) / 1e18` results in precision loss when:
1. `ratePerUnit` is small relative to 1e18
2. `consumption` is small
3. The product is less than 1e18

## Decision
We will implement a **minimum rate per unit** requirement to ensure viable micropayments:

### 1. Add Minimum Rate Validation
```solidity
uint256 public constant MIN_RATE_PER_UNIT = 0.001 ether; // 0.001 ETH minimum

function registerContent(
    bytes32 contentId,
    address token,
    ContentType contentType,
    uint128 ratePerUnit,
    string calldata metadata
) external {
    require(ratePerUnit >= MIN_RATE_PER_UNIT, "Rate below minimum");
    // ... rest of function
}
```

### 2. Update Rate Calculation Strategy
For the MVP, we will:
- Require minimum rates that generate viable micropayments
- Document this limitation for creators
- Consider future improvements for sub-minimum micropayments

### 3. Alternative Solutions (Future)
- **Precision scaling**: Use smaller divisors (1e15, 1e12)
- **Accumulation**: Batch small micropayments
- **Fixed-point arithmetic**: Implement custom decimal handling

## Consequences
### Positive
- ✅ **Guaranteed viable micropayments**: All rates will generate payments above minimum
- ✅ **Simple implementation**: No complex precision handling needed for MVP
- ✅ **Clear documentation**: Creators understand minimum requirements

### Negative
- ❌ **Higher barrier**: Small creators may need higher rates
- ❌ **Less granular**: Cannot support very small micropayments
- ❌ **Market limitation**: May exclude some use cases

## Implementation Plan
1. **Phase 1 (MVP)**: Add minimum rate validation
2. **Phase 2**: Document creator guidelines
3. **Phase 3**: Research precision improvements

## References
- [ADR-005: Gas Optimization Strategy](./005-gas-optimization-strategy.md)
- [ADR-006: Gas Optimization Implementation](./006-gas-optimization-implementation.md)
- Solidity Integer Division: https://docs.soliditylang.org/en/latest/types.html#division

