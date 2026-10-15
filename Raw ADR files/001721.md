# 3. python runnable selection

Date: 2024-05-07

## Status

Accepted

## Context

To allow different installations of Python in the same machine, we can use a tool called `pyenv`.

The virtual environment is a self-contained directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages.
The main advantage of using a virtual environment is that it allows you to manage dependencies for different projects separately to avoid **conflicts** between dependencies.

We don't need to use it when we are using Docker, but it's a good practice to use it when we are developing locally.

There are different tools to create a virtual environment, such as `venv`, `virtualenv`, `pipenv`.

## venv

### Pros:
- Lightweight and included in Python standard library.
- Simple to use and straightforward setup process.
- Follows the Python Enhancement Proposal (PEP) 405 standard.
- Supports Python 3.3 and later versions.

### Cons:
- Limited to the Python version installed on the system.
- Global installation requires administrative privileges.
- No built-in support for managing multiple virtual environments or dependency resolution.
- Dependency tracking is limited to packages installed within the virtual environment.

---

## virtualenv

### Pros:
- Provides more flexibility in choosing Python versions.
- Supports Python 2 and Python 3 versions.
- Can be installed globally or per-user without administrative privileges.
- Integrates with various tools and frameworks.

### Cons:
- Requires installing additional software (although it's a common practice).
- Dependency management and tracking are manual.
- No built-in support for managing multiple virtual environments or dependency resolution.

---

## pipenv

### Pros:
- Combines package management (pip) and virtual environment management (virtualenv).
- Simplifies dependency management with a `Pipfile` and `Pipfile.lock`.
- Automatically creates and manages virtual environments.
- Supports dependency resolution and deterministic builds.

### Cons:
- Adds complexity compared to basic virtual environment tools.
- Slower initialization and installation times due to dependency resolution.
- Dependency management relies heavily on the `pipenv` tool, which might not be suitable for all projects.

---

## Virtualenvwrapper

### Pros:
- Provides a set of extensions to enhance virtualenv functionality.
- Simplifies virtual environment management with commands like `mkvirtualenv` and `workon`.
- Supports managing multiple virtual environments with ease.
- Integrates well with shell environments for improved productivity.

### Cons:
- Adds a layer of abstraction, which might be unnecessary for simple projects.
- Relies on the `virtualenv` tool for creating virtual environments.
- Requires additional installation and setup compared to basic virtual environment tools.
- Dependency management and tracking are manual.



## Decision

The simplest one is `venv`, which is included in the Python standard library. See README.md for more information.

## Consequences

Using `venv` with `pyenv` and a different packager manager has an isolation on the Python version and the dependencies.
It's a good practice to use it when we are developing locally,
but it creates a level of complexity to set up that other alternatives as`virtualenv` .
