# ADR-009: AI Component Testing Strategy

**Date:** 2025-09-06

**Status:** Proposed

## Context

The PlumbingPOC application relies on two critical AI components powered by OpenAI's GPT-4:
1. **Follow-up Question Generation** (`getGptFollowUp` in `requestController.js`): Determines if additional clarifying questions are needed based on user answers.
2. **Request Triage Analysis** (`triageRequest` in `triageController.js`): Analyzes new requests to provide priority and profitability scores.

These components are essential to the application's value proposition but introduce testing challenges:
- External API dependency on OpenAI
- Variable response times and costs
- Non-deterministic outputs
- Need to test both success and error scenarios

The existing test suite (as documented in `tests/README.md`) lacks coverage for these AI components, which is identified as a gap in the "Next Steps" section.

## Decision

We will implement **mocked AI component testing** using the following strategy:

1. **Mocking Approach**: Use Vitest's mocking capabilities to intercept OpenAI API calls
2. **Contract-Based Testing**: Test against the established JSON response contracts
3. **Scenario Coverage**: Test success paths, error handling, and edge cases
4. **Integration with Existing Suite**: Add to the current test pyramid structure

## Implementation Details

### Mock Strategy
- Mock the OpenAI client to return predetermined JSON responses
- Test the application's handling of various AI response scenarios
- Validate that the application correctly parses and processes AI outputs

### Test Scenarios
**Follow-up Questions:**
- Clear answers requiring no follow-up
- Ambiguous answers requiring specific questions
- Invalid JSON responses (graceful degradation)
- API errors (timeout, rate limits)

**Triage Analysis:**
- Standard request with expected priority/profitability scores
- Emergency request with high priority
- Invalid JSON responses
- Database update failures after AI processing

### Test Structure
```
tests/unit/ai/
├── openai-integration.test.ts    # Mocked OpenAI API tests
└── ai-contracts.test.ts          # Contract validation tests
```

## Consequences

**Pros:**
- **Deterministic Testing**: Eliminates variability from live AI calls
- **Cost Control**: No API costs during testing
- **Fast Execution**: Mocked tests run quickly
- **Reliable CI/CD**: Tests don't depend on external services
- **Contract Validation**: Ensures application handles AI responses correctly

**Cons:**
- **Limited Real-World Coverage**: Doesn't test actual AI behavior
- **Maintenance Overhead**: Mocks must be updated if AI contracts change
- **False Confidence**: Passing tests don't guarantee real AI performance

**Risks:**
- **Contract Drift**: If AI prompts change, mocks may become outdated
- **Mitigation**: Include integration tests with real AI calls in staging environment

## Alternatives Considered

1. **Real API Calls in Tests**: Rejected due to cost, latency, and non-determinism
2. **Self-Hosted AI Models**: Rejected due to infrastructure complexity
3. **No AI Testing**: Rejected as it leaves critical components untested

## Related Decisions

- ADR-002: Choice of Primary AI Provider (OpenAI)
- ADR-003: Choice of Backend API Framework (Express/Node)
- ADR-007: Choice of Data Validation Library (Zod for contracts)
