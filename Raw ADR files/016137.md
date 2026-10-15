# ADR-0001: Off-chain Test Environment Stabilization

**Status:** Accepted

## Context

The `offchain` project's test suite suffered from chronic instability and non-deterministic failures. The most common errors were `ResourceNotFoundRpcError` and `Block could not be found`, usually occurring during the execution of tests that interacted with the `viem` client.

The initial diagnosis pointed to several causes, such as race conditions in Anvil's initialization, Jest's configuration, and inconsistencies in the creation of `viem` clients in the test files.

The final investigation, by enabling the Anvil process logs, revealed the root cause: an `Error: Address already in use (os error 98)`. "Zombie" Anvil processes from previous test runs that were not terminated correctly continued to occupy port 8545. This prevented the new Anvil instance for the current test suite from starting correctly, resulting in cascading RPC connection failures.

## Decision

To definitively resolve the instability, a three-part solution was implemented, focused on robustness and the correct isolation of the different types of tests:

1.  **Preventive Port Cleaning:** The `jest.globalSetup.ts` script was modified to, before starting a new Anvil process, execute a command (`lsof -t -i:8545 | xargs kill -9`) that identifies and forces the termination of any process occupying port 8545. This ensures that each test run starts with a clean environment.

2.  **Refactoring and Isolation of Unit Tests:** All unit tests (in the `*.test.ts` files within `src/`) were refactored to be completely stateless. The new architecture follows two principles:
    *   **Shared Client:** All tests now import and use the same `testClient` instance from `lib/viem.ts`.
    *   **Mocking with `jest.spyOn`:** Blockchain calls (`multicall`, `readContract`, etc.) are intercepted and simulated using `jest.spyOn()`. This prevents unit tests from making real RPC calls, making them faster and more robust.

3.  **Integration Test Isolation:** The logic for managing the blockchain state (`evm_snapshot` and `evm_revert`) was removed from Jest's global configuration (`jest.setup.ts`) and moved into the only file that actually needs it: `test/integration/liquidation.test.ts`. This contains the complexity of state management only where it is strictly necessary.

## Consequences

### Positive

*   **Stability:** The test suite is now stable and deterministic.
*   **Clarity:** The separation between unit tests (fast, with mocks) and integration tests (slow, with state) is clearer and reinforced.
*   **Easier Debugging:** Future errors will more likely be related to business logic than to environment issues.

### Negative

*   **OS Dependency:** The port cleaning solution uses `lsof` and `kill` commands, which are standard in Unix-based environments (Linux, macOS). Developers on Windows will need to use WSL or have equivalent implementations of these commands in their PATH.
