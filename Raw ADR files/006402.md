# ADR-023: Containerization Strategy

## Status
Proposed

## Date
2025-03-02

## Context
Our Aronim Bookstore application requires a consistent, portable, and scalable deployment approach across different environments (development, testing, staging, and production). We need a containerization strategy that:

- Ensures consistency between development and production environments
- Simplifies deployment and scaling of our application
- Supports our microservices architecture and deployment patterns
- Facilitates DevOps practices and CI/CD pipeline integration
- Optimizes resource utilization and startup performance
- Addresses security concerns for containerized applications
- Provides proper monitoring and observability for containers
- Enables efficient local development workflows
- Supports our Java-based Spring Boot application
- Aligns with industry best practices and standards

Without a well-defined containerization strategy, we risk inconsistent deployments, inefficient resource usage, security vulnerabilities, and operational challenges as our application grows.

## Decision
We will implement a comprehensive containerization strategy using **Docker** with the following components:

### 1. Container Base Images
- Use **Eclipse Temurin** (formerly AdoptOpenJDK) as our Java base image
- Implement multi-stage builds to minimize image size
- Standardize on Alpine-based images where appropriate
- Establish versioning strategy for base images
- Create custom base images for shared requirements

### 2. Image Layering Strategy
- Optimize layer caching for faster builds and deployments
- Separate dependencies from application code
- Group related operations to minimize layer count
- Implement proper layer ordering for caching efficiency
- Document layer strategy for consistent implementation

### 3. Configuration Management
- Use environment variables for runtime configuration
- Implement secrets management using appropriate tools
- Externalize configuration from container images
- Follow the twelve-factor app methodology
- Create appropriate configuration templates

### 4. Container Security
- Implement least privilege principle for container execution
- Scan images for vulnerabilities using appropriate tools
- Use non-root users for running applications
- Apply security hardening to container images
- Establish image signing and verification process

### 5. Development Workflow
- Implement Docker Compose for local development
- Create dev-specific container configurations
- Support hot reloading for development efficiency
- Provide debugging capabilities for containerized applications
- Document container-based development practices

### 6. Orchestration Preparation
- Design containers for Kubernetes compatibility
- Implement proper health checks and probes
- Define resource requirements and limits
- Support zero-downtime deployments
- Structure containers for horizontal scaling

## Implementation Approach

1. **Base Image Selection**
   - Standardize on Eclipse Temurin JDK 21 for Java applications
   - Use slim variants for runtime images
   - Document base image selection criteria
   - Establish image update process

2. **Dockerfile Design**
   - Create optimized multi-stage build Dockerfiles
   - Separate build and runtime environments
   - Implement proper layer caching strategy
   - Document Dockerfile best practices

3. **Local Development**
   - Configure Docker Compose for local environment
   - Implement volume mounting for code changes
   - Set up debugging configuration
   - Document local development workflow

4. **CI/CD Integration**
   - Implement container building in CI pipeline
   - Configure automated testing of containers
   - Set up image scanning and security validation
   - Establish image promotion process between environments

5. **Monitoring and Observability**
   - Configure container health checks
   - Implement logging strategy for containers
   - Set up metrics collection from containers
   - Document monitoring approach

## Consequences

### Positive
- Consistent environments across development and production
- Improved deployment reliability and speed
- Better resource utilization and isolation
- Enhanced security through isolation and scanning
- Simplified scaling and orchestration
- Improved developer productivity with consistent environments
- Faster onboarding for new team members
- Better support for CI/CD practices
- Reduced "works on my machine" issues
- Simplified dependency management

### Negative
- Learning curve for containerization concepts
- Additional complexity in build and deployment pipeline
- Potential performance overhead compared to bare metal
- Need for container-specific monitoring and management
- Security considerations specific to containers
- Additional operational knowledge requirements
- Potential challenges with stateful services
- Need for careful resource management

## Alternatives Considered

