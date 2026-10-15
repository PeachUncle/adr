# Decision to Export Utility Classes to a Separate Kotlin Library

## Status

**Proposed**

## Context

The current project includes several utility classes and libraries, such as logging utilities and the `Dsi` class, which provide reusable functionality across multiple parts of the application. Keeping these utilities within the main project introduces challenges:

1. **Code Duplication**: Other projects that need similar functionality may duplicate the code, leading to inconsistencies and maintenance overhead.
2. **Tight Coupling**: Tying these utilities to the main API project increases the complexity of refactoring or reusing them in other contexts.
3. **Scalability**: As the project grows, maintaining utilities alongside domain-specific logic becomes harder to manage.

By extracting these utilities into a separate Kotlin library, the project can promote reuse, improve modularity, and enable easier maintenance.

## Decision

The utility classes and libraries will be exported to a separate Kotlin library. This library will:

1. Contain general-purpose utilities (e.g., logging, configuration helpers, and the `Dsi` class).
2. Be versioned and published to a private or public repository for reuse across multiple projects.
3. Be designed as a dependency that can be imported by this and other projects as needed.

### Implementation Details

1. **Library Structure**:
    - Create a new Kotlin project for the utility library.
    - Organize utilities into clearly defined packages (e.g., `logging`, `config`, `validation`).

2. **Dependency Management**:
    - Use Maven or Gradle to define and manage dependencies for the library.
    - Publish the library to a repository (e.g., Maven Central, JitPack, or a private repository).

3. **API Design**:
    - Ensure the library exposes a clean and minimal API.
    - Include comprehensive documentation for each utility.

4. **Integration with the Main Project**:
    - Replace existing utility code in the main project with imports from the new library.

### Example Library Structure

```
com.example.utilities
├── logging
│   ├── Logger.kt
├── config
│   ├── ConfigLoader.kt
├── validation
│   ├── Validator.kt
├── Dsi.kt
```

## Consequences

### Benefits

- **Reusability**: Utilities can be reused across multiple projects without duplication.
- **Modularity**: Separating utilities from the main project improves the modularity of the codebase.
- **Maintainability**: Changes to utilities can be made in one place, reducing the risk of inconsistencies.
- **Scalability**: Simplifies the main project by offloading general-purpose code to a dedicated library.

### Drawbacks

- **Initial Setup**: Extracting and packaging utilities requires initial effort.
- **Dependency Management**: Adds a dependency to the main project, which must be managed and updated.
- **Versioning Overhead**: Changes to the library must be versioned and published, which adds complexity to the development workflow.

## Alternatives Considered

1. **Keep Utilities in the Main Project**:
    - Rejected because it limits reusability and increases maintenance complexity.

2. **Duplicate Utilities Across Projects**:
    - Rejected because it leads to inconsistencies and higher maintenance overhead.

3. **Inline Utilities in Specific Use Cases**:
    - Rejected because it reduces modularity and makes testing and reuse harder.

## Implementation Plan

1. **Extract Code**:
    - Move existing utility classes from the main project to a new Kotlin project.

2. **Set Up Build and Publishing**:
    - Configure Gradle or Maven for the library project.
    - Publish the library to a suitable repository.

3. **Refactor Main Project**:
    - Replace references to old utility code with imports from the new library.

4. **Testing**:
    - Ensure utilities function as expected in their new context.
    - Write tests for any new or updated functionality.

5. **Documentation**:
    - Document how to use the library and its utilities.
    - Update the main project documentation to reflect the changes.

## Conclusion

Exporting utilities to a separate Kotlin library improves reusability, maintainability, and modularity. While the initial setup requires effort, the long-term benefits of scalability and consistency outweigh the drawbacks. This decision aligns with best practices for creating reusable, maintainable software components.
