# ADR-012: Adoption of Keycloak for Identity Management (Embedded Deployment)

## Status
Rejected

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
- Integrates well with our Spring Boot application architecture
- Offers flexibility for future growth and changing requirements

Additionally, we have specific deployment constraints:
- We need to minimize infrastructure complexity and operational overhead
- We prefer to avoid managing separate services when possible
- We want to simplify our deployment topology
- We need to maintain a small infrastructure footprint

Building identity management capabilities from scratch would be time-consuming and risky. Therefore, we need to select an established IAM solution that meets our requirements while also addressing our deployment constraints.

## Decision
We will adopt **Keycloak** as our identity and access management solution, using an **embedded deployment strategy** where Keycloak runs within our Spring Boot application rather than as a separate service.

### 1. Embedded Deployment Approach
- Use Keycloak Embedded Server library to run Keycloak within our Spring Boot application
- Configure Keycloak to use the same database as our application
- Start and manage Keycloak server lifecycle as part of our application startup
- Access Keycloak's API programmatically from within our application when needed

### 2. Core Identity Management Features
- User registration and profile management
- Password policies and recovery workflows
- Multi-factor authentication (MFA)
- Session management
- Account linking and social login
- User federation with LDAP/Active Directory

### 3. Authentication & Authorization
- OAuth 2.0 implementation (all standard flows)
- OpenID Connect support
- Fine-grained role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Client access management
- Token customization

### 4. Integration Approach
- Direct programmatic access to Keycloak APIs within the application
- Spring Security integration for protecting application endpoints
- Shared database schema for application and Keycloak data
- Custom health checks and monitoring

## Implementation Approach
We will implement embedded Keycloak with the following approach:

1. **Embedded Server Configuration**
   - Add Keycloak Embedded Server dependency to our Spring Boot application
   - Configure Keycloak to use our application's database
   - Configure custom startup and shutdown hooks
   - Disable features not needed in embedded mode

2. **Deployment Strategy**
   - Package Keycloak within our application JAR/WAR file
   - Configure embedded server to use appropriate ports and contexts
   - Set up proper memory allocation for the embedded server
   - Implement graceful startup and shutdown procedures

3. **Integration with Our Application**
   - Use Spring Security OAuth2 Resource Server for API protection
   - Configure direct programmatic access to Keycloak's admin APIs
   - Ensure proper transaction management between application and Keycloak

4. **User Management**
   - Define initial roles and groups structure
   - Configure password policies and MFA requirements
   - Set up self-service registration and profile management

5. **Custom Theming**
   - Package custom themes within the application
   - Configure theme loader for embedded deployment

## Consequences

### Positive
- Simplified deployment with a single application to manage
- Reduced infrastructure complexity and operational overhead
- Shared database connection pool and resources
- No network latency between application and identity provider
- Easier development and testing environment setup
- Reduced total infrastructure cost
- Simpler backup and restore procedures
- Consistent scaling as a single unit

### Negative
- Higher memory footprint for the application
- Potential resource contention between application and Keycloak
- More complex application startup and shutdown procedures
- Limited ability to scale Keycloak independently
- Potential challenges with Keycloak version upgrades
- Less isolation between application and identity provider
- Fewer deployment options for high availability
- Not the standard deployment pattern, so less community guidance
- May complicate clustering in the future

## Alternatives Considered

1. **Standalone Keycloak Deployment**
   - Better isolation between services
   - Independent scaling and resource allocation
   - Standard deployment with better community support
   - More complex infrastructure and operations
   - Higher total resource usage

2. **Auth0**
   - Fully managed authentication service
   - No deployment concerns
   - Higher cost for growing user base
   - Less control over data and infrastructure
   - Potential vendor lock-in

3. **Custom Implementation with Spring Security**
   - Complete control over implementation
   - Tailored to our exact requirements
   - Significantly higher development effort
   - Higher security risk of custom implementation
   - Diversion of resources from core business functionality

4. **Lightweight Alternatives (e.g., jHipster UAA)**
   - Designed for microservices architecture
   - Potentially smaller footprint
   - Less comprehensive feature set
   - Less mature and less community support
   - Limited enterprise integration options

## Implementation Notes

### Gradle Dependencies (Kotlin DSL)

```kotlin
dependencies {
    // Keycloak embedded server
    implementation("org.keycloak:keycloak-embedded-server:${property("keycloak.version")}")
    
    // Keycloak Spring Boot integration
    implementation("org.keycloak:keycloak-spring-boot-starter:${property("keycloak.version")}")
    
    // Spring Security OAuth2 Resource Server
    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
}
```

### Embedded Server Configuration

