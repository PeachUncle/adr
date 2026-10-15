# [ADR-AUTH-002] Select Azure Entra ID External Identities for Authentication

## Status
Accepted

## Context
The platform requires a secure, scalable, and standards-abiding Identity Provider (IdP) to manage external users (Tenants).
We need to support:
1.  OpenID Connect (OIDC) standards.
2.  Branded login pages.
3.  Reasonable cost scaling.

The candidates considered were:
- **AWS Cognito**: Native integration with AWS.
- **Auth0**: Developer-friendly, feature-rich.
- **Azure Entra ID External Identities**: Microsoft's CIAM solution.

## Related Requirements
*   Satisfies [Supported Authentication Methods ](../../spec/functional-requirements/auth.md#FR-AUTH-001)
*   Satisfies [Multi-Factor Authentication ](../../spec/non-functional-requirements/security.md#NFR-SEC-003)
*   Satisfies [Adaptive Authentication ](../../spec/non-functional-requirements/security.md#NFR-SEC-006)

## Decision
We will use **Azure Entra ID External Identities** as the primary Authentication Provider for external users.

Rules:
1.  The `Auth Service` component in the architecture maps to Azure Entra ID.
2.  The API Gateway will validate JWTs issued by Azure Entra ID.

## Rationale
1.  **Cost Efficiency**:
    **Auth0** is significantly more expensive at scale for B2C/SaaS use cases compared to platform-native solutions. Azure Entra ID offers a generous free tier (MAU based) and competitive pricing.

2.  **Usability & Developer Experience**:
    **AWS Cognito** is known for its steep learning curve, limited customization options for hosted UI, and AWS-specific idiosyncrasies that can complicate standard OIDC flows.
    **Azure Entra ID** provides a robust, enterprise-grade identity foundation with better documentation and standard compliance than Cognito, making it easier to implement and maintain.
    Although it adds a multi-cloud element (AWS + Azure), the identity layer is logically separate enough that the integration overhead is manageable via standard OIDC.

## Consequences
Positive:
- Lower cost than Auth0.
- Better standards compliance and DX than Cognito.
- Leveraging Microsoft's security expertise.

Negative:
- **Multi-Cloud Complexity**: We introduce a dependency on Azure while running infrastructure on AWS. This requires managing credentials and billing across two clouds.
- **Latency**: Potential slight increase in latency for token validation if public keys are fetched across cloud boundaries (negligible in practice with caching).
