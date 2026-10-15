# ADR-0010: Development Environment Configuration

## Status
**Accepted**

## Context
During the development of the Nucleus admin dashboard, we encountered several integration challenges between the Vue.js frontend and ASP.NET Core backend:

1. **HTTPS Redirect Issues**: The backend was configured to redirect HTTP requests to HTTPS, causing redirect loops in development
2. **CORS Configuration**: Cross-origin requests between frontend (localhost:3000) and backend (localhost:5001) needed proper configuration
3. **API Communication**: Frontend needed seamless communication with backend API endpoints
4. **Development Workflow**: Developers needed fast, reliable development experience

The team needed to establish a development environment configuration that would enable smooth frontend-backend integration while maintaining security and performance.

## Decision
We implemented the following development environment configuration:

### Backend Configuration
- **HTTPS Redirect**: Disabled `UseHttpsRedirection()` in development environment only
- **CORS Policy**: Configured "AllowAll" policy for development with proper production restrictions
- **Port Configuration**: Backend runs on HTTP port 5001 and HTTPS port 7001
- **Environment Detection**: Used `app.Environment.IsDevelopment()` for conditional configuration

### Frontend Configuration
- **Vite Proxy**: Configured proxy to forward `/api` requests to `http://localhost:5001`
- **Development Server**: Frontend runs on `http://localhost:3000`
- **Proxy Events**: Added proxy event handlers for debugging and monitoring
- **Secure Flag**: Set `secure: false` for development proxy configuration

### Development Workflow
- **Hot Reload**: Vite provides hot module replacement for frontend changes
- **API Proxy**: Seamless API communication without CORS issues
- **Error Handling**: Comprehensive error handling and debugging capabilities
- **Environment Separation**: Clear separation between development and production configurations

## Consequences

### Positive
- **Seamless Development**: Frontend and backend integrate smoothly without configuration issues
- **Fast Iteration**: Hot reload and proxy enable rapid development cycles
- **Debugging**: Proxy event handlers provide visibility into API communication
- **Security**: HTTPS redirect remains enabled in production environments
- **Flexibility**: Environment-specific configuration allows different settings per environment

### Negative
- **Environment Complexity**: Different configurations for development vs production
- **Security Risk**: CORS "AllowAll" policy in development (mitigated by environment detection)
- **Configuration Management**: Need to maintain separate configurations for different environments

### Neutral
- **Port Management**: Multiple ports required for development (3000, 5001, 7001)
- **Documentation**: Additional documentation needed for environment setup

## Rationale
The decision to disable HTTPS redirect in development was driven by:

1. **Development Efficiency**: Eliminates redirect loops and simplifies API communication
2. **Security**: HTTPS redirect remains enabled in production for security
3. **Environment Separation**: Clear distinction between development and production configurations

The Vite proxy configuration was chosen because:

1. **Seamless Integration**: Eliminates CORS issues in development
2. **Debugging**: Provides visibility into API requests and responses
3. **Performance**: No additional network hops for API communication
4. **Simplicity**: Single configuration handles all API endpoints

The CORS "AllowAll" policy in development was justified by:

1. **Development Speed**: Eliminates CORS configuration complexity during development
2. **Security**: Only applies to development environment
3. **Flexibility**: Allows testing from different origins during development

## Related Decisions
- [ADR-0009: Vue.js Admin Dashboard Architecture](../adr/ADR-0009-vue-admin-dashboard.md)
- [ADR-0002: ASP.NET Core](../adr/ADR-0002-aspnet-core.md)

## References
- [ASP.NET Core Environment Configuration](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/environments)
- [Vite Proxy Configuration](https://vitejs.dev/config/#server-proxy)
- [CORS in ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/security/cors) 