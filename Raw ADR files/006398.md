# ADR-019: Logging Framework and Standards for Spring Boot Application

## Status
Accepted

## Date
2025-03-01

## Context
Our Spring Boot application requires a comprehensive and consistent logging approach to support development, debugging, monitoring, and troubleshooting. We need a logging strategy that:

- Provides visibility into application behavior across environments
- Enables effective debugging and troubleshooting
- Supports operational monitoring and alerting
- Maintains appropriate security and privacy controls for sensitive data
- Integrates well with our Spring Boot architecture
- Scales with our application growth
- Minimizes performance impact
- Supports structured logging for better searchability and analysis
- Aligns with our overall observability strategy
- Enables correlation of events across distributed systems

Without a standardized logging approach, we risk inconsistent log quality, missing critical information during incidents, performance issues from inefficient logging, and security/compliance concerns from improper handling of sensitive data.

## Decision
We will implement a standardized logging strategy using **SLF4J** with **Logback** as the implementation, enhanced with the following components:

### 1. Logging Framework
- Use **SLF4J** as the logging facade
- Implement **Logback** as the logging framework
- Configure JSON output format for production environments
- Use human-readable format for development environments
- Implement MDC (Mapped Diagnostic Context) for request tracing

### 2. Logging Levels and Usage
- Define clear guidelines for appropriate use of each log level:
  - **ERROR**: Application errors requiring immediate attention
  - **WARN**: Potential issues or unexpected events that don't cause application failure
  - **INFO**: Significant application events and milestones
  - **DEBUG**: Detailed information for debugging purposes
  - **TRACE**: Very detailed information for troubleshooting specific issues
- Configure default level of INFO for production
- Configure appropriate levels per package/class

### 3. Log Content Standards
- Include correlation IDs in all logs
- Define required context fields for different log types
- Implement consistent message formatting
- Establish conventions for logging exceptions
- Apply masking for sensitive data (PII, credentials, etc.)
- Include source information (class, method) where appropriate

### 4. Structured Logging
- Use JSON format for machine processing
- Define a standard schema for log events
- Include consistent metadata fields
- Support custom fields for specific event types
- Enable easy filtering and aggregation

### 5. Operational Approach
- Configure log rotation and retention policies
- Implement centralized log aggregation
- Set up log monitoring and alerting
- Define log backup and archival strategy
- Establish log access controls

## Implementation Approach

1. **Framework Configuration**
   - Configure Logback as the SLF4J implementation
   - Set up appropriate appenders for different environments
   - Implement JSON formatting for production logs
   - Configure asynchronous logging for better performance

2. **Context Enrichment**
   - Implement web filter for request context capture
   - Configure MDC for correlation ID propagation
   - Add service and instance information to logs
   - Integrate with distributed tracing if applicable

3. **Security and Privacy**
   - Implement masking for sensitive data
   - Configure appropriate log levels to prevent excessive information
   - Ensure proper log file permissions and access controls
   - Implement compliance with relevant regulations (GDPR, HIPAA, etc.)

4. **Developer Guidelines**
   - Create logging standards documentation
   - Provide examples of proper logging practices
   - Implement static analysis rules for logging
   - Include logging review in code reviews

## Consequences

### Positive
- Consistent logging across the application
- Improved troubleshooting capabilities
- Better operational visibility
- Enhanced security through proper data handling
- Easier log analysis and search
- Support for automated monitoring and alerting
- Clear correlation of related events
- Reduced time to resolve issues
- Better compliance with security and privacy requirements
- Improved developer experience with clear guidelines

### Negative
- Initial overhead to implement standardized logging
- Learning curve for developers to follow logging standards
- Potential performance impact if not configured properly
- Need for ongoing maintenance of logging configuration
- Storage requirements for log retention
- Additional complexity in log processing pipeline
- Risk of over-logging or under-logging without proper guidance

## Alternatives Considered

