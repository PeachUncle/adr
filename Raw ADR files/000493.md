# ADR-002: Enhanced Campaign Creation with Multimodal AI Analysis

**Author: JP + 2025-06-15**
**Status**: Accepted
**Date**: 2025-06-15

## Context

The initial campaign creation flow required users to manually input all business context, leading to:
- Time-consuming manual data entry
- Inconsistent or incomplete business descriptions
- Limited context for AI to generate relevant campaigns
- Poor user experience for campaign managers

User feedback indicated need for:
- Automated business context extraction
- File upload capabilities for visual and document analysis
- Control over AI creativity levels
- Campaign type specialization

## Decision

We will implement an enhanced campaign creation system with:

### 1. Smart Business Analysis
- **URL Analysis**: Scrape and analyze business websites, about pages, product pages
- **Automated Context Extraction**: Extract business purpose, sector, locality, target audience
- **Reduced Manual Input**: Auto-populate business description from URL analysis

### 2. Multimodal File Processing
- **Image Analysis**: Gemini Vision API for product/brand image analysis
- **Document Processing**: PDF/DOC parsing for detailed specifications
- **Campaign Asset Analysis**: Existing materials for style consistency
- **Visual Direction**: Extract design preferences from uploaded images

### 3. AI Creativity Controls
- **Creativity Dial**: 1-10 scale for controlling AI experimental vs. conservative approach
- **Campaign Type Specialization**: Different AI prompts for product/service/brand/event campaigns
- **Temperature Control**: Adjust AI creativity based on user preference

### 4. Enhanced User Experience
- **Progressive Disclosure**: Show advanced options only when needed
- **Smart Defaults**: Pre-select reasonable values based on analysis
- **Visual Feedback**: Show analysis progress and results
- **Fallback Options**: Manual input available if automated analysis fails

## Technical Implementation

### Frontend Enhancements
```typescript
interface EnhancedCampaign extends Campaign {
  businessUrl?: string;
  aboutPageUrl?: string;
  productServiceUrl?: string;
  campaignType: 'product' | 'service' | 'brand' | 'event';
  creativityLevel: number; // 1-10
  uploadedImages: File[];
  uploadedDocuments: File[];
  campaignAssets: File[];
}
```

### Backend API Endpoints
```
POST /api/v1/campaigns/analyze-url     - URL scraping and analysis
POST /api/v1/campaigns/analyze-files   - File upload and processing
POST /api/v1/campaigns/create-enhanced - Enhanced campaign creation
```

### AI Agent Architecture
```python
class CampaignPreparationAgent:
    def analyze_business_url(self, url: str) -> BusinessContext
    def analyze_uploaded_files(self, files: List[File]) -> FileAnalysis
    def extract_visual_direction(self, images: List[Image]) -> VisualStyle
    def generate_enhanced_context(self, context: EnhancedContext) -> CampaignContext
```

## Consequences

### Positive
- **Improved UX**: Significantly reduced manual input required
- **Better AI Context**: More comprehensive business understanding for AI
- **Multimodal Capabilities**: Leverage Gemini's vision and document processing
- **User Control**: Creativity dial gives users control over AI behavior
- **Campaign Specialization**: Type-specific prompts improve relevance

### Negative
- **Increased Complexity**: More backend processing and error handling required
- **File Storage**: Need to handle file uploads and temporary storage
- **API Dependencies**: Reliance on external URL scraping and file processing
- **Performance**: URL analysis and file processing add latency

### Risks
- **URL Scraping Failures**: Websites may block or limit scraping
- **File Processing Errors**: Corrupted or unsupported file formats
- **Privacy Concerns**: Handling of uploaded business documents
- **Cost Implications**: Increased Gemini API usage for multimodal processing

## Alternatives Considered

### 1. Manual Input Only
- **Pros**: Simple, no external dependencies
- **Cons**: Poor UX, limited AI context, time-consuming

### 2. URL Analysis Only
- **Pros**: Automated context extraction
- **Cons**: Limited to web-available information, no visual analysis

### 3. File Upload Only
- **Pros**: Rich context from documents/images
- **Cons**: Still requires manual URL input, no web scraping

## Implementation Plan

### Phase 1: Backend API Foundation
1. Create FastAPI service with file upload support
2. Implement URL scraping with BeautifulSoup
3. Add Gemini multimodal analysis endpoints

### Phase 2: Frontend Integration
1. Enhanced campaign creation form
2. File upload components with progress indicators
3. URL analysis integration with loading states

### Phase 3: AI Enhancement
1. Campaign type specialization
2. Creativity level controls
3. Visual style analysis from images

### Phase 4: Testing & Optimization
1. End-to-end testing with real URLs and files
2. Performance optimization for file processing
3. Error handling and fallback mechanisms

## Success Metrics

- **Reduced Input Time**: <50% of original manual input time
- **Improved AI Relevance**: User satisfaction scores for generated content
- **Feature Adoption**: % of users using URL analysis vs. manual input
- **Processing Success Rate**: % of successful URL/file analysis operations

## Related ADRs

- ADR-001: Technology Stack Selection
- Future ADR: Data Privacy and Security for File Uploads
- Future ADR: Caching Strategy for URL Analysis Results