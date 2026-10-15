# ADR-003: AI Service Integration

## Status
Accepted

## Context
The Recipe Keeper application requires AI capabilities to:
- Extract recipe information from photos of food/recipes
- Parse and structure recipe data from URLs
- Generate missing recipe information (nutrition, prep time estimates)
- Provide intelligent search and recommendations

We needed to choose an AI service that provides:
- Vision capabilities for photo analysis
- Text processing for URL content extraction
- Good API reliability and uptime
- Reasonable pricing for expected usage
- Strong developer experience

## Considered Options

### Option 1: Google Gemini API
- **Vision**: Gemini Pro Vision for image analysis
- **Text**: Gemini Pro for text processing
- **Pricing**: $0.00025 per 1K characters
- **Rate Limits**: 60 requests per minute (free tier)
- **Pros**: Cutting-edge capabilities, good documentation, Google reliability
- **Cons**: Newer service, higher cost at scale

### Option 2: OpenAI GPT-4 Vision
- **Vision**: GPT-4 Vision for image analysis
- **Text**: GPT-4 for text processing
- **Pricing**: $0.01 per 1K tokens (vision), $0.03 per 1K tokens (text)
- **Rate Limits**: 500 requests per minute
- **Pros**: Proven capabilities, excellent documentation, mature ecosystem
- **Cons**: Higher cost, OpenAI dependency

### Option 3: Anthropic Claude
- **Vision**: Claude 3 Vision for image analysis
- **Text**: Claude 3 for text processing
- **Pricing**: $0.25 per 1K tokens (vision), $0.25 per 1K tokens (text)
- **Rate Limits**: Variable based on plan
- **Pros**: Strong safety features, good reasoning
- **Cons**: Higher cost, limited vision capabilities

### Option 4: AWS Rekognition + Comprehend
- **Vision**: Rekognition for image analysis
- **Text**: Comprehend for text processing
- **Pricing**: $0.0012 per image (Rekognition), $0.0001 per character (Comprehend)
- **Rate Limits**: High throughput
- **Pros**: AWS reliability, lower cost at scale
- **Cons**: Less sophisticated for recipe understanding, multiple services

### Option 5: Custom ML Models
- **Vision**: Custom vision model for recipe detection
- **Text**: Custom NLP model for recipe parsing
- **Pricing**: Infrastructure costs only
- **Rate Limits**: Based on infrastructure
- **Pros**: Complete control, no external dependencies
- **Cons**: High development cost, maintenance burden, limited capabilities

## Decision

We chose **Google Gemini API** (specifically Gemini 2.0 Flash) as our AI service provider.

### Rationale

1. **Unified API**: Single service for both vision and text processing
2. **Performance**: Excellent results for recipe understanding from images
3. **Cost Effective**: Competitive pricing for startup/prototype phase
4. **Developer Experience**: Well-documented SDK and examples
5. **Reliability**: Google's infrastructure and uptime guarantees
6. **Features**: Built-in safety filters and content moderation
7. **Flexibility**: Good support for structured output (JSON)

## Implementation Strategy

### Service Architecture
```typescript
// AI Service Layer
interface AIService {
  analyzeRecipePhoto(imageBuffer: Buffer): Promise<RecipeData>;
  extractRecipeFromUrl(url: string): Promise<RecipeData>;
  enhanceRecipeData(recipe: Partial<RecipeData>): Promise<RecipeData>;
}

// Gemini Implementation
class GeminiAIService implements AIService {
  private client: GoogleGenerativeAI;
  private model: GenerativeModel;
}
```

### Photo Analysis Flow
1. **Image Upload**: User uploads photo via frontend
2. **Preprocessing**: Resize/optimize image if needed
3. **AI Analysis**: Send to Gemini with structured prompt
4. **Response Parsing**: Parse JSON response to recipe format
5. **Validation**: Validate extracted data structure
6. **User Review**: Present data for user confirmation/editing

### URL Extraction Flow
1. **URL Input**: User provides recipe URL
2. **Content Scraping**: Extract webpage content using Puppeteer
3. **Content Cleaning**: Remove ads, navigation, irrelevant content
4. **AI Processing**: Send clean content to Gemini
5. **Response Parsing**: Parse JSON response to recipe format
6. **Validation**: Validate extracted data structure
7. **User Review**: Present data for user confirmation/editing

