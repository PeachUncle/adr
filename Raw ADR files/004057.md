# ADR-005: SOAP Adapter Implementation Approach

## Status

Accepted

## Context

SwiftTrack must integrate with a legacy Client Management System (CMS) that only supports SOAP/XML communication. The CMS requires client registration, order creation, and status updates via SOAP calls. We need a robust, maintainable approach to handle this integration.

## Decision

We will implement a **dedicated SOAP adapter service** using a combination of WSDL-based client generation and custom XML processing, with comprehensive error handling and monitoring.

## Rationale

### SOAP Integration Challenges

1. **Legacy Protocol**: SOAP is verbose and has different error handling patterns
2. **XML Complexity**: Manual XML marshalling/unmarshalling is error-prone
3. **Schema Evolution**: WSDL changes require adapter updates
4. **Error Mapping**: SOAP faults need translation to domain errors
5. **Performance**: XML processing overhead and network latency

### Implementation Strategy

Rather than trying to abstract SOAP into REST patterns, we'll:

- Embrace SOAP semantics while providing clean internal APIs
- Use code generation for type safety and consistency
- Implement comprehensive error handling and retry logic
- Provide detailed monitoring and observability

## Technical Implementation

### SOAP Client Generation

```typescript
// Using soap npm package for WSDL-based generation
import * as soap from 'soap';

interface CmsClientConfig {
  wsdlUrl: string;
  endpoint: string;
  timeout: number;
  credentials?: {
    username: string;
    password: string;
  };
}

class SoapClientFactory {
  async createClient(config: CmsClientConfig): Promise<soap.Client> {
    const client = await soap.createClientAsync(config.wsdlUrl);
    client.setEndpoint(config.endpoint);
    // Configure security, headers, etc.
    return client;
  }
}
```

### Message Transformation Layer

```typescript
// Domain object to SOAP message transformation
class CmsMessageTransformer {
  orderToSoapRequest(order: Order): CreateOrderRequest {
    return {
      OrderHeader: {
        OrderId: order.orderId.toString(),
        ClientId: order.userId.toString(),
        OrderDate: order.createdAt.toISOString(),
        Priority: order.priority ? 'HIGH' : 'NORMAL',
      },
      OrderDetails: {
        OrderType: order.orderType,
        Amount: order.amount.toString(),
        DeliveryAddress: order.address,
        SpecialInstructions: order.specialInstructions,
      },
    };
  }

  soapResponseToOrder(response: CreateOrderResponse): CmsOrderReference {
    return {
      cmsOrderId: response.OrderReference.OrderId,
      status: this.mapCmsStatus(response.OrderReference.Status),
      externalReference: response.OrderReference.ExternalRef,
    };
  }
}
```

### Error Handling Strategy

```typescript
// SOAP-specific error handling
class SoapErrorHandler {
  handleSoapFault(fault: any): CmsIntegrationError {
    const faultCode = fault.faultcode || fault.Code;
    const faultString = fault.faultstring || fault.Reason;

    switch (faultCode) {
      case 'CLIENT_NOT_FOUND':
        return new CmsClientNotFoundError(faultString);
      case 'INVALID_ORDER_DATA':
        return new CmsValidationError(faultString);
      case 'SYSTEM_UNAVAILABLE':
        return new CmsUnavailableError(faultString);
      default:
        return new CmsIntegrationError(faultString);
    }
  }

  isRetryableError(error: Error): boolean {
    return (
      error instanceof CmsUnavailableError ||
      error.message.includes('timeout') ||
      error.message.includes('connection')
    );
  }
}
```

### Circuit Breaker Integration

```typescript
import CircuitBreaker from 'opossum';

class CmsIntegrationService {
  private circuitBreaker: CircuitBreaker;

  constructor(
    private soapClient: any,
    private transformer: CmsMessageTransformer
  ) {
    this.circuitBreaker = new CircuitBreaker(this.callSoapService.bind(this), {
      timeout: 30000, // 30s timeout
      errorThresholdPercentage: 50,
      resetTimeout: 60000, // 1 minute
      volumeThreshold: 10, // Min calls before breaking
    });

    this.setupCircuitBreakerEvents();
  }

  async createOrder(order: Order): Promise<CmsOrderReference> {
    const soapRequest = this.transformer.orderToSoapRequest(order);
    const response = await this.circuitBreaker.fire(soapRequest);
    return this.transformer.soapResponseToOrder(response);
  }

  private async callSoapService(request: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.soapClient.CreateOrder(request, (err: any, result: any) => {
        if (err) {
          reject(this.errorHandler.handleSoapFault(err));
        } else {
          resolve(result);
        }
      });
    });
  }
}
```

### Configuration Management

```typescript
// Environment-specific SOAP configuration
interface SoapConfiguration {
  wsdl: {
    url: string;
    cacheTtl: number;
  };
  endpoint: {
    url: string;
    timeout: number;
  };
  security: {
    username?: string;
    password?: string;
    certificate?: string;
  };
  retry: {
    attempts: number;
    delay: number;
    backoffFactor: number;
  };
}

// Configuration by environment
const soapConfigs: Record<string, SoapConfiguration> = {
  development: {
    wsdl: { url: 'http://localhost:8080/cms/wsdl', cacheTtl: 300 },
    endpoint: { url: 'http://localhost:8080/cms/soap', timeout: 10000 },
    retry: { attempts: 3, delay: 1000, backoffFactor: 2 },
  },
  production: {
    wsdl: { url: 'https://cms.swiftlogistics.com/wsdl', cacheTtl: 3600 },
    endpoint: { url: 'https://cms.swiftlogistics.com/soap', timeout: 30000 },
    security: { username: process.env.CMS_USERNAME, password: process.env.CMS_PASSWORD },
    retry: { attempts: 5, delay: 2000, backoffFactor: 2 },
  },
};
```

