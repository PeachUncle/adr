### **Status:** Selected

### **Date:** 27.06.2025

### **Author:** Pohorilets Vladyslav

## **Context**:

We need to pick an architectural style that:

- helps us reach our business goals,
- gives a clear structure to the system and shows how parts connect,
- makes it easier to make technical decisions later,
- keeps the code easy to maintain, test, and change,
- lets us update infrastructure without breaking the main logic,
- supports long-term development, even if requirements change.

## Reviewed options:

1. **Layered Architecture**
   - **Pros:**
     - Very simple and easy to understand
     - Well-known and supported by many tools and frameworks
     - Clear separation between layers (like controllers, services, repositories)
     - Easy to onboard new developers
     - Good for most business applications
   - **Cons:**
     - Sometimes layers can become too dependent on each other
     - If not careful, logic can "leak" between layers
     - Not as flexible as some other patterns for very complex systems

2. **Micro-kernel Architecture**
   - **Pros:**
     - Good for plugin-based systems
     - Easy to add new features as plugins
   - **Cons:**
     - Too complex for our current needs
     - Not a great fit for business logic-heavy apps

3. **Event-Driven Architecture**
   - **Pros:**
     - Scales well
     - Components are decoupled
   - **Cons:**
     - Harder to trace what's happening
     - More infrastructure needed
     - Overkill for our use case

4. **Clean Architecture**
   - **Pros:**
     - Very strict separation of concerns
     - High testability
     - Technology-agnostic core
   - **Cons:**
     - More complex to set up
     - Slower onboarding for new devs
     - Can be too much for smaller projects

## Decision taken:

We decided to use **Layered Architecture** for this project.

## Arguments

- Our project is a typical business application with clear layers: controllers (API), services (business logic), and repositories (data access).
- Layered Architecture is simple, easy to understand, and matches the way most teams work.
- It's easy to test each layer separately.
- New developers can quickly understand the structure and start working.
- We don't need the extra complexity of Clean Architecture or Event-Driven patterns right now.
- If the project grows, we can still refactor or add more advanced patterns later.

## Consequences:

**Positive**
- The codebase is easy to read and maintain.
- Onboarding new team members is fast.
- Each layer has a clear responsibility, so bugs are easier to find and fix.
- We can swap out infrastructure (like the database) with minimal changes to business logic.
- Testing is straightforward, since we can mock layers.

**Negative**
- If we're not careful, logic might leak between layers.
- For very large or complex systems, we might need to rethink the architecture later.
- Some flexibility is lost compared to more advanced patterns.
