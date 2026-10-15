# 4. Separate admin and public API endpoints

Date: 2019-10-29

## Status

Accepted

## Context

This application has two different clients:

- Frontend application that needs course catalog, authentication,
  cart and order information
- Backend application needs to manage the catalog, being able to
  modify courses, options, instructors, etc

Naturally, those use cases share a lot of business logic when it comes
to the actual operations they need to perform. But they also differ
in terms of input/output and authentication/authorization.

## Decision

In order to facilitate application maintenance and collaboration, the
endpoints available to the two very different use cases are in the
same codebase. This prevents us from having to share a common module
or library, containing business logic, between separate applications.

This requires a clear separation between what is a public endpoint,
and what is an administration endpoint. We've decided to use a
simplistic approach: namespaces.

When inspecting the codebase, you'll see that the source files are
organized in modules:

    src/
    ├── Course
    │   ├── Admin
    │   │   ├── Input
    │   │   │   └── CourseRequest
    │   │   ├── Output
    │   │   │   └── CourseOutput
    │   │   ├── CreateCourse
    │   │   ├── RemoveCourse
    │   ├── Api
    │   │   ├── Input
    │   │   │   └── CourseRequest
    │   │   ├── Output
    │   │   │   └── CourseOutput
    │   │   └── SearchCourses
    ├── Instructor
    │   ├── Admin
    │   │   ├── Input
    │   │   │   └── InstructorRequest
    │   │   ├── Output
    │   │   │   └── InstructorOutput
    │   │   ├── CreateInstructor
    │   │   ├── RemoveInstructor
    │   ├── Api
    │   │   ├── Input
    │   │   │   └── InstructorRequest
    │   │   ├── Output
    │   │   │   └── InstructorOutput
    │   │   └── SearchInstructors

All of the endpoint-specific implementations are contained within
the `Admin` or `Api` namespaces. The objects with names beginning
with verbs are actions. The `Input` and `Output` namespaces are
responsible, respectively, for handling request parsing and
response formatting.

## Consequences

The codebase is bigger and more complex. We also have to handle
separate authentication and authorization mechanisms for each
endpoint, which can make our in-app firewall more verbose.
