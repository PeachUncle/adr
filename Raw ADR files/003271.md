# ADR-007: Event-Driven Architecture

## Status
Accepted - December 2024

## Context
Microservices need to communicate asynchronously to maintain loose coupling and handle high-volume operations without blocking.

## Decision
Implement **Event-Driven Architecture** using:
- AWS SNS/SQS for message queuing
- EventBridge for event routing
- Event sourcing for critical workflows

## Event Schema

```typescript
// events/base.event.ts
export interface BaseEvent {
  id: string;
  type: string;
  timestamp: string;
  version: string;
  source: string;
  correlationId: string;
  causationId?: string;
  userId?: string;
  metadata: Record<string, any>;
}

// events/order.events.ts
export interface OrderCreatedEvent extends BaseEvent {
  type: 'order.created';
  data: {
    orderId: string;
    userId: string;
    items: OrderItem[];
    totalAmount: number;
    currency: string;
    shippingAddress: Address;
    paymentMethod: string;
  };
}

export interface OrderPaidEvent extends BaseEvent {
  type: 'order.paid';
  data: {
    orderId: string;
    paymentId: string;
    amount: number;
    currency: string;
    paymentMethod: string;
  };
}

export interface OrderShippedEvent extends BaseEvent {
  type: 'order.shipped';
  data: {
    orderId: string;
    trackingNumber: string;
    carrier: string;
    estimatedDelivery: string;
  };
}
```

## Event Bus Implementation

```typescript
// event-bus.service.ts
import {
  SNSClient,
  PublishCommand
} from '@aws-sdk/client-sns';
import {
  SQSClient,
  SendMessageCommand,
  ReceiveMessageCommand,
  DeleteMessageCommand
} from '@aws-sdk/client-sqs';

export class EventBus {
  private snsClient: SNSClient;
  private sqsClient: SQSClient;
  private topicArn: string;

  constructor() {
    this.snsClient = new SNSClient({ region: process.env.AWS_REGION });
    this.sqsClient = new SQSClient({ region: process.env.AWS_REGION });
    this.topicArn = process.env.SNS_TOPIC_ARN!;
  }

  async publish<T extends BaseEvent>(event: T): Promise<void> {
    const command = new PublishCommand({
      TopicArn: this.topicArn,
      Message: JSON.stringify(event),
      MessageAttributes: {
        eventType: {
          DataType: 'String',
          StringValue: event.type
        },
        correlationId: {
          DataType: 'String',
          StringValue: event.correlationId
        }
      }
    });

    await this.snsClient.send(command);

    logger.info('Event published', {
      eventId: event.id,
      eventType: event.type,
      correlationId: event.correlationId
    });
  }

  async subscribe<T extends BaseEvent>(
    queueUrl: string,
    handler: (event: T) => Promise<void>
  ): Promise<void> {
    while (true) {
      try {
        const command = new ReceiveMessageCommand({
          QueueUrl: queueUrl,
          MaxNumberOfMessages: 10,
          WaitTimeSeconds: 20,
          MessageAttributeNames: ['All']
        });

        const response = await this.sqsClient.send(command);

        if (response.Messages) {
          await Promise.all(
            response.Messages.map(async (message) => {
              try {
                const event = JSON.parse(message.Body!) as T;
                await handler(event);

                // Delete message after successful processing
                await this.sqsClient.send(
                  new DeleteMessageCommand({
                    QueueUrl: queueUrl,
                    ReceiptHandle: message.ReceiptHandle!
                  })
                );
              } catch (error) {
                logger.error('Event processing failed', {
                  messageId: message.MessageId,
                  error
                });
                // Message will be retried or sent to DLQ
              }
            })
          );
        }
      } catch (error) {
        logger.error('Error receiving messages', { error });
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }
}

// Usage in service
class OrderService {
  private eventBus: EventBus;

  async createOrder(orderData: CreateOrderDTO): Promise<Order> {
    const order = await this.repository.create(orderData);

    // Publish event
    await this.eventBus.publish<OrderCreatedEvent>({
      id: generateId(),
      type: 'order.created',
      timestamp: new Date().toISOString(),
      version: '1.0',
      source: 'order-service',
      correlationId: orderData.correlationId,
      userId: orderData.userId,
      metadata: {},
      data: {
        orderId: order.id,
        userId: order.userId,
        items: order.items,
        totalAmount: order.totalAmount,
        currency: order.currency,
        shippingAddress: order.shippingAddress,
        paymentMethod: order.paymentMethod
      }
    });

    return order;
  }
}

// Event handlers
class InventoryService {
  async handleOrderCreated(event: OrderCreatedEvent): Promise<void> {
    logger.info('Reserving inventory', {
      orderId: event.data.orderId,
      items: event.data.items
    });

    for (const item of event.data.items) {
      await this.reserveInventory(item.productId, item.quantity);
    }

    await this.eventBus.publish<InventoryReservedEvent>({
      id: generateId(),
      type: 'inventory.reserved',
      timestamp: new Date().toISOString(),
      version: '1.0',
      source: 'inventory-service',
      correlationId: event.correlationId,
      causationId: event.id,
      metadata: {},
      data: {
        orderId: event.data.orderId,
        items: event.data.items
      }
    });
  }
}
```

