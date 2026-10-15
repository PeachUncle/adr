# Environment Configuration

## Status

Accepted

## Context

The Taskify MVP needs secure and manageable configuration for different environments, aligning with the established three-tier environment strategy (development → staging → production) from the development environment ADR. This includes API keys, database connections, and authentication secrets. Configuration should be secure, environment-specific, and easy to manage while integrating seamlessly with the established stack (SvelteKit, Cloudflare services) and development tools (Wrangler CLI, npm). Given the privacy and security requirements for handling child data, configuration management is critical for maintaining secure access to sensitive services and data.

## Decision

- Use Cloudflare KV for production and staging configuration storage (aligning with established stack decisions)
- Use environment variables for local development configuration (.env files) supporting the Node.js LTS development environment
- Set up .env files with .env.example templates for local development, integrating with npm package management
- Use Wrangler secrets for sensitive configuration in Cloudflare environments, leveraging the established Wrangler CLI development tool
- Implement configuration validation at application startup using TypeScript for type safety
- Use different configuration namespaces for each environment tier (development → staging → production)
- Document all configuration variables and their purposes for team collaboration
- Integrate configuration management with the established testing strategy (Vitest, Cucumber.js, Svelte Testing Library, MSW) for consistent test environments and API mocking
- Support configuration of database connections for Cloudflare D1 across all environment tiers (local SQLite for development, D1 for staging/production)

## Consequences

Configuration will be secure and environment-appropriate across all three tiers (development → staging → production), ensuring safe progression of code changes. Developers will have clear guidance on required configuration through .env.example templates, supporting consistent development environments. Sensitive data will be properly protected through Wrangler secrets management, maintaining security standards for child data handling. 

The TypeScript-based configuration validation will integrate with the established code quality tools (ESLint, Prettier) and provide compile-time safety. Initial setup requires understanding of Cloudflare KV and Wrangler secrets management, which aligns with the established development environment requirements. Configuration management will support the SvelteKit application stack and Cloudflare services integration, ensuring consistent behavior across all environments. The approach enables automated testing and deployment through CI/CD pipelines while maintaining security and environment isolation.

## Urls

- [Cloudflare KV Documentation](https://developers.cloudflare.com/kv/)
- [Wrangler Secrets Management](https://developers.cloudflare.com/workers/wrangler/commands/#secret)
- [Environment Variables Best Practices](https://12factor.net/config)
- [Cloudflare Workers Environment Variables](https://developers.cloudflare.com/workers/platform/environment-variables/)
- [Dotenv Documentation](https://github.com/motdotla/dotenv)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Environment Strategy Documentation](../docs/environment-strategy.md)
