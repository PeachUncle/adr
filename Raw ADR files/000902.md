# 005: Structured Logging with Context

## Status

Accepted

## Date

2025-12-15

## Context

As the application grew to include API calls, caching, error handling, and user interactions, we needed observability into what the application was doing. Traditional print statements were insufficient for:

- Debugging production issues
- Understanding performance characteristics
- Tracking user behavior patterns
- Monitoring API usage and costs
- Identifying error patterns

Alternatives:
1. **Print statements** - Simple debugging
   - ❌ Not persistent
   - ❌ No structure
   - ❌ Can't filter by level
   - ❌ No context

2. **Python logging (basic)** - Standard library
   - ✅ Built-in, no dependencies
   - ⚠️ Requires configuration
   - ❌ No structure without custom formatter

3. **Structured logging** - Contextual logs
   - ✅ Machine-parseable
   - ✅ Rich context
   - ✅ Easy to filter/search
   - ✅ Integrates with monitoring

4. **Third-party services only** (e.g., Datadog)
   - ❌ Vendor lock-in
   - ❌ Costs money
   - ❌ Requires network

## Decision

Implement **structured logging** with contextual metadata using Python's logging module with a custom formatter.

Architecture:
```python
logger.info(
    "Recommendation generated",
    extra={
        "query": user_interest[:50],
        "model": "llama-3.1-8b-instant",
        "cached": False,
        "duration_ms": 234.5,
        "books_count": 5,
    }
)
```

Output format:
```
2025-12-15T10:30:45.123Z [INFO] Recommendation generated | query=hopeful solarpunk..., model=llama-3.1-8b-instant, cached=False, duration=234.5ms
```

Features:
- ISO 8601 timestamps (UTC)
- Structured context fields
- Exception tracing
- Configurable log levels
- File and console output
- Sentry integration for errors

Context tracked:
- **Query**: User interest (truncated)
- **Model**: LLM model used
- **Cached**: Cache hit/miss
- **Duration**: Request latency (ms)
- **Books Count**: Results returned
- **Errors**: Full exception traces

## Consequences

### Positive
- **Debugging**: Easy to trace request flow
- **Performance**: Track slow requests
- **Monitoring**: Can parse logs for metrics
- **Alerting**: Integration with error tracking (Sentry)
- **Audit trail**: Know what happened when
- **Analytics**: Usage patterns visible in logs
- **Cost tracking**: Monitor API call frequency

### Negative
- **Log volume**: More data to store
- **Performance overhead**: Minimal but measurable
- **Complexity**: Need to manage log files
- **Privacy**: Must be careful with PII (we truncate queries)

### Neutral
- Requires discipline to add logging consistently
- Log format must be maintained across changes

### Risks
- **Log explosion**: Heavy usage creates large log files
  - Mitigation: Log rotation, retention policies
- **PII leakage**: User queries might contain sensitive info
  - Mitigation: Truncate to 50-100 chars, no full text logging
- **Performance impact**: Logging adds overhead
  - Mitigation: Async logging, conditional debug logs

## Implementation Notes

Logger setup (`logger.py`):
```python
class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            # Extract extra fields
            "query": getattr(record, "query", None),
            "model": getattr(record, "model", None),
            ...
        }
        # Format as readable string
        return f"{log_data['timestamp']} [{log_data['level']}] {log_data['message']} | ..."
```

Integration points:
- `recommender.py`: Log recommendation requests, cache hits, API errors
- `google_books.py`: Log API calls and failures
- `app.py`: Log startup/shutdown

Sentry integration:
- Optional via environment variable `SENTRY_DSN`
- Automatic error reporting for ERROR+ level logs
- Stack traces, context, breadcrumbs
- Free tier sufficient for personal projects

Configuration:
```python
setup_logging(
    level="INFO",  # DEBUG, INFO, WARNING, ERROR
    sentry_dsn=os.getenv("SENTRY_DSN"),  # Optional
    enable_console=True,
    log_file="app.log",  # Optional
)
```

Privacy considerations:
- Truncate queries to 50-100 characters
- No logging of API keys or secrets
- No logging of full recommendation text (only metadata)

## References

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Structlog](https://www.structlog.org/) (inspiration)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [The Twelve-Factor App: Logs](https://12factor.net/logs)
