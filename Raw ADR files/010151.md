---
doc_id: DOC-2025-00037
title: "Akka.NET + Semantic Kernel + ECS: Intelligent Avatar Architecture"
doc_type: adr
status: draft
canonical: false
created: 2025-10-24
tags: [architecture, akka, semantic-kernel, ecs, ai, agents, avatars, adr]
summary: >
  Architecture Decision Record for integrating three-layer intelligent avatar system combining
  Arch ECS (entity data), Akka.NET (actor lifecycle), and Semantic Kernel (AI reasoning) to create
  complete, intelligent NPCs and enemies in the dungeon crawler game.
source:
  author: agent
  agent: claude
  model: sonnet-4.5
related:
  - DOC-2025-00018  # Architecture
  - DOC-2025-00033  # Dungeon Crawler Features
---

# Akka.NET + Semantic Kernel + ECS: Intelligent Avatar Architecture

**Status**: Draft
**Decision Date**: 2025-10-24
**Authors**: Claude (AI Agent)
**Reviewers**: TBD

## Context

The Lablab Bean dungeon crawler currently uses:

- **Arch ECS**: Entity-Component-System for game entities (player, enemies, items)
- **Simple AI**: Enum-based behaviors (`Wander`, `Chase`, `Flee`, `Patrol`, `Idle`)
- **Event Bus**: High-performance pub-sub messaging (1.1M+ events/sec)

**Current Limitations:**

- ❌ NPCs lack personality and memory
- ❌ AI behaviors are static and predictable
- ❌ No dialogue generation capabilities
- ❌ Enemies don't adapt to player tactics
- ❌ No context-aware decision making

**User Vision:**
> "Combining Akka.NET (actor-based) with Semantic Kernel (agent-based) with ECS (entity) should make avatars in the game more complete."

## Decision

Implement a **three-layer intelligent avatar architecture**:

1. **Layer 1: ECS (Entity Data)** - "What Exists"
   - Fast component storage and queries (Arch ECS)
   - Components: `Position`, `Health`, `Combat`, `Actor`, `AI`

2. **Layer 2: Akka.NET (Actor Lifecycle)** - "How It Lives"
   - State management and message handling
   - Supervision trees for fault tolerance
   - Actor persistence for save/load

3. **Layer 3: Semantic Kernel (Intelligence)** - "Why It Acts"
   - AI reasoning and planning
   - Dialogue generation
   - Personality-driven decision making

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│              Terminal.Gui / ReactiveUI / xterm.js                │
└───────────────────────────┬─────────────────────────────────────┘
                            │ ObservableCollections + R3
┌───────────────────────────▼─────────────────────────────────────┐
│                   EVENT BUS (IEventBus)                          │
│    Sequential Async Pub-Sub • 1.1M events/sec • Error Isolation │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼─────────┐
│  LAYER 1: ECS  │  │ LAYER 2:    │  │  LAYER 3:        │
│  (Arch)        │  │ AKKA.NET    │  │  SEMANTIC        │
│  Entity Data   │  │ Actor State │  │  KERNEL          │
└───────┬────────┘  └──────┬──────┘  └────────┬─────────┘
        │                  │                   │
        │ Components       │ Actors            │ Agents
        │ • Position       │ • NpcActor        │ • DialogueAgent
        │ • Health         │ • EnemyActor      │ • QuestAgent
        │ • Combat         │ • BossActor       │ • TacticsAgent
        │ • AI (tag)       │ • MerchantActor   │ • DungeonMasterAgent
        │                  │                   │
        └──────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   SYSTEMS   │
                    │ • AISystem  │
                    │ • Combat    │
                    │ • Movement  │
                    └─────────────┘
```

### Layer 1: ECS (Arch) - Entity Data

**Responsibility**: Fast component storage, efficient queries, game state

**Existing Components:**

```csharp
public struct Actor { int Energy; int Speed; }
public struct Health { int Current; int Maximum; }
public struct Combat { int Attack; int Defense; }
public struct Position { Point Point; }
public struct AI { AIBehavior Behavior; }  // Simple enum
public struct Enemy { string Type; EffectType? InflictsEffect; }
public struct Player { string Name; }
```

**New Bridge Components:**

```csharp
// Links ECS entity to Akka actor
public struct AkkaActorRef
{
    public IActorRef ActorRef { get; set; }
}

