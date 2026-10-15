# ADR-011: Azure Storage Integration for Permanent Media URLs

## Status
**ACCEPTED** - 2025-08-12

## Context

### User Request
The user requested replacement of ephemeral Discord attachment URLs with permanent URLs from their Azure Blob Storage container: 
> "I'd like to replace the ephemeral Discord URL with a permanent one. My media is hosted in a container in Azure Blob Storage"

### Technical Challenge
Discord attachment URLs are temporary and expire, making them unsuitable for permanent content publishing. The user's preference for relative paths (`/files/images/...`) for domain-mapped containers required flexible URL generation.

### Discord Timeout Constraint
Initial implementation faced Discord's 3-second interaction response timeout when uploading files during modal creation. User provided brilliant strategic insight:
> "What if...the upload to Azure was actually done when I hit submit? Basically during the PR creation process rather than when opening the modal?"

## Decision

### 1. Azure Storage Service Implementation
Implement comprehensive Azure Blob Storage integration with:
- **AzureStorageService**: Complete service with managed identity authentication
- **Flexible URL Generation**: Support for relative paths, SAS tokens, and direct URLs
- **Error Handling**: Graceful fallback to original URLs on upload failures
- **HTTP Client Optimization**: Requests-based implementation for reliable downloads

### 2. Strategic Upload Timing
Move Azure Storage uploads from modal creation to PR creation phase:
- **Modal Performance**: Discord modals open immediately without upload delays
- **Background Processing**: Azure uploads happen during PR creation (no timeout pressure)
- **User Experience**: Seamless modal interaction with permanent URLs generated during publishing
- **Architecture**: Clean separation of real-time UI and background media processing

### 3. Configuration Flexibility
Support multiple Azure Storage URL strategies:
```python
# Domain-mapped containers (user preference)
AZURE_STORAGE_USE_RELATIVE_PATHS=true → "/files/images/filename.jpg"

# SAS token URLs  
AZURE_STORAGE_USE_SAS_TOKENS=true → "https://...blob.core.windows.net/...?sas_token"

# Direct URLs
(both false) → "https://account.blob.core.windows.net/container/filename.jpg"
```

### 4. Publishing Pipeline Integration
Integrate Azure Storage uploads into existing publishing workflow:
- **Discord URL Detection**: Automatic identification of Discord CDN URLs
- **Smart Upload Processing**: Filename extraction and content-type detection
- **URL Replacement**: Seamless replacement in PostData before content generation
- **Backward Compatibility**: Graceful operation when Azure Storage unavailable

## Implementation Details

### Core Service Architecture
```python
class AzureStorageService:
    async def upload_discord_attachment(
        self, 
        discord_url: str, 
        filename: str,
        guild_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> str:
        # Download from Discord, upload to Azure, return permanent URL
```

### Publishing Service Enhancement
```python
async def _process_media_uploads(self, post_data: PostData) -> PostData:
    # Process media uploads during PR creation, not modal creation
    if updated_data.media_url and self._is_discord_url(updated_data.media_url):
        permanent_url = await storage_service.upload_discord_attachment(...)
        updated_data.media_url = permanent_url
    return updated_data
```

### Environment Configuration
```bash
# Azure Container Apps Environment Variables
AZURE_STORAGE_USE_RELATIVE_PATHS=true      # User preference for domain mapping
AZURE_STORAGE_USE_SAS_TOKENS=false         # No SAS tokens needed
ENABLE_AZURE_STORAGE=true                  # Enable Azure Storage integration
AZURE_STORAGE_ACCOUNT_NAME=secretref:azure-storage-account-name
AZURE_STORAGE_CONTAINER_NAME=secretref:azure-storage-container-name
```

## Consequences

### Positive
- **✅ User Requirement Fulfilled**: Ephemeral Discord URLs replaced with permanent Azure Storage URLs
- **✅ Domain Mapping Support**: Clean relative path URLs for domain-mapped containers
- **✅ Performance Excellence**: Discord modals open immediately, no timeout issues
- **✅ Strategic Innovation**: User's timing insight implemented as breakthrough solution
- **✅ Production Integration**: Seamless integration with existing Azure Container Apps deployment
- **✅ Managed Identity**: Enterprise-grade authentication without credential management
- **✅ Error Resilience**: Comprehensive fallback ensuring publishing never fails
- **✅ Configuration Flexibility**: Support for multiple URL generation strategies

### Negative
- **⚠️ Azure Dependency**: Introduces dependency on Azure Storage service
- **⚠️ Upload Latency**: PR creation time slightly increased due to media upload processing
- **⚠️ Storage Costs**: Additional Azure Storage costs for media files
- **⚠️ Complexity**: Increased system complexity with external service integration

### Mitigations
- **Fallback Strategy**: Original URLs preserved if Azure Storage fails
- **Error Handling**: Comprehensive logging and graceful degradation
- **Cost Management**: User controls their own Azure Storage billing
- **Documentation**: Complete setup and troubleshooting guides provided

## Alternatives Considered

### 1. Discord URL Retention (Rejected)
**Reason**: Discord URLs are ephemeral and expire, making them unsuitable for permanent content

### 2. GitHub Large File Storage (Rejected)
**Reason**: User specifically requested Azure Storage integration with their existing infrastructure

### 3. Modal Upload Timing (Rejected)
**Reason**: Discord 3-second timeout constraint makes modal upload timing impractical

### 4. Third-Party CDN (Rejected)
**Reason**: User already has Azure Storage infrastructure and prefers self-hosted solution

## References

- **User Original Request**: Permanent Azure Storage URLs to replace ephemeral Discord URLs
- **Strategic Timing Insight**: User's breakthrough suggestion about upload timing during submission
- **Azure Documentation**: Azure Blob Storage best practices and managed identity authentication
- **Discord API Constraints**: 3-second interaction response timeout requirements
- **Implementation PR**: GitHub PR demonstrating complete Azure Storage integration

## Decision Makers
- **Primary**: User requirement and strategic insight
- **Technical**: Development team implementation following user specifications
- **Deployment**: Azure Container Apps production validation

## Date: 2025-08-12
**Author**: Development Team  
**Reviewers**: User feedback and production validation  
**Status**: Accepted and Implemented ✅
