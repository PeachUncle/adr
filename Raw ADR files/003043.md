## ADR 12: RDBMS vs. Document DB for Data Storage
### Context
We are faced with the decision of choosing between a Relational Database Management System (RDBMS) and a Document Database (Document DB) for storing data in our travel management application. This decision significantly impacts data schema flexibility and search capabilities.

### Decision
We chose to implement a Document Database (Document DB) for data storage in our travel management application.

### Decision Rationale
+ *Flexi-Schema Requirement:* Our application deals with data from various travel providers (hotels, rail, airlines, etc.), each potentially having different data schemas or formats. The flexi-schema approach offered by Document DBs is well-suited to handle this variability. It allows us to store data without the rigid structure required by traditional RDBMS.
+ *Integration with Search Engines:* Document DBs have deep integration with search-based engines such as Lucene or Elasticsearch through platforms like Atlas. Leveraging these integrations enables us to perform precise searches with features like weighting, boosting, and relevance scoring. This is essential for providing users with accurate and tailored travel search results.

### Implications
+ *Data Modeling:* We need to design data models that leverage the flexible schema capabilities of Document DBs. This includes accommodating variations in data structures from different travel providers.
+ *Integration with Search Engines:* To fully utilize the search capabilities of Document DBs, we must ensure proper integration with search engines, including setting up and optimizing search queries.
+ *Data Migration:* If data from other sources or legacy systems needs to be migrated, a migration plan must be developed to accommodate the transition to the Document DB schema.

### Alternatives Considered
We considered using an RDBMS for data storage due to its strong data consistency and relational structure. However, the rigid schema of RDBMS could pose challenges when dealing with data from diverse travel providers with varying formats.

### Decision Outcome
This decision prioritizes flexibility and search capabilities, aligning with the requirements of our travel management application. The use of a Document DB allows us to handle diverse data schemas efficiently and provides powerful search functionality to enhance the user experience.
