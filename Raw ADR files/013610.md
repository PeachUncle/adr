# ADR-001: Application Architecture (Umbrella vs Single App)

## Status
Accepted

## Context
We need to decide the architectural structure for the multiplayer Parchís game backend. This decision will impact:

- **Separation of concerns**: How we organize game logic, web communication, and process coordination
- **Testability**: Ease of writing unit tests vs integration tests
- **Deployments**: Flexibility for independent deployments or as a single unit
- **Initial complexity vs scalability**: Balance between development simplicity and growth capacity
- **Team collaboration**: Future developer onboarding and parallel development

## Options Considered

**Option A: Single Phoenix Application**
- Single Phoenix application containing all functionality
- Phoenix contexts to separate game logic, web interface, and process management
- All dependencies bundled together

**Option B: Umbrella Project (3 apps)**
- `parchis_core`: Pure game logic (no external dependencies)
- `parchis_game`: Process management, GenServers, supervision trees
- `parchis_web`: Phoenix app with channels and HTTP interface

**Option C: Microservices**
- Separate services communicating via HTTP/gRPC
- Game service, Web service, potentially Match-making service

## Learning Resources for Decision
- **Umbrella Projects**: "Programming Phoenix 1.4" Chapter 13 (Chris McCord)
- **Elixir in Action** Chapter 13 - Building a distributed system (Saša Jurić)
- **Official Guide**: [Umbrella Projects - Elixir Guides](https://elixir-lang.org/getting-started/mix-otp/dependencies-and-umbrella-projects.html)
- **Best Practices**: José Valim's blog post "Umbrella projects" (2017)

## Decision
**Choose Option B: Umbrella Project (3 apps)**

## Rationale
1. **AI Agent Context Management**: Clear app boundaries allow keeping only relevant code in AI context when working on specific layers
2. **Well-Defined Domain Separation**: Game rules are stable and well-understood, making `parchis_core` a perfect candidate for pure functions
3. **Empirical Testing Strategy**: Separate apps enable isolated testing of pure logic vs infrastructure concerns
4. **Methodology Showcase**: Demonstrates clean architecture principles and AI-assisted development workflow
5. **Future Collaboration**: Clear boundaries facilitate parallel development when team grows

## Architecture Structure

```
apps/
├── parchis_core/        # Pure game logic - no external dependencies
│   ├── Game rules and validation
│   ├── Board state management  
│   └── Move calculations
├── parchis_game/        # Process coordination and state management
│   ├── GenServer processes
│   ├── Supervision trees
│   └── Game registry
└── parchis_web/         # Web interface and real-time communication
    ├── Phoenix channels
    ├── HTTP endpoints
    └── Client communication
```

## Consequences

**Positive:**
- Clear separation enables focused AI agent interactions
- Pure game logic can be tested in isolation
- Infrastructure can evolve independently from business rules
- Better showcase of architectural thinking

**Negative:**
- Initial setup complexity higher than single app
- Need to manage inter-app dependencies
- First-time umbrella learning curve

**Mitigation:**
- Start with minimal viable structure and evolve incrementally
- Use comprehensive documentation for umbrella-specific patterns
- Leverage empirical testing to validate architectural decisions

## Compliance
This decision supports Modern Software Engineering principles:
- **Fast Feedback**: Isolated testing of pure functions
- **Build Quality In**: Clear separation of concerns
- **Focus on Outcomes**: Architecture serves AI methodology goals