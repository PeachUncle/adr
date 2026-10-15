# ADR-9 Server-rendered HTML user interface

## Context

A simple and robust way to present the application to the users is needed

## Decision

Implement a user interface as a set of server-rendered dynamic HTML
pages, generated from Clojure data through hiccup.

## Expected consequences

The server-side of the application gains a new responsibility for
defining the presentation of the data and functionality. Its scope
will therefore increase slightly, but there does not need to be a
separate front-end application. A single application is expected to be
simpler to maintain than two interrelated ones, especially in the case
where these two would be written in different languages and rely on
tools from different ecosystems.

Compared to the common SPA + REST backend architecture, it becomes
possible to even omit the REST API entirely, as well as the parts of
the application that would consume that API and produce JavaScript
data. While it will take some code to emit the user interface elements
and the endpoints that accept data in, this is expected to be smaller
in volume than the full REST API and the entire separate application.

It becomes feasible to implement an application that does not require
JavaScript to be enabled. The HTML for a single view is expected to be
small, so a full page load stays fast and light. These consequences
fit well with the aims to minimize the load the application places on
end-user devices and network.

## Candidate comparison

1. **Server-side rendering** (chosen)
   - **Pros**:
     - Enable writing the entire application with the back-end
       language -> convenient maintenance
     - Really light requirements on the client side
     - Useful content visible to the user with a small number of small
       HTTP transfers -> even a cold reload can be fast
     - An API with marshalling and validation needed mainly for
       actions that mutate application state
     - No front-end framework
       - No keeping up with a changing framework -> convenient
         maintenance
       - No need to transmit the framework to client -> support slow
         connectivity
     - Avoid all interaction with the node.js ecosystem
   - **Cons**:
     - Page reload on every navigation
     - Some interactions (e.g. a searchable `<select>`) are difficult
       to implement with pure server-side rendering
     - In 2025, not a very popular, and thus potentially unfamiliar,
       pattern to delivering the UI

2. **Server-side rendering with htmx and websocket**
   - **Pros**:
     - Enable writing *almost* the entire application with the
       back-end language -> convenient maintenance
     - Reasonably light requirements on the client side
     - Useful content visible to the user with a small number of small
       HTTP transfers -> even a cold reload can be fast
     - An API with marshalling and validation needed mainly for
       actions that mutate application state
     - Minimal front-end framework (the standalone htmx library)
     - Avoid all interaction with the node.js ecosystem
     - Incremental, dynamic updates to the UI from server
       code. Capabilities comparable to client-side code.
   - **Cons**:
     - Complexity and constrainsts of relying on the websocket
       communication
     - In 2025, not a very popular and thus potentially unfamiliar
       pattern to delivering the UI

3. **SPA with vanilla JS**
   - **Pros**:
     - Small download
     - Simple tooling
     - Few dependencies
   - **Cons**:
     - Must maintain a full API to application data, with
       marshalling and validation
     - Possibly some interaction with the node.js ecosystem
     - Lots of wheels to re-invent
     - Self-invented wheels might have some unaddressed
       quality-of-life wants

4. **SPA with Vite + Svelte**
   - **Pros**:
     - A typical and familiar approach
     - Good developer experience with hot reloads and other
       quality-of-life bits
   - **Cons**:
     - Must maintain a full API to application data, with
       marshalling and validation
     - Deep interaction with the node.js ecosystem -> more maintenance
       work
     - Complex build system -> more maintenance work
     - Large dependency tree -> more maintenance work
     - Bundle size (reasonable for Svelte, but still it's the heaviest
       of the options considered)
