# ADR-002: Use Azure Event Hubs for Message Ingestion

## Status
Accepted

## Context
The Payments Ingestion system needs to handle high-volume payment transaction data from multiple sources. Requirements include:
- Handle thousands of events per second
- Provide reliable message delivery
- Support multiple independent consumers
- Enable replay capability for failed processing
- Integrate easily with Azure Functions
- Scale elastically with load

Options considered: Azure Event Hubs, Azure Service Bus, Kafka on AKS, AWS Kinesis

## Decision
We will use **Azure Event Hubs** as our message streaming platform for payment transaction ingestion.

## Consequences

### Positive
- **High throughput**: Handles millions of events per second with partitioning
- **Native Azure integration**: Seamless integration with Azure Functions, Event Grid
- **Partition-based parallelism**: Multiple partitions enable parallel processing
- **Message retention**: Configurable retention (1-7 days) for replay scenarios
- **Consumer groups**: Multiple independent consumers can read the same stream
- **Auto-inflate**: Automatic scaling of throughput units for variable load
- **Managed service**: No infrastructure management, automatic updates
- **Cost-effective**: Pay for throughput units, cheaper than managing Kafka
- **Apache Kafka compatible**: Can use Kafka clients if needed

### Negative
- **Limited retention**: Maximum 7 days retention (vs unlimited in Kafka)
- **No topic compaction**: Cannot compact topics like Kafka
- **Partition limits**: 32 partitions per Event Hub in Standard tier
- **Azure-specific**: Vendor lock-in to Azure ecosystem
- **Message size limit**: 1 MB per message

## Alternatives Considered

### Azure Service Bus
**Pros**: Advanced messaging features (transactions, sessions), guaranteed FIFO
**Cons**: Lower throughput than Event Hubs, higher cost, more complex
**Reason rejected**: Event Hubs better suited for high-volume streaming

### Kafka on Azure Kubernetes Service (AKS)
**Pros**: Full Kafka features, unlimited retention, no vendor lock-in
**Cons**: Requires cluster management, higher operational overhead, more expensive
**Reason rejected**: Operational complexity not justified for our use case

### AWS Kinesis
**Pros**: Similar to Event Hubs, proven at scale
**Cons**: Requires AWS, team lacks AWS experience, migration cost
**Reason rejected**: Team familiarity with Azure, existing Azure infrastructure

## Implementation Details

### Configuration by Environment

| Feature | Dev | Staging | Production |
|---------|-----|---------|------------|
| SKU | Standard | Standard | Standard |
| Capacity (TUs) | 1 | 2 | 4 |
| Partitions | 2 | 4 | 8 |
| Retention | 1 day | 3 days | 7 days |
| Auto-inflate | Disabled | Enabled | Enabled |

### Consumer Groups
- `default`: Built-in consumer group
- `payments-processor`: Main processing function
- `analytics`: Analytics and reporting
- `monitoring`: Health checks and monitoring

### Security
- Managed Identity authentication
- SAS token-based authorization for legacy systems
- Network rules and firewall for production
- Encryption at rest and in transit

## Performance Targets

| Environment | Target Throughput | Latency (p95) |
|-------------|------------------|---------------|
| Development | 100 events/sec | < 5 sec |
| Staging | 1,000 events/sec | < 2 sec |
| Production | 10,000 events/sec | < 1 sec |

## References
- [Azure Event Hubs Documentation](https://docs.microsoft.com/azure/event-hubs/)
- [Event Hubs vs Service Bus](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messaging-overview#event-hubs)
- [Event Hubs Kafka Protocol Support](https://docs.microsoft.com/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview)

## Date
2025-12-04

## Author
Infrastructure Team

