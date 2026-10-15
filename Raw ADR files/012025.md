# ADR-003: Data Validation with Class-Transformer and Class-Validator

## Context

In our microservice architecture we need to validate input data across multiple contexts:

1. **HTTP REST APIs**: Validate request bodies, query parameters, and path parameters
2. **gRPC Services**: Validate protobuf messages transformed to DTOs
3. **Kafka Message Consumers**: Validate asynchronous message payloads with DLQ handling

The challenges include:

- **Consistency**: Same validation rules across all contexts
- **Type Safety**: Leverage TypeScript for compile-time validation
- **Error Handling**: Consistent and descriptive error responses
- **Dead Letter Queue**: Handle invalid Kafka messages without data loss
- **Performance**: Efficient validation without significant overhead
- **Hybrid Applications**: NestJS hybrid apps (HTTP + gRPC + Kafka) require careful handling of global providers

## Decision

We adopt **class-transformer** and **class-validator** as our universal validation solution with specific implementations for each context.

> **⚠️ Critical for Hybrid Applications**: Global pipes, filters, and interceptors (`APP_PIPE`, `APP_FILTER`, `APP_INTERCEPTOR`) **MUST NOT be used** in NestJS hybrid applications that combine HTTP, gRPC, and microservices. They don't work reliably across all transport types. See comments in `src/main.ts` for detailed explanation.

### 1. Core Validation Infrastructure

```typescript
// Base DTO with common validation patterns
export abstract class BaseDto {
  @IsUUID(4)
  @IsNotEmpty()
  id: string;

  @IsDateString()
  @IsOptional()
  createdAt?: string;
}
```

### 2. HTTP Context Implementation

> **⚠️ Hybrid applications**: DO NOT use global APP_PIPE as a provider in modules or in `main.ts` with app.useGlobalPipes() function.
>
> **✅ Recommended**: Use `@UsePipes` at controller or method level for HTTP validation.

```typescript
// Controller level validation & serialization + error handling
@Controller("orders")
@UsePipes(HTTPValidationPipe)
@UseInterceptors(ClassSerializerInterceptor, HTTPInterceptor)
@UseFilters(
    InternalExceptionFilter,
    DomainExceptionFilter,
    RPCExceptionFilter,
    AxiosExceptionFilter,
    HTTPExceptionFilter
)
export class OrdersHTTPController {
    @Post()
    createOrder(@Body() dto: CreateOrderCommand): Observable<OrderDTO> {
        return this.ordersService.createOrder(dto);
    }

    @Patch(":id/confirm")
    confirmOrder(@Param("id", ParseUUIDPipe) id: string): Observable<void> {
        return this.ordersService.reserveOrder(id);
    }
}
```

### 3. gRPC Context Implementation

> **⚠️ Hybrid applications**: DO NOT use global APP_PIPE as a provider in modules or in `main.ts` with app.useGlobalPipes() function.
>
> **✅ Recommended**: Use custom decorators with `@UsePipes` for gRPC method-level validation.

```typescript
// Controller level serialization + error handling
@Controller("orders")
@UseInterceptors(ClassSerializerInterceptor, gRPCInterceptor)
@UseFilters(
    InternalExceptionFilter,
    DomainExceptionFilter,
    RPCExceptionFilter,
    AxiosExceptionFilter,
    HTTPExceptionFilter
)
export class OrdersgRPCController {
    private readonly logger = new Logger(OrdersgRPCController.name);
    constructor(
        private ordersService: OrdersAppService,
        @Inject("KAFKA_CLIENT") private readonly client: ClientKafka
    ) {}

    // Method-level validation using custom decorator
    @GrpcMethod("OrdersController", "GetOrder")
    @ValidateGrpc(GetOrderCommand)
    getOrder(
        data: GetOrderCommand,
        metadata: Metadata,
        call: ServerUnaryCall<any, any>
    ): Observable<OrderDTO> {
        const id = data.id;
        return this.ordersService.getOrder(id);
    }

    // Method-level validation using custom decorator
    @GrpcMethod("OrdersController", "CreateOrder")
    @ValidateGrpc(CreateOrderCommand)
    createOrder(
        data: CreateOrderCommand,
        metadata: Metadata,
        call: ServerUnaryCall<any, any>
    ): Observable<OrderDTO> {
        return this.ordersService.createOrder(data);
    }
}
```

**Why Method-Level Validation for gRPC:**

- gRPC methods receive protobuf-transformed data that needs specific validation
- Each method may have different command/query DTOs with different validation rules
- Global pipes and interceptors don't work reliably in hybrid NestJS applications
- The `@ValidateGrpc` decorator provides clean, method-specific validation

