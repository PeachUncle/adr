### 1. Title
**001 : Data Retrieval Method**

### 2. Context
The objective of the Nuxt application is to read any type of data contained in the Sylius application's database, either in an aggregated or non-aggregated manner. The expected volume of requests is several tens of thousands per day, with each request retrieving data not exceeding a few kilobytes. The data retrieval method must be secure and offer optimal performance.

The current architecture of the Sylius application is that of a standard Sylius application in its latest version. For communication between Nuxt and Sylius, two protocols are considered:
- The REST API present in a basic Sylius installation.
- Direct database connection via the Prisma ORM.

### 3. Decision
We have decided to use Prisma for the direct connection to the Sylius database from the Nuxt application. This method avoids the need for extensive modifications to the existing REST API and bypasses the use of Doctrine, thereby improving performance.

### 4. Options Considered
1. **Using Sylius REST API**
2. **Using Prisma for direct database connection**

### 5. Justification
**Using Sylius REST API**
- *Advantages*:
  - Utilizes existing Sylius features.
  - Easy integration for developers already familiar with the REST API.
- *Disadvantages*:
  - May require extensive modifications to meet the specific needs of the Nuxt application.
  - Potentially limited performance due to the use of Doctrine and additional layers of the REST API.

**Using Prisma for direct database connection**
- *Advantages*:
  - Improved performance by bypassing Doctrine.
  - Flexibility and direct control over SQL queries.
  - No need for extensive modifications to the existing REST API.
- *Disadvantages*:
  - Requires integration and management of Prisma.
  - May increase complexity in terms of maintaining two distinct systems.

### 6. Consequences
- **Performance**: Using Prisma enhances performance by avoiding the additional layers of the REST API and Doctrine.
- **Security**: Direct database connection requires additional security measures to protect the data.
- **Maintenance**: Maintenance could be more complex due to the management of Prisma alongside Sylius.
- **Development**: Development will be more flexible with direct control over SQL queries via Prisma.

### 7. Status
Accepted

### 8. Date
April 20, 2024