# [ADR-TECH-001] Language and Runtime Selection

## Context and Problem Statement
We need to select the primary programming language and runtime environment for the backend services Control Plane.
This decision is governed by **Rule [CC-DEV-001]** (AI-First Development).

### Decision Drivers
* **AI Code Generation Accuracy**: Code must be generated reliably and correctly by AI agents.
* **AWS Integration**: First-class support in AWS Lambda and SDKs (Boto3).
* **Execution Performance**: Cold start limits and runtime overhead.
* **Ecosystem Maturity**: Availability of libraries (PowerTools) to reduce custom code.

## Considered Options
* **Python 3.12+** (with Pydantic/PowerTools)
* **Rust** (AWS Lambda Rust Runtime)
* **TypeScript** (Node.js 20.x)
* **Go** (Golang 1.21+)

## Decision Outcome
**Chosen Option**: **Python 3.12+**

**Justification**:
While **Rust** provides superior runtime efficiency (memory/CPU) and is ideal for "Serverless First" from a resource perspective, we select **Python 3.12+** for the following reasons in an AI-driven development context:
1.  **LLM Proficiency**: Large Language Models have significantly more training data for Python/Boto3/Lambda patterns than Rust/AWS-SDK-Rust. This maximizes the success rate of AI-generated code.
2.  **Ecosystem Support**: `aws-lambda-powertools-python` and `boto3` are the de-facto standards for AWS, offering richer features and faster updates than their Rust counterparts.
3.  **Hybrid Approach**: The AI Agent can easily refactor individual performance-critical Lambda functions to **Rust** if observability data indicates a bottleneck, but the default should be the language where the AI is most competent (Python).

### Positive Consequences
* **High Quality Generation**: AI produces idiomatic, correct code with high probability.
* **Rich Ecosystem**: Immediate access to mature libraries.

### Negative Consequences
* **Runtime Overhead**: Higher memory/CPU usage than Rust.
* **Cold Starts**: Slower than compiled binaries (mitigated by Provisioned Concurrency or future optimization to Rust).
