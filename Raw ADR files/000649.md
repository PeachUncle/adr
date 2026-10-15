# 3. Facade Patter Between API and Module 

## Status

Accepted

## Context

The single API layer needs to communicate with individual Modules. We don't want the API layer to be tightly coupled to the modules themselves and their behaviour. Therefore, we just expose a small simple API for each module.

## Decision

The module (contract) that defines a module (IModule) should look like this:

```csharp
/// <summary>
/// Represends a module in a modular monolith architecture.
/// </summary>
public interface IModule
{
    /// <summary>
    /// Sends a command to the module, and doesn't return any data.
    /// </summary>
    /// <param name="command">The command to be send to the module.</param>
    /// <param name="cancellationToken">Propogates notification that operations should be cancelled.</param>
    /// <returns>A <see cref="Task"/> that returns when the operation is complete.</returns>
    public abstract Task SendCommand(ICommand command, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sends a command to the module and expects a result.
    /// </summary>
    /// <typeparam name="TResult">The type of result expected from the command.</typeparam>
    /// <param name="command">The command to send to the module.</param>
    /// <param name="cancellationToken">Propogates notification that operations should be cancelled.</param>
    /// <returns>Data of type <typeparamref name="TResult"/> that was returned from the command.</returns>
    public abstract Task<TResult> SendCommand<TResult>(ICommand<TResult> command, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sends a query to the module and expects a result.
    /// </summary>
    /// <typeparam name="TResult">The type of result expected from the query.</typeparam>
    /// <param name="query">The query to be sent to the module.</param>
    /// <param name="cancellationToken">Propogates notification that operations should be cancelled.</param>
    /// <returns>Data of type <typeparamref name="TResult"/> that was returned from the query.</returns>
    public abstract Task<TResult> SendQuery<TResult>(IQuery<TResult> query, CancellationToken cancellationToken = default);

    /// <summary>
    /// Publishes a notification to the module 
    /// </summary>
    /// <param name="notification">The notification to be published to the module.</param>
    /// <param name="cancellationToken">Propogates notification that operations should be cancelled.</param>
    /// <returns>A <see cref="Task"/> that returns when the operation is complete.</returns>
    public abstract Task PublishNotification(INotification notification, CancellationToken cancellationToken = default);
}
```

The concretion of this abstraction (e.g., UsersModule) will send commands to the appropriate module. 

The result is that the modules behaviour is entirely encapsulated.

## Consequences

- API and modules are loosely coupled.
- API can *only* communicate with the module via the facade (the implementation of the IModule interface).