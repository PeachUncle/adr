# ADR-016: Adoption of Flyway for Database Schema Evolution

## Status
Accepted

## Date
2025-03-01

## Context
Our Spring Boot application with PostgreSQL requires a reliable and systematic approach to database schema management. We need a solution that:

- Tracks and versions database schema changes
- Supports collaborative development with multiple developers
- Enables consistent schema application across different environments
- Provides a way to manage schema changes across deployments
- Integrates well with our Spring Boot application and CI/CD pipeline
- Handles both development and production database migrations safely
- Supports SQL-based schema changes and data migrations
- Maintains a history of all database changes
- Works well with our PostgreSQL database
- Facilitates database refactoring and evolution over time

Managing database schema changes manually or with ad-hoc scripts leads to inconsistencies, errors, and deployment challenges. Without proper versioning and tracking, database changes become a significant risk during application updates and deployments.

## Decision
We will use **Flyway** as our database schema migration and version control tool. Flyway will be used to:

### 1. Schema Version Control
- Define all database schema changes as versioned SQL migration scripts
- Track the history of schema modifications through a dedicated metadata table
- Maintain a record of which migrations have been applied to each environment
- Support collaborative development of database changes

### 2. Migration Types
- Handle structural changes (tables, columns, indexes, constraints)
- Manage reference/lookup data
- Support repeatable migrations for views, functions, and procedures
- Enable Java-based migrations for complex scenarios when needed

### 3. Integration Points
- Integrate with Spring Boot application startup
- Run as part of CI/CD pipeline for automated testing
- Support manual execution for DBA-controlled environments
- Generate reports on migration status

### 4. Operational Approach
- Store migration scripts in SQL format for direct database compatibility
- Use a consistent versioning scheme for migrations (timestamp-based)
- Include descriptive comments in migration scripts
- Organize migrations by version or feature
- Implement proper baseline for existing databases

## Implementation Approach

1. **Project Structure**
   - Store migration scripts in `src/main/resources/db/migration/`
   - Use a consistent naming convention: `V{version}__{description}.sql`
   - Organize repeatable migrations in `src/main/resources/db/migration/repeatable/`
   - Include comments in SQL files explaining the purpose of each change

2. **Versioning Strategy**
   - Use timestamp-based versioning (e.g., `V20230501120000__create_customer_table.sql`)
   - Ensure version numbers are always increasing
   - Include descriptive names in migration files
   - Never modify a migration that has been committed to version control

3. **Development Workflow**
   - Developers create new migration scripts for their database changes
   - Changes are tested locally before committing
   - CI pipeline validates migrations against a test database
   - Release process includes database migration as a step

4. **Handling Environments**
   - Use Spring profiles to control environment-specific configurations
   - Implement baseline migrations for existing production databases
   - Consider separate migration paths for major/minor versions

## Consequences

### Positive
- Simple, SQL-first approach to database migrations
- Clear and straightforward versioning system
- Easy to understand for developers with SQL experience
- Minimal overhead and complexity
- Native support in Spring Boot
- Automated migration execution during application startup
- Reliable detection of migration conflicts
- Good performance with minimal overhead
- Support for different database vendors if needed in future
- Straightforward integration with CI/CD pipelines

### Negative
- Limited rollback support in community edition
- SQL scripts can be less structured than XML/YAML alternatives
- Less support for complex refactorings compared to some alternatives
- No built-in support for generating documentation from migrations
- Migration scripts may require duplication for different database vendors
- Less flexibility for complex conditions or preconditions
- Need for discipline in maintaining migration files
- Risk of conflicts with parallel development

## Alternatives Considered

1. **Liquibase**
   - More flexible format options (XML, YAML, JSON, SQL)
   - Better support for complex refactorings
   - Built-in rollback capabilities
   - More verbose configuration
   - Steeper learning curve
   - More features but increased complexity

2. **Hibernate Schema Generation**
   - Automatic schema generation from entity mappings
   - Convenient for early development
   - Lacks fine-grained control over schema evolution
   - Not suitable for production environments
   - No explicit versioning of changes
   - Limited support for complex migrations

