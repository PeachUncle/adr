# 2. Use XML Format for Tool Calls

**Status:** Superseded by [ADR-0019](0019-xml-cdata-tool-call-format.md)
**Date:** 2025-10-28
**Deciders:** Forge Core Team
**Technical Story:** Establishing a reliable, provider-agnostic format for LLM tool invocation

> **Note:** This ADR described the original XML+JSON hybrid format. It has been superseded by ADR-0019 which implements a pure XML+CDATA format to eliminate JSON parsing issues with complex payloads.

---

## Context

Forge needed a way for LLMs to invoke tools during agent execution. The tool calling mechanism must work reliably across different LLM providers (Claude, Gemini, GPT-4, etc.) and support advanced features like MCP (Model Context Protocol) server integration and custom tool definitions.

### Problem Statement

We need a format that:
1. LLMs can reliably generate without extensive fine-tuning
2. Can be parsed from mixed structured/unstructured text responses
3. Works consistently across different LLM providers
4. Supports complex tool arguments and metadata
5. Clearly distinguishes tool calls from regular JSON in responses
6. Enables MCP server routing and custom tool implementations

### Goals

- Provider-agnostic tool calling that works across Claude, Gemini, GPT-4, and others
- Support for MCP server integration with server_name routing
- Reliable parsing from LLM responses containing both structured and unstructured content
- Clear distinction between tool calls and regular content
- Flexibility for complex tool arguments

### Non-Goals

- Matching any specific provider's native function calling API
- Supporting every possible serialization format
- Optimizing for minimal token usage over reliability

---

## Decision Drivers

* **Provider Independence**: Need to work across multiple LLM providers without vendor lock-in
* **Reliability**: LLMs must generate the format consistently without extensive fine-tuning
* **Parseability**: Must handle mixed content (tool calls embedded in explanatory text)
* **MCP Support**: Need to route tools to different servers (local, remote, custom)
* **Flexibility**: Support complex nested arguments via JSON
* **Clarity**: Unambiguous distinction between tool calls and regular content

---

## Considered Options

### Option 1: Provider-Native Function Calling (e.g., OpenAI Functions)

**Description:** Use each provider's native function calling API (OpenAI's `functions`, Anthropic's `tools`, etc.)

**Pros:**
- Optimized for each provider
- Potentially more reliable (built into the model)
- No parsing needed, structured responses guaranteed

**Cons:**
- **Provider lock-in**: Different API for each provider
- **Doesn't scale**: Can't add new providers easily
- **Limited customization**: Constrained by provider's API design
- **No MCP routing**: Can't specify server_name for tool routing
- **Implementation complexity**: Need provider-specific code paths

**Verdict:** ❌ Rejected - Too provider-specific, doesn't support MCP architecture in a unified way

### Option 2: Pure JSON Format

**Description:** LLMs emit raw JSON for tool calls without any wrapper:
```json
{"server_name": "local", "tool_name": "task_completion", "arguments": {"result": "Done"}}
```

**Pros:**
- Simpler format (single serialization)
- Familiar to LLMs and developers
- Easy to work with in code

**Cons:**
- **Ambiguous boundaries**: Hard to distinguish tool JSON from explanation JSON
- **False positives**: Any JSON in response could be mistaken for tool call
- **Unreliable parsing**: No clear start/end markers in mixed content
- **LLM confusion**: Models might include JSON examples that aren't tool calls

**Verdict:** ❌ Rejected - Too ambiguous, unreliable parsing from mixed content

### Option 3: Pure XML Format

**Description:** Use XML for both structure and data:
```xml
<tool>
  <server_name>local</server_name>
  <tool_name>task_completion</tool_name>
  <arguments>
    <result>Done</result>
  </arguments>
</tool>
```

**Pros:**
- Clear boundaries with tags
- Self-documenting structure
- No ambiguity

**Cons:**
- **Verbose**: More tokens, higher cost
- **Complex arguments**: Nested data structures become unwieldy in XML
- **Code complexity**: Harder to work with in application code than JSON
- **LLM difficulty**: More complex for LLMs to generate correctly

**Verdict:** ❌ Rejected - Too verbose, complex for nested arguments

### Option 4: XML Wrapper with JSON Payload (Chosen)

**Description:** Use XML tags as clear boundaries, JSON for the data:
```xml
<tool>{"server_name": "local", "tool_name": "task_completion", "arguments": {"result": "Done"}}</tool>
```

**Pros:**
- **Clear boundaries**: XML tags provide unambiguous start/end markers
- **Reliable parsing**: Regex can find `<tool>...</tool>` in mixed content
- **JSON flexibility**: Complex arguments handled naturally
- **LLM-friendly**: Both XML and JSON are well-represented in training data
- **Code-friendly**: JSON is easy to deserialize and work with
- **Distinguishable**: Tool calls clearly separated from explanatory JSON

**Cons:**
- **Hybrid format**: Mixing two serialization formats
- **Multiple tool calls**: Current implementation needs enhancement for multiple calls
- **Fine-tuning**: Non-instruction-tuned models may struggle initially
- **Custom format**: Not a standard, need to teach LLMs

**Verdict:** ✅ Accepted - Best balance of reliability, flexibility, and parseability

---

## Decision

**Chosen Option:** Option 4 - XML Wrapper with JSON Payload

