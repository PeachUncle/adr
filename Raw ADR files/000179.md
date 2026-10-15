**Title**: ADR-0002-Circuit Breakers for Provider Calls

**Status**: [[Proposed]] (By [[Hossein]] - at 2024-10-12)

**Tags**: [[Idempotency]], [[Messaging]], [[Transactional Inbox]], [[Reliability]]

**Context**: In a distributed system, ensuring idempotent processing of requests and avoiding duplicate operations is critical for maintaining data integrity and system reliability. Traditional approaches like request deduplication based on unique identifiers may introduce complexity and overhead. Therefore, leveraging a transactional inbox provides a structured and reliable mechanism to handle idempotency while guaranteeing at least-once processing semantics.

**Decision**: We decide to utilize a transactional inbox pattern to handle idempotency and avoid duplicate processing in the system. The key components and characteristics of this approach include:

1. Inbox for Incoming Requests: Establish a transactional inbox to store incoming requests before processing. Each request is appended to the inbox in a transactionally consistent manner, ensuring that no requests are lost or duplicated during ingestion.
    
2. Idempotent Processing: Implement idempotent processing logic within the service layer to handle requests from the transactional inbox. Before processing a request, the service checks the inbox to determine if a similar request has been processed previously. If a duplicate request is detected, the service applies idempotent processing to ensure consistent behavior and outcome.
    
3. Transactional Guarantees: Leverage transactional properties of the inbox to provide at least-once processing semantics. By atomically appending requests to the inbox and processing them within the same transaction, we ensure that each request is either processed exactly once or not at all, thereby avoiding duplicate operations and maintaining data consistency.
    
4. Idempotency Token Integration: Optionally, integrate idempotency tokens into incoming requests to facilitate more efficient idempotent processing. Idempotency tokens can be used to uniquely identify requests and avoid unnecessary lookups in the inbox for previously processed requests.

**Justification**: Utilizing a transactional inbox pattern for handling idempotency offers several advantages in terms of reliability, consistency, and simplicity. By storing incoming requests in a transactionally consistent manner, we guarantee that each request is processed exactly once or not at all, eliminating the risk of duplicate operations and ensuring data integrity. Additionally, integrating idempotent processing logic within the service layer simplifies the implementation and reduces the complexity associated with traditional deduplication approaches.

**Consequences**:

✅ **Improved Reliability**: Leveraging a transactional inbox enhances the reliability of request processing by providing at least-once semantics and preventing duplicate operations.
✅ **Simplified Processing Logic**: Idempotent processing logic integrated within the service layer simplifies request handling and reduces the complexity of implementing deduplication mechanisms.
❌ **Potential Performance Overhead**: Transactional operations on the inbox may introduce performance overhead, particularly under high concurrency or throughput scenarios. Careful optimization and tuning are necessary to mitigate latency and resource consumption.
❌ **Integration Complexity**: Integrating the transactional inbox pattern into existing systems may require modifications to message ingestion, processing, and error handling logic. Proper testing and validation are essential to ensure seamless integration and operation.
❌ **Transactional Guarantees**: While the transactional inbox provides at least-once processing semantics, it may not guarantee exactly-once processing in all scenarios. Additional measures, such as idempotent processing and idempotency token integration, are necessary to achieve stronger consistency guarantees.
