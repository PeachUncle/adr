# ADR 004: Use of BackgroundService for Job Execution

## Context

In designing the job scheduling library, the decision was made to use `BackgroundService` for managing job execution. This aligns with .NET's best practices and standard patterns for background task processing, which ensures that background operations are handled efficiently and consistently.

## Decision

The `AllJobsExecutorBackgroundService` class is implemented as an internal class. This decision was made based on the following considerations:

- **Encapsulation of Implementation Details:** Keeping the `AllJobsExecutorBackgroundService` class internal encapsulates the details of background job execution from the client. This is a standard practice in .NET to ensure that the implementation details of background tasks are hidden, providing a cleaner and more maintainable API.

- **Alignment with .NET Patterns:** Using `BackgroundService` is a standard pattern in .NET for running background tasks. This pattern allows the library to leverage the existing framework's capabilities for background processing, ensuring that job execution adheres to best practices in terms of lifecycle management and exception handling.

- **Client Flexibility:** Clients should use the `IJob` interface to define job logic. The internal `BackgroundService` manages job scheduling and execution, allowing clients to focus on implementing job functionality rather than managing background tasks. The library provides configuration methods like `AddHostedJobScheduler` and `AddJobScheduler` to allow clients to integrate the service with or without the internal background service as needed.

## Consequences

- **Pros:**
  - Adheres to .NET best practices and patterns for background task management.
  - Keeps implementation details hidden from clients, simplifying their interaction with the library.
  - Provides flexibility for job configuration through `AddHostedJobScheduler` and `AddJobScheduler`.

- **Cons:**
  - Requires providing two methods of injection (with and without `BackgroundService`), which adds complexity to the library.
  - Clients may need to implement their own background service if they do not want to use the provided `BackgroundService`. However, the internal background service only calls the `IJob.Execute` method, so clients can still implement their own solutions if desired.

- **Mitigations:**
  - Provide comprehensive documentation and examples on how to use the `IJob` interface and configure job execution, ensuring that clients understand how to effectively utilize the library.
