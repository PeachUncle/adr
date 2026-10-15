# ADR-0004: Technology Stack Selection - Scala 3 and Functional Programming

**Status**: Accepted  
**Date**: 2025-11-26  
**Deciders**: Tony Moores  
**Technical Story**: Phase 0 - Foundation

## Context

TJMPaaS services require a technology stack that supports building scalable, maintainable, cloud-native applications. The stack selection impacts:

- Service development velocity
- Code quality and maintainability
- Developer productivity
- Performance and scalability
- Ecosystem and tooling availability
- Hiring and team expansion (future)
- Commercial viability and support

### Problem Statement

Select a primary technology stack for TJMPaaS service development that aligns with:
- Functional programming principles
- Modern language features and type safety
- Cloud-native and reactive system requirements
- Scalability and performance needs
- Container-friendly deployment

### Goals

- Strong type safety and functional programming support
- Excellent JVM ecosystem access
- Modern language features and syntax
- Good build tool and dependency management
- Active community and commercial support
- Aligns with digital commerce and e-commerce patterns
- Performance suitable for high-throughput services

### Constraints

- Must run in containers effectively
- Must support reactive patterns
- Must integrate with cloud-native infrastructure
- Solo developer initially - productivity matters
- Future team hiring considerations

## Decision

**Adopt Scala 3 with functional programming paradigm as the primary technology stack**, using:

- **Language**: Scala 3 (Scala 3.3+)
- **Programming Paradigm**: Functional programming (pure FP where practical)
- **Build Tool**: Mill
- **JVM**: OpenJDK (LTS versions)
- **Containerization**: Docker with optimized JVM settings

## Rationale

### Scala 3 Advantages

**Modern Language Features**:
- Significant syntax improvements over Scala 2
- Better type inference
- Improved metaprogramming (inline, macros)
- Union and intersection types
- Opaque types for zero-cost abstractions
- Given/using for context passing

**Functional Programming**:
- First-class FP support
- Immutable data structures
- Pattern matching and algebraic data types
- For-comprehensions for effect composition
- Seamless integration with FP libraries (Cats, ZIO, fs2)

**JVM Ecosystem**:
- Access to entire Java ecosystem
- Battle-tested JVM performance
- Extensive library availability
- Strong concurrency primitives
- Well-understood deployment and tuning

**Type Safety**:
- Strong static typing catches errors at compile time
- Reduced runtime errors
- Better refactoring support
- Self-documenting code through types
- Compiler as pair programmer

### Functional Programming Fit

**Reactive Systems**:
- FP naturally supports reactive patterns
- Immutability reduces concurrency issues
- Pure functions are easier to test and reason about
- Composition enables building complex systems from simple parts

**Digital Commerce**:
- FP excels at business logic modeling
- Type safety reduces payment/transaction errors
- Immutability critical for audit trails
- Pure functions simplify testing of business rules

**Maintainability**:
- Referential transparency aids understanding
- No hidden state reduces bugs
- Mathematical foundations provide rigor
- Composition over inheritance scales better

### Mill Build Tool

**Simplicity**:
- Scala-based build definitions (no new language)
- Fast and predictable
- Good IDE support
- Easy to understand and extend

**Performance**:
- Faster than sbt for many operations
- Better caching
- Parallel execution

**Modern**:
- Designed for modern Scala
- Good Scala 3 support
- Active development

### Performance Characteristics

**JVM**:
- Mature performance optimization
- Excellent garbage collection
- Just-in-time compilation
- Good profiling tools

**Scala 3**:
- Improved compile times vs Scala 2
- Better runtime performance
- Smaller bytecode
- TASTy for faster compilation

## Alternatives Considered

### Alternative 1: Kotlin

**Description**: JetBrains language for JVM with better Java interop

**Pros**:
- Excellent Java interop
- Good IDE support (IntelliJ)
- Growing adoption
- Simpler than Scala
- Good for team hiring

**Cons**:
- Less functional programming support than Scala
- Smaller FP ecosystem
- Not as strong for pure FP
- Less expressive type system
- Reactive support not as mature

**Reason for rejection**: Insufficient functional programming capabilities; doesn't align with FP paradigm preference

### Alternative 2: Java (Modern - 17+)

**Description**: Use modern Java with records, pattern matching, virtual threads

**Pros**:
- Ubiquitous
- Largest talent pool
- Most mature tooling
- Best library support
- Industry standard

**Cons**:
- Verbose compared to Scala
- Limited functional programming support
- Still heavily object-oriented
- Less expressive
- Doesn't align with FP preference

**Reason for rejection**: Insufficient functional programming support; too verbose for preferred development style

### Alternative 3: Haskell

**Description**: Pure functional language

**Pros**:
- Purest functional programming
- Most advanced type system
- Enforces FP discipline
- Excellent for learning FP
- Strong correctness guarantees

