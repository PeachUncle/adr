# ADR: 003 - Authentication Method for ProjectOneMil

## Context
The `ProjectOneMil` project requires a secure authentication method to manage user access and permissions. The project is built using .NET 8.0 and integrates with Entity Framework Core and PostgreSQL. Additionally, the project includes a system for sending confirmation emails to users upon registration. The team needs to decide on the authentication method and email confirmation system to be used.

## Decision
We have decided to use ASP.NET Core Identity for authentication and an SMTP-based email sender for sending confirmation emails in the `ProjectOneMil` project.

## Alternatives Considered
1. **JWT (JSON Web Tokens)**:
   - Pros:
     - Stateless and scalable.
     - Can be used across different platforms.
   - Cons:
     - Requires additional setup and configuration.
     - Token management can be complex.

2. **OAuth2/OpenID Connect**:
   - Pros:
     - Industry-standard protocol for authorization.
     - Supports single sign-on (SSO).
   - Cons:
     - More complex to implement.
     - Requires third-party identity providers.

## Rationale
ASP.NET Core Identity and SMTP-based email sender were chosen for the following reasons:
- **Integration**: Seamless integration with ASP.NET Core and Entity Framework Core.
- **Features**: Provides built-in features for user management, password hashing, and role-based authorization.
- **Security**: Offers robust security features, including password policies, account lockout, and two-factor authentication.
- **Email Confirmation**: The SMTP-based email sender allows for sending confirmation emails to users, enhancing security and user verification.
- **Simplicity**: Simplifies the implementation of authentication, authorization, and email confirmation in the project.

## Consequences
- **Positive**:
  - Simplified user management and authentication process.
  - Robust security features out of the box.
  - Easy integration with the existing .NET backend and PostgreSQL database.
  - Enhanced user verification through email confirmation.
- **Negative**:
  - Limited flexibility compared to custom JWT implementation.
  - Potential learning curve for team members unfamiliar with ASP.NET Core Identity and SMTP configuration.

## Implementation
The following steps will be taken to implement ASP.NET Core Identity and SMTP-based email sender in the `ProjectOneMil` project:
1. **Install Packages**: Ensure the `Microsoft.AspNetCore.Identity.EntityFrameworkCore` package is included in the project.
2. **Configure Services**: Configure Identity services in the `Startup.cs` or `Program.cs` file.
3. **Create Identity Models**: Define user and role models by extending `IdentityUser` and `IdentityRole`.
4. **Set Up Database**: Configure Entity Framework Core to use PostgreSQL for storing identity data.
5. **Implement Authentication**: Set up authentication and authorization middleware in the ASP.NET Core pipeline.
6. **Configure Email Sender**: Implement the `IEmailSender` interface using `SmtpEmailSender` class.
7. **Send Confirmation Emails**: Use the `SmtpEmailSender` to send confirmation emails upon user registration.
8. **Create User Interfaces**: Develop user interfaces for registration, login, and email confirmation.

## References
- [ASP.NET Core Identity Documentation](https://docs.microsoft.com/en-us/aspnet/core/security/authentication/identity)
- [Entity Framework Core Documentation](https://docs.microsoft.com/en-us/ef/core/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [jQuery Documentation](https://api.jquery.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
- [jQuery DataTables Documentation](https://datatables.net/)
- [JavaScript MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [SMTP Client Documentation](https://docs.microsoft.com/en-us/dotnet/api/system.net.mail.smtpclient)
