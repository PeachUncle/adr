# ADR-001: Understanding Claude CLI's Semantic Chunking for Codebase Processing

## Status
Proposed

## Context
Claude CLI effectively handles large codebases that would otherwise exceed Claude's 128k token context window. After studying Claude CLI, we've observed that it doesn't simply send entire files but appears to implement intelligent chunking strategies that respect code structure.

When processing large codebases, Claude CLI appears to:
1. Filter and prioritize relevant files based on user queries
2. Chunk large files intelligently, maintaining semantic coherence
3. Include critical context like class definitions and import statements
4. Prioritize functional code over comments and whitespace
5. Track what has been processed to avoid redundant token usage

Understanding these mechanisms is crucial for our experimental learning project.

## Decision
We will study Claude CLI's codebase handling through experimental observation and develop our own experimental implementation that:

1. Analyzes how Claude CLI processes large codebases
2. Observes patterns in file selection and chunking strategies
3. Explores how Claude CLI maintains context across multiple files
4. Documents our findings for educational purposes
5. Implements an experimental semantic chunking system based on our observations

Our observation approach will include:
1. Sending progressively larger codebases to Claude CLI
2. Analyzing which content is prioritized in responses
3. Testing different file types and structures
4. Measuring token usage patterns

## Consequences
- **Positive**: Better understanding of how Claude CLI efficiently processes codebases
- **Positive**: Learning about semantic chunking approaches for LLM context optimization
- **Positive**: Gaining insights into Claude CLI's internal mechanisms
- **Positive**: Practical experience implementing similar approaches
- **Negative**: Our observations may not fully reveal the exact mechanisms used
- **Negative**: Our experimental implementation may differ from Claude CLI's approach

## Implementation Approach

```python
# chunking_study.py - Experimental code to study Claude CLI's chunking behavior
import subprocess
import json
import os
import re

def analyze_claude_cli_chunking(repo_path, query):
    """Analyze how Claude CLI processes a repository in response to a query."""
    # Set up a session
    session_result = subprocess.run(
        ["claude", "session", "create", "--name", "chunking-study"],
        capture_output=True, text=True
    )
    session_data = json.loads(session_result.stdout)
    session_id = session_data["id"]
    
    # Send the directory
    dir_result = subprocess.run(
        ["claude", "dir", "send", "--session", session_id, repo_path, "--include", "*.py"],
        capture_output=True, text=True
    )
    
    # Send a query about code in the repo
    prompt_result = subprocess.run(
        ["claude", "prompt", "--session", session_id, query],
        capture_output=True, text=True
    )
    
    # Analyze the response to determine what was included
    response = json.loads(prompt_result.stdout)
    content = response["content"][0]["text"]
    
    # Analyze which files/portions were referenced in the response
    references = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path) as f:
                    file_content = f.read()
                
                # Look for snippets from this file in the response
                snippets = find_content_in_response(file_content, content)
                if snippets:
                    references.append({
                        "file": path,
                        "snippets": snippets,
                        "is_complete": len(snippets) == 1 and len(snippets[0]) == len(file_content)
                    })
    
    return {
        "token_usage": response.get("usage", {}),
        "referenced_files": references
    }

def find_content_in_response(file_content, response):
    """Find which portions of a file were included in a response."""
    # This is a simplistic approach - in practice, we'd use more sophisticated 
    # text similarity measures to identify partial matches
    snippets = []
    
    # Split file into logical sections (functions, classes, etc.)
    sections = re.split(r'(def\s+\w+|class\s+\w+)', file_content)
    
    for i in range(1, len(sections), 2):
        section = sections[i] + sections[i+1] if i+1 < len(sections) else sections[i]
        # Check if this section or a significant portion appears in the response
        if section in response or significant_overlap(section, response):
            snippets.append(section)
    
    return snippets

def significant_overlap(text, response, threshold=0.7):
    """Check if there is significant text overlap."""
    # Simplified implementation - would be more sophisticated in practice
    lines = text.split('\n')
    matched_lines = 0
    
    for line in lines:
        line = line.strip()
        if len(line) > 10 and line in response:  # Only check non-trivial lines
            matched_lines += 1
    
    return matched_lines / len(lines) > threshold if lines else False
```

## Learning Outcomes

Through this study, we aim to understand:

1. How Claude CLI determines which files are relevant to a query
2. What chunking strategies Claude CLI appears to use
3. How Claude CLI maintains essential context across chunks
4. What heuristics seem to guide its token usage optimizations

This experimental study will help us build a conceptual model of Claude CLI's approach to codebase processing, which we can then implement in our own experimental tool.