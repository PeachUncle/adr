# ADR-010: Multi-LLM Experimental Framework

## Status
Proposed

## Context
The CodeCompass system is initially designed around Claude 3.7 Sonnet, but other AI systems may offer different capabilities, pricing models, and integration approaches. Recent benchmarks such as SWE-bench Verified and TAU-bench provide standardized ways to compare AI performance on software engineering tasks. It's important to distinguish between the LLMs themselves (like Claude 3.7 Sonnet) and the development environments that integrate these models (like Cursor AI, WindsurfAI, and CLIne).

## Decision
We will implement a Multi-LLM Experimental Framework that:

1. Creates an abstraction layer for AI interactions that works across different providers and environments
2. Implements adapter patterns for different environments:
   - Direct LLM APIs (Anthropic Claude, OpenAI GPT)
   - IDE integrations (Cursor AI, WindsurfAI)
   - Command-line tools (Claude Code CLI)
   - Editor extensions (CLIne for VS Code)
3. Provides standardized metrics collection aligned with industry benchmarks:
   - SWE-bench Verified metrics for real-world software issue resolution
   - TAU-bench metrics for agentic tool usage
   - Token usage and response time
   - Cost per operation
4. Includes a configurable testing harness for running identical queries across multiple environments
5. Builds visualization tools for comparing performance across different setups
6. Creates a pluggable architecture allowing users to easily add new LLMs and integration environments
7. Implements A/B testing capabilities to compare different prompt engineering approaches

## Consequences
- **Positive**: Enables objective comparison of different AI-powered coding environments for specific tasks
- **Positive**: Provides flexibility to switch between providers and tools as technology and pricing evolve
- **Positive**: Creates a community-extensible framework for testing new AI tools as they emerge
- **Positive**: Helps identify which types of tasks are best suited to specific environments
- **Negative**: Significantly increases implementation complexity
- **Negative**: Requires maintaining compatibility with multiple APIs and tools that may change
- **Negative**: May distract from optimizing for a single high-quality implementation

## Implementation Approach

The Multi-LLM Experimental Framework would be structured as follows:

1. **Core Abstraction Layer**:
   - Common interfaces for all AI interactions
   - Standardized request/response format
   - Consistent error handling and retry logic

2. **Environment-Specific Adapters**:
   - **LLM API Adapters**:
     - Claude API Adapter (Anthropic)
     - GPT API Adapter (OpenAI)
     - Other LLM providers
   - **IDE Integration Adapters**:
     - Cursor AI Adapter
     - WindsurfAI Adapter
   - **Tool Integration Adapters**:
     - Claude Code CLI Adapter
     - CLIne VS Code Extension Adapter
   - Extensible plugin system for community-contributed adapters

3. **Benchmark Integration**:
   - SWE-bench Verified task execution
   - TAU-bench agent evaluation
   - Custom benchmark creation tools

4. **Testing Harness**:
   - Experiment definition system (YAML or JSON)
   - Identical prompt execution across environments
   - Performance metric collection
   - Result comparison visualization

## Example Experimental Configuration

```yaml
experiment:
  name: "Code Review Performance Test"
  description: "Testing AI performance on reviewing a Python module"
  
  target_file: "./backend/services/payment.py"
  
  environments:
    - name: "claude-direct"
      type: "llm-api"
      provider: "anthropic"
      model: "claude-3.7-sonnet"
      config:
        temperature: 0.7
        max_tokens: 4000
        thinking_mode: "extended"
        thinking_tokens: 10000
    
    - name: "cursor-ide"
      type: "ide-integration"
      base_llm: "claude-3.5-sonnet"  # The underlying LLM
      version: "latest"
      config:
        temperature: 0.7
        max_tokens: 4000
        
    - name: "windsurf-ide"
      type: "ide-integration"
      base_llm: "claude-3.5-sonnet"  # The underlying LLM
      version: "2.1"
      config:
        temperature: 0.7
        max_tokens: 4000
        
    - name: "claude-code-cli"
      type: "cli-tool"
      base_llm: "claude-3.7-sonnet"
      config:
        temperature: 0.7
        max_tokens: 4000
        
    - name: "cline-extension"
      type: "vscode-extension"
      base_llm: "configurable"  # Can use various LLMs
      config:
        default_model: "deepseek"
  
  tasks:
    - name: "code_review"
      prompt: "Please review this payment processing module for security vulnerabilities."
      metrics:
        - response_time
        - token_usage
        - vulnerability_detection_accuracy
        
    - name: "refactoring_suggestion"
      prompt: "Suggest refactoring to improve the performance of the processPayment method."
      metrics:
        - response_time
        - token_usage
        - code_quality_score
``` 