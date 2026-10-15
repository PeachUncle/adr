# Architecture Decision Record (ADR)

## Build system

**Status**: Accepted \
**Date**: 07/05/2023 \
**Decision-maker**: Mario Miosga \
**Technical decision**: Choose CMake as the build system for the C++ project.

### Context

The C++ project requires a reliable and efficient build system to automate the compilation, testing, and deployment processes. The existing manual build process is time-consuming and prone to errors. Therefore, a decision is needed to choose a suitable build system that can streamline the development workflow, improve productivity, and ensure consistent and reliable builds.

### Decision

I have decided to adopt the CMake build system for the C++ project. CMake is a popular and widely-used build system that offers several benefits for C++ projects. It provides a platform-independent way of defining the build process and generating the necessary build files (Makefiles or IDE project files). CMake supports incremental builds, dependency tracking, and parallel builds, which can significantly speed up the compilation process. Additionally, it has good integration with popular development tools and IDEs.

I also considered the following alternatives:

1. Gradle

    Gradle is a versatile build system that supports multiple programming languages, including C and C++. It provides a declarative build configuration using a Groovy or Kotlin-based DSL. Gradle offers powerful dependency management and build automation capabilities, making it suitable for large-scale projects. However, for this particular C++ project, we found that CMake's platform independence, simplicity, and better integration with C++ specific tools and libraries were more aligned with our requirements.

2. Bazel

    Bazel is a build system developed by Google that emphasizes scalability and performance. It uses a language-agnostic build configuration syntax and focuses on reproducibility and incremental builds. While Bazel provides excellent support for large-scale projects and complex build graphs, we determined that its learning curve and initial setup overhead may outweigh the benefits for this relatively smaller C++ project.

### Rationale

The decision to choose CMake as the build system is based on the following factors:

1. Popularity and Community Support

    CMake is widely adopted in the C and C++ development community. It has an active community with extensive documentation, tutorials, and a rich set of plugins and extensions. This ensures good support and availability of resources for troubleshooting and extending the build system.

2. Platform Independence

    CMake allows the project to be built on multiple platforms, including Windows, macOS, and various Unix-based systems. It abstracts the build process from the underlying platform, making it easier to maintain and port the project across different environments.

3. Flexibility and Modularity

    CMake provides a flexible and modular approach to defining the build process. It supports the organization of the project into separate modules, libraries, and executables, allowing for better code organization and reusability. CMake also enables easy integration with external libraries and dependencies.

4. Incremental Builds and Dependency Tracking

    CMake has built-in support for incremental builds, which means that only modified source files and their dependencies are recompiled. This significantly reduces build times during iterative development. CMake's dependency tracking mechanism ensures that changes to dependencies trigger the recompilation of affected components, maintaining the integrity of the build.

5. Integration with IDEs and Development Tools

    CMake integrates well with popular integrated development environments (IDEs) such as Visual Studio, CLion, and Xcode. It can generate project files compatible with these IDEs, enabling seamless development and debugging experiences. Furthermore, CMake integrates with various testing frameworks, enabling automated testing as part of the build process.

### Consequences

The adoption of CMake as the build system for the C++ project will result in the following consequences:

1. Improved Productivity

    The automated build process provided by CMake will save developers' time and effort, eliminating manual compilation steps. This will improve productivity and allow developers to focus more on coding and testing.

2. Consistent and Reliable Builds

    CMake's standardized build process ensures consistent and reliable builds across different platforms and environments. This reduces the risk of build-related issues and improves the overall stability of the project.

3. Learning Curve

    Developers who are unfamiliar with CMake may need to invest some time initially to understand its concepts and syntax. However, the long-term benefits and the availability of learning resources make it a worthwhile investment.

4. Integration Effort

    Integrating the existing project with CMake may require some effort to set up the build configuration and migrate the existing build files. However, the flexibility and modularity of CMake will facilitate this process.

### Related ADRs

None.

### Notes

- JetBrains [build system](https://www.jetbrains.com/lp/devecosystem-2022/cpp/#Which-project-models-or-build-systems-do-you-regularly-use) survey
- CMake [documentation](https://cmake.org/cmake/help/latest/)
- Gradle [documentation](https://docs.gradle.org/current/userguide/userguide.html?_gl=1*18ajhr1*_ga*MTI0MTIxMjQ4NC4xNjg3ODU4NDk0*_ga_7W7NC6YNPT*MTY4Nzg1ODQ5NC4xLjAuMTY4Nzg1ODQ5NC42MC4wLjA.)
- Bazel [documentation](https://bazel.build/docs)
