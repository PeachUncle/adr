# 📋 ADR-007: Server Actions for API

## Status

Accepted

## Context

With the adoption of Next.js App Router, we needed to decide on an approach for handling data mutations and API calls in the Reportly application. The options included:

1. Traditional API Routes
2. Server Components with data fetching
3. Server Actions for form submissions and mutations
4. Client-side API calls with SWR or React Query

We needed an approach that would provide security, performance, and a good developer experience.

## Decision

We decided to use Next.js Server Actions as the primary mechanism for data mutations and API calls in the Reportly application.

## Rationale

Server Actions provide several advantages that align with our project requirements:

1. **Security**: Server-side execution prevents exposure of sensitive logic and credentials.
2. **Progressive Enhancement**: Works without JavaScript for better accessibility and resilience.
3. **Simplified Development**: No need to create separate API routes for each operation.
4. **Type Safety**: End-to-end type safety when used with TypeScript.
5. **Reduced Client-Server Code**: Eliminates the need for duplicate validation logic.
6. **Optimistic Updates**: Built-in support for optimistic UI updates.
7. **Form Handling**: Native integration with HTML forms.
8. **Caching Integration**: Works with Next.js cache system for efficient data handling.

## Consequences

### Positive

- Simplified architecture with fewer separate API routes
- Improved security with server-side execution
- Better developer experience with co-located action code
- Progressive enhancement for better accessibility
- Reduced client-side JavaScript

### Negative

- Newer feature with evolving best practices
- Limited to Next.js applications
- Potential for mixing concerns in component files
- Learning curve for developers used to separate API routes

## Implementation Details

1. **Action Organization**:
   - Group actions by feature area
   - Place in dedicated directories for better organization
   - Use consistent naming conventions

2. **Security Considerations**:
   - Include authentication checks in each action
   - Implement proper input validation
   - Use zod for schema validation

3. **Error Handling**:
   - Consistent error response format
   - Client-side error handling patterns
   - Logging for server-side errors

## Alternatives Considered

### Traditional API Routes

API Routes would provide more separation between client and server code but would require more boilerplate and duplicate validation logic.

### Client-side API Calls

Client-side API calls with SWR or React Query would provide more control over data fetching but with less security and progressive enhancement.

### tRPC

tRPC would provide excellent type safety and a unified API layer but would add complexity and another dependency to the project.

## References

- [Next.js Server Actions Documentation](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions)
- [Progressive Enhancement with Server Actions](https://nextjs.org/blog/next-13-4#server-actions-alpha)
- [Security Considerations for Server-side Code](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
- [Form Handling Best Practices](https://web.dev/learn/forms/)
