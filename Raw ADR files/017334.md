# ADR 002: MicroPayVault Design - Escrow System for Micropayments

## Status
Accepted

## Context
We need a secure and efficient escrow system to handle micropayments between users and creators. The system must support:
- Pre-loaded user balances
- Monthly spending limits
- Creator earnings tracking
- Secure fund management
- Gas-efficient micropayments

## Decision
Implement a centralized vault contract (`MicroPayVault`) that acts as an escrow system for all micropayments.

### Key Design Decisions:

#### 1. **Centralized Vault vs Direct Transfers**
- **Chosen**: Centralized vault approach
- **Reason**: Reduces gas costs for micropayments, enables batch processing, and provides better user experience

#### 2. **Balance Management**
- **Chosen**: User deposits funds into vault, micropayments deducted from balance
- **Reason**: Eliminates need for individual transaction approvals, enables seamless micropayments

#### 3. **Monthly Limits**
- **Chosen**: Configurable monthly spending limits per user
- **Reason**: Protects users from overspending, provides budget control

#### 4. **Creator Earnings**
- **Chosen**: Accumulate earnings in vault, creators withdraw when desired
- **Reason**: Reduces gas costs, enables creators to batch withdrawals

## Consequences

### Positive
- ✅ **Gas Efficiency**: Single vault reduces transaction costs
- ✅ **User Experience**: No per-transaction approvals needed
- ✅ **Security**: Centralized fund management with proper access controls
- ✅ **Scalability**: Can handle thousands of micropayments efficiently
- ✅ **Budget Control**: Monthly limits prevent overspending

### Negative
- ❌ **Centralization Risk**: Single point of failure (mitigated by proper security)
- ❌ **Complexity**: More complex than direct transfers
- ❌ **Trust Requirement**: Users must trust the vault contract

### Neutral
- 🔄 **Fund Locking**: User funds are locked in vault until withdrawal
- 🔄 **Withdrawal Process**: Additional step for users to withdraw funds

## Implementation Details

### Contract Structure
```solidity
contract MicroPayVault {
    mapping(address => UserBalance) public userBalances;
    mapping(address => CreatorEarnings) public creatorEarnings;
    
    struct UserBalance {
        uint256 balance;
        uint256 monthlyLimit;
        uint256 monthlySpent;
        uint256 lastReset;
    }
    
    struct CreatorEarnings {
        uint256 totalEarnings;
        uint256 pendingWithdrawal;
        uint256 lastWithdrawal;
    }
}
```

### Key Functions
- `deposit()`: User deposits funds
- `withdraw()`: User withdraws funds
- `sendMicropayment()`: Send micropayment to creator
- `withdrawCreatorEarnings()`: Creator withdraws earnings
- `setMonthlyLimit()`: Configure spending limits

### Security Features
- ReentrancyGuard for withdrawal functions
- Owner-only emergency withdrawal
- Input validation for all parameters
- Monthly limit enforcement

## Alternatives Considered

### 1. **Direct Transfers**
- **Pros**: Simple, no trust required
- **Cons**: High gas costs, poor UX, requires per-transaction approval
- **Rejected**: Not suitable for micropayments

### 2. **Payment Channels**
- **Pros**: Very gas efficient
- **Cons**: Complex implementation, requires off-chain coordination
- **Rejected**: Overkill for our use case

### 3. **Batch Processing**
- **Pros**: Gas efficient for multiple payments
- **Cons**: Delayed payments, complex state management
- **Rejected**: Doesn't provide real-time micropayments

## Related Decisions
- ADR-001: Content Type Enum Design
- ADR-003: Micropayment Amount Limits
- ADR-004: Monthly Limit Reset Strategy

## References
- [OpenZeppelin ReentrancyGuard](https://docs.openzeppelin.com/contracts/4.x/api/security#ReentrancyGuard)
- [EIP-20 Token Standard](https://eips.ethereum.org/EIPS/eip-20)
- [Gas Optimization Best Practices](https://ethereum.org/en/developers/docs/gas/)