**Cons**:
- Steeper learning curve
- Smaller ecosystem
- Harder to hire for
- Less industry adoption
- Deployment complexity
- Not JVM-based (separate infrastructure)

**Reason for rejection**: Too niche for commercial viability; hiring concerns; ecosystem limitations

### Alternative 4: TypeScript/Node.js

**Description**: JavaScript with types for backend services

**Pros**:
- Large talent pool
- Fast development
- Good for APIs
- Excellent async support
- Large ecosystem

**Cons**:
- Not compiled language
- Weaker type system
- Not functional-first
- Performance limitations
- Not ideal for complex business logic

**Reason for rejection**: Insufficient type safety; doesn't align with FP paradigm; performance concerns for commerce workloads

### Alternative 5: Go

**Description**: Google's systems programming language

**Pros**:
- Simple and fast
- Excellent for cloud services
- Good concurrency (goroutines)
- Fast compilation
- Easy to learn

**Cons**:
- Not functional
- No generics until recently (limited)
- Verbose error handling
- Limited expressiveness
- Not suitable for FP approach

**Reason for rejection**: Not functional programming; doesn't align with paradigm preference

### Alternative 6: Rust

**Description**: Systems programming with memory safety

**Pros**:
- Memory safety without GC
- Excellent performance
- Growing ecosystem
- Modern language features
- Good for systems programming

**Cons**:
- Steep learning curve
- Ownership system complexity
- Not functional-first
- Smaller ecosystem than JVM
- Harder to hire for

**Reason for rejection**: Not functional-first; steep learning curve; ecosystem smaller than needed

## Consequences

### Positive

- **Expressive Code**: Scala 3 enables concise, readable code
- **Type Safety**: Strong typing catches errors at compile time
- **FP Benefits**: Immutability, pure functions, composition
- **JVM Ecosystem**: Access to vast library ecosystem
- **Performance**: JVM performance and optimization maturity
- **Maintainability**: FP principles improve long-term maintenance
- **Commercial Viability**: Scala used successfully in finance, e-commerce
- **Reactive Ready**: Excellent support for reactive patterns

### Negative

- **Learning Curve**: Scala and FP have learning curve
- **Compilation Speed**: Scala compilation slower than some languages
- **Hiring**: Smaller talent pool than Java/Python
- **Ecosystem Navigation**: Need to choose among FP libraries
- **JVM Overhead**: Container images larger than native executables

### Neutral

- **Community**: Smaller than Java but active and mature
- **Tooling**: Good but not as extensive as Java
- **Documentation**: Varies by library, improving

## Implementation

### Requirements

**Development Environment**:
- Scala 3.3+ (latest stable)
- Mill build tool
- OpenJDK 17 or 21 (LTS)
- VS Code with Metals or IntelliJ IDEA

**Core Libraries** (to be defined in service projects):
- Effect system: ZIO or Cats Effect
- HTTP: http4s or ZIO HTTP
- JSON: circe or zio-json
- Database: doobie or quill
- Testing: munit or scalatest
- Actor systems: Pekko, Akka Typed 2.6.x, or ZIO Actors (see ADR-0006)
- Event sourcing: Pekko Persistence or Akka Persistence (see ADR-0007)

**Framework Selection**:
- Best-fit framework per service
- Maximum 3 frameworks per category across all TJMSolns projects
- Open-source only (Apache 2.0, MIT, BSD, EPL)
- See [PDR-0005: Framework Selection Policy](../PDRs/PDR-0005-framework-selection-policy.md)

**Build Configuration**:
- Mill build definitions
- Dependency management in build.sc
- Multi-module support for complex services
- Docker image building integrated

**Container Optimization**:
- Layered JARs for better caching
- JVM tuning for containers
- Smaller base images (distroless or alpine)
- Memory settings appropriate for container limits

### Migration Path

Phase-by-phase adoption:
1. **Phase 0-1**: Establish stack, create first service
2. **Phase 2**: Expand service catalog with Scala 3
3. **Phase 3**: Refine patterns and libraries
4. **Future**: Consider GraalVM native image for select services

### Timeline

- **Q4 2025**: Stack selected, first service development begins
- **Q1 2026**: Core services implemented
- **Q2 2026**: Patterns and practices established
- **Ongoing**: Stack refined based on experience

## Validation

Success criteria:

- Services build and deploy successfully
- Performance meets requirements
- Code quality and maintainability high
- Development velocity acceptable
- FP principles applied consistently
- Integration with cloud infrastructure works well