1. **Virtual Machines**
   - Stronger isolation between applications
   - Higher resource overhead
   - Slower startup times
   - More complex management
   - Less efficient for microservices architecture

2. **Platform-as-a-Service (PaaS)**
   - Simpler deployment model
   - Less control over infrastructure
   - Potential vendor lock-in
   - Higher costs at scale
   - Less customization options

3. **Serverless Deployment**
   - Lower operational overhead
   - Pay-per-use pricing model
   - Cold start latency issues
   - Less control over runtime environment
   - Potential challenges with long-running processes

4. **Traditional Deployment**
   - Familiar approach for many teams
   - Direct access to underlying system
   - Environment inconsistency issues
   - More complex scaling
   - Higher operational overhead

## Implementation Notes

### Multi-Stage Dockerfile Example

```dockerfile
# Stage 1: Build stage
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app

# Copy gradle files first for better layer caching
COPY gradle/ gradle/
COPY gradlew build.gradle.kts settings.gradle.kts ./
COPY gradle.properties ./
RUN chmod +x ./gradlew

# Download dependencies first (will be cached if no changes)
RUN ./gradlew dependencies --no-daemon

# Copy source code and build
COPY src/ src/
RUN ./gradlew build --no-daemon -x test

# Stage 2: Runtime stage
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Configuration and application metadata
LABEL org.opencontainers.image.title="Aronim Bookstore"
LABEL org.opencontainers.image.description="Bookstore Application"
LABEL org.opencontainers.image.version="1.0.0"

# Set environment variables
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
ENV SPRING_PROFILES_ACTIVE="production"

# Copy the built artifact from the builder stage
COPY --from=builder /app/build/libs/*.jar app.jar

# Expose application port
EXPOSE 8080

# Configure health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD wget -q --spider http://localhost:8080/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Docker Compose for Local Development

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8080:8080"
      - "5005:5005"  # For remote debugging
    environment:
      - SPRING_PROFILES_ACTIVE=dev
      - SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/bookstore
      - SPRING_DATASOURCE_USERNAME=postgres
      - SPRING_DATASOURCE_PASSWORD=postgres
      - JAVA_TOOL_OPTIONS=-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
    volumes:
      - ./:/app
      - gradle-cache:/home/gradle/.gradle
    depends_on:
      - db
      - keycloak

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=bookstore
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  keycloak:
    image: quay.io/keycloak/keycloak:21.0
    command: ["start-dev"]
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=admin
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://db:5432/keycloak
      - KC_DB_USERNAME=postgres
      - KC_DB_PASSWORD=postgres
    ports:
      - "8081:8080"
    depends_on:
      - db

volumes:
  postgres-data:
  gradle-cache:
```

### Development-Specific Dockerfile

```dockerfile
# Dockerfile.dev - Optimized for development
FROM eclipse-temurin:21-jdk-alpine
WORKDIR /app

# Install development tools
RUN apk add --no-cache curl jq bash

# Create non-root user but with sufficient permissions for development
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app
USER appuser

# We'll mount the source code from the host
VOLUME ["/app"]

# Use Gradle for development mode
ENTRYPOINT ["./gradlew", "bootRun", "--no-daemon"]
```

### Container Security Scanning in CI/CD

```yaml
# GitHub Actions workflow excerpt
jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
      
      - name: Build with Gradle
        run: ./gradlew build
      
      - name: Build Docker image
        run: docker build -t aronim-bookstore:${{ github.sha }} .
      
      - name: Scan Docker image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'aronim-bookstore:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
          ignore-unfixed: true
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
```

### Kubernetes Deployment Example

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aronim-bookstore
  labels:
    app: aronim-bookstore
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aronim-bookstore
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    metadata:
      labels:
        app: aronim-bookstore
    spec:
      containers:
        - name: app
          image: aronim-bookstore:${VERSION}
          imagePullPolicy: Always
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "production"
            - name: SPRING_DATASOURCE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
            - name: SPRING_DATASOURCE_USERNAME
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: username
            - name: SPRING_DATASOURCE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - ALL
