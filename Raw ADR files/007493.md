# ADR-001 – Database choice: Azure Cosmos DB (Serverless) 
 
**Status:** Accepted  
**Date:** 2025-10-30  
**Author:** Niklas Häll 
 
---
 
## Context 
The project requires a database solution that handles dynamic data volumes with low operational costs.  
The system should be able to run continuously without generating costs during inactivity and should easily scale up when needed.  
Since the solution runs in the Azure ecosystem, compatibility and easy integration are important factors.
 
---
 
## Decision 
We use **Azure Cosmos DB in Serverless mode** as the primary data storage for trips, bookings, and zones.  
The database offers a cost-effective model where only actual requests are billed, which fits the project's MVP phase.  
Cosmos DB integrates directly with the .NET SDK and can be used without external database operations. 
 
---
 
## Consequences 
**Advantages:** 
- No fixed cost – pay per request.  
- Scalable and fully managed solution within Azure.  
- Easy to integrate with .NET and Azure services (App Service, Functions, Key Vault).  
- Serverless mode makes it easy to keep the development environment running at low cost. 
 
**Disadvantages:** 
- Limited support for advanced joins and relationships.  
- Price per request can increase under high load.   
- Locked into the Azure ecosystem. 
 
---
 
## Risks / Mitigations

- **Risk:** The database may be exposed externally due to incorrect configuration.  
  **Mitigation:** Restrict external calls to the database via private networks and authentication. Ensure that only the API has permissions against Cosmos via Managed Identity.

- **Risk:** Too high cost during load peaks.  
  **Mitigation:** Implement request throttling (rate limiting) and telemetry monitoring to track usage patterns. 
 
---
 
## Alternatives 
- **Azure SQL Database** – more traditional model but higher base cost.  
- **PostgreSQL (Azure Flexible Server)** – powerful but requires more configuration and maintenance.  
- **MongoDB Atlas** – similar document model but outside the Azure ecosystem. 
 
---
 
## References 
- [System overview](../system_overview.md)  
- [Azure Cosmos DB – Serverless best practices](https://learn.microsoft.com/en-us/azure/cosmos-db/serverless)
