# 11. Selecting the Decision on when to Update Events

Date: 2024-05-08

## Status

Accepted

## Context

In a FastAPI application that persists events for external providers, there is a need to decide on the timing of updating events in the system. The options considered are:

1. At start up of the application
2. At receiving a GET request
3. With a Cron job

## Decision
After evaluating the options, the decision is to update events at the start up of the application.

## Pros and Cons

### At Start Up of the Application
#### Pros:
- **Simplicity**: Updating events at start up simplifies the process and ensures that the data is up-to-date from the beginning.
- **Efficiency**: It reduces the latency for users accessing the data as it is already updated when the application starts.
- **Consistency**: Ensures that the data is consistent and avoids potential discrepancies that may arise from delayed updates.

#### Cons:
- **Potential Delay**: If the update process is time-consuming, it may delay the application start-up time.
- **Resource Intensive**: Depending on the volume of data and the update process, it may consume resources during start-up.

### At Receiving a GET Request
#### Pros:
- **On-Demand Update**: Ensures that events are updated only when requested, reducing unnecessary updates.
- **Scalability**: Allows for scaling based on traffic and demand, updating events as needed.

#### Cons:
- **Latency**: May introduce latency for the first user requesting the data if it needs to be updated.
- **Complexity**: Handling updates on each GET request can introduce complexity and potential issues in managing the update process.

### With a Cron Job
#### Pros:
- **Scheduled Updates**: Allows for scheduled and periodic updates, ensuring data freshness.
- **Separation of Concerns**: Decouples the update process from user requests, improving performance.

#### Cons:
- **Delayed Updates**: Data may not be immediately up-to-date, depending on the frequency of the cron job.
- **Maintenance Overhead**: Requires additional configuration and maintenance of the cron job.

## Selected Decision
The decision to update events at the start-up of the application is chosen for its simplicity, efficiency, and consistency benefits. This approach ensures that the data is up-to-date from the beginning, simplifying the update process and providing a seamless experience for users accessing the events.
