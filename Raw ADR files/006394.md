# ADR-015: Adoption of Liquibase for Database Schema Evolution

## Status
Rejected

## Date
2025-03-01

## Context
Our Spring Boot application with PostgreSQL requires a reliable and systematic approach to database schema management. We need a solution that:

- Tracks and versions database schema changes
- Supports collaborative development with multiple developers
- Enables consistent schema application across different environments
- Provides rollback capabilities for schema changes
- Integrates well with our Spring Boot application and CI/CD pipeline
- Handles both development and production database migrations safely
- Supports complex schema changes and data migrations
- Maintains a history of all database changes
- Works well with our PostgreSQL database
- Facilitates database refactoring and evolution over time

Managing database schema changes manually or with ad-hoc scripts leads to inconsistencies, errors, and deployment challenges. Without proper versioning and tracking, database changes become a significant risk during application updates and deployments.

## Decision
We will use **Liquibase** as our database schema migration and version control tool. Liquibase will be used to:

### 1. Schema Version Control
- Define all database schema changes as versioned changesets
- Track the history of schema modifications
- Maintain a record of which changes have been applied to each environment
- Support parallel development of database changes

### 2. Migration Types
- Handle structural changes (tables, columns, indexes, constraints)
- Manage reference/lookup data
- Support conditional changes based on database state
- Enable complex migrations with custom SQL when needed

### 3. Integration Points
- Integrate with Spring Boot application startup
- Run as part of CI/CD pipeline for automated testing
- Support manual execution for DBA-controlled environments
- Generate schema documentation

### 4. Operational Approach
- Store changelog files in XML format for better structure and validation
- Organize changelogs hierarchically by feature or module
- Include descriptive comments for each changeset
- Use contexts to control environment-specific changes
- Implement proper tagging for releases

## Implementation Approach

1. **Project Structure**
   - Store changelog files in `src/main/resources/db/changelog/`
   - Use a master changelog to include all other changelogs
   - Organize changelogs by feature or chronologically
   - Follow a consistent naming convention for changelog files

2. **Change Management**
   - Each changeset will have a unique identifier and author
   - Include descriptive comments explaining the purpose of each change
   - Use contexts to control environment-specific changes
   - Tag database state at significant releases

3. **Development Workflow**
   - Developers create changesets for their database modifications
   - Changes are tested locally before committing
   - CI pipeline validates changesets against a test database
   - Release process includes database migration as a step

4. **Rollback Strategy**
   - Implement explicit rollback instructions for each changeset where possible
   - Test rollback procedures in development environment
   - Document changes that cannot be safely rolled back

## Consequences

### Positive
- Version-controlled database schema evolution
- Repeatable, automated database migrations
- Consistent database state across environments
- Clear history of database changes
- Support for complex refactoring and migrations
- Reduced risk during deployments
- Better collaboration among team members
- Integration with Spring Boot and CI/CD pipeline
- Ability to roll back problematic changes
- Database changes tied to application code changes
- Support for different database vendors if needed in future

### Negative
- Additional learning curve for team members
- Overhead in managing changelog files
- Complex changes may still require careful planning
- Potential performance impact during application startup
- Need for discipline in maintaining changelog files
- Some complex migrations may require custom handling
- Testing database migrations adds complexity to CI/CD pipeline
- Risk of conflicts in changelog files with parallel development

## Alternatives Considered

1. **Flyway**
   - Similar purpose and functionality
   - SQL-first approach vs. Liquibase's XML/YAML/JSON/SQL options
   - Simpler but less flexible than Liquibase
   - Less support for complex refactorings
   - Limited rollback support in community edition
   - Good Spring Boot integration

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

4. **Database-Specific Tools**
   - Tools like pgAdmin for PostgreSQL
   - Visual tools may be easier for some team members
   - Lack of version control integration
   - Not easily automated in CI/CD pipeline
   - Environment-specific management challenges

## Implementation Notes

### Gradle Dependencies (Kotlin DSL)

```kotlin
plugins {
    id("org.liquibase.gradle") version "2.1.1"
}

dependencies {
    // Liquibase core
    implementation("org.liquibase:liquibase-core")
    
    // Spring Boot Liquibase integration (optional if using Spring Boot)
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    
    // Liquibase Gradle plugin (for standalone usage)
    liquibaseRuntime("org.liquibase:liquibase-core:4.9.1")
    liquibaseRuntime("org.liquibase:liquibase-groovy-dsl:3.0.2")
    liquibaseRuntime("info.picocli:picocli:4.6.3")
    liquibaseRuntime("org.postgresql:postgresql:42.3.6")
}

// Liquibase plugin configuration (if using the plugin)
liquibase {
    activities.register("main") {
        this.arguments = mapOf(
            "changeLogFile" to "src/main/resources/db/changelog/db.changelog-master.xml",
            "url" to "jdbc:postgresql://localhost:5432/appdb",
            "username" to "appuser",
            "password" to "apppassword"
        )
    }
}
```

