# ADR-007: File Publisher for Local Simulator Testing

## Status
Accepted

## Context
The Payment Data Simulator needs to support local testing and development workflows. The initial implementation only supported publishing to Azure Event Hubs, which requires:
- Azure credentials and connection strings
- Network access to Azure services
- Cost implications for development/testing
- Complexity for local development setup

Developers need a way to:
- Test the simulator locally without Azure dependencies
- Generate sample transaction files for testing
- Validate transaction generation logic
- Debug and iterate quickly
- Share test data files with team members

## Decision
We will implement a **FilePublisher** that writes transactions to local files, supporting:
- **JSONL format** (one JSON object per line) - default, easy to process line-by-line
- **JSON array format** - alternative format for structured data
- **Append mode** - allows accumulating transactions across multiple runs
- **Async I/O** - non-blocking file operations using thread pool executor

The FilePublisher will be integrated into the existing publisher abstraction, allowing seamless switching between Event Hubs and file output via configuration.

## Consequences

### Positive
- **Local Development**: Developers can test without Azure setup
- **Cost Savings**: No Azure costs for local testing
- **Fast Iteration**: Quick feedback loop without network latency
- **Data Sharing**: Transaction files can be shared and version controlled
- **Debugging**: Easy to inspect and validate generated transactions
- **CI/CD Integration**: Can generate test data files in CI pipelines
- **Flexibility**: Multiple output formats support different use cases
- **No Dependencies**: Works without Azure SDK for file output

### Negative
- **File Management**: Need to manage output directories and file cleanup
- **Storage Limits**: Local disk space limitations vs cloud storage
- **No Real-time Processing**: Files must be processed separately vs Event Hubs streaming
- **Additional Code**: More code to maintain and test
- **Format Differences**: File format may differ from Event Hubs message format

## Alternatives Considered

### Stdout Publisher Only
**Pros**: Simplest implementation, works everywhere
**Cons**: Limited flexibility, harder to process programmatically, no file persistence
**Reason rejected**: Need persistent files for testing and data sharing

### Database Publisher
**Pros**: Structured storage, queryable
**Cons**: Requires database setup, more complex, slower for high volume
**Reason rejected**: Overkill for local testing, adds unnecessary dependencies

### Multiple File Formats (CSV, Avro, etc.)
**Pros**: More format options
**Cons**: Increased complexity, more code to maintain
**Reason rejected**: JSONL and JSON array provide sufficient flexibility

### Event Hubs Local Emulator
**Pros**: Matches production environment exactly
**Cons**: Additional setup complexity, still requires Azure tooling
**Reason rejected**: File publisher is simpler and sufficient for local testing

## Implementation Details

### Configuration
```yaml
simulator:
  output:
    destination: "file"
    file_path: "output/transactions.jsonl"
    format: "jsonl"  # or "json_array"
    append: false
    batch_size: 100
```

### File Formats
- **JSONL**: One transaction per line, easy to stream and process
- **JSON Array**: Structured array format, better for small datasets

### Integration
- Uses same BasePublisher interface as EventHubPublisher
- Seamless switching via configuration
- Supports same batching and metrics as other publishers

## References
- [Simulator User Guide](./SIMULATOR-USER-GUIDE.md)
- [README Simulator Test](./README_SIMULATOR_TEST.md)
- Source: `src/simulator/publishers/file.py`