3. **Manual SQL Scripts**
   - Complete control over SQL execution
   - No additional tooling required
   - No versioning or tracking of applied changes
   - Error-prone and difficult to manage
   - Challenging to maintain consistency across environments
   - No built-in rollback support

4. **jOOQ Migrations**
   - Type-safe schema definition
   - Integration with jOOQ's code generation
   - Less mature migration framework
   - Requires additional dependencies
   - Smaller community compared to Flyway or Liquibase

## Implementation Notes

### Gradle Dependencies (Kotlin DSL)

```kotlin
plugins {
    id("org.flywaydb.flyway") version "8.5.13"
}

dependencies {
    // Flyway core
    implementation("org.flywaydb:flyway-core:8.5.13")
    
    // Spring Boot Flyway integration (optional if using Spring Boot)
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    
    // PostgreSQL driver (required for Flyway to connect to the database)
    runtimeOnly("org.postgresql:postgresql:42.3.6")
}

// Flyway plugin configuration (if using the plugin)
flyway {
    url = "jdbc:postgresql://localhost:5432/appdb"
    user = "appuser"
    password = "apppassword"
    locations = arrayOf("classpath:db/migration")
    isBaselineOnMigrate = true
}
```

### Spring Boot Configuration

```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
    baseline-version: 0
    out-of-order: false
    validate-on-migrate: true
    placeholder-replacement: true
    placeholders:
      table_suffix: ${ENVIRONMENT:dev}
    schemas: public
    default-schema: public
    connect-retries: 3
    sql-migration-prefix: V
    repeatable-sql-migration-prefix: R
    sql-migration-separator: __
    sql-migration-suffixes: .sql
```

### Example Versioned Migration

```sql
-- V20230501120000__create_customer_table.sql

-- Create customers table
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Add index on email for faster lookups
CREATE INDEX idx_customers_email ON customers(email);

-- Create addresses table
CREATE TABLE addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    street VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL,
    address_type VARCHAR(20) NOT NULL,
    is_default BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Add index on customer_id for faster lookups and joins
CREATE INDEX idx_addresses_customer_id ON addresses(customer_id);

-- Add comments to tables for documentation
COMMENT ON TABLE customers IS 'Stores customer information';
COMMENT ON TABLE addresses IS 'Stores customer addresses';
```

### Example Subsequent Migration

```sql
-- V20230502143000__add_customer_status.sql

-- Add status column to customers table
ALTER TABLE customers 
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE';

-- Create index on status for filtering
CREATE INDEX idx_customers_status ON customers(status);

-- Add comment to document the column
COMMENT ON COLUMN customers.status IS 'Customer status (ACTIVE, INACTIVE, SUSPENDED)';
```

### Example Repeatable Migration

```sql
-- R__create_customer_view.sql

-- This is a repeatable migration that will run whenever its checksum changes
-- Drop the view if it exists to allow recreation
DROP VIEW IF EXISTS customer_addresses_view;

-- Create the view
CREATE OR REPLACE VIEW customer_addresses_view AS
SELECT 
    c.id AS customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.status,
    a.id AS address_id,
    a.street,
    a.city,
    a.state,
    a.postal_code,
    a.country,
    a.address_type,
    a.is_default
FROM customers c
LEFT JOIN addresses a ON c.id = a.customer_id;

-- Add comment to the view
COMMENT ON VIEW customer_addresses_view IS 'Provides a denormalized view of customers with their addresses';
```

### Java-Based Migration Example

```java
package com.example.migration;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.SingleConnectionDataSource;

public class V20230510120000__Complex_Data_Migration extends BaseJavaMigration {

    @Override
    public void migrate(Context context) throws Exception {
        JdbcTemplate jdbcTemplate = new JdbcTemplate(
            new SingleConnectionDataSource(context.getConnection(), true));
        
        // Complex migration logic
        jdbcTemplate.query(
            "SELECT id, old_format_data FROM legacy_table",
            rs -> {
                String id = rs.getString("id");
                String oldData = rs.getString("old_format_data");
                
                // Transform data
                String newData = transformData(oldData);
                
                jdbcTemplate.update(
                    "INSERT INTO new_table (id, transformed_data) VALUES (?, ?)",
                    id, newData);
            }
        );
    }
    
    private String transformData(String oldData) {
        // Data transformation logic
        return oldData.toUpperCase(); // Simplified example
    }
}
```