### Mock Implementation for Testing

```typescript
// SOAP service mock for development and testing
class MockCmsService {
  async CreateOrder(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 100));

    // Generate mock response
    return {
      OrderReference: {
        OrderId: `CMS-${Date.now()}`,
        Status: 'CREATED',
        ExternalRef: request.OrderHeader.OrderId,
        CreatedDate: new Date().toISOString(),
      },
    };
  }

  async UpdateOrderStatus(request: UpdateOrderStatusRequest): Promise<UpdateOrderStatusResponse> {
    return {
      Success: true,
      OrderId: request.OrderId,
      NewStatus: request.Status,
      UpdatedDate: new Date().toISOString(),
    };
  }
}
```

### Monitoring and Observability

```typescript
// SOAP-specific metrics and logging
class SoapMetrics {
  private static metrics = {
    soapCallsTotal: new Counter({
      name: 'soap_calls_total',
      help: 'Total SOAP calls made',
      labelNames: ['operation', 'status'],
    }),
    soapCallDuration: new Histogram({
      name: 'soap_call_duration_seconds',
      help: 'SOAP call duration',
      labelNames: ['operation'],
    }),
    circuitBreakerState: new Gauge({
      name: 'circuit_breaker_state',
      help: 'Circuit breaker state (0=closed, 1=open, 2=half-open)',
      labelNames: ['service'],
    }),
  };

  static recordSoapCall(operation: string, duration: number, success: boolean) {
    this.metrics.soapCallsTotal.inc({
      operation,
      status: success ? 'success' : 'error',
    });
    this.metrics.soapCallDuration.observe({ operation }, duration);
  }
}
```

## Testing Strategy

### Unit Testing

```typescript
// Mock SOAP client for unit tests
describe('CmsIntegrationService', () => {
  let service: CmsIntegrationService;
  let mockSoapClient: any;

  beforeEach(() => {
    mockSoapClient = {
      CreateOrder: jest.fn(),
      UpdateOrderStatus: jest.fn(),
    };
    service = new CmsIntegrationService(mockSoapClient, transformer);
  });

  it('should create order successfully', async () => {
    const mockResponse = { OrderReference: { OrderId: 'CMS-123' } };
    mockSoapClient.CreateOrder.mockImplementation((req, cb) => cb(null, mockResponse));

    const result = await service.createOrder(testOrder);
    expect(result.cmsOrderId).toBe('CMS-123');
  });
});
```

### Integration Testing

```typescript
// Integration tests with actual SOAP service
describe('CMS Integration E2E', () => {
  let cmsService: CmsIntegrationService;

  beforeAll(async () => {
    // Connect to test CMS instance
    cmsService = await createCmsService(testConfig);
  });

  it('should handle full order lifecycle', async () => {
    const order = createTestOrder();

    // Create order
    const reference = await cmsService.createOrder(order);
    expect(reference.cmsOrderId).toBeDefined();

    // Update status
    await cmsService.updateOrderStatus(reference.cmsOrderId, 'IN_PROGRESS');

    // Verify status
    const status = await cmsService.getOrderStatus(reference.cmsOrderId);
    expect(status).toBe('IN_PROGRESS');
  });
});
```

## Consequences

### Positive

- **Type Safety**: WSDL-based generation provides compile-time safety
- **Maintainability**: Clear separation between SOAP and domain logic
- **Reliability**: Comprehensive error handling and circuit breaker protection
- **Testability**: Mock implementations enable thorough testing
- **Monitoring**: Detailed observability for troubleshooting

### Negative

- **Complexity**: Additional abstraction layer adds complexity
- **Performance**: XML processing and network overhead
- **Dependencies**: External SOAP service availability dependency
- **Versioning**: WSDL changes require adapter updates

### Operational Considerations

- **WSDL Caching**: Cache WSDL files to reduce startup time
- **Connection Pooling**: Reuse SOAP client connections
- **Monitoring**: Track SOAP call success rates and latencies
- **Alerting**: Alert on circuit breaker state changes
- **Documentation**: Maintain SOAP message format documentation

## Alternative Approaches Considered

### REST Proxy

- **Pros**: Could abstract SOAP as REST
- **Cons**: Loses SOAP semantics, complex error mapping

### Direct XML Processing

- **Pros**: Full control over XML generation
- **Cons**: Very error-prone, no type safety

### Message Queue Bridge

- **Pros**: Asynchronous processing
- **Cons**: Adds complexity, doesn't fit request-response pattern

## Migration Path

### Phase 1: Basic Integration

- Implement core SOAP operations (create, update, query)
- Basic error handling and logging
- Simple retry logic

### Phase 2: Enhanced Reliability

- Circuit breaker implementation
- Comprehensive monitoring
- Advanced error handling

### Phase 3: Performance Optimization

- Connection pooling
- Request/response caching
- Parallel processing where possible

## Review Date

This decision will be reviewed in 6 months or when CMS integration requirements change significantly.
