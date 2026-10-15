# ADR 005: .NET Migration with Clean Architecture

## Status
Accepted

## Date
2025-11-30

## Context
The Node.js backend implementation served as a rapid prototype but has limitations for production scalability, particularly around file processing and resource management. As the system grows, we need:

1. **Better file handling**: Large CNAB file uploads (potentially GB-sized) require streaming and chunked processing
2. **Resource efficiency**: Memory-intensive operations need better control and optimization
3. **Enterprise readiness**: Type safety, compiled performance, and mature tooling
4. **Future scalability**: Architecture that supports cloud-native patterns (Lambda, S3, event-driven)

## Decision
Migrate backend to .NET 8 with Clean Architecture (Onion Architecture) pattern:

### Technology Stack
- **Runtime**: .NET 8 with ASP.NET Core
- **ORM**: Entity Framework Core 8 with MySQL (Pomelo provider)
- **Testing**: xUnit, FluentAssertions, Microsoft.AspNetCore.Mvc.Testing
- **Logging**: Serilog
- **API Documentation**: Swashbuckle (Swagger/OpenAPI)
- **Containerization**: Docker multi-stage builds

### Architecture Layers

```
┌─────────────────────────────────────────┐
│         LiterateSniffle.API             │  ← Presentation Layer
│   (Controllers, Middleware, Program)    │     HTTP endpoints, request/response
└──────────────┬──────────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────────┐
│         LiterateSniffle.Core            │  ← Business Logic Layer
│   (Services, Models, Exceptions)        │     Domain logic, validation
└──────────────┬──────────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────────┐
│    LiterateSniffle.Infrastructure       │  ← Data Access Layer
│   (Entities, DbContext, Repositories)   │     Database, external services
└─────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. API Layer (Presentation)
- **Purpose**: HTTP interface and request handling
- **Contents**: 
  - Controllers (UploadController, TransactionsController, StoresController)
  - Middleware (ExceptionMiddleware)
  - Program.cs (dependency injection, middleware pipeline)
- **Dependencies**: References Core and Infrastructure
- **Current Implementation**: Direct file upload to disk
- **Future Path**: Gateway to cloud services (S3, Lambda)

#### 2. Core Layer (Business Logic)
- **Purpose**: Domain logic independent of infrastructure
- **Contents**:
  - Services (CNABParserService, FileUploadService, TransactionService)
  - Models (ParsedCNABData, ParsedTransaction)
  - Exceptions (CNABParseException, ValidationException)
- **Dependencies**: No dependencies on other layers (pure business logic)
- **Key Principle**: Infrastructure-agnostic - can run without database or HTTP
- **Benefits**: Highly testable, reusable across different contexts

#### 3. Infrastructure Layer (Data Access)
- **Purpose**: External concerns (database, file system, external APIs)
- **Contents**:
  - Entities (Transaction, TransactionType, Store, FileUpload)
  - ApplicationDbContext (EF Core context)
  - Entity Configurations (Fluent API)
  - Migrations
- **Dependencies**: No dependencies on API layer
- **Benefits**: Can swap database providers without affecting business logic

### Why Clean Architecture?

#### Separation of Concerns
Each layer has a single responsibility:
- **API**: Handle HTTP, return responses
- **Core**: Execute business rules, validate data
- **Infrastructure**: Persist data, communicate with external systems

#### Dependency Inversion Principle
Dependencies point inward:
- API → Core → Infrastructure (compile-time)
- Runtime: API calls Core, Core has no knowledge of Infrastructure
- Benefits: Can test Core in complete isolation

#### Future-Proof Design
Current API limitation: Direct file uploads with synchronous processing.

**Production-Ready Future Architecture**:
```
User Upload → API Gateway → S3 Bucket
                ↓
            Lambda Function (triggered by S3 event)
                ↓
            Core Layer (CNABParserService)
                ↓
            Process in chunks (stream from S3)
                ↓
            Write to Database in batches
