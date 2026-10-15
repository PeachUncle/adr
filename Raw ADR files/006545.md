# 001: Use ZeroMQ for Inter-Process Communication

Date: 2025-04-18

Status: accepted

## Context

The previous architecture relied on an in-process `RealtimeDispatcher` based on Python's `asyncio` for event handling between the Tick Producer, Strategy, and Order Executor. While functional, this approach faced several limitations for achieving lower latency and higher throughput, especially when aiming for higher frequency trading:

1.  **Python Global Interpreter Lock (GIL):** The GIL prevents true parallel execution of CPU-bound Python code (like complex strategy calculations) on multi-core processors within a single process.
2.  **`asyncio.sleep()` Delays:** The dispatcher's event loop contained `asyncio.sleep()` calls, introducing fixed latency.
3.  **In-Process Bottlenecks:** All components shared the same event loop. Slow I/O operations (e.g., database access in the strategy or executor) or heavy computations could potentially block or delay the processing of other critical events (like incoming ticks).
4.  **Buffering Latency:** The `TickProducer` buffered events and processed them periodically via `schedule`, adding artificial latency between tick reception and strategy processing.
5.  **Scalability:** Scaling strategy execution horizontally (running multiple strategy instances) was not straightforward within a single process.
6.  **Alignment with HFT Practices:** Distributed architectures using low-latency messaging queues are common in higher-frequency trading systems to decouple components and optimize performance.
The user provided an architecture diagram suggesting a distributed approach using ZeroMQ.

## Decision

We decided to replace the in-process `RealtimeDispatcher` and its associated event handling logic with **ZeroMQ (ZMQ)** for Inter-Process Communication (IPC) between the core trading components: Gateway (TickProducer), Strategy Engine, and Order Executor.

Specific implementation details:

1.  **Communication Patterns:**
    *   **Tick Data:** Use the ZMQ **PUB/SUB** (Publish/Subscribe) pattern. `RunGatewayUseCase` (`TickProducer`) acts as the publisher, binding to a known address. Strategy process(es) act as subscribers, connecting to the gateway's address and subscribing to tick topics.
    *   **Trading Signals:** Use the ZMQ **PUSH/PULL** pattern. Strategy process(es) act as PUSHers, connecting to a known address. The Order Executor process acts as the PULLer, binding to that address.
2.  **Serialization:** Use the **`msgpack`** library for serializing/deserializing data (like `TickEvent` and `TradingSignal`) sent over ZMQ. `msgpack` is chosen for its efficiency and performance compared to alternatives like JSON. Custom serialization handlers are implemented for Python `datetime` objects and `Enum` types.
3.  **Process Separation:** Core components (`TickProducer`, `SupportResistanceStrategy`, `OrderExecutor`) are refactored to operate independently, assuming they will run in separate operating system processes.
4.  **Infrastructure Layer:** Created a new `src/infrastructure/messaging` package containing reusable ZMQ socket wrappers (`ZmqPublisher`, `ZmqSubscriber`, `ZmqPusher`, `ZmqPuller`) and the `msgpack` serializer/deserializer.
5.  **Component Refactoring:**
    *   `TickProducer`: Now takes a `ZmqPublisher` dependency and publishes serialized ticks directly, removing internal buffering and scheduling.
    *   `SupportResistanceStrategy`: Removes `RealtimeDispatcher` dependency. Takes a `ZmqPusher` dependency to send serialized signals. Processes ticks received externally (e.g., from a ZMQ subscriber in its own process loop).
    *   `OrderExecutor`: Removes `RealtimeDispatcher` dependency. Takes a `ZmqPuller` dependency. Implements `process_received_signal` to poll the puller, deserialize signals, and execute orders.
    *   `RunGatewayUseCase`: Initializes gateway components and ZMQ sockets (PUB for ticks, PULL for signals listening side). It no longer manages a central event loop for strategy/execution.

## Consequences

**Positive:**

*   **Improved Parallelism:** Enables running the Strategy Engine and Order Executor in separate processes, effectively bypassing the Python GIL limitation for CPU-bound tasks.
*   **Potential Latency Reduction:** Decouples components, reducing the chance that slow operations in one component block others. Leverages ZMQ's low-latency transport.
*   **Enhanced Modularity:** Components are more independent, communicating only via defined ZMQ messages, making them easier to develop, test, and replace individually.
*   **Increased Scalability:** Strategy processes can potentially be scaled horizontally by running multiple instances subscribing to the same tick feed (PUB/SUB) and pushing signals to the same executor (PUSH/PULL load balancing).
*   **Fault Isolation:** An error in one process (e.g., Strategy) is less likely to bring down the entire system compared to the monolithic event loop.
*   **Alignment with Architecture Goal:** Moves the system closer to the distributed architecture depicted by the user and common in performant trading systems.

**Negative:**

*   **Increased Complexity:** Introduces the overhead of managing multiple processes, inter-process communication, and potential ZMQ connection/error handling complexities.
*   **New Dependencies:** Adds runtime dependencies on `pyzmq` and `msgpack`.
*   **Serialization Overhead:** Data must be serialized and deserialized for IPC, adding a small amount of latency (though `msgpack` minimizes this).
*   **Deployment Complexity:** Requires a strategy for launching and managing the separate processes (e.g., using supervisor, docker-compose, or custom scripts).
*   **Debugging Challenges:** Debugging issues across multiple processes can be more complex than within a single process.
*   **Configuration Management:** ZMQ addresses need to be configured and coordinated between processes. 