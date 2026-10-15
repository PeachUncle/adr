# ADR-002: Studying Claude CLI's Differential Update System

## Status
Proposed

## Context
Claude CLI efficiently handles code updates without requiring full re-ingestion of a codebase after each change. Through observation, we've noticed that Claude CLI appears to implement some form of differential update system that only processes changed files rather than re-analyzing the entire codebase.

Understanding how Claude CLI tracks and processes code changes is crucial for our learning project, as it represents a significant optimization for working with evolving codebases.

## Decision
We will study Claude CLI's approach to differential updates by:

1. Analyzing how Claude CLI behaves when files are added, modified, or deleted
2. Investigating whether Claude CLI maintains checksums or other identifiers for files
3. Observing how Claude CLI incorporates changes into its existing understanding of a codebase
4. Examining how context is maintained when changes affect multiple related files
5. Documenting the observed behavior to inform our experimental implementation

Our study methodology will include:
1. Setting up controlled experiments with versioned codebases
2. Making specific changes and observing Claude CLI's responses
3. Tracking session state and token usage patterns for different types of updates
4. Testing both small and large-scale changes to identify potential thresholds

## Consequences
- **Positive**: Deeper understanding of Claude CLI's efficient update mechanisms
- **Positive**: Insights into optimizing token usage for evolving codebases
- **Positive**: Learning applicable patterns for our experimental implementation
- **Negative**: May not fully reveal Claude CLI's internal mechanisms
- **Negative**: Conclusions will be based on observation rather than direct knowledge

## Implementation Study

```python
# claude_diff_study.py
import subprocess
import json
import hashlib
import os

def study_claude_differential_updates():
    """
    Study how Claude CLI handles differential updates to codebases.
    This experimental code analyzes behavior, not for production use.
    """
    # Create a test codebase repository
    os.makedirs("claude_test_repo", exist_ok=True)
    
    # Create a file and send to Claude
    with open("claude_test_repo/test_file.py", "w") as f:
        f.write("def example_function():\n    return 'Hello World'\n")
    
    # Create a session and send the initial file
    session_result = subprocess.run(
        ["claude", "session", "create", "--name", "diff-study"],
        capture_output=True, text=True
    )
    session_data = json.loads(session_result.stdout)
    session_id = session_data["id"]
    
    # Send the directory to Claude
    subprocess.run(
        ["claude", "dir", "send", "--session", session_id, "claude_test_repo"],
        capture_output=True, text=True
    )
    
    # Make a change to the file
    with open("claude_test_repo/test_file.py", "w") as f:
        f.write("def example_function():\n    return 'Hello Updated World'\n\ndef new_function():\n    pass\n")
    
    # Send the directory again and observe how Claude handles the change
    update_result = subprocess.run(
        ["claude", "dir", "send", "--session", session_id, "claude_test_repo"],
        capture_output=True, text=True
    )
    
    # Ask Claude what changed
    prompt_result = subprocess.run(
        ["claude", "prompt", "--session", session_id, "What changes did you notice in the code?"],
        capture_output=True, text=True
    )
    
    # Analyze Claude's understanding of the changes
    response = json.loads(prompt_result.stdout)
    
    # Document token usage for the update
    token_usage = response.get("usage", {})
    
    return {
        "initial_session": session_data,
        "update_result": json.loads(update_result.stdout) if update_result.stdout else None,
        "claude_understanding": response["content"][0]["text"],
        "token_usage": token_usage
    }
```

This experimental methodology will help us understand how Claude CLI efficiently handles code updates and inform our design of similar systems.