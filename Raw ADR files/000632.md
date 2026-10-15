# Technology stack selection for CMS

## Context and Problem Statement

ABC Limited is developing a multi-tenant, scalable and accessible complaint management system (CMS) for multiple different large scale companies, spanning across multiple different industries, such as Banking, Rail, Airlines and Telecom. The system will need to support web and mobile functionality for the front end, alongside a RESTful API backend. The main problem would be selecting a technology stack that would ensure scalability, maintainability, security, and extensibility.

## Considered Options

* **Frontend with JavaScript/TypeScript & Backend with C# (REST API) & SQL Server database**
* **Frontend with Python (Django) & Backend with Django REST Framework & PostgreSQL database**
* **Fullstack Node.js (Express.js REST API with REACT frontend) & MongoDB database**

## Decision Outcome

Chosen option: ***"Frontend with JavaScript/TypeScript & Backend with C# (ASP.NET, REST API) & SQL Server database"***, because this stack matches well with the scale of users that this system will need to handle. It offers strong support for multi tenancy and security and should make it simple to expand and integrate new companies from different industries into the sytem all in their own environment. The robust nature of the technologies chosen will provide us with easy API development and will be easy to integrate all types of different testing methods ranging from Automation, to basic assertion unit tests. Finally, the technology is a common and powerful tooling supported by many different hosting and cloud providers, making it simple to deploy the system when the development is complete.

### Consequences

* Good, because ASP.NET Core provides high performance, which will be crucial to an ever scaling system.

* Good, because ASP.NET Core provides native support for REST API's and JSON serialisation, which will be a perfect fit for supporting JSON API requests from the frontend along with being quick and simple to put together.

* Good, because as standard SQL Server boasts good security and tenant isolation, which will be perfect for the multi tenant nature of CMS.

* Good, because TypeScript offers type safety and easy to maintain frontend development.

* Good, all of the tech chosen for this stack is all mainstream technology that a lot of largescale applications already use, therefore it is proven technology that will have a lot of support industry wide. This will include cloud integration.

* Bad, because managing both JavaScript/TypeScript and C# together will make increase the overall complexity of development.

* Bad, because licensing costs for SQL Server will likely be a lot more expensive that other alternatives such as PostgreSQL.