// Links ECS entity to SK agent
public struct SemanticAgent
{
    public string AgentId { get; set; }
    public AgentType Type { get; set; }  // Dialogue, Quest, Tactics, etc.
}

// Enhanced AI with capabilities
public struct IntelligentAI
{
    public AICapability Capabilities { get; set; }  // Flags: Learning, Memory, Dialogue
    public string Personality { get; set; }          // e.g., "Cautious merchant", "Aggressive warrior"
    public string EmotionalState { get; set; }       // e.g., "Fearful", "Confident", "Neutral"
}

[Flags]
public enum AICapability
{
    None = 0,
    Learning = 1 << 0,      // Can learn from interactions
    Memory = 1 << 1,        // Remembers past events
    Dialogue = 1 << 2,      // Can engage in conversation
    Planning = 1 << 3,      // Can make multi-step plans
    Adaptation = 1 << 4     // Adapts tactics to player
}

public enum AgentType
{
    Dialogue,      // Conversation generation
    Quest,         // Quest logic and progression
    Tactics,       // Combat decision-making
    Merchant,      // Trading and negotiation
    DungeonMaster  // Overall game orchestration
}
```

**Querying Intelligent Entities:**

```csharp
// Find all NPCs with dialogue capability
var dialogueQuery = new QueryDescription()
    .WithAll<Position, IntelligentAI, AkkaActorRef, SemanticAgent>();

world.Query(in dialogueQuery, (Entity entity, ref Position pos, ref IntelligentAI ai) =>
{
    if (ai.Capabilities.HasFlag(AICapability.Dialogue))
    {
        // This NPC can have conversations
    }
});
```

### Layer 2: Akka.NET - Actor Lifecycle

**Responsibility**: State management, message handling, supervision, persistence

**Core Actor Types:**

#### 1. Avatar Actor

Manages individual NPC/enemy lifecycle and coordinates with SK.

```csharp
public class AvatarActor : ReceiveActor
{
    private readonly Entity _entity;
    private readonly World _world;
    private readonly IActorRef _skBridge;
    private AvatarState _state;

    public AvatarActor(Entity entity, World world, IActorRef skBridge)
    {
        _entity = entity;
        _world = world;
        _skBridge = skBridge;
        _state = new AvatarState
        {
            RecentMemories = new List<string>(),
            Relationships = new Dictionary<string, int>(),
            Goals = new List<string>()
        };

        // Handle game events
        Receive<TakeDamageMessage>(OnTakeDamage);
        Receive<PlayerNearbyMessage>(OnPlayerNearby);
        Receive<DialogueRequestMessage>(OnDialogueRequest);

        // Handle SK responses
        Receive<AIDecisionMessage>(OnAIDecision);
        Receive<DialogueResponseMessage>(OnDialogueResponse);
        Receive<TacticalPlanMessage>(OnTacticalPlan);
    }

    private void OnPlayerNearby(PlayerNearbyMessage msg)
    {
        // Update ECS position reference
        ref var pos = ref _entity.Get<Position>();
        ref var ai = ref _entity.Get<IntelligentAI>();

        // Build context for SK
        var context = new AvatarContext
        {
            AvatarId = Self.Path.Name,
            Health = _entity.Get<Health>(),
            Position = pos,
            PlayerPosition = msg.PlayerPosition,
            Personality = ai.Personality,
            EmotionalState = ai.EmotionalState,
            RecentMemories = _state.RecentMemories.TakeLast(5).ToList(),
            VisibleEntities = msg.VisibleEntities
        };

        // Ask SK for decision
        _skBridge.Tell(new GetAIDecisionRequest
        {
            AvatarId = Self.Path.Name,
            Context = context
        });
    }

