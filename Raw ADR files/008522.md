# 6. Decision to Use Postman for Acceptance Testing in the CI/CD Pipeline

## Status

**Accepted**

## Context

Automated acceptance testing is a crucial part of the CI/CD pipeline, ensuring that the API meets functional requirements before deployment. The testing framework must:
- **Validate Endpoints**: Confirm that API endpoints behave as expected.
- **Ensure Consistency**: Provide consistent test execution across development, testing, and production environments.
- **Be Easy to Maintain**: Enable straightforward updates to test cases as the API evolves.
- **Integrate with CI/CD**: Support seamless execution within the CI/CD pipeline.

Postman, combined with its CLI tool, Newman, was selected as the solution for automated acceptance testing due to its ease of use, widespread adoption, and integration capabilities.

## Decision

The project will use **Postman** for defining acceptance tests and **Newman** for executing those tests within the CI/CD pipeline.

### Postman
- **Test Design**: Postman will be used to design and store test collections that validate the API's endpoints, responses, and behaviors.
- **Collection Storage**: Test collections will be version-controlled alongside the project repository to ensure traceability and alignment with API changes.

### Newman
- **Test Execution**: Newman will run the Postman collections as part of the CI/CD pipeline.
- **Environment Integration**: Newman will execute tests against different environments (e.g., staging, production) using environment-specific variables.

### Newman Docker Container
- **Simplified Setup**: The official Newman Docker container eliminates the need to install Node.js or Newman directly in the CI/CD environment, reducing setup complexity.
- **Version Control**: Using the Docker container ensures that the same version of Newman is consistently used across environments, avoiding compatibility issues.
- **Example Workflow**:
    - A Docker Compose service or CI/CD pipeline step can use the Newman Docker container to execute tests:
      ```yaml
      services:
        newman:
          image: postman/newman:alpine
          command: run /collections/my-collection.json -e /environments/staging.json
          volumes:
            - ./postman:/collections
            - ./postman-environments:/environments
      ```
    - Alternatively, in a CI/CD pipeline:
      ```yaml
      - name: Run Postman Tests
        uses: docker://postman/newman:alpine
        with:
          args: run /collections/my-collection.json -e /environments/staging.json
      ```

## Consequences

### Benefits
- **Developer-Friendly**: Postman provides a user-friendly interface for designing, running, and debugging API tests.
- **Comprehensive Testing**: Postman collections support a wide range of tests, including functional, integration, and performance checks.
- **Dockerized Execution**: The Newman Docker container simplifies running tests in isolated environments, ensuring consistency across local development and CI/CD.
- **Environment Flexibility**: Postman’s environment variables simplify testing across multiple environments without modifying the test logic.
- **Reusable Test Collections**: Collections can be reused for manual and automated testing, reducing duplication of effort.
- **Wide Adoption**: Postman and Newman are industry-standard tools with robust documentation and community support.

### Drawbacks
- **Learning Curve**: Developers unfamiliar with Postman or Newman may require time to learn the tools.
- **Dependency on Postman**: The project relies on Postman’s ecosystem, which could introduce challenges if tool compatibility changes in the future.
- **Command-Line Execution**: Newman’s output may require additional parsing or customization for detailed reporting in CI/CD logs.

## Alternatives Considered

1. **JUnit with MockMVC**:
    - Rejected because it focuses on unit testing and mocking rather than full end-to-end acceptance testing.
2. **Custom Python Scripts with Requests**:
    - Rejected due to increased maintenance overhead and lack of a standardized interface for managing and running test cases.
3. **Karate DSL**:
    - Rejected because Postman is more widely adopted, offers a better developer experience, and supports both manual and automated workflows.

## Conclusion

Postman, combined with Newman, provides a robust, developer-friendly solution for automated acceptance testing in the CI/CD pipeline. Using the Newman Docker container further simplifies test execution and ensures consistency across environments. This decision ensures reliable and repeatable testing of API functionality, improving confidence in deployments and reducing production issues.