### 4. Kafka Consumer Implementation

> **⚠️ Important**: Kafka consumers should NEVER use global pipes or validation providers. For detailed Kafka validation and Dead Letter Queue implementation, see [ADR-006: Kafka Consumer Validation and DLQ](./adr-006-kafka-validation-dlq.md).

```typescript
// Kafka consumers use controller-level validation and manual error handling
@Controller("orders")
@UseFilters(KafkaExceptionFilter)  // See ADR-006 for detailed implementation
export class OrdersKafkaConsumer {
    @EventPattern('order.created')
    async handleOrderCreated(@Payload() data: OrderCreatedEventDto) {
        // Validation and DLQ handling - see ADR-006
        await this.orderService.processOrderCreated(data);
    }
}
```

### 5. DTO Composition with NestJS Mapped Types

> **✅ Recommended**: Use NestJS mapped types (`PartialType`, `PickType`, `OmitType`, `IntersectionType`) to compose DTOs from base classes while preserving all validation decorators.

For comprehensive guidance on DTO composition and validation inheritance, see [ADR-007: NestJS Mapped Types for DTO Composition and Validation Inheritance](./adr-007-nestjs-mapped-types.md).

**Quick Overview:**

```typescript
// Base DTO with comprehensive validation
export class CreateOrderDto {
  @IsUUID(4)
  @IsNotEmpty()
  customerId: string;

  @ValidateNested({ each: true })
  @Type(() => CreateOrderItemDto)
  @ArrayMinSize(1)
  @ArrayMaxSize(50)
  items: CreateOrderItemDto[];

  @IsEnum(OrderStatus)
  @IsOptional()
  status?: OrderStatus = OrderStatus.PENDING;
}

// ✅ PartialType: Makes all properties optional while preserving validators
export class UpdateOrderDto extends PartialType(CreateOrderDto) {
  // Automatically inherits all validation with optional properties
}

// ✅ PickType: Select specific properties with their validators
export class OrderStatusUpdateDto extends PickType(CreateOrderDto, ['status'] as const) {
  // Only includes status field with full validation
}

// ✅ OmitType: Exclude properties while keeping others
export class CreateOrderRequestDto extends OmitType(CreateOrderDto, ['id'] as const) {
  // Excludes auto-generated id field
}

// ✅ IntersectionType: Combine multiple DTOs
export class OrderWithMetadataDto extends IntersectionType(
  CreateOrderDto,
  class AuditFieldsDto {
    @IsUUID(4) createdBy: string;
    @IsDateString() createdAt: string;
  }
) {
  // Combines all validation from both sources
}
```

## Key Implementation Principles for Hybrid Applications

> **🔑 Critical Rules for NestJS Hybrid Apps (HTTP + gRPC + Kafka):**

1. **NO Global Providers**: Never use `APP_PIPE`, `APP_FILTER`, `APP_INTERCEPTOR` - they don't work reliably across transports
2. **Controller-Level Decoration**: Use `@UsePipes`, `@UseFilters`, `@UseInterceptors` at controller or method level
3. **Transport-Specific Validation**: Different pipes for HTTP vs gRPC contexts
4. **Manual Kafka Validation**: Use dedicated DLQ solution - see [ADR-006](./adr-006-kafka-validation-dlq.md)
5. **Method-Level gRPC**: Use `@ValidateGrpc` decorator for each gRPC method that needs validation
6. **Leverage Mapped Types**: Use NestJS mapped types to compose DTOs without duplicating validation rules - see [ADR-007](./adr-007-nestjs-mapped-types.md)

### 1. Custom Validators for Business Rules

```typescript
// Custom business rule validator
@ValidatorConstraint({ name: 'orderItemsValid', async: true })
export class OrderItemsValidConstraint implements ValidatorConstraintInterface {
  constructor(private readonly productService: ProductService) {}

  async validate(items: CreateOrderItemDto[]): Promise<boolean> {
    // Validate business rules (e.g., product exists, sufficient inventory)
    for (const item of items) {
      const product = await this.productService.findById(item.productId);
      if (!product || product.stock < item.quantity) {
        return false;
      }
    }
    return true;
  }

  defaultMessage(): string {
    return 'One or more order items are invalid';
  }
}

// Usage in DTO
export class CreateOrderDto {
  @Validate(OrderItemsValidConstraint)
  @ValidateNested({ each: true })
  @Type(() => CreateOrderItemDto)
  items: CreateOrderItemDto[];
}
```

### 2. Validation Groups for Context-Specific Rules

