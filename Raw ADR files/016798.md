# ADR 0001: Implement Concurrent Product Insert with Database Constraints

**Status:** Accepted

**Context:**
Our application requires a mechanism to prevent race conditions during concurrent updates to the database. Specifically, when multiple requests attempt to modify the same resource simultaneously, we need to ensure that only one request succeeds, and others are handled gracefully. This is a common requirement in systems handling financial transactions, unique resource allocation, or state changes.

We considered three main approaches:

1.  **Java's `ReentrantLock`:** A low-level concurrency utility for thread-safe access to a shared resource.
2.  **Redis Distributed Lock:** A distributed locking mechanism using Redis to coordinate access across multiple application instances.
3.  **Database Constraints:** Leveraging the database's built-in transactional and locking capabilities to handle concurrency.

**Decision:**
We have decided to proceed with using **database constraints** to manage concurrency. Specifically, we will rely on a combination of a `unique` key constraint and an `INSERT` statement to ensure atomic updates. This approach is sufficient for the current scope of our project, which is a proof-of-concept/demo. We will not use `ReentrantLock` or a Redis distributed lock at this time.

**Rationale:**
* **Simplicity and Speed of Implementation:** Using the database's built-in features is the fastest way to achieve the required concurrency control for this demo. There is no need to add new dependencies (`Redis`, etc.) or write complex custom locking logic.
* **No New Dependencies:** This approach avoids introducing external dependencies like Redis, which would add complexity in terms of setup, maintenance, and potential points of failure.
* **Sufficiency for Project Scope:** For a demo project, the performance and scalability of a database-based lock are more than adequate.
* **Single Point of Authority:** The database is the single source of truth for the data, and using its native mechanisms ensures data integrity is maintained at the most fundamental level.

**Consequences:**

**Pros:**
* Fast to implement and reduces development time, allowing us to focus on core demo features.
* No new dependencies or infrastructure required.
* Reliable and transactional, as it leverages the database's ACID properties.

**Cons:**
* **Performance Bottleneck:** For very high-throughput systems, database row-level locks can become a performance bottleneck. This approach is less performant than an in-memory or dedicated distributed locking solution for a large number of concurrent requests.
* **Scalability Limitations:** This solution is less scalable than a distributed locking mechanism. If the application were to scale to dozens or hundreds of instances, the database could become a point of contention.
* **Limited Scope:** This approach only provides concurrency control for operations within the database. It does not address race conditions or synchronization issues involving other services or resources outside of the database transaction.

**Alternatives Considered:**
* **`ReentrantLock`:**
    * **Pros:** Very fast for in-process synchronization. No external dependencies.
    * **Cons:** Not suitable for distributed applications with multiple running instances. The lock is only effective within a single JVM, which would not prevent race conditions if the application is scaled horizontally.
* **Redis Distributed Lock:**
    * **Pros:** Highly scalable and performant for distributed systems. Can manage concurrency across multiple application instances.
    * **Cons:** Adds an external dependency (Redis) which increases infrastructure complexity and potential for new failure modes. Requires more development time to implement and test properly.

**Future Considerations:**
This decision is considered temporary for the demo project. If the project were to evolve into a production application with high concurrency requirements, we would need to revisit this decision and likely transition to a more scalable solution, such as a dedicated distributed lock (e.g., using Redis, Zookeeper, or Consul). The architecture is designed to allow for this future enhancement without a complete rewrite.