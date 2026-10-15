# Architecture Decision Record: Storage & Access Pattern Evolution

## Status

Proposed

## Context

Our Tides system serves two distinct user experiences:

1. **AI-Assisted Workflow Management** - Users interact with the system through Claude Desktop using natural language commands via the MCP (Model Context Protocol) server
2. **Native Mobile Experience** - Users interact directly through a React Native application with traditional UI elements

Currently, we have implemented a hybrid storage approach using:
- Cloudflare D1 (SQLite) for metadata and user authentication
- Cloudflare R2 (Object Storage) for complete JSON documents

This has led to several challenges:
- Complexity in maintaining consistency between D1 and R2
- Limited querying capabilities (can't efficiently query nested data)
- Redundant data access patterns for different client types
- Difficulty implementing real-time updates

### Key Insight

From a client perspective, the delivery format (JSON via MCP protocol or direct database access) is more important than the underlying storage mechanism. Our React Native application will eventually become a full MCP client, benefiting from AI capabilities, but needs to be developed rapidly in the near term.

## Decision Options

We have identified two viable paths forward:

### Option 1: Migrate to Supabase PostgreSQL

Migrate to Supabase PostgreSQL as the single source of truth for all data storage, while enabling a dual-track development approach.

### Option 2: Optimize Existing Cloudflare Architecture

Refine our current Cloudflare D1/R2 architecture with improved synchronization and access patterns.

Both options would support a phased approach:
1. **Short-term**: React Native app connects directly to the storage layer for rapid development
2. **Long-term**: All clients connect through MCP, which becomes the universal gateway to data and AI capabilities

## Architecture Evolution

### Option 1: Supabase Migration Path

**Phase 1: Parallel Development**
```
┌─────────────────────┐     ┌─────────────────────┐
│  Claude Desktop     │     │   React Native      │
│  (AI Interactions)  │     │   (Direct UI)       │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           ▼                           ▼
┌─────────────────────┐      ┌─────────────────────┐
│   MCP Server        │      │   Supabase SDK      │
│ (AI-powered tools)  │      │   (Direct Access)   │
└──────────┬──────────┘      └──────────┬──────────┘
           │                            │
           ▼                            ▼
┌──────────────────────────────────────────────────┐
│              Supabase PostgreSQL                 │
│         (Single Source of Truth)                 │
└──────────────────────────────────────────────────┘
```

**Phase 2: Complete Integration**
```
┌─────────────────────┐     ┌─────────────────────┐
│  Claude Desktop     │     │   React Native      │
│  (AI Interactions)  │     │   (AI-Enhanced UI)  │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           │                           │
           ▼                           ▼
┌──────────────────────────────────────────────────┐
│                  MCP Server                      │
│    (Universal Gateway: Data + AI Services)       │
└──────────┬───────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│              Supabase PostgreSQL                 │
│         (Single Source of Truth)                 │
└──────────────────────────────────────────────────┘
```

### Option 2: Cloudflare Optimization Path

**Phase 1: Parallel Development**
```
┌─────────────────────┐     ┌─────────────────────┐
│  Claude Desktop     │     │   React Native      │
│  (AI Interactions)  │     │   (Direct UI)       │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           ▼                           ▼
┌─────────────────────┐      ┌─────────────────────┐
│   MCP Server        │      │ Cloudflare Client   │
│ (AI-powered tools)  │      │   (Direct Access)   │
└──────────┬──────────┘      └──────────┬──────────┘
           │                            │
           ▼                            ▼
┌─────────────────┐     ┌─────────────────────────┐
│  Cloudflare D1  │◄───►│    Cloudflare R2        │
│   (Metadata)    │     │  (JSON Documents)       │
└─────────────────┘     └─────────────────────────┘
                  Improved Sync Layer
```

**Phase 2: Complete Integration**
```
┌─────────────────────┐     ┌─────────────────────┐
│  Claude Desktop     │     │   React Native      │
│  (AI Interactions)  │     │   (AI-Enhanced UI)  │
└──────────┬──────────┘     └──────────┬──────────┘
           │                            │
           │                            │
           ▼                            ▼
┌──────────────────────────────────────────────────┐
│                  MCP Server                      │
│    (Universal Gateway: Data + AI Services        │
└──────────┬───────────────────┬───────────────────┘
           │                   │
           ▼                   ▼
┌─────────────────┐     ┌─────────────────────────┐
│  Cloudflare D1  │◄───►│    Cloudflare R2        │
│   (Metadata)    │     │  (JSON Documents)       │
└─────────────────┘     └─────────────────────────┘
                  Optimized Storage Layer
```

## Gherkin-Style Scenarios

```gherkin
Feature: Storage and Access Pattern Evolution

  Scenario: Phase 1 - React Native Direct Access (Supabase)
    Given the React Native app needs to display user tides
    When the app requests tide data
    Then the app uses Supabase SDK directly
    And the data is retrieved efficiently
    And real-time updates are enabled via Supabase subscriptions

  Scenario: Phase 1 - React Native Direct Access (Cloudflare)
    Given the React Native app needs to display user tides
    When the app requests tide data
    Then the app uses Cloudflare Worker API directly
    And the data is retrieved from D1 for metadata
    And complete documents are retrieved from R2 when needed

  Scenario: Phase 1 - Claude Desktop AI Interaction
    Given a user wants to analyze work patterns
    When the user asks Claude Desktop for insights
    Then Claude Desktop forwards the request to MCP
    And MCP retrieves data from the storage layer
    And MCP applies AI processing to generate insights
    
  Scenario: Phase 2 - React Native Becomes MCP Client
    Given the React Native app has been developed with a data abstraction layer
    When we implement the MCP client functionality
    Then the app seamlessly transitions to using MCP
    And all data requests go through MCP
    And the app gains AI capabilities without major refactoring
    
  Scenario: Phase 2 - Universal Business Logic
    Given all clients access data through MCP
    When business rules or validations change
    Then we update logic in a single place (MCP)
    And all clients automatically receive consistent handling
```

## Technical Implementation

### Data Abstraction Layer for React Native

```typescript
// Generic interface for data access
interface DataService {
  getTides(): Promise<Tide[]>;
  createTide(tideData: TideInput): Promise<Tide>;
  // Additional methods...
}

// Option 1: Supabase Implementation
export class SupabaseDataService implements DataService {
  private supabase: SupabaseClient;
  
  constructor() {
    this.supabase = createClient(
      SUPABASE_URL,
      SUPABASE_ANON_KEY
    );
  }

  async getTides(): Promise<Tide[]> {
    const { data, error } = await this.supabase
      .from('tides')
      .select('*');
      
    if (error) throw error;
    return data;
  }
  
  // Additional methods...
}

// Option 2: Cloudflare Implementation
export class CloudflareDataService implements DataService {
  private apiClient: ApiClient;
  
  constructor() {
    this.apiClient = new ApiClient(API_ENDPOINT);
  }

  async getTides(): Promise<Tide[]> {
    return this.apiClient.get('/tides');
  }
  
  // Additional methods...
}

// Phase 2: MCP client implementation (future)
export class MCPDataService implements DataService {
  private mcpClient: MCPClient;
  
  constructor() {
    this.mcpClient = new MCPClient(MCP_URL);
  }
  
  async getTides(): Promise<Tide[]> {
    return this.mcpClient.request('getTides', {});
  }
  
  // MCP-powered AI methods
  async getSuggestions(tideId: string): Promise<Suggestion[]> {
    return this.mcpClient.request('getSuggestions', { tideId });
  }
}
```

### Option 1: Supabase Schema

```sql
-- Core tables with proper relationships
CREATE TABLE tides (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL,
  flow_type TEXT CHECK (flow_type IN ('daily', 'weekly', 'project', 'seasonal')),
  description TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE flow_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tide_id UUID REFERENCES tides(id) ON DELETE CASCADE,
  intensity TEXT CHECK (intensity IN ('gentle', 'moderate', 'strong')),
  duration INTEGER NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ,
  energy_level TEXT,
  work_context TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Additional tables...

-- Enable Row Level Security
ALTER TABLE tides ENABLE ROW LEVEL SECURITY;
ALTER TABLE flow_sessions ENABLE ROW LEVEL SECURITY;
-- Additional security policies...
```

### Option 2: Improved Cloudflare D1/R2 Integration

```typescript
// Enhanced synchronization layer
export class HybridStorage {
  constructor(
    private d1Client: D1Database,
    private r2Client: R2Bucket
  ) {}
  
  // Atomic write operations
  async createTide(input: CreateTideInput): Promise<Tide> {
    const id = crypto.randomUUID();
    
    // Extract metadata for D1
    const metadata = {
      id,
      user_id: input.userId,
      name: input.name,
      flow_type: input.flowType,
      status: 'active',
      created_at: new Date().toISOString()
    };
    
    // Transaction-like pattern
    try {
      // Store metadata in D1
      await this.d1Client.prepare(`
        INSERT INTO tides (id, user_id, name, flow_type, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).bind(
        id,
        metadata.user_id,
        metadata.name,
        metadata.flow_type,
        metadata.status,
        metadata.created_at,
        metadata.created_at
      ).run();
      
      // Store full document in R2
      const fullDocument = {
        ...metadata,
        ...input,
        sessions: [],
        energy_updates: []
      };
      
      await this.r2Client.put(`tides/${id}`, JSON.stringify(fullDocument));
      
      return fullDocument;
    } catch (error) {
      // Attempt rollback if possible
      // Log failure for potential cleanup
      throw new Error(`Failed to create tide: ${error.message}`);
    }
  }
  
  // Optimized read patterns
  async getTide(id: string, includeDetails: boolean = false): Promise<Tide> {
    // For basic metadata, just query D1
    if (!includeDetails) {
      const result = await this.d1Client.prepare(`
        SELECT * FROM tides WHERE id = ?
      `).bind(id).first();
      
      if (!result) throw new Error(`Tide not found: ${id}`);
      return result as Tide;
    }
    
    // For full document, get from R2
    const object = await this.r2Client.get(`tides/${id}`);
    if (!object) throw new Error(`Tide not found in R2: ${id}`);
    
    const fullDocument = await object.json();
    return fullDocument;
  }
  
  // Batch operations for efficiency
  async getTidesForUser(userId: string): Promise<Tide[]> {
    // Get list of IDs from D1
    const results = await this.d1Client.prepare(`
      SELECT id FROM tides WHERE user_id = ?
    `).bind(userId).all();
    
    // Parallel fetch from R2 for better performance
    const tidePromises = results.results.map(row => 
      this.r2Client.get(`tides/${row.id}`).then(obj => obj.json())
    );
    
    return Promise.all(tidePromises);
  }
}
```

### MCP Server Integration

```typescript
// Universal MCP gateway with storage abstraction
export class MCPGateway {
  private storageClient: StorageInterface;
  private aiProcessor: AIProcessor;
  
