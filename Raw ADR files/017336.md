# ADR 004: Monthly Limit Reset Strategy

## Status
Accepted

## Context
We need to implement a strategy for resetting user monthly spending limits. The system must:
- Track monthly spending accurately
- Reset limits at appropriate intervals
- Handle edge cases (new users, limit changes)
- Provide predictable behavior for users

## Decision
Implement a 30-day rolling window reset strategy with automatic limit reset when users set new limits.

### Key Design Decisions:

#### 1. **Reset Interval**
- **Chosen**: 30-day rolling window
- **Reason**: Aligns with typical billing cycles, provides predictable behavior

#### 2. **Reset Trigger**
- **Chosen**: Automatic reset when 30 days have passed since last reset
- **Reason**: Ensures consistent behavior without manual intervention

#### 3. **New User Handling**
- **Chosen**: Reset on first limit setting
- **Reason**: Provides immediate start of monthly cycle

#### 4. **Limit Change Handling**
- **Chosen**: Reset monthly spent when changing limits
- **Reason**: Prevents confusion and ensures fair limit application

## Consequences

### Positive
- ✅ **Predictability**: Users know when limits reset
- ✅ **Fairness**: Equal treatment for all users
- ✅ **Simplicity**: Easy to understand and implement
- ✅ **Consistency**: Same behavior across all users
- ✅ **Automation**: No manual intervention required

### Negative
- ❌ **Rigidity**: Fixed 30-day cycle may not suit all users
- ❌ **Complexity**: Additional logic for tracking reset dates
- ❌ **Gas Costs**: Slight increase in gas for reset checks

### Neutral
- 🔄 **User Education**: Users need to understand the reset cycle
- 🔄 **Timing**: Reset timing may not align with user preferences

## Implementation Details

### Contract Logic
```solidity
contract MicroPayVault {
    struct UserBalance {
        uint256 balance;
        uint256 monthlyLimit;
        uint256 monthlySpent;
        uint256 lastReset;  // Timestamp of last reset
    }
    
    function _resetMonthlyLimitIfNeeded(address user) internal {
        UserBalance storage balance = userBalances[user];
        
        // Reset if it's a new month (30 days passed)
        if (balance.lastReset == 0 || _isNewMonth(balance.lastReset)) {
            balance.monthlySpent = 0;
            balance.lastReset = block.timestamp;
        }
    }
    
    function _isNewMonth(uint256 lastReset) internal view returns (bool) {
        return block.timestamp >= lastReset + 30 days;
    }
    
    function setMonthlyLimit(uint256 limit) external {
        UserBalance storage balance = userBalances[msg.sender];
        balance.monthlyLimit = limit;
        
        // Reset monthly spent when setting new limit
        _resetMonthlyLimitIfNeeded(msg.sender);
    }
}
```

### Reset Scenarios

#### 1. **New User**
- `lastReset = 0` → Reset on first limit setting
- `monthlySpent = 0`
- `lastReset = block.timestamp`

#### 2. **30-Day Cycle**
- Check if `block.timestamp >= lastReset + 30 days`
- If true: reset `monthlySpent = 0`, update `lastReset`

#### 3. **Limit Change**
- Always reset `monthlySpent = 0` when changing limits
- Update `lastReset = block.timestamp`

### Edge Cases Handled
- Users with no previous limit
- Users changing limits mid-cycle
- Contract upgrades and migrations
- Time manipulation attempts

## Alternatives Considered

### 1. **Calendar Month Reset**
- **Pros**: Aligns with calendar months
- **Cons**: Complex implementation, different reset times for different users
- **Rejected**: Too complex for MVP

### 2. **Fixed Day of Month**
- **Pros**: Predictable reset dates
- **Cons**: Complex logic, edge cases with month lengths
- **Rejected**: Over-complex for current needs

### 3. **Manual Reset**
- **Pros**: User control
- **Cons**: Poor UX, potential for abuse
- **Rejected**: Not user-friendly

### 4. **No Reset**
- **Pros**: Simple implementation
- **Cons**: Limits become permanent, poor UX
- **Rejected**: Not suitable for monthly limits

## Future Considerations

### Phase 2 Enhancements
- Configurable reset intervals (weekly, bi-weekly, etc.)
- User-defined reset dates
- Pro-rated limits for partial months
- Reset notifications and reminders

### Advanced Features
- Multiple limit tiers
- Seasonal limit adjustments
- Usage-based limit recommendations
- Reset history tracking

## Related Decisions
- ADR-002: MicroPayVault Design
- ADR-003: Micropayment Amount Limits
- ADR-005: Gas Optimization Strategy

## References
- [Solidity Time Units](https://docs.soliditylang.org/en/latest/units-and-global-variables.html#time-units)
- [Blockchain Timestamp Considerations](https://ethereum.org/en/developers/docs/blocks/)
- [User Experience Best Practices](https://www.nngroup.com/articles/usability-101-introduction-to-usability/)
