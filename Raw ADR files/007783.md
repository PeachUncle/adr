# ADR: Hybrid Deployment Strategy with AWS-based Backend for Copper Print Gallery

## Date
2024-07-31 (Updated: 2024-08-03)

## Status
Proposed

## Context
The Copper Print Gallery system needs a deployment environment that is cost-effective, scalable, and manageable. Our initial decision to use Heroku for all services proved to be more expensive than anticipated. We decided on a hybrid approach, and upon further analysis, we've identified that all backend services can be efficiently hosted on AWS.

## Decision
We have decided to:
1. Use Heroku for frontend services (Web Application, Artist Web Application)
2. Use AWS Lambda for all backend services (Content Management Service, Search Service, Image Processing Service)
3. Use Amazon API Gateway as the API Gateway for all backend services

## Rationale
1. Cost-Effectiveness: This approach leverages the cost benefits of serverless architecture for all backend services.
2. Scalability: AWS Lambda and Amazon API Gateway can automatically scale to handle varying loads.
3. Simplified Architecture: By hosting all backend services on AWS, we eliminate the need for cross-platform API routing.
4. Unified Backend Management: Using Amazon API Gateway for all backend services provides a single point of control for API routing, security, and monitoring.
5. Clear Separation: Frontend on Heroku, Backend on AWS creates a clear separation of concerns.

## Implementation Strategy
1. Deploy Web Application and Artist Web Application on Heroku.
2. Implement Content Management Service, Search Service, and Image Processing Service as AWS Lambda functions.
3. Set up Amazon API Gateway as the entry point for all backend API requests.
4. Configure frontend applications to make API calls to Amazon API Gateway.
5. Use AWS S3 for file storage (as previously decided).
6. Update CI/CD pipelines to handle deployments to both Heroku and AWS.
7. Implement comprehensive logging and monitoring across both environments.

## Consequences

### Positive
- Simplified backend architecture with all services on AWS.
- Improved scalability and performance for backend services.
- Clear separation between frontend and backend environments.
- Elimination of cross-platform API routing complexity.

### Negative
- Need to manage two different platforms (Heroku and AWS).
- Potential learning curve for team members not familiar with AWS services.

### Risks
- Dependency on AWS for all backend operations.
- Potential for increased latency between frontend and backend if not properly optimized.

## Mitigation Strategies
- Implement thorough monitoring and alerting for AWS services.
- Conduct performance testing to ensure acceptable latency between Heroku and AWS.
- Provide team training on AWS Lambda and API Gateway best practices.
- Regularly review and optimize AWS usage to manage costs.

## Specific Service Considerations
1. Content Management Service and Search Service:
    - Implement as Lambda functions, with direct integration to Amazon API Gateway.
    - Use Amazon Elasticsearch Service for the Search Service, which integrates well with Lambda.

2. Image Processing Service:
    - Leverage the existing asynchronous design, which aligns well with Lambda's execution model.
    - Use AWS Step Functions or SQS for managing long-running processes if needed.

3. Frontend Applications:
    - Update to make API calls to Amazon API Gateway instead of a Heroku-based API.
    - Implement proper CORS configuration in API Gateway to allow requests from Heroku-hosted frontends.

## Alternatives Considered
1. Full migration to AWS (including frontend services): Rejected to minimize disruption and leverage existing Heroku knowledge for frontend services.
2. Keeping some backend services on Heroku: Rejected to simplify the backend architecture and fully leverage AWS serverless capabilities.

## Related Decisions
- Configuration Management Strategy (to be updated for AWS-focused backend)
- Logging and Monitoring Strategy (to be updated for hybrid Heroku/AWS setup)
- Use of Amazon S3 for file storage

## References
- Amazon API Gateway: [https://aws.amazon.com/api-gateway/](https://aws.amazon.com/api-gateway/)
- AWS Lambda: [https://aws.amazon.com/lambda/](https://aws.amazon.com/lambda/)
- Heroku: [https://www.heroku.com/](https://www.heroku.com/)