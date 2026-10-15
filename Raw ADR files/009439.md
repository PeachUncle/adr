# 19. Pure XML with CDATA for Tool Call Arguments

**Status:** Superseded by [ADR-0024](0024-xml-escaping-primary-with-cdata-fallback.md)
**Date:** 2025-11-17
**Deciders:** Forge Core Team
**Technical Story:** Eliminating ALL parsing issues by using pure XML structure
**Supersedes:** ADR-0002 (revised approach based on feedback)

> **Note:** This ADR established CDATA as mandatory for all code/content fields. ADR-0024 revises this approach to make XML entity escaping the primary method, with CDATA as a fallback option. Both methods remain fully supported.

---

## Context

The current XML+JSON hybrid format (ADR-0002) has parsing failures with large/complex payloads. An initial proposal suggested XML+CDATA with JSON inside, but this still carries JSON parsing risk. 

**Key Insight:** We can eliminate JSON parsing issues entirely by using pure XML structure with CDATA only for actual content fields.

### Problem Statement

**Current Format Issues:**
```xml
<tool>{"server_name": "local", "tool_name": "write_to_file", "arguments": {"path": "file.go", "content": "..."}}</tool>
```

1. JSON escaping required for all content
2. Nested escape sequences become unmanageable
3. Single escape error breaks entire tool call

**Previous Considerations:**
```xml
<arguments><![CDATA[
{
  "path": "file.go",
  "content": "func main() {...}"
}
]]></arguments>
```

- Still requires JSON parsing
- JSON syntax errors can still occur
- Nested objects require careful JSON formatting

---

## Decision

**Chosen Solution:** Pure XML with CDATA for content fields only

### Format Specification

```xml
<tool>
<server_name>local</server_name>
<tool_name>write_to_file</tool_name>
<arguments>
  <path>src/main.go</path>
  <content><![CDATA[package main

import "fmt"

func main() {
	fmt.Println("No escaping needed!")
	// Any code with "quotes", 'apostrophes', backslashes\, etc.
}]]></content>
</arguments>
</tool>
```

### Structure Rules

1. **Metadata as XML elements**: `<server_name>` and `<tool_name>`
2. **Arguments as nested XML**: Each parameter is an XML element
3. **Simple values**: Direct text content (strings, numbers, booleans)
4. **Large/complex content**: Wrapped in `<![CDATA[...]]>`
5. **Arrays**: Multiple elements with same name or structured XML
6. **Objects**: Nested XML elements

---

## Examples

### Simple Tool Call

```xml
<tool>
<server_name>local</server_name>
<tool_name>task_completion</tool_name>
<arguments>
  <result>Task completed successfully</result>
</arguments>
</tool>
```

### Large File Write

```xml
<tool>
<server_name>local</server_name>
<tool_name>write_to_file</tool_name>
<arguments>
  <path>components/Button.tsx</path>
  <content><![CDATA[import React from 'react';

interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ onClick, children }) => {
  return (
    <button onClick={onClick} className="px-4 py-2">
      {children}
    </button>
  );
};]]></content>
</arguments>
</tool>
```

### Complex Diff with Multiple Edits

```xml
<tool>
<server_name>local</server_name>
<tool_name>apply_diff</tool_name>
<arguments>
  <path>src/app.ts</path>
  <edits>
    <edit>
      <search><![CDATA[const oldConfig = {
	api: "http://old.com",
	key: "old_key"
};]]></search>
      <replace><![CDATA[const newConfig = {
	api: "https://new.com",
	key: "new_key",
	verbose: true
};]]></replace>
    </edit>
    <edit>
      <search><![CDATA[function process(data) {
	return data.map(x => x * 2);
}]]></search>
      <replace><![CDATA[function process(data) {
	return data
		.filter(x => x > 0)
		.map(x => x * 2);
}]]></replace>
    </edit>
  </edits>
</arguments>
</tool>
```

### Array Arguments

```xml
<tool>
<server_name>local</server_name>
<tool_name>search_files</tool_name>
<arguments>
  <path>src</path>
  <pattern>\.ts$</pattern>
  <exclude>node_modules</exclude>
  <exclude>dist</exclude>
  <exclude>.git</exclude>
</arguments>
</tool>
```

---

## Rationale

### Why This Eliminates ALL Parsing Issues

1. **No JSON Parsing**: Pure XML eliminates JSON syntax errors entirely
2. **CDATA for Content**: Large code blocks need zero escaping
3. **Explicit Structure**: Each argument is clearly named and typed
4. **LLM Training Data**: XML is extensively represented in training data (HTML, SVG, RSS, config files)
5. **Streaming Friendly**: Clear XML boundaries work perfectly with streaming

### Comparison with Previous Proposals

**Current (XML+JSON):**
- ❌ Requires JSON escaping for all content
- ❌ Prone to escape sequence errors
- ✅ Compact format

