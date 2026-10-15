# 0004 - Use xUnit for unit testing

Date: 2026-01-03

## Status

Accepted

## Context

This repository needs a consistent, modern unit testing framework for automated tests run locally and in CI. The solution targets .NET 10 and uses modern build pipelines. We evaluated common .NET test frameworks to pick a default that fits our style and CI workflows.

## Decision

We will use xUnit as the repository's primary unit testing framework.

## Decision Drivers

- Good .NET Core / .NET 10 integration and first-class support for `dotnet test`.
- Simple, modern API that encourages per-test constructor setup and `IDisposable` cleanup instead of attribute-based setup/teardown.
- Built-in support for async tests (`async Task`) and flexible parameterized tests (`[Theory]` + `[InlineData]`, `[MemberData]`).
- Support for fixtures (`IClassFixture`, `ICollectionFixture`) to manage shared context clearly.
- Default parallel test execution which speeds up test runs in CI.

## Alternatives Considered

- NUnit: mature and feature rich; has many attributes and features, but xUnit's fixture model and constructor-based setup are preferred.
- MSTest: official Microsoft offering; adequate for simple scenarios, but less modern API and fewer extensibility points compared to xUnit.

## Consequences

- Tests will be authored using xUnit attributes and patterns (`[Fact]`, `[Theory]`, fixtures).  
- CI pipeline and local development should install the `xunit` runner packages where required and invoke tests with `dotnet test`.  
- Developers familiar with NUnit or MSTest may need to adapt to xUnit idioms, but conversion is straightforward.

## Implementation Notes

- Add a test project (for example `tests/HealthReport.Application.Tests`) and reference `xunit`, `xunit.runner.visualstudio` and any assertion/utility packages as needed.  
- Use `dotnet test` in CI to run tests.  
- Encourage use of `IClassFixture` / `ICollectionFixture` for shared expensive resources to keep tests fast and deterministic.

