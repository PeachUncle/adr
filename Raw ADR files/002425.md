# ADR-0002: Dynamic and State-Managed TaigaClient Instantiation

- **Status:** Accepted
- **Date:** 2025-11-02

## Context and Problem Statement

The initial architecture (see `architecture.md` prior to this ADR) proposed instantiating a single, stateless `TaigaClient` at application startup and injecting it into Tauri's managed state. This approach is simple and efficient.

However, the product design (`doc-desing.md`) requires that the user can specify the Taiga API endpoint URL at the time of login. This conflicts with the startup-instantiation model, as the URL is not known when the application first launches. Relying on a pre-configured environment variable would violate this requirement and make the application less flexible for users with self-hosted Taiga instances.

## Architectural Drivers

- **Flexibility:** The user must be able to change the API endpoint from the UI.
- **Robustness:** The application should not crash or fail if a configuration value is missing at startup.
- **Logical State:** The `TaigaClient` is only needed after a user attempts to authenticate. It is more logical for it to exist only after this point.

## Considered Options

1.  **Instantiate Client at Startup (Original Plan):** Create the client at startup with a default URL and replace it later. This is complex to manage in Tauri's state and could lead to race conditions or inconsistent state.
2.  **Create a New Client for Every API Call:** This is inefficient, as it would not reuse the underlying HTTP client and would require passing the URL and token for every single operation.
3.  **Dynamic Instantiation and State Management on Login:** Create the client only when the user logs in and then place it into managed state for other commands to use.

## Decision

We will proceed with **Option 3**. The `TaigaClient` will no longer be created at application startup.

The `login` Tauri command will now be responsible for:

1.  Accepting the `api_url` as an argument from the frontend.
2.  Creating a `TaigaClient` instance with the provided URL.
3.  Using the client to authenticate with the Taiga API.
4.  Upon successful authentication, placing the now-authenticated client instance into Tauri's managed state using `app_handle.manage()`.

Subsequent commands that need to communicate with the API will retrieve the client from the managed state via the `tauri::State` guard. If a command is called before a client is in the state (i.e., before login), Tauri will correctly return an error, which we can handle on the frontend.

## Consequences

### Positive

- The application now fully supports the user-configurable API URL requirement.
- The startup process is more robust and does not depend on environment variables.
- The application state is more logical: the client only exists after authentication is attempted.

### Negative

- The `login` command has a slight increase in responsibility.
- The frontend must be prepared to handle errors from commands that are called before the client is available in the state.
