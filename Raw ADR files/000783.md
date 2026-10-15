---
docid: ADR-071
title: ADR 029 Multi Format Punchout Integration
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-029: Multi-Format Punchout Integration for Craft Software

**Status:** Proposed  
**Date:** January 3, 2026  
**Owner:** @Architect  
**Stakeholders:** @Backend, @Frontend, @ProductOwner, @Security

## Context

B2X needs to integrate with German craft software systems (Handwerkersoftware) like Taifun, MSoft, and GWS to enable seamless procurement workflows between wholesalers and skilled trades. The integration must support four separate ITEK B2B standards as independent interfaces:

- **IDS Connect**: Shop system interface for direct catalog access
- **Open Masterdata**: Webservice for product data exchange  
- **OSD**: Open Shop Display punchout interface
- **OCI**: SAP Open Catalog Interface for punchout catalogs

Each interface has its own communication protocol but serves similar purposes in connecting craft software with B2X's catalog and ordering systems.

## Decision

Implement a **modular punchout gateway architecture** with four independent adapter services, each handling one ITEK standard. The architecture will:

1. **Separate Adapters**: One adapter service per ITEK standard
2. **Unified Gateway**: Central orchestration service for routing and tenant management
3. **Craft Software Integration**: Direct integration points for Taifun, MSoft, GWS systems
4. **Multi-Tenant Support**: Tenant-specific configurations and mappings

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Craft Software Systems                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │   Taifun    │ │   MSoft     │ │    GWS      │ ...        │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 B2X Punchout Gateway                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ IDS Connect │ │ Open Master │ │    OSD     │ │    OCI     │ │
│  │  Adapter    │ │   Adapter   │ │  Adapter   │ │  Adapter   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Unified Gateway Service                     │ │
│  │  • Request Routing & Load Balancing                         │ │
│  │  • Tenant Context Management                                │ │
│  │  • Authentication & Authorization                           │ │
│  │  • Response Aggregation                                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 B2X Core Services                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │   Catalog   │ │   Orders    │ │   Search    │            │
│  │  Service    │ │  Service    │ │  Service    │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Adapter Specifications

### IDS Connect Adapter
- **Protocol**: HTTP/HTTPS with XML payloads
- **Authentication**: API keys or OAuth2
- **Data Format**: IDS XML schema
- **Endpoints**: 
  - `/ids/catalog/search` - Product search
  - `/ids/catalog/details` - Product details
  - `/ids/order/create` - Order placement

### Open Masterdata Adapter  
- **Protocol**: SOAP webservice
- **Authentication**: WS-Security
- **Data Format**: Open Masterdata XML
- **Endpoints**:
  - `/masterdata/products` - Product data webservice
  - `/masterdata/categories` - Category hierarchy
  - `/masterdata/pricing` - Dynamic pricing

### OSD Adapter
- **Protocol**: HTTP POST with form data
- **Authentication**: Session tokens
- **Data Format**: OSD XML/HTML
- **Endpoints**:
  - `/osd/display` - Shop display interface
  - `/osd/cart` - Shopping cart operations
  - `/osd/checkout` - Order finalization

### OCI Adapter
- **Protocol**: HTTP GET/POST with query parameters
- **Authentication**: Basic auth or certificates
- **Data Format**: OCI XML
- **Endpoints**:
  - `/oci/hook` - Punchout initiation
  - `/oci/return` - Order return to ERP

## Implementation Strategy

### Phase 1: Core Infrastructure (2-3 weeks)
- Implement unified gateway service
- Set up tenant configuration management
- Create adapter base framework
- Establish monitoring and logging

### Phase 2: IDS Connect & Open Masterdata (3-4 weeks)
- Implement IDS Connect adapter
- Implement Open Masterdata adapter
- Integration testing with sample data
- Documentation and API specs

### Phase 3: OSD & OCI (3-4 weeks)
- Implement OSD adapter
- Implement OCI adapter
- Cross-format testing
- Performance optimization

### Phase 4: Craft Software Integration (2-3 weeks)
- Taifun system integration
- MSoft system integration  
- GWS system integration
- End-to-end testing

## Technical Considerations

### Data Mapping & Transformation
- Each adapter handles format-specific data mapping
- Unified internal data model for B2X core services
- Configurable field mappings per tenant

### Error Handling & Resilience
- Circuit breaker pattern for adapter failures
- Retry mechanisms with exponential backoff
- Fallback responses for degraded service

### Security & Compliance
- End-to-end encryption for all interfaces
- Audit logging for all transactions
- GDPR compliance for customer data handling

### Performance & Scalability
- Asynchronous processing for high-volume requests
- Caching layer for frequently accessed data
- Horizontal scaling support for adapters

## Risks & Mitigations

### Risk: Complex Integration Testing
**Mitigation**: Start with mock adapters, implement comprehensive test suites

### Risk: Protocol Version Compatibility  
**Mitigation**: Version negotiation and backward compatibility support

### Risk: Performance Bottlenecks
**Mitigation**: Load testing early, implement caching and optimization

### Risk: Security Vulnerabilities
**Mitigation**: Security review at each phase, penetration testing

## Success Metrics

- **Functional**: All four adapters operational with test craft software
- **Performance**: <500ms response time for catalog searches
- **Reliability**: 99.9% uptime for production deployments
- **Security**: Zero security incidents in first 6 months
- **Adoption**: Integration with at least 3 craft software systems

## Alternatives Considered

### Option 1: Single Unified Adapter
**Rejected**: Would require complex conditional logic and make maintenance difficult

### Option 2: External Punchout Service
**Rejected**: Would introduce vendor dependency and reduce control over integration

### Option 3: Fallback Chain Architecture
**Rejected**: Standards are independent interfaces, not hierarchical fallbacks

## Conclusion

The modular adapter architecture provides the flexibility needed to support multiple ITEK standards while maintaining clean separation of concerns. Each adapter can be developed, tested, and deployed independently, reducing risk and enabling incremental delivery.

This approach enables B2X to serve the German craft software ecosystem effectively, supporting seamless procurement workflows for skilled trades using their preferred software systems.

## Next Steps

1. Create detailed technical specifications for each adapter
2. Set up development environment with mock services
3. Begin implementation of unified gateway service
4. Schedule kickoff meeting with craft software vendors

---

**References:**
- [KB-021] enventa Trade ERP Integration
- [ADR-028] ERP API Integration Architecture  
- ITEK Standards Documentation
- Taifun, MSoft, GWS Integration Requirements