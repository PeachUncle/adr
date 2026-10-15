# ADR-003: AI Service Provider - Azure OpenAI

## Status
Accepted

## Context
The core functionality of the ESRI App Finder & Builder Assistant relies on conversational AI to understand user problems and recommend appropriate ESRI applications. We need to select an AI service provider that:
- Provides state-of-the-art large language models (GPT-4 class)
- Offers reliable, low-latency API access
- Complies with enterprise security and compliance requirements
- Integrates well with our Azure infrastructure
- Provides cost-effective pricing for our expected usage
- Supports streaming responses for better UX
- Has strong documentation and community support

## Decision
We will use **Azure OpenAI Service with GPT-4** as our AI service provider.

### Configuration
- **Model**: GPT-4 (gpt-4 or gpt-4-32k depending on availability)
- **Deployment**: Dedicated deployment in our Azure subscription
- **Region**: East US or similar (closest to target users)
- **Temperature**: 0.7 (balance between creativity and consistency)
- **Max Tokens**: 800 per response (sufficient for recommendations)
- **Streaming**: Enabled for real-time chat experience

## Consequences

### Positive
1. **Enterprise Compliance**: Azure OpenAI is enterprise-ready with SOC 2, HIPAA, and other certifications
2. **Data Privacy**: Data stays within Azure tenant, not used to train OpenAI models
3. **Infrastructure Integration**: Seamless integration with other Azure services (Key Vault, Monitor, etc.)
4. **SLA Guarantees**: 99.9% uptime SLA with Azure support
5. **Cost Management**: Predictable pricing, integrated Azure billing
6. **Low Latency**: Dedicated deployment reduces latency vs. public OpenAI API
7. **Content Filtering**: Built-in content filtering for safety
8. **Rate Limits**: Higher rate limits than public API
9. **Regional Deployment**: Can deploy in specific regions for compliance
10. **GPT-4 Access**: Reliable access to latest GPT-4 models

### Negative
1. **Cost**: Slightly more expensive than public OpenAI API (~10-20% higher)
2. **Azure Lock-in**: Harder to switch to other providers
3. **Deployment Approval**: Requires Azure OpenAI access approval (can take days)
4. **Limited Model Selection**: Only models approved by Microsoft available
5. **Regional Availability**: Not all regions support all models

## Alternatives Considered

### 1. **OpenAI Public API**
- **Pros**:
  - Easiest to get started
  - Latest models available first
  - Slightly lower cost per token
  - No approval process
- **Cons**:
  - Data used to improve OpenAI models (opt-out available but complex)
  - No Azure integration
  - No enterprise SLA
  - Higher latency (shared infrastructure)
  - Rate limits harder to scale
  - Less compliance guarantees
- **Why Rejected**: Data privacy concerns and lack of enterprise compliance make it unsuitable for production.

### 2. **Anthropic Claude (via AWS Bedrock)**
- **Pros**:
  - Excellent performance on complex reasoning
  - Strong safety features
  - Competitive pricing
- **Cons**:
  - Requires AWS account (different cloud provider)
  - Less mature Azure integration
  - Smaller developer community
  - No direct Azure support
- **Why Rejected**: Multi-cloud complexity not worth it for v1. Prefer Azure-native solution.

### 3. **Google Vertex AI (PaLM/Gemini)**
- **Pros**:
  - Competitive performance
  - Good for specific tasks
- **Cons**:
  - Requires GCP account (different cloud provider)
  - Less mature than GPT-4
  - No Azure integration
  - Smaller ecosystem
- **Why Rejected**: Multi-cloud complexity. GPT-4 is more mature for our use case.

### 4. **Open Source LLMs (Llama 2, Mistral, etc.)**
- **Pros**:
  - Full control
  - No per-token costs after deployment
  - No vendor lock-in
  - Can fine-tune
- **Cons**:
  - Require significant infrastructure (GPU clusters)
  - Performance not yet at GPT-4 level for our tasks
  - High maintenance overhead
  - Slower inference times
  - Complex deployment
- **Why Rejected**: Not practical for v1. GPT-4 quality is essential for good user experience.

### 5. **Azure AI Studio with Open Models**
- **Pros**:
  - Azure-native
  - Can use open source models
  - Lower per-token costs
- **Cons**:
  - Still requires infrastructure management
  - Not as performant as GPT-4
  - More complex setup
- **Why Rejected**: Azure OpenAI provides better balance of performance and simplicity.

## Implementation Details

### Azure OpenAI Setup

#### 1. Resource Creation
```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name esri-assistant-openai \
  --resource-group esri-assistant-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

#### 2. Model Deployment
```bash
# Deploy GPT-4 model
az cognitiveservices account deployment create \
  --name esri-assistant-openai \
  --resource-group esri-assistant-rg \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --scale-settings-capacity 10
```

### Integration Code

#### Environment Configuration
```typescript
// config/openai.config.ts
export const openAIConfig = {
  endpoint: process.env.AZURE_OPENAI_ENDPOINT!,
  apiKey: process.env.AZURE_OPENAI_API_KEY!,
  deploymentName: process.env.AZURE_OPENAI_DEPLOYMENT_NAME || 'gpt-4',
  apiVersion: '2024-02-15-preview',
  maxTokens: 800,
  temperature: 0.7,
  topP: 0.95,
  frequencyPenalty: 0,
  presencePenalty: 0
};
```

#### Service Implementation
```typescript
// services/ai.service.ts
import { OpenAIClient, AzureKeyCredential } from '@azure/openai';
import { openAIConfig } from '../config/openai.config';

export class AIService {
  private client: OpenAIClient;

