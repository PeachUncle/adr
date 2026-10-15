# Data Persistence and Sharing Strategy

## Decision

To address potential locking issues and maintain a single source of truth, the `dagster_project` project will maintain exclusive control over the DuckDB/dbt instance for structured data. The `validation_tool.ts` web application will interact with raw image files and JSON blobs of AI results, which will be passed into its Docker container via volume mounts.

## Context

Initially, there was consideration of sharing a single DuckDB/SQLite instance between the `dagster_project` and `validation_tool.ts` web application. However, this approach presents significant risks:

* **Locking Issues:** Concurrent access from both systems to a single file-based database (DuckDB/SQLite) can lead to database locking, reducing system responsiveness and potentially causing data corruption.
* **Complexity:** Managing concurrent read/write operations and ensuring data integrity across two distinct applications sharing a single database instance adds considerable architectural complexity.

## Rationale

1. **Avoidance of Locking Issues:** By giving `dagster_project` exclusive control over the DuckDB/dbt instance, we eliminate the risk of database locking conflicts with the web application.
2. **Clear Ownership and Single Source of Truth:** dbt is designed for data transformation and modeling, making it the ideal candidate to manage the structured data. This approach reinforces the principle of a single source of truth for processed business card data within the dbt models.
3. **Simplicity for Web Application:** The `validation_tool.ts` web application primarily needs access to raw image files and the JSON output from the AI processing. Providing these via volume mounts keeps the web application stateless and simplifies its data access patterns.
4. **Future Scalability:** Should the need arise for more robust data sharing or real-time access for the web application, alternative solutions like Redis (with persistence) or other dedicated key-value stores can be introduced without disrupting the core data management strategy of dbt.

## Implications

* **Data Flow:** Raw image files will be ingested by `dagster_project`, processed, and the results (JSON blobs) will be stored alongside the original images. Both the raw images and the JSON results will be made available to the `validation_tool.ts` web application via shared volumes.
* **No Direct Web App Database Access:** The `validation_tool.ts` web application will not have direct read/write access to the DuckDB/dbt database.
* **Volume Management:** Docker Compose or Kubernetes configurations will need to explicitly define volume mounts for sharing the relevant directories (raw images, AI result JSONs) between the host and the `validation_tool.ts` container.

## Alternatives Considered

* **Shared DuckDB/SQLite Instance:** Rejected due to locking concerns and increased complexity.
* **Redis/Key-Value Store:** While a viable option for future real-time data needs, it introduces additional infrastructure and complexity that is not immediately required for the current scope. The current approach prioritizes simplicity and leverages existing file system capabilities.
