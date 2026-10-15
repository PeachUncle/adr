---
docid: ADR-059
title: ADR 024 Dapr Evaluation Deferred
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-024: Dapr Evaluation - Deferred

**Status**: Accepted  
**Date**: 2. Januar 2026  
**Deciders**: @SARAH, @Architect, @Backend, @DevOps, @TechLead  
**Technical Story**: Team Brainstorming - Dapr im B2X-Projekt

## Context

Das Team evaluierte den Einsatz von [Dapr (Distributed Application Runtime)](https://dapr.io/) als ergänzende oder alternative Infrastruktur für B2X.

### Aktueller Tech-Stack

| Komponente | Technologie | Status |
|------------|-------------|--------|
| Orchestrierung | .NET Aspire | ✅ Produktiv |
| CQRS/Messaging | Wolverine | ✅ Produktiv |
| Service Communication | HTTP/gRPC (direkt) | ✅ Produktiv |
| State Management | EF Core + PostgreSQL | ✅ Produktiv |
| Pub/Sub | Wolverine (in-process) | ✅ Produktiv |
| Resilience | Polly | ✅ Gerade implementiert |
| ERP Integration | Custom Actor Pattern | ✅ Gerade implementiert |

### Dapr Capabilities vs. Aktuelle Lösung

| Capability | Dapr | B2X (aktuell) | Overlap |
|------------|------|---------------------|---------|
| Service Invocation | Sidecar-Proxy | Direkte HTTP/gRPC | Vollständig |
| State Management | Pluggable Stores | EF Core + PostgreSQL | Vollständig |
| Pub/Sub | Multi-Broker | Wolverine | Teilweise |
| Actors | Virtual Actors | Custom ErpActor | Teilweise |
| Secrets | Secret Stores | Azure Key Vault | Vollständig |
| Observability | Built-in | Aspire Dashboard | Vollständig |
| Resilience | Built-in Retries | Polly | Vollständig |

## Decision

**Dapr wird zum aktuellen Zeitpunkt NICHT eingeführt.**

Die Entscheidung wird bei folgenden Triggern re-evaluiert:
- Kubernetes Production Rollout
- Multi-Cloud Deployment Anforderungen
- Cross-Service Event-Architektur

## Rationale

### Warum NICHT jetzt?

1. **Kein Mehrwert gegenüber bestehendem Stack**
   - Aspire + Wolverine + Polly decken alle aktuellen Anforderungen ab
   - ERP Actor Pattern mit Polly Resilience gerade fertig implementiert
   - Zusätzliche Komplexität ohne klaren Business-Nutzen

2. **Overlap mit bestehender Infrastruktur**
   - Wolverine ist für CQRS spezialisierter als Dapr Pub/Sub
   - Aspire bietet bereits exzellente Dev/Prod Orchestrierung
   - Polly Resilience Pipeline gerade implementiert

3. **Operationale Komplexität**
   - Sidecar pro Service = mehr Ressourcenverbrauch
   - Zusätzliche Lernkurve für Team
   - Debugging komplexer durch Sidecar-Indirektion

4. **ERP Integration bleibt Custom**
   - Kein Dapr-Binding für enventa Trade ERP
   - Custom ErpActor mit gRPC/.NET Framework Bridge bleibt nötig
   - Dapr Actors würden Migration erfordern ohne klaren Vorteil

### Wo Dapr ZUKÜNFTIG Sinn machen könnte

1. **Kubernetes Production**
   - Service Mesh Capabilities ohne Istio-Komplexität
   - Einheitliche Observability über alle Services

2. **Multi-Cloud Deployment**
   - Vendor-unabhängige Abstraktion
   - Portabilität zwischen Azure, AWS, On-Premise

3. **Cross-Service Events**
   - Wenn echte verteilte Microservices entstehen
   - Broker-agnostisches Pub/Sub (RabbitMQ, Kafka, Azure Service Bus)

## Alternatives Considered

### Alternative 1: Vollständige Dapr-Adoption
- **Pro**: Einheitliches Programmiermodell, Future-Proof
- **Contra**: Hoher Migrationsaufwand, Overlap mit Wolverine
- **Entscheidung**: Abgelehnt - ROI nicht gegeben

### Alternative 2: Dapr nur für Actors (ERP)
- **Pro**: Dapr Actors könnten ErpActor vereinfachen
- **Contra**: Gerade Polly Resilience implementiert, Migration-Aufwand
- **Entscheidung**: Abgelehnt - bestehende Lösung funktioniert

### Alternative 3: Dapr als Service Mesh (später)
- **Pro**: Sinnvoll bei K8s Production
- **Contra**: Aktuell nicht relevant
- **Entscheidung**: Deferred - Re-Evaluation bei K8s Rollout

## Consequences

### Positive
- Fokus bleibt auf Feature-Entwicklung statt Infrastruktur-Migration
- Keine zusätzliche Komplexität im aktuellen Sprint
- Team-Expertise in Wolverine + Aspire wird vertieft
- Ressourcen bleiben schlank (kein Sidecar-Overhead)

### Negative
- Potenzielle spätere Migration wenn Dapr doch benötigt
- Kein standardisiertes Service Mesh Pattern (vorerst)

### Neutral
- Entscheidung ist reversibel
- Dapr-Evaluation kann jederzeit wieder aufgenommen werden

## Re-Evaluation Trigger

Diese Entscheidung wird automatisch re-evaluiert wenn:

| Trigger | Verantwortlich | Aktion |
|---------|---------------|--------|
| K8s Production geplant | @DevOps | Dapr als Service Mesh evaluieren |
| Multi-Cloud Requirement | @Architect | Dapr Abstraction evaluieren |
| Cross-Service Events benötigt | @Backend | Dapr Pub/Sub evaluieren |
| Neue Dapr Major Version | @TechLead | Feature-Review |

## Related Decisions

- [ADR-001](ADR-001-event-driven-architecture.md) - Event-Driven Architecture (Wolverine)
- [ADR-003](../DOCUMENT_REGISTRY.md) - Aspire Orchestration
- [ADR-023](ADR-023-erp-plugin-architecture.md) - ERP Plugin Architecture (Actor Pattern)

## References

- [Dapr Official Documentation](https://docs.dapr.io/)
- [Dapr .NET SDK](https://github.com/dapr/dotnet-sdk)
- [Dapr vs. Service Mesh Comparison](https://docs.dapr.io/concepts/service-mesh/)
- [.NET Aspire Overview](https://learn.microsoft.com/en-us/dotnet/aspire/get-started/aspire-overview)
- [Wolverine Documentation](https://wolverine.netlify.app/)

---

## Sign-Off

| Role | Agent | Decision | Date |
|------|-------|----------|------|
| Coordinator | @SARAH | ✅ Approved | 2026-01-02 |
| Architecture | @Architect | ✅ Approved | 2026-01-02 |
| Backend | @Backend | ✅ Approved | 2026-01-02 |
| DevOps | @DevOps | ✅ Approved | 2026-01-02 |
| Tech Lead | @TechLead | ✅ Approved | 2026-01-02 |

---

**Next Review**: Bei Kubernetes Production Planung oder Q2 2026
