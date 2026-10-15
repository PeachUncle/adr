# ADR-003: Download Strategy and Resumable Downloads

## Status
Accepted

## Context
ETF documents can be large files (PDFs, Excel spreadsheets) and network interruptions are common. We need a robust download strategy that can handle failures gracefully and resume interrupted downloads to avoid wasting bandwidth and time.

## Decision
We will implement a comprehensive download strategy with the following features:

### Resumable Downloads
1. **HTTP Range Requests**: Use `Range` headers to resume partial downloads
2. **File Verification**: Calculate SHA256 checksums for integrity verification
3. **Progress Tracking**: Store download progress metadata for recovery
4. **Size Validation**: Compare downloaded size with expected content length

### Concurrency Control
1. **Async Downloads**: Use aiohttp for high-performance async downloads
2. **Semaphore Limiting**: Control concurrent downloads to respect server limits
3. **Fallback to Sync**: Use synchronous downloads for small batches

### Error Handling
1. **Exponential Backoff**: Retry failed downloads with increasing delays
2. **Multiple Strategies**: Fall back from HEAD to GET requests if needed
3. **Partial Cleanup**: Remove corrupted partial downloads
4. **Detailed Logging**: Track all download attempts and failures

### Storage Organisation
1. **Fund-based Structure**: Organise files by fund symbol
2. **Document Type Classification**: Categorise files (fact sheets, holdings, etc.)
3. **Metadata Tracking**: Store download records with timestamps and checksums
4. **Deduplication**: Avoid re-downloading existing files

## Implementation Details

### File Naming Convention
```
{FUND_SYMBOL}_{DOCUMENT_TYPE}.{extension}
```
Examples:
- `VTI_fact_sheet.pdf`
- `SPY_holdings.xlsx`
- `QQQ_performance.csv`

### Metadata Structure
```json
{
  "url": "https://...",
  "local_path": "/app/download/funds/VTI/VTI_fact_sheet.pdf",
  "file_size": 1048576,
  "download_date": "2024-01-15T10:30:00Z",
  "checksum": "sha256:...",
  "fund_symbol": "VTI",
  "document_type": "fact_sheet"
}
```

### Progress Tracking
```json
{
  "incomplete_downloads": [
    "/app/download/funds/VTI/partial_file.pdf"
  ],
  "last_run": "2024-01-15T10:30:00Z",
  "total_processed": 150
}
```

## Consequences

**Positive:**
- Reliable downloads that can survive network interruptions
- Efficient bandwidth usage through resumable downloads
- High performance through async concurrency
- Comprehensive error tracking and recovery
- Organised storage structure for easy navigation

**Negative:**
- Increased complexity compared to simple sequential downloads
- Additional storage overhead for metadata and progress tracking
- Need to handle edge cases like server-side file changes
- More complex testing requirements for resumable functionality

**Risks Mitigated:**
- Network interruptions causing complete re-downloads
- Server rate limiting from too many concurrent requests
- Storage space waste from duplicate downloads
- Data corruption from incomplete transfers

## Monitoring and Observability
- Download success/failure rates tracked in statistics
- Progress reporting through Rich CLI interface
- Detailed logging of all download attempts
- Storage usage reporting and cleanup utilities