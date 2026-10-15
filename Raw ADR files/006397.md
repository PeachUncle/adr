# ADR-018: Centralized Exception Handling for Spring Boot Application

## Status
Accepted

## Date
2025-03-01

## Context
Our Spring Boot application needs a consistent, maintainable, and user-friendly approach to handling exceptions. Currently, exception handling is inconsistent across different parts of the application, leading to:

- Inconsistent error responses returned to clients
- Duplicated error handling code across controllers
- Insufficient logging of exceptions
- Lack of clear distinction between client errors and server errors
- Poor user experience due to unclear error messages
- Difficulty in troubleshooting issues in production
- Security concerns with exposing sensitive information in error responses
- Challenges in maintaining error handling as the application grows

A well-designed exception handling strategy is crucial for API usability, system maintainability, and operational excellence. We need a solution that provides consistent error responses, appropriate logging, and clear separation of concerns.

## Decision
We will implement a **Centralized Exception Handling** approach using Spring's `@ControllerAdvice` and `@ExceptionHandler` mechanisms with the following components:

### 1. Exception Hierarchy
- Create a custom exception hierarchy with a base application exception
- Distinguish between client errors (4xx) and server errors (5xx)
- Define specific exception types for common error scenarios
- Include appropriate metadata in exceptions (error codes, user messages)

### 2. Global Exception Handler
- Implement a global exception handler using `@ControllerAdvice`
- Define specific handlers for different exception types
- Map exceptions to appropriate HTTP status codes
- Provide consistent error response structure
- Include different levels of detail based on environment (dev/prod)

### 3. Standardized Error Response Format
- Define a consistent error response structure for all API errors
- Include fields for error code, message, timestamp, path, and details
- Support localized error messages
- Include correlation IDs for error tracking
- Provide appropriate level of detail based on exception type

### 4. Logging Strategy
- Log exceptions with appropriate severity levels
- Include contextual information in logs
- Ensure sensitive data is not logged
- Use structured logging format for better searchability
- Correlate logs with error responses

### 5. Integration with Monitoring
- Tag errors for monitoring and alerting
- Collect metrics on error rates by type
- Enable tracing for error investigation
- Integrate with observability tools

## Implementation Approach

1. **Exception Hierarchy Design**
   - Create base exception classes
   - Implement specific exception types for different scenarios
   - Include appropriate metadata in exceptions

2. **Global Exception Handler Implementation**
   - Create a central exception handler class
   - Define handlers for specific exception types
   - Implement fallback handlers for unexpected exceptions
   - Configure environment-specific behavior

3. **Error Response Standardization**
   - Define error response DTOs
   - Implement consistent mapping from exceptions to responses
   - Support internationalization for error messages

4. **Logging and Monitoring Integration**
   - Configure appropriate logging levels
   - Integrate with application monitoring
   - Set up alerts for critical errors

## Consequences

### Positive
- Consistent error handling across the entire application
- Improved API usability with clear error messages
- Reduced code duplication in controllers
- Better separation of concerns
- Enhanced troubleshooting capabilities
- Appropriate logging of exceptions
- Improved security by controlling error information exposure
- Easier maintenance as the application evolves
- Better integration with monitoring and alerting systems

### Negative
- Initial overhead to implement the exception handling framework
- Learning curve for developers to use the custom exception types
- Risk of overengineering if too many specific exception types are created
- Potential performance impact from additional processing for error responses
- Need for ongoing maintenance of the exception hierarchy
- Possible complexity in handling framework-specific exceptions

## Alternatives Considered

1. **Controller-Level Exception Handling**
   - Using try-catch blocks in controllers
   - More direct control over exception handling
   - Leads to significant code duplication
   - Inconsistent error responses
   - Tightly couples error handling to controllers

2. **Aspect-Oriented Exception Handling**
   - Using AspectJ for exception handling
   - More flexible pointcut definitions
   - Higher complexity
   - Less standard approach
   - Steeper learning curve

3. **Framework-Specific Error Pages**
   - Using Spring Boot's error page mechanism
   - Simpler implementation for web applications
   - Less suitable for REST APIs
   - Limited customization options
   - Difficult to include detailed error information

4. **Middleware Approach**
   - Implementing exception handling as middleware
   - Common in some frameworks like Express.js
   - Not as well-supported in Spring Boot
   - Would require custom implementation
   - Less integration with Spring's features

## Implementation Notes

