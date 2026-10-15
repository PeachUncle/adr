# 23. Bash Mode Architecture for Direct Shell Command Execution

**Status:** Proposed
**Date:** 2025-01-21
**Deciders:** Forge Development Team
**Technical Story:** Implement a bash mode in the TUI that allows users to execute shell commands directly using the `!` prefix, bypassing the agent loop for immediate command execution.

---

## Context

### Background

The Forge TUI currently provides two mechanisms for executing shell commands:

1. **Agent-Driven Execution**: The agent can call the `execute_command` tool as part of its reasoning loop ([ADR-0013](0013-streaming-command-execution.md))
2. **Slash Commands**: User can trigger specific operations via slash commands like `/commit`, `/pr`, etc.

However, developers frequently need to run arbitrary shell commands during development sessions without engaging the agent. Common use cases include:
- Checking git status (`git status`)
- Running tests (`npm test`, `go test ./...`)
- Viewing file contents (`cat config.yml`)
- Searching for text (`grep -r "pattern"`)
- Package management (`npm install`, `go get`)

Currently, users must either:
- Switch to another terminal window
- Ask the agent to execute the command (slow, uses tokens)
- Exit Forge to run commands

### Problem Statement

**The TUI lacks a direct, fast mechanism for executing shell commands without involving the agent.** This forces users to context-switch between Forge and their shell, breaking their workflow and reducing productivity.

### Goals

- Provide instant shell command execution from within the TUI
- Maintain consistent command output display using existing overlay system
- Preserve security boundaries (workspace validation)
- Support command history and editing
- Enable both one-off commands and multi-command workflows
- Minimize cognitive overhead (simple, intuitive interface)

### Non-Goals

- Full-featured shell replacement (no job control, pipes, etc.)
- Interactive command support (no `vim`, `less`, etc.)
- Shell scripting language support
- Command auto-completion
- Multiple concurrent command execution

---

## Decision Drivers

* **Developer Experience**: Commands should execute instantly without agent overhead
* **Workflow Integration**: Seamless integration with existing TUI patterns
* **Consistency**: Reuse existing command execution and display infrastructure
* **Security**: Maintain workspace boundaries and approval mechanisms
* **Simplicity**: Minimal new concepts or UI patterns to learn
* **Flexibility**: Support both quick commands and multi-command sessions

---

## Considered Options

### Option 1: Prefix-Based Direct Execution (One-Shot)

**Description:** Detect `!` prefix in the normal input flow and execute commands directly via the existing `execute_command` tool, bypassing the agent entirely.

**User Experience:**
```
> !git status
[Command overlay shows output]

> !npm test
[Command overlay shows output]

> What files did the test modify?
[Normal agent conversation resumes]
```

**Implementation:**
- Detect `!` prefix in `Update()` function before agent input handling
- Call `execute_command` tool directly (not through agent)
- Display output using existing command overlay system
- Return to normal input mode after command completes

**Pros:**
- Extremely simple to understand and use
- No mode switching or state management
- Reuses existing command execution infrastructure
- Natural integration with current workflow
- Each command is independent (no state)
- Works well with command history (↑/↓ arrows)

**Cons:**
- Cannot easily run multiple related commands
- Must prefix every command with `!`
- No persistent bash session (each command isolated)
- Cannot set environment variables across commands

### Option 2: Mode-Based Bash Session

**Description:** Add a `/bash` slash command that enters a persistent bash mode where all input is treated as shell commands until explicitly exited.

**User Experience:**
```
> /bash
[Bash mode activated]
bash> git status
[Output shown]
bash> npm install
[Output shown]
bash> exit
[Bash mode deactivated, return to normal input]
```

**Implementation:**
- Add `bashMode` boolean state to model
- Change input prompt when in bash mode
- All input goes directly to execute_command
- Special handling for `exit` command to leave mode
- Update status bar to show current mode

**Pros:**
- Natural for running multiple related commands
- Familiar shell-like experience
- No need to prefix every command
- Can maintain working directory state
- Better for complex multi-step operations

**Cons:**
- Mode switching adds complexity
- Users must remember to exit bash mode
- Ambiguity between agent conversation and commands
- More state management required
- Harder to mix agent questions with commands

### Option 3: Hybrid Approach (Prefix + Mode)

**Description:** Combine both approaches: `!` for one-off commands, `/bash` for persistent mode.

**User Experience:**
```
> !git status
[Quick one-off command]

> /bash
bash> npm install express
bash> npm test
bash> exit

> Can you explain that test failure?
[Agent conversation resumes]
```

