## ADR 009: Sentry for Telemetry

## Context
We need to select a telemetry solution for NeuroLingo to monitor performance, detect errors, and analyze user interactions across both the frontend and back-end. The chosen solution must support real-time error tracking, provide detailed performance insights, integrate well with our existing stack, and scale with future growth. It should also be easy to set up and maintain.

### Options
Sentry provides error tracking and performance monitoring, helping us identify crashes and performance bottlenecks. It offers detailed stack traces, user context, and release management. Additionally, Sentry has introduced basic session replay capabilities, though it is relatively limited.

LogRocket specializes in session replay, recording detailed user sessions, including UI interactions, network requests, and console logs. This allows us to play back user sessions to understand exactly what happened in complete detail. However, LogRocket does not have the full performance monitoring capabilities of Sentry and is primarily focused on the frontend.

OpenTelemetry offers an open-source framework for telemetry, including traces, metrics, and logs. It provides flexibility and control but requires significant setup and configuration. It is a more complex solution, better suited for larger, more customized observability needs.

## Decision

We will use Sentry as our primary tool for both frontend and back-end telemetry. Sentry provides a comprehensive error tracking solution and performance monitoring that fits our needs. It also includes basic session replay functionality, which will allow us to replay user sessions for debugging issues.

Sentry's simplicity, out-of-the-box functionality, and ability to integrate with our existing stack make it the ideal choice for our current needs. If more detailed session replay becomes necessary in the future, we can reconsider integrating LogRocket for that specific functionality on the frontend. We can also consider the integration of usability monitoring platforms like HotJar, which enable broader understanding of how our users interact with our application.

## Status

Accepted

## Consequences

Using **Sentry** as our telemetry tool will give us immediate access to real-time error tracking and performance monitoring, which will significantly enhance our ability to identify and resolve issues quickly. By tracking crashes and bottlenecks, we will be able to optimize the user experience and ensure that problems are addressed proactively. Additionally, Sentry’s session replay feature, though not as advanced as LogRocket’s, will allow us to replay user sessions to debug specific issues and better understand user interactions with the application.

However, the session replay functionality in Sentry is limited compared to LogRocket. This may become a constraint if we need more detailed session data for complex user behavior or interactions. While Sentry offers a good balance of error tracking and performance monitoring, it may not be as specialized for in-depth session analysis, which could affect how thoroughly we can diagnose certain user-related issues.

There may also be some performance overhead associated with integrating Sentry, as we will be logging and tracking telemetry data in real time. This could impact application performance if not optimized properly, especially in cases of high traffic or resource-intensive operations. We will need to ensure that the telemetry data collection is efficient and doesn’t hinder the user experience.

By opting for Sentry, we are choosing a tool that simplifies integration and setup, making it easy to get started without significant overhead. However, this decision means we are not leveraging the flexibility that OpenTelemetry offers for highly customized telemetry solutions. By sticking to Sentry, we do not have granular control over the data we collect.

Lastly, as we are implementing a platform with session replay capabilities, it will be crucial to maintain compliance with data privacy regulations. Session replay can potentially capture sensitive user data, so we will need to ensure that proper safeguards are in place to protect user privacy and meet any necessary governance stasndards (e.g. blurring information on sign-up).
