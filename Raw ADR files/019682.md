# Architecture Decision Record (ADR)

## Test Framework

**Status**: Accepted \
**Date**: 07/05/2023 \
**Technical decision**: Choose GoogleTest as the Test Framework for the C project.

### Context

The C project requires a robust and efficient test framework to automate unit testing, fuzzing, and mocking. Effective testing is crucial for ensuring the correctness, reliability, and maintainability of the project. Therefore, a decision is needed to choose a suitable test framework that supports these functionallities.

### Decision

After evaluating several options, including GoogleTest, CUnit, and Ceedling, we have decided to adopt GoogleTest as the test framework for the C project. GoogleTest provides comprehensive support for unit tests, fuzzing, mocks, and test fixtures, fulfilling the project's testing requirements.

### We also considered the following alternatives

1. CUnit:

    CUnit is a lightweight and widely used unit testing framework for C projects. It provides a simple and easy-to-use interface for writing and executing unit tests. However, CUnit lacks built-in support for fuzzing, mocks, and test fixtures, which are important requirements for our project.

2. Ceedling:

    Ceedling is a build system and test framework specifically designed for C projects. It integrates with CMock and Unity, which provide mocking and unit testing capabilities. While Ceedling offers a convenient setup for unit testing and mocking, it doesn't provide direct support for fuzzing, which is a valuable testing technique for uncovering edge cases and vulnerabilities.

### Rationale

The decision to choose GoogleTest as the test framework is based on the following factors:

1. Unit Testing Support:

    GoogleTest is a widely adopted and mature test framework that provides excellent support for unit testing in C projects. It offers a rich set of assertion macros, test runners, and test discovery capabilities, making it easy to write and execute unit tests.

2. Fuzzing Support:

    The compatibility between GoogleTest and the FuzzTest framework allows for efficient and effective fuzz testing of the C project. FuzzTest, built on top of GoogleTest, provides powerful fuzzing capabilities that can uncover hidden bugs and vulnerabilities in the project's code.

3. Mocking Capabilities:

    GoogleTest includes a flexible and powerful mocking framework called GoogleMock. This feature enables developers to create mock objects and define their behavior, allowing for isolated testing of components with external dependencies.

4. Test Fixtures:

    GoogleTest supports the use of test fixtures, which provide a way to set up and tear down common test environments and shared resources. Test fixtures help in organizing and reusing setup and teardown code across multiple tests, leading to more maintainable and concise test suites.

### Consequences

The adoption of GoogleTest as the test framework for the C project will result in the following consequences:

1. Comprehensive Testing Capabilities:

    GoogleTest's support for unit tests, fuzzing, mocks, and test fixtures ensures comprehensive testing coverage for the project, facilitating the detection of bugs, verifying functionality, and improving code quality.

2. Integration with existing Google FuzzTest:

    The compatibility between GoogleTest and the FuzzTest framework allows for seamless integration of fuzz testing into the project's testing strategy. This integration enhances the project's resilience to potential security vulnerabilities and strengthens its overall reliability.

3. Learning Curve:

    Developers who are new to GoogleTest may need to invest some time initially to understand its concepts and usage. However, the wealth of documentation, tutorials, and community support available for GoogleTest will assist in the learning process and enable developers to effectively utilize the test framework.

### Related ADRs

None.

### Notes

- JetBrains [unit-testing frameworks](https://www.jetbrains.com/lp/devecosystem-2022/c/#which-unit-testing-frameworks-do-you-regularly-use-if-any-two-years) survey
- GoogleTest [GitHub](https://github.com/google/googletest)
- FuzzTest [GitHub](https://github.com/google/fuzztest)
- CUnit [GitLab](https://gitlab.com/cunity/cunit)
- Ceedling [GitHub](https://github.com/ThrowTheSwitch/Ceedling)
