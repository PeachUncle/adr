# ADR-1 Use the microservice architecture style

# Status
Accepted

# Context
The overall architecture of the baby url generation is simple, easy to create, maintain and **evolve**. Also require easy to scale and resilience features.
For the small number of urls, we can use the monolithic architecture but as system evolve we need to support millions of url redirection. So we need to consider any distributed
architecture solution.

Consider architectures in [architecture styles worksheets](https://www.developertoarchitect.com/downloads/worksheets.html) 
![](https://github.com/punitpatel214/baby-url-generator/blob/master/ADRS/architectures.png)

# Decision
We use the microservice architecture for the backend service of the baby url generation. Microservice will be containerized with Docker.
Positive consequences of the wide use of microservices contribute to this decision:
- large number of tools and frameworks for microservice development, as well as for monitoring, logging and distributed tracing.
- increasing number of engineers familiar with the style and respective dev tools and frameworks.
- support for containerized microservices available in public cloud providers.

Alternatives:
- **Serverless** : we can create backend service as Serverless architecture. However, for some functionality like In memory cache (Key Generation Service) don't fit in Serverless Architecture. Distributed cache required in Key Generation Service as well for Serverless architecture. At the initial state we don't want to mix both microservice and serverless architecture in system. Also, developer have to learn how to create, maintain and deploy serverless architecture.
- **Service-based-architecture**: This style will work for the system.  It has the nice benefit of separating the system in coarse-grained units called domain services. They are simpler to design and reduce the burden of packaging, deploying and overseeing to a reasonably small number of units. We chose microservice over service-based for two main reasons:
  - Microservices are more suitable to containerization and hence cloud-deployment.
  - In terms of scalability, ability to evolve and elasticity, microservice architecture seems better fit.

## Consequences
- Team need to understand dev ops fundamental
- Debugging, Distributed Tracing and monitor need extra efforts. Team need to have knowledge of log consolidation, distributed tracing and monitoring distributed application.
- Developers should be familiar with microservice development, [microservice patterns](https://microservices.io/),
 as well as with tools and frameworks, such as:  
  - Docker
  - Kubernetes
  - Cloud 

  
