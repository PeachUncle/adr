# Title: Core Entities and Relationships in Clearview

### Date: September 30, 2024

### Decision Maker: Clearview Engineering Team

### Status: Accepted

### Context:

We need to define the core entities and their relationships within the Clearview application to ensure a well-structured data model and efficient functionality. These entities will form the foundation of our database schema and influence the design of our APIs and user interface.

### Decision:

The core entities in Clearview are:

**Jobs**: Represents a specific job opening that a company wants to fill.

**Candidates**: Represents individuals seeking employment.

**Companies**: Represents organizations posting job openings.

**Hiring Manager**: Someone who lists the job opening, schedules interviews and makes a hiring decision

**LLM (Large Language Model)**: This entity represents the integration of Large Language Models within the application. While not a traditional data entity like the others, it's a core component of the system.



### Consequences:

**Clear Data Structure**: Defining these entities and their relationships will result in a well-organized database schema.
**Efficient Functionality**: Clear relationships enable efficient querying and data retrieval for features like job searching, candidate matching, and application tracking.
**Scalability**: A well-defined data model allows for easier scaling of the application as data volume grows.
**Maintainability**: Understanding the core entities and their interactions simplifies code maintenance and future development.

### Alternatives Considered:

**Combining Jobs and Companies**: Treating jobs as attributes of companies. This was rejected as it limits the flexibility to handle scenarios like multiple departments within a company posting jobs independently.
Additional Notes:

The specific attributes of each entity will be further refined during the database design phase.
The implementation of the LLM entity will involve integrating with a fine tuned LLM  and defining appropriate APIs for accessing their functionalities.
Security and privacy considerations related to candidate data and LLM access will be addressed during the design and development phases.