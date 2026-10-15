# ADR 0001: Choice of gRPC for Communication Protocol

## Status

Accepted

## Date

2025-03-01

## Context

LlamaCalc requires a communication protocol for clients to interact with the calculation service. The protocol must be efficient, support multiple languages, and provide a clear contract between client and server. The following options were considered:

1. **REST over HTTP/JSON**: Traditional, widely-used approach
2. **GraphQL**: Schema-based query language 
3. **gRPC**: Modern, high-performance RPC framework
4. **SOAP**: Enterprise messaging protocol
5. **Custom TCP Protocol**: Custom-built binary protocol

## Decision Drivers

- Performance requirements
- Support for multiple programming languages
- Type safety and schema definition
- Streaming support
- Security considerations
- Developer experience

## Decision

We decided to use **gRPC** as the primary communication protocol for LlamaCalc.

## Rationale

gRPC provides several advantages that align with our requirements:

1. **Performance**: gRPC uses Protocol Buffers for binary serialization, resulting in smaller payloads and faster processing compared to text-based formats like JSON or XML.

2. **Language Support**: gRPC has official support for multiple languages including Go, Java, C++, Python, and more, making it easier for clients to interact with our service.

3. **Type Safety**: Protocol Buffers provide a strict typing system that helps catch errors at compile time rather than runtime.

4. **Service Definition**: The .proto files serve as a clear contract between client and server, making it easier to understand and evolve the API.

5. **Streaming Support**: gRPC supports bidirectional streaming, which can be useful for future extensions of the calculator service.

6. **HTTP/2**: gRPC uses HTTP/2, which provides features like multiplexing, header compression, and binary framing.

7. **Built-in Auth**: gRPC has built-in support for various authentication mechanisms.

Here's a performance comparison from our benchmarks (see [Performance Benchmarks](../performance.md)):

| Protocol  | Requests/sec (50 concurrent) | Avg. Latency |
|-----------|------------------------------|--------------|
| gRPC      | 94,362                       | 0.53ms       |
| REST/HTTP | 32,457                       | 1.52ms       |
| SOAP      | 12,853                       | 3.86ms       |
| GraphQL   | 28,963                       | 1.73ms       |

## Consequences

### Positive

- Higher throughput and lower latency
- Type-safe API definition
- Automatic client generation in multiple languages
- Simpler implementation of auth and interceptors
- Better support for streaming operations in the future

### Negative

- Less widespread adoption compared to REST
- Requires understanding of Protocol Buffers
- Limited browser support (requires gRPC-Web)
- More complex setup than REST
- Debugging can be more challenging (less human-readable)

## Alternatives Considered

### REST over HTTP/JSON

While REST is more widely used and easier to debug, it lacks the performance advantages and type safety of gRPC. For a calculation service where efficiency is important, REST was not optimal.

### GraphQL

GraphQL would provide more flexibility in queries, but LlamaCalc's API is relatively simple and does not require the querying flexibility that GraphQL provides. The performance overhead of GraphQL was not justified.

### SOAP

SOAP is too verbose and has significant performance overhead, making it unsuitable for a high-performance calculation service.

### Custom TCP Protocol

A custom protocol would offer maximum performance but would require significant development effort and would not have the ecosystem benefits of gRPC.

## Implementation Details

The implementation includes:

1. Protocol Buffers definition in `proto/calculator.proto`
2. gRPC server implementation in `cmd/server/main.go`
3. Client examples in multiple languages
4. Authentication integration with gRPC interceptors

## Related Documents

- [gRPC Official Documentation](https://grpc.io/docs/)
- [Protocol Buffers Language Guide](https://protobuf.dev/programming-guides/proto3/)
- [Performance Benchmarks](../performance.md) 