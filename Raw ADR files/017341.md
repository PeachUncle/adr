# ADR-009: Race Condition in Session Updates

## Status
**Proposed** - Security vulnerability identified, mitigation plan defined

## Context

During security analysis of the `MeteredAccess` contract, a potential race condition was identified in the `updateSession` function. The current implementation allows users to call `updateSession` multiple times rapidly before the previous transaction is confirmed, potentially leading to:

1. **Double-spending attacks** - Users could consume content without proper payment
2. **Inconsistent state** - Session consumption could be manipulated
3. **Economic exploitation** - Users could bypass intended micropayment mechanisms

### Current Vulnerable Code
```solidity
function updateSession(bytes32 sessionId, uint128 consumption) external override nonReentrant {
    Session storage session = sessions[sessionId];
    require(session.user == msg.sender, "Not session owner");
    require(session.active, "Session not active");
    require(consumption > 0, "Invalid consumption amount");
    
    // VULNERABLE: No protection against rapid successive calls
    require(consumption > session.totalConsumption, "No consumption increase");
    uint128 consumptionIncrease = consumption - session.totalConsumption;
    
    session.totalConsumption = consumption;
    session.lastUpdate = uint32(block.timestamp);
}
```

## Decision

Implement a **time-based cooldown mechanism** combined with **nonce-based updates** to prevent race conditions in session updates.

### Proposed Solution

1. **Add cooldown period** - Minimum time between updates per user
2. **Implement nonce system** - Each update must include an incrementing nonce
3. **Add bounds checking** - Maximum consumption per update
4. **Event-based validation** - Track update frequency through events

### Implementation Strategy

```solidity
// Add to MeteredAccess contract
mapping(address => uint256) public lastUpdateTime;
mapping(address => uint256) public userNonce;
uint256 public constant UPDATE_COOLDOWN = 1; // 1 second minimum
uint256 public constant MAX_CONSUMPTION_PER_UPDATE = 1e18; // 1 token max

function updateSession(
    bytes32 sessionId, 
    uint128 consumption,
    uint256 nonce
) external override nonReentrant {
    Session storage session = sessions[sessionId];
    require(session.user == msg.sender, "Not session owner");
    require(session.active, "Session not active");
    require(consumption > 0, "Invalid consumption amount");
    
    // Anti-race condition measures
    require(block.timestamp >= lastUpdateTime[msg.sender] + UPDATE_COOLDOWN, "Too frequent updates");
    require(nonce == userNonce[msg.sender] + 1, "Invalid nonce");
    require(consumption <= MAX_CONSUMPTION_PER_UPDATE, "Consumption too high");
    
    // Update nonce and timestamp
    userNonce[msg.sender]++;
    lastUpdateTime[msg.sender] = block.timestamp;
    
    // Validate consumption increase
    require(consumption > session.totalConsumption, "No consumption increase");
    uint128 consumptionIncrease = consumption - session.totalConsumption;
    
    // Update session
    session.totalConsumption = consumption;
    session.lastUpdate = uint32(block.timestamp);
    
    emit SessionUpdated(sessionId, consumptionIncrease, 0);
}
```

## Consequences

### Positive Consequences
- **Eliminates race conditions** - Prevents rapid successive updates
- **Improves security** - Reduces attack surface for economic exploitation
- **Maintains performance** - Minimal gas cost increase
- **Backward compatible** - Can be implemented without breaking existing functionality

### Negative Consequences
- **Increased complexity** - Additional state management required
- **Gas cost increase** - ~2,000 gas per update for nonce and timestamp checks
- **User experience impact** - 1-second cooldown between updates
- **Frontend changes** - Need to track and increment nonces

### Risk Mitigation
- **Gradual rollout** - Implement with feature flag
- **Monitoring** - Track update patterns and cooldown violations
- **User education** - Clear messaging about update frequency limits
- **Fallback mechanism** - Emergency override for legitimate high-frequency use cases

## Implementation Plan

### Phase 1: Preparation (Day 1)
- [ ] Update contract interfaces
- [ ] Add new state variables
- [ ] Create migration script

### Phase 2: Implementation (Day 2)
- [ ] Implement cooldown mechanism
- [ ] Add nonce validation
- [ ] Update event emissions

### Phase 3: Testing (Day 3)
- [ ] Add race condition tests
- [ ] Test cooldown enforcement
- [ ] Validate nonce incrementing

### Phase 4: Deployment (Day 4)
- [ ] Deploy to testnet
- [ ] Run integration tests
- [ ] Monitor for issues

## Security Considerations

### Attack Scenarios Prevented
1. **Rapid Update Attack** - User calls updateSession multiple times in same block
2. **Consumption Manipulation** - User artificially inflates consumption without payment
3. **Economic Bypass** - User consumes content without triggering micropayments

### Additional Protections
- **Event monitoring** - Track unusual update patterns
- **Rate limiting** - Implement per-address daily limits
- **Circuit breakers** - Emergency pause if suspicious activity detected

## References

- [ADR-003: Micropayments Amount Limits](./003-micropayment-amount-limits.md)
- [ADR-006: Gas Optimization Implementation](./006-gas-optimization-implementation.md)
- [Security Audit Checklist](../security-audit-checklist.md)
- [OpenZeppelin ReentrancyGuard Documentation](https://docs.openzeppelin.com/contracts/4.x/api/security#ReentrancyGuard)

## Related Issues

- **Priority**: HIGH
- **Impact**: Economic security
- **Effort**: MEDIUM (2-3 days implementation)
- **Dependencies**: None (can be implemented independently)

---

**Created**: August 18, 2025  
**Last Updated**: August 18, 2025  
**Author**: Security Team  
**Reviewers**: [To be assigned]