1. **Log4j2**
   - Better performance than Logback in some scenarios
   - More configuration options
   - Less integrated with Spring Boot
   - Requires additional configuration
   - Historical security vulnerabilities (though addressed)

2. **JUL (java.util.logging)**
   - Built into Java
   - No external dependencies
   - Limited functionality compared to alternatives
   - Less flexible configuration
   - Poor integration with modern logging ecosystems

3. **Custom Logging Solution**
   - Tailored exactly to our needs
   - High development and maintenance overhead
   - Risk of reinventing solved problems
   - No community support
   - Potential for inconsistent implementation

4. **ELK/OpenSearch Direct Integration**
   - Direct integration with log aggregation
   - Tighter coupling with specific technology
   - More complex configuration
   - Less flexibility to change log destinations
   - Potential performance impact

## Implementation Notes

### Gradle Dependencies (Kotlin DSL)

```kotlin
dependencies {
    // SLF4J with Logback (included in Spring Boot)
    implementation("org.springframework.boot:spring-boot-starter-logging")
    
    // JSON formatting for logs
    implementation("net.logstash.logback:logstash-logback-encoder:7.2")
    
    // For correlation IDs in distributed systems
    implementation("org.springframework.cloud:spring-cloud-starter-sleuth:3.1.3")
    
    // Optional: Zipkin for distributed tracing
    implementation("org.springframework.cloud:spring-cloud-sleuth-zipkin:3.1.3")
    
    // Aspect-oriented programming support for logging aspects
    implementation("org.springframework.boot:spring-boot-starter-aop")
}
```

### Logback Configuration (logback-spring.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- Import Spring Boot defaults -->
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>
    
    <!-- Properties -->
    <property name="LOG_PATH" value="${LOG_PATH:-./logs}"/>
    <property name="LOG_ARCHIVE" value="${LOG_PATH}/archive"/>
    <property name="SERVICE_NAME" value="my-application"/>
    
    <!-- Appenders -->
    
    <!-- Console appender for development -->
    <springProfile name="dev,local,default">
        <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
            <encoder>
                <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] [%X{traceId:-},%X{spanId:-}] %-5level %logger{36} - %msg%n</pattern>
            </encoder>
        </appender>
    </springProfile>
    
    <!-- Console appender for production (JSON format) -->
    <springProfile name="prod,staging,qa">
        <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
            <encoder class="net.logstash.logback.encoder.LogstashEncoder">
                <includeMdcKeyName>traceId</includeMdcKeyName>
                <includeMdcKeyName>spanId</includeMdcKeyName>
                <includeMdcKeyName>userId</includeMdcKeyName>
                <includeMdcKeyName>requestId</includeMdcKeyName>
                <includeMdcKeyName>sessionId</includeMdcKeyName>
                <includeMdcKeyName>clientIp</includeMdcKeyName>
                <fieldNames>
                    <timestamp>timestamp</timestamp>
                    <thread>thread</thread>
                    <logger>logger</logger>
                    <level>level</level>
                    <message>message</message>
                </fieldNames>
                <customFields>{"service":"${SERVICE_NAME}","environment":"${spring.profiles.active:-unknown}"}</customFields>
            </encoder>
        </appender>
    </springProfile>
    
    <!-- File appender for all environments -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/${SERVICE_NAME}.log</file>
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <includeMdcKeyName>userId</includeMdcKeyName>
            <includeMdcKeyName>requestId</includeMdcKeyName>
            <includeMdcKeyName>sessionId</includeMdcKeyName>
            <includeMdcKeyName>clientIp</includeMdcKeyName>
            <customFields>{"service":"${SERVICE_NAME}","environment":"${spring.profiles.active:-unknown}"}</customFields>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_ARCHIVE}/${SERVICE_NAME}.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
            <totalSizeCap>3GB</totalSizeCap>
        </rollingPolicy>
    </appender>
    
    <!-- Async appender for better performance -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="FILE"/>
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
        <includeCallerData>true</includeCallerData>
    </appender>
    
    <!-- Error appender for critical errors only -->
    <appender name="ERROR_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/${SERVICE_NAME}-error.log</file>
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>ERROR</level>
        </filter>
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <customFields>{"service":"${SERVICE_NAME}","environment":"${spring.profiles.active:-unknown}"}</customFields>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_ARCHIVE}/${SERVICE_NAME}-error.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>60</maxHistory>
            <totalSizeCap>1GB</totalSizeCap>
        </rollingPolicy>
    </appender>
    
    <!-- Loggers -->
    
    <!-- Application logger -->
    <logger name="com.example" level="${LOG_LEVEL_APP:-INFO}"/>
    
    <!-- Spring Framework loggers -->
    <logger name="org.springframework" level="${LOG_LEVEL_SPRING:-INFO}"/>
    <logger name="org.springframework.web" level="${LOG_LEVEL_SPRING_WEB:-INFO}"/>
    <logger name="org.springframework.security" level="${LOG_LEVEL_SPRING_SECURITY:-INFO}"/>
    
    <!-- Database loggers -->
    <logger name="org.hibernate.SQL" level="${LOG_LEVEL_HIBERNATE_SQL:-INFO}"/>
    <logger name="org.hibernate.type.descriptor.sql.BasicBinder" level="${LOG_LEVEL_HIBERNATE_SQL_PARAMS:-INFO}"/>
    
    <!-- Root logger -->
    <root level="${LOG_LEVEL_ROOT:-INFO}">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC_FILE"/>
        <appender-ref ref="ERROR_FILE"/>
    </root>
