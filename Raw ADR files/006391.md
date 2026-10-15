# ADR-010: API Security Strategy for Spring Boot Application

## Status
Accepted

## Date
2025-03-01

## Context
Our Spring Boot application exposes REST APIs that require protection against unauthorized access and potential security threats. We need a comprehensive security strategy that:

- Protects sensitive data and operations
- Authenticates users and client applications reliably
- Authorizes access based on appropriate permissions
- Prevents common API security vulnerabilities
- Integrates well with our Spring Boot architecture
- Supports our API versioning and documentation approaches
- Provides monitoring and auditing capabilities
- Balances security with usability and performance

Without a robust API security strategy, we risk unauthorized access to sensitive data, potential data breaches, compliance violations, and damage to user trust and company reputation.

## Decision
We will implement an API security strategy with the following key components:

### 1. Authentication Mechanism
We will use **OAuth 2.0 with JWT (JSON Web Tokens)** as our primary authentication mechanism:

- OAuth 2.0 will provide a standardized authorization framework
- JWT will be used for token format due to its self-contained nature and statelessness
- We will implement the following OAuth 2.0 flows:
  - Authorization Code flow with PKCE for web applications
  - Client Credentials flow for service-to-service communication
  - Resource Owner Password flow (limited use cases only)
- Tokens will be signed using RS256 (RSA Signature with SHA-256)
- Access tokens will have a short lifetime (1 hour)
- Refresh tokens will be used for obtaining new access tokens
- Spring Security with OAuth2 Resource Server will be used for implementation

### 2. Authorization Model
We will implement a **Role-Based Access Control (RBAC)** system with the following characteristics:

- Roles will be defined at a coarse-grained level (e.g., USER, ADMIN)
- Permissions will be defined at a fine-grained level (e.g., READ_BOOKS, CREATE_ORDER)
- Roles will be mapped to sets of permissions
- JWT claims will contain user roles and/or permissions
- Spring Security's method-level security will be used with annotations:
  - `@PreAuthorize` for permission checks
  - `@PostAuthorize` for result filtering when needed
- API endpoints will be secured by default, with explicit configuration needed to make endpoints public

### 3. API Security Measures
We will implement the following security measures:

- **HTTPS Only**: All API traffic will be encrypted using TLS 1.2+
- **CORS Configuration**: Strict Cross-Origin Resource Sharing policies
- **CSRF Protection**: For browser-based clients with appropriate exceptions for API calls
- **Rate Limiting**: To prevent abuse and DoS attacks
- **Input Validation**: Thorough validation of all input data
- **Output Encoding**: Proper encoding of response data to prevent injection attacks
- **Security Headers**: Implementation of recommended security headers:
  - Content-Security-Policy
  - Strict-Transport-Security
  - X-Content-Type-Options
  - X-Frame-Options
  - X-XSS-Protection
- **Request Timeouts**: Appropriate timeouts to prevent resource exhaustion

### 4. Sensitive Data Handling
- PII (Personally Identifiable Information) will be encrypted at rest
- Sensitive data will be masked in logs
- Data classification will guide security controls
- Data minimization principles will be applied to API responses

### 5. Security Monitoring and Auditing
- Authentication events will be logged (successes and failures)
- Access to sensitive resources will be audited
- Failed authorization attempts will be monitored
- Suspicious activity patterns will trigger alerts
- Regular security scanning of APIs will be performed

### 6. Integration with API Documentation
- Security requirements will be documented in OpenAPI specification
- Authentication flows will be described in additional documentation
- Security-related error responses will be documented

## Consequences

### Positive
- Standardized approach to API security across the application
- Strong authentication and authorization mechanisms
- Defense in depth through multiple security layers
- Compliance with security best practices
- Stateless authentication improving scalability
- Clear documentation of security requirements
- Improved monitoring and incident response capabilities

### Negative
- Added complexity in implementation and maintenance
- Performance overhead from security checks
- Additional development effort for security features
- Potential usability challenges for API consumers
- Need for key/certificate management
- Learning curve for developers to implement security correctly

## Alternatives Considered

1. **Basic Authentication**
   - Simpler to implement
   - Less secure, especially without HTTPS
   - No standard expiration mechanism
   - Credentials sent with every request
   - No support for third-party authorization

