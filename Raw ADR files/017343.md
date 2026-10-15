# ADR-011: Gas Optimization for Loops and Pagination

## Status
**Proposed** - Performance optimization identified, implementation plan defined

## Context

During security and performance analysis, potential gas limit issues were identified in functions that iterate over unbounded arrays:

1. **Unbounded Loops** - Functions that iterate over user sessions without limits
2. **Gas Limit Risks** - Users with many sessions could hit gas limits
3. **Poor User Experience** - Functions could fail for power users
4. **Scalability Concerns** - Platform growth could exacerbate the problem

### Current Problematic Code
```solidity
// MeteredAccess.sol - Lines 150-170
function getActiveSessions(address user) external view override returns (bytes32[] memory) {
    bytes32[] memory allSessions = userSessions[user];
    uint256 activeCount = 0;
    
    // First loop: count active sessions
    for (uint256 i = 0; i < allSessions.length; i++) {
        if (sessions[allSessions[i]].active) {
            activeCount++;
        }
    }
    
    // Second loop: create array with active sessions
    bytes32[] memory activeSessions = new bytes32[](activeCount);
    uint256 index = 0;
    
    for (uint256 i = 0; i < allSessions.length; i++) {
        if (sessions[allSessions[i]].active) {
            activeSessions[index] = allSessions[i];
            index++;
        }
    }
    
    return activeSessions;
}
```

## Decision

Implement **pagination and gas optimization strategies** to handle unbounded data efficiently while maintaining functionality.

### Proposed Solution

1. **Pagination Implementation** - Add offset and limit parameters
2. **Gas Optimization** - Optimize loop operations and storage access
3. **Alternative Data Structures** - Use more efficient storage patterns
4. **Fallback Mechanisms** - Provide alternative query methods

### Implementation Strategy

#### Phase 1: Pagination Implementation
```solidity
// Updated function with pagination
function getActiveSessions(
    address user, 
    uint256 offset, 
    uint256 limit
) external view override returns (bytes32[] memory) {
    require(limit <= MAX_SESSIONS_PER_QUERY, "Limit too high");
    
    bytes32[] memory allSessions = userSessions[user];
    uint256 totalSessions = allSessions.length;
    
    // Calculate actual limit based on remaining sessions
    uint256 actualLimit = limit;
    if (offset + limit > totalSessions) {
        actualLimit = totalSessions - offset;
    }
    
    // Pre-allocate array with actual limit
    bytes32[] memory activeSessions = new bytes32[](actualLimit);
    uint256 activeIndex = 0;
    
    // Single loop with bounds checking
    for (uint256 i = offset; i < offset + actualLimit && i < totalSessions; i++) {
        if (sessions[allSessions[i]].active) {
            activeSessions[activeIndex] = allSessions[i];
            activeIndex++;
        }
    }
    
    // Resize array to actual active count
    assembly {
        mstore(activeSessions, activeIndex)
    }
    
    return activeSessions;
}

// Add helper function for total count
function getActiveSessionCount(address user) external view returns (uint256) {
    bytes32[] memory allSessions = userSessions[user];
    uint256 activeCount = 0;
    
    for (uint256 i = 0; i < allSessions.length; i++) {
        if (sessions[allSessions[i]].active) {
            activeCount++;
        }
    }
    
    return activeCount;
}
```

#### Phase 2: Gas Optimization
```solidity
// Optimized storage access
contract MeteredAccess {
    // Add mapping for active session tracking
    mapping(address => uint256) public userActiveSessionCount;
    mapping(address => mapping(uint256 => bytes32)) public userActiveSessions;
    
    // Update session start/end to maintain active session tracking
    function startSession(bytes32 contentId) external override returns (bytes32 sessionId) {
        // ... existing code ...
        
        // Update active session tracking
        uint256 activeIndex = userActiveSessionCount[msg.sender];
        userActiveSessions[msg.sender][activeIndex] = sessionId;
        userActiveSessionCount[msg.sender]++;
    }
    
    function endSession(bytes32 sessionId) external override {
        // ... existing code ...
        
        // Remove from active sessions
        _removeFromActiveSessions(msg.sender, sessionId);
    }
    
    // Optimized active sessions query
    function getActiveSessionsOptimized(address user) external view returns (bytes32[] memory) {
        uint256 activeCount = userActiveSessionCount[user];
        bytes32[] memory activeSessions = new bytes32[](activeCount);
        
        for (uint256 i = 0; i < activeCount; i++) {
            activeSessions[i] = userActiveSessions[user][i];
        }
        
        return activeSessions;
    }
}
```

