# ADR-005: Use Docker for Containerization

## Status
Accepted

## Context
The SMS messaging platform consists of multiple services and infrastructure components that need to be deployed consistently across development, testing, and production environments. We need a containerization strategy that provides:

- Consistent deployment across environments
- Easy dependency management
- Simplified local development setup
- Production-ready deployment option
- Service isolation and resource management
- Integration with CI/CD pipelines

Traditional deployment methods involve complex server setup, dependency management, and environment-specific configuration issues.

## Decision
We will use Docker for containerizing all application services and infrastructure components, with Docker Compose for local development and orchestration.

**Components to Containerize**:
- SMS Service (Quarkus application)
- Processor Service (Quarkus application)  
- PostgreSQL database
- Apache Kafka
- Monitoring stack (Prometheus, Grafana)
- Kafka UI for development

## Consequences

### Positive
- **Environment Consistency**: Identical deployment across dev, test, and production
- **Simplified Dependencies**: All dependencies packaged within containers
- **Easy Local Setup**: Single command deployment for development
- **Isolation**: Services run in isolated environments with resource limits
- **Scalability**: Easy horizontal scaling of services
- **CI/CD Integration**: Natural fit for automated build and deployment pipelines
- **Version Control**: Infrastructure as code with versioned images
- **Developer Onboarding**: New developers can start quickly with minimal setup

### Negative
- **Operational Complexity**: Need to understand Docker concepts and operations
- **Resource Overhead**: Container runtime overhead compared to native deployment
- **Security Considerations**: Need to manage container security and vulnerabilities
- **Debugging Complexity**: Additional layer for debugging and troubleshooting
- **Storage Management**: Need to handle persistent data and volumes properly

### Neutral
- **Learning Curve**: Team needs Docker knowledge
- **Tooling Requirements**: Need Docker-related tools and monitoring
- **Image Management**: Need container registry and image lifecycle management

## Implementation Details

### Service Containerization

**SMS Service Dockerfile**:
```dockerfile
# Multi-stage build for optimized production image
FROM eclipse-temurin:17-jdk-jammy AS build
WORKDIR /code
COPY pom.xml /code/pom.xml
COPY src /code/src
RUN apt-get update && apt-get install -y maven
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-jammy
RUN apt-get update && apt-get install -y curl
COPY --from=build /code/target/quarkus-app/ /deployments/
EXPOSE 8080
CMD ["java", "-jar", "/deployments/quarkus-run.jar"]
```

**Processor Service Dockerfile**:
```dockerfile
FROM eclipse-temurin:17-jdk-jammy AS build
WORKDIR /code  
COPY pom.xml /code/pom.xml
COPY src /code/src
RUN apt-get update && apt-get install -y maven
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-jammy
RUN apt-get update && apt-get install -y curl
COPY --from=build /code/target/quarkus-app/ /deployments/
EXPOSE 8081
CMD ["java", "-jar", "/deployments/quarkus-run.jar"]
```

### Docker Compose Configuration

**Development Setup** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: sms-postgres
    environment:
      POSTGRES_DB: smsdb
      POSTGRES_USER: smsuser
      POSTGRES_PASSWORD: smspass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U smsuser -d smsdb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - sms-network

  kafka:
    image: confluentinc/cp-kafka:7.8.0
    container_name: sms-kafka
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_LISTENERS: CONTROLLER://0.0.0.0:29093,PLAINTEXT://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:29093
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LOG_DIRS: /var/lib/kafka/data
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: true
    volumes:
      - kafka_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5
    networks:
      - sms-network

  sms-service:
    build: ./service-sms
    container_name: sms-service
    environment:
      QUARKUS_DATASOURCE_JDBC_URL: jdbc:postgresql://postgres:5432/smsdb
      QUARKUS_DATASOURCE_USERNAME: smsuser
      QUARKUS_DATASOURCE_PASSWORD: smspass
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/q/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sms-network

volumes:
  postgres_data:
  kafka_data:

networks:
  sms-network:
    driver: bridge
```

### Build Optimization

**Multi-stage Builds**:
- **Build Stage**: Compile and package application
- **Runtime Stage**: Minimal runtime environment with JRE
- **Layer Caching**: Optimize Docker layer caching for faster builds

**Image Size Optimization**:
```dockerfile
# Use Alpine images for smaller size
FROM eclipse-temurin:17-jre-alpine

# Remove unnecessary packages
RUN apk --no-cache del build-dependencies

