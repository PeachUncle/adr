# 3. Use Unix pipes for communication with plugins

Date: 2024-01-28

## Status

Accepted

## Context

The rss-transform project is designed as a management component (`rss-pipeline`)
that calls plugins which perform Extract, Transform and Load operations. I
intend that inter-process communication be completely language agnostic and as
dumb as a bag of rocks, in order to make it as easy as possible to write
plugins for the tool.

## Decision

I decided to use JSON passed over Unix pipes for communication with plugins:

Alternatives considered: gRPC with `go-plugin`, run-time plugins with the
`plugin` package and shared libraries, Unix sockets, network sockets.

## Consequences

Advantages:

1. *Simplicity and ease of use*: As dumb as a bag of rocks. Other inter-process
   communication mechanisms can be called remotely, but would add unnecessary
   complexity for plugin writers.
2. *Language agnosticism*: Everything can accept JSON on stdin, and write
   JSON to stdout.
3. *Operating system agnosticism*: exec(), stdin and stdout are available at
   all good bookshops.
4. *Unix philosophy*: Composition of small programs that do one thing and do it
   well, and communicate via text streams.
5. *Horizontal scalability*: Due to the nature of the work, pipelines are
   completely independent.

Risks:

1. *Tooling*: The tooling for testing REST services is probably more robust.
2. *No remote calls*: Plugins must run in the same environment as the
   `rss-pipeline` component.
   * Mitigation 1: design a plugin that is a thin wrapper around a network call.
   * Mitigation 2: add a remote plugin mechanism in the future.
3. *Scalability and performance*: We will see some overhead due to starting and
   stopping processes. At the scale I'm working at (see ACR 0002), this doesn't
   concern me. However I may be underestimating the scale at which the tool
   will be used.
4. *Universality of JSON*: Somewhere out there is a library that generates JSON
   the `encoding/json` package can't consume.
5. *Broken plugins*: We'll need to pay special attention to defensive
   programming when interacting with external plugins.