    private void OnAIDecision(AIDecisionMessage msg)
    {
        // Update ECS component based on SK decision
        ref var ai = ref _entity.Get<AI>();
        ai.Behavior = msg.SuggestedBehavior;

        // Update emotional state
        ref var intAi = ref _entity.Get<IntelligentAI>();
        intAi.EmotionalState = msg.NewEmotionalState;

        // Store memory
        _state.RecentMemories.Add(msg.Reasoning);

        // Publish event to event bus
        PublishGameEvent(new AIBehaviorChangedEvent
        {
            EntityId = _entity.Id,
            NewBehavior = msg.SuggestedBehavior,
            Reason = msg.Reasoning,
            EmotionalState = msg.NewEmotionalState
        });
    }

    private void OnDialogueRequest(DialogueRequestMessage msg)
    {
        // Forward to SK for dialogue generation
        ref var intAi = ref _entity.Get<IntelligentAI>();

        _skBridge.Tell(new GetDialogueRequest
        {
            AvatarId = Self.Path.Name,
            PlayerInput = msg.PlayerInput,
            Personality = intAi.Personality,
            EmotionalState = intAi.EmotionalState,
            ConversationHistory = _state.RecentMemories
        });
    }

    private void OnDialogueResponse(DialogueResponseMessage msg)
    {
        // Store conversation in memory
        _state.RecentMemories.Add($"Player said: {msg.PlayerInput}");
        _state.RecentMemories.Add($"I said: {msg.Response}");

        // Publish dialogue event
        PublishGameEvent(new NPCDialogueEvent
        {
            EntityId = _entity.Id,
            Response = msg.Response
        });
    }

    private void PublishGameEvent(object evt)
    {
        Context.ActorSelection("/user/event-bus-bridge")
            .Tell(new PublishGameEvent(evt));
    }

    // Persistence for save/load
    protected override void PreRestart(Exception reason, object message)
    {
        // Save state before restart (supervision)
        SaveSnapshot(_state);
        base.PreRestart(reason, message);
    }
}

// Avatar internal state
public class AvatarState
{
    public List<string> RecentMemories { get; set; }
    public Dictionary<string, int> Relationships { get; set; }  // EntityId -> Affinity (-100 to +100)
    public List<string> Goals { get; set; }
}
```

#### 2. Semantic Kernel Bridge Actor

Manages SK kernel instances and routes requests to appropriate agents.

```csharp
public class SemanticKernelBridgeActor : ReceiveActor
{
    private readonly Dictionary<string, NpcIntelligenceAgent> _agents = new();
    private readonly Kernel _kernel;
    private readonly IEventBus _eventBus;

    public SemanticKernelBridgeActor(Kernel kernel, IEventBus eventBus)
    {
        _kernel = kernel;
        _eventBus = eventBus;

        Receive<GetAIDecisionRequest>(async msg =>
        {
            var agent = GetOrCreateAgent(msg.AvatarId);
            var decision = await agent.DecideActionAsync(msg.Context);
            Sender.Tell(decision);
        });

        Receive<GetDialogueRequest>(async msg =>
        {
            var agent = GetOrCreateAgent(msg.AvatarId);
            var response = await agent.GenerateDialogueAsync(msg);
            Sender.Tell(response);
        });

        Receive<GetTacticalPlanRequest>(async msg =>
        {
            var agent = GetOrCreateAgent(msg.AvatarId);
            var plan = await agent.CreateTacticalPlanAsync(msg.Context);
            Sender.Tell(plan);
        });
    }

    private NpcIntelligenceAgent GetOrCreateAgent(string avatarId)
    {
        if (!_agents.ContainsKey(avatarId))
        {
            _agents[avatarId] = new NpcIntelligenceAgent(_kernel, _eventBus, avatarId);
        }
        return _agents[avatarId];
    }
}
```

#### 3. Event Bus Bridge Actor

Bidirectional bridge between Event Bus and Akka.NET.

```csharp
public class EventBusAkkaAdapter : ReceiveActor
{
    private readonly IEventBus _eventBus;

