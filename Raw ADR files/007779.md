# ADR: Use Auth0 for Artist Authentication in Copper Print Gallery

## Date
2024-07-31 (Updated: 2024-08-14)

## Status
Proposed

## Context
The Copper Print Gallery system requires a secure authentication solution for the artist to manage content. Public users will browse the gallery anonymously and do not require authentication. Given our hybrid architecture with frontend on Heroku and backend services on AWS Lambda, we need to ensure our authentication solution works seamlessly across this distributed system.

## Decision
We have decided to use Auth0 for handling artist authentication in the Copper Print Gallery system, with token validation occurring on the AWS side.

## Rationale
1. Platform Agnostic: Auth0 works well with both Heroku and AWS, fitting our hybrid architecture.
2. Managed Service: Auth0 provides a fully managed authentication service, reducing operational overhead.
3. Flexibility: Allows for future expansion of authentication needs.
4. Security: Offers robust security features including MFA and anomaly detection.
5. AWS Integration: Can be easily integrated with AWS API Gateway and Lambda for token validation.

## Implementation Strategy
1. Set up an Auth0 account and create a new application for Copper Print Gallery artist access.
2. Configure Auth0 to issue JWT tokens compatible with AWS services.
3. Implement token validation using a Lambda authorizer in API Gateway.
4. Update the Heroku-hosted frontend applications to obtain and include valid Auth0 tokens in API requests to AWS.
5. Store Auth0 configuration securely using AWS Secrets Manager for backend services and Heroku Config Vars for frontend applications.
6. Implement proper CORS configuration in API Gateway to allow authenticated requests from Heroku-hosted frontends.

## Consequences

### Positive
- Consistent authentication mechanism across our hybrid architecture.
- Reduced operational overhead due to managed service.
- Strong security features available for protecting artist access.
- Flexibility to add more authentication features or users in the future if needed.

### Negative
- Need to manage Auth0 configuration across two platforms (Heroku and AWS).
- Slight increase in complexity for token validation on AWS side.

### Risks
- Potential for token validation issues if Auth0 configuration isn't consistent between frontend and backend.
- Need to ensure proper handling of CORS for secure cross-origin requests.

## Related Decisions
- Hybrid Deployment Strategy with AWS-based Backend
- API Gateway configuration

## References
- Auth0 Documentation: [https://auth0.com/docs/](https://auth0.com/docs/)
- AWS API Gateway Lambda Authorizer: [https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- Auth0 with AWS Lambda: [https://auth0.com/docs/quickstart/backend/aws-api-gateway-custom-authorizer](https://auth0.com/docs/quickstart/backend/aws-api-gateway-custom-authorizer)