# ADR-005: TypeORM for Database Infrastructure

## Context

Para implementar la persistencia de datos en nuestra arquitectura DDD, necesitamos una solución que permita:

1. **Mapeo Objeto-Relacional**: Traducir nuestros aggregates y entidades de dominio a estructuras de base de datos relacionales
2. **Separación de Capas**: Mantener el dominio independiente de la tecnología de persistencia específica
3. **Flexibilidad**: Permitir cambios en el esquema de base de datos sin afectar la lógica de dominio
4. **Migrations**: Gestión versionada de cambios en el esquema de base de datos
5. **Testing**: Capacidad de usar bases de datos en memoria para pruebas unitarias
6. **Type Safety**: Aprovechar TypeScript para validación de tipos en tiempo de compilación

## Decision

Adoptamos **TypeORM** como nuestra solución de persistencia con las siguientes implementaciones:

### 1. Repository Pattern Implementation

```typescript
// Domain interface (puerto)
export interface IOrderRepository {
  findById(id: OrderId): Promise<Order | null>;
  save(order: Order): Promise<void>;
  findByCustomerId(customerId: CustomerId): Promise<Order[]>;
}

// Infrastructure implementation (adaptador)
@Injectable()
export class TypeOrmOrderRepository implements IOrderRepository {
  constructor(
    @InjectRepository(OrderEntity)
    private readonly orderRepository: Repository<OrderEntity>,
    private readonly orderMapper: OrderMapper
  ) {}

  async findById(id: OrderId): Promise<Order | null> {
    const entity = await this.orderRepository.findOne({
      where: { id: id.value },
      relations: ['items']
    });
    return entity ? this.orderMapper.toDomain(entity) : null;
  }
}
```

### 2. Entity-Domain Mapping

```typescript
// Database Entity (Infrastructure)
@Entity('orders')
export class OrderEntity {
  @PrimaryColumn('uuid')
  id: string;

  @Column()
  customerId: string;

  @Column({ type: 'enum', enum: OrderStatus })
  status: OrderStatus;

  @OneToMany(() => OrderItemEntity, item => item.order, { cascade: true })
  items: OrderItemEntity[];

  @CreateDateColumn()
  createdAt: Date;
}

// Domain Aggregate (Domain)
export class Order {
  private constructor(
    private readonly _id: OrderId,
    private readonly _customerId: CustomerId,
    private _status: OrderStatus,
    private _items: OrderItem[]
  ) {}
}
```

### 3. Migrations Strategy

```typescript
// database/migrations/
export class CreateOrderTable1704326400000 implements MigrationInterface {
  name = 'CreateOrderTable1704326400000'

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.createTable(
      new Table({
        name: 'orders',
        columns: [
          { name: 'id', type: 'uuid', isPrimary: true },
          { name: 'customer_id', type: 'uuid', isNullable: false },
          { name: 'status', type: 'enum', enum: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'] },
          { name: 'created_at', type: 'timestamp', default: 'CURRENT_TIMESTAMP' }
        ]
      })
    );
  }
}
```

### 4. Configuration

```typescript
// Infrastructure configuration
@Module({
  imports: [
    TypeOrmModule.forRootAsync({
      useFactory: (config: ConfigService) => ({
        type: 'postgres',
        host: config.get('DB_HOST'),
        port: config.get('DB_PORT'),
        username: config.get('DB_USERNAME'),
        password: config.get('DB_PASSWORD'),
        database: config.get('DB_NAME'),
        entities: [OrderEntity, OrderItemEntity],
        migrations: ['database/migrations/*.ts'],
        synchronize: false, // Always use migrations in production
        logging: config.get('NODE_ENV') === 'development'
      }),
      inject: [ConfigService]
    }),
    TypeOrmModule.forFeature([OrderEntity, OrderItemEntity])
  ],
  providers: [
    {
      provide: 'IOrderRepository',
      useClass: TypeOrmOrderRepository
    }
  ]
})
export class OrdersPersistenceModule {}
```

## Consequences

### Positive

- ✅ **Type Safety**: TypeScript completo con validación en tiempo de compilación
- ✅ **Domain Independence**: El dominio no conoce TypeORM, solo interfaces
- ✅ **Migration Management**: Versionado automático de esquema de base de datos
- ✅ **Development Experience**: Decoradores declarativos y query builder intuitivo
- ✅ **Testing**: Soporte nativo para SQLite en memoria en tests
- ✅ **Performance**: Lazy loading, eager loading, y optimizaciones de consultas
- ✅ **Multiple Database Support**: PostgreSQL, MySQL, SQLite, etc.

### Negative

- ❌ **Learning Curve**: Los desarrolladores deben aprender TypeORM específicamente
- ❌ **Generated Queries**: Menos control sobre SQL generado en casos complejos
- ❌ **Migration Complexity**: Cambios complejos de esquema pueden requerir SQL manual
- ❌ **Memory Usage**: ORM overhead comparado con SQL puro

### Risks Mitigated

- **Vendor Lock-in**: Repository pattern permite cambiar ORM sin afectar dominio
- **Performance**: Query profiling y optimización disponibles
- **Data Integrity**: Migrations y validaciones en múltiples capas

## Implementation Guidelines

### 1. Naming Conventions

```typescript
// Database entities: suffix 'Entity'
OrderEntity, OrderItemEntity

// Domain models: sin suffix
Order, OrderItem

// Mappers: suffix 'Mapper'
OrderMapper, OrderItemMapper
```

### 2. Mapper Pattern

```typescript
@Injectable()
export class OrderMapper {
  toDomain(entity: OrderEntity): Order {
    return Order.reconstruct(
      OrderId.create(entity.id),
      CustomerId.create(entity.customerId),
      entity.status,
      entity.items.map(item => this.orderItemMapper.toDomain(item))
    );
  }

  toEntity(domain: Order): OrderEntity {
    const entity = new OrderEntity();
    entity.id = domain.id.value;
    entity.customerId = domain.customerId.value;
    entity.status = domain.status;
    entity.items = domain.items.map(item => this.orderItemMapper.toEntity(item));
    return entity;
  }
}
```

### 3. Transaction Management

```typescript
@Injectable()
export class OrderApplicationService {
  constructor(
    @Inject('IOrderRepository')
    private readonly orderRepository: IOrderRepository,
    private readonly dataSource: DataSource
  ) {}

  async createOrder(command: CreateOrderCommand): Promise<void> {
    await this.dataSource.transaction(async manager => {
      const order = Order.create(/*...*/);

      // Use transaction-aware repository
      const txRepository = manager.getCustomRepository(TypeOrmOrderRepository);
      await txRepository.save(order);

      // All operations in same transaction
      await this.eventPublisher.publishInTransaction(order.events, manager);
    });
  }
}
```

## Alternatives Considered

1. **Prisma**: Más moderno pero menos maduro, query builder diferente
2. **Raw SQL with Query Builder**: Más control pero mayor complejidad
3. **Sequelize**: Menos TypeScript native, más orientado a JavaScript
4. **MikroORM**: Similar a TypeORM pero menos ecosystem

## References

- [TypeORM Documentation](https://typeorm.io/)
- [Repository Pattern in DDD](https://martinfowler.com/eaaCatalog/repository.html)
- [ADR-001: DDD Architecture](./adr-001-ddd-architecture.md)
