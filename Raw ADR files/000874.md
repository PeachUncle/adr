# ADR: Implementation of Asynchronous API for ActionItem Management

## Decision Group

TD - Technology Decision

Proposed | 2024-10-27

## Problem/Issue

The system faces challenges in ensuring the safety and reliability of requests for creating and updating ActionItems. Synchronous processing models expose the system to risks of losing requests due to transient failures or network issues between services. There's a critical need for a strategy that prioritizes the secure receipt of requests before processing, aligning with our guiding principle of "Get it safe, then get it done".

## Decision

We have decided to implement our internal (non-Activity Pub) API an asynchronous API for handling ActionItem creation and updates. This API will leverage Kafka to enqueue requests as messages, immediately returning an HTTP 202 (Accepted) response. The emphasis is on quickly and safely storing requests "on disk" in Kafka, ensuring their persistence before any further processing is attempted. This decision is driven by the need to prevent the loss of requests due to operational failures or network issues, thereby enhancing the system's overall safety and reliability.

## Considered Alternatives

* *Synchronous API*: Direct, real-time processing of requests with immediate feedback on success or failure.
* *Queue-Based Asynchronous Processing (Non-Kafka)*: Utilizing alternative queuing technologies or in-memory solutions for asynchronous processing.

## Arguments

### Pro

* *Enhanced Reliability*: Leveraging Kafka's persistent storage mechanisms ensures that requests are not lost, even in the event of service disruptions or network failures.
* *Fault Tolerance*: Kafka provides built-in fault tolerance and replication features, further safeguarding against data loss.
* *Improved Error Management*: The asynchronous model allows for the separation of request receipt from processing. Errors encountered during processing are logged in an `Exceptions` node within the ActionItem, facilitating better error tracking and management without impacting the initial request acceptance.
* *Decoupling of Components*: This approach decouples the API layer from processing logic, allowing for independent scaling and maintenance of each component without risking request integrity.
* *Immediate Acknowledgement*: Users receive immediate feedback that their request has been received and queued for processing, improving the user experience during high-load situations.

### Con

* *Increased System Complexity*: Introducing Kafka and asynchronous processing adds complexity to the system's architecture and operational requirements.
* *Monitoring and Debugging Challenges*: Tracking the status of requests from acceptance through to processing necessitates more sophisticated monitoring and debugging tools.
* *Development and Operational Overhead*: Requires initial investment in setting up Kafka, developing error handling mechanisms, and establishing monitoring solutions.

## Related decisions

N/A

## Extends

N/A

## Related requirements

* The system must ensure no loss of ActionItem requests, even in the event of internal failures or network issues.
* ActionItems must include an `Exceptions` node for detailed tracking of any errors encountered during asynchronous processing.
* The system should prioritize the safe receipt and storage of requests as a foundational principle of operation.
