# ADR 0002: Auth Configuration as Code (Pluggable OAuth2)

-   **Date**: 2025-06-12
-   **Author**: Tristan Muggridge

## Status

Accepted

## Context

Onigiri is being built to serve a wide range of users — from indie teams to enterprise orgs. A core goal is to make the application _plug-and-play_ with minimal friction.

Traditionally, apps integrate with a handful of hardcoded auth providers (e.g., “Login with Azure AD”), but that’s limiting. Instead, Onigiri should support **any OAuth2-compliant provider**, provided the correct configuration is supplied.

The idea is to implement a **declarative, YAML-based auth plugin system**, where the authentication flow is defined through configuration, not hardcoded logic.

## Decision

We will implement a generic OAuth2 client in code and delegate the provider-specific details to a configuration layer defined in YAML.

This configuration will include:

-   `client_id`
-   `client_secret`
-   Optional `scopes`
-   `auth_url`
-   `token_url`
-   `user_info_url` (for fetching user profile data post-auth)

To handle variation in user info responses (e.g., GitHub returns `login`, Discord returns `username`), we will also support **configurable transforms**. These will allow users to define how to extract fields like:

-   `id`
-   `username`
-   `email`
-   `full_name`

Each transform will be a named operation (e.g., `extract`, `concat`, `replace`, `mapField`) with parameters. These will be implemented in Go and registered centrally, so they can be reused and extended by contributors.

## Example

A YAML auth provider might look like:

```yaml
provider: discord
auth_url: https://discord.com/api/oauth2/authorize
token_url: https://discord.com/api/oauth2/token
user_info_url: https://discord.com/api/users/@me
client_id: ${DISCORD_CLIENT_ID}
client_secret: ${DISCORD_CLIENT_SECRET}
transforms:
    id:
        op: extract
        path: id
    username:
        op: concat
        args:
            - path: username
            - string: "#"
            - path: discriminator
```
