# ADR 003: Adopt Scalar for Interactive API Documentation

**Status**: Proposed  
**Date**: 2025-09-29  
**Deciders**: Development Team  
**Technical Story**: [Link to related issue or story]

## Context

The Patient Health Record application currently uses Swagger UI for API documentation, integrated through FastEndpoints' `SwaggerDocument` configuration. While functional, Swagger UI provides a basic interface that may not offer the best user experience for developers exploring and testing the API.

Scalar is an open-source alternative to Swagger UI that provides a more modern, interactive, and user-friendly interface for API documentation. It supports OpenAPI specifications and offers features like better navigation, request/response examples, and a cleaner design.

The application is built with ASP.NET Core 9 and uses FastEndpoints for API routing. The current setup generates OpenAPI documents via the Microsoft.AspNetCore.OpenApi package, which is compatible with Scalar.

## Decision

We will adopt Scalar as the primary interactive API documentation tool, replacing the current Swagger UI implementation.

### Implementation Details

1. **Install Scalar.AspNetCore Package**:

   ```bash
   dotnet add package Scalar.AspNetCore
   ```

2. **Update Program.cs**:
   - Remove or comment out the existing Swagger UI configuration
   - Add Scalar configuration in the development environment:

   ```csharp
   if (app.Environment.IsDevelopment())
   {
       app.MapScalarApiReference();
   }
   ```

3. **Update Launch Settings**:
   - Set the launch URL to "" (empty string) in `launchSettings.json` for direct access to the documentation at the root path

4. **Remove FastEndpoints SwaggerDocument**:
   - Remove the `.SwaggerDocument()` call from the FastEndpoints configuration

## Rationale

- **Improved User Experience**: Scalar provides a more modern and intuitive interface compared to Swagger UI
- **Better Integration**: Works seamlessly with ASP.NET Core's OpenAPI document generation
- **Open Source**: No licensing concerns, community-supported
- **Developer Productivity**: Enhanced navigation and testing capabilities
- **Consistency**: Aligns with modern API documentation standards

## Consequences

### Positive

- Enhanced developer experience when exploring and testing APIs
- More professional appearance for API documentation
- Better support for complex OpenAPI specifications
- Improved accessibility and usability

### Negative

- Additional dependency (Scalar.AspNetCore package)
- Potential learning curve for team members familiar with Swagger UI
- Requires development environment configuration

### Neutral

- No impact on production builds (only enabled in development)
- Maintains compatibility with existing OpenAPI generation

## Compliance

- Follows OWASP API Security guidelines for documentation
- Maintains security best practices by limiting to development environment
- Ensures accessibility standards are met by Scalar's design

## Implementation Notes

- Scalar will be configured to only run in development environments to avoid exposing API documentation in production
- The existing OpenAPI document generation will remain unchanged
- Team members should familiarize themselves with Scalar's interface and features
- Consider adding custom branding or configuration as needed

## Review Date

2026-03-29 (6 months from adoption)

## References

- [Scalar ASP.NET Core Integration Guide](https://guides.scalar.com/scalar/scalar-api-references/integrations/net-aspnet-core/integration)
- [Microsoft ASP.NET Core OpenAPI Documentation](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/using-openapi-documents?view=aspnetcore-9.0)
- [Scalar Official Website](https://scalar.com/)
- [FastEndpoints Documentation](https://fast-endpoints.com/)
