# ADR 006: Azure Application Insights for Observability

**Status**: Accepted  
**Date**: 2024-12-XX  
**Deciders**: Development Team  
**Technical Story**: Monitoring, logging, and distributed tracing

## Context

Sistema distribuido con múltiples microservicios requiere:

- **Distributed tracing**: Request flow across services
- **Logging**: Centralized log aggregation
- **Metrics**: Performance, availability, dependencies
- **Alerting**: Proactive issue detection

Opciones evaluadas:

1. **Azure Application Insights**
2. ELK Stack (Elasticsearch, Logstash, Kibana)
3. Prometheus + Grafana + Loki
4. DataDog
5. New Relic

## Decision

**Azure Application Insights** + Log Analytics Workspace

### Ventajas

- ✅ **Integration**: Nativo .NET, auto-instrumentation
- ✅ **Distributed Tracing**: Automatic correlation IDs
- ✅ **Cost**: Reasonable para dev/small-scale
- ✅ **Tooling**: Azure Portal, VS Code extension, KQL queries
- ✅ **Alerts**: Built-in alerting rules
- ✅ **Learning Curve**: Familiar para Azure devs

### Comparación

| Feature                | App Insights | ELK | Prometheus+Grafana | DataDog |
|-----------------------|-------------|-----|-------------------|---------|
| .NET Auto-Instrument  | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Distributed Tracing   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Setup Complexity      | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Cost (managed)        | $$ | Self/$$$ | Self/$ | $$$ |
| Query Language        | KQL | Lucene | PromQL | Custom |

## Consequences

### Positive

- Zero-config distributed tracing con correlation IDs
- Live Metrics Stream para debugging real-time
- Smart Detection de anomalías (ML-powered)
- Integración Terraform para IaC

### Negative

- Vendor lock-in Azure
- Costo escala con volumen (sampling requerido en producción)
- KQL learning curve

### Mitigations

- **Lock-in**: OpenTelemetry wrapper para portabilidad futura
- **Costo**: Adaptive sampling + retention policies
- **KQL**: Documentar queries comunes en runbook

## Implementation

### Current Resources (Terraform)

```hcl
resource "azurerm_application_insights" "main" {
  name                = "interstellar-tracker-dev-ai"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
}
```

### .NET Integration

```csharp
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.ConnectionString = builder.Configuration["ApplicationInsights:ConnectionString"];
});
```

### Alerts Configured

1. **Response Time** > 1s (95th percentile)
2. **Failure Rate** > 5%
3. **Dependency Failures** > 3 in 5min

### Queries Útiles

```kql
// Request duration P95
requests
| where timestamp > ago(1h)
| summarize percentile(duration, 95) by bin(timestamp, 5m)

// Failed dependencies
dependencies
| where success == false
| summarize count() by target, resultCode
```

## Future Enhancements

### Phase 4 (RabbitMQ)

- Track message broker metrics
- Dead-letter queue monitoring

### Phase 5 (SonarQube)

- Correlate code quality with runtime issues

### Production

- Application Map para visualización
- Availability tests (synthetic monitoring)
- Profiler para CPU/memory analysis

## References

- [Application Insights Documentation](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- `terraform/environments/dev/main.tf`
- `docs/monitoring.md`
- ADR-001: Clean Architecture
