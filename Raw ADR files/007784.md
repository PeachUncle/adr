# ADR: Image Processing Workflow for Copper Print Gallery

## Date
2024-07-27 (Updated: 2024-07-28)

## Status
Proposed

## Context
The Copper Print Gallery system needs to handle image uploads, process these images into various versions, and manage the results. This process involves interaction between the Content Management Service and the Image Processing Service, and needs to be efficient, scalable, and error-resistant.

## Decision
We have decided on the following workflow for image processing:

1. Upload Initiation:
    - The Content Management Service receives the image upload request.
    - It generates a unique ID for the image.
    - It stores the original image in temporary storage.
    - It creates a database entry for the image with initial metadata.

2. Processing Request:
    - The Content Management Service sends an asynchronous processing request to the Image Processing Service.
    - This request includes the image ID and a reference to the original image in temporary storage.

3. Acknowledgment:
    - The Image Processing Service immediately returns an acknowledgment, confirming receipt of the processing request.

4. Asynchronous Processing:
    - The Image Processing Service processes the image, creating various versions as defined in the system configuration.
    - It implements internal retry logic for transient failures.

5. Result Communication:
    - Upon successful completion, the Image Processing Service sends a callback to a predefined endpoint on the Content Management Service.
    - This callback includes:
        - The image ID
        - Details of all processed versions (including their specific version IDs)
        - Extracted EXIF data
        - Any processing metadata (e.g., processing time, applied operations)

6. Metadata Update:
    - The Content Management Service updates its database with the received information.
    - It moves the original image from temporary to permanent storage or discards it based on configured retention policy.
    - It marks the processing job as complete.

7. Error Handling:
    - If processing ultimately fails after internal retries, the Image Processing Service sends an error callback.
    - The error callback includes the image ID and detailed error information.
    - The Content Management Service handles this by updating the image status.
    - If retry is deemed necessary, the Content Management Service can initiate a new processing request using the original image in temporary storage.

## Consequences

### Positive
- Asynchronous processing allows for better scalability and responsiveness.
- Clear separation of concerns between content management and image processing.
- Robust error handling with possibility for retries.
- Temporary storage of original images enables recovery from processing failures.

### Negative
- Increased complexity in managing asynchronous workflows.
- Need for temporary storage management and cleanup processes.
- Potential for increased storage usage due to keeping original images temporarily.

### Risks
- Temporary storage could grow large if not managed properly.
- Need to ensure secure handling of images in temporary storage.

## Implementation Notes
- Implement a cleanup process for temporary storage to remove successfully processed or excessively old images.
- Ensure proper error logging and monitoring for the entire workflow.
- Consider implementing a maximum retry limit to prevent infinite processing attempts for problematic images.
- Implement secure access controls for the temporary storage to prevent unauthorized access to original images.

## Related Decisions
- Image ID Assignment and Versioning
- Definition of Image Version Names and Properties for Copper Print Gallery
- Frontend Responsive Image Implementation Strategy

## References
- Asynchronous Request-Reply Pattern: [Microsoft Azure Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/patterns/async-request-reply)
- Handling Long-Running Jobs in Web APIs: [CodeMaze Blog](https://code-maze.com/aspnetcore-handling-long-running-tasks/)
- Best Practices for Background Jobs: [RabbitMQ Documentation](https://www.rabbitmq.com/tutorials/tutorial-two-python.html)
- Temporary File Management in Python: [Python Documentation](https://docs.python.org/3/library/tempfile.html)
- Error Handling Best Practices: [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)