    public EventBusAkkaAdapter(IEventBus eventBus)
    {
        _eventBus = eventBus;

        // Subscribe to game events → forward to actors
        _eventBus.Subscribe<EnemyKilledEvent>(async evt =>
        {
            Context.ActorSelection($"/user/avatars/avatar-{evt.EnemyId}")
                .Tell(new EntityDestroyedMessage());
        });

        _eventBus.Subscribe<PlayerMovedEvent>(async evt =>
        {
            // Notify nearby NPCs
            Context.ActorSelection("/user/avatars/*")
                .Tell(new PlayerNearbyMessage(evt.NewPosition, evt.VisibleEntities));
        });

        // Receive from actors → publish to event bus
        Receive<PublishGameEvent>(async msg =>
        {
            await _eventBus.PublishAsync(msg.Event);
        });
    }
}
```

**Supervision Strategy:**

```csharp
public class AvatarSupervisor : UntypedActor
{
    protected override SupervisorStrategy SupervisorStrategy()
    {
        return new OneForOneStrategy(
            maxNrOfRetries: 3,
            withinTimeRange: TimeSpan.FromMinutes(1),
            localOnlyDecider: ex =>
            {
                return ex switch
                {
                    HttpRequestException => Directive.Restart,  // LLM timeout
                    ArgumentException => Directive.Stop,         // Invalid state
                    _ => Directive.Escalate
                };
            });
    }

    protected override void OnReceive(object message)
    {
        // Supervisor only handles failures
    }
}
```

### Layer 3: Semantic Kernel - Intelligence

**Responsibility**: AI reasoning, dialogue generation, decision-making, planning

#### NPC Intelligence Agent

```csharp
public class NpcIntelligenceAgent
{
    private readonly Kernel _kernel;
    private readonly IEventBus _eventBus;
    private readonly string _avatarId;
    private readonly ChatHistory _chatHistory;

    public NpcIntelligenceAgent(Kernel kernel, IEventBus eventBus, string avatarId)
    {
        _kernel = kernel;
        _eventBus = eventBus;
        _avatarId = avatarId;
        _chatHistory = new ChatHistory();
    }

    /// <summary>
    /// AI decision-making with personality and context
    /// </summary>
    public async Task<AIDecisionMessage> DecideActionAsync(AvatarContext context)
    {
        var prompt = $$$"""
        You are {{{context.Personality}}}, an NPC in a dungeon crawler game.

        ## Current Situation
        - Your health: {{{context.Health.Current}}}/{{{context.Health.Maximum}}}
        - Your position: {{{context.Position.Point}}}
        - Player position: {{{context.PlayerPosition.Point}}}
        - Distance to player: {{{CalculateDistance(context.Position, context.PlayerPosition)}}} tiles
        - Current emotional state: {{{context.EmotionalState}}}

        ## Recent Memories
        {{{FormatMemories(context.RecentMemories)}}}

        ## Visible Entities
        {{{FormatVisibleEntities(context.VisibleEntities)}}}

        ## Decision Required
        Choose ONE action: Wander, Chase, Flee, Patrol, Idle

        Consider:
        1. Your personality and current emotional state
        2. Your health and the player's threat level
        3. Recent events from your memories
        4. Tactical advantages/disadvantages

        Respond in JSON format:
        {
          "action": "Chase|Flee|Wander|Patrol|Idle",
          "reasoning": "Brief explanation of why you chose this action",
          "new_emotional_state": "Fearful|Confident|Cautious|Aggressive|Neutral",
          "internal_thought": "What you're thinking (shown to player if nearby)"
        }
        """;

        var result = await _kernel.InvokePromptAsync<string>(prompt);
        var decision = ParseDecisionJson(result);

        // Publish AI thought event (for debugging or player insight)
        await _eventBus.PublishAsync(new AIThoughtEvent
        {
            AvatarId = _avatarId,
            Thought = decision.InternalThought,
            Reasoning = decision.Reasoning
        });

        return new AIDecisionMessage
        {
            SuggestedBehavior = decision.Action,
            Reasoning = decision.Reasoning,
            NewEmotionalState = decision.NewEmotionalState,
            InternalThought = decision.InternalThought
        };
    }

