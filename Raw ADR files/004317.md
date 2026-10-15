# ADR-007: W3C PROV Compliance for Provenance

## Status
Accepted

## Context
ToolVault supports scientific reproducibility and quality assurance in analytical workflows. The UK Government's Reproducible Analytical Pipelines (RAPs) initiative emphasizes the need for traceable, reproducible analysis. Users must be able to verify how results were produced and reproduce analytical processes. Provenance information must travel with output data to ensure it remains accessible when files are shared independently of ToolVault.

## Decision
We will implement W3C PROV-compliant provenance tracking with the following characteristics:

### Compliance Level
- **PROV-compatible JSON-LD subset**: Covers essential W3C PROV concepts in practical format
- **Standards alignment**: Ensures interoperability while maintaining implementation simplicity
- **Extensible foundation**: Allows future enhancement to full PROV-DM if needed

### Embedding Strategy
- **Direct embedding**: Provenance embedded directly within output files using format-native metadata
- **Format-specific approach**: Leverage each file type's native metadata capabilities
  - GeoJSON: Custom properties in feature metadata
  - CSV: Structured comments in file headers
  - Images: EXIF metadata or embedded annotations
  - Custom formats: Defined metadata sections

### Provenance Granularity
- **Standard level capture**:
  - Tool identity and version (from bundle timestamp)
  - Execution timestamp and duration
  - User identity (when available)
  - Input parameters and configuration
  - Input data checksums/identifiers
  - Execution environment details (ToolVault version, platform)
  - Output data characteristics

### Pipeline Provenance
- **Reference-based chaining**: Each tool records provenance of its immediate inputs only
- **Traceable lineage**: Full pipeline reconstructible by following provenance references
- **Manageable complexity**: Avoids exponential growth in multi-step workflows

## Rationale

### Scientific Reproducibility
PROV compliance enables others to understand and reproduce analytical processes, supporting scientific rigor and the UK Government's RAP objectives.

### Embedded Provenance Necessity
Direct embedding ensures provenance cannot be accidentally separated from data when files are shared, moved, or archived independently of ToolVault.

### JSON-LD Practicality
PROV-compatible JSON-LD provides standards compliance while remaining human-readable and easy to process programmatically without RDF complexity.

### Format-Specific Integration
Using native metadata capabilities ensures compatibility with existing tools and workflows while preserving provenance information.

### Reference-Based Pipeline Tracking
Immediate-input-only recording maintains provenance chains without creating unmanageably large provenance records in complex pipelines.

## Consequences

### Positive
- **Reproducibility support**: Enables verification and reproduction of analytical processes
- **Standards compliance**: Aligns with W3C PROV for interoperability
- **Data integrity**: Provenance travels with data regardless of distribution method
- **Quality assurance**: Provides audit trail for analytical procedures
- **RAP alignment**: Supports UK Government reproducibility initiatives

### Negative
- **File size overhead**: Embedded provenance increases output file sizes
- **Implementation complexity**: Format-specific embedding requires different handling per file type
- **Tool integration**: Tools must be modified to embed provenance in outputs
- **Performance impact**: Additional processing time for provenance generation and embedding

### Mitigation Strategies
- **Efficient encoding**: Use compact JSON-LD serialization to minimize size overhead
- **Optional embedding**: Allow users to disable provenance for performance-critical applications
- **Standardized libraries**: Provide common provenance embedding functions for different formats
- **Incremental implementation**: Phase in provenance support across file formats over time

## Implementation Notes
- Provenance schema will be defined as JSON-LD context compatible with W3C PROV
- Tool execution framework will automatically capture standard provenance elements
- Format-specific embedding libraries will be developed for common output types
- Provenance validation tools will ensure PROV compliance
- Documentation will provide examples of provenance usage for reproducibility scenarios