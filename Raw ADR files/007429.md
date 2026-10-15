# ADR-020: CodeCompass LiteLLM Demo Implementation

## Status
Proposed

## Context
Based on our existing ADR-017 (LiteLLM Integration for Multi-Model Support), we want to create a practical demonstration of how to use multiple LLM models for code understanding through a unified interface. This allows users to:

1. Choose the most appropriate model for their specific use case
2. Compare results across different models
3. Optimize costs by selecting different models based on needs
4. Create fallback mechanisms when a primary model is unavailable

While ADR-017 provides the architectural design, we need a concrete implementation that users can test, learn from, and adapt for their own projects.

## Decision
We will create a CodeCompass LiteLLM Demo that:

1. **Implements a working CLI tool**:
   - Provides a simple command-line interface for interacting with multiple LLMs
   - Supports file and directory input for code context
   - Allows model selection and configuration
   - Demonstrates effective prompt construction

2. **Includes a web-based demo interface**:
   - Model selection and comparison
   - Code input and analysis visualization
   - Performance and cost comparison metrics
   - Response quality assessment

3. **Demonstrates integration with multiple providers**:
   - Anthropic (Claude models)
   - OpenAI (GPT models)
   - Mistral AI models
   - Other providers available through LiteLLM

4. **Shows practical code navigation techniques**:
   - Semantic code search
   - Code structure analysis
   - Dependency tracking
   - Function explanation and documentation

## Implementation Approach

### CLI Implementation

1. **Basic CLI Structure**:
   ```python
   #!/usr/bin/env python3
   
   import argparse
   import os
   import sys
   from typing import List, Dict, Any
   import yaml
   import litellm
   
   def main():
       parser = argparse.ArgumentParser(description="CodeCompass - Multi-LLM code assistant")
       parser.add_argument("--model", default="anthropic/claude-3-sonnet", 
                          help="LiteLLM model identifier")
       parser.add_argument("--file", action="append", 
                          help="File(s) to include in context (can be specified multiple times)")
       parser.add_argument("--dir", 
                          help="Directory to scan for relevant files")
       parser.add_argument("--prompt", required=True, 
                          help="Prompt to send to the model")
       parser.add_argument("--temperature", type=float, default=0.7, 
                          help="Temperature for generation")
       parser.add_argument("--max-tokens", type=int, default=1000, 
                          help="Maximum tokens to generate")
       
       args = parser.parse_args()
       
       # Build context from files
       messages = []
       
       # Process individual files
       if args.file:
           for file_path in args.file:
               try:
                   with open(file_path, 'r') as f:
                       content = f.read()
                   messages.append({
                       "role": "user",
                       "content": f"File {file_path}:\n```\n{content}\n```"
                   })
               except Exception as e:
                   print(f"Error reading {file_path}: {e}", file=sys.stderr)
       
       # Process directory if specified
       if args.dir:
           # Implementation of directory scanning and processing
           pass
       
       # Add the user prompt
       messages.append({"role": "user", "content": args.prompt})
       
       # Call the model using LiteLLM
       try:
           response = litellm.completion(
               model=args.model,
               messages=messages,
               temperature=args.temperature,
               max_tokens=args.max_tokens
           )
           
           # Print the response
           print(response.choices[0].message.content)
           
       except Exception as e:
           print(f"Error calling LLM: {e}", file=sys.stderr)
           sys.exit(1)
   
   if __name__ == "__main__":
       main()
   ```

2. **Configuration Management**:
   ```python
   class ConfigManager:
       """Manages CodeCompass configuration."""
       
       def __init__(self, config_path=None):
           self.config_path = config_path or os.path.expanduser("~/.codecompass/config.yaml")
           self.config = self._load_config()
       
       def _load_config(self):
           """Load configuration from file or use defaults."""
           if os.path.exists(self.config_path):
               try:
                   with open(self.config_path, 'r') as f:
                       return yaml.safe_load(f)
               except Exception:
                   pass
           
           # Default configuration
           return {
               "default_model": "anthropic/claude-3-sonnet",
               "temperature": 0.7,
               "max_tokens": 1000,
               "models": {
                   "fast": "anthropic/claude-3-haiku",
                   "balanced": "anthropic/claude-3-sonnet",
                   "powerful": "anthropic/claude-3-opus",
                   "cost_effective": "mistral/mistral-large-latest"
               }
           }
   ```

### Web Interface Components

1. **Model Selector Component**:
   ```jsx
   function ModelSelector({ selectedModel, onModelChange, availableModels }) {
       return (
           <div className="model-selector">
               <h3>Select LLM Model</h3>
               <select 
                   value={selectedModel} 
                   onChange={(e) => onModelChange(e.target.value)}
               >
                   {Object.entries(availableModels).map(([key, model]) => (
                       <option key={key} value={model.id}>
                           {model.name} ({model.provider})
                       </option>
                   ))}
               </select>
           </div>
       );
   }
   ```

2. **Model Comparison Component**:
   ```jsx
   function ModelComparison({ codeInput, prompt, models }) {
       const [results, setResults] = useState({});
       const [isLoading, setIsLoading] = useState(false);
       
       const runComparison = async () => {
           setIsLoading(true);
           const newResults = {};
           
           for (const [modelName, modelId] of Object.entries(models)) {
               try {
                   // In a real implementation, this would call an API
                   const result = await mockApiCall(modelId, codeInput, prompt);
                   newResults[modelName] = result;
               } catch (error) {
                   newResults[modelName] = { error: error.message };
               }
           }
           
           setResults(newResults);
           setIsLoading(false);
       };
       
       return (
           <div className="model-comparison">
               <button 
                   onClick={runComparison}
                   disabled={isLoading || !codeInput || !prompt}
               >
                   {isLoading ? 'Running...' : 'Compare Models'}
               </button>
               
               {Object.entries(results).length > 0 && (
                   <div className="comparison-results">
                       {Object.entries(results).map(([modelName, result]) => (
                           <div key={modelName} className="model-result">
                               <h4>{modelName}</h4>
                               {result.error ? (
                                   <div className="error">{result.error}</div>
                               ) : (
                                   <div className="response">{result.response}</div>
                               )}
                           </div>
                       ))}
                   </div>
               )}
           </div>
       );
   }
   ```

### Tutorial Content Structure

1. **Introduction to LiteLLM**
   - Overview of multi-model capabilities
   - Supported providers and models
   - Key advantages of model flexibility

2. **Setting Up CodeCompass with LiteLLM**
   - Installation and configuration
   - API key management for different providers
   - Basic usage examples

3. **Choosing the Right Model**
   - Comparison of different models' capabilities
   - Cost considerations
   - Performance benchmarks
   - Specialized use cases

4. **Advanced Usage**
   - Model fallback strategies
   - Caching and cost optimization
   - Prompt engineering for different models
   - Error handling and retries

5. **Building Your Own Tools**
   - Extending the basic implementation
   - Creating custom integrations
   - Saving and analyzing responses
   - Integration with development workflows

## Consequences
- **Positive**: Demonstrates practical multi-model usage for code understanding
- **Positive**: Provides a working implementation users can adapt
- **Positive**: Helps users optimize for cost, performance, and capabilities
- **Positive**: Shows how to migrate between different LLM providers
- **Negative**: Requires maintaining compatibility with LiteLLM updates
- **Negative**: Model capabilities and APIs may evolve, requiring updates

## Implementation Timeline
- CLI implementation: 1-2 days
- Web interface implementation: 2-3 days
- Tutorial content: 1-2 days
- Testing and refinement: 1 day

Total estimated timeline: 5-8 days 