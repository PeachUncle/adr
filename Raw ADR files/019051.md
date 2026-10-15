# ADR-0007: Chat UI Framework

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Chat UI Framework" includes component library, streaming client, state management, and fallback strategy).

- **Status:** Accepted
- **Date:** 2025-12-17
- **Feature:** 002-ai-chatbot
- **Context:** Phase 3 requires a real-time chat interface where users can converse with the AI assistant. The UI must support streaming responses (tokens appearing as generated), display tool call activity, handle conversation history, and provide a responsive experience on mobile and desktop. The chat interface must integrate with the existing Next.js + Shadcn/ui frontend architecture while enabling production-ready streaming patterns.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines chat UX pattern and streaming architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - ChatKit, custom Shadcn, react-chat-elements evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects frontend components, state management, and API integration
-->

## Decision

We will adopt the following integrated chat UI framework:

- **Primary Component Library:** OpenAI ChatKit (@openai/chatkit-react)
- **Fallback Strategy:** Custom Shadcn/ui chat components (if ChatKit incompatible)
- **SSE Client:** eventsource-parser for parsing Server-Sent Events
- **State Management:** Zustand store (conversation-store.ts)
- **Landing Behavior:** Load most recent conversation; else show new chat
- **Conversation Management:** Sidebar with kebab menu (Rename/Delete)
- **Production Setup:** Domain allowlist configuration for ChatKit

### Component Architecture

```typescript
// Primary: OpenAI ChatKit (90% of cases)
import { ChatKit, MessageList, MessageInput } from '@openai/chatkit-react';

function ChatInterface({ conversationId }) {
  const { messages, sendMessage, isStreaming } = useConversationStore();

  return (
    <ChatKit>
      <MessageList messages={messages} />
      <MessageInput
        onSend={sendMessage}
        disabled={isStreaming}
      />
    </ChatKit>
  );
}

// Fallback: Custom Shadcn/ui (if ChatKit doesn't work)
import { Card, Input, Button, ScrollArea } from '@/components/ui';

function ChatInterfaceFallback() {
  return (
    <Card>
      <ScrollArea>{/* Message list */}</ScrollArea>
      <Input /><Button>Send</Button>
    </Card>
  );
}
```

### SSE Streaming Pattern

```typescript
// lib/sse/client.ts
import { createParser } from 'eventsource-parser';

export async function streamChat(
  message: string,
  conversationId: number | null,
  onToken: (token: string) => void,
  onToolCall: (call: ToolCall) => void,
  onDone: (data: { conversationId: number }) => void
) {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ conversation_id: conversationId, message }),
  });

  const parser = createParser((event) => {
    if (event.type === 'event') {
      const data = JSON.parse(event.data);
      switch (event.event) {
        case 'token': onToken(data.content); break;
        case 'tool_call': onToolCall(data); break;
        case 'done': onDone(data); break;
      }
    }
  });

  const reader = response.body.getReader();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    parser.feed(new TextDecoder().decode(value));
  }
}
```

### Zustand Conversation Store

```typescript
// stores/conversation-store.ts
interface ConversationStore {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  streamingContent: string;

  // Actions
  fetchConversations: () => Promise<void>;
  selectConversation: (id: number) => Promise<void>;
  createConversation: () => void;
  sendMessage: (content: string) => Promise<void>;
  appendStreamToken: (token: string) => void;
  renameConversation: (id: number, title: string) => Promise<void>;
  deleteConversation: (id: number) => Promise<void>;
}
```

### Rationale

OpenAI ChatKit provides production-ready chat components with built-in streaming support, matching the OpenAI design language. The eventsource-parser library handles SSE parsing correctly across browsers. Zustand provides predictable state management for conversation data. The 90/10 strategy (ChatKit primary, Shadcn fallback) ensures we have a working chat UI regardless of ChatKit compatibility issues. Loading the most recent conversation on chat page visit provides continuity for returning users.

## Consequences

### Positive

- **Production Ready:** ChatKit provides battle-tested chat components
- **Streaming First:** Built-in streaming support matches our SSE backend
- **Consistent Design:** Matches OpenAI design language (familiar to ChatGPT users)
- **Reduced Development Time:** Pre-built components accelerate chat UI development
- **Browser Compatibility:** eventsource-parser handles SSE parsing across browsers
- **State Predictability:** Zustand store manages conversation state cleanly
- **Fallback Safety:** Shadcn/ui fallback ensures chat works if ChatKit fails
- **TypeScript Support:** ChatKit and eventsource-parser are fully typed

### Negative

- **ChatKit Dependency:** Reliance on OpenAI's component library (may change/deprecate)
  - *Mitigation:* Fallback to Shadcn/ui; ChatKit is actively maintained
- **Domain Allowlist:** Production requires configuring ChatKit domain allowlist
  - *Mitigation:* Documented in deployment checklist; localhost works without config
- **Styling Constraints:** ChatKit styling may not perfectly match existing app theme
  - *Mitigation:* ChatKit supports theming; can customize CSS variables
- **Additional Dependencies:** Adds ~50KB for ChatKit + ~10KB for eventsource-parser
  - *Mitigation:* Acceptable for chat feature; can lazy-load chat page
- **Learning Curve:** Team must learn ChatKit component API
  - *Mitigation:* Well-documented; similar to other React component libraries

## Alternatives Considered

### Alternative A: Custom Shadcn/ui Chat Interface (Full Custom)
- **Pros:** Full control, matches existing app design, no external dependency
- **Cons:** Must build streaming UI logic, message rendering, input handling from scratch
- **Why Rejected:** Building production-quality chat UI requires significant development time. ChatKit provides streaming patterns that would take weeks to build correctly. Reserved as fallback only.

### Alternative B: react-chat-elements
- **Pros:** Lightweight, flexible, customizable
- **Cons:** Less polished, no built-in streaming support, dated design
- **Why Rejected:** Lacks streaming support out of box; would require significant customization. ChatKit's streaming integration is more mature.

### Alternative C: Stream Chat (GetStream.io)
- **Pros:** Full-featured chat platform, real-time, enterprise-ready
- **Cons:** Paid service ($99+/month after trial), requires external service, overkill
- **Why Rejected:** Introduces paid third-party dependency; violates free-tier constraint. Our simple AI chat doesn't need full chat platform features.

### Alternative D: WebSockets Instead of SSE
- **Pros:** Bidirectional communication, lower latency, wider support
- **Cons:** More complex implementation, requires connection management, overkill for unidirectional streaming
- **Why Rejected:** SSE is sufficient for server-to-client token streaming; WebSocket bidirectionality is unnecessary. SSE is simpler to implement and debug.

### Alternative E: Native EventSource API
- **Pros:** Browser native, no dependencies
- **Cons:** Limited error handling, doesn't parse event types, inconsistent across browsers
- **Why Rejected:** eventsource-parser provides better event parsing and error handling. Native EventSource is lower-level than needed.

## References

- Feature Spec: [specs/002-ai-chatbot/spec.md](../../specs/002-ai-chatbot/spec.md)
- Implementation Plan: [specs/002-ai-chatbot/plan.md](../../specs/002-ai-chatbot/plan.md) §Phase 5
- Research Notes: [specs/002-ai-chatbot/research.md](../../specs/002-ai-chatbot/research.md) §3, §5, §8
- Related ADRs: ADR-0001 (Frontend Stack - Zustand, Shadcn), ADR-0004 (UI Component Strategy)
- OpenAI ChatKit Documentation: https://platform.openai.com/docs/guides/chatkit
- eventsource-parser: https://www.npmjs.com/package/eventsource-parser
- MDN Server-Sent Events: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
