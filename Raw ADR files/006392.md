# ADR-011: Adoption of Keycloak for Identity Management (Containerized Deployment)

## Status
Accepted

## Date
2025-03-01

## Context
Our application requires a robust identity and access management (IAM) solution to handle authentication, authorization, and user management. We need a system that:

- Provides secure authentication for our web and mobile applications
- Supports modern authentication protocols (OAuth 2.0, OpenID Connect)
- Offers comprehensive user management capabilities
- Can integrate with existing enterprise identity providers
- Supports single sign-on (SSO) across multiple applications
- Provides robust security features and compliance capabilities
- Can be self-hosted or used as a managed service
- Integrates well with our Spring Boot application architecture
- Offers flexibility for future growth and changing requirements

Building these capabilities from scratch would be time-consuming, risky, and would divert resources from our core business functionality. Therefore, we need to select an established IAM solution that meets our requirements.

## Decision
We will adopt **Keycloak** as our identity and access management solution. Keycloak is an open-source identity and access management solution developed by Red Hat that provides:

### 1. Core Identity Management Features
- User registration and profile management
- Password policies and recovery workflows
- Multi-factor authentication (MFA)
- Session management
- Account linking and social login
- User federation with LDAP/Active Directory

### 2. Authentication & Authorization
- OAuth 2.0 implementation (all standard flows)
- OpenID Connect support
- Fine-grained role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Client access management
- Token customization

### 3. Integration Capabilities
- Well-documented REST APIs
- SAML 2.0 support for enterprise integration
- Identity brokering with external providers
- Spring Security integration
- Client adapters for various platforms

### 4. Administration & Security
- Administrative console for user management
- Audit logging
- Brute force detection and prevention
- Account threat detection
- Custom authentication flows

### 5. Deployment Options
- Self-hosted (on-premises or cloud infrastructure)
- Container-friendly architecture
- Clustering support for high availability
- Database flexibility (supports multiple backends)

## Implementation Approach
We will implement Keycloak with the following approach:

1. **Deployment Strategy**
   - Initially deploy Keycloak in a containerized environment
   - Configure with PostgreSQL as the backend database
   - Set up with redundancy for high availability

2. **Integration with Our Application**
   - Use Spring Security OAuth2 Resource Server for API protection
   - Implement OpenID Connect for web application authentication
   - Configure client applications in Keycloak

3. **User Management**
   - Define initial roles and groups structure
   - Configure password policies and MFA requirements
   - Set up self-service registration and profile management

4. **Custom Theming**
   - Customize login pages to match our application branding
   - Ensure consistent user experience across authentication flows

5. **Monitoring and Operations**
   - Implement monitoring for Keycloak instances
   - Set up alerting for authentication anomalies
   - Establish backup and recovery procedures

## Consequences

### Positive
- Comprehensive IAM solution without building from scratch
- Industry-standard security protocols and best practices
- Reduced development time for authentication features
- Flexibility to adapt to changing security requirements
- Centralized user management across multiple applications
- Strong community support and regular security updates
- Ability to federate with enterprise identity providers
- Self-hosted option maintains control over sensitive data
- Open-source with commercial support options available

### Negative
- Introduces additional infrastructure to maintain
- Learning curve for team to understand Keycloak configuration
- Potential performance overhead for authentication flows
- Requires expertise for proper security configuration
- Customization may be complex for advanced scenarios
- Upgrade management for security patches
- Potential single point of failure if not properly clustered
- Additional monitoring and operational requirements

## Alternatives Considered

1. **Auth0**
   - Fully managed authentication service
   - Excellent developer experience
   - Higher cost for growing user base
   - Less control over data and infrastructure
   - Potential vendor lock-in

2. **Okta**
   - Enterprise-focused identity solution
   - Comprehensive features and compliance
   - Significant cost for growing organizations
   - More complex than needed for our current scale
   - Less flexibility for customization

3. **Custom Implementation with Spring Security**
   - Complete control over implementation
   - Tailored to our exact requirements
   - Significantly higher development and maintenance effort
   - Higher security risk of custom implementation
   - Diversion of resources from core business functionality

4. **Firebase Authentication**
   - Easy integration for mobile applications
   - Limited customization options
   - Tied to Google Cloud ecosystem
   - Less suitable for enterprise integration
   - Limited administrative capabilities

## Implementation Notes

### Managing User Data

1. **Store core identity data in Keycloak:**
   - Authentication credentials (passwords)
   - Basic user profile (name, email, etc.)
   - Roles and permissions
   - Groups/organization memberships

2. **Store application-specific data in your application:**
   - User preferences
   - Application usage history
   - Business-specific attributes
   - Extended profile information

3. **Link the data using a consistent identifier:**
   - Use Keycloak's user ID as a foreign key in your application's user model
   - Retrieve the user ID from the JWT token during authenticated requests

This approach follows the principle of separation of concerns - letting Keycloak handle identity management (what it's designed for) while your application manages domain-specific user data.


### Spring Boot Integration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(authorize -> authorize
                .requestMatchers("/api/v*/public/**").permitAll()
                .requestMatchers("/v3/api-docs/**", "/swagger-ui/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthenticationConverter()))
            );
        
        return http.build();
    }
    
    @Bean
    public JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter = new JwtGrantedAuthoritiesConverter();
        grantedAuthoritiesConverter.setAuthoritiesClaimName("realm_access.roles");
        grantedAuthoritiesConverter.setAuthorityPrefix("ROLE_");
        
        JwtAuthenticationConverter jwtAuthenticationConverter = new JwtAuthenticationConverter();
        jwtAuthenticationConverter.setJwtGrantedAuthoritiesConverter(grantedAuthoritiesConverter);
        return jwtAuthenticationConverter;
    }
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(List.of("https://bookstore.example.com"));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