**Implementation:**
- Implement both Option 1 and Option 2
- `!` prefix always works (even outside bash mode)
- `/bash` enters mode where prefix is optional
- In bash mode, `!` still works but not required

**Pros:**
- Maximum flexibility for different workflows
- Users can choose their preferred style
- Supports both quick commands and sessions
- Backward compatible (can add features later)

**Cons:**
- Two ways to do the same thing (potential confusion)
- More implementation complexity
- More documentation required
- Slightly larger API surface

### Option 4: Command Palette Integration

**Description:** Add shell commands to the existing command palette (Ctrl+P style), allowing selection and execution without typing full commands.

**User Experience:**
```
> /
[Command palette shows: git status, npm test, etc.]
↓ [Select git status]
[Command executes]
```

**Implementation:**
- Extend command palette to include common shell commands
- Store frequently used commands
- Allow filtering and selection
- Execute via execute_command tool

**Pros:**
- Leverages existing palette UI
- Discoverability of common commands
- No new syntax to learn
- Good for repeated commands

**Cons:**
- Limited to predefined commands
- Doesn't support arbitrary commands
- Requires maintaining command list
- Less flexible than typing
- Awkward for commands with arguments

---

## Decision

**Chosen Option:** Option 3 - Hybrid Approach (Prefix + Mode)

### Rationale

The hybrid approach provides the best of both worlds, supporting different user workflows and preferences:

1. **Maximum Flexibility**: Users can choose their preferred style based on context
   - `!` for quick one-off commands during conversation
   - `/bash` for focused multi-command sessions
2. **Natural Workflow Integration**: Each mechanism serves distinct use cases
   - Quick commands fit the conversational flow
   - Persistent mode supports complex multi-step operations
3. **Progressive Disclosure**: Users can start with simple `!` commands and discover `/bash` mode as needed
4. **Existing Infrastructure**: Fully reuses the execute_command tool and command overlay system
5. **Familiar Patterns**: Both `!` (Jupyter, IPython) and `/bash` (mode-based) are recognized conventions
6. **Future-Proof**: Comprehensive solution that won't need revision

**Implementation Strategy**: Build both features together, ensuring they complement each other:
- `!` prefix works everywhere (even inside bash mode for consistency)
- `/bash` mode simply changes the default behavior (no prefix required)
- Clean mode switching with clear visual indicators

### Implementation Details

**Input Handling Flow (! prefix):**
```
User types: "!git status"
  ↓
TUI detects ! prefix in Update()
  ↓
Extract command: "git status"
  ↓
Call execute_command tool directly
  ↓
Display in command overlay
  ↓
Return to normal input (or bash mode if active)
```

**Input Handling Flow (/bash mode):**
```
User types: "/bash"
  ↓
Activate bash mode (update state)
  ↓
Change prompt to "bash> "
  ↓
User types: "git status"
  ↓
All input treated as shell command (no ! needed)
  ↓
Execute command via execute_command tool
  ↓
Display in command overlay
  ↓
Stay in bash mode until "exit" or Ctrl+D
```

**Code Changes Required:**

1. **pkg/executor/tui/executor.go** (model struct):
   ```go
   type model struct {
       // ... existing fields ...
       bashMode bool // Track if in bash mode
   }
   ```

2. **pkg/executor/tui/executor.go** (Update function):
   ```go
   case tea.KeyEnter:
       input := m.textarea.Value()
       
       // Check for bash mode exit
       if m.bashMode && (input == "exit" || input == "quit") {
           m.bashMode = false
           m.textarea.Reset()
           m.updatePrompt() // Change prompt back to ">"
           return m, nil
       }
       
       // In bash mode, treat everything as a command
       if m.bashMode {
           m.textarea.Reset()
           return executeBashCommand(m, input)
       }
       
       // Check for ! prefix (works outside bash mode)
       if strings.HasPrefix(strings.TrimSpace(input), "!") {
           cmd := strings.TrimSpace(strings.TrimPrefix(input, "!"))
           m.textarea.Reset()
           return executeBashCommand(m, cmd)
       }
       
       // Check for /bash command
       if strings.TrimSpace(input) == "/bash" {
           m.bashMode = true
           m.textarea.Reset()
           m.updatePrompt() // Change prompt to "bash>"
           return m, nil
       }
       
       // Existing slash command handling...
       // Existing agent input handling...
   ```