### Exception Hierarchy

```java
// Base exception class
public abstract class ApplicationException extends RuntimeException {
    
    private final String errorCode;
    private final HttpStatus status;
    
    protected ApplicationException(String message, String errorCode, HttpStatus status) {
        super(message);
        this.errorCode = errorCode;
        this.status = status;
    }
    
    public String getErrorCode() {
        return errorCode;
    }
    
    public HttpStatus getStatus() {
        return status;
    }
}

// Client error base class
public abstract class ClientErrorException extends ApplicationException {
    
    protected ClientErrorException(String message, String errorCode, HttpStatus status) {
        super(message, errorCode, status != null ? status : HttpStatus.BAD_REQUEST);
    }
}

// Server error base class
public abstract class ServerErrorException extends ApplicationException {
    
    protected ServerErrorException(String message, String errorCode, HttpStatus status) {
        super(message, errorCode, status != null ? status : HttpStatus.INTERNAL_SERVER_ERROR);
    }
}

// Specific exception examples
public class ResourceNotFoundException extends ClientErrorException {
    
    public ResourceNotFoundException(String resourceType, String identifier) {
        super(
            String.format("%s not found with identifier: %s", resourceType, identifier),
            "RESOURCE_NOT_FOUND",
            HttpStatus.NOT_FOUND
        );
    }
}

public class ValidationException extends ClientErrorException {
    
    private final List<FieldError> fieldErrors;
    
    public ValidationException(List<FieldError> fieldErrors) {
        super(
            "Validation failed for the request",
            "VALIDATION_ERROR",
            HttpStatus.UNPROCESSABLE_ENTITY
        );
        this.fieldErrors = fieldErrors;
    }
    
    public List<FieldError> getFieldErrors() {
        return fieldErrors;
    }
    
    public static class FieldError {
        private final String field;
        private final String message;
        
        public FieldError(String field, String message) {
            this.field = field;
            this.message = message;
        }
        
        public String getField() {
            return field;
        }
        
        public String getMessage() {
            return message;
        }
    }
}

public class BusinessRuleViolationException extends ClientErrorException {
    
    public BusinessRuleViolationException(String message, String errorCode) {
        super(message, errorCode, HttpStatus.CONFLICT);
    }
}

public class ExternalServiceException extends ServerErrorException {
    
    private final String serviceName;
    
    public ExternalServiceException(String serviceName, String message) {
        super(
            String.format("Error in external service %s: %s", serviceName, message),
            "EXTERNAL_SERVICE_ERROR",
            HttpStatus.SERVICE_UNAVAILABLE
        );
        this.serviceName = serviceName;
    }
    
    public String getServiceName() {
        return serviceName;
    }
}
```

### Error Response DTO

```java
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponse {
    
    private final String errorCode;
    private final String message;
    private final int status;
    private final String path;
    private final String timestamp;
    private final String correlationId;
    private final List<FieldErrorDTO> details;
    
    @Builder
    public ErrorResponse(
            String errorCode,
            String message,
            int status,
            String path,
            List<FieldErrorDTO> details) {
        this.errorCode = errorCode;
        this.message = message;
        this.status = status;
        this.path = path;
        this.timestamp = ZonedDateTime.now(ZoneOffset.UTC)
                .format(DateTimeFormatter.ISO_INSTANT);
        this.correlationId = MDC.get("correlationId");
        this.details = details;
    }
    
    // Getters
    
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class FieldErrorDTO {
        private final String field;
        private final String message;
        
        public FieldErrorDTO(String field, String message) {
            this.field = field;
            this.message = message;
        }
        
        // Getters
    }
}
```

### Global Exception Handler

