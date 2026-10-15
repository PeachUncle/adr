# 007 - Application of Testcontainers for Integration Testing of the Database

**Reporter:** Rafał Karaś

## Context

The decision concerns tools and practices related to integration testing of the database within the project. The key aspect is the effective and reliable verification of the system's integration with the database in a testing environment.

## Considered Options

- **Option #1** - Use of the Testcontainers library to run Docker containers for databases in integration tests.
- **Option #2** - Manual management of database instances for tests.

## Decision

After a thorough analysis of the available options, the decision has been made to go with **Option #1**, which is the use of the Testcontainers library to run Docker containers for databases in integration tests.

This decision is based on the following reasons:
1. **Environmental Isolation:** Testcontainers allows running isolated instances of databases in Docker containers, eliminating issues related to interference between tests.
2. **Ease of Configuration:** Configuring databases for tests is much simpler when they can be run in Docker containers using Testcontainers.
3. **Automated Container Lifecycle Management:** Testcontainers automatically manages the container lifecycle, from starting to stopping, eliminating the need for manual management of database instances.
4. **Easy Integration with CI/CD Testing:** The use of Testcontainers facilitates the integration of tests with the CI/CD process, ensuring consistency between the developer environment and the testing environment.

## Expected result

Adopting Testcontainers as a tool for integration testing of the database will enable effective, isolated, and reliable testing of the system's integration with the database.

Impact on:
- **Organization:** It will simplify the management of integration tests, eliminating issues related to interference between tests.
- **Standardization:** It will provide a consistent approach to integration testing of the database in the project.
- **Concrete Solution:** It will allow easy configuration and management of the container lifecycle for databases in tests.

Potential negative consequences:
- The need for adaptation for individuals who have not worked with Testcontainers before.

## Benefits of Using Testcontainers

1. **Test Isolation:** Testcontainers ensures test isolation, eliminating potential problems arising from interference between tests.
2. **Ease of Configuration:** Running isolated instances of databases in Docker containers using Testcontainers simplifies the configuration of the testing environment.
3. **Automated Container Lifecycle:** estcontainers automates the container lifecycle, avoiding the need for manual management of database instances.
4. **Integration with CI/CD:** The use of Testcontainers facilitates the integration of tests with the CI/CD process, ensuring consistency between the developer environment and the testing environment.
5. **Support for Various Databases:** Testcontainers supports various databases, enabling integration testing for different database management systems.

## Links

- [Testcontainers](https://testcontainers.com/guides/getting-started-with-testcontainers-for-dotnet/)
