# ADR-003: WebSocket Contract Design

## Status

Proposed

## Context

The A1Betting platform requires real-time communication for:

- Live sports data updates (scores, stats, play-by-play)
- Real-time prop odds changes
- ML model prediction updates
- System health and performance notifications
- User-specific alerts and portfolio updates
- Arbitrage opportunity notifications

Current WebSocket implementation includes:

- Enhanced WebSocket routes (`/ws/v2/*` endpoints)
- Legacy WebSocket support (`/ws/legacy/{client_id}`)
- WebSocket connection registry (`ws_registry.py`)
- Correlation ID support for request tracking
- Multiple specialized endpoints (odds, arbitrage, sports)

However, the current WebSocket contract lacks:

- Standardized message format across all endpoints
- Comprehensive error handling and reconnection strategies
- Message versioning and backward compatibility
- Client capability negotiation
- Rate limiting and subscription management

## Decision

We will implement a standardized WebSocket contract with versioned message formats, comprehensive error handling, and flexible subscription management.

### Message Format Standard

All WebSocket messages will follow a standardized envelope format:

```json
{
  "version": "v2",
  "type": "data|error|control|subscription",
  "timestamp": "2025-01-16T10:30:00Z",
  "correlation_id": "uuid-v4",
  "channel": "sport.mlb|odds|arbitrage|system",
  "payload": {
    "event": "update|create|delete|subscribe|unsubscribe",
    "data": { ... },
    "metadata": {
      "source": "data_provider|ml_engine|system",
      "confidence": 0.95,
      "expires_at": "2025-01-16T10:35:00Z"
    }
  }
}
```

### Channel Hierarchy

```text
sport.{sport_name}          - Sport-specific data (scores, stats)
  ├── sport.mlb.games       - MLB game updates
  ├── sport.mlb.players     - MLB player stats
  └── sport.mlb.plays       - MLB play-by-play

odds.{provider}             - Odds data from various providers
  ├── odds.prizepicks       - PrizePicks prop odds
  ├── odds.draftkings       - DraftKings odds
  └── odds.fanduel          - FanDuel odds

arbitrage                   - Arbitrage opportunities
  ├── arbitrage.alerts      - New arbitrage opportunities
  └── arbitrage.expired     - Expired opportunities

system                      - System-level notifications
  ├── system.health         - Service health updates
  ├── system.performance    - Performance metrics
  └── system.maintenance    - Maintenance notifications

user.{user_id}             - User-specific updates
  ├── user.portfolio        - Portfolio updates
  ├── user.alerts           - Personal alerts
  └── user.preferences      - Settings changes
```

### Connection Lifecycle

1. **Connection Establishment**
   - Client connects to `/ws/v2/connect`
   - Server sends welcome message with connection metadata
   - Client capabilities negotiation (supported versions, compression, etc.)

2. **Subscription Management**
   - Clients subscribe to specific channels using subscription messages
   - Server confirms subscriptions and provides estimated message volume
   - Rate limiting applied per subscription type

3. **Message Delivery**
   - Server delivers messages based on active subscriptions
   - Message acknowledgment for critical updates
   - Automatic reconnection with subscription recovery

4. **Connection Termination**
   - Graceful disconnection with unsubscription from all channels
   - Connection cleanup in registry
   - Client-side reconnection strategy

### Error Handling Strategy

```json
{
  "version": "v2",
  "type": "error",
  "timestamp": "2025-01-16T10:30:00Z",
  "correlation_id": "uuid-v4",
  "payload": {
    "error_code": "RATE_LIMIT_EXCEEDED",
    "error_message": "Rate limit exceeded for channel sport.mlb",
    "error_details": {
      "retry_after": 30,
      "current_rate": "100/min",
      "limit": "50/min"
    },
    "recovery_suggestions": [
      "Reduce subscription frequency",
      "Consider upgrading to higher rate limit tier"
    ]
  }
}
```

### Implementation Pattern

```python
class WebSocketContractHandler:
    def __init__(self):
        self.connection_registry = WebSocketRegistry()
        self.subscription_manager = SubscriptionManager()
        
    async def handle_message(self, websocket, raw_message):
        try:
            message = self.parse_message(raw_message)
            
            if message.type == "subscription":
                await self.handle_subscription(websocket, message)
            elif message.type == "control":
                await self.handle_control(websocket, message)
            else:
                await self.send_error(websocket, "INVALID_MESSAGE_TYPE")
                
        except ValidationError as e:
            await self.send_error(websocket, "INVALID_MESSAGE_FORMAT", str(e))
            
    async def broadcast_to_channel(self, channel: str, data: dict):
        subscribers = self.subscription_manager.get_subscribers(channel)
        message = self.create_message("data", channel, data)
        
        for websocket in subscribers:
            if self.rate_limiter.allow(websocket, channel):
                await websocket.send_text(message.json())
```

## Consequences

### Positive Consequences

- **Standardization**: Consistent message format across all WebSocket communications
- **Scalability**: Channel-based subscriptions reduce unnecessary message delivery
- **Reliability**: Comprehensive error handling and reconnection strategies
- **Observability**: All messages include correlation IDs for distributed tracing
- **Flexibility**: Versioned contracts allow backward compatibility and gradual upgrades
- **Performance**: Rate limiting prevents client and server overload

### Negative Consequences

- **Complexity**: Standardized contract adds complexity to WebSocket implementations
- **Message Size**: Envelope format increases message size compared to simple payloads
- **Migration Effort**: Existing WebSocket clients need migration to new contract
- **Resource Usage**: Subscription management requires additional memory and processing

### Neutral Consequences

- **Client Libraries**: Need client-side libraries to simplify contract implementation
- **Documentation**: Comprehensive API documentation required for WebSocket contract
- **Testing**: WebSocket integration tests become more complex

## Related Decisions

- Integrates with observability strategy (ADR-001) through correlation IDs and structured logging
- Supports model degradation strategy (ADR-002) through real-time model health notifications
- Future decisions about client-side state management will build on this WebSocket foundation

## Notes

- Existing WebSocket registry (`ws_registry.py`) provides foundation for connection management
- Legacy WebSocket endpoints (`/ws/legacy/*`) will be maintained during transition period
- Consider implementing WebSocket compression (permessage-deflate) for large message payloads
- Rate limiting should be configurable per subscription type and user tier
- Message acknowledgment should be optional and configurable per channel type
- Consider implementing message queuing for offline clients (Redis Streams or similar)
- WebSocket security should include authentication, authorization, and input validation