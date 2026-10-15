# Architecture Decision Record (ADR)

## Test Framework

**Status**: Accepted \
**Date**: 07/05/2023 \
**Decision-maker**: Mario Miosga \
**Technical decision**: Choose GoogleTest as the Test framework for the C++ project.

### Context

The C++ project requires a robust and efficient test framework to automate unit testing, fuzzing, mocks, and test fixtures. Effective testing is crucial for ensuring the correctness, reliability, and maintainability of the project. Therefore, a decision is needed to choose a suitable test framework that supports these testing requirements. Additionally, considering that Google has released the FuzzTest framework compatible with the Google Test framework, it is important to evaluate this compatibility as well.

### Decision

After evaluating several options, including Google Test, Catch2, and CppUnit, we have decided to adopt Google Test as the test framework for the C++ project. Google Test provides comprehensive support for unit tests, fuzzing, mocks, and test fixtures, fulfilling the project's testing requirements. The compatibility between Google Test and the newly released FuzzTest framework further strengthens this decision.

### I also considered the following alternatives:

1. Catch2
   
    Catch2 is a popular and lightweight test framework for C++ projects. It offers an expressive and intuitive syntax for writing tests, making it easy to create and maintain test cases. However, Catch2's support for fuzzing is not as extensive as Google Test's, and it does not provide a built-in mocking framework like Google Mock.

2. CppUnit
   
    CppUnit is a mature and widely used test framework for C++ projects. It provides a rich set of features for writing and executing unit tests, including support for test fixtures and test suites. However, CppUnit lacks native support for fuzzing and mocking, which are important testing capabilities for our project.


### Rationale

The decision to choose Google Test as the test framework is based on the following factors:

1. Unit Testing Support
   
    Google Test is a widely adopted and mature test framework that provides excellent support for unit testing in C++ projects. It offers a rich set of assertion macros, test runners, and test discovery capabilities, making it easy to write and execute unit tests.

2. Fuzzing Support
   
    The compatibility between Google Test and the FuzzTest framework, released by Google, allows for efficient and effective fuzz testing of the C++ project. FuzzTest, built on top of Google Test, provides powerful fuzzing capabilities that can uncover hidden bugs and vulnerabilities in the project's code.

3. Mocking Capabilities
   
    Google Test includes a flexible and powerful mocking framework called Google Mock. This feature enables developers to create mock objects and define their behavior, allowing for isolated testing of components with external dependencies.

4. Test Fixtures
   
    Google Test supports the use of test fixtures, which provide a way to set up and tear down common test environments and shared resources. Test fixtures help in organizing and reusing setup and teardown code across multiple tests, leading to more maintainable and concise test suites.

### Consequences

The adoption of Google Test as the test framework for the C++ project will result in the following consequences:

1. Comprehensive Testing Capabilities
   
    Google Test's support for unit tests, fuzzing, mocks, and test fixtures ensures comprehensive testing coverage for the project, facilitating the detection of bugs, verifying functionality, and improving code quality.

2. Integration with Google FuzzTest
   
    The compatibility between Google Test and the FuzzTest framework allows for seamless integration of fuzz testing into the project's testing strategy. This integration enhances the project's resilience to potential security vulnerabilities and strengthens its overall reliability.

3. Learning Curve
   
    Developers who are new to Google Test may need to invest some time initially to understand its concepts and usage. However, the wealth of documentation, tutorials, and community support available for Google Test will assist in the learning process and enable developers to effectively utilize the test framework.

### Related ADRs

None.

### Notes


- JetBrains [unit-testing frameworks](https://www.jetbrains.com/lp/devecosystem-2022/cpp/#Which-unit-testing-frameworks-do-you-regularly-use) survey
- GoogleTest [GitHub](https://github.com/google/googletest)
- FuzzTest [GitHub](https://github.com/google/fuzztest)
- CppUnit [documentation](https://cppunit.sourceforge.net/doc/1.8.0/)
- Catch2 [GitHub](https://github.com/catchorg/Catch2)
