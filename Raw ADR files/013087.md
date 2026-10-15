# ADR 6: Use Key Vault for Secrets and Credentials

## Status
Adopted 

## Context
Managing secrets and credentials securely is crucial for ensuring the integrity and confidentiality of applications and data.
Traditionally, secrets and credentials are stored directly within application configuration files or environment variables,
which poses significant security risks such as unauthorized access, accidental exposure, and difficulty in managing access control
. To mitigate these risks, various solutions for secrets management have emerged, including Azure Key Vault, which provides a secure and centralized storage for sensitive information.

## Decision
We will  use Azure Key Vault for managing secrets and credentials in our system.

## Consequences
### Positive

- **Security**: Azure Key Vault offers a protected and centralized repository for storing sensitive data, including secrets and credentials used for integrating third-party services and managing authentication tokens for users' email accounts.
- **Access controls**: It provides fine-grained access control mechanisms to ensure that only authorized individuals or systems can read, write, and manage secrets, thereby safeguarding sensitive information.
- **Scalability**: Key vaults are designed to be scalable, and many cloud-based providers offer multi-region replication, ensuring that the solution can grow to meet evolving needs and maintain availability.
- **Simplified secrets management**: Most providers offer programmable APIs and tools that streamline secret retrieval and management, simplifying the process for developers and administrators.
- **Versioning and Backup**: Azure Key Vault supports versioning of secrets, allowing us to manage multiple versions and roll back changes if necessary.
- **Developer Productivity**: By offloading the management of secrets and credentials to Azure Key Vault, developers can focus on building and deploying applications without worrying about the security implications of handling sensitive information.

### Negative
- **Cost**: Adds additional costs associated with storing and accessing secrets.
- **Learning Curve**: Team members may need to familiarize themselves with Azure Key Vault and its usage patterns, including integration with existing applications and workflows.

