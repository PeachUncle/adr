# ADR 0002: Extensibility for Tasks 2, 3, and 4

**Date**: 2025-10-18  
**Author**: Aditya R.  
**Status**: Accepted

## Context

Task 1 establishes the foundation. Tasks 2-4 will build upon this codebase with additional features:
- **Task 2**: Kubernetes-based execution
- **Task 3**: Consumer application
- **Task 4**: Advanced features (unspecified)

This ADR documents extension points and future work.

## Extension Points Already Implemented

### 1. CommandRunner Interface

**Current State**:
```java
public interface CommandRunner {
    TaskExecution execute(String command, String correlationId) throws Exception;
}
```

**Implementations**:
- ✅ `LocalCommandRunner`: Production-ready for Task 1
- ⏳ `KubernetesCommandRunner`: Stub (returns 501)

**Future Implementations** (Task 2):
- `KubernetesJobRunner`: Execute commands in Kubernetes Jobs
- `KubernetesPodRunner`: Execute in ephemeral pods
- `DockerRunner`: Execute in Docker containers

**Activation**:
```yaml
spring:
  profiles:
    active: k8s  # Activates KubernetesCommandRunner
```

### 2. Environment-Based Configuration

**Already Configured**:
- `MONGODB_URI`: Database connection (for containerization)
- `SERVER_PORT`: Application port (for Kubernetes Service)
- `POLICY_FILE`: Security policy location
- `AUDIT_LOG`: Audit trail location

**Task 2 Additions**:
- `KUBE_CONFIG`: Path to kubeconfig file
- `KUBE_NAMESPACE`: Kubernetes namespace for jobs
- `CONTAINER_IMAGE`: Image for job pods
- `RESOURCE_LIMITS_CPU`: CPU limit for jobs
- `RESOURCE_LIMITS_MEMORY`: Memory limit for jobs

### 3. Micrometer Metrics

**Current State**:
- Micrometer enabled
- Prometheus endpoint exposed: `/actuator/prometheus`
- Default JVM and HTTP metrics

**Task 2/3 Additions**:
- Custom metrics for command execution rates
- Task execution duration histograms
- Kubernetes job success/failure counters
- MongoDB query performance metrics

**Example**:
```java
@Timed(value = "task.execution", description = "Task execution time")
public TaskExecution execute(...) { ... }
```

### 4. OpenAPI Specification

**Current State**:
- Auto-generated from annotations
- Available at `/api-docs` and `api-spec/openapi.yaml`

**Task 3 Additions**:
- Consumer application can import spec for client generation
- API versioning support (`/api/v1`, `/api/v2`)

## TODOs for Task 2: Kubernetes Execution

### 2.1 Implement KubernetesCommandRunner

**File**: `src/main/java/dev/adityar/kaiburr/task1/service/KubernetesCommandRunner.java`

**Requirements**:
```java
@Service
@Profile("k8s")
public class KubernetesCommandRunner implements CommandRunner {
    
    @Autowired
    private KubernetesClient kubeClient;
    
    @Override
    public TaskExecution execute(String command, String correlationId) throws Exception {
        // 1. Create Job spec with command
        V1Job job = buildJobSpec(command, correlationId);
        
        // 2. Submit job to Kubernetes
        batchV1Api.createNamespacedJob(namespace, job, ...);
        
        // 3. Wait for job completion (with timeout)
        // 4. Retrieve logs from job pod
        // 5. Delete job (cleanup)
        // 6. Return TaskExecution with logs and exit code
    }
}
```

**Dependencies to Add**:
```xml
<dependency>
    <groupId>io.kubernetes</groupId>
    <artifactId>client-java</artifactId>
    <version>18.0.0</version>
</dependency>
```

### 2.2 Dockerfile

**File**: `Dockerfile`

```dockerfile
FROM maven:3.8-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Build**:
```bash
docker build -t kaiburr-task1:1.0.0 .
```

### 2.3 Kubernetes Manifests

**Directory**: `k8s/`

**Files**:
- `deployment.yaml`: Application deployment
- `service.yaml`: ClusterIP service
- `configmap.yaml`: Environment configuration
- `secret.yaml`: MongoDB credentials
- `rbac.yaml`: ServiceAccount + Role for Job creation

**Example Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kaiburr-task1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kaiburr-task1
  template:
    metadata:
      labels:
        app: kaiburr-task1
    spec:
      serviceAccountName: kaiburr-task1
      containers:
      - name: app
        image: kaiburr-task1:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongo-secret
              key: uri
        - name: SPRING_PROFILES_ACTIVE
          value: "k8s"
```

### 2.4 Helm Chart

**Directory**: `helm/kaiburr-task1/`

**Structure**:
```
helm/
└── kaiburr-task1/
    ├── Chart.yaml
    ├── values.yaml
    ├── templates/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── configmap.yaml
    │   ├── secret.yaml
    │   └── rbac.yaml
    └── README.md
```

**Install**:
```bash
helm install kaiburr-task1 ./helm/kaiburr-task1 \
  --set mongodb.uri=mongodb://... \
  --set image.tag=1.0.0
```

## TODOs for Task 3: Consumer Application

### 3.1 REST Client Library

**Option 1**: OpenAPI Generator
```bash
openapi-generator-cli generate \
  -i api-spec/openapi.yaml \
  -g java \
  -o client/kaiburr-client
```

**Option 2**: Spring Cloud OpenFeign
```java
@FeignClient(name = "kaiburr-task1", url = "${kaiburr.url}")
public interface TaskClient {
    @PutMapping("/api/tasks")
    TaskResponse createTask(@RequestBody TaskRequest request);
    
    @GetMapping("/api/tasks/{id}")
    TaskResponse getTask(@PathVariable String id);
}
```