</configuration>
```

### Request Context Filter

```java
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class RequestContextFilter extends OncePerRequestFilter {
    
    private static final String REQUEST_ID_HEADER = "X-Request-ID";
    private static final String SESSION_ID_ATTR = "sessionId";
    private static final String USER_ID_ATTR = "userId";
    private static final String CLIENT_IP_ATTR = "clientIp";
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        try {
            // Extract or generate request ID
            String requestId = request.getHeader(REQUEST_ID_HEADER);
            if (StringUtils.isEmpty(requestId)) {
                requestId = UUID.randomUUID().toString();
            }
            MDC.put("requestId", requestId);
            response.setHeader(REQUEST_ID_HEADER, requestId);
            
            // Add session ID if available
            HttpSession session = request.getSession(false);
            if (session != null) {
                MDC.put(SESSION_ID_ATTR, session.getId());
            }
            
            // Add user ID if authenticated
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication != null && authentication.isAuthenticated() && 
                    !(authentication instanceof AnonymousAuthenticationToken)) {
                MDC.put(USER_ID_ATTR, authentication.getName());
            }
            
            // Add client IP
            String clientIp = extractClientIp(request);
            MDC.put(CLIENT_IP_ATTR, clientIp);
            
            // Continue with the request
            filterChain.doFilter(request, response);
        } finally {
            // Clear MDC to prevent memory leaks
            MDC.clear();
        }
    }
    
    private String extractClientIp(HttpServletRequest request) {
        String clientIp = request.getHeader("X-Forwarded-For");
        if (StringUtils.isEmpty(clientIp) || "unknown".equalsIgnoreCase(clientIp)) {
            clientIp = request.getHeader("Proxy-Client-IP");
        }
        if (StringUtils.isEmpty(clientIp) || "unknown".equalsIgnoreCase(clientIp)) {
            clientIp = request.getHeader("WL-Proxy-Client-IP");
        }
        if (StringUtils.isEmpty(clientIp) || "unknown".equalsIgnoreCase(clientIp)) {
            clientIp = request.getRemoteAddr();
        }
        
        // If X-Forwarded-For contains multiple IPs, take the first one
        if (clientIp != null && clientIp.contains(",")) {
            clientIp = clientIp.split(",")[0].trim();
        }
        
        return clientIp;
    }
}
```

### Sensitive Data Masking

```java
@Component
public class LoggingUtils {
    
