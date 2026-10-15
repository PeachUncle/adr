# Architecture Decision Record (ADR-001)

## Title: Technology Stack & Deployment for Nisien Tea Round Picker

### Context
Nisien Tea Round Picker is a productivity tool designed to facilitate fair selection for choosing who should make tea for their team in the office. It will:
- Provide an intuitive interface for managing teams and participants.
- Randomly select a tea maker to make tea for the team.
- Record historical tea rounds and the tea orders made by participants.
- Allow for mobile support, meaning that users can easily choose who should make tea from anywhere in the office.

The application consists of two main components:
- **Frontend:** A React web application with TypeScript.
- **Backend:** An ASP.NET Core Web API in C#.

The project is organized into separate FrontEnd and BackEnd directories and is deployed on Azure, with the frontend hosted on Azure Static Web Apps and the backend on Azure App Service.

### Decision
The following technology stack and deployment approach have been chosen:
- **Frontend:** React with TypeScript
- **Backend:** ASP.NET Core Web API (C#)
- **Database:** Entity Framework (EF) using an in-memory database during development.
- **Hosting/Deployment:**
  - **Frontend:** Azure Static Web Apps.
  - **Backend:** Azure App Service.
- **CI/CD:** Automated deployment via GitHub Actions.
- **Repository Structure:** Separate directories for `FrontEnd` and `BackEnd` ensure clear code boundaries.

### Rationale

#### **Frontend – React with TypeScript**
- **React:** A popular library for building dynamic user interfaces with reusable components. I wanted to use React to gain experience with it, as it is a widely popular framework with extensive support available.
- **TypeScript:** Provides static typing to improve code quality and reduce runtime errors.
- **Styling:** I will be relying on Bootstrap for styling since it makes it easy to create a good-looking website with minimal effort and provides built-in mobile support.
- **Past Experience:** I have no direct experience with React but I have experience with other reactivie javascript frameworks such as vue.js I wanted to use React to see how it compares to other frameworks and to gain experience with it.
- **Key Benefits:** Promotes a modular architecture through the use of components, making it easy to quickly update and modify the project. It also speeds up development with a rich ecosystem of pre-made components and allows for easy integration with REST APIs.

#### **Backend – ASP.NET Core Web API (C#)**
- **ASP.NET Core:** A proven framework for secure, high-performance APIs.
- **C#:** Offers robust tooling, asynchronous support, and strong testing capabilities.
- **Past Experience:** I have plenty of experience in developing web APIs with this framework.
- **Key Benefits:** Enables clear separation of business logic and data access while seamlessly integrating with databases. 

#### **Azure Hosting & CI/CD**
- **Deployment:** Azure Static Web Apps and Azure App Service provide easily hosting, with plenty of options for scalability.
- **CI/CD:** GitHub Actions streamline continuous integration and deployment reducing manual overhead for deployment and easily integrates with Azure services.

#### **Repository Structure**
- **Separation of Concerns:** Distinct directories for frontend and backend promote maintainability and collaboration.

### Consequences

#### **Positive Outcomes:**
- **Scalable Architecture:** The chosen stack supports growth and future enhancements.
- **Efficient Development:** Clear code separation and robust tooling enhance developer productivity.
- **Cloud-Ready:** Azure's services offer scalability, reliability, and ease of management.
- **Improved Developer Experience:** Static typing and comprehensive API documentation (via Swagger) to provide clarity to data structures and clearly illustrate how the front and back ends connect.

#### **Challenges:**
- **Initial Setup:** Configuring Azure services will require additional effort.
- **Database Transition:** Migrating from an in-memory database to a persistent one at a later date could cause issues and will require additional thoughts for schema changes and migration processes.
- **Learning Curve:** I will need to familiarize myself with React so I will have to rely on the existing extensive documentation and community support.

### Alternatives Considered

1. **Vue.js Frontend**
   - **Pros:** Familiarity with Vue.js could accelerate development.
   - **Cons:** Using React aligns with Nisien's preferred framework, aiding review and interview discussions while providing a professional growth opportunity.

### Decision Status
**Accepted** – The selected technology stack and deployment strategy, utilizing React with TypeScript and ASP.NET Core Web API (C#) hosted on Azure will be used for the initial implimentation of this project. Future iterations may incorporate persistent storage, enhanced analytics, and additional features such as notifications.