```

### Container Image Tagging Strategy

```bash
#!/bin/bash
# Example script for tagging container images

# Get the version from Gradle properties
VERSION=$(./gradlew properties -q | grep "version:" | awk '{print $2}')

# Get the Git commit hash
GIT_COMMIT=$(git rev-parse --short HEAD)

# Tag formats
LATEST_TAG="aronim-bookstore:latest"
VERSION_TAG="aronim-bookstore:${VERSION}"
COMMIT_TAG="aronim-bookstore:${VERSION}-${GIT_COMMIT}"

# Build the image
docker build -t ${LATEST_TAG} -t ${VERSION_TAG} -t ${COMMIT_TAG} .

# For production releases, also push to registry
if [[ "$ENVIRONMENT" == "production" ]]; then
    REGISTRY="registry.example.com"
    
    docker tag ${LATEST_TAG} ${REGISTRY}/${LATEST_TAG}
    docker tag ${VERSION_TAG} ${REGISTRY}/${VERSION_TAG}
    docker tag ${COMMIT_TAG} ${REGISTRY}/${COMMIT_TAG}
    
    docker push ${REGISTRY}/${LATEST_TAG}
    docker push ${REGISTRY}/${VERSION_TAG}
    docker push ${REGISTRY}/${COMMIT_TAG}
fi
```

### JVM Container Configuration

```bash
#!/bin/bash
# Example entrypoint script with JVM configuration for containers

# Calculate container memory limit
if [ -f /sys/fs/cgroup/memory/memory.limit_in_bytes ]; then
  MEMORY_LIMIT_IN_BYTES=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)
else
  MEMORY_LIMIT_IN_BYTES=$(cat /proc/meminfo | grep MemTotal | awk '{print $2 * 1024}')
fi

# Set JVM options based on container memory
if [ ${MEMORY_LIMIT_IN_BYTES} -lt 1073741824 ]; then
  # Less than 1GB
  JAVA_OPTS="${JAVA_OPTS} -XX:MaxRAMPercentage=70.0"
else
  # 1GB or more
  JAVA_OPTS="${JAVA_OPTS} -XX:MaxRAMPercentage=80.0"
fi

# Enable GC logging for monitoring
JAVA_OPTS="${JAVA_OPTS} -Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags:filecount=5,filesize=10M"

# Set timezone if provided
if [ ! -z "$TZ" ]; then
  JAVA_OPTS="${JAVA_OPTS} -Duser.timezone=${TZ}"
fi

# Execute the application
exec java ${JAVA_OPTS} -jar app.jar
```

## Container Registry Strategy

We will use a private container registry for storing and distributing our container images, with the following structure:

- **Development images**: `registry.example.com/aronim-bookstore/dev:{tag}`
- **Testing images**: `registry.example.com/aronim-bookstore/test:{tag}`
- **Release candidates**: `registry.example.com/aronim-bookstore/rc:{version}-{build}`
- **Production images**: `registry.example.com/aronim-bookstore/prod:{version}`

This structure allows for proper separation of images across environments and facilitates our CI/CD promotion process.

## Compliance Verification
- Security scanning of container images
- Verification of container configuration and hardening
- Testing of containers in CI/CD pipeline
- Validation of resource requirements and limits
- Performance testing of containerized application
- Verification of monitoring and observability setup
- Documentation review for containerization practices

## References
- Docker Documentation: https://docs.docker.com/
- Java Containerization Best Practices: https://www.oracle.com/java/technologies/javase/jdk-containers.html
- Spring Boot Container Documentation: https://spring.io/guides/topicals/spring-boot-docker
- Container Security Best Practices: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- Twelve-Factor App Methodology: https://12factor.net/
- Eclipse Temurin Images: https://hub.docker.com/_/eclipse-temurin
- Kubernetes Documentation: https://kubernetes.io/docs/home/
