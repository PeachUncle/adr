# ADR-003: Use Quarkus as Java Framework

## Status
Accepted

## Context
We need to select a Java framework for building the microservices that provides:

- Fast startup times for containerized environments
- Low memory footprint for efficient resource utilization
- Reactive programming capabilities for high-throughput message processing
- Native cloud integrations (Kafka, PostgreSQL, monitoring)
- Developer productivity with hot reload and good tooling
- Production-ready features (health checks, metrics, OpenAPI)

Traditional frameworks like Spring Boot, while mature, have longer startup times and higher memory usage, which can be problematic in containerized microservices environments.

## Decision
We will use Quarkus as the primary Java framework for both SMS Service and Processor Service.

**Version**: Quarkus 3.15.1 (latest stable)
**Java Version**: 17+ (LTS)
**Build Tool**: Maven

## Consequences

### Positive
- **Fast Startup**: Sub-second startup times improve container deployment speed
- **Low Memory Usage**: Smaller memory footprint allows for better container density
- **Native Compilation**: Option to compile to native binary with GraalVM for even better performance
- **Reactive First**: Built-in reactive programming support with SmallRye
- **Cloud Native**: Designed for Kubernetes and containerized environments
- **Developer Experience**: Excellent hot reload during development (`quarkus:dev`)
- **Extension Ecosystem**: Rich set of extensions for common integrations
- **Standards Compliance**: Implements MicroProfile and Jakarta EE standards
- **Modern Stack**: Uses latest Java features and reactive paradigms

### Negative
- **Smaller Ecosystem**: Fewer third-party libraries compared to Spring
- **Learning Curve**: Reactive programming concepts may be new to some developers
- **Maturity**: Newer framework with potentially less battle-tested in large enterprises
- **Native Compilation Complexity**: GraalVM native compilation can be complex for some dependencies
- **Limited Documentation**: Some advanced use cases may have less documentation

### Neutral
- **Different Paradigms**: Different approach from traditional Spring-based development
- **Extension Dependencies**: Need to use Quarkus-specific extensions for integrations
- **Configuration Style**: Uses MicroProfile Config instead of Spring's configuration

## Implementation Details

### Key Extensions Used

**Core Extensions**:
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-resteasy-reactive-jackson</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-orm-panache</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-jdbc-postgresql</artifactId>
</dependency>
```

**Messaging Extensions**:
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-messaging-kafka</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-reactive-messaging</artifactId>
</dependency>
```

**Observability Extensions**:
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-health</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-micrometer-registry-prometheus</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-openapi</artifactId>
</dependency>
```

### Configuration Management

**MicroProfile Config**:
```properties
# Database configuration
quarkus.datasource.db-kind=postgresql
quarkus.datasource.jdbc.url=${DATABASE_URL:jdbc:postgresql://localhost:5432/smsdb}
quarkus.datasource.username=${DATABASE_USER:smsuser}
quarkus.datasource.password=${DATABASE_PASSWORD:smspass}

# Kafka configuration
kafka.bootstrap.servers=${KAFKA_BOOTSTRAP_SERVERS:localhost:9092}

# OpenAPI configuration
quarkus.smallrye-openapi.info-title=SMS Service API
quarkus.smallrye-openapi.info-version=1.0.0
```

### Reactive Programming

**Message Producer**:
```java
@ApplicationScoped
public class MessageProducer {
    
    @Channel("sms-requests")
    Emitter<Message> emitter;
    
    public void sendSmsRequest(Message message) {
        emitter.send(message);
    }
}
```

**Message Consumer**:
```java
@ApplicationScoped
public class MessageConsumer {
    
    @Incoming("sms-requests")
    public CompletionStage<Void> process(Message message) {
        // Process message asynchronously
        return processMessage(message);
    }
}
```

### Development Features

**Hot Reload**:
```bash
# Start development mode with hot reload
./mvnw quarkus:dev

# Access dev UI
http://localhost:8080/q/dev/
```

**Testing Support**:
```java
@QuarkusTest
class MessageServiceTest {
    
    @Inject
    MessageService messageService;
    
    @Test
    void shouldSendMessage() {
        // Test implementation
    }
}
```

## Performance Characteristics

### Startup Time
- **JVM Mode**: ~2-3 seconds
- **Native Mode**: ~0.1 seconds

### Memory Usage
- **JVM Mode**: ~100-200MB heap
- **Native Mode**: ~50-100MB RSS

### Throughput
- **REST API**: 10,000+ requests/second
- **Kafka Processing**: 100,000+ messages/second

## Alternatives Considered

### Spring Boot
- **Pros**: Mature ecosystem, extensive documentation, large community
- **Cons**: Slower startup, higher memory usage, not optimized for containers
- **Decision**: Good framework but Quarkus better fits cloud-native requirements

### Micronaut
- **Pros**: Fast startup, low memory usage, compile-time DI
- **Cons**: Smaller ecosystem, different programming model
- **Decision**: Good alternative but Quarkus has better reactive integration

### Helidon
- **Pros**: Oracle-backed, reactive-first, microservices-focused
- **Cons**: Smaller community, less documentation, newer framework
- **Decision**: Promising but less mature ecosystem

### Vert.x
- **Pros**: Very high performance, fully reactive, polyglot
- **Cons**: Lower-level programming model, steeper learning curve
- **Decision**: Excellent performance but prefer higher-level abstractions

## Migration Considerations

### From Spring Boot
- **Configuration**: Convert `application.yml` to `application.properties`
- **Dependency Injection**: Convert Spring annotations to CDI
- **Data Access**: Convert Spring Data to Panache
- **Testing**: Convert Spring Test to QuarkusTest

### Learning Resources
- **Official Documentation**: https://quarkus.io/guides/
- **Training Materials**: Red Hat Developer resources
- **Community**: Quarkus Google Groups and Stack Overflow

## Future Considerations

### Native Compilation
- **Benefit**: Even faster startup and lower memory usage
- **Complexity**: Requires careful dependency management
- **Strategy**: Evaluate for production once application is stable

### Extension Development
- **Custom Extensions**: May need custom extensions for specific integrations
- **Contribution**: Opportunity to contribute back to Quarkus ecosystem

## Related Decisions
- [ADR-001: Use Microservices Architecture](001-microservices-architecture.md)
- [ADR-002: Use Apache Kafka as Message Broker](002-kafka-message-broker.md)
- [ADR-004: Use PostgreSQL as Primary Database](004-postgresql-database.md)
