# TSDR-1010 Code Generation

## Status

Accepted

## Context

We want code generation for (one will be source, others derived from):
- DB Model / Chart / Diagram
- DB Schema
- DB Migrations
- API Model / DB Communication (should include basic validation)
- API controllers / handlers
- API Validation
- API Routing
- OpenAPI 3 (Swagger 1 and 2 are previous versions of OpenAPI) (API Documentation)
- Web Client use of API
- Web Client Validation
- Mobile Client use of API
- Mobile Client Validation
- SDKs for other languages for our clients

Code generation should allow for:
- Overrides when we want our own code.
- Pagination
- Filters

## Decision

Don't do it.
https://threedots.tech/post/common-anti-patterns-in-go-web-applications/

## Why

I've done a cursory look at many of all the generators out at the moment. There
isn't anything that covers all we want to generate, or even
generate code the way we would want it. I gave a hard look at goa. Goa's new
user experience was painful. I'd be willing to try it again and perhaps it would
go better now that I have more experience. sqlc was givin even more time. sqlc
drops the ball on filters and pagination. We could dig deep and fix. We could
generate our own templates. I hate the standard library template package. I'm not
going to marry my self to it. sqlc's code seems bloated. Trying to be everything
to everyone. flags for every version of outputted code. Some of the flags produce
broken code.Doesn't seem sustainable.

Code generation feels like an uphill battle. I get the impression they are
like ORMs. Good at 80% but fight like hell on the 20%. The brochure is nice but
gets in way when you try to do something interesting. Just frustrating. 

## Consequences

We will be on our own to keep code in sync.

## Short List of Options

- [sqlc](https://sqlc.dev/)
  - Source: SQL
  - Generates: API Model / DB Communication
- [Goa](https://github.com/goadesign/goa)
  - Source: DSL
  - Generates:
    - Go API
    - OpenAPI Spec
  - **TRIED** may give another chance.
- [oapi-codegen](https://github.com/oapi-codegen/oapi-codegen)
  - Source: OpenAPI specs
  - Generates:
    - API Clients
  - developer was on fallthrough podcast
- [oto](https://github.com/pacedotdev/oto/tree/main/otohttp) by Mat Ryer 
  - Source: GO code (structs)
  - Generates:
    - API controllers / handlers
    - API Validation
    - API Routing
  - **liked this** can generate anything I want from templates. Simple code but
    but would be heavy lift of generating many of our own templates.

## Other Possible Options

- [awesome-go](https://github.com/avelino/awesome-go?tab=readme-ov-file#go-generate-tools)
- [reddit confused_by_the_openapi_options](https://www.reddit.com/r/golang/comments/1gmhz08/confused_by_the_openapi_options_for_go/)
- [reddit](https://www.reddit.com/r/golang/comments/1avsog1/go_openapi_codegen/)

- Code → Spec
  - Astra by
  - (Gin-only, Echo & Fiber WIP as of 2024-02-22)
  - Fuego (built with go 1.22 uses generics and standard http started end of 2023)
  - [Gleece](https://github.com/gopher-fleece/gleece)
    - Code -> Code + Spec
    - Generates routers for Gin, Echo v4, Gorilla Mux, Chi v5, and Fiber v2 routers. Probably I could add standard library router.
    - Generates HTTP routing generation, authorization enforcement, payload validation, error handling, and OpenAPI v3 specification generation
    - https://zuplo.com/blog/2025/03/04/holistic-view-of-apis
  - [Huma](https://huma.rocks/)
    - built on top of chi
    - generates spec from the go code. Essentially you write a chi server and
      Huma generates the openapi spec from it.
  - Tonic
  - libopenapi
  - kin-openapi (seems semi-abandoned as of 2024-02-22)
  - go restful
    - generates open api spec from code.
- Spec → SDK
  - https://packagemain.tech/p/practical-openapi-in-golang **SHORT LIST TO TRY**
  - [Laurence de Jong](https://ldej.nl/post/generating-go-from-openapi-3/)
  - oapi-codegen
    doesn't do OpenAPI 3?
  - ogen **TRIED**
  - microsoft/kiota
- DSL → Spec + Code
- Unknown if Spec or SDK first
  - [Prism](https://stoplight.io/open-source/prism)
    - use for testing?
  - [swaggest - rest](https://github.com/swaggest/rest)
  - [swaggest - openapi-go](https://github.com/swaggest/openapi-go)

## sqlc Notes

- [sql-gen-go](https://github.com/sqlc-dev/sqlc-gen-go)
  - a plugin but more of an example as it is just a pull of the code from sqlc.
- [sqlc-gen-go-server](https://github.com/walterwanderley/sqlc-gen-go-server/)
  - Source: SQL
  - Generates:
    - API Model / DB Communication (should include basic validation)
    - API controllers / handlers
    - API Validation
    - API Routing
  - This is a sqlc plugin. Need to test how code is different from sqlc-http. Same developer of both projects.
  - fork of [sql-gen-go](https://github.com/sqlc-dev/sqlc-gen-go) but also does
    server code.
- [sqlc-http](https://github.com/walterwanderley/sqlc-http)
  - Source: SQL
  - Generates:
    - API Model / DB Communication (should include basic validation)
    - API controllers / handlers
    - API Validation
    - API Routing
  - Seems to pretty much generate same code as sqlc-gen-go-server but without
    being a plugin.
- https://www.reddit.com/r/golang/comments/1aiooft/sqlc_dynamic_queries_with_pagination_and_filters/
- https://www.reddit.com/r/golang/comments/183292y/best_practices_with_sqlc_and_dynamic_filters/?share_id=fTJsRkD8PPGBA2jm4VXhD&utm_medium=android_app&utm_name=androidcss&utm_source=share&utm_term=1


## Not an Option

- [OpenAPI Generator](https://openapi-generator.tech/)
  - Source: OpenAPI 3
  - Generates:
    - API
    - Clients
    - PostgreSQL Schema (beta)
  - seems to be specifically set up to create many generators
  - written in **Java**
  - fork of swagger-codegen.
  - If we have to write our own generators we don't want to be writing in a different language.
- [speakeasy](https://www.speakeasy.com/docs/languages/golang/oss-comparison-go)
  - trying to sell speakeasy
  - generates sdks
- [swagger-codegen](https://github.com/swagger-api/swagger-codegen)
  - written in **Java** and Mustache??
  - If we have to write our own generators we don't want to be writing in a different language.
- swaggo/swag (OAS3 Beta)
  - **TRIED** supported frameworks:
  - gin, echo, buffalo, net/http (standard library), gorilla/mux, go-chi/chi,
    flamingo, fiber, atreugo, hertz

