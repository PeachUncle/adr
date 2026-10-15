# 1. Programming Language: Rust

Date: 2024-04-29

## Status

Proposed

## Context

The backend system requires the robust handling of movie file uploads, followed by a process that splits the movie into
frames
and composites them to create "long exposure" style images. The language chosen for this system needs to efficiently
manage file I/O operations, invoke external utilities like FFmpeg, and ensure performance and reliability.

## Considered Options

* TypeScript
* Rust
* Kotlin
* Python

## Decision

I am considering Rust for backend development to leverage its memory safety, concurrency control, and efficient
execution. Rust's ownership model and compile time guarantees could potentially reduce bugs and runtime failures,
especially in the file manipulation and processing tasks which are (currently) central to the application. The proposed
approach is to:

* Develop a prototype in Rust for the file upload and processing functionality.
* Evaluate the development experience in Rust, especially concerning the learning curve and development speed.
  Compare the prototype's performance and reliability with the solutions of others or prototypes in other languages,
  like TypeScript.
* This evaluation period will help determine if Rust's benefits outweigh the costs for the projects specific needs.

## Consequences

### TypeScript

**Pros:**

- **Rich Ecosystem**: Leverages the vast npm ecosystem, with countless libraries and tools available for use.
- **Type Safety**: Introduces static typing to JavaScript, enabling better tooling, improved performance, and increased
  developer productivity through early error detection.
- **Community and Support**: Backed by Microsoft and a strong community, TypeScript receives continuous improvements and
  support.

**Cons:**

- **Runtime Errors**: Type safety does not eliminate the possibility of runtime errors, especially when interacting with
  plain JavaScript libraries.
- **Performance**: TypeScript's performance is not as efficient as Rust, especially in CPU bound tasks.

### Rust

**Pros:**

- **Performance**: Rust offers memory safety without a garbage collector, enabling high performance similar to C and
  C++.
- **Safety Guarantees**: Features like ownership and borrowing prevent null pointer dereferences and guarantee thread
  safety.
- **Modern Toolchain**: Cargo, Rust's package manager, and build system, provides an excellent out-of-the-box experience
  for managing dependencies and builds.
- **Growing Ecosystem**: While newer, Rust's ecosystem is actively growing and offers many libraries for web development
  like Rocket and Actix.

**Cons:**

- **Steeper Learning Curve**: Rust's strict compiler and concepts like ownership and lifetime can be challenging for
  newcomers.
- **Younger Ecosystem**: Rust's ecosystem is less mature compared to languages like Python or JavaScript, potentially
  requiring more custom code.

### Kotlin

**Pros:**

- **Spring Framework**: With robust support for the Spring Framework, Kotlin benefits from a mature ecosystem for
  enterprise level applications.
- **Familiarity**: Having experience with Kotlin can significantly accelerate development and reduce the learning curve.
- **Interoperability with Java**: Kotlin is fully interoperable with Java, allowing access to the vast array of Java
  libraries and frameworks.
- **Modern Language Features**: Offers modern language features like coroutines for asynchronous programming, extension
  functions, and null safety.

**Cons:**

- **Smaller Community**: The community is smaller compared to languages like Python, which might impact finding
  resources or troubleshooting issues.
- **Kotlin-Specific Libraries**: While the ecosystem is growing, some libraries and tools may still be Kotlin-specific
  and less mature than their Java counterparts.

### Python

**Pros:**

- **Extensive Libraries**: A wealth of libraries for nearly every task imaginable, including Django and Flask for web
  development, and libraries for OpenCV (Image Processing).
- **Rapid Prototyping**: Python's simple and clean syntax makes it an excellent choice for rapid development and
  prototyping.
- **Versatility**: Used in various domains like web development, data science, machine learning, and automation.
- **Community Support**: A large, active community means plenty of documentation, tutorials, and third-party tools.

**Cons:**

- **Performance**: Being an interpreted language, Python may not perform as well as compiled languages for CPU intensive
  tasks.
- **Runtime Type Errors**: Dynamic typing makes type-related errors only detectable at runtime.
- **Hard maintainability**: Python's dynamic nature can make it harder to maintain codebases and refactor code.
