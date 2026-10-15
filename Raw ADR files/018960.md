# Design Decision: Auto Migrations

- [`@timescaledb/typeorm`](../../packages/typeorm/README.md)

The TypeORM integration for TimescaleDB will automatically generate the necessary SQL for TimescaleDB. This means that the user will not have to worry about the TimescaleDB SQL at all, and just work with the TypeORM entities.

## Context

Our goal is to make this library as easy to integrate into TypeORM as possible. This means that we should make sure that the migrations are as easy to use as possible or non-existent from the user's perspective.

### Assumptions

1. Users are familiar with TypeORM's entity and decorator patterns but may not be familiar with TimescaleDB

2. Schema changes to hypertables happen infrequently after initial creation

3. Most users want a simple declarative way to work with TimescaleDB features

4. Migration automation is more valuable than having fine-grained control over TimescaleDB SQL

5. Users prefer working with TypeScript classes and decorators over writing raw SQL

6. When schema changes are needed, users can handle them manually using the builder API

## Decision

**The Timescale SQL is hidden from the user.** You won't see generated Timescale SQL in the migrations. Instead, it will be generated and pushed on the fly. For example:

```typescript
@Entity('page_loads')
@Hypertable({
  by_range: { column_name: 'time' },
  compression: {
    compress: true,
    compress_orderby: 'time',
  },
})
export class PageLoad {
  @PrimaryColumn({ type: 'timestamp' })
  time!: Date;
}
```

The above entity will automatically generate and execute the necessary TimescaleDB SQL during migrations:

```sql
SELECT create_hypertable('page_loads', by_range('time'));
ALTER TABLE "page_loads" SET (timescaledb.compress, timescaledb.compress_orderby = "time");
```

## Limitations

### Versioning

Schema changes are not versioned. This means that if you change the schema, you will have to manually update the database. This is a limitation of the TypeORM integration, but can be worked around using the builder manually.

## Benefits

### Control over the SQL

We can control and update the SQL generation without requiring user changes. For example, when creating hypertables:

```typescript
// Internal SQL generation can be updated
const sql = hypertable.up().build();
await dataSource.query(sql);
```

### Push newer versions of the SQL on the fly

SQL updates can be pushed without user intervention, allowing seamless updates to TimescaleDB features.

### No knowledge needed of TimescaleDB SQL

Users can work purely with TypeORM entities and decorators without understanding the underlying TimescaleDB SQL.

## Workarounds

### Use the builder manually

For more control, you can use the SQL builder directly:

```typescript
const hypertable = TimescaleDB.createHypertable('my_table', {
  by_range: { column_name: 'time' },
});
const sql = hypertable.up().build();
await queryRunner.query(sql);
```

See the [core tests](https://github.com/timescale/timescaledb-ts/tree/main/packages/core/tests) for more builder examples.
