# Use `Instructor` for Structured Output Handling

**Status**: Proposed  
**Date**: 2025-02-16  
**Deciders**: Architectrons

## Context and Problem Statement

The certification system leverages AI with Retrieval-Augmented Generation (RAG) to analyze candidate answers and provide structured feedback. The challenge is ensuring that the AI generates responses in a predictable and structured format, which is critical for grading, feedback automation, and system integration.

## Decision Drivers

* The AI responses need to be structured for downstream processing.  
* The system should minimize hallucinations and enforce schema validation.  
* Integration with LLMs should be seamless and efficient.  
* The solution should support multiple AI models and be easy to extend.  
* The implementation should be maintainable and well-supported in the AI community.  

## Considered Options

1. **Using `Instructor` package for structured output handling.**  
2. **Manually post-processing LLM outputs with regex and parsing.**  
3. **Using OpenAI function calling or JSON mode.**  

## Decision Outcome

**Chosen option: "Using `Instructor` package for structured output handling," because it provides built-in schema validation and ensures reliable structured output from LLMs without complex post-processing.**

### Consequences

* **Good, because** it ensures AI-generated responses strictly follow a predefined schema.  
* **Good, because** it minimizes hallucinations by aligning responses to expected structures.  
* **Good, because** it simplifies development by reducing the need for complex post-processing logic.  
* **Bad, because** it introduces an external dependency (`Instructor` package).  
* **Bad, because** it may have performance overhead compared to raw LLM API responses.  

## Pros and Cons of the Options

### **Using `Instructor` package for structured output handling**  

* **Good, because** it enforces schema validation directly within LLM responses.  
* **Good, because** it supports multiple LLMs and minimizes hallucinations.  
* **Neutral, because** it relies on an external package (`Instructor`).  
* **Bad, because** potential performance overhead compared to raw API calls.  

### **Manually post-processing LLM outputs with regex and parsing**  

* **Good, because** it avoids adding dependencies.  
* **Neutral, because** parsing logic can be controlled but requires effort.  
* **Bad, because** it increases code complexity.  
* **Bad, because** regex-based parsing is brittle and error-prone.  

### **Using OpenAI function calling or JSON mode**  

* **Good, because** OpenAI supports function calling and structured JSON output.  
* **Good, because** no need for extra dependencies if using OpenAI.  
* **Bad, because** limited to OpenAI models, reducing flexibility.  
* **Bad, because** may not generalize well for multi-model AI systems.  

## More Information

- [Instructor](https://github.com/jxnl/instructor)  
- [RAG and structured response best practices](https://www.promptingguide.ai/)  