```typescript
// Validation groups for different contexts
export enum ValidationGroups {
  CREATE = 'create',
  UPDATE = 'update',
  PARTIAL = 'partial',
  STATUS_UPDATE = 'status_update',
  ADMIN = 'admin'
}

// DTO with validation groups
export class OrderDTO {
  @IsUUID(4)
  @IsNotEmpty({ groups: [ValidationGroups.CREATE, ValidationGroups.UPDATE] })
  id: string;

  @IsUUID(4)
  @IsNotEmpty({ groups: [ValidationGroups.CREATE] })
  @IsOptional({ groups: [ValidationGroups.UPDATE] })
  customerId: string;

  @IsEnum(OrderStatus)
  @IsOptional({ groups: [ValidationGroups.CREATE] })
  @IsNotEmpty({ groups: [ValidationGroups.STATUS_UPDATE] })
  status: OrderStatus;
}

// Custom validation pipe with groups
@Injectable()
export class GroupValidationPipe extends ValidationPipe {
  constructor(private readonly validationGroup: string) {
    super({
      groups: [validationGroup],
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true
    });
  }
}

// Usage in controllers
@Controller('orders')
export class OrdersController {
  @Post()
  @UsePipes(new GroupValidationPipe(ValidationGroups.CREATE))
  async createOrder(@Body() dto: CreateOrderRequestDto) {
    // DTO validated with CREATE group rules
  }

  @Patch(':id/status')
  @UsePipes(new GroupValidationPipe(ValidationGroups.STATUS_UPDATE))
  async updateStatus(@Body() dto: UpdateOrderStatusDto) {
    // DTO validated with STATUS_UPDATE group rules
  }
}
```

### 3. Error Transformation and Messaging

```typescript
// Custom validation pipe with enhanced error handling
@Injectable()
export class HTTPValidationPipe extends ValidationPipe {
  constructor() {
    super({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      exceptionFactory: (errors: ValidationError[]) => {
        const formattedErrors = this.formatValidationErrors(errors);
        return new BadRequestException({
          message: 'Validation failed',
          errors: formattedErrors,
          timestamp: new Date().toISOString()
        });
      }
    });
  }

  private formatValidationErrors(errors: ValidationError[]): any[] {
    return errors.map(error => ({
      property: error.property,
      value: error.value,
      constraints: error.constraints,
      children: error.children?.length ? this.formatValidationErrors(error.children) : undefined
    }));
  }
}
```

## Consequences

### Positive

- ✅ **Consistency**: Same validation rules across HTTP, gRPC, and Kafka contexts
- ✅ **Type Safety**: Complete TypeScript integration with declarative decorators
- ✅ **Reliability**: No dependency on unreliable global providers in hybrid apps
- ✅ **Error Handling**: Context-appropriate validation error responses
- ✅ **DRY Principle**: Mapped types eliminate validation rule duplication - see [ADR-007](./adr-007-nestjs-mapped-types.md)
- ✅ **Maintainability**: Clear inheritance relationships between DTOs
- ✅ **Performance**: Efficient validation with minimal overhead
- ✅ **Flexibility**: Easy composition and modification of validation rules

### Negative

- ❌ **Verbosity**: Must explicitly add validation to each controller/method
- ❌ **Learning Curve**: Developers must understand hybrid app limitations and mapped types
- ❌ **Runtime Validation**: Validation errors only detectable at runtime
- ❌ **Complex Inheritance**: Deep DTO inheritance chains can become hard to follow

### Risks Mitigated

- **Data Integrity**: Multi-layer validation prevents corrupted data processing
- **Code Duplication**: Mapped types eliminate repeated validation decorator definitions
- **Silent Failures**: Explicit validation prevents processing of invalid data
- **Maintenance Burden**: Changes to base DTOs automatically propagate to derived DTOs
- **Type Safety**: Compile-time checking prevents property selection errors

## Alternatives Considered

1. **Joi**: JavaScript-based, less TypeScript integration
2. **Yup**: Similar to Joi, less decorator support
3. **Zod**: More modern but less NestJS ecosystem
4. **Custom Validators**: More control but greater complexity

## References

- [Class-Validator Documentation](https://github.com/typestack/class-validator)
- [Class-Transformer Documentation](https://github.com/typestack/class-transformer)
- [NestJS Validation](https://docs.nestjs.com/techniques/validation)
- [ADR-006: Kafka Consumer Validation and DLQ](./adr-006-kafka-validation-dlq.md) - Kafka-specific validation
- [ADR-007: NestJS Mapped Types](./adr-007-nestjs-mapped-types.md) - DTO composition and validation inheritance