```

**Why this architecture enables it**:
1. **Core Layer is portable**: CNABParserService can run in Lambda unchanged
2. **No tight coupling**: Parser doesn't know about HTTP or file system
3. **Testable**: Same unit tests work in Lambda environment
4. **Scalable**: Lambda auto-scales, processes files asynchronously
5. **Cost-effective**: Pay only for processing time, no idle servers

## Implementation Details

### CNAB File Processing
- **Format**: 80-character fixed-width records (CNAB 80)
- **Date Format**: YYYYMMDD (e.g., 20190301 = March 1, 2019)
- **Validation**: 
  - Header/trailer record validation
  - Type code validation (1-9)
  - Field-level validation (date, time, CPF, card, amounts)
  - Store owner/name presence

### API Endpoints
- `POST /api/upload` - Single file upload
- `POST /api/upload/chunk` - Chunked upload (partial cloud-ready)
- `POST /api/upload/complete` - Complete chunked upload
- `GET /api/transactions` - List all transactions
- `GET /api/transactions/store/{id}` - Transactions by store
- `GET /api/stores/summary` - Store summaries with balances
- `GET /health` - Health check

### Response Format Consistency
Aligned with Node.js implementation:
```json
{
  "message": "CNAB file uploaded, validated, and data stored successfully",
  "filename": "generated-guid.txt",
  "originalName": "original.cnab",
  "size": 12345,
  "mimetype": "text/plain",
  "format": "CNAB 80",
  "transactionsCount": 150,
  "fileUploadId": "uuid"
}
```

### Test Coverage
- **Target**: 80% minimum coverage
- **Current**: 18 tests (7 unit + 11 integration), 100% passing
- **Approach**:
  - Unit tests for Core layer (business logic)
  - Integration tests for API layer (WebApplicationFactory)
  - In-memory database for test isolation

## Consequences

### Positive
1. **Type Safety**: Compile-time error detection vs runtime surprises
2. **Performance**: 
   - Compiled code runs 2-5x faster than Node.js
   - Better memory management (no GC pauses like V8)
   - Native async/await without event loop overhead
3. **Enterprise Tooling**: 
   - Visual Studio, Rider IDEs with advanced debugging
   - Azure integration (App Service, Functions, Container Apps)
   - Built-in dependency injection
4. **Clean Architecture Benefits**:
   - Core layer is testable in isolation (no mocking infrastructure)
   - Easy to swap implementations (MySQL → PostgreSQL, disk → S3)
   - Business logic reusable in console apps, workers, Functions
5. **Cloud-Native Ready**:
   - Core services can run in Azure Functions/AWS Lambda unchanged
   - Infrastructure layer can be swapped for cloud services
   - Chunked upload foundation already in place
6. **Maintainability**:
   - Strong typing reduces bugs
   - Clear layer boundaries prevent "spaghetti code"
   - Easy onboarding (explicit dependencies)

### Negative
1. **Learning Curve**: Team needs .NET knowledge
2. **Dual Maintenance**: Currently maintaining both Node.js and .NET backends
3. **Deployment Complexity**: Docker images larger than Node.js
4. **Ecosystem**: Some npm packages have no .NET equivalent

### Risks
1. **Migration Gap**: Feature parity achieved but ongoing maintenance needed
2. **Team Skills**: Training required if team is JavaScript-focused
3. **Tooling Costs**: Visual Studio licenses (though VS Code + C# extension is free)

## Current Limitations & Future Work

### Current API File Handling (Not Ideal)
The current implementation uploads files directly to the API server:
```
Client → API Controller → Disk → Parse → Database
```

**Problems**:
- Files stored on API server (not scalable)
- Synchronous processing (blocks request)
- Memory intensive for large files
- Single point of failure
- No retry mechanism

### Recommended Production Architecture
```
Client → API Gateway → S3 Bucket (pre-signed URL)
                         ↓ (S3 event trigger)
                    Lambda Function
                         ↓
                Stream file from S3 in chunks
                         ↓
                Core.CNABParserService (unchanged!)
                         ↓
                Batch write to Database
                         ↓
                Update status in DynamoDB/SQS
```

**Benefits**:
1. **Scalability**: Lambda auto-scales, processes thousands of files concurrently
2. **Reliability**: S3 durability (11 nines), retry mechanisms, dead-letter queues
3. **Cost**: Pay only for processing time (vs. always-on server)
4. **Performance**: Stream processing, no file storage on server
5. **Monitoring**: CloudWatch metrics, X-Ray tracing

**Migration Path**:
1. ✅ **Phase 1 (Current)**: Clean Architecture with separated layers
2. **Phase 2**: Add S3 SDK to Infrastructure layer, upload files to S3
3. **Phase 3**: Deploy Core layer to Lambda, trigger on S3 events
4. **Phase 4**: API becomes lightweight orchestrator (generate pre-signed URLs)
5. **Phase 5**: Stream processing for GB-sized files

### Why Core/Infrastructure Split Matters
The separation enables this future:
- **Core Layer** runs in Lambda without modification
- **Infrastructure Layer** swapped for cloud services (S3, SQS, RDS)
- **API Layer** becomes thin gateway (authentication, routing only)
- **Zero business logic changes** during cloud migration

## Alternatives Considered

### 1. Keep Node.js, Add Worker Processes
**Rejected because**:
- Still requires infrastructure management
- Worker scaling more complex than Lambda
- Memory management issues persist

### 2. Serverless Framework with Node.js
**Rejected because**:
- JavaScript's weak typing makes large refactors risky
- V8 cold starts can be slower than .NET
- Harder to ensure Core layer purity

### 3. Go with Clean Architecture
**Considered positively but rejected**:
- Excellent performance and Lambda support
- Smaller team, less .NET expertise
- .NET has better ORM (EF Core vs GORM)
- Azure Functions mature ecosystem

### 4. Monolithic .NET (No Clean Architecture)
**Rejected because**:
- Couples business logic to infrastructure
- Cannot extract Core for Lambda without major refactor
- Testing requires full infrastructure (database, etc.)

## Related ADRs
- ADR 001: Node.js Full-Stack Development (superseded for backend)
- ADR 002: AI-Assisted Development (still applies)
- ADR 003: Database Choice (MySQL maintained for compatibility)
- ADR 004: Transaction Description Storage (still applies)

## References
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Onion Architecture](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/)
- [AWS Lambda with .NET](https://aws.amazon.com/blogs/compute/introducing-the-net-6-runtime-for-aws-lambda/)
- [Azure Functions .NET Isolated Worker](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)
