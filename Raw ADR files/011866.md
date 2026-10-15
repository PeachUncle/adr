# ADR-001: JWT-based Cross-Domain Authentication

## Status
Accepted

## Date
2025-04-26

## Context
Our Magento 2 ecosystem includes multiple domains/websites that need to provide a seamless user experience. Currently, customers must log in separately on each domain, causing friction in the user journey between our related stores.

We need a secure and efficient way for a customer logged into one domain to seamlessly authenticate on another domain without re-entering credentials, while maintaining security and proper session management.

## Decision Drivers
* Security of customer data and authentication process
* User experience across multiple domains
* Performance impact on the system
* Maintainability of the solution
* Compatibility with Magento's authentication system

## Considered Options
1. **Shared session storage (Redis)**: Configure all domains to use the same Redis instance for session storage.
2. **OAuth 2.0 with an external identity provider**: Implement a third-party SSO solution.
3. **Cross-domain cookies**: Attempt to share cookies across domains.
4. **JWT token-based authentication with direct redirect**: Generate and pass JWT tokens between domains for authentication.

## Decision
We will implement option 4: **JWT token-based authentication with direct redirect**.

Authentication flow:
1. User logs into Domain A
2. User clicks "Switch Store" link to go to Domain B
3. Domain A generates a JWT token containing minimal user information
4. User is redirected to Domain B with the token
5. Domain B validates the token and automatically logs in the user
6. Authentication details are logged for security tracking

## Technical Implementation Details

### JWT Token Structure
- Header: `{ "typ": "JWT", "alg": "HS256" }`
- Payload:
  ```json
  {
    "iss": "domain-a.com",           // Issuer
    "aud": "domain-b.com",           // Audience
    "iat": 1619395200,               // Issued at timestamp
    "exp": 1619395500,               // Expiration (5 minutes)
    "jti": "random-unique-id",       // JWT ID
    "sub": "customer_id",            // Subject (customer ID)
    "email": "customer@example.com", // Customer email
    "name": "Customer Name"          // Customer name
  }
  ```
- Signature: HMAC-SHA256 of header and payload using a shared secret key

### Security Considerations
- Short token expiration time (5 minutes)
- Encrypted JWT secret in Magento configuration
- Validation of token signature and claims on receiving domain
- HTTPS required for all communications
- Only basic customer information in token payload
- Display of Magento loader during redirection to prevent user from intercepting the process

## Consequences

### Advantages
- No shared session storage required
- Minimal information transmitted between domains
- Follows security best practices
- Token expiration limits the attack window
- Visual feedback during authentication process
- Integrates with Magento's native authentication system

### Disadvantages
- Requires identical JWT secret on all domains
- May require periodic secret rotation
- Token-based approach requires proper implementation to avoid security risks

### Risks and Mitigations
- **Risk**: JWT token interception
  **Mitigation**: HTTPS, short expiration time, display loader during redirect

- **Risk**: JWT secret compromise
  **Mitigation**: Encrypted storage, secret rotation capability

## Related Decisions
- Choice of controller-based implementation over formal Web API (simplicity and session access)
- Use of feature flag to easily disable functionality if issues arise
- Implementation as a dedicated module rather than core customization

## References
- [JWT.io](https://jwt.io/introduction) - Introduction to JSON Web Tokens
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) - Security best practices