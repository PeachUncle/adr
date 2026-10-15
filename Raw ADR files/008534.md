# Decision to Log Client IP Address

## Status

**Proposed**

## Context

Logging the client IP address is a fundamental practice for enhancing observability, security, and troubleshooting capabilities in web applications. By capturing the IP address of each request, the application can:

1. **Enhance Security**: Identify suspicious or malicious activity, such as repeated failed login attempts or requests from blocked IP ranges.
2. **Support Troubleshooting**: Provide developers and support teams with valuable context for diagnosing issues or reproducing errors.
3. **Improve Analytics**: Enable geographic and network-level analysis of application usage patterns.

Client IP logging is particularly useful in environments where load balancers, proxies, or other intermediate layers are involved, as these may mask the originating client’s IP unless explicitly handled.

## Decision

The application will log the client IP address for every incoming HTTP request. This information will be included in log entries alongside other contextual data, such as Transaction IDs (TXIDs), to facilitate cross-referencing and deeper telemetry insights.

### Implementation Details

1. **IP Address Extraction**:
    - Extract the client IP address from the `X-Forwarded-For` header when the application is behind a load balancer or proxy.
    - Fall back to the remote address from the HTTP request if the `X-Forwarded-For` header is unavailable.

2. **Logging**:
    - Include the extracted IP address in the application’s structured log entries.
    - Example log format:
      ```json
      {
        "timestamp": "2024-12-17T12:34:56Z",
        "level": "INFO",
        "message": "Request received",
        "txid": "1.0",
        "client_ip": "192.168.1.1",
        "endpoint": "/customers"
      }
      ```

3. **Security Considerations**:
    - Mask or anonymize sensitive IP information (e.g., truncating to `192.168.1.0/24`) for logs used in non-production environments.
    - Ensure that IP address logging complies with data protection regulations (e.g., GDPR, CCPA).

4. **Documentation**:
    - Document the log format and the logic for extracting client IPs in the project’s README or developer guide.

## Consequences

### Benefits

- **Enhanced Observability**: Provides additional context for understanding application usage and diagnosing issues.
- **Improved Security**: Supports the detection and prevention of suspicious activities or abuse.
- **Valuable Analytics**: Enables insights into client locations and network characteristics.

### Drawbacks

- **Privacy Concerns**: Logging IP addresses may raise privacy concerns and require adherence to regulatory requirements.
- **Overhead**: Additional processing to extract and log IP addresses introduces minimal performance overhead.
- **Data Storage**: Logs with IP addresses may need to be retained securely and purged periodically to comply with data retention policies.

## Alternatives Considered

1. **Do Not Log Client IPs**:
    - Rejected because it limits the ability to diagnose issues or understand user behavior.

2. **Log Only in Debug Mode**:
    - Rejected because this approach provides limited value in production environments where issues are most critical to resolve.

## Implementation Plan

1. **Middleware**:
    - Implement middleware to extract the client IP address from incoming requests.

2. **Logging Integration**:
    - Update structured logging configurations to include the `client_ip` field.

3. **Testing**:
    - Validate IP extraction logic in environments with and without proxies.
    - Test log entries for consistency and compliance with privacy policies.

4. **Compliance Review**:
    - Ensure that the logging of IP addresses adheres to applicable data protection laws.

## Conclusion

Logging client IP addresses enhances the application’s observability, security, and analytical capabilities. By implementing this feature responsibly and with privacy considerations, the project benefits from improved troubleshooting and deeper insights into client behavior while maintaining compliance with regulatory requirements.