```java
@Configuration
public class KeycloakServerConfig {

    @Bean
    public EmbeddedKeycloakServer embeddedKeycloakServer() {
        return new EmbeddedKeycloakServer();
    }

    @Bean
    public ServerProperties serverProperties() {
        ServerProperties bean = new ServerProperties();
        bean.setContextPath("/auth");
        return bean;
    }

    @Bean
    public FilterRegistrationBean<KeycloakSessionServletFilter> keycloakSessionManagement() {
        FilterRegistrationBean<KeycloakSessionServletFilter> filter = new FilterRegistrationBean<>();
        filter.setFilter(new KeycloakSessionServletFilter());
        filter.addUrlPatterns("/auth/*");
        return filter;
    }
}

public class EmbeddedKeycloakServer implements InitializingBean, DisposableBean {

    private KeycloakServer keycloakServer;

    @Override
    public void afterPropertiesSet() throws Exception {
        System.setProperty("keycloak.embedded", "true");
        System.setProperty("keycloak.configurationFile", "classpath:keycloak-server.json");
        
        keycloakServer = KeycloakServer.bootstrap(
            new KeycloakServerConfig.KeycloakServerProperties());
    }

    @Override
    public void destroy() {
        keycloakServer.stop();
    }
}
```

### Application Security Configuration

```java
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .cors()
            .and()
            .csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeRequests()
                .antMatchers("/auth/**").permitAll()  // Keycloak endpoints
                .antMatchers("/api/v*/public/**").permitAll()
                .antMatchers("/v3/api-docs/**", "/swagger-ui/**").permitAll()
                .anyRequest().authenticated()
            .and()
            .oauth2ResourceServer()
                .jwt();
    }
}
```

### Keycloak Server Configuration (keycloak-server.json)

```json
{
  "hostname": {
    "provider": "${keycloak.hostname.provider:default}",
    "fixed": {
      "hostname": "${keycloak.hostname.fixed.hostname:localhost}",
      "port": "${keycloak.hostname.fixed.port:8080}"
    }
  },
  "admin": {
    "realm": "master"
  },
  "eventsStore": {
    "provider": "${keycloak.eventsStore.provider:jpa}"
  },
  "realm": {
    "provider": "${keycloak.realm.provider:jpa}"
  },
  "user": {
    "provider": "${keycloak.user.provider:jpa}"
  },
  "userFederatedStorage": {
    "provider": "${keycloak.userFederatedStorage.provider:jpa}"
  },
  "userSessionPersister": {
    "provider": "${keycloak.userSessionPersister.provider:jpa}"
  },
  "authorizationPersister": {
    "provider": "${keycloak.authorization.provider:jpa}"
  },
  "theme": {
    "staticMaxAge": "${keycloak.theme.staticMaxAge:2592000}",
    "cacheTemplates": "${keycloak.theme.cacheTemplates:true}",
    "cacheThemes": "${keycloak.theme.cacheThemes:true}",
    "folder": {
      "dir": "${keycloak.theme.dir}"
    }
  },
  "connectionsJpa": {
    "provider": "default",
    "dataSource": "java:jboss/datasources/KeycloakDS",
    "initializeEmpty": true,
    "migrationStrategy": "update",
    "showSql": false,
    "formatSql": true,
    "globalStats": false
  }
}
```

### Application Properties Configuration

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/appdb
    username: appuser
    password: apppassword
    driver-class-name: org.postgresql.Driver
    
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:8080/auth/realms/our-application
          jwk-set-uri: http://localhost:8080/auth/realms/our-application/protocol/openid-connect/certs

server:
  port: 8080
  
keycloak:
  embedded:
    enabled: true
  server:
    context-path: /auth
  realm: our-application
  resource: app-client
  public-client: true
  principal-attribute: preferred_username
```

## Compliance Verification
- Regular security audits of embedded Keycloak configuration
- Performance testing to ensure adequate resource allocation
- Memory profiling to optimize JVM settings
- Testing of startup and shutdown procedures
- Verification of data integrity between application and Keycloak schemas
- Disaster recovery testing
- Load testing to ensure performance under concurrent authentication requests

## References
- Keycloak Embedded Documentation: https://www.keycloak.org/docs/latest/server_development/#_embed_keycloak
- Spring Boot with Embedded Keycloak: https://www.baeldung.com/keycloak-embedded-in-spring-boot-app
- Keycloak Server SPI: https://www.keycloak.org/docs/latest/server_development/#_providers
- Spring Security OAuth2 Resource Server: https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html
- Keycloak Admin REST API: https://www.keycloak.org/docs-api/latest/rest-api/
