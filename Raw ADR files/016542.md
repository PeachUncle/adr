# ADR-006: LLM Provider Abstraction Layer

## Status

**Accepted** - January 2026

## Context

Sentinel RFP relies heavily on Large Language Models for:

- Response generation (primary value)
- Query planning and decomposition
- Response review and scoring
- Embeddings generation
- Document OCR (Vision)

We need to decide how to integrate with LLM providers:

1. **Direct integration**: Call provider APIs directly
2. **LangChain**: Use LangChain abstraction
3. **Custom abstraction**: Build our own provider abstraction
4. **Hybrid**: Mix of approaches

### Requirements

- Support multiple providers (Anthropic, OpenAI)
- Easy provider switching (fallback, A/B testing)
- Cost tracking per tenant
- Rate limiting and retry logic
- Zero data retention guarantees
- Streaming support for UX
- Type-safe API

## Decision

**Build a custom LLM abstraction layer without LangChain dependency.**

### Rationale

| Factor         | LangChain         | Custom          | Winner |
| -------------- | ----------------- | --------------- | ------ |
| Type Safety    | Partial           | Full TypeScript | Custom |
| Bundle Size    | Large (100+ deps) | Minimal         | Custom |
| Control        | Limited           | Full            | Custom |
| Learning Curve | High              | Low (our code)  | Custom |
| Updates        | External          | Internal        | Custom |
| Debugging      | Complex chains    | Simple          | Custom |
| Testing        | Hard to mock      | Easy            | Custom |

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM ABSTRACTION LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                         ┌─────────────────┐                         │
│                         │   LLM Service   │                         │
│                         │   (Interface)   │                         │
│                         └────────┬────────┘                         │
│                                  │                                   │
│                    ┌─────────────┼─────────────┐                    │
│                    │             │             │                    │
│                    ▼             ▼             ▼                    │
│           ┌───────────────┐ ┌───────────────┐ ┌───────────────┐    │
│           │   Anthropic   │ │    OpenAI     │ │  Self-Hosted  │    │
│           │   Provider    │ │   Provider    │ │   Provider    │    │
│           │               │ │               │ │   (Future)    │    │
│           │ • Claude 3.5  │ │ • GPT-4o      │ │               │    │
│           │ • Claude 3    │ │ • GPT-4       │ │ • Llama       │    │
│           │   Opus        │ │ • GPT-3.5     │ │ • Mistral     │    │
│           └───────────────┘ └───────────────┘ └───────────────┘    │
│                    │             │             │                    │
│                    └─────────────┼─────────────┘                    │
│                                  │                                   │
│                    ┌─────────────┴─────────────┐                    │
│                    │                           │                    │
│                    ▼                           ▼                    │
│           ┌───────────────┐           ┌───────────────┐            │
│           │    Router     │           │    Cache      │            │
│           │               │           │               │            │
│           │ • Fallback    │           │ • Semantic    │            │
│           │ • Load balance│           │ • Response    │            │
│           │ • A/B test    │           │ • Embedding   │            │
│           └───────────────┘           └───────────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

#### Core Interface

```typescript
// packages/ai/src/types.ts
export interface LLMProvider {
  readonly name: string;
  readonly supportedModels: string[];

  complete(request: CompletionRequest): Promise<CompletionResponse>;
  stream(request: CompletionRequest): AsyncGenerator<StreamChunk>;
  embed(request: EmbeddingRequest): Promise<EmbeddingResponse>;
}

export interface CompletionRequest {
  model: string;
  messages: Message[];
  temperature?: number;
  maxTokens?: number;
  stopSequences?: string[];
  tools?: Tool[];
  metadata?: {
    tenantId: string;
    requestId: string;
    feature: string;
  };
}

export interface CompletionResponse {
  id: string;
  content: string;
  model: string;
  usage: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
  };
  stopReason: 'end_turn' | 'max_tokens' | 'tool_use';
  latencyMs: number;
}
```

#### Anthropic Provider

```typescript
// packages/ai/src/providers/anthropic.provider.ts
import Anthropic from '@anthropic-ai/sdk';

export class AnthropicProvider implements LLMProvider {
  readonly name = 'anthropic';
  readonly supportedModels = [
    'claude-3-5-sonnet-20241022',
    'claude-3-opus-20240229',
    'claude-3-haiku-20240307',
  ];

  private client: Anthropic;

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }

  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    const start = Date.now();

    const response = await this.client.messages.create({
      model: request.model,
      max_tokens: request.maxTokens ?? 4096,
      temperature: request.temperature ?? 0.3,
      messages: this.mapMessages(request.messages),
      stop_sequences: request.stopSequences,
    });

    return {
      id: response.id,
      content: this.extractContent(response),
      model: response.model,
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
        totalTokens: response.usage.input_tokens + response.usage.output_tokens,
      },
      stopReason: this.mapStopReason(response.stop_reason),
      latencyMs: Date.now() - start,
    };
  }

  async *stream(request: CompletionRequest): AsyncGenerator<StreamChunk> {
    const stream = await this.client.messages.stream({
      model: request.model,
      max_tokens: request.maxTokens ?? 4096,
      messages: this.mapMessages(request.messages),
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta') {
        yield {
          type: 'delta',
          content: event.delta.text,
        };
      }
    }

    const finalMessage = await stream.finalMessage();
    yield {
      type: 'done',
      usage: {
        inputTokens: finalMessage.usage.input_tokens,
        outputTokens: finalMessage.usage.output_tokens,
      },
    };
  }
}
```

