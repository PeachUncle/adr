# ADR 002: Logging Strategy for MCP Quotes Server

## Status
Accepted

## Context
For Step 2 (Serper.dev Integration & Quote Retrieval Logic), we need to implement logging for API requests, responses, and error handling. Since this is an MCP server that communicates via stdio (standard input/output), we cannot use console logging as it would interfere with the MCP communication protocol. We need a file-based logging solution that provides structured logging capabilities.

## Decision
We will use **Winston** as our logging framework with the following configuration:

1. **File-Only Transports**: No console output to avoid interfering with MCP stdio communication
2. **Multiple Log Files**: 
   - `combined.log` for general application logs (info level and above)
   - `errors.log` for error-level logs only
3. **Log Levels**: Use standard Winston log levels (error, warn, info, debug)
4. **Structured Format**: JSON format for easy parsing and analysis
5. **Sensitive Data Protection**: Never log API keys or other sensitive information

## Rationale
- **MCP Compatibility**: File-only logging ensures no interference with stdio communication
- **Debugging Capability**: Structured logs help with troubleshooting API integration issues
- **Security**: Explicit exclusion of sensitive data from logs
- **Performance**: Minimal impact on application performance
- **Industry Standard**: Winston is the most widely adopted logging library for Node.js

## Implementation Configuration
```typescript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'errors.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

## Consequences
- **Positive**: 
  - Clean separation between application logs and MCP communication
  - Structured logging for better debugging
  - Configurable log levels for different environments
  - Security-focused approach to sensitive data
- **Negative**: 
  - Additional dependency and configuration complexity
  - Log files need to be managed (rotation, cleanup)
  - No real-time console visibility during development (by design)

## Log File Management
- Log files will be created in the project root directory
- Consider implementing log rotation for production deployments
- Add log files to `.gitignore` to prevent sensitive information leakage