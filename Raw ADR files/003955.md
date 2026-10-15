# ADR 005: Return to Gemini in Chatbot After Model Version Fix

## Status
Accepted

## Date
2025-12-14

## Context
The chatbot implementation was previously experiencing issues with the Gemini model integration. The core problem was identified as an incorrect model version specification that was causing operational failures in the RAG (Retrieval Augmented Generation) system. During this period, alternative approaches may have been considered or temporarily implemented while the issue was being diagnosed and resolved.

## Decision
We have decided to return to using Gemini as the primary LLM for the chatbot after successfully fixing the model version issue. The correct model version has been identified and properly configured, resolving the previous operational problems.

## Details of Fix
- Identified the correct Gemini model version to use
- Updated the model configuration in the backend services
- Verified that the RAG system now functions properly with the correct model version
- Tested query and selection-based interactions to ensure they work as expected

## Alternatives Considered
1. Switch to a different LLM provider permanently
2. Continue using temporary workaround solutions
3. Implement custom model version handling

## Consequences
### Positive
- Restores the originally intended architecture with Gemini as the primary LLM
- Maintains consistency with initial project design
- Leverages the specific features and optimizations of the Gemini model
- Maintains performance characteristics expected by users

### Negative
- Had to invest time in debugging the model version issue
- Temporary disruption to chatbot functionality during the fix period

### Neutral
- Configuration remains specific to the Gemini API
- Monitoring for potential future model version issues is necessary

## Validation
- All API endpoints (`/api/query`, `/api/selection`, `/api/health`) tested successfully
- RAG functionality verified with actual textbook content
- Integration with Qdrant vector database confirmed working
- End-to-end chatbot interaction functionality validated

## Team Agreement
This decision has been validated through testing and is now the established approach for the chatbot's LLM integration.