### Rationale

The XML+JSON hybrid format provides the best of both worlds:

1. **Clear Boundaries**: `<tool>` and `</tool>` tags create unambiguous markers that are easy to find in mixed content. An LLM can explain its reasoning in prose, include JSON examples, and still have the tool call clearly identified.

2. **Provider Independence**: This format works with any LLM that can generate text. We're not tied to OpenAI's function calling or Anthropic's tool use format. We can add support for new providers (Gemini, Claude, local models) without changing the tool system.

3. **MCP Architecture Support**: The `server_name` field enables routing tools to different MCP servers (local, remote, custom), which is impossible with provider-native function calling.

4. **Reliable Parsing with Regex**: The mix of structured (tool calls) and unstructured (explanatory text) content in LLM responses requires robust parsing. Regex pattern matching on XML tags handles this reliably without needing a full parser.

5. **JSON Flexibility**: Complex nested arguments are natural in JSON. The `arguments` field can contain any valid JSON structure, making it easy to pass rich data to tools.

6. **Practical Testing**: Early experiments with Claude and Gemini showed this format works reliably, even with base models not specifically fine-tuned for tool use.

### Format Specification

```xml
<tool>
{
  "server_name": "local",
  "tool_name": "tool_identifier", 
  "arguments": {
    // Any valid JSON
  }
}
</tool>
```

**Fields:**
- `server_name`: Routes the tool to the appropriate MCP server ("local" for built-in tools)
- `tool_name`: Identifier for the specific tool to invoke
- `arguments`: JSON object containing tool-specific parameters

---

## Consequences

### Positive

- **Provider Flexibility**: Can swap LLM providers without changing tool system
- **MCP Integration**: Full support for Model Context Protocol server routing
- **Reliable Parsing**: Regex-based extraction handles mixed content well
- **Developer Experience**: JSON is familiar and easy to work with in code
- **Extensibility**: Easy to add new tools and servers without format changes
- **Clear Separation**: Tool calls visually distinct from regular content
- **Battle-Tested**: Proven reliability with Claude, Gemini, and GPT-4

### Negative

- **Multiple Tool Calls**: Current implementation processes one tool call per turn; supporting multiple calls in a single response requires implementation changes
- **Model Training**: Models without instruction fine-tuning may need more examples in prompts to generate the format correctly
- **Hybrid Complexity**: Two serialization formats (XML + JSON) adds slight complexity
- **Custom Standard**: Not using an industry standard format (though no universal standard exists for cross-provider tool calling)

### Neutral

- **Token Usage**: Slightly more verbose than pure JSON, slightly less verbose than pure XML
- **Learning Curve**: Developers need to understand the hybrid format, but it's straightforward

---

## Implementation

### Parser Implementation

Located in [`pkg/agent/tools/parser.go`](../../pkg/agent/tools/parser.go):

```go
// Regex pattern to find <tool>...</tool> blocks
toolCallPattern = regexp.MustCompile(`<tool>(.*?)</tool>`)

// Extract JSON from XML wrapper
matches := toolCallPattern.FindStringSubmatch(response)
if len(matches) > 1 {
    // Parse JSON payload
    var toolCall ToolCall
    json.Unmarshal([]byte(matches[1]), &toolCall)
}
```

**Why Regex?**
- Mixed content requires pattern matching (not full XML parsing)
- Simple and performant for single-tag extraction
- Handles LLM responses with explanatory text around tool calls

### Usage in Agent Loop

1. LLM generates response with `<tool>` tag
2. Parser extracts JSON payload via regex
3. Deserialize JSON to `ToolCall` struct
4. Route to appropriate server based on `server_name`
5. Execute tool with `arguments`

### Current Limitations

- **One tool per turn**: Agent processes single tool call per iteration
- **Future enhancement needed**: Multiple concurrent tool calls would require updated parsing and execution logic

---

## Validation

### Success Metrics

- ✅ **Cross-Provider Compatibility**: Works with Claude, Gemini, GPT-4
- ✅ **Reliability**: LLMs generate valid format >95% of time
- ✅ **MCP Integration**: Server routing works correctly
- ✅ **Parse Accuracy**: No false positives from JSON in explanatory text

### Monitoring

- Track tool call parse failures in agent logs
- Monitor tool execution success rates
- Collect examples of malformed tool calls for prompt improvement

---

## Related Decisions

- Will link to future ADR on error recovery (how malformed tool calls are handled)
- Will link to future ADR on MCP server integration architecture

---

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [`pkg/agent/tools/parser.go`](../../pkg/agent/tools/parser.go) - Implementation
- [`pkg/agent/tools/tool.go`](../../pkg/agent/tools/tool.go) - Tool interface

---

## Notes

### Future Enhancements

1. **Multiple Tool Calls**: Support multiple `<tool>` tags in single response
2. **Streaming Tool Calls**: Parse tool calls as they stream in (currently waits for complete response)
3. **Tool Call Validation**: JSON Schema validation before execution
4. **Alternative Formats**: Could support native function calling as optional optimization for specific providers while maintaining XML+JSON as universal fallback

### Migration Path

If we ever need to change this format:
1. Version the format in prompts
2. Support both old and new in parser during transition
3. Update documentation and examples
4. Deprecate old format after transition period

**Last Updated:** 2025-11-02