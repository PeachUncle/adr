# ADR-009: API Documentation Strategy for Spring Boot Application

## Status
Accepted

## Date
2025-03-01

## Context
Our Spring Boot application exposes REST APIs that will be consumed by various clients including internal teams, external partners, and potentially public developers. Comprehensive, accurate, and up-to-date API documentation is essential for:

- Enabling developers to understand and use our APIs correctly
- Reducing onboarding time for new team members and API consumers
- Ensuring consistency between documentation and actual implementation
- Supporting our API versioning strategy
- Facilitating API testing and client code generation
- Improving overall developer experience

Without a well-defined documentation strategy, we risk having outdated or incomplete documentation, inconsistent documentation formats across different parts of the API, and increased support burden due to documentation-related questions.

## Decision
We will implement an API documentation strategy with the following key elements:

### 1. Documentation Approach
We will use **OpenAPI Specification** (formerly Swagger) as our API documentation standard, implemented through SpringDoc (which is based on springdoc-openapi). This will provide:

- A standardized format for API documentation
- Interactive API documentation UI
- Machine-readable API specifications
- Client code generation capabilities
- Integration with our Spring Boot application

### 2. Implementation Details
- We will use annotations in our controller classes to document endpoints
- Documentation will be code-first, generated directly from our source code
- The OpenAPI specification will be automatically generated at build time
- Documentation will be version-specific, aligned with our API versioning strategy
- We will host interactive documentation at `/swagger-ui.html`
- The OpenAPI JSON specification will be available at `/v3/api-docs`

### 3. Documentation Content Requirements
Each API endpoint will be documented with:

- Clear description of purpose and functionality
- All path, query, and header parameters with descriptions and constraints
- Request body schema with field descriptions and validation rules
- Response body schema for each possible response code
- All possible response status codes with descriptions
- Authentication requirements
- Rate limiting information (if applicable)
- Example requests and responses
- Deprecation notices and migration paths (when applicable)

### 4. Code Standards for Documentation
- Every REST controller class must include a `@Tag` annotation with description
- Every controller method must include an `@Operation` annotation with summary and description
- All DTOs must use `@Schema` annotations for field descriptions
- All parameters must include `@Parameter` annotations with descriptions
- All possible responses must be documented with `@ApiResponse`
- Custom validation constraints should include descriptive messages

### 5. Documentation Versioning
- Each API version will have its own separate OpenAPI documentation
- We will use SpringDoc's grouping feature to organize documentation by version
- The documentation URL will include the version: `/swagger-ui.html?configId=v1`
- Deprecated endpoints will be clearly marked with deprecation notices

### 6. Additional Documentation
Beyond the OpenAPI specification, we will provide:

- Getting started guides for common use cases
- Authentication and authorization guides
- Rate limiting and quota information
- Change logs between API versions
- Postman collections for manual testing
- Code examples in popular languages

### 7. Documentation Review Process
- API documentation will be reviewed as part of the code review process
- Automated tests will verify the OpenAPI specification is valid
- Documentation completeness will be part of our definition of done

## Consequences

### Positive
- Self-documenting code ensures documentation stays in sync with implementation
- Standardized documentation format improves consistency
- Interactive documentation facilitates API exploration and testing
- Machine-readable specifications enable client code generation
- Improved developer experience for API consumers
- Reduced support burden related to API usage questions
- Better visibility into API capabilities and requirements
- Documentation becomes a first-class citizen in the development process

### Negative
- Requires additional development effort to maintain comprehensive annotations
- Annotations can make controller code more verbose
- Generated documentation may not cover all complex scenarios or business rules
- May require additional customization for specific documentation needs
- Keeping examples up-to-date requires ongoing maintenance

## Alternatives Considered

1. **Manual Documentation**
   - Using tools like Confluence or Markdown files
   - More flexibility in documentation structure and content
   - Higher risk of documentation becoming outdated
   - No interactive testing capabilities
   - No automatic client code generation

2. **RAML (RESTful API Modeling Language)**
   - Design-first approach to API documentation
   - Strong typing and modeling capabilities
   - Less integration with Spring Boot
   - Smaller community and ecosystem compared to OpenAPI

3. **Spring REST Docs**
   - Test-driven documentation approach
   - Documentation is automatically verified by tests
   - More complex setup and maintenance
   - Less interactive documentation compared to Swagger UI
   - Learning curve for the team

4. **GraphQL Schema Documentation**
   - Would require switching to GraphQL for our API
   - Self-documenting schema with introspection
   - Different paradigm than REST
   - Would require significant changes to our API design

## Implementation Notes

- We will use SpringDoc OpenAPI UI version 1.6.x or newer
- Configuration will be added to the application.yml file:

```yaml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
    display-request-duration: true
    groups-order: DESC
    operationsSorter: method
    disable-swagger-default-url: true
  show-actuator: false
  group-configs:
    - group: v1
      paths-to-match: /api/v1/**
    - group: v2
      paths-to-match: /api/v2/**
```

- Example controller documentation:

```java
@RestController
@RequestMapping("/api/v1/books")
@Tag(name = "Book Management", description = "APIs for managing books in the catalog")
public class BookController {

    @Operation(
        summary = "Get book by ID",
        description = "Retrieves a book from the catalog by its unique identifier",
        responses = {
            @ApiResponse(responseCode = "200", description = "Book found"),
            @ApiResponse(responseCode = "404", description = "Book not found"),
            @ApiResponse(responseCode = "401", description = "Unauthorized")
        }
    )
    @GetMapping("/{id}")
    public ResponseEntity<BookDTO> getBook(
        @Parameter(description = "The unique identifier of the book") 
        @PathVariable Long id
    ) {
        // Implementation
    }
}
```

- We will create a documentation configuration class:

```java
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("Bookstore API")
                .version("1.0")
                .description("API for the Bookstore application")
                .contact(new Contact()
                    .name("API Support")
                    .email("api-support@example.com")
                    .url("https://example.com/support"))
                .license(new License()
                    .name("Apache 2.0")
                    .url("https://www.apache.org/licenses/LICENSE-2.0")))
            .components(new Components()
                .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                    .type(SecurityScheme.Type.HTTP)
                    .scheme("bearer")
                    .bearerFormat("JWT")
                    .in(SecurityScheme.In.HEADER)
                    .name("Authorization")));
    }
}
```

## Compliance Verification
- Pull request reviews will check for proper documentation annotations
- Build process will generate and validate OpenAPI specification
- Automated tests will verify documentation endpoints are accessible
- Code quality tools will be configured to check for missing documentation
- Periodic reviews of the generated documentation will be conducted

## References
- OpenAPI Specification: https://spec.openapis.org/oas/latest.html
- SpringDoc OpenAPI: https://springdoc.org/
- Spring Boot REST API Documentation: https://www.baeldung.com/spring-rest-openapi-documentation
- Swagger Annotations Guide: https://github.com/swagger-api/swagger-core/wiki/Swagger-2.X---Annotations
