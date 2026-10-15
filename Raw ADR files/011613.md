# 4. Image Processing Strategy: Custom Long Exposure Image Creation

Date: 2024-04-29

## Status

Proposed

## Context

The project involves creating long exposure images from videos by cutting the videos into frames and processing these frames. Several options were considered for implementing this feature, each with its own set of advantages and drawbacks. Given the time constraints of 16 hours for the first issue and the need for a flexible yet performant solution, a decision needs to be made on the approach to take.

## Considered Options

* Using external tools like ImageMagick
* Using libraries like OpenCV
* Implementing a custom method for image creation
* Using shaders to leverage GPU power
* Using WebAssembly for client-side processing

## Decision

I have chosen to implement a custom method for creating long exposure images due to its flexibility and feasibility within the given time constraints. This method allows for a tailored solution that meets the project's specific requirements without overshooting the allocated development time.

## Consequences

### Using External Tools like ImageMagick

**Pros:**

- Powerful and versatile tool for image manipulation.
- Wide range of features and support for various image formats.
- Extensive documentation and community support.

**Cons:**

- Steep learning curve due to unfamiliarity.
- Overhead of integrating and managing external tools.
- Potential performance overhead due to external process calls.

### Using Libraries like OpenCV

**Pros:**

- High performance with optimized algorithms for image processing.
- Extensive functionality for computer vision tasks.
- Active community and comprehensive documentation.

**Cons:**

- Requires learning and understanding OpenCV's API.
- Potentially more complex than needed for the current scope.
- May introduce dependencies that need to be managed.
- Library is not that well supported for Rust, so calling it as external application would be needed.

### Implementing a Custom Method for Image Creation

**Pros:**

- Full control over the implementation and optimization.
- Flexibility to adapt to specific project requirements.
- Feasible within the 16-hour time constraint for the first issue.

**Cons:**

- May require more initial development time compared to using existing tools.
- Potential for reinventing the wheel for common image processing tasks.
- Performance may not be as optimized as specialized libraries.

### Using Shaders to Leverage GPU Power

**Pros:**

- Significantly faster processing by leveraging GPU power.
- Improved user experience with faster response times.
- Potential for high performance with complex image processing tasks.

**Cons:**

- Requires knowledge of shader programming, which I currently lack.
- Steep learning curve and additional development time needed.
- Complexity in integrating shader-based processing with existing codebase.

### Using WebAssembly for Client-side Processing

**Pros:**

- Offloads processing to the client's machine, reducing server load and costs.
- High performance due to near-native execution speed.
- Can enhance scalability by distributing workload to clients.

**Cons:**

- Requires learning and implementing WebAssembly.
- Additional complexity in setting up and managing client-side processing.
- Security considerations with running code on client machines.

## Conclusion

I have chosen to implement a custom method for creating long exposure images. This approach offers the flexibility needed to meet specific project requirements and is achievable within the given time constraints. While other options like using OpenCV or shaders offer performance benefits, they require additional learning and complexity that are not feasible for the initial implementation phase. Future iterations may explore GPU acceleration or WebAssembly to further enhance performance and scalability.