### Prompt Engineering

#### Photo Analysis Prompt
```javascript
const photoPrompt = `
Analyze this food/recipe photo and extract recipe information. Return a JSON object with:
- title: Recipe name (string)
- servings: Number of servings (number)
- prepTime: Preparation time in minutes (number)
- cookTime: Cooking time in minutes (number)
- difficulty: "easy", "medium", or "hard" (string)
- ingredients: Array of {quantity: string, unit: string, item: string}
- directions: Array of {step: number, instruction: string}
- nutrition: {calories: number, protein: number, carbohydrates: number, fat: number, fiber: number, sodium: number}
- tags: Array of relevant tags (strings)

If information is not visible, make reasonable estimates based on the dish type and typical recipes.
Ensure all fields are present and properly formatted.
`;
```

#### URL Extraction Prompt
```javascript
const urlPrompt = `
Extract recipe information from this webpage content. Return a JSON object with the same structure as the photo analysis.
Focus on finding:
- Recipe title and description
- Ingredient list with quantities
- Step-by-step instructions
- Cooking/prep times
- Serving information
- Nutritional data if available

Parse various recipe formats (JSON-LD, microdata, plain text) and return standardized structure.
`;
```

## Error Handling & Resilience

### Rate Limiting
- Implement exponential backoff for API calls
- Queue requests during high traffic
- Graceful degradation when limits exceeded
- User feedback for processing delays

### Fallback Strategies
- Cache common responses to reduce API calls
- Provide manual entry when AI fails
- Retry with simplified prompts on errors
- Graceful error messages for users

### Monitoring & Logging
- Track API usage and costs
- Monitor success/failure rates
- Log errors for debugging
- Performance metrics for optimization

## Consequences

### Positive
- **User Experience**: Seamless recipe import from photos and URLs
- **Efficiency**: Rapid data extraction reduces manual entry
- **Accuracy**: AI provides consistent, structured data
- **Scalability**: Cloud-based service handles traffic spikes
- **Maintenance**: No need to maintain custom ML models
- **Features**: Rich capabilities for recipe understanding

### Negative
- **Cost**: Usage-based pricing can scale with user adoption
- **Dependency**: External service dependency and potential downtime
- **Privacy**: Recipe data sent to external service
- **Rate Limits**: API limits may constrain usage during peak times
- **Accuracy**: AI may misinterpret complex recipes or images
- **Vendor Lock-in**: Switching providers requires significant refactoring

### Neutral
- **Internet Dependency**: Requires internet connection for AI features
- **Latency**: Network calls add processing time
- **Complexity**: Additional error handling and monitoring needed

## Implementation Details

### Configuration
```typescript
interface AIConfig {
  apiKey: string;
  model: string;
  rateLimitPerMinute: number;
  timeout: number;
  retryAttempts: number;
  cacheEnabled: boolean;
}
```

### Caching Strategy
- Cache successful responses for 24 hours
- Use content hash as cache key
- Implement cache invalidation for updates
- Store in Redis for distributed caching

### Security Measures
- API key rotation and secure storage
- Input validation and sanitization
- Rate limiting per user/IP
- Content filtering for inappropriate images
- HTTPS for all API communications

### Performance Optimization
- Compress images before sending
- Batch multiple requests when possible
- Implement request deduplication
- Use streaming for large responses
- Monitor and optimize prompt efficiency

## Cost Management

### Pricing Model
- Free tier: 60 requests per minute
- Paid tier: $0.00025 per 1K characters
- Estimated cost: $0.01-0.05 per recipe extraction

### Usage Optimization
- Implement intelligent caching
- Optimize prompt length
- Use batch processing where possible
- Monitor and alert on usage spikes
- Implement user-based rate limiting

## Related ADRs
- [ADR-001: Technology Stack Selection](./001-technology-stack.md)
- [ADR-002: Database Schema Design](./002-database-schema.md)

## Review Date
This decision should be reviewed if:
- Costs exceed budget projections
- Service reliability issues arise
- Better alternatives become available
- User feedback indicates poor AI accuracy
- Rate limits become constraining