### Method Security Configuration

```java
@Configuration
@EnableMethodSecurity
public class MethodSecurityConfig {

    @Bean
    public GrantedAuthorityDefaults grantedAuthorityDefaults() {
        // Remove the ROLE_ prefix so we can use @PreAuthorize("hasRole('ADMIN')") instead of @PreAuthorize("hasRole('ROLE_ADMIN')")
        return new GrantedAuthorityDefaults("");
    }
}
```

### Service Layer Security Example

```java
@Service
public class BookService {

    private final BookRepository bookRepository;
    
    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }
    
    @PreAuthorize("hasRole('USER')")
    public List<Book> findAllBooks() {
        return bookRepository.findAll();
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    public Book createBook(BookDTO bookDTO) {
        // Implementation
    }
    
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public void deleteBook(UUID id) {
        // Implementation
    }
    
    @PostAuthorize("returnObject.orElse(new Book()).owner == authentication.name")
    public Optional<Book> findById(UUID id) {
        return bookRepository.findById(id);
    }
}
```

### Application Properties Configuration

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://keycloak.example.com/realms/our-application
          jwk-set-uri: https://keycloak.example.com/realms/our-application/protocol/openid-connect/certs

  # Optional: Client registration for OAuth2 Login (if needed)
  security:
    oauth2:
      client:
        registration:
          keycloak:
            client-id: bookstore-app
            client-secret: your-client-secret
            scope: openid,profile,email
            authorization-grant-type: authorization_code
            redirect-uri: "{baseUrl}/login/oauth2/code/{registrationId}"
        provider:
          keycloak:
            issuer-uri: https://keycloak.example.com/realms/our-application
            user-name-attribute: preferred_username
```

### Keycloak Docker Deployment with Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: ${KEYCLOAK_DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U keycloak"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - keycloak-network

  keycloak:
    image: quay.io/keycloak/keycloak:latest
    command: ["start-dev", "--import-realm"]
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: ${KEYCLOAK_DB_PASSWORD}
      KC_HOSTNAME: keycloak.example.com
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
      KC_PROXY: edge
      KC_HEALTH_ENABLED: true
    volumes:
      - ./keycloak/realm-export.json:/opt/keycloak/data/import/realm.json
      - ./keycloak/themes:/opt/keycloak/themes
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - keycloak-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health/ready"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:latest
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
      - ./nginx/certs:/etc/nginx/ssl
    ports:
      - "443:443"
    depends_on:
      - keycloak
    networks:
      - keycloak-network

volumes:
  postgres_data:

networks:
  keycloak-network:
    driver: bridge
```

### Testing with Spring Security and Keycloak

```java
@WebMvcTest(BookController.class)
@Import(SecurityTestConfig.class)
class BookControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private BookService bookService;

    @Test
    @WithMockUser(roles = "USER")
    void shouldReturnBookWhenBookExists() throws Exception {
        // Test implementation
    }
    
    @Test
    void shouldReturnUnauthorizedWhenNoAuthentication() throws Exception {
        // Test implementation
    }
    
    @Test
    @WithJwt(claims = @Claims(
        sub = "user123",
        iss = "https://keycloak.example.com/realms/our-application",
        realmAccess = @RealmAccess(roles = {"USER"})
    ))
    void shouldReturnBookWhenValidJwt() throws Exception {
        // Test implementation using JWT authentication
    }
}

// Custom JWT authentication for tests
@Retention(RetentionPolicy.RUNTIME)
@WithSecurityContext(factory = WithJwtSecurityContextFactory.class)
public @interface WithJwt {
    Claims claims() default @Claims;
}

@Retention(RetentionPolicy.RUNTIME)
public @interface Claims {
    String sub() default "user123";
    String name() default "Test User";
    String email() default "user@example.com";
    String iss() default "https://keycloak.example.com/realms/our-application";
    RealmAccess realmAccess() default @RealmAccess;
}

@Retention(RetentionPolicy.RUNTIME)
public @interface RealmAccess {
    String[] roles() default {"USER"};
}
```

## Compliance Verification
- Regular security audits of Keycloak configuration
- Penetration testing of authentication flows
- Monitoring of authentication events and anomalies
- Regular reviews of access policies and permissions
- Verification of compliance requirements (GDPR, HIPAA, etc.)
- Testing of disaster recovery procedures
- Validation of integration with application security

## References
- Keycloak Official Documentation: https://www.keycloak.org/documentation
- Spring Security OAuth2 Resource Server: https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html
- Spring Security Method Security: https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html
- Keycloak with Spring Boot: https://www.baeldung.com/spring-boot-keycloak
- Spring Security Testing: https://docs.spring.io/spring-security/reference/servlet/test/index.html
- Keycloak Clustering Guide: https://www.keycloak.org/server/high-availability
- OAuth 2.0 Security Best Practices: https://oauth.net/articles/authentication/
