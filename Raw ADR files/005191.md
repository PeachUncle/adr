# ADR-00006: Deployment and Infrastructure Architecture

## Status
**Accepted** - 2024-09-28

## Context
The AGoat Publisher system needs a reliable, scalable deployment architecture that supports development, staging, and production environments. The system must handle both content management and business-specific functionality while maintaining high availability and security.

## Decision
Implement a cloud-native deployment architecture using:
- **Google Cloud Platform (GCP)** as the primary cloud provider
- **CockroachDB** for distributed database hosting
- **Google Cloud Secrets Manager** for secure configuration management
- **Docker containers** for application deployment
- **Local development environment** with unified startup scripts
- **Environment-specific configurations** for dev/staging/production
- **Automated deployment pipelines** with CI/CD

## Rationale
1. **Cloud-Native**: GCP provides managed services and scalability
2. **Database Reliability**: CockroachDB provides distributed, fault-tolerant database
3. **Security**: GCP Secrets Manager provides secure configuration management
4. **Consistency**: Docker containers ensure consistent deployment across environments
5. **Development Experience**: Local development environment with hot reload
6. **Scalability**: Cloud-native architecture supports horizontal scaling
7. **Monitoring**: Integrated monitoring and logging capabilities

## Consequences

### Positive
- **Scalability**: Cloud-native architecture supports growth
- **Reliability**: Managed services provide high availability
- **Security**: Secure configuration management and encryption
- **Consistency**: Docker containers ensure consistent deployments
- **Development Experience**: Fast local development with hot reload
- **Monitoring**: Integrated observability and logging
- **Cost Efficiency**: Pay-as-you-scale pricing model

### Negative
- **Vendor Lock-in**: Dependency on GCP services
- **Complexity**: More complex infrastructure management
- **Learning Curve**: Team needs cloud and container expertise
- **Cost**: Cloud services can be expensive at scale
- **Latency**: Network latency for distributed services

## Implementation Details

### Infrastructure Components
```bash
# Development Environment
- Local Go API server (port 8080)
- Local React frontend (port 3000)
- CockroachDB connection via GCP
- GCP Secrets Manager for configuration
- Hot reload with Air tool
- Vite dev server for frontend

# Production Environment
- GCP Cloud Run for API deployment
- GCP Cloud Run for frontend deployment
- CockroachDB managed service
- GCP Secrets Manager for secrets
- GCP Load Balancer for traffic distribution
- GCP Cloud CDN for static assets
```

### Configuration Management
```bash
# GCP Secrets
- agoat-publisher-db-main-cockroach-ca
- agoat-publisher-db-main-cockroach-dsn
- OIDC provider configurations
- API keys and certificates

# Environment Variables
- GCP_PROJECT=agoat-publisher-dev
- DATABASE_DSN (from secrets)
- CA_CERTIFICATE (from secrets)
- OIDC_PROVIDER_CONFIGS
```

### Deployment Architecture
1. **Development**: Local development with unified startup script
2. **Staging**: GCP Cloud Run with staging database
3. **Production**: GCP Cloud Run with production database
4. **CI/CD**: Automated deployment pipelines
5. **Monitoring**: GCP Cloud Monitoring and Logging

### Key Features
1. **Unified Startup**: Single script starts entire development environment
2. **Hot Reload**: Automatic code reloading for development
3. **Secret Management**: Secure configuration via GCP Secrets Manager
4. **Database Connectivity**: Secure CockroachDB connections
5. **Environment Isolation**: Separate environments for dev/staging/prod
6. **Health Checks**: System monitoring and health endpoints

### Security Measures
- Secure secret management with GCP Secrets Manager
- Encrypted database connections
- Environment-specific configurations
- Network security with VPC and firewalls
- Access control with IAM roles
- Audit logging for all operations

### Development Workflow
1. **Local Development**: Unified startup script for full stack
2. **Code Changes**: Hot reload for immediate feedback
3. **Testing**: Local testing with staging database
4. **Deployment**: Automated deployment to staging/production
5. **Monitoring**: Real-time monitoring and alerting

### Monitoring and Observability
- GCP Cloud Monitoring for system metrics
- GCP Cloud Logging for application logs
- Health check endpoints for service monitoring
- Performance metrics and alerting
- Error tracking and debugging

## References
- [Google Cloud Platform Documentation](https://cloud.google.com/docs)
- [CockroachDB Cloud Documentation](https://www.cockroachlabs.com/docs/cockroachcloud/)
- [Docker Documentation](https://docs.docker.com/)
- [GCP Secrets Manager Documentation](https://cloud.google.com/secret-manager)
- [Deployment Requirements](../../requirements-and-user-stories/final-nonfunctional/reliability-requirements.md)
- [Security Requirements](../../requirements-and-user-stories/final-nonfunctional/security-requirements.md)
- [Startup Script](../../local-scripts/start-full-stack-unified.sh)