### 3.2 WebSocket for Real-Time Updates

**Enhancement**: Add WebSocket endpoint for execution progress

**File**: `src/main/java/dev/adityar/kaiburr/task1/websocket/TaskExecutionWebSocket.java`

```java
@ServerEndpoint("/ws/tasks/{taskId}/executions")
public class TaskExecutionWebSocket {
    @OnOpen
    public void onOpen(Session session, @PathParam("taskId") String taskId) {
        // Subscribe to task execution updates
    }
    
    @OnMessage
    public void onMessage(String message, Session session) {
        // Handle client messages (e.g., cancel execution)
    }
}
```

**Consumer Usage**:
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/tasks/task-001/executions');
ws.onmessage = (event) => {
    const execution = JSON.parse(event.data);
    console.log('Progress:', execution.progress);
};
```

### 3.3 GraphQL API (Alternative)

**Enhancement**: Add GraphQL layer for flexible querying

**Dependencies**:
```xml
<dependency>
    <groupId>com.graphql-java-kickstart</groupId>
    <artifactId>graphql-spring-boot-starter</artifactId>
    <version>15.0.0</version>
</dependency>
```

**Schema** (`src/main/resources/graphql/schema.graphqls`):
```graphql
type Task {
    id: ID!
    name: String!
    owner: String!
    command: String!
    executions: [TaskExecution!]!
}

type Query {
    task(id: ID!): Task
    tasks(page: Int, size: Int): [Task!]!
    searchTasks(name: String!): [Task!]!
}

type Mutation {
    createTask(input: TaskInput!): Task!
    executeTask(id: ID!): TaskExecution!
}
```

## TODOs for Task 4: Advanced Features

### 4.1 Authentication & Authorization

**Spring Security** with JWT:
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/tasks/**").hasRole("USER")
                .requestMatchers("/api/validation/**").permitAll()
            )
            .oauth2ResourceServer(OAuth2ResourceServerConfigurer::jwt);
        return http.build();
    }
}
```

**Owner-based Access Control**:
- Users can only execute/delete their own tasks
- Admins can manage all tasks

### 4.2 Rate Limiting

**Bucket4j** integration:
```java
@RateLimiter(name = "taskExecution", fallbackMethod = "rateLimitFallback")
public TaskExecutionResponse executeTask(String id) { ... }
```

**Configuration**:
```yaml
resilience4j:
  ratelimiter:
    instances:
      taskExecution:
        limitForPeriod: 10
        limitRefreshPeriod: 1m
        timeoutDuration: 0
```

### 4.3 Event Sourcing

**MongoDB Change Streams** for audit trail:
```java
@Component
public class TaskEventListener {
    @EventListener
    public void onTaskExecuted(TaskExecutedEvent event) {
        // Publish to Kafka/RabbitMQ
        // Update read models
        // Trigger webhooks
    }
}
```

### 4.4 S3 Integration for Large Outputs

**Conditional Storage**:
- Outputs < 64 KiB: Store in MongoDB
- Outputs > 64 KiB: Upload to S3, store reference

```java
if (stdout.length() > 65536) {
    String s3Key = s3Service.upload(stdout, correlationId);
    execution.setStdoutLocation("s3://" + bucket + "/" + s3Key);
} else {
    execution.setStdout(stdout);
}
```

## Migration Path

### Phase 1: Task 1 (Current)
- ✅ Local execution
- ✅ MongoDB persistence
- ✅ REST API
- ✅ Security validation

### Phase 2: Task 2 (Kubernetes)
- 🔲 Kubernetes runner implementation
- 🔲 Docker image
- 🔲 Helm chart
- 🔲 CI/CD pipeline

### Phase 3: Task 3 (Consumer)
- 🔲 Client library
- 🔲 WebSocket support
- 🔲 GraphQL API (optional)
- 🔲 Example consumer app

### Phase 4: Task 4 (Advanced)
- 🔲 Authentication/Authorization
- 🔲 Rate limiting
- 🔲 Event sourcing
- 🔲 S3 integration
- 🔲 Multi-tenancy

## Database Schema Evolution

**Current** (Task 1):
```javascript
{
  _id: "task-001",
  name: "...",
  owner: "...",
  command: "...",
  taskExecutions: [
    { startTime, endTime, exitCode, stdout, stderr, correlationId }
  ]
}
```

**Future** (Task 2+):
```javascript
{
  _id: "task-001",
  name: "...",
  owner: "...",
  command: "...",
  executionStrategy: "local|kubernetes|docker",  // NEW
  kubernetesConfig: { ... },                     // NEW
  taskExecutions: [
    {
      startTime, endTime, exitCode,
      stdoutLocation: "s3://..." | "inline",     // CHANGED
      stderrLocation: "s3://..." | "inline",     // CHANGED
      correlationId,
      executedBy: "local|k8s-job-xyz",           // NEW
      resourceUsage: { cpu, memory }             // NEW
    }
  ]
}
```

**Migration**:
- Add fields with defaults
- Maintain backward compatibility
- Use MongoDB schema versioning

## Consequences

### Positive
- ✅ Clear upgrade path to Kubernetes
- ✅ Minimal code changes required
- ✅ Existing tests remain valid
- ✅ API contract stability

### Challenges
- ⚠️ Kubernetes complexity (RBAC, networking)
- ⚠️ State management in distributed system
- ⚠️ Testing in Kubernetes environment

## References

- Kubernetes API Documentation
- Spring Cloud Kubernetes
- Helm Best Practices
- Twelve-Factor App

---

**Related**: [ADR 0001: Architecture Decisions](0001-decisions.md)
