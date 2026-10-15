# Adoption of Problem Details for HTTP APIs Standard for Error Responses

## Decision Group

* TD - Technology Decision
* Proposed | 2024-11-14

## Problem/Issue

APIs across various projects have inconsistent formats for error reporting, leading to challenges in error diagnosis, client-side error handling, and overall API usability. The lack of a standardized error response format complicates integration efforts, increases client-side logic complexity, and impedes clear communication of error conditions.

## Decision

We have decided to adopt the "Problem Details for HTTP APIs" standard, as outlined in RFC 9457, for all API error responses. This decision mandates the use of a standardized, structured format for conveying errors in HTTP response content across all current and future APIs.

## Considered Alternatives

* Custom error response formats tailored to each API
* Use of simple error codes and messages without structured data
* Utilization of existing logging frameworks without standardized client-facing error structures

## Arguments

### Pro

* Consistency: Ensures a uniform approach to error handling across all APIs, facilitating easier consumption and integration.
* Clarity and Usability: Improves the clarity of error responses, making it easier for clients to understand and react to errors.
* Standardization: Aligns with an established Internet standard (RFC 9457), promoting best practices and enhancing interoperability with third-party clients and tools.
* Extensibility: Provides flexibility to include additional, context-specific information in error responses without deviating from the standard format.
* Debugging Efficiency: Aids in quicker diagnosis and resolution of issues by providing detailed, standardized error information.

### Con

* Initial Implementation Effort: Adopting a new standard requires initial effort to update existing APIs and educate developers.
* Overhead for Simple APIs: For APIs with very simple error models, the structured format might introduce unnecessary overhead.
* Potential for Information Overload: Including too much detail in error responses could potentially expose sensitive information or overwhelm clients.

## Related decisions

N/A

## Extends

N/A

## Related requirements

N/A