    /// <summary>
    /// Dialogue generation with personality
    /// </summary>
    public async Task<DialogueResponseMessage> GenerateDialogueAsync(GetDialogueRequest request)
    {
        var prompt = $$$"""
        You are {{{request.Personality}}}, an NPC in a dungeon.
        Current emotional state: {{{request.EmotionalState}}}

        ## Conversation History
        {{{FormatChatHistory()}}}

        Player says: "{{{request.PlayerInput}}}"

        Respond in character. Keep it brief (1-2 sentences max).
        Consider your emotional state when responding.
        """;

        var response = await _kernel.InvokePromptAsync<string>(prompt);

        // Update chat history
        _chatHistory.AddUserMessage(request.PlayerInput);
        _chatHistory.AddAssistantMessage(response);

        return new DialogueResponseMessage
        {
            Response = response,
            PlayerInput = request.PlayerInput
        };
    }

    /// <summary>
    /// Tactical planning for boss fights
    /// </summary>
    public async Task<TacticalPlanMessage> CreateTacticalPlanAsync(AvatarContext context)
    {
        var prompt = $$$"""
        You are a tactical AI for {{{context.Personality}}}, a boss enemy.

        ## Battlefield Analysis
        - Your health: {{{context.Health.Percentage * 100}}}%
        - Player distance: {{{CalculateDistance(context.Position, context.PlayerPosition)}}} tiles
        - Visible threats: {{{context.VisibleEntities.Count}}}

        ## Create a 3-step tactical plan
        Consider:
        1. Positioning (should you close distance, create distance, or hold?)
        2. Ability usage (when to use special attacks)
        3. Phase transitions (how strategy changes at low health)

        Respond in JSON:
        {
          "steps": [
            {"action": "description", "priority": "high|medium|low"},
            {"action": "description", "priority": "high|medium|low"},
            {"action": "description", "priority": "high|medium|low"}
          ],
          "overall_strategy": "Aggressive|Defensive|Balanced"
        }
        """;

        var result = await _kernel.InvokePromptAsync<string>(prompt);
        var plan = ParseTacticalPlanJson(result);

        return new TacticalPlanMessage
        {
            Steps = plan.Steps,
            OverallStrategy = plan.OverallStrategy
        };
    }

    private double CalculateDistance(Position a, Position b)
    {
        var dx = a.Point.X - b.Point.X;
        var dy = a.Point.Y - b.Point.Y;
        return Math.Sqrt(dx * dx + dy * dy);
    }

    private string FormatMemories(List<string> memories)
    {
        return memories.Any()
            ? string.Join("\n- ", memories.Select((m, i) => $"{i + 1}. {m}"))
            : "No recent memories";
    }