#### Router with Fallback

```typescript
// packages/ai/src/router.ts
export class LLMRouter {
  private providers: Map<string, LLMProvider>;
  private fallbackChain: string[];

  constructor(config: RouterConfig) {
    this.providers = new Map();
    this.fallbackChain = config.fallbackChain;

    // Initialize providers
    if (config.anthropicKey) {
      this.providers.set('anthropic', new AnthropicProvider(config.anthropicKey));
    }
    if (config.openaiKey) {
      this.providers.set('openai', new OpenAIProvider(config.openaiKey));
    }
  }

  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    const provider = this.selectProvider(request.model);

    for (const providerName of this.fallbackChain) {
      try {
        const provider = this.providers.get(providerName);
        if (!provider) continue;

        return await this.withRetry(() => provider.complete(request));
      } catch (error) {
        this.logger.warn(`Provider ${providerName} failed, trying fallback`, { error });
        continue;
      }
    }

    throw new Error('All LLM providers failed');
  }

  private async withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        if (!this.isRetryable(error)) throw error;
        await this.delay(Math.pow(2, attempt) * 100);
      }
    }

    throw lastError;
  }
}
```

#### Cost Tracking

```typescript
// packages/ai/src/cost-tracker.ts
export class CostTracker {
  // Pricing per 1M tokens (as of Jan 2026)
  private pricing = {
    'claude-3-5-sonnet-20241022': { input: 3.0, output: 15.0 },
    'claude-3-opus-20240229': { input: 15.0, output: 75.0 },
    'gpt-4o': { input: 5.0, output: 15.0 },
    'gpt-4o-mini': { input: 0.15, output: 0.6 },
    'text-embedding-3-large': { input: 0.13, output: 0 },
  };

  trackUsage(tenantId: string, model: string, usage: TokenUsage): void {
    const price = this.pricing[model];
    if (!price) return;

    const cost =
      (usage.inputTokens / 1_000_000) * price.input +
      (usage.outputTokens / 1_000_000) * price.output;

    this.emit('llm.usage', {
      tenantId,
      model,
      inputTokens: usage.inputTokens,
      outputTokens: usage.outputTokens,
      costUsd: cost,
      timestamp: new Date(),
    });
  }
}
```

### Model Selection Strategy

```typescript
const MODEL_ROUTING = {
  // High-stakes tasks: Use best model
  'response.generation': {
    primary: 'claude-3-5-sonnet-20241022',
    fallback: 'gpt-4o',
  },

  // Planning: Good reasoning needed
  'query.planning': {
    primary: 'claude-3-5-sonnet-20241022',
    fallback: 'gpt-4o',
  },

  // Review: Needs careful analysis
  'response.review': {
    primary: 'claude-3-5-sonnet-20241022',
    fallback: 'gpt-4o',
  },

  // Classification: Simple task, use cheaper
  'query.classification': {
    primary: 'gpt-4o-mini',
    fallback: 'claude-3-haiku-20240307',
  },

  // Embeddings: OpenAI best price/quality
  'text.embedding': {
    primary: 'text-embedding-3-large',
    fallback: null, // No fallback, critical
  },

  // Vision/OCR: GPT-4o Vision superior
  'document.ocr': {
    primary: 'gpt-4o',
    fallback: 'claude-3-5-sonnet-20241022',
  },
};
```

## Consequences

### Positive

- **Full control**: Customize behavior exactly as needed
- **Type safety**: 100% TypeScript, full IDE support
- **Small footprint**: No LangChain dependency tree
- **Easy testing**: Simple mocking, no complex chains
- **Cost visibility**: Built-in tracking per tenant
- **Fast iteration**: Change logic without library updates

### Negative

- **Maintenance**: Must maintain provider integrations
- **Missing features**: No LangChain ecosystem (chains, agents)
- **Updates**: Must track API changes manually

### Mitigations

- Official SDKs handle most complexity
- Build only what we need (YAGNI)
- Automated tests catch API changes
- Document integration patterns

## Caching Strategy

```typescript
// Semantic caching for similar queries
const cache = new SemanticCache({
  similarityThreshold: 0.95,
  ttl: 3600, // 1 hour
});

async function cachedComplete(request: CompletionRequest) {
  const cacheKey = await cache.findSimilar(request.messages);
  if (cacheKey) {
    metrics.increment('llm.cache.hit');
    return cache.get(cacheKey);
  }

  const response = await router.complete(request);
  await cache.set(request.messages, response);

  return response;
}
```

## Related ADRs

- ADR-002: Multi-Agent RAG Architecture
- ADR-003: Vector Storage Strategy

## References

- [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript)
- [OpenAI TypeScript SDK](https://github.com/openai/openai-node)
- [LLM Caching Strategies](https://www.anthropic.com/news/prompt-caching)