### Spring Boot Configuration

```yaml
spring:
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.xml
    contexts: ${LIQUIBASE_CONTEXTS:default}
    default-schema: public
    liquibase-schema: public
    parameters:
      textColumnType: VARCHAR(255)
    drop-first: false
    label-filter: ${LIQUIBASE_LABEL_FILTER:}
```

### Master Changelog Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ext="http://www.liquibase.org/xml/ns/dbchangelog-ext"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog 
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.5.xsd
        http://www.liquibase.org/xml/ns/dbchangelog-ext 
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-ext.xsd">
        
    <property name="uuid_type" value="uuid" dbms="postgresql"/>
    <property name="uuid_type" value="varchar(36)" dbms="h2,mysql"/>
    <property name="now" value="now()" dbms="postgresql"/>
    <property name="now" value="current_timestamp" dbms="h2,mysql"/>
    
    <!-- Initial Schema -->
    <include file="db/changelog/v1.0/01-initial-schema.xml"/>
    <include file="db/changelog/v1.0/02-reference-data.xml"/>
    
    <!-- Feature: Customer Management -->
    <include file="db/changelog/v1.1/01-customer-preferences.xml"/>
    <include file="db/changelog/v1.1/02-customer-metadata.xml"/>
    
    <!-- Feature: Order Processing -->
    <include file="db/changelog/v1.2/01-order-status-workflow.xml"/>
    <include file="db/changelog/v1.2/02-order-history.xml"/>
    
</databaseChangeLog>
```

### Example Changeset File

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.5.xsd">

    <changeSet id="20230501-1" author="dev.team">
        <comment>Create customer table</comment>
        <createTable tableName="customers">
            <column name="id" type="${uuid_type}">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="first_name" type="varchar(50)">
                <constraints nullable="false"/>
            </column>
            <column name="last_name" type="varchar(50)">
                <constraints nullable="false"/>
            </column>
            <column name="email" type="varchar(100)">
                <constraints nullable="false" unique="true"/>
            </column>
            <column name="created_at" type="timestamp with time zone" defaultValueDate="${now}">
                <constraints nullable="false"/>
            </column>
            <column name="updated_at" type="timestamp with time zone" defaultValueDate="${now}">
                <constraints nullable="false"/>
            </column>
        </createTable>
        <createIndex indexName="idx_customers_email" tableName="customers">
            <column name="email"/>
        </createIndex>
    </changeSet>
    
    <changeSet id="20230501-2" author="dev.team">
        <comment>Create addresses table with foreign key to customers</comment>
        <createTable tableName="addresses">
            <column name="id" type="${uuid_type}">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="customer_id" type="${uuid_type}">
                <constraints nullable="false" foreignKeyName="fk_addresses_customer_id" references="customers(id)"/>
            </column>
            <column name="street" type="varchar(100)">
                <constraints nullable="false"/>
            </column>
            <column name="city" type="varchar(50)">
                <constraints nullable="false"/>
            </column>
            <column name="state" type="varchar(50)"/>
            <column name="postal_code" type="varchar(20)">
                <constraints nullable="false"/>
            </column>
            <column name="country" type="varchar(50)">
                <constraints nullable="false"/>
            </column>
            <column name="address_type" type="varchar(20)">
                <constraints nullable="false"/>
            </column>
            <column name="is_default" type="boolean" defaultValueBoolean="false">
                <constraints nullable="false"/>
            </column>
            <column name="created_at" type="timestamp with time zone" defaultValueDate="${now}">
                <constraints nullable="false"/>
            </column>
            <column name="updated_at" type="timestamp with time zone" defaultValueDate="${now}">
                <constraints nullable="false"/>
            </column>
        </createTable>
        <createIndex indexName="idx_addresses_customer_id" tableName="addresses">
            <column name="customer_id"/>
        </createIndex>
    </changeSet>
    
    <changeSet id="20230501-3" author="dev.team">
        <comment>Add stored procedure for address validation</comment>
        <createProcedure>
            CREATE OR REPLACE FUNCTION validate_address(
                p_street VARCHAR,
                p_city VARCHAR,
                p_country VARCHAR
            ) RETURNS BOOLEAN AS $$
            BEGIN
                -- Address validation logic here
                RETURN TRUE;
            END;
            $$ LANGUAGE plpgsql;
        </createProcedure>
        <rollback>
            DROP FUNCTION IF EXISTS validate_address;
        </rollback>
    </changeSet>
    
    <changeSet id="20230501-4" author="dev.team">
        <comment>Insert reference data for countries</comment>
        <createTable tableName="countries">
            <column name="code" type="char(2)">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="name" type="varchar(100)">
                <constraints nullable="false"/>
            </column>
        </createTable>
        <loadData
            file="db/data/countries.csv"
            tableName="countries">
            <column name="code" header="code"/>
            <column name="name" header="name"/>
        </loadData>
    </changeSet>
    
    <changeSet id="20230502-1" author="dev.team">
        <comment>Add status column to customers table</comment>
        <addColumn tableName="customers">
            <column name="status" type="varchar(20)" defaultValue="ACTIVE">
                <constraints nullable="false"/>
            </column>
        </addColumn>
        <rollback>
            <dropColumn tableName="customers" columnName="status"/>
        </rollback>
    </changeSet>
    
</databaseChangeLog>
```