```java
@RestControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE)
public class GlobalExceptionHandler {
    
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    private final MessageSource messageSource;
    private final boolean includeStackTrace;
    
    public GlobalExceptionHandler(
            MessageSource messageSource,
            @Value("${application.error.include-stack-trace:false}") boolean includeStackTrace) {
        this.messageSource = messageSource;
        this.includeStackTrace = includeStackTrace;
    }
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFoundException(
            ResourceNotFoundException ex, WebRequest request) {
        
        log.info("Resource not found: {}", ex.getMessage());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .errorCode(ex.getErrorCode())
                .message(ex.getMessage())
                .status(ex.getStatus().value())
                .path(extractPath(request))
                .build();
        
        return new ResponseEntity<>(errorResponse, ex.getStatus());
    }
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(
            ValidationException ex, WebRequest request) {
        
        log.info("Validation error: {}", ex.getMessage());
        
        List<ErrorResponse.FieldErrorDTO> fieldErrors = ex.getFieldErrors().stream()
                .map(fieldError -> new ErrorResponse.FieldErrorDTO(
                        fieldError.getField(),
                        fieldError.getMessage()))
                .collect(Collectors.toList());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .errorCode(ex.getErrorCode())
                .message(ex.getMessage())
                .status(ex.getStatus().value())
                .path(extractPath(request))
                .details(fieldErrors)
                .build();
        
        return new ResponseEntity<>(errorResponse, ex.getStatus());
    }
    
    @ExceptionHandler(BusinessRuleViolationException.class)
    public ResponseEntity<ErrorResponse> handleBusinessRuleViolationException(
            BusinessRuleViolationException ex, WebRequest request) {
        
        log.info("Business rule violation: {}", ex.getMessage());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .errorCode(ex.getErrorCode())
                .message(ex.getMessage())
                .status(ex.getStatus().value())
                .path(extractPath(request))
                .build();
        
        return new ResponseEntity<>(errorResponse, ex.getStatus());
    }
    
    @ExceptionHandler(ExternalServiceException.class)
    public ResponseEntity<ErrorResponse> handleExternalServiceException(
            ExternalServiceException ex, WebRequest request) {
        
        log.error("External service error: {} - {}", ex.getServiceName(), ex.getMessage());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .errorCode(ex.getErrorCode())
                .message(ex.getMessage())
                .status(ex.getStatus().value())
                .path(extractPath(request))
                .build();
        
        return new ResponseEntity<>(errorResponse, ex.getStatus());
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleMethodArgumentNotValidException(
            MethodArgumentNotValidException ex, WebRequest request) {
        
        log.info("Validation error on method arguments");
        
        List<ErrorResponse.FieldErrorDTO> fieldErrors = ex.getBindingResult().getFieldErrors().stream()
                .map(fieldError -> new ErrorResponse.FieldErrorDTO(
                        fieldError.getField(),
                        resolveLocalizedMessage(fieldError)))
                .collect(Collectors.toList());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .errorCode("VALIDATION_ERROR")
                .message("Validation failed for the request")
                .status(HttpStatus.UNPROCESSABLE_ENTITY.value())
                .path(extractPath(request))
                .details(fieldErrors)
                .build();
        
        return new ResponseEntity<>(errorResponse, HttpStatus.UNPROCESSABLE_ENTITY);
    }
    
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDeniedException(
            AccessDeniedException ex, WebRequest request) {
        
        log.warn("Access denied: {}", ex.getMessage());
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .errorCode("ACCESS_DENIED")
                .message("You do not have permission to access this resource")
                .status(HttpStatus.FORBIDDEN.value())
                .path(extractPath(request))
                .build();
        
        return new ResponseEntity<>(errorResponse, HttpStatus.FORBIDDEN);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(
            Exception ex, WebRequest request) {
        
        log.error("Unhandled exception", ex);
        
        ErrorResponse errorResponse = ErrorResponse.builder()
                .errorCode("INTERNAL_SERVER_ERROR")
                .message("An unexpected error occurred")
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .path(extractPath(request))
                .build();
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }
    
    private String extractPath(WebRequest request) {
        return ((ServletWebRequest) request).getRequest().getRequestURI();
    }
    
    private String resolveLocalizedMessage(FieldError fieldError) {
        try {
            return messageSource.getMessage(fieldError, LocaleContextHolder.getLocale());
        } catch (NoSuchMessageException e) {
            return fieldError.getDefaultMessage();
        }
    }
}
```

### Exception Usage in Service Layer