    private static final String MASK = "********";
    private static final Pattern EMAIL_PATTERN = 
        Pattern.compile("([a-zA-Z0-9_.-]+)@([a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)");
    private static final Pattern CREDIT_CARD_PATTERN = 
        Pattern.compile("\\b(?:\\d[ -]*?){13,16}\\b");
    private static final Pattern SSN_PATTERN = 
        Pattern.compile("\\b\\d{3}-\\d{2}-\\d{4}\\b");
    
    /**
     * Masks sensitive data in the given string
     */
    public static String maskSensitiveData(String input) {
        if (input == null) {
            return null;
        }
        
        // Mask email addresses
        String masked = EMAIL_PATTERN.matcher(input).replaceAll(mr -> {
            String username = mr.group(1);
            String domain = mr.group(2);
            return username.substring(0, Math.min(3, username.length())) + "..." + "@" + domain;
        });
        
        // Mask credit card numbers
        masked = CREDIT_CARD_PATTERN.matcher(masked).replaceAll(mr -> {
            String ccNum = mr.group();
            return ccNum.substring(0, 4) + MASK;
        });
        
        // Mask SSNs
        masked = SSN_PATTERN.matcher(masked).replaceAll("XXX-XX-XXXX");
        
        return masked;
    }
    
    /**
     * Creates a log-safe version of an object by removing/masking sensitive fields
     */
    public static <T> String toLogSafeString(T object) {
        if (object == null) {
            return null;
        }
        
        try {
            ObjectMapper mapper = new ObjectMapper();
            mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
            
            // Configure masking filter
            mapper.setFilterProvider(new SimpleFilterProvider()
                .addFilter("sensitiveFilter", SimpleBeanPropertyFilter.serializeAllExcept("password", "ssn", "creditCard")));
            mapper.addMixIn(Object.class, SensitiveDataMixIn.class);
            
            String json = mapper.writeValueAsString(object);
            return maskSensitiveData(json);
        } catch (JsonProcessingException e) {
            // Fallback to toString if JSON serialization fails
            return maskSensitiveData(object.toString());
        }
    }
    
    @JsonFilter("sensitiveFilter")
    private static class SensitiveDataMixIn {
        // This is a marker class for the mixin
    }
}
```

### Logging Aspect for Method Entry/Exit

```java
@Aspect
@Component
public class LoggingAspect {
    
    private static final Logger log = LoggerFactory.getLogger(LoggingAspect.class);
    
    @Around("@annotation(loggable)")
    public Object logMethod(ProceedingJoinPoint joinPoint, Loggable loggable) throws Throwable {
        String methodName = joinPoint.getSignature().getName();
        String className = joinPoint.getSignature().getDeclaringTypeName();
        
        // Log method entry
        if (loggable.entryLevel() != LogLevel.OFF) {
            logMethodEntry(className, methodName, joinPoint.getArgs(), loggable);
        }
        
        long startTime = System.currentTimeMillis();
        try {
            // Execute the method
            Object result = joinPoint.proceed();
            
            // Log method exit
            if (loggable.exitLevel() != LogLevel.OFF) {
                logMethodExit(className, methodName, result, 
                        System.currentTimeMillis() - startTime, loggable);
            }
            
            return result;
        } catch (Throwable ex) {
            // Log exception
            if (loggable.exceptionLevel() != LogLevel.OFF) {
                logMethodException(className, methodName, ex, loggable);
            }
            throw ex;
        }
    }
    
    private void logMethodEntry(String className, String methodName, 
            Object[] args, Loggable loggable) {
        String message = String.format("Entering %s.%s(%s)", 
                className, methodName, formatArgs(args, loggable.maskArgs()));
        
        logWithLevel(loggable.entryLevel(), message);
    }
    
