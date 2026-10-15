# ADR-003 – Infrastructure as Code (IaC) – tool choice: Bicep

**Status:** Accepted  
**Date:** 2025-10-30  
**Author:** Niklas Häll

---

## Context
The project requires a tool to define and reproduce infrastructure in Azure in a controlled and version-managed way.  
The choice of IaC tool affects both development speed, readability, and how easily the solution can be integrated into CI/CD flows.  
The alternatives considered are **Bicep**, **ARM templates**, and **Terraform**.

---

## Decision
We use **Bicep** as the tool for Infrastructure as Code.  
Bicep provides a declarative syntax with high readability and has **built-in support in Azure CLI and Azure DevOps**, which makes integration with existing pipelines and resources smooth.  
Since the project already utilizes several Azure services (App Service, Cosmos DB, Key Vault, etc.), Bicep provides a natural fit and requires no extra runtime or external dependencies.

### CI/CD Integration
Bicep integrates seamlessly with **GitHub Actions** workflows for infrastructure deployment:
- Infrastructure is deployed manually via Azure CLI using Bicep templates (not automated in CI/CD)
- Bicep modules are organized in `infra/modules/` for reusability
- Application deployments (via Docker containers) are automated through GitHub Actions workflows
- Bicep defines the infrastructure foundation that applications deploy into
- No separate infrastructure pipeline needed - infrastructure changes are infrequent and require manual review

---

## Consequences
**Advantages:**  
- First-class support in Azure CLI, developer IDE, and DevOps.  
- Clear and declarative syntax that simplifies maintenance and code review.  
- No external configuration or backend required (unlike Terraform).  
- Easy to build upon for future operations in Azure.  

**Disadvantages:**  
- Less portable – difficult to move to other cloud platforms. 
- Limited support for multi-cloud scenarios.  
- ARM templates are generated in the background, which can make troubleshooting more technical. (Bicep becomes an overlay, a "layer on top")  

---

## Risks / Mitigations
- **Risk:** Incorrect Bicep parameters can cause unwanted resource changes.  
  **Mitigation:** Introduce validation via `what-if` (done locally via CLI before deployment) in CI/CD pipelines.  

- **Risk:** Limited support for non-Azure resources.  
  **Mitigation:** Keep Terraform as a potential tool for future multi-cloud expansion. Had we not had such extensive use of Azure resources otherwise, we would have chosen Terraform over Bicep. 

---

## Alternatives
- **Terraform:** Portable and well-established, but requires a backend (state file needs to be stored, but becomes large in large projects so it's usually handled via a remote backend) and extra configuration.  
- **ARM templates:** Directly supported by Azure but harder to read and maintain.  
- **Pulumi:** Powerful but unnecessarily complex for this project.  

---

## CI/CD Pipeline Context
While Bicep handles infrastructure definition, the project uses **GitHub Actions** for application CI/CD:
- **CI Workflow:** Builds Docker images and pushes to GitHub Container Registry (GHCR)
- **CD Workflows:** Deploy applications to Azure App Service and Function App
- Infrastructure deployment remains manual (via `az deployment group create`) to ensure controlled infrastructure changes
- See [ADR-008 - Deployment Strategy](./ADR-008-docker-deployment.md) for detailed CI/CD pipeline architecture

## References
- [System overview](../system_overview.md)  
- [ADR-008 - Deployment Strategy](./ADR-008-docker-deployment.md) - CI/CD pipeline and Docker deployment
- [Microsoft Learn – Bicep documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