3. **pkg/executor/tui/bash_commands.go** (new file):
   ```go
   // executeBashCommand executes a shell command directly
   func executeBashCommand(m model, command string) (model, tea.Cmd) {
       if command == "" {
           return m, nil
       }
       
       // Create execute_command tool instance
       // Generate execution ID
       // Send EventTypeCommandExecutionStart
       // Execute command via tool
       // Stream output to overlay
       // Return model with overlay activated
       // Maintain bash mode state
   }
   
   // updatePrompt changes the textarea prompt based on mode
   func (m *model) updatePrompt() {
       if m.bashMode {
           m.textarea.Prompt = "bash> "
           m.textarea.FocusedStyle.Prompt = lipgloss.NewStyle().Foreground(mintGreen)
       } else {
           m.textarea.Prompt = "> "
           m.textarea.FocusedStyle.Prompt = lipgloss.NewStyle().Foreground(salmonPink)
       }
   }
   ```

4. **Command Overlay Integration**:
   - Reuse existing command overlay from ADR-0013
   - Display command and working directory
   - Stream stdout/stderr in real-time
   - Show exit code and duration on completion
   - Return to appropriate mode after overlay dismissed

5. **Status Bar Updates**:
   - Show current mode in status bar
   - Visual indicator when in bash mode (e.g., "[BASH]")

**Security Considerations:**

- All commands execute in the workspace directory (existing behavior)
- Commands are subject to timeout (default 30s, configurable)
- Auto-approval settings apply if configured
- No special privileges - runs with forge's permissions

**User Feedback:**

- Command shown in chat: `🔧 !git status`
- Result summary: `✓ Command completed (exit code: 0, duration: 234ms)`
- Full output available in overlay (press 'v' to view last)

---

## Consequences

### Positive

- **Instant Command Execution**: No agent overhead, immediate results
- **Workflow Continuity**: No need to switch terminals or exit Forge
- **Dual Interface**: 
  - `!` prefix for quick commands during conversation
  - `/bash` mode for focused command sessions
- **Familiar UX**: Both `!` and `/bash` are recognized patterns
- **Flexible Workflow**: Supports both conversational and operational modes
- **Minimal Code**: Reuses 90% of existing infrastructure
- **Discoverable**: Clear progression from `!` to `/bash` mode
- **Safe**: All existing security mechanisms apply
- **Visual Clarity**: Prompt changes indicate current mode

### Negative

- **Slightly More Complex**: Two ways to execute commands (though complementary)
- **Mode Management**: Users must remember to exit bash mode
- **No Environment Persistence**: Cannot set variables across commands (inherent to exec.Command)
- **Limited Shell Features**: No pipes, redirects, job control (acceptable trade-off)
- **Additional State**: bashMode boolean flag to track

### Neutral

- **Non-Interactive Only**: Commands requiring interaction (vim, less) won't work (this is expected)
- **Command History**: Works with existing textarea history mechanism
- **Output Handling**: Uses overlay pattern (consistent with execute_command)

---

## Implementation

### Phase 1: Core Functionality (Week 1)

1. Add `bashMode` boolean to model struct
2. Add `!` prefix detection in Update() function
3. Implement `/bash` slash command handler
4. Implement executeBashCommand() function
5. Add mode-aware prompt handling (updatePrompt())
6. Wire up to execute_command tool
7. Test with common commands (git, npm, go)

### Phase 2: Visual Polish (Week 1)

1. Update status bar to show current mode
2. Change prompt color in bash mode (mint green vs salmon pink)
3. Add visual indicator "[BASH]" in status area
4. Ensure command overlay works in both modes

### Phase 3: Documentation (Week 1)

1. Add to help overlay (`/help` command)
2. Update README with both `!` and `/bash` examples
3. Add examples to getting-started docs
4. Update command palette to show bash commands
5. Document mode switching behavior

### Phase 4: Enhancements (Future)

1. Command history specific to bash commands
2. Common command suggestions in palette
3. Command aliases/shortcuts
4. Working directory tracking per session

### Migration Path

No migration needed - purely additive feature. Existing functionality remains unchanged.

### Timeline

- **Implementation**: 3-4 days (both `!` and `/bash`)
- **Testing**: 1-2 days
- **Documentation**: 1 day
- **Total**: ~1 week for production-ready feature

---

## Validation

### Success Metrics

- **Adoption Rate**: % of sessions that use `!` commands
- **Command Frequency**: Average number of bash commands per session
- **Performance**: Command execution latency < 100ms overhead
- **Error Rate**: % of commands that fail vs. succeed
- **User Feedback**: Satisfaction with feature in user surveys

