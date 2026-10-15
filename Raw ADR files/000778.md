---
docid: ADR-063
title: ADR 026 Bmecat Catalog Import Architecture
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-026: BMEcat Catalog Import Architecture

**Status**: Proposed  
**Date**: 3. Januar 2026  
**Owner**: @Architect  
**DocID**: `ADR-026`

---

## Context

B2X needs to support importing product catalogs in BMEcat format, a standard used by trade associations in Germany and Europe. The system must be able to:

1. Parse BMEcat XML files (version 1.2/2005)
2. Validate catalog data and structure
3. Store catalog metadata and products
4. Maintain data identifiability for catalog removal
5. Support tenant isolation
6. Provide progress tracking for large imports

### Business Requirements
- **Import Capability**: Accept BMEcat XML files via API
- **Data Identifiability**: Tag all imported data with catalog ID for removal
- **Tenant Isolation**: Catalogs must be tenant-specific
- **Performance**: Handle catalogs with 100k+ products
- **Reliability**: Robust error handling and validation

### Technical Constraints
- **Architecture**: Onion Architecture with Domain-Driven Design
- **Framework**: .NET 10 with Wolverine CQRS
- **Database**: PostgreSQL with multi-tenant schema
- **Security**: Input validation, XXE prevention, size limits

---

## Decision

### 1. Adapter Pattern for Catalog Import

**Chosen**: Implement BMEcat import as an adapter in the Catalog domain, following the existing adapter pattern for data exchange formats.

**Rationale**:
- Consistent with system requirements ("adapter hooks for BMECat/DATANORM")
- Allows easy extension to other formats (CSV, DATANORM)
- Keeps parsing logic isolated from domain logic
- Enables testing of import logic independently

**Implementation**:
```csharp
// Catalog.Application/Adapters
public interface ICatalogImportAdapter
{
    Task<ImportResult> ImportAsync(Stream catalogStream, CatalogMetadata metadata);
}

public class BmecatImportAdapter : ICatalogImportAdapter
{
    // BMEcat-specific parsing logic
}
```

### 2. Async Processing for Large Catalogs

**Chosen**: Use background processing for catalogs >1,000 products, synchronous for smaller catalogs.

**Rationale**:
- Large catalogs (>100k products) can take several minutes to process
- Prevents API timeouts and improves user experience
- Allows progress tracking and cancellation
- Balances complexity vs. performance

**Implementation**:
```csharp
// Command with processing strategy
public class ImportBmecatCommand
{
    public Stream CatalogStream { get; set; }
    public CatalogMetadata Metadata { get; set; }
    public ProcessingStrategy Strategy { get; set; } // Sync or Async
}

public enum ProcessingStrategy
{
    Synchronous,  // < 1k products
    Asynchronous  // >= 1k products
}
```

### 3. Composite Key for Data Identifiability

**Chosen**: Use composite key `{tenant_id}-{supplier_id}-{catalog_id}-{import_timestamp}` for catalog identification.

**Rationale**:
- Ensures uniqueness across tenants
- Allows multiple versions of same catalog
- Enables complete catalog removal
- Supports audit trails

