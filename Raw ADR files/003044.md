## ADR 2: Single DB vs. DB for Each Service

### Context
We need to determine the database architecture for our microservices-based application: using a single database for all services or separate databases for each service.

### Decision

+ We would use a managed document DB for data storage.
+ We will use a single database with a separate schema for each service.
+ We can switch to a single database per service if and only if required in future with a simple migration of schemas from the existing DB. 

### Decision Rationale

+ As a startup, investment (money, time and effort) on multiple DBs when the user volume is low would be counterproductive from a maintenance and cost point of view. 
+ Single DB can even sustain on high volume as the DB chosen here is a managed instance which allows us to scale up on demand.
+ We intend to create a document DB on the cloud and create one schema/collection per service which can in future migrate these schemas to gain scalability if need be.
+ As the overall application mostly would be JSON driven, the use of single document DB is most suitable with service-specific schemas (which can be the building block of future enhancement and migrations).

However, separate databases provide isolation, reducing the risk of one service impacting others. This approach allows each service to choose the database technology best suited to its needs. It aligns with microservices principles, enabling independent data management.

### Implications

+ Database schema management and data consistency may require careful planning.
+ Cross-service database connectivity requirements should be carefully planned to ensure the number of connections required by different services.
+ We need to keep the max scalability into consideration for better infra planning.

### Implementation Details

+ Create and manage individual schemas for each microservice or component.
+ Implement data synchronization and consistency strategies where necessary.
+ Implement and review database synchronization between master/writer node to the reader node. The sync delay should be negligible.

### Monitoring and Testing

+ Monitor database performance and usage for each microservice.
+ Test data isolation and consistency across services.

### Open Issues

Data backup and disaster recovery strategies for distributed databases.
