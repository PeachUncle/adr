---
status: proposed
date: 2024-12-10
decision-makers: Michael Ogunrinde, James Bateman, Cory-Newman 
---

# Authentication and Authorisation Mechanisms for AML System

## Context and Problem Statement

The AML system requires a secure and user-friendly authentication and authorisation system to manage different types of users (members, staff, administrators, accountants, purchase managers) with varying access levels. The system must handle separate authentication flows for regular users and staff members, manage sessions securely, and implement role-based access control while maintaining security best practices.

## Decision Drivers

* Must support separate authentication flows for regular users and staff members
* Need to protect sensitive user and payment data through proper access control
* Must integrate seamlessly with the existing membership management system
* Must implement role-based access control for different staff roles (admin, accountant, purchase manager)
* Must maintain secure session management with appropriate timeouts
* Must handle JWT tokens securely for API authentication
* Should provide a clear separation between member and staff access

## Considered Options

* Custom authentication implementation
* NextAuth.js implementation
* Auth0 or similar third-party authentication service
* Passport.js with custom providers
* Firebase Authentication

## Decision Outcome

Chosen option: "NextAuth.js implementation", because:

1. Provides built-in security features while allowing customisation
2. Natural integration with our Next.js framework
3. Can be implemented with multiple credential providers to separate member and staff authentication
4. Supports JWT-based sessions out of the box
5. No additional cost for our expected user base
6. Active community and regular updates
7. Provides debug mode for development and troubleshooting

### Planned Implementation Details

1. Authentication flows:
    * Seperate credential providers for members and staff
    * Custom login pages for different user types
    * JWT-based session management

2. Role-based Access control:
   * Member: Basic access rights
   * Staff: Extended access rights
   * Admin: Full system access
   * Additional roles: Accountant, Purchase Manager

3. Security measures:
   * Session timouts
   * Secure token handling
   * Environment-based secrets
   * HTTPS enforcement

### Consequences

* Good, because it reduces development time with pre-built security features
* Good, because it provides flexibility for future authentication methods
* Good, because it integrates naturally with our Next.js stack
* Bad, because it adds a framework dependency
* Bad, because complex custom requirements might need workarounds

### Confirmation

The decision will be validated through:

1. Testing of both user and staff authentication flows.
2. Verification of role-based access control
3. Session timeout testing
4. Security audit of JWT handling
5. Performance testing under load

## Pros and Cons of the Options

### NextAuth.js Implementation

* Good, because of native Next.js integration
* Good, because of built-in security features
* Good, because it's free and open-source
* Bad, because it might limit some custom authentication flows
* Bad, because we're dependent on the framework's development

### Custom authentication implementation

* Good, because of complete control over implementation
* Good, because no external dependencies
* Bad, because requires significant development time
* Bad, because higher risk of security vulnerabilities
* Bad, because requires ongoing maintenance

### Auth0 Integration

* Good, because of enterprise-grade security
* Good, because of comprehensive feature set
* Bad, because of potential cost scaling issues
* Bad, because of vendor lock-in
* Bad, because might be overly complex for our needs

### Firebase Authentication

* Good, because of easy implementation
* Good, because of Google infrastructure
* Bad, because of potential vendor lock-in
* Bad, because of potential cost scaling
* Bad, because less control over authentication flow

### Passport.js with Custom Strategy

* Good, because of flexibility
* Good, because of mature ecosystem
* Bad, because requires more setup time
* Bad, because requires more maintenance
* Bad, because less integrated with Next.js

## More Information

Implementation requirements:

To implement this decision, we will need:

1. Development team training on NextAuth.js
2. Security review of planned implementation
3. Documentation of role-based access control requirements
4. Integration plan with backend services
5. Testing strategy for authentication flows