    private string FormatChatHistory()
    {
        return string.Join("\n", _chatHistory.Select(msg =>
            $"{(msg.Role == AuthorRole.User ? "Player" : "Me")}: {msg.Content}"));
    }
}
```

## Integration Flow Example

### Scenario: Player Encounters Boss

1. **ECS System detects proximity**
   - `AISystem.ProcessAI()` finds boss entity within aggro range
   - Boss has `AkkaActorRef` component

2. **Event Bus publishes event**

   ```csharp
   await _eventBus.PublishAsync(new PlayerNearbyEvent
   {
       PlayerPosition = playerPos,
       VisibleEntities = nearbyEntities
   });
   ```

3. **Event Bus Bridge forwards to Akka**
   - `EventBusAkkaAdapter` receives event
   - Sends `PlayerNearbyMessage` to `BossActor`

4. **Boss Actor requests AI decision**

   ```csharp
   private void OnPlayerNearby(PlayerNearbyMessage msg)
   {
       var context = BuildAvatarContext(msg);
       _skBridge.Tell(new GetAIDecisionRequest { Context = context });
   }
   ```

5. **SK Bridge routes to agent**
   - `SemanticKernelBridgeActor` gets or creates agent
   - Invokes `NpcIntelligenceAgent.DecideActionAsync()`

6. **SK Agent reasons**

   ```
   LLM analyzes:
   - Boss personality: "Ancient dragon, proud and cunning"
   - Health: 80% → Still confident
   - Player threat: Low level → Chase aggressively
   - Emotional state: "Confident"

   Decision:
   {
     "action": "Chase",
     "reasoning": "Player is weak, I am strong. Time to end this quickly.",
     "new_emotional_state": "Aggressive",
     "internal_thought": "*The dragon's eyes gleam with predatory hunger*"
   }
   ```

7. **SK Bridge sends response**

   ```csharp
   Sender.Tell(new AIDecisionMessage
   {
       SuggestedBehavior = AIBehavior.Chase,
       Reasoning = "Player is weak...",
       NewEmotionalState = "Aggressive"
   });
   ```

8. **Boss Actor updates ECS**

   ```csharp
   private void OnAIDecision(AIDecisionMessage msg)
   {
       ref var ai = ref _entity.Get<AI>();
       ai.Behavior = AIBehavior.Chase;

       ref var intAi = ref _entity.Get<IntelligentAI>();
       intAi.EmotionalState = "Aggressive";
   }
   ```

9. **Actor publishes event**

   ```csharp
   PublishGameEvent(new AIBehaviorChangedEvent
   {
       EntityId = _entity.Id,
       NewBehavior = AIBehavior.Chase,
       Reason = msg.Reasoning
   });
   ```

10. **Next frame: AISystem executes**
    - `AISystem.ProcessAI()` queries entities with `Actor` + `AI`
    - Finds boss with `AI.Behavior = Chase`
    - Executes chase logic (pathfinding toward player)

11. **UI updates**
    - ReactiveUI receives `AIBehaviorChangedEvent`
    - Shows message: "*The dragon's eyes gleam with predatory hunger*"
    - Activity log: "Ancient Dragon is now chasing you!"

## Benefits

### 1. Complete Avatars

- ✅ **Data (ECS)**: Fast queries, efficient storage
- ✅ **Lifecycle (Akka)**: State management, fault tolerance
- ✅ **Intelligence (SK)**: Reasoning, personality, dialogue

### 2. Separation of Concerns

- **ECS**: "What components does this entity have?"
- **Akka.NET**: "How does this entity manage state and respond to events?"
- **SK**: "Why does this entity make specific decisions?"

### 3. Scalability

- **ECS**: Handle 10,000+ entities for rendering/physics
- **Akka.NET**: Create actors for ~100 "important" entities (bosses, NPCs)
- **SK**: Invoke for ~10 "intelligent" entities needing AI decisions

### 4. Fault Tolerance

- **ECS**: Entity survives AI crashes
- **Akka.NET**: Supervisor restarts failed actors
- **SK**: LLM timeout doesn't crash game, falls back to simple AI

### 5. Rich Behaviors

- NPCs remember past interactions
- Dialogue adapts to player choices
- Enemies learn player tactics
- Boss fights have multi-phase strategies
- Merchants negotiate based on relationship

## Consequences

### Positive

- ✅ NPCs feel alive and unique
- ✅ Replayability through emergent narratives
- ✅ Fault-tolerant AI (supervision trees)
- ✅ Can save/load NPC state (Akka persistence)
- ✅ Works with existing event bus architecture
- ✅ Can run simple AI when SK unavailable (graceful degradation)

### Negative

- ❌ High complexity (three frameworks to learn)
- ❌ LLM latency (100-1000ms per decision)
- ❌ Cost of LLM API calls
- ❌ Debugging distributed actors is harder
- ❌ ~10+ additional NuGet packages

### Neutral

- ⚠️ Not all entities need all layers (simple goblins → ECS only)
- ⚠️ Intelligent AI reserved for important NPCs/bosses
- ⚠️ Can implement incrementally (start with bosses only)

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

- [ ] Add Akka.NET packages to `Directory.Packages.props`
- [ ] Add Semantic Kernel packages
- [ ] Create bridge components (`AkkaActorRef`, `SemanticAgent`, `IntelligentAI`)
- [ ] Implement `EventBusAkkaAdapter`
- [ ] Set up actor system with supervision

### Phase 2: Simple Boss AI (Week 3-4)

- [ ] Implement `AvatarActor` for bosses
- [ ] Implement `SemanticKernelBridgeActor`
- [ ] Create `NpcIntelligenceAgent` with basic decision-making
- [ ] Test with one boss entity
- [ ] Measure latency and performance

### Phase 3: Dialogue System (Week 5-6)

- [ ] Add dialogue capability to `IntelligentAI`
- [ ] Implement chat history tracking
- [ ] Create merchant NPC with dialogue
- [ ] Build UI for NPC conversations
- [ ] Test conversation persistence

### Phase 4: Advanced Features (Week 7-8)

- [ ] Add memory and learning
- [ ] Implement relationship tracking
- [ ] Create tactical planning for boss fights
- [ ] Add emotional state transitions
- [ ] Test save/load with Akka persistence

### Phase 5: Optimization (Week 9-10)

- [ ] Profile LLM call latency
- [ ] Implement caching for common decisions
- [ ] Add fallback AI when SK unavailable
- [ ] Optimize actor message throughput
- [ ] Document best practices

## Technical Specifications

### Package Dependencies

```xml
<!-- Akka.NET -->
<PackageVersion Include="Akka" Version="1.5.31" />
<PackageVersion Include="Akka.Hosting" Version="1.5.31" />
<PackageVersion Include="Akka.Persistence" Version="1.5.31" />
<PackageVersion Include="Akka.Persistence.Sql" Version="1.5.31" />