Metrics:
- Build time acceptable (< 2 minutes for typical service)
- Service startup time < 30 seconds
- Development feedback loop fast
- Bug density low (FP benefits)
- Refactoring confidence high

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Scala learning curve | Medium | Start simple; use FP gradually; document patterns |
| Limited talent pool | Medium | Invest in documentation; consider contractors; training materials |
| Compilation speed | Low | Use Mill incremental compilation; keep services small |
| JVM container size | Low | Use optimized base images; layer JARs; consider native image later |
| Library choice paralysis | Medium | Define standard stack; document library selections |
| Ecosystem changes | Low | Use stable libraries; follow community; stay on LTS JDK |

## Related Decisions

- ADR-0003: Containerization Strategy (Scala 3 containerizes well)
- ADR-0005: Reactive Manifesto Alignment (Scala 3 supports reactive patterns)
- ADR-0006: Agent-Based Service Patterns (FP fits agent patterns)
- ADR-0007: CQRS and Event-Driven Architecture (Scala 3 excellent for CQRS/ES)
- PDR-0005: Framework Selection Policy (guidelines for library choices)
- [SECURITY-JWT-PERMISSIONS.md](../../technical/standards/SECURITY-JWT-PERMISSIONS.md) - Complete Scala/Akka HTTP JWT implementations
- Future ADR: Effect system selection (ZIO vs Cats Effect)
- Future ADR: HTTP framework selection

## Related Best Practices

This decision is validated by comprehensive industry research:

- **[Functional Programming Best Practices](../../technical/best-practices/architecture/functional-programming.md)**: Facebook study shows 57% fewer defects with FP; Jane Street successfully uses FP for $100B+ daily trading volume; Zalando reports better maintainability and team productivity.

- **[Scala 3 Best Practices](../../technical/best-practices/development/scala3.md)**: LinkedIn and Spotify have successfully adopted Scala 3 in production; 2-3x faster compilation than Scala 2.13; modern features (enums, opaque types, union types) significantly improve developer experience; excellent fit for domain modeling in commerce applications.

- **[Mill Build Tool Best Practices](../../technical/best-practices/development/mill-build-tool.md)**: VirtusLab reports 40% faster builds and 30% configuration reduction vs SBT; 2-3x faster incremental builds; Discord and Databricks use Mill successfully at scale; 10x simpler build configuration.

**Key Validation**: All three pillars of this technology stack decision (Scala 3, Functional Programming, Mill) are validated by industry evidence showing 2-3x compilation speed improvements, 40-60% fewer defects, and significant maintainability gains in production environments at scale.

## Related Features

**Features That Validate This Decision**:

*To be documented in Phase 1 (Governance Inference Analysis)*

Expected features:
- All service features should use Scala 3 with functional programming patterns
- Features should demonstrate immutability, pure functions, and effect systems (ZIO/Cats Effect)
- Mill build integration across all services

**Inference Tracking**: See [GOVERNANCE-FEATURE-INFERENCE-MAP.md](../../GOVERNANCE-FEATURE-INFERENCE-MAP.md#adr-0004-scala-3-technology-stack)

## References

- [Scala 3 Documentation](https://docs.scala-lang.org/scala3/)
- [Mill Build Tool](https://mill-build.com/)
- [Functional Programming in Scala](https://www.manning.com/books/functional-programming-in-scala-second-edition)
- [Reactive Manifesto](https://www.reactivemanifesto.org/)
- [Scala for Digital Commerce](https://www.lightbend.com/case-studies) - Various e-commerce case studies
- [ZIO](https://zio.dev/)
- [Typelevel Cats](https://typelevel.org/cats/)

## Notes

This decision aligns with Tony's preference for functional programming and positions TJMPaaS with a technology stack that:

- **Supports digital commerce**: Strong type safety reduces payment errors, audit trails benefit from immutability
- **Enables reactive systems**: FP naturally supports reactive patterns (see ADR-0005)
- **Facilitates maintainability**: Pure functions and immutability reduce complexity
- **Provides commercial credibility**: Scala used successfully by many e-commerce companies
- **Supports CQRS/ES**: Excellent for event-sourced systems and CQRS patterns (see ADR-0007)
- **Framework flexibility**: Rich ecosystem with multiple options per category (see PDR-0005)

The combination of Scala 3's modern features with functional programming provides the best foundation for building the sophisticated, reliable services required for digital commerce platforms.

While the talent pool is smaller than Java, the productivity and correctness benefits of FP with Scala 3 outweigh hiring challenges, especially for a solo developer initially. Documentation and clear patterns (see PDR-0004 for repository organization) will facilitate future team growth.

**Open-Source Requirement**:

All frameworks and libraries must use permissive open-source licenses (Apache 2.0, MIT, BSD, EPL) to ensure:
- Zero licensing costs
- Freedom to use in commercial offerings
- No vendor lock-in
- Ability to fork if needed

See PDR-0005 for detailed framework selection policy.

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-26 | Initial draft and acceptance | Tony Moores |
