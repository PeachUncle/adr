# ADR-6 Standard output Logging with tools.logging and SLF4J

## Context

The application needs logging capabilities to support debugging,
monitoring, and compliance requirements. The project has strict
constraints on cost, simplicity, computational footprint, and data
protection (GDPR). The logging solution must work in both production
and local development environments without adding significant
complexity or resource overhead.

Key considerations:
- Minimal computational footprint to align with environmental goals
- Simple implementation that doesn't require complex setup
- GDPR compliance through careful handling of personal data
- Flexibility to potentially enhance logging in the future
- Compatibility with the deployment environment's logging capabilities

## Decision

Implement logging by using the org.clojure/tools.logging library,
using primarily human-readable, plain text format.

Route that and every other logging API used in the dependencies
through the SLF4J API with a simple stdio implementation.

## Expected Consequences

Use of org.clojure/tools.logging will make logging code familiar and
intuitive for Clojure developers.

Using stdio for logging significantly simplifies the application's
logging implementation while transferring the responsibility of log
management to the deployment environment.

The deployment environment will be responsible for providing storage
and rotation of logs according to operational needs. Most of the
common production deployment mechanisms are capable of this.

Being able to use a minimalistic logger implementation, the
application's computational footprint is reduced, as no file I/O or
log formatting operations are needed within the application itself.

The SLF4J abstraction layer provides flexibility for future
enhancements if needed.

By carefully controlling what information is logged (excluding PII and
sensitive data), this approach maintains GDPR compliance.

A potential downside is that the lack of structured logging might make
automated log analysis more challenging if such needs arise in the
future.

## Candidate comparison

1. **Stdio logging with tools.logging and SLF4J (chosen)**
   - **Pros**:
     - Minimal implementation complexity
     - No file I/O overhead in the application
     - Lowest computational footprint, apart possibly for `println`
     - Leverages infrastructure for log management
     - Flexible for future enhancements via SLF4J
     - Human-readable format for easy debugging
     - Works seamlessly in both development and production
   - **Cons**:
     - Less structured format may complicate automated analysis
     - Dependent on infrastructure for log retention and rotation

2. **Local file storage with non-structured logging**
   - **Pros**:
     - Simple implementation
     - Human-readable format
     - Full control over log files
   - **Cons**:
     - Application must handle file rotation and management
     - Adds file I/O overhead to the application
     - Still lacks structured format benefits

3. **Local file storage with structured logging**
   - **Pros**:
     - Machine-readable format enables future tooling
     - More flexible for analysis and monitoring
   - **Cons**:
     - Higher implementation complexity
     - Application handles file rotation and management
     - Adds file I/O and formatting overhead

4. **Cloud-based logging service**
   - **Pros**:
     - Centralized log collection and search
     - Built-in alerting and monitoring capabilities
   - **Cons**:
     - Additional cost that may exceed budget
     - Added complexity to the architecture
     - Dependency on external service

## Implementation Notes

1. Use tools.logging as the logging facade throughout the application
2. Ensure that tools.logging and everything else to delegate to slf4j
3. Configure the simplest possible SLF4J implementation that logs to stdio
4. Follow these logging guidelines:
   - Use appropriate log levels (ERROR, WARN, INFO, DEBUG)
   - Never log personally identifiable information
   - Never log sensitive data like passwords or authentication tokens
   - Include relevant context (request IDs, operation types) when available
   - Keep messages concise but informative
5. Ensure the production deployment environment is configured to:
   - Capture stdio logs
   - Implement appropriate log rotation
   - Maintain logs for a reasonable period (suggest 7 days)
   - Secure log files appropriately