```java
@Service
@Transactional(readOnly = true)
public class ProductService {
    
    private final ProductRepository productRepository;
    
    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }
    
    public ProductDTO getProductById(UUID id) {
        return productRepository.findById(id)
                .map(this::convertToDto)
                .orElseThrow(() -> new ResourceNotFoundException("Product", id.toString()));
    }
    
    @Transactional
    public ProductDTO createProduct(ProductDTO productDTO) {
        // Validate product data
        validateProduct(productDTO);
        
        // Check for duplicate SKU
        if (productRepository.existsBySku(productDTO.getSku())) {
            throw new BusinessRuleViolationException(
                    "Product with SKU " + productDTO.getSku() + " already exists",
                    "DUPLICATE_PRODUCT_SKU");
        }
        
        Product product = new Product();
        updateProductFromDto(product, productDTO);
        
        try {
            Product savedProduct = productRepository.save(product);
            return convertToDto(savedProduct);
        } catch (DataIntegrityViolationException e) {
            throw new ServerErrorException(
                    "Failed to create product due to data integrity violation",
                    "DATA_INTEGRITY_ERROR",
                    HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    
    private void validateProduct(ProductDTO productDTO) {
        List<ValidationException.FieldError> errors = new ArrayList<>();
        
        if (productDTO.getPrice() != null && productDTO.getPrice().compareTo(BigDecimal.ZERO) <= 0) {
            errors.add(new ValidationException.FieldError("price", "Price must be greater than zero"));
        }
        
        if (StringUtils.isBlank(productDTO.getName())) {
            errors.add(new ValidationException.FieldError("name", "Name cannot be empty"));
        }
        
        if (!errors.isEmpty()) {
            throw new ValidationException(errors);
        }
    }
    
    // Other methods
}
```

### Controller Example

```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {
    
    private final ProductService productService;
    
    public ProductController(ProductService productService) {
        this.productService = productService;
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<ProductDTO> getProduct(@PathVariable UUID id) {
        ProductDTO product = productService.getProductById(id);
        return ResponseEntity.ok(product);
    }
    
    @PostMapping
    public ResponseEntity<ProductDTO> createProduct(
            @Valid @RequestBody ProductDTO productDTO) {
        ProductDTO createdProduct = productService.createProduct(productDTO);
        
        URI location = ServletUriComponentsBuilder
                .fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(createdProduct.getId())
                .toUri();
        
        return ResponseEntity.created(location).body(createdProduct);
    }
    
    // Note: No try-catch blocks needed in the controller methods
    // The global exception handler takes care of all exceptions
}
```

### Configuration for Exception Handling

```java
@Configuration
public class ExceptionHandlingConfig {
    
    @Bean
    public MessageSource messageSource() {
        ReloadableResourceBundleMessageSource messageSource = new ReloadableResourceBundleMessageSource();
        messageSource.setBasename("classpath:messages");
        messageSource.setDefaultEncoding("UTF-8");
        return messageSource;
    }
    
    @Bean
    public LocalValidatorFactoryBean validator(MessageSource messageSource) {
        LocalValidatorFactoryBean bean = new LocalValidatorFactoryBean();
        bean.setValidationMessageSource(messageSource);
        return bean;
    }
}
```

### Logging Configuration

```yaml
logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] [%X{correlationId}] %-5level %logger{36} - %msg%n"
  level:
    root: INFO
    com.example: DEBUG
    org.springframework.web: INFO
```

### Monitoring Integration

```java
@Configuration
public class ExceptionMetricsConfig {
    
    private final MeterRegistry meterRegistry;
    
    public ExceptionMetricsConfig(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    @EventListener
    public void onException(ApplicationException ex) {
        String errorCode = ex.getErrorCode();
        String errorType = ex instanceof ClientErrorException ? "client" : "server";
        
        meterRegistry.counter("application.exceptions", 
                "error_code", errorCode,
                "error_type", errorType,
                "status", String.valueOf(ex.getStatus().value()))
            .increment();
    }
    
    @Bean
    public ApplicationEventMulticaster applicationEventMulticaster() {
        SimpleApplicationEventMulticaster eventMulticaster = new SimpleApplicationEventMulticaster();
        eventMulticaster.setTaskExecutor(new SimpleAsyncTaskExecutor());
        return eventMulticaster;
    }
}
```

## Compliance Verification
- Review of all API error responses for consistency
- Testing of different exception scenarios
- Verification of logging output for different error types
- Security review to ensure sensitive information is not leaked
- Performance testing to measure impact of exception handling
- Usability testing of error messages
- Monitoring setup to track exception rates
- Documentation of error codes and response formats for API consumers

## References
- Spring Exception Handling: https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-ann-exceptionhandler
- REST API Error Handling Best Practices: https://www.baeldung.com/rest-api-error-handling-best-practices
- Spring Boot Error Handling: https://www.toptal.com/java/spring-boot-rest-api-error-handling
- Exception Handling Patterns: https://www.oracle.com/technical-resources/articles/java/effective-exceptions.html
- HTTP Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