### Using Contexts for Environment-Specific Changes

```xml
<changeSet id="20230505-1" author="dev.team" context="dev,test">
    <comment>Add test data - only for development and test environments</comment>
    <loadData
        file="db/data/test-customers.csv"
        tableName="customers">
        <column name="id" header="id"/>
        <column name="first_name" header="first_name"/>
        <column name="last_name" header="last_name"/>
        <column name="email" header="email"/>
    </loadData>
</changeSet>

<changeSet id="20230505-2" author="dev.team" context="prod">
    <comment>Create additional indexes for production environment</comment>
    <createIndex indexName="idx_customers_name_email" tableName="customers">
        <column name="last_name"/>
        <column name="email"/>
    </createIndex>
</changeSet>
```

### Custom Java-Based Migration

```java
package com.example.migration;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import liquibase.change.custom.CustomTaskChange;
import liquibase.database.Database;
import liquibase.database.jvm.JdbcConnection;
import liquibase.exception.CustomChangeException;
import liquibase.exception.SetupException;
import liquibase.exception.ValidationErrors;
import liquibase.resource.ResourceAccessor;

public class ComplexDataMigration implements CustomTaskChange {
    
    @Override
    public void execute(Database database) throws CustomChangeException {
        JdbcConnection connection = (JdbcConnection) database.getConnection();
        
        try {
            // Complex data migration logic
            Statement stmt = connection.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT id, old_format_data FROM legacy_table");
            
            PreparedStatement updateStmt = connection.prepareStatement(
                "INSERT INTO new_table (id, transformed_data) VALUES (?, ?)");
                
            while (rs.next()) {
                String id = rs.getString("id");
                String oldData = rs.getString("old_format_data");
                
                // Transform data
                String newData = transformData(oldData);
                
                updateStmt.setString(1, id);
                updateStmt.setString(2, newData);
                updateStmt.addBatch();
            }
            
            updateStmt.executeBatch();
            rs.close();
            stmt.close();
            updateStmt.close();
        } catch (Exception e) {
            throw new CustomChangeException("Error executing complex migration: " + e.getMessage(), e);
        }
    }
    
    private String transformData(String oldData) {
        // Data transformation logic
        return oldData.toUpperCase(); // Simplified example
    }
    
    @Override
    public String getConfirmationMessage() {
        return "Complex data migration completed successfully";
    }
    
    @Override
    public void setUp() throws SetupException {}
    
    @Override
    public void setFileOpener(ResourceAccessor resourceAccessor) {}
    
    @Override
    public ValidationErrors validate(Database database) {
        return new ValidationErrors();
    }
}
```

```xml
<changeSet id="20230510-1" author="dev.team">
    <comment>Complex data migration using custom Java class</comment>
    <customChange class="com.example.migration.ComplexDataMigration"/>
</changeSet>
```

### Running Liquibase Outside Spring Boot

```bash
 Using Liquibase CLI
liquibase \
  --driver=org.postgresql.Driver \
  --classpath=/path/to/postgresql-jdbc.jar \
  --changeLogFile=db/changelog/db.changelog-master.xml \
  --url="jdbc:postgresql://localhost:5432/appdb" \
  --username=appuser \
  --password=apppassword \
  update
```

## CI/CD Integration

```yaml
# Example GitHub Actions workflow step
- name: Run Database Migration
  run: |
    ./mvnw liquibase:update \
      -Dliquibase.url=jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME \
      -Dliquibase.username=$DB_USERNAME \
      -Dliquibase.password=$DB_PASSWORD
  env:
    DB_HOST: ${{ secrets.DB_HOST }}
    DB_PORT: 5432
    DB_NAME: ${{ secrets.DB_NAME }}
    DB_USERNAME: ${{ secrets.DB_USERNAME }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

## Compliance Verification
- Pre-commit validation of changelog files
- Testing migrations in CI pipeline with test database
- Verification of rollback capabilities
- Review of changelog files during code reviews
- Regular audits of database schema against changelogs
- Validation of migration performance on production-like data volumes
- Monitoring of migration execution times

## References
- Liquibase Documentation: https://docs.liquibase.com/
- Spring Boot Liquibase Integration: https://docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.liquibase
- Liquibase Best Practices: https://www.liquibase.org/get-started/best-practices
- Database Refactoring Patterns: https://databaserefactoring.com/
- Liquibase vs Flyway Comparison: https://www.baeldung.com/liquibase-vs-flyway
- Changelogs Reference: https://docs.liquibase.com/concepts/changelogs/home.html
