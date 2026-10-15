# Title: Clearview Tech Stack

### Date: September 30, 2024

### Decision Maker: Clearview Engineering Team

### Status: Accepted

### Context:

We will be building a microservices-based arch with asynchronous communication between services using message queues.  We need to define the technology stack for this application to ensure efficient development, scalability, and maintainability.


### Decision:

We will use the following technology stack for the Clearview application:

### Programming Language: Go (Golang)
Go provides excellent performance, concurrency support, and a growing ecosystem of libraries well-suited for building microservices. The team is very familiar with Golang
### Framework: Gin
Gin is a lightweight and fast web framework for Go, offering performance and ease of use for building RESTful APIs.

### Microservices Communication: Message Queues (Kafka)
Message queues enable asynchronous communication between microservices, improving decoupling and resilience.

### Database: PostgreSQL
PostgreSQL is a robust, open-source relational database that provides reliability, data integrity, and advanced features suitable for our application.

### Reporting Database: PostgreSQL
We will use a separate PostgreSQL database for reporting to avoid impacting the performance of the primary application database.

### Observability: ELK Stack (Elasticsearch, Logstash, Kibana)
The ELK stack provides a comprehensive solution for logging, monitoring, and visualizing application performance and health.
### Frontend: React
React is a popular JavaScript library for building user interfaces, providing a component-based approach and a large community.


### Consequences:

**Performance**: Go and Gin provide excellent performance for building high-performance microservices.
**Scalability**: The microservices architecture with message queues allows for independent scaling of services.
**Maintainability**: Go's clear syntax and the modularity of microservices contribute to improved code maintainability.
**Observability**: The ELK stack provides comprehensive monitoring and troubleshooting capabilities.
**Developer Productivity**: Using well-established technologies with strong communities ensures good documentation, support, and a pool of skilled developers.

### Alternatives Considered:

**Other Languages**: Node.js with NestJS, Python with Flask/Django
**Other Databases**: MySQL, MongoDB

### Rationale:

The chosen technology stack offers a balance of performance, scalability, maintainability, and developer productivity. It aligns well with our requirements for a microservices-based architecture and provides a solid foundation for building a robust and scalable resume screening application. Ease of use and familiarity also played a very big part in this decision