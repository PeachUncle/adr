# Architecture Decision Record (ADR)

## Dependency manager

**Status**: Accepted \
**Date**: 07/05/2023 \
**Decision-maker**: Mario Miosga \
**Technical decision**: Choose vcpkg as the dependency manager for the C++ project.

### Context

A C++ project requires a dependency manager to handle external dependencies effectively. I have evaluated three options: Conan v2.x, Conan v1.x, and vcpkg. Each option has its advantages and limitations, and we need to select the most suitable dependency manager based on our project requirements.

### Decision

I have decided to use vcpkg as the dependency manager for our C++ project.

Benefits of vcpkg:

1. Easy integration in CMake

    vcpkg offers seamless integration with CMake, allowing us to easily manage and build dependencies within our build system. This will streamline the development process and improve productivity.

2. C++/CMake Implementation

    Vcpkg is implemented in C++, aligning with the language of the project itself. This choice emphasizes transparency and familiarity for C++ developers using the dependency manager. By using C++, Vcpkg ensures that users do not need to learn another programming language solely to understand and use the dependency manager.

4. Large amount of packages

    vcpkg provides a wide range of pre-compiled packages, giving us access to a comprehensive selection of libraries and tools. This extensive package repository will save us time and effort in finding and configuring dependencies.

5. Collaboratively Maintained Packages

    Vcpkg follows a model where packages are collaboratively maintained, resulting in a single, well-maintained version of each package. This approach reduces the need for users to sift through multiple public packages to find one that suits their needs, reducing potential compatibility issues and improving the overall quality of packages.

7. Versioning possibility

    vcpkg allows us to specify precise versions of packages, ensuring consistent and reproducible builds. This versioning capability is crucial for maintaining stability and avoiding unexpected behavior caused by package updates.

8. Automatic SBOM generation

    vcpkg includes built-in functionality to automatically generate Software Bill of Materials (SBOM) with license information in SPDX format for every package. This feature enhances our compliance efforts and helps ensure proper license management within our project.

### Rationale

I have chosen vcpkg over the other options due to the following considerations:

- Conan v2.x
  > Conan v2.x is not compatible with all packages from ConanCenter recipes. This limitation could lead to difficulties and inconsistencies when managing dependencies, potentially causing delays or errors during the development process.

- Conan v1.x
  > Conan v1.x although compatible with ConanCenter recipes, presents challenges in integration with CMake. It introduces an additional point of failure and requires extra effort to maintain the integration, which may lead to increased development and maintenance overhead.

By selecting vcpkg, we ensure a smooth integration with CMake, gain access to a vast library of packages, maintain version control over dependencies, and benefit from automatic SPDX SBOM generation for license compliance.

### Consequences

The decision to use vcpkg as the dependency manager for our C++ project will result in the following consequences:

1. Improved development experience

    The integration of vcpkg with CMake will simplify the management of dependencies and improve the overall development experience.

2. Variety of libraries to choose from

    The wide variety of packages available in vcpkg's repository will provide us with a broad range of libraries and tools to choose from.
  
3. Reducing risks

    Version control of packages will ensure consistent and predictable builds, reducing the risk of unexpected behavior caused by dependency updates.
  
4. Automatic SBOM generation

    The automatic SPDX SBOM generation in vcpkg will enhance our compliance efforts by providing comprehensive license information for each package.
  
5. Migrating existing dependencies

   It is important to note that we may need to invest some effort in migrating existing dependencies or configurations to vcpkg.

### Related ADRs

None.

### Notes

- JetBrains [dependency manager](https://www.jetbrains.com/lp/devecosystem-2022/cpp/#How-do-you-manage-your-third-party-libraries-in-C) survey
- vcpkg [documentation](https://learn.microsoft.com/en-us/vcpkg/)
- Conan v1.x [documentation](https://docs.conan.io/en/1.59/index.html)
- Conan v2.x [documentation](https://docs.conan.io/2/)