    private void logMethodExit(String className, String methodName, 
            Object result, long executionTime, Loggable loggable) {
        String resultStr = loggable.logResult() ? 
                LoggingUtils.toLogSafeString(result) : "[RESULT NOT LOGGED]";
        
        String message = String.format("Exiting %s.%s: returned %s (execution time: %dms)", 
                className, methodName, resultStr, executionTime);
        
        logWithLevel(loggable.exitLevel(), message);
    }
    
    private void logMethodException(String className, String methodName, 
            Throwable ex, Loggable loggable) {
        String message = String.format("Exception in %s.%s: %s", 
                className, methodName, ex.getMessage());
        
        logWithLevel(loggable.exceptionLevel(), message, ex);
    }
    
    private String formatArgs(Object[] args, boolean maskArgs) {
        if (args == null || args.length == 0) {
            return "";
        }
        
        return Arrays.stream(args)
                .map(arg -> maskArgs ? LoggingUtils.toLogSafeString(arg) : String.valueOf(arg))
                .collect(Collectors.joining(", "));
    }
    
    private void logWithLevel(LogLevel level, String message) {
        logWithLevel(level, message, null);
    }
    
    private void logWithLevel(LogLevel level, String message, Throwable ex) {
        switch (level) {
            case TRACE:
                if (ex == null) log.trace(message); else log.trace(message, ex);
                break;
            case DEBUG:
                if (ex == null) log.debug(message); else log.debug(message, ex);
                break;
            case INFO:
                if (ex == null) log.info(message); else log.info(message, ex);
                break;
            case WARN:
                if (ex == null) log.warn(message); else log.warn(message, ex);
                break;
            case ERROR:
                if (ex == null) log.error(message); else log.error(message, ex);
                break;
            default:
                // Do nothing for OFF
        }
    }
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Loggable {
    LogLevel entryLevel() default LogLevel.DEBUG;
    LogLevel exitLevel() default LogLevel.DEBUG;
    LogLevel exceptionLevel() default LogLevel.ERROR;
    boolean logResult() default true;
    boolean maskArgs() default true;
}

public enum LogLevel {
    TRACE, DEBUG, INFO, WARN, ERROR, OFF
}
```

### Logging Service

```java
@Service
public class LoggingService {
    
    private static final Logger log = LoggerFactory.getLogger(LoggingService.class);
    private static final Logger securityLog = LoggerFactory.getLogger("SECURITY_LOGGER");
    private static final Logger auditLog = LoggerFactory.getLogger("AUDIT_LOGGER");
    
    /**
     * Logs an application event with structured data
     */
    public void logApplicationEvent(String eventType, String message, Map<String, Object> data) {
        MDC.put("eventType", eventType);
        try {
            // Convert data to JSON for structured logging
            ObjectMapper mapper = new ObjectMapper();
            String dataJson = mapper.writeValueAsString(data);
            
            log.info("{}: {} - data={}", eventType, message, dataJson);
        } catch (JsonProcessingException e) {
            log.info("{}: {} - data serialization failed: {}", eventType, message, e.getMessage());
        } finally {
            MDC.remove("eventType");
        }
    }
    
    /**
     * Logs a security event
     */
    public void logSecurityEvent(String eventType, String username, String action, String outcome) {
        MDC.put("eventType", eventType);
        MDC.put("username", username);
        
        try {
            securityLog.info("Security event: {} performed by {} with outcome {}", 
                    action, username, outcome);
        } finally {
            MDC.remove("eventType");
            MDC.remove("username");
        }
    }
    
    /**
     * Logs an audit event for compliance
     */
    public void logAuditEvent(String user, String action, String resource, 
            String resourceId, String outcome) {
        MDC.put("user", user);
        MDC.put("action", action);
        MDC.put("resource", resource);
        MDC.put("resourceId", resourceId);
        MDC.put("outcome", outcome);
        
        try {
            auditLog.info("AUDIT: User {} {} {} with ID {} - {}", 
                    user, action, resource, resourceId, outcome);
        } finally {
            MDC.remove("user");
            MDC.remove("action");
            MDC.remove("resource");
            MDC.remove("resourceId");
            MDC.remove("outcome");
        }
    }
    