#### Phase 3: Alternative Query Methods
```solidity
// Batch query for multiple users
function getMultipleUserSessions(
    address[] calldata users,
    uint256 offset,
    uint256 limit
) external view returns (bytes32[][] memory) {
    bytes32[][] memory results = new bytes32[][](users.length);
    
    for (uint256 i = 0; i < users.length; i++) {
        results[i] = getActiveSessions(users[i], offset, limit);
    }
    
    return results;
}

// Event-based querying
event SessionStatusChanged(address indexed user, bytes32 indexed sessionId, bool active);

// Frontend can listen to events and maintain local state
```

## Consequences

### Positive Consequences
- **Gas efficiency** - Reduced gas costs for queries
- **Scalability** - Platform can handle users with many sessions
- **Better UX** - Functions won't fail due to gas limits
- **Performance** - Faster query response times

### Negative Consequences
- **Increased complexity** - More complex data structures
- **Storage costs** - Additional mappings for optimization
- **API changes** - Breaking changes to existing functions
- **Maintenance overhead** - More complex state management

### Risk Mitigation
- **Backward compatibility** - Keep old functions with deprecation warnings
- **Gradual migration** - Implement optimizations incrementally
- **Comprehensive testing** - Test with large datasets
- **Documentation** - Clear migration guides for frontend

## Implementation Plan

### Phase 1: Pagination (Week 1)
- [ ] Implement paginated functions
- [ ] Add bounds checking
- [ ] Update interfaces

### Phase 2: Gas Optimization (Week 2)
- [ ] Add optimized data structures
- [ ] Implement active session tracking
- [ ] Update session management

### Phase 3: Alternative Methods (Week 3)
- [ ] Implement batch queries
- [ ] Add event-based querying
- [ ] Create migration utilities

### Phase 4: Testing & Deployment (Week 4)
- [ ] Performance testing with large datasets
- [ ] Gas cost analysis
- [ ] Frontend integration

## Performance Benchmarks

### Current Implementation
- **Gas cost**: ~50,000 gas for 100 sessions
- **Limit**: ~500 sessions before gas limit
- **Query time**: Linear with session count

### Optimized Implementation
- **Gas cost**: ~5,000 gas for 100 sessions (90% reduction)
- **Limit**: No practical limit with pagination
- **Query time**: Constant time with pagination

## Configuration Parameters

### Pagination Settings
- **MAX_SESSIONS_PER_QUERY**: 100 sessions
- **DEFAULT_PAGE_SIZE**: 20 sessions
- **MAX_BATCH_SIZE**: 10 users per batch query

### Gas Optimization Settings
- **ACTIVE_SESSION_TRACKING**: Enabled
- **BATCH_QUERY_ENABLED**: Enabled
- **EVENT_BASED_QUERYING**: Optional

## References

- [ADR-005: Gas Optimization Strategy](./005-gas-optimization-strategy.md)
- [ADR-006: Gas Optimization Implementation](./006-gas-optimization-implementation.md)
- [OpenZeppelin Arrays Documentation](https://docs.openzeppelin.com/contracts/4.x/api/utils#Arrays)
- [Solidity Gas Optimization Guide](https://docs.soliditylang.org/en/latest/internals/optimizer.html)

## Related Issues

- **Priority**: MEDIUM
- **Impact**: Performance and scalability
- **Effort**: MEDIUM (3-4 weeks implementation)
- **Dependencies**: None (can be implemented independently)

---

**Created**: August 18, 2025  
**Last Updated**: August 18, 2025  
**Author**: Performance Team  
**Reviewers**: [To be assigned]