### Adding Test Data for Development

```sql
-- V20230505120000__add_test_data.sql

-- Only add this data if we're in a development environment
DO $$
BEGIN
    -- Check if we're in a development environment
    IF current_setting('app.environment', true) = 'dev' THEN
        -- Insert test customers
        INSERT INTO customers (id, first_name, last_name, email, status)
        VALUES
            ('11111111-1111-1111-1111-111111111111', 'John', 'Doe', 'john.doe@example.com', 'ACTIVE'),
            ('22222222-2222-2222-2222-222222222222', 'Jane', 'Smith', 'jane.smith@example.com', 'ACTIVE'),
            ('33333333-3333-3333-3333-333333333333', 'Bob', 'Johnson', 'bob.johnson@example.com', 'INACTIVE');
            
        -- Insert test addresses
        INSERT INTO addresses (id, customer_id, street, city, state, postal_code, country, address_type, is_default)
        VALUES
            ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', '123 Main St', 'Anytown', 'CA', '12345', 'USA', 'HOME', true),
            ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222', '456 Oak Ave', 'Somewhere', 'NY', '67890', 'USA', 'HOME', true),
            ('cccccccc-cccc-cccc-cccc-cccccccccccc', '33333333-3333-3333-3333-333333333333', '789 Pine Blvd', 'Nowhere', 'TX', '54321', 'USA', 'HOME', true);
    END IF;
END $$;
```

### Running Flyway Manually

```bash
 Using Flyway CLI
flyway \
  -driver=org.postgresql.Driver \
  -url=jdbc:postgresql://localhost:5432/appdb \
  -user=appuser \
  -password=apppassword \
  -locations=filesystem:src/main/resources/db/migration \
  migrate
```

## CI/CD Integration

```yaml
 Example GitHub Actions workflow step
- name: Run Database Migration
  run: |
    ./mvnw flyway:migrate \
      -Dflyway.url=jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME \
      -Dflyway.user=$DB_USERNAME \
      -Dflyway.password=$DB_PASSWORD
  env:
    DB_HOST: ${{ secrets.DB_HOST }}
    DB_PORT: 5432
    DB_NAME: ${{ secrets.DB_NAME }}
    DB_USERNAME: ${{ secrets.DB_USERNAME }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

## Spring Boot Integration

```java
@Component
public class FlywayMigrationReporter {

    private static final Logger log = LoggerFactory.getLogger(FlywayMigrationReporter.class);
    
    @Bean
    public FlywayMigrationStrategy flywayMigrationStrategy() {
        return flyway -> {
            // You can add custom logic before migration
            log.info("Starting Flyway migration...");
            
            // Run the migration
            flyway.migrate();
            
            // Report on completed migrations
            MigrationInfo[] appliedMigrations = flyway.info().applied();
            log.info("Applied {} migrations:", appliedMigrations.length);
            for (MigrationInfo migration : appliedMigrations) {
                log.info("  {} : {} from file {} ({})",
                    migration.getVersion(),
                    migration.getDescription(),
                    migration.getScript(),
                    migration.getState());
            }
        };
    }
}
```

## Compliance Verification
- Pre-commit validation of SQL scripts
- Testing migrations in CI pipeline with test database
- Regular review of Flyway metadata table to ensure consistency
- Review of SQL migration files during code reviews
- Performance testing of migrations on production-like data volumes
- Regular audits to ensure all environments are on the same version
- Validation of SQL syntax and compatibility with target database version

## References
- Flyway Documentation: https://flywaydb.org/documentation/
- Spring Boot Flyway Integration: https://docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.flyway
- Flyway Best Practices: https://flywaydb.org/documentation/concepts/bestpractices
- Database Refactoring Patterns: https://databaserefactoring.com/
- Flyway vs Liquibase Comparison: https://www.baeldung.com/liquibase-vs-flyway
- Flyway Command Line: https://flywaydb.org/documentation/usage/commandline/