    /**
     * Logs performance metrics
     */
    public void logPerformanceMetric(String operation, long durationMs, String details) {
        MDC.put("metricType", "PERFORMANCE");
        MDC.put("operation", operation);
        MDC.put("durationMs", String.valueOf(durationMs));
        
        try {
            log.info("Performance: {} took {}ms - {}", operation, durationMs, details);
        } finally {
            MDC.remove("metricType");
            MDC.remove("operation");
            MDC.remove("durationMs");
        }
    }
}
```

### Application Properties

```yaml
# Logging configuration
logging:
  config: classpath:logback-spring.xml
  level:
    root: INFO
    com.example: INFO
    org.springframework: INFO
    org.hibernate.SQL: INFO
  path: ${LOG_PATH:./logs}
  
# Spring Boot Actuator for log level management
management:
  endpoints:
    web:
      exposure:
        include: loggers,health,info
  endpoint:
    loggers:
      enabled: true
```

### Usage Examples

```java
@Service
public class CustomerService {
    
    private static final Logger log = LoggerFactory.getLogger(CustomerService.class);
    private final LoggingService loggingService;
    
    public CustomerService(LoggingService loggingService) {
        this.loggingService = loggingService;
    }
    
    @Loggable(entryLevel = LogLevel.DEBUG, exitLevel = LogLevel.INFO)
    public CustomerDTO findCustomerById(UUID id) {
        log.debug("Looking up customer with ID: {}", id);
        
        // Business logic
        
        // Log application event
        Map<String, Object> eventData = new HashMap<>();
        eventData.put("customerId", id);
        eventData.put("lookupSource", "internal");
        loggingService.logApplicationEvent("CUSTOMER_LOOKUP", "Customer lookup", eventData);
        
        return customerDTO;
    }
    
    @Loggable
    public void updateCustomerAddress(UUID customerId, AddressDTO address) {
        log.info("Updating address for customer: {}", customerId);
        
        // Business logic
        
        // Log audit event
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        loggingService.logAuditEvent(
                username,
                "UPDATE",
                "CUSTOMER_ADDRESS", 
                customerId.toString(),
                "SUCCESS");
    }
    
    public void processLargeDataSet(List<CustomerDTO> customers) {
        log.info("Processing batch of {} customers", customers.size());
        
        long startTime = System.currentTimeMillis();
        
        // Process each customer
        for (CustomerDTO customer : customers) {
            try {
                processCustomer(customer);
            } catch (Exception e) {
                // Log error but continue processing
                log.error("Failed to process customer {}: {}", 
                        customer.getId(), e.getMessage(), e);
            }
        }
        
        long duration = System.currentTimeMillis() - startTime;
        loggingService.logPerformanceMetric(
                "BATCH_CUSTOMER_PROCESSING", 
                duration, 
                "Processed " + customers.size() + " customers");
    }
    
    private void processCustomer(CustomerDTO customer) {
        // Implementation
    }
}
```

## Compliance Verification
- Code review to ensure adherence to logging standards
- Static analysis to detect improper logging practices
- Log file audits to verify content and format
- Performance testing to measure logging impact
- Security review of sensitive data handling
- Verification of log aggregation and search capabilities
- Testing of log rotation and retention policies
- Review of logging levels across environments

## References
- SLF4J Documentation: http://www.slf4j.org/manual.html
- Logback Documentation: http://logback.qos.ch/documentation.html
- Spring Boot Logging: https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.logging
- Logstash Encoder: https://github.com/logstash/logstash-logback-encoder
- Structured Logging Best Practices: https://www.innoq.com/en/blog/structured-logging/
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- Log Management Best Practices: https://www.graylog.org/post/log-management-best-practices
