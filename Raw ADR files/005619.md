# Architecture Decision Record: Enhanced Streaming Implementation

## Status
Accepted

## Date
2024-06-17

## Context
The AI Logo Generator processes complex, multi-stage generation tasks that can take several minutes to complete. Users need real-time feedback on the status of their logo generation to provide a responsive and engaging experience. Our current streaming implementation has several limitations:

1. **Limited Progress Information**: Basic progress updates with minimal detail about what's happening in each stage
2. **Unreliable Time Estimates**: No accurate time remaining calculations based on actual system performance
3. **Basic Error Handling**: Minimal error recovery and reconnection capabilities
4. **No Structured Message Types**: All communication is ad-hoc with no standardized format
5. **Limited Preview Capabilities**: Only basic SVG previews without structured metadata
6. **No Heartbeat Mechanism**: Connection drops are not detected reliably

These limitations affect user experience and system reliability, particularly for longer running generations or unstable network connections.

## Decision
We decided to implement an enhanced streaming system with the following components:

1. **Comprehensive Message Type System**:
   - Standardized message types for each kind of communication
   - Structured payloads with consistent schemas
   - Support for backward compatibility with existing clients

2. **Enhanced Progress Tracking**:
   - Detailed per-stage progress updates
   - Overall pipeline progress with reliable percentage calculations
   - Clear status messages for each phase of generation

3. **Intelligent Time Estimation**:
   - Stage-based time calculations with historical data
   - Adaptive time estimates that improve as more stages complete
   - Reliability metrics to indicate confidence in time estimates

4. **Advanced Error Handling and Recovery**:
   - Automatic reconnection for network interruptions
   - Detailed error categorization and contextual information
   - Support for recoverable vs. non-recoverable errors

5. **Rich Preview Capabilities**:
   - Multiple preview types (SVG, PNG, HTML)
   - Metadata for previews including dimensions and content type
   - Stage-specific preview tracking

6. **Connection Reliability**:
   - Heartbeat mechanism to detect stalled connections
   - Automatic recovery from temporary failures
   - Graceful degradation when reconnection fails

## Consequences

### Positive
1. **Improved User Experience**: More detailed and accurate progress information
2. **Higher Reliability**: Better handling of network issues and interruptions
3. **More Accurate Time Estimates**: Improved predictions of completion times
4. **Rich Preview Content**: Better visualization of in-progress generation
5. **Structured Data**: Easier client-side handling with consistent message formats
6. **Backward Compatibility**: Existing clients continue to work with minimal changes

### Negative
1. **Increased Complexity**: More sophisticated code with additional features
2. **Higher Bandwidth Usage**: More frequent and detailed messages
3. **Additional Processing**: More client and server-side computation for metrics
4. **Memory Usage**: Tracking historical performance data requires memory

### Neutral
1. **API Changes**: New capabilities require client updates to fully utilize
2. **Configuration Options**: More settings to tune for optimal performance

## Alternatives Considered

1. **WebSockets**: Full-duplex communication would allow bidirectional messaging
   - Pros: Real-time bidirectional communication
   - Cons: Higher complexity, additional infrastructure requirements
   - Decision: Not needed for the current use case where client-to-server communication is minimal

2. **GraphQL Subscriptions**: Subscription-based updates for long-running operations
   - Pros: Well-structured schema, client-specified data requirements
   - Cons: Significant architecture change, steeper learning curve
   - Decision: Excessive for our needs; HTTP streaming is simpler and sufficient

3. **Polling with Cached Results**: Regular HTTP polling instead of streaming
   - Pros: Simpler implementation, works in all browsers
   - Cons: Higher latency, more server requests, less efficient
   - Decision: Would create poor user experience for operations taking minutes

4. **No Changes**: Keep the existing simple streaming implementation
   - Pros: No development cost, no risk of regressions
   - Cons: Missing important features for user experience
   - Decision: Current limitations are significant enough to justify enhancements

## Implementation Details

### Message Structure
```typescript
interface BaseStreamMessage {
  type: StreamMessageType;
  timestamp?: number;
  sessionId?: string;
}

enum StreamMessageType {
  START = 'start',
  PROGRESS = 'progress',
  PREVIEW = 'preview',
  STAGE_COMPLETE = 'stage_complete',
  RESULT = 'result',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info',
  CACHE = 'cache',
  HEARTBEAT = 'heartbeat',
  END = 'end'
}
```

### Stream Processor
```typescript
class EnhancedStreamProcessor {
  // Configuration options
  private options: EnhancedStreamingOptions;

  // Process a stream with enhanced features
  async processStream(
    streamOrUrl: ReadableStream<Uint8Array> | string,
    callbacks: EnhancedStreamingCallbacks,
    requestInit?: RequestInit
  ): Promise<void>;

  // Support for reconnection
  private reconnectAttempts: number;
  
  // Time tracking and estimation
  private startTime: number;
  private stageStartTimes: Record<string, number>;
  private stageHistory: Record<string, { startTime: number, endTime?: number }>;
  
  // Heartbeat mechanism
  private heartbeatTimer?: NodeJS.Timeout;
  private lastHeartbeat: number;
}
```

### Time Estimation
```typescript
class TimeEstimator {
  // Calculate based on historical performance
  private stageHistory: Record<string, { duration: number, speed: number }>;
  
  // Adaptive estimation that improves with more data
  estimate(currentStageId: string, stageProgressPercent: number): TimeEstimation;
  
  // Reliability metrics
  private calculateReliability(): number;
}
```

### Client Integration
```typescript
interface EnhancedStreamingCallbacks {
  onStart?: (sessionId: string, estimatedTime: number, stages: Stage[]) => void;
  onProgress: (progress: GenerationProgress) => void;
  onPreview: (preview: StagePreview) => void;
  onStageComplete?: (stageId: string, stageName: string, duration: number) => void;
  onComplete: (assets: GeneratedAssets, sessionId: string, metrics?: any) => void;
  onError: (error: Error, recoverable?: boolean, retryAfter?: number) => void;
  onWarning?: (message: string, code?: string) => void;
  onInfo?: (message: string, details?: unknown) => void;
  onCache?: (isCached: boolean, source?: 'full' | 'partial') => void;
  onEnd?: (status: 'success' | 'error' | 'cancelled') => void;
  onHeartbeat?: () => void;
}
```

## Future Considerations

1. **Interactive Streaming**: Allow users to send messages during generation to guide the process
2. **Partial Results**: Enable downloading of completed assets even if some stages fail
3. **Generation Pausing**: Support for pausing and resuming long-running generations
4. **Multiple Concurrent Generations**: Track and manage multiple logo generations in parallel
5. **Telemetry Integration**: Collect performance metrics for system optimization