<!-- Semantic Kernel -->
<PackageVersion Include="Microsoft.SemanticKernel" Version="1.25.0" />
<PackageVersion Include="Microsoft.SemanticKernel.Agents.Core" Version="1.25.0-alpha" />
<PackageVersion Include="Microsoft.SemanticKernel.Connectors.OpenAI" Version="1.25.0" />
```

### Configuration

```json
{
  "SemanticKernel": {
    "OpenAI": {
      "ModelId": "gpt-4o-mini",
      "ApiKey": "sk-...",
      "MaxTokens": 500
    },
    "Fallback": {
      "EnableSimpleAI": true,
      "TimeoutMs": 5000
    }
  },
  "Akka": {
    "ActorSystem": "DungeonCrawler",
    "Persistence": {
      "ConnectionString": "Data Source=avatars.db"
    }
  }
}
```

### Performance Targets

- **ECS Queries**: < 1ms for 10,000 entities
- **Actor Messages**: < 10ms roundtrip
- **SK Decisions**: < 2000ms (with fallback at 5000ms)
- **Event Bus**: 1M+ events/sec (existing performance)

## Alternatives Considered

### Alternative 1: SK Only (No Akka.NET)

**Pros**: Simpler, fewer dependencies
**Cons**: No state management, no fault tolerance, no actor supervision
**Verdict**: ❌ Rejected - Missing lifecycle management

### Alternative 2: Akka.NET Only (No SK)

**Pros**: Stateful actors, supervision
**Cons**: Manual AI logic, no LLM reasoning, static behaviors
**Verdict**: ❌ Rejected - Missing intelligence layer

### Alternative 3: Custom Actor Pattern with MessagePipe

**Pros**: Lighter weight, uses existing MessagePipe
**Cons**: Reinventing Akka.NET features, no persistence, no supervision
**Verdict**: ⚠️ Possible for v1, but limits future capabilities

### Alternative 4: Three-Layer Architecture (Chosen)

**Pros**: Complete solution, best-in-class for each concern
**Cons**: Complexity, learning curve
**Verdict**: ✅ **Chosen** - Provides complete avatars

## References

- [Semantic Kernel Agent Framework](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/)
- [Akka.NET Documentation](https://getakka.net/articles/intro/what-is-akka.html)
- [Arch ECS Documentation](https://github.com/genaray/Arch)
- DOC-2025-00018: Lablab Bean Architecture
- DOC-2025-00033: Dungeon Crawler Features

## Approval

- [ ] **Technical Lead**: TBD
- [ ] **Project Owner**: TBD
- [ ] **Security Review**: TBD (API key management)
- [ ] **Performance Review**: TBD (latency acceptable?)

---

**Next Steps:**

1. Review this ADR with team
2. Create proof-of-concept with one boss
3. Measure performance and costs
4. Decide: Proceed or use Alternative 3
