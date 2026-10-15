# ADR 005: YARP for API Gateway

**Status**: Accepted  
**Date**: 2024-12-XX  
**Deciders**: Development Team  
**Technical Story**: API Gateway implementation for microservices routing

## Context

Necesitamos un API Gateway para:

- Routing centralizado a microservicios
- Load balancing
- Rate limiting
- Authentication/Authorization edge
- Telemetry unificada

Opciones evaluadas:

1. **YARP** (Yet Another Reverse Proxy)
2. Ocelot
3. Azure API Management
4. Kong
5. Custom gateway con ASP.NET Core

## Decision

**Elegimos YARP** (Microsoft.ReverseProxy)

### Ventajas

- ✅ **Performance**: Alto throughput, baja latencia (basado en ASP.NET Core)
- ✅ **Flexibilidad**: Configuración dinámica, extensible
- ✅ **Mantenimiento**: Microsoft OSS, .NET nativo
- ✅ **Observability**: Integración nativa con Application Insights
- ✅ **Costo**: Open source, sin licencias
- ✅ **Learning curve**: Familiar para equipo .NET

### Comparación

| Feature              | YARP | Ocelot | Azure APIM | Kong |
|---------------------|------|--------|-----------|------|
| Performance         | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| .NET Integration    | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Cost (self-hosted)  | Free | Free | $$$ | Free/$$$ |
| Active Development  | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Community           | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Consequences

### Positive

- Control completo sobre routing logic
- Fácil integración con Application Insights
- Deployment como cualquier app .NET
- Hot-reload de configuración sin downtime

### Negative

- Feature set menor que Azure APIM (no built-in dev portal, analytics UI)
- Requiere código C# para funcionalidades avanzadas
- Self-hosted: responsabilidad de HA, scaling

### Mitigations

- Para analytics: usamos Grafana + Prometheus
- Para HA: Kubernetes con 3+ replicas
- Documentación API: Swagger UI agregado

## Implementation Notes

### Configuration

```json
{
  "ReverseProxy": {
    "Routes": {
      "calculation-route": {
        "ClusterId": "calculation-cluster",
        "Match": { "Path": "/api/calculations/{**catch-all}" }
      }
    },
    "Clusters": {
      "calculation-cluster": {
        "Destinations": {
          "destination1": { "Address": "http://calculation-service:5001" }
        }
      }
    }
  }
}
```

### Extensions

- Custom middleware para logging
- Rate limiting: AspNetCoreRateLimit
- Auth: JWT validation antes de proxy

## References

- [YARP Documentation](https://microsoft.github.io/reverse-proxy/)
- ADR-001: Clean Architecture + Microservices
- `src/Services/ApiGateway/InterstellarTracker.ApiGateway/`
