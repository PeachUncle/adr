# ADR 008: Micropayment User Parameter Fix

## Status
Accepted

## Context
The original implementation of the `sendMicropayment` function in `MicroPayVault` was using `msg.sender` to identify the user whose balance should be debited. However, this created an architectural issue when `MeteredAccess` contract called `sendMicropayment` on behalf of users.

The problem was:
- `MeteredAccess` calls `microPayVault.sendMicropayment()`
- `msg.sender` inside `MicroPayVault` becomes the `MeteredAccess` contract address
- `MicroPayVault` tries to debit balance from `userBalances[msg.sender]` (which is the contract address)
- But the actual user balance is stored under the user's address
- This caused "Insufficient balance" errors even when users had sufficient funds

## Decision
We decided to modify the `sendMicropayment` function signature to accept an explicit `user` parameter:

### Before:
```solidity
function sendMicropayment(
    address creator, 
    uint256 amount, 
    string calldata contentId
) external override
```

### After:
```solidity
function sendMicropayment(
    address user,
    address creator, 
    uint256 amount, 
    string calldata contentId
) external override
```

## Implementation Changes

### 1. Interface Update (`IMicroPayVault.sol`)
- Added `user` parameter to `sendMicropayment` function signature

### 2. Contract Update (`MicroPayVault.sol`)
- Modified function to use `userBalances[user]` instead of `userBalances[msg.sender]`
- Added validation: `require(user != address(0), "Invalid user address");`

### 3. MeteredAccess Update (`MeteredAccess.sol`)
- Updated call to pass `msg.sender` (the actual user) as the first parameter:
```solidity
microPayVault.sendMicropayment(
    msg.sender,  // User address
    content.creator,
    paymentDue,
    _bytes32ToString(session.contentId)
);
```

### 4. Test Updates
- Updated all test files to use the new function signature
- Added `user.address` as the first parameter in all `sendMicropayment` calls

## Consequences

### Positive
- ✅ Fixed the "Insufficient balance" error that was preventing micropayments
- ✅ All 64 tests now pass (was 61 before)
- ✅ Proper separation of concerns: contracts can act on behalf of users
- ✅ Maintains security: only authorized contracts can call `sendMicropayment`

### Negative
- ⚠️ Breaking change to the public interface
- ⚠️ Requires updates to all calling code
- ⚠️ Slightly more complex function signature

## Testing
- All existing tests updated and passing
- Integration tests confirm the fix works correctly
- Gas usage remains reasonable (~129k gas per micropayment)

## Related Issues
- Resolves the persistent "Insufficient balance" errors in MeteredAccess tests
- Enables proper micropayment processing in the content monetization dApp