  constructor(storageClient, aiProcessor) {
    this.storageClient = storageClient;
    this.aiProcessor = aiProcessor;
  }

  // Base data access operations
  async getTides(userId: string): Promise<Tide[]> {
    return this.storageClient.getTidesForUser(userId);
  }
  
  async createTide(input: CreateTideInput): Promise<Tide> {
    return this.storageClient.createTide(input);
  }
  
  // AI-enhanced operations
  async analyzeTidePatterns(userId: string): Promise<Analysis> {
    // Fetch data through storage abstraction
    const tides = await this.getTides(userId);
    
    // Apply AI processing
    return this.aiProcessor.analyzePatterns(tides);
  }
  
  async suggestNextAction(tideId: string): Promise<Suggestion> {
    // Get full tide details
    const tide = await this.storageClient.getTide(tideId, true);
    
    // Generate AI suggestion
    return this.aiProcessor.generateSuggestion(tide);
  }
}

// Factory for creating the right storage implementation
export function createStorageClient(type: 'supabase' | 'cloudflare'): StorageInterface {
  if (type === 'supabase') {
    return new SupabaseStorage(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
  } else {
    return new HybridStorage(
      D1Database.fromBinding(env.DB),
      R2Bucket.fromBinding(env.R2_BUCKET)
    );
  }
}
```

## Implementation Plan

### Option 1: Supabase Migration Path

#### Phase 1: Parallel Development (Weeks 1-6)

1. **Supabase Migration** (Weeks 1-2)
   - Set up Supabase project and schema
   - Migrate data from D1/R2
   - Implement and test Supabase adapter for MCP

2. **React Native Direct Integration** (Weeks 3-4)
   - Implement Data Service abstraction layer
   - Build UI with direct Supabase integration
   - Develop real-time features using Supabase

3. **MCP Server Enhancement** (Weeks 5-6)
   - Evolve MCP to be Supabase-aware
   - Enhance AI capabilities
   - Document MCP protocol for future React Native integration

#### Phase 2: Progressive MCP Integration (Weeks 7-12)

4. **MCP Client for React Native** (Weeks 7-8)
   - Implement MCPClient class
   - Create MCPDataService implementation
   - Test basic data operations

5. **Feature Parity Validation** (Week 9)
   - Test all app features through MCP
   - Fix any discrepancies
   - Performance optimization

6. **AI Feature Integration** (Weeks 10-12)
   - Add AI-powered features to React Native
   - Implement UI components for AI interactions
   - Complete transition to full MCP client

### Option 2: Cloudflare Optimization Path

#### Phase 1: Cloudflare Enhancement (Weeks 1-6)

1. **Storage Layer Optimization** (Weeks 1-2)
   - Implement improved HybridStorage class
   - Create robust synchronization mechanisms
   - Develop efficient query patterns

2. **React Native API Integration** (Weeks 3-4)
   - Create dedicated API endpoints for React Native
   - Implement CloudflareDataService class
   - Build UI with direct API integration

3. **MCP Server Refinement** (Weeks 5-6)
   - Enhance MCP server with optimized storage access
   - Improve AI capabilities
   - Document MCP protocol for future React Native integration

#### Phase 2: Progressive MCP Integration (Weeks 7-12)

4. **MCP Client for React Native** (Weeks 7-8)
   - Same steps as Option 1

5. **Feature Parity Validation** (Week 9)
   - Same steps as Option 1

6. **AI Feature Integration** (Weeks 10-12)
   - Same steps as Option 1

## Comparison of Options

### Option 1: Supabase Migration

#### Pros
- Full SQL capabilities with PostgreSQL
- Built-in real-time subscriptions
- Row-level security for multi-tenancy
- Simplified data model (no synchronization needed)
- Better scalability for complex queries
- Third-party authentication integration

#### Cons
- Migration effort from existing D1/R2
- Vendor lock-in with Supabase
- Potentially higher costs
- Less integration with existing Cloudflare infrastructure

### Option 2: Cloudflare Optimization

#### Pros
- Leverage existing Cloudflare infrastructure
- Edge computing benefits (low latency)
- Potentially lower costs
- Familiarity with current technology
- No major migration required

#### Cons
- Continued complexity of dual-storage system
- Limited query capabilities compared to PostgreSQL
- Custom synchronization logic required
- Less mature real-time capabilities
- More complex multi-tenancy implementation

## Decision Outcome

The detailed analysis of both options reveals viable paths forward. The primary factors in making the final decision should be:

1. **Development velocity**: How quickly can each option be implemented?
2. **Long-term maintainability**: Which option simplifies the architecture?
3. **Feature requirements**: Which option better supports real-time features and complex queries?
4. **Infrastructure strategy**: Are we committed to Cloudflare or open to diversifying?

Regardless of the storage option selected, the phased approach with a data abstraction layer enables a smooth transition to a universal MCP gateway. This evolution supports our long-term vision of AI-enhanced experiences across all clients while enabling rapid development in the near term.

The recommended approach is **[To be determined after team discussion]** based on the analysis presented in this document.