2. **API Keys**
   - Simple to implement and use
   - Limited security features
   - No built-in expiration or rotation
   - Difficult to manage at scale
   - No standard for authorization information

3. **Custom Token Solution**
   - Could be tailored to specific needs
   - Would require custom implementation
   - No standardization benefits
   - Higher risk of security vulnerabilities
   - Increased maintenance burden

4. **Session-Based Authentication**
   - Familiar model for web applications
   - Requires session state management
   - Less suitable for API-first design
   - Scaling challenges with distributed systems
   - CSRF vulnerabilities

## Implementation Notes

### OAuth 2.0 / JWT Configuration
We will use Spring Security OAuth2 Resource Server with the following configuration:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .cors().and()
            .csrf().disable()  // For API endpoints
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS).and()
            .authorizeRequests()
                .antMatchers("/api/v*/public/**").permitAll()
                .antMatchers("/api/v*/auth/**").permitAll()
                .antMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
                .anyRequest().authenticated().and()
            .oauth2ResourceServer()
                .jwt()
                .jwtAuthenticationConverter(jwtAuthenticationConverter());
        
        // Security headers
        http.headers()
            .contentSecurityPolicy("default-src 'self'")
            .and()
            .frameOptions().deny()
            .xssProtection().block(true)
            .and()
            .contentTypeOptions();
    }
    
    private JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter = new JwtGrantedAuthoritiesConverter();
        grantedAuthoritiesConverter.setAuthoritiesClaimName("permissions");
        grantedAuthoritiesConverter.setAuthorityPrefix("PERMISSION_");
        
        JwtAuthenticationConverter jwtAuthenticationConverter = new JwtAuthenticationConverter();
        jwtAuthenticationConverter.setJwtGrantedAuthoritiesConverter(grantedAuthoritiesConverter);
        return jwtAuthenticationConverter;
    }
}
```

### Method Security
```java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class MethodSecurityConfig extends GlobalMethodSecurityConfiguration {
    // Configuration if needed
}

@RestController
@RequestMapping("/api/v1/books")
public class BookController {

    @PreAuthorize("hasPermission('READ_BOOKS')")
    @GetMapping("/{id}")
    public ResponseEntity<BookDTO> getBook(@PathVariable Long id) {
        // Implementation
    }

    @PreAuthorize("hasPermission('MANAGE_BOOKS')")
    @PostMapping
    public ResponseEntity<BookDTO> createBook(@Valid @RequestBody BookDTO bookDTO) {
        // Implementation
    }
}
```

### Rate Limiting
We will use Spring Cloud Gateway or a similar solution for rate limiting:

```java
@Configuration
public class RateLimitingConfig {

    @Bean
    public KeyResolver userKeyResolver() {
        return exchange -> {
            // Use JWT subject or client ID as the key
            String userId = extractUserIdFromJWT(exchange);
            return Mono.just(userId != null ? userId : "anonymous");
        };
    }
}
```

### Security in OpenAPI Documentation
```java
@Operation(
    summary = "Create a new book",
    security = @SecurityRequirement(name = "bearer-jwt"),
    responses = {
        @ApiResponse(responseCode = "201", description = "Book created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid input"),
        @ApiResponse(responseCode = "401", description = "Unauthorized"),
        @ApiResponse(responseCode = "403", description = "Forbidden - insufficient permissions")
    }
)
@PostMapping
public ResponseEntity<BookDTO> createBook(@Valid @RequestBody BookDTO bookDTO) {
    // Implementation
}
```

## Compliance Verification
- Regular security audits of API implementation
- Automated security testing as part of CI/CD pipeline
- Penetration testing of API endpoints
- Code reviews with security focus
- Static application security testing (SAST)
- Dynamic application security testing (DAST)
- Dependency vulnerability scanning
- Compliance checks against OWASP API Security Top 10

## References
- OWASP API Security Top 10: https://owasp.org/www-project-api-security/
- Spring Security OAuth2 Resource Server: https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html
- JWT Best Practices: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-jwt-bcp
- OAuth 2.0 Security Best Practices: https://oauth.net/2/oauth-best-practice/
- NIST Digital Identity Guidelines: https://pages.nist.gov/800-63-3/