### Monitoring

- Log bash command usage (anonymized)
- Track common commands (inform palette suggestions)
- Monitor execution times and failures
- Collect user feedback via GitHub issues

### Testing Checklist

**! Prefix Mode:**
- [ ] `!git status` executes and displays output
- [ ] `!npm test` runs and shows results
- [ ] `!echo "test"` handles simple commands
- [ ] `!sleep 5` respects timeout
- [ ] `!invalid-command` shows error gracefully
- [ ] `!` works inside bash mode (explicit override)

**/bash Mode:**
- [ ] `/bash` enters bash mode (prompt changes)
- [ ] Commands execute without `!` prefix in bash mode
- [ ] `exit` command leaves bash mode
- [ ] Ctrl+D leaves bash mode (optional)
- [ ] Status bar shows "[BASH]" indicator
- [ ] Prompt color changes (mint green)

**General:**
- [ ] Security: commands cannot escape workspace
- [ ] Output overlay displays correctly in both modes
- [ ] Command history works with bash commands
- [ ] Multi-line input with `!` prefix
- [ ] Special characters in commands
- [ ] Mode state persists across overlay open/close
- [ ] Agent conversation works normally outside bash mode

---

## Related Decisions

- [ADR-0009](0009-tui-executor-design.md) - TUI Executor Design (base architecture)
- [ADR-0012](0012-enhanced-tui-executor.md) - Enhanced TUI Executor (slash commands)
- [ADR-0013](0013-streaming-command-execution.md) - Streaming Command Execution (overlay pattern)
- [ADR-0010](0010-tool-approval-mechanism.md) - Tool Approval Mechanism (security)

---

## References

- [Jupyter Notebook Magic Commands](https://ipython.readthedocs.io/en/stable/interactive/magics.html) - Uses `!` for shell
- [IPython Shell Access](https://ipython.readthedocs.io/en/stable/interactive/shell.html) - Shell command integration
- [VS Code Integrated Terminal](https://code.visualstudio.com/docs/terminal/basics) - Terminal integration patterns
- [GitHub CLI](https://cli.github.com/) - CLI tool integration examples

---

## Notes

**Design Philosophy:**

The bash mode feature follows Forge's principle of **minimal, intuitive interfaces**. The `!` prefix is:
- **Memorable**: Single character, hard to forget
- **Visible**: Stands out in the input field
- **Standard**: Used by many developer tools
- **Safe**: Explicit opt-in for shell execution

**Alternative Prefixes Considered:**

- `$` - Conflicts with shell variables, less visible
- `>` - Conflicts with shell redirect syntax
- `.` - Too subtle, conflicts with relative paths
- `!` - **CHOSEN** - Clear, standard, unambiguous

**User Personas:**

1. **Quick Command User**: Runs occasional git commands while chatting with agent
   - Uses `!git status`, `!git diff` between questions
   - Values speed and simplicity
   - Stays in conversation mode, uses `!` prefix

2. **Power User**: Runs many commands in sequence
   - Enters `/bash` mode for focused command sessions
   - Executes multiple related commands (git workflow, testing, etc.)
   - Uses `exit` to return to conversation when done

3. **Hybrid User**: Switches between conversation and commands
   - Asks agent a question, then runs `!` commands to verify
   - Enters `/bash` for complex operations
   - Returns to agent with results/questions

4. **Learning User**: Experimenting with commands
   - Benefits from seeing commands in chat history
   - Can ask agent about command output
   - Uses `/bash` to practice command sequences

**FAQ:**

Q: Why not just use the agent to run commands?
A: Agent adds latency (LLM call) and uses tokens. Direct execution is instant.

Q: What's the difference between `!` and `/bash`?
A: `!` is for quick one-off commands during conversation. `/bash` is for focused command sessions where you run multiple related commands.

Q: Can I use `!` inside bash mode?
A: Yes! `!` always works, providing an explicit way to run commands even in bash mode.

Q: Can I run `vim` or other interactive commands?
A: No - interactive commands require TTY allocation, which is not supported.

Q: Will this support pipes like `ls | grep test`?
A: Initially no - commands are executed via exec.Command which doesn't support shell features. This could be added later by wrapping in `sh -c`.

Q: Can I set environment variables?
A: Not across commands - each command runs independently. This is a limitation of exec.Command.

Q: How do I exit bash mode?
A: Type `exit` or `quit`. Alternatively, Ctrl+C or Esc returns to conversation mode.

**Last Updated:** 2025-01-21