**Alternative (XML+CDATA+JSON):**
- ❌ Still requires JSON parsing
- ❌ JSON syntax errors still possible
- ✅ Better than current for large payloads

**This Proposal (Pure XML+CDATA):**
- ✅ Zero JSON parsing
- ✅ Zero escape sequences for content
- ✅ Clear, explicit structure
- ❌ More verbose

**Trade-off:** ~20-30% more tokens for 99.9% reliability improvement

---

## Implementation

### Parser Changes

```go
type ToolCall struct {
    ServerName string
    ToolName   string
    Arguments  map[string]interface{}
}

func ParseToolCallXML(text string) (*ToolCall, error) {
    // 1. Extract <tool>...</tool> block
    // 2. Parse server_name and tool_name as XML elements
    // 3. Parse <arguments> recursively:
    //    - Text content → string value
    //    - CDATA content → string value (raw)
    //    - Nested elements → nested map/array
    // 4. Return ToolCall with arguments map
}
```

### Streaming Parser

```go
type XMLToolCallParser struct {
    state        ParserState
    elementStack []string
    cdataMode    bool
    buffer       strings.Builder
}

// States: Outside, InTool, InServerName, InToolName, InArguments, InCDATA
```

### Tool Schema Updates

Tools define their schema in Go structs, parser maps XML to struct:

```go
type WriteToFileArgs struct {
    Path    string `xml:"path"`
    Content string `xml:"content"`
}

type ApplyDiffArgs struct {
    Path  string `xml:"path"`
    Edits []struct {
        Search  string `xml:"search"`
        Replace string `xml:"replace"`
    } `xml:"edits>edit"`
}
```

---

## Implementation Plan

### Phase 1: Core Parser Implementation

**Task 1.1: Implement Pure XML Parser**
- File: `pkg/agent/tools/parser.go`
- Create `ParseToolCallXML()` function
- Parse `<tool>` wrapper and extract `<server_name>`, `<tool_name>`
- Recursively parse `<arguments>` into `map[string]interface{}`
- Handle CDATA sections for content fields
- Support arrays (multiple elements with same name)
- Handle edge case: `]]>` in CDATA content

**Task 1.2: Update Streaming Parser**
- File: `pkg/llm/parser/toolcall.go`
- Add XML state machine for streaming
- Detect CDATA boundaries (`<![CDATA[` and `]]>`)
- Buffer partial XML tags across chunks
- Emit complete tool calls when `</tool>` received

**Task 1.3: Comprehensive Test Suite**
- Create `pkg/agent/tools/parser_xml_test.go`
- Test simple arguments (strings, numbers, booleans)
- Test large content (files up to 10MB in CDATA)
- Test complex structures (nested objects, arrays)
- Test edge cases (`]]>` in content, special characters)
- Test streaming scenarios (tags split across chunks)
- Test all existing tool call patterns

### Phase 2: Tool Schema Updates

**Task 2.1: Update Tool Argument Structs**
- Convert all `json:` tags to `xml:` tags in tool files
- Update struct definitions for XML deserialization
- Test XML unmarshaling for each tool

### Phase 3: Documentation & Prompts

**Task 3.1: Update System Prompts**
- File: `cmd/forge/prompts.go`
- Replace JSON examples with XML format
- Add CDATA usage guidelines
- Document when to use CDATA vs plain text
- Provide examples for common tools (write_to_file, apply_diff)

**Task 3.2: Update Tool Documentation**
- Add XML format examples for each tool
- Show before/after format comparisons
- Document edge cases and best practices

### Phase 4: Validation & Deployment

**Task 4.1: Performance Benchmarks**
- Create benchmark tests comparing XML vs JSON parsing
- Test with various payload sizes (1KB, 10KB, 100KB, 1MB, 10MB)
- Ensure <10% performance regression
- Profile memory usage

**Task 4.2: Deploy and Monitor**
- Deploy parser changes to production
- Monitor parse success rates via metrics
- Track error logs for parsing issues
- Validate >99.9% success rate

## Success Criteria

- ✅ Parse success rate >99.9% for all tool calls
- ✅ All unit tests passing with >90% coverage
- ✅ Performance within 10% of current implementation
- ✅ Zero JSON parsing errors in production
- ✅ Comprehensive documentation updated

---

## Consequences

### Positive

- **Zero JSON parsing errors**: Eliminated entirely
- **Zero escape sequences**: For content fields (99% of the problem)
- **Clear structure**: Explicit argument names and types
- **Better error messages**: XML parsing errors are clearer than JSON
- **Type safety**: Can validate structure before execution
- **Future-proof**: Easy to extend with new argument types

### Negative

- **Verbosity**: ~20-30% more tokens per tool call
- **Complex nested data**: Requires nested XML (less compact than JSON)
- **Learning curve**: Teams familiar with JSON may need time to adapt

### Neutral