# Use specific tags instead of 'latest'
FROM postgres:16-alpine
```

### Health Checks

**Application Health Checks**:
```dockerfile
# In Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/q/health || exit 1
```

**Dependency Health Checks**:
```yaml
# In docker-compose.yml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U smsuser -d smsdb"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

## Development Workflow

### Local Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f sms-service

# Rebuild specific service
docker-compose build sms-service
docker-compose up -d sms-service

# Stop all services
docker-compose down

# Clean up volumes (caution: destroys data)
docker-compose down -v
```

### Debugging
```bash
# Access container shell
docker exec -it sms-service /bin/bash

# View container logs
docker logs sms-service --follow

# Monitor resource usage
docker stats
```

### Testing
```bash
# Run tests in container
docker run --rm -v $(pwd):/workspace -w /workspace maven:3.8-openjdk-17 mvn test

# Integration testing with test containers
./mvnw verify -Dquarkus.profile=test
```

## Production Considerations

### Image Security
```dockerfile
# Use non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup
USER appuser

# Scan for vulnerabilities
# docker scout cves sms-service:latest
```

### Resource Limits
```yaml
services:
  sms-service:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25' 
          memory: 256M
```

### Environment-specific Configurations
```yaml
# docker-compose.prod.yml
services:
  sms-service:
    image: sms-service:${TAG:-latest}
    environment:
      QUARKUS_LOG_LEVEL: INFO
      JAVA_OPTS: "-Xms256m -Xmx512m"
```

## Container Registry

### Image Tagging Strategy
```bash
# Build with version tag
docker build -t sms-service:1.0.0 ./service-sms
docker build -t sms-service:latest ./service-sms

# Tag for registry
docker tag sms-service:1.0.0 registry.company.com/sms-service:1.0.0
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Build and push Docker image
  uses: docker/build-push-action@v4
  with:
    context: ./service-sms
    push: true
    tags: |
      registry.company.com/sms-service:latest
      registry.company.com/sms-service:${{ github.sha }}
```

## Monitoring and Logging

### Centralized Logging
```yaml
services:
  sms-service:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Container Metrics
```yaml
# Add cAdvisor for container metrics
cadvisor:
  image: gcr.io/cadvisor/cadvisor:latest
  container_name: cadvisor
  ports:
    - "8888:8080"
  volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:ro
    - /sys:/sys:ro
    - /var/lib/docker/:/var/lib/docker:ro
```

## Alternatives Considered

### Virtual Machines
- **Pros**: Better isolation, familiar operational model
- **Cons**: Higher resource overhead, slower startup, complex dependency management
- **Decision**: Docker provides better resource utilization and deployment speed

### Kubernetes from Start
- **Pros**: Production-grade orchestration, auto-scaling, service discovery
- **Cons**: High complexity for initial development, steep learning curve
- **Decision**: Docker Compose for development, Kubernetes as future migration path

### Podman
- **Pros**: Daemonless, rootless containers, Docker-compatible
- **Cons**: Smaller ecosystem, less mature tooling
- **Decision**: Docker has better ecosystem and team familiarity

### Serverless (AWS Lambda, etc.)
- **Pros**: No server management, automatic scaling, pay-per-use
- **Cons**: Vendor lock-in, cold start latency, limited runtime environments
- **Decision**: Considered for future but need more control for current requirements

## Migration Strategy

### From Traditional Deployment
1. **Containerize Services**: Start with application services
2. **Infrastructure Migration**: Move databases and message brokers to containers
3. **Orchestration**: Add Docker Compose for local development
4. **Production Deployment**: Gradual migration to containerized production

### Future Kubernetes Migration
1. **Helm Charts**: Create Kubernetes manifests
2. **Service Mesh**: Consider Istio for advanced networking
3. **Monitoring**: Kubernetes-native monitoring stack
4. **Storage**: Migrate to Kubernetes persistent volumes

## Best Practices

### Dockerfile Best Practices
- Use specific base image tags
- Minimize number of layers
- Use multi-stage builds
- Don't run as root user
- Use .dockerignore file
- Keep images small and focused

### Docker Compose Best Practices
- Use named volumes for persistent data
- Define networks explicitly
- Use health checks for dependencies
- Environment-specific override files
- Use secrets for sensitive data

### Security Best Practices
- Regular image updates
- Vulnerability scanning
- Non-root containers
- Resource limits
- Network segmentation
- Secrets management

## Related Decisions
- [ADR-001: Use Microservices Architecture](001-microservices-architecture.md)
- [ADR-003: Use Quarkus as Java Framework](003-quarkus-framework.md)
- [ADR-004: Use PostgreSQL as Primary Database](004-postgresql-database.md)