**Database Schema**:
```sql
CREATE TABLE catalog_imports (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    supplier_id VARCHAR(100) NOT NULL,
    catalog_id VARCHAR(100) NOT NULL,
    import_timestamp TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    product_count INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(tenant_id, supplier_id, catalog_id, import_timestamp)
);

CREATE TABLE catalog_products (
    id UUID PRIMARY KEY,
    catalog_import_id UUID REFERENCES catalog_imports(id),
    supplier_aid VARCHAR(100) NOT NULL,
    product_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

### 4. XML Processing Strategy

**Chosen**: Use `System.Xml` with XSD validation for parsing and `XmlReader` for streaming large files.

**Rationale**:
- Built-in .NET XML support is robust and secure
- XSD validation prevents malformed data
- Streaming prevents memory issues with large files
- Better performance than DOM parsing

**Security Measures**:
- Disable DTD processing (XXE prevention)
- Set max file size (100MB)
- Validate against BMEcat 1.2 XSD schema

### 5. Progress Tracking

**Chosen**: Implement progress tracking with WebSocket updates for async imports.

**Rationale**:
- Large imports can take minutes to hours
- Users need visibility into processing status
- Enables cancellation of long-running imports
- Improves user experience

**Implementation**:
```csharp
public class ImportProgress
{
    public Guid ImportId { get; set; }
    public ImportStatus Status { get; set; }
    public int ProcessedProducts { get; set; }
    public int TotalProducts { get; set; }
    public string CurrentStep { get; set; }
    public DateTime UpdatedAt { get; set; }
}
```

---

## Consequences

### Positive
- **Extensibility**: Adapter pattern allows easy addition of other formats
- **Performance**: Async processing handles large catalogs efficiently
- **Security**: Built-in XML validation and size limits
- **User Experience**: Progress tracking for long operations
- **Compliance**: Complete data removal capability

### Negative
- **Complexity**: Async processing adds architectural complexity
- **Database Load**: Large catalogs create many database records
- **Memory Usage**: XML streaming still requires some buffering
- **Testing**: Async operations harder to test

### Risks
- **Performance Degradation**: Very large catalogs (>1M products) may need optimization
- **XML Vulnerabilities**: Need careful implementation of security measures
- **Data Consistency**: Async processing requires careful error handling

### Mitigation Strategies
- **Performance**: Implement batch processing and database indexing
- **Security**: Regular security audits and penetration testing
- **Testing**: Comprehensive integration tests with realistic data sizes
- **Monitoring**: Add metrics for import performance and success rates

---

## Alternatives Considered

### Alternative 1: Synchronous Only
- **Pros**: Simpler implementation, easier testing
- **Cons**: API timeouts for large catalogs, poor UX
- **Rejected**: Doesn't scale for enterprise catalogs

### Alternative 2: External Service (Azure Functions)
- **Pros**: Better scalability, isolation
- **Cons**: Additional complexity, latency, cost
- **Rejected**: Overkill for current requirements

### Alternative 3: Database-Only Solution
- **Pros**: Simpler, no XML parsing
- **Cons**: No validation, harder to extend
- **Rejected**: Doesn't meet BMEcat standard requirements

### Alternative 4: Third-Party Library
- **Pros**: Faster implementation, battle-tested
- **Cons**: Dependency management, licensing, customization
- **Rejected**: Built-in .NET XML support is sufficient

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)
- Create ICatalogImportAdapter interface
- Implement BmecatImportAdapter with basic parsing
- Add database tables and repositories
- Create ImportBmecatCommand handler

### Phase 2: Validation & Security (Week 3)
- Add XSD validation
- Implement security measures (XXE prevention, size limits)
- Add input sanitization
- Create unit tests

### Phase 3: Async Processing (Week 4)
- Implement background job processing
- Add progress tracking
- Create WebSocket notifications
- Add cancellation support

### Phase 4: API & UI Integration (Week 5)
- Create REST API endpoint
- Add frontend upload component
- Implement progress UI
- Add error handling

### Phase 5: Testing & Optimization (Week 6)
- Performance testing with large catalogs
- Integration testing
- Security testing
- Documentation

---

## Success Metrics

- **Import Success Rate**: >99% for valid BMEcat files
- **Performance**: <5 minutes for 100k products
- **Security**: Zero XXE vulnerabilities
- **Data Integrity**: 100% identifiable data removal
- **User Satisfaction**: Progress tracking for all async imports

---

## Related Documents

- **Requirements**: [REQ-002-bmecat-import.md](.ai/requirements/REQ-002-bmecat-import.md)
- **Security Review**: To be created
- **API Documentation**: To be created
- **Testing Plan**: To be created

---

**Status**: Proposed - Ready for Technical Review  
**Next**: Security review and implementation planning</content>
<parameter name="filePath">/Users/holger/Documents/Projekte/B2X/.ai/decisions/ADR-026-bmecat-catalog-import-architecture.md