- **LLM generation**: XML is as familiar as JSON to modern LLMs
- **Code complexity**: Parser is different, not necessarily more complex

---

## CDATA Edge Cases

### Handling `]]>` in Content

If content contains `]]>` (extremely rare), split the CDATA:

```xml
<content><![CDATA[XML example: ]]]]><![CDATA[> is CDATA end marker]]></content>
```

LLM instruction: "If content contains `]]>`, split it as: `]]]]><![CDATA[>`"

### When to Use CDATA

**Use CDATA for:**
- File content (code, HTML, JSON, etc.)
- Large text blocks with special characters
- Diff search/replace content
- Any content with quotes, backslashes, newlines

**Don't use CDATA for:**
- Simple strings (file paths, names)
- Numbers, booleans
- Small text values without special characters

## Type Inference

The XML parser automatically converts string values to appropriate types:

### Automatic Type Conversion Rules

1. **Booleans**: `true` or `false` (case-insensitive) → Go `bool`
   ```xml
   <recursive>true</recursive>        <!-- becomes bool(true) -->
   <enabled>FALSE</enabled>           <!-- becomes bool(false) -->
   ```

2. **Null**: `null` (case-insensitive) → Go `nil`
   ```xml
   <optional>null</optional>          <!-- becomes nil -->
   ```

3. **Integers**: Numeric strings without decimal → Go `int` or `int64`
   ```xml
   <count>123</count>                 <!-- becomes int(123) -->
   <line_start>1</line_start>         <!-- becomes int(1) -->
   ```

4. **Floats**: Numeric strings with decimal or scientific notation → Go `float64`
   ```xml
   <ratio>3.14</ratio>                <!-- becomes float64(3.14) -->
   <value>1.23e10</value>             <!-- becomes float64(1.23e10) -->
   ```

5. **Strings**: Everything else remains as string
   ```xml
   <path>./src/main.go</path>         <!-- remains string -->
   <name>hello</name>                 <!-- remains string -->
   ```

### Type Inference Examples

```xml
<tool>
<server_name>local</server_name>
<tool_name>example</tool_name>
<arguments>
  <name>test</name>              <!-- string -->
  <count>42</count>              <!-- int -->
  <ratio>3.14</ratio>            <!-- float64 -->
  <enabled>true</enabled>        <!-- bool -->
  <disabled>false</disabled>     <!-- bool -->
  <optional>null</optional>      <!-- nil -->
</arguments>
</tool>
```

### Edge Cases

- **Leading zeros**: `007` → `int(7)` (not string)
- **Quoted values**: `"true"` → `string("true")` (not bool)
- **Special floats**: `+Inf`, `-Inf`, `NaN` are parsed as `float64`
- **CDATA content**: Always treated as string (no type conversion)
- **Nested XML**: Recursively parsed into `map[string]interface{}`

### Forcing String Type

If you need the literal string `"true"` instead of boolean `true`:

1. **Use quotes**: `<param>"true"</param>` → string `"true"`
2. **Use CDATA**: `<param><![CDATA[true]]></param>` → string `true`

Note: CDATA content is never type-converted and always remains as string.

---

## Validation

### Success Metrics

- ✅ **Parse success rate**: >99.9% for all tool calls
- ✅ **Zero JSON errors**: Eliminate JSON parsing as failure mode
- ✅ **Performance**: <10% slower than current implementation
- ✅ **Token overhead**: Acceptable trade-off for reliability

### Test Coverage

1. **Simple arguments**: Strings, numbers, booleans
2. **Large content**: Files up to 10MB
3. **Complex structures**: Nested objects, arrays
4. **Edge cases**: `]]>` in content, special characters
5. **All tools**: Every tool with various argument combinations

---

## Tool Examples

### execute_command

```xml
<tool>
<server_name>local</server_name>
<tool_name>execute_command</tool_name>
<arguments>
  <command>npm install</command>
  <working_dir>./frontend</working_dir>
</arguments>
</tool>
```

### search_files

```xml
<tool>
<server_name>local</server_name>
<tool_name>search_files</tool_name>
<arguments>
  <path>src</path>
  <pattern><![CDATA[func.*\(.*\)]]></pattern>
  <file_pattern>*.go</file_pattern>
</arguments>
</tool>
```

### read_file

```xml
<tool>
<server_name>local</server_name>
<tool_name>read_file</tool_name>
<arguments>
  <path>src/main.go</path>
  <line_start>1</line_start>
  <line_end>100</line_end>
</arguments>
</tool>
```

---

## Related Decisions

- [ADR-0002: XML Format for Tool Calls](0002-xml-format-for-tool-calls.md) - Original format

---

## References

- [XML Specification (W3C)](https://www.w3.org/TR/xml/)
- [CDATA Sections](https://www.w3.org/TR/xml/#sec-cdata-sect)
- [Go XML Encoding](https://pkg.go.dev/encoding/xml)

---

**Last Updated:** 2025-11-17