## Event Patterns & Best Practices

### 1. Event Naming Conventions
```typescript
// Pattern: {domain}.{entity}.{action}
'order.created'
'order.paid'
'order.shipped'
'inventory.reserved'
'inventory.depleted'
'payment.processed'
'payment.failed'
```

### 2. Idempotency
```typescript
class EventHandler {
  private processedEvents: Set<string>;

  async handleEvent(event: BaseEvent): Promise<void> {
    // Check if event already processed
    if (await this.isProcessed(event.id)) {
      logger.info('Event already processed', { eventId: event.id });
      return;
    }

    try {
      // Process event
      await this.processEvent(event);

      // Mark as processed
      await this.markProcessed(event.id);
    } catch (error) {
      logger.error('Event processing failed', { eventId: event.id, error });
      throw error;
    }
  }

  private async isProcessed(eventId: string): Promise<boolean> {
    return this.cache.get(`processed:${eventId}`) !== null;
  }

  private async markProcessed(eventId: string): Promise<void> {
    await this.cache.set(`processed:${eventId}`, true, 86400); // 24 hours
  }
}
```

### 3. Dead Letter Queues
```typescript
// SQS configuration with DLQ
const queueConfig = {
  QueueName: 'order-events-queue',
  Attributes: {
    MessageRetentionPeriod: '86400', // 1 day
    VisibilityTimeout: '300', // 5 minutes
    RedrivePolicy: JSON.stringify({
      deadLetterTargetArn: process.env.DLQ_ARN,
      maxReceiveCount: 3 // Retry 3 times before DLQ
    })
  }
};
```

### 4. Event Versioning
```typescript
interface OrderCreatedEventV2 extends BaseEvent {
  type: 'order.created';
  version: '2.0';
  data: {
    orderId: string;
    userId: string;
    items: OrderItem[];
    totalAmount: number;
    currency: string;
    shippingAddress: Address;
    paymentMethod: string;
    // New field in v2
    promotionCode?: string;
  };
}

// Version-aware handler
async handleOrderCreated(event: OrderCreatedEvent): Promise<void> {
  switch (event.version) {
    case '1.0':
      return this.handleV1(event as OrderCreatedEventV1);
    case '2.0':
      return this.handleV2(event as OrderCreatedEventV2);
    default:
      throw new Error(`Unsupported event version: ${event.version}`);
  }
}
```

## Consequences

### Positive
- Loose coupling between microservices
- Scalable asynchronous processing
- Built-in retry mechanisms with DLQ
- Event history for audit and replay
- Improved fault tolerance

### Negative
- Increased complexity in debugging distributed flows
- Eventual consistency challenges
- Need for idempotency handling
- Message ordering guarantees require careful design
- Additional infrastructure costs

## Implementation Checklist
- [x] Set up SNS topics for event publishing
- [x] Create SQS queues for event consumption
- [x] Configure Dead Letter Queues
- [x] Implement event schema versioning
- [x] Add idempotency handling
- [x] Set up monitoring for event processing
- [x] Document event flows and dependencies

## Related ADRs
- ADR-001: Microservices Architecture (planned)
- ADR-004: Multi-Layer Caching Strategy
- ADR-005: Comprehensive Observability Strategy
- ADR-006: Zero-Trust Security Architecture

## References
- [AWS SNS/SQS Best Practices](https://aws.amazon.com/sqs/faqs/)
- [Event-Driven Architecture Patterns](https://martinfowler.com/articles/201701-event-driven.html)
- [EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)

---

**Note**: This ADR contains the initial implementation. Additional sections on event sourcing, CQRS patterns, and saga orchestration may be added in future revisions.
