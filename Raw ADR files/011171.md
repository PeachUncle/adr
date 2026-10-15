# ADR 002: Selection of pre-commit as a tool for automated code validation

**Date:** 2024-09-23

## Context
In our microservices project, where various services are being developed, maintaining code quality and consistency is crucial for ensuring ease of development and readability. To guarantee that all code changes comply with established standards, we need a tool that automates the code validation process before changes are committed to the repository.

## Decision
We have chosen **pre-commit** as the tool for automated code validation in the project.

### Benefits of pre-commit:
1. **Automated code checking**  
   The tool will run linters, formatters, and other tests on the code before each commit.
2. **Automatic formatting**  
   Using tools like Black (for Python), Ruff, or djLint, code will be formatted according to accepted standards automatically.
3. **Ease of installation and configuration**  
   Pre-commit is straightforward to configure and integrate into existing repositories.
4. **Modularity and extensibility**  
   Hooks can be added or modified to suit project-specific needs, including validation for other languages or custom tools.
5. **Protection against unwanted changes**  
   Pre-commit helps identify undesirable changes, such as accidentally added large files or YAML syntax errors.

## Justification
1. **Continuous code quality**  
   Automated code validation ensures early error detection, improving overall quality and reducing the risk of introducing defects.
2. **Process automation**  
   Pre-commit eliminates the need for manual checks, increasing efficiency.
3. **Code consistency**  
   Tools like Black and Ruff ensure consistent formatting across all microservices (e.g., `accounts`, `visits`).
4. **Minimized human error**  
   Automating formatting and validation reduces the risk of mistakes in these processes.

## Consequences
1. **Initial setup effort**  
   Setting up pre-commit hooks requires an initial time investment but is a one-time task.
2. **Mandatory adherence to standards**  
   Code will not be committed to the repository until all validations pass, requiring team compliance.
3. **Potentially longer commit times**  
   For large projects, running pre-commit hooks might slightly increase commit times. However, the benefits outweigh this minor drawback.

## Alternatives
1. **Manual linter and formatter execution**  
   This approach is error-prone and relies on developers remembering to run tools before committing.
2. **Using CI/CD tools exclusively**  
   Relying on tools like Jenkins or GitHub Actions to validate code after committing delays error detection and can result in more time-consuming fixes.

## Conclusion
Pre-commit ensures automated code validation at the local commit level, enhancing code quality, consistency across the project, and team productivity.
