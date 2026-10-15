# 002: Refactor Event-Driven Processes for SOLID Principles and Resilience

Date: 2025-05-19

Status: proposed

[001](001-use-zeromq-for-ipc.md)

## Context

The current deployment scripts (`run_strategy.py`, `run_order_executor.py`, and the CLI controller `AllInOneController`) wire together the core components of the high-frequency trading system using ZeroMQ for IPC. While functional, these scripts have grown to include responsibilities beyond their primary roles, and several areas of error handling, dependency management, and operational resilience are not clearly defined.

Key observations:
- **Tight coupling**: The process classes directly instantiate concrete ZMQ socket wrappers (`ZmqSubscriber`, `ZmqPusher`, `ZmqPuller`) and strategy/order-executor logic, making extension and testing harder.
- **Configuration spread**: Scripts mix command-line parsing, configuration loading, and business-logic orchestration in the same module.
- **Error handling gaps**: ZMQ reconnection and backoff strategies are not defined. Failures in one component may cascade without graceful recovery or restart.
- **Single Responsibility Principle (SRP)**: Each script handles multiple concerns (configuration, process lifecycle, message serialization, business logic invocation, and user I/O messaging).
- **Open-Closed Principle (OCP)**: Adding alternative strategies or execution modes would require modifying existing code rather than extending via abstractions.
- **Dependency Inversion Principle (DIP)**: High-level orchestration depends on low-level ZMQ and API implementations directly.
- **Resilience**: There is no supervisor or health-checking mechanism for background processes. In HFT scenarios, transient errors (e.g., network blips) can lead to silent message loss or process termination.

## Decision

1. **Introduce Abstractions for IPC and Lifecycle Management**
   - Define messaging interfaces (e.g., `ITickSubscriber`, `ISignalPublisher`, `ISignalSubscriber`) in the `src/interactor/interfaces/messaging` package.
   - Provide concrete ZeroMQ-based implementations in `src/infrastructure/messaging`, bound via a Dependency Injection container (`ServiceContainer`).

2. **Refactor Process Scripts to Use DI and SRP**
   - Move process bootstrap logic into a new `src/app/processes` module:
     - `StrategyProcessRunner`
     - `OrderExecutorProcessRunner`
   - Each runner depends only on abstractions (config, logger, messaging interfaces, repositories, strategy/use-case interfaces).
   - Separate configuration parsing (CLI) from process orchestration.

3. **Centralize Configuration**
   - Fully adopt the existing `Config` class for all ZMQ addresses, timeouts, and API endpoints.
   - Remove ad-hoc `config_dict` usage; use typed `Config` injected into runners.

4. **Enhance Resilience**
   - Implement retry/backoff for ZMQ socket connections and reconnections.
   - Introduce a lightweight supervisor component (`ProcessSupervisorService`) to monitor child processes (or threads), restart on failure, and expose health-check endpoints.
   - Add circuit-breaker pattern around external API calls (`PFCFApi`) with clear fallback and alerting.

5. **Improve Error Handling and Observability**
   - Replace `print` statements with structured logging at appropriate levels (INFO, WARNING, ERROR).
   - Ensure all exceptions are logged with context and, where possible, allow the process to continue or restart cleanly.
   - Add metrics hooks (e.g., publishing heartbeat or latency metrics) for end-to-end monitoring.

6. **Conform to Clean Architecture and SOLID**
   - Keep use cases (interactors) and domain logic completely decoupled from infrastructure and CLI layers.
   - Controllers/runners should only coordinate orchestration of injected dependencies.
   - Use Google style docstrings across all new modules.

## Consequences

**Positive:**
- Clear separation of concerns makes the codebase more maintainable and testable.
- New strategies or execution modes can be added by implementing new abstractions without modifying existing code.
- Improved operational resilience: sockets reconnect automatically, processes restart on failure, and circuit breakers prevent cascading failures.
- Better observability: structured logging and metrics enable faster diagnosis in a production HFT environment.

**Negative:**
- Requires non-trivial refactoring of existing scripts, impacting release timelines.
- Introduces additional complexity (DI container, supervisor service).
- May increase the learning curve for new contributors unfamiliar with the chosen DI or supervisor patterns.