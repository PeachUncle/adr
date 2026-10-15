# 8. Stream Processing

Updated: 2024-06-02

## Status

Accepted

## Context

In our project, we are building a data processing pipeline that involves transferring data between different
components of our system. These components include data producers, a message broker, and data consumers.
The data being transferred includes user-generated content, system logs, and metadata, which is primarily structured as
key-value pairs. Two data serialization formats were considered: JSON and Apache Avro.
JSON is a widely-used, text-based format known for its human readability and ease of use, while Apache Avro is a binary
format known for its compactness, schema evolution support, and fast serialization/deserialization.

## Decision

After evaluating both options, we decided to use JSON for the following reasons:

Human Readability: JSON is human-readable, which makes it easier for developers to inspect and debug data during development and testing. This is particularly beneficial for a study project where learning and understanding the data flow is crucial.
Ease of Use: JSON is straightforward to use with many programming languages, requiring minimal additional setup. Most programming languages have built-in support for JSON or offer libraries that simplify JSON parsing and generation.
Flexibility: JSON does not require a predefined schema, allowing us to iterate quickly and make changes to the data structure without modifying schema definitions.
Tooling and Ecosystem: JSON has a vast ecosystem with extensive tool support, including validators, formatters, and visualization tools, which can enhance productivity and simplify development.
Interoperability: JSON is a ubiquitous format used in many web APIs and services, ensuring compatibility and easy integration with external systems if needed.

## Consequences

Performance: JSON, being a text-based format, is generally less efficient in terms of serialization/deserialization speed and storage size compared to Avro. This could impact the performance of our data processing pipeline, especially with large volumes of data.
Lack of Schema Enforcement: Without a schema, there's a risk of inconsistencies and errors in the data structure, as JSON does not enforce data types or required fields. This could lead to data integrity issues if not carefully managed.
Larger Data Size: JSON tends to be larger in size compared to binary formats like Avro, which could result in higher storage costs and increased network bandwidth usage.
Potential Scalability Limitations: As the project scales, the inefficiencies associated with JSON might become more pronounced, potentially necessitating a reconsideration of the serialization format in the future.
By choosing JSON, we prioritize ease of development, readability, and flexibility, which align well with the goals of our study project. However, we remain aware of the trade-offs, particularly regarding performance and scalability, and are prepared to revisit this decision if the project's requirements evolve.