# ADR: Use AWS CloudWatch for Logging and Monitoring in Copper Print Gallery

## Date
2024-07-31 (Updated: 2024-08-14)

## Context
The Copper Print Gallery system requires logging and monitoring capabilities to ensure system health and facilitate troubleshooting. Our hybrid architecture, with frontend services on Heroku and backend services on AWS, presents challenges for implementing a unified logging and monitoring solution.

## Decision
We have decided to use AWS CloudWatch as our primary logging and monitoring solution for the Copper Print Gallery system, with log forwarding from Heroku to CloudWatch.

## Rationale
1. Centralization: CloudWatch provides a unified platform for logs and metrics from both AWS services and external sources.
2. Integration: Native integration with our AWS-based backend services.
3. Scalability: CloudWatch can handle logging and monitoring needs as our system grows.
4. Cost-effectiveness: Consolidating on AWS services may be more cost-effective than using multiple third-party solutions.
5. Flexibility: Allows for custom metrics and logs from both Heroku and AWS components.

## Implementation Strategy
1. Configure AWS Lambda functions and API Gateway to log directly to CloudWatch Logs.
2. Set up a log drain in Heroku to forward logs from frontend applications to CloudWatch Logs.
3. Implement custom metrics publication from Heroku applications to CloudWatch.
4. Develop a consistent log format across all services, including correlation IDs for tracing requests across the system.
5. Create CloudWatch Dashboards for visualizing key metrics from both Heroku and AWS components.
6. Set up CloudWatch Alarms for critical metrics and log patterns.

## Consequences

### Positive
- Unified view of system behavior and performance across our hybrid architecture.
- Simplified operations by centralizing on AWS tools.
- Powerful querying and visualization capabilities for logs and metrics.

### Negative
- Increased complexity in Heroku application configuration for log forwarding and metric publication.
- Learning curve for team members not familiar with CloudWatch.

### Risks
- Potential increased AWS costs for log ingestion, storage, and processing.
- Possible delays or data loss in log forwarding from Heroku to CloudWatch.

## Mitigation Strategies
- Implement robust error handling and retry mechanisms in log forwarding and metric publication processes.
- Regularly audit logging and monitoring setup to ensure all components are properly integrated.
- Provide team training on CloudWatch tools and best practices.
- Implement log retention policies and metric filter to manage costs.

## Monitoring Plan
1. Real-time: Set up CloudWatch Alarms for immediate notification of critical issues.
2. Daily: Review CloudWatch Dashboards for system health and performance trends.
3. Weekly: Analyze log data for patterns and potential optimizations.
4. Monthly: Review and adjust logging and monitoring strategy based on gathered insights.

## Related Decisions
- Hybrid Deployment Strategy with AWS-based Backend
- Use of Auth0 for authentication (for monitoring authentication-related events)

## References
- AWS CloudWatch: [https://aws.amazon.com/cloudwatch/](https://aws.amazon.com/cloudwatch/)
- Heroku Log Drains: [https://devcenter.heroku.com/articles/log-drains](https://devcenter.heroku.com/articles/log-drains)
- CloudWatch Logs Insights: [https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)