  constructor() {
    this.client = new OpenAIClient(
      openAIConfig.endpoint,
      new AzureKeyCredential(openAIConfig.apiKey)
    );
  }

  async generateRecommendations(userMessage: string, context?: any) {
    const messages = [
      {
        role: 'system',
        content: this.getSystemPrompt()
      },
      ...this.buildContextMessages(context),
      {
        role: 'user',
        content: userMessage
      }
    ];

    const response = await this.client.getChatCompletions(
      openAIConfig.deploymentName,
      messages,
      {
        maxTokens: openAIConfig.maxTokens,
        temperature: openAIConfig.temperature,
        topP: openAIConfig.topP
      }
    );

    return this.parseResponse(response);
  }

  async generateStreamingResponse(userMessage: string, context?: any) {
    // Streaming implementation for real-time chat
    const messages = this.buildMessages(userMessage, context);
    
    const stream = await this.client.streamChatCompletions(
      openAIConfig.deploymentName,
      messages,
      {
        maxTokens: openAIConfig.maxTokens,
        temperature: openAIConfig.temperature
      }
    );

    return stream;
  }

  private getSystemPrompt(): string {
    return `You are an expert assistant helping users choose the right ESRI configurable application from a list of 12 options:

1. Instant Apps (various templates)
2. Web AppBuilder
3. Experience Builder
4. Dashboards
5. StoryMaps
6. Survey123
7. Collector
8. Explorer
9. Navigator
10. QuickCapture
11. Field Maps
12. Workforce

Your role is to:
- Understand the user's problem or goal
- Recommend 1-3 most relevant applications
- Explain why each app fits their use case
- Suggest specific features or capabilities
- Guide them toward creating a web map with appropriate data

Be concise, friendly, and avoid GIS jargon. Focus on business value, not technical details.`;
  }

  private buildContextMessages(context?: any) {
    // Build conversation history from context
    return [];
  }

  private parseResponse(response: any) {
    // Parse and structure the AI response
    const content = response.choices[0]?.message?.content;
    
    return {
      content,
      recommendations: this.extractRecommendations(content),
      suggestedActions: this.extractActions(content)
    };
  }

  private extractRecommendations(content: string) {
    // Extract structured app recommendations from AI response
    // Use regex or prompt engineering to get structured data
    return [];
  }

  private extractActions(content: string) {
    // Extract suggested next actions
    return [];
  }
}
```

### Prompt Engineering Strategy

#### System Prompt
```
You are an expert ESRI application advisor helping non-technical users choose the right configurable application. You have deep knowledge of 12 ESRI applications and their capabilities.

Your responses should:
1. Recommend 1-3 applications that best fit the user's described problem
2. Explain in 2-3 sentences why each app is a good fit
3. List 3-4 key capabilities relevant to their use case
4. Suggest next steps (create map, search for data, etc.)

Avoid:
- GIS jargon or technical terms
- Recommending too many options (max 3)
- Generic descriptions that could apply to any app

Format your recommendations as:
**App Name**: [Brief explanation]
- Capability 1
- Capability 2
- Capability 3
```

#### Few-Shot Examples
Include 3-5 example interactions in the system prompt to guide the model.

## Cost Analysis

### Pricing (Azure OpenAI GPT-4)
- **Input tokens**: ~$0.03 per 1K tokens
- **Output tokens**: ~$0.06 per 1K tokens

### Expected Usage (per month)
- **Users**: 1000 active users
- **Messages per user**: 10 messages per session
- **Average tokens per message**:
  - Input: 500 tokens (system prompt + user message)
  - Output: 400 tokens (recommendations)
- **Total monthly tokens**: 
  - Input: 1000 × 10 × 500 = 5M tokens = $150
  - Output: 1000 × 10 × 400 = 4M tokens = $240
- **Total**: ~$390/month at moderate usage

### Cost Optimization Strategies
1. **Caching**: Cache common recommendations
2. **Prompt Optimization**: Reduce system prompt length
3. **Response Limits**: Cap max tokens at 800
4. **Rate Limiting**: Prevent abuse
5. **Lazy Loading**: Only call AI when necessary

## Security Considerations

### API Key Management
- Store keys in **Azure Key Vault**
- Rotate keys quarterly
- Use managed identities where possible

### Content Filtering
- Enable Azure OpenAI content filtering
- Block harmful/inappropriate content
- Log filtered requests for review

### Rate Limiting
- Implement per-user rate limits
- Monitor for abuse patterns
- Alert on anomalies

### Data Privacy
- Don't log sensitive user messages
- Ensure GDPR compliance
- Data stays in Azure tenant

## Monitoring & Observability

### Key Metrics
- Token usage (input/output)
- Response latency
- Error rates
- Content filter hits
- Cost per day/week/month

### Alerts
- High error rates (>5%)
- Slow responses (>5 seconds)
- Budget overruns
- Content filter anomalies

### Tools
- Azure Monitor
- Application Insights
- Custom dashboards

## Future Considerations

### Model Upgrades
- Monitor for GPT-4 Turbo availability
- Test newer models in staging
- Gradual rollout of model updates

### Fine-Tuning (Future)
- Collect user feedback
- Fine-tune on ESRI-specific conversations
- Improve recommendation accuracy

### Alternative Models (Fallback)
- Have GPT-3.5-Turbo as cost-effective fallback
- Implement model selection based on query complexity

## References
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure OpenAI REST API Reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)
- [GPT-4 Model Card](https://platform.openai.com/docs/models/gpt-4)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)

## Related ADRs
- [ADR-002: Backend Architecture](./002-backend-architecture.md)

---
**Date**: 2025-11-05  
**Author**: Development Team  
**Status**: Accepted
