# 2. Choose GitPython for Git Repository Management

Date: 2025-04-08

## Status

Accepted

## Context

We are developing a Python-based CLI tool, venture, that will help manage
multiple software projects. The tool will provide commands such as create,
remove, workon, and list, allowing users to easily navigate between
projects.

One key feature is the ability to automatically clone a Git repository
when the user runs venture workon <git-repo>. The decision on how to
handle Git repository management is critical, especially considering
how we want the tool to behave when dealing with SSH and HTTPS-based Git
URLs.

The options considered were:

Using subprocess to call Git commands externally (via the command line).
Using a pure-Python Git library, such as GitPython or Dulwich.
Implementing our own minimal Git handling.

## Decision

We have chosen to use GitPython for handling Git operations in the venture
project. This decision was made after considering the trade-offs between ease
of use, reliability, and performance.

GitPython provides the following advantages:

Pythonic API: It abstracts the complexities of interacting with Git, making
the codebase easier to maintain and understand.
Full Git support: It supports both HTTPS and SSH Git URLs seamlessly.
Well-maintained: GitPython is widely used in the Python community, which means
it's likely to receive updates and bug fixes.
No need for Git installation on the system for non-SSH-based repositories
(HTTPS-based cloning).

## Consequences

* Git installation required: For SSH-based clones, Git must be installed on the
  system, as GitPython internally relies on the git binary for SSH operations.
* External dependencies: GitPython introduces one additional external
  dependency (GitPython itself), which adds a minimal overhead but provides a
  high-level abstraction for handling Git repositories.
* Ease of integration: GitPython allows us to integrate Git operations directly
  into the Python code without needing to rely on subprocess calls or shell
  commands, leading to cleaner and more maintainable code.
* Long-term maintainability: Using GitPython will likely reduce the need for
  custom implementations of Git-related operations, helping to future-proof
  the venture project as the repository management grows.
