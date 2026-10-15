## Architecture Decision Record (ADR): Historical Data Versioning in MidasFlow

### 1. Title

Versioning of Historical Data Using Database Concepts for Time-based Lookups

### 2. Status

Proposed

### 3. Context

MidasFlow aims to provide users with the capability to access historical data. To achieve this, data needs to be stored in a manner that supports versioning and allows for time-specific queries. The challenge is to design a system that efficiently captures, stores, and retrieves data snapshots, adapting concepts from database versioning.

### 4. Decision

#### 4.1. Versioned Storage

- **Implementation**: Each piece of data or dataset will be stored with an associated version number, and every alteration (be it an append, overwrite, or index creation) will increment this version number.

- **Timestamping**: Every version will have an associated timestamp, representing the precise moment of its creation.

#### 4.2. Manifest Usage

- **Purpose**: The manifest will act as a directory or ledger, tracking the various versions of the data and their associated metadata.

- **Content**:

- Version number.

- Timestamp.

- Description of the change (e.g., "Appended data from source X", "Overwrite due to data correction", "Index creation for faster queries").

- **Implementation**: The manifest will be updated in real-time as data changes occur, ensuring an accurate record of all versions.

#### 4.3. Access Patterns

- **Time-based Lookups**: Users can specify a particular timestamp, and the system will retrieve the data version closest to, but not exceeding, that timestamp.

- **Version-based Lookups**: Alternatively, users can directly query a specific version number to retrieve associated data.

#### 4.4. Automatic Versioning

- **Appends**: When new data is added to an existing dataset, the system will automatically create a new version and update the manifest.

- **Overwrites**: If data is corrected or replaced, a fresh version will be generated, retaining the history of previous versions.

- **Index Creation**: Building a new index will also lead to a new version, ensuring that any structural or optimization changes are recorded.

#### 4.5. Delta format for Historical Data and Versioning

Delta is a data format based on Apache Parquet.

-   Goal: Leverage Delta's capabilities to provide ACID transactions and scalable metadata handling, along with time-travel features for historical data access.

-   Implementation:

    -   Replace or complement the existing storage layer with Delta Lake to store data in a versioned manner.
    -   Delta Lake will maintain transaction logs that allow for "time-travel" to access previous versions of the data.
    -   Utilize Delta Lake's ability to handle Parquet files, ensuring efficient data storage and querying capabilities.
    -   Allow users to specify a particular timestamp or version number, leveraging Delta Lake's time-travel capabilities to retrieve the associated dataset.

### 5. Consequences

- **Advantages**:

- Provides a clear and systematic method to access historical data.

- Ensures data integrity and traceability through detailed manifest records.

- Allows for both time-based and version-based data retrieval.

- **Challenges**:

- The system may experience increased storage demands due to the retention of multiple data versions.

- Efficient pruning or archiving strategies might be needed to manage old or rarely accessed versions.

- Retrieval times may increase as the volume of versioned data grows, necessitating optimized querying mechanisms.


This ADR proposes the use of database versioning concepts to facilitate historical data access in MidasFlow. Continuous evaluation will be essential as the system scales, ensuring that the versioning mechanism remains efficient and meets user requirements.

### 6. References
- [Delta Lake](https://delta.io/)
- [delta-rs](https://github.com/delta-io/delta-rs)
- [Understanding Delta File Logs - The Heart of the Delta Lake](https://www.youtube.com/watch?v=pCH_qNqnms0)
- [Understanding Delta File Logs Part 2 - Demonstrating Transactions](https://www.youtube.com/watch?v=ZSTJLfZy_Hs)
- [Understanding Delta File Logs Part 3 - The Deep Dive](https://www.youtube.com/watch?v=al_E0QFpNlw)
- [Diving Into Delta Lake: Unpacking The Transaction Log](https://www.databricks.com/blog/2019/08/21/diving-into-delta-lake-unpacking-the-transaction-log.html)
- [Tech Talk | Diving into Delta Lake Part 1: Unpacking the Transaction Log](https://www.youtube.com/watch?v=F91G4RoA8is)