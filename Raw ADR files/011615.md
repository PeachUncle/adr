# 5. Movie File Processing and Storage Strategy

Date: 2024-06-01

## Status

Accepted

## Context

The project involves processing movie files uploaded by users, splitting them into frames, and creating long exposure images. The processed frames should be viewable in the user interface. Several options were considered for handling the movie files, each with its own advantages and drawbacks. For this project, the chosen approach needs to balance ease of implementation, performance, and potential security concerns.

## Considered Options

* Saving files in a cloud service (AWS, GCP)
* Storing files locally on the server
* Processing files entirely on the user’s machine

## Decision

I have chosen to save the movie files locally on the server. This approach simplifies implementation, and provides acceptable performance within the context of this uni project.

## Consequences

### Saving Files in a Cloud Service (AWS, GCP)

**Pros:**

- Scalable storage solutions with robust infrastructure.
- High availability and redundancy.
- Managed services with various options for data processing and storage.

**Cons:**

- Additional cost for storage and data transfer.
- Increased complexity in setting up and managing cloud services.
- Potential latency issues due to network transfer times.
- Requires integration with cloud APIs and handling authentication.

### Storing Files Locally on the Server

**Pros:**

- Simplified implementation without needing to integrate external services.
- Immediate access to files with minimal latency.
- No additional costs associated with cloud storage.
- Easier debugging and monitoring within a local environment.

**Cons:**

- Limited by server storage capacity.
- Single point of failure without redundancy.
- Requires robust server management to handle load and storage.
- Hurts the lifetime of my SSD :-/

### Processing Files Entirely on the User’s Machine

**Pros:**

- Offloads processing to the client, reducing server load.
- Can potentially reduce server costs if processing is entirely client-side.
- Leverages the user’s hardware for potentially faster processing.

**Cons:**

- Performance depends heavily on the user’s machine capabilities.
- Increased complexity in implementing client-side video processing.
- Potential need for technologies like WebAssembly, adding to the learning curve.
- User’s RAM and CPU could become bottlenecks, leading to poor performance.

## Security Considerations

- **UUID Assignment**: Movies are assigned a random UUID to prevent easy guessing of file names.
- **Image Serving**: Frames are served via `img src=` tags, which could be a potential security flaw if URLs are guessed or intercepted.
- **Data Privacy**: For higher security needs, further mitigation steps such as secure tokens, authenticated sessions, or encrypted storage would be necessary.

## Conclusion

Storing movie files locally on the server was chosen for this university project due to its simplicity, cost-effectiveness, and ease of implementation. While this approach has some limitations in terms of scalability and redundancy, it meets the project’s requirements within the given constraints. Future iterations might explore cloud storage or client-side processing as the project scales or if higher security and performance are demanded.
