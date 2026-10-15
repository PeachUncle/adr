# ADR-003: Workflow Engine Design (Hybrid State Machine + Event Sourcing)

## Status

Accepted

## Date

2025-12-02

## Context

The Workflow Manager requires a robust workflow execution engine that supports:

1. **State Management**:
   - Pause workflows at any step
   - Resume workflows from exact pause point
   - Validate state before transitions
   - Submit/complete workflows
   - Rollback to previous steps

2. **Intermediate State Persistence**:
   - Save state at every step transition
   - Query workflow state at any point
   - Recover from failures
   - Support long-running workflows (days/weeks)

3. **Audit Requirements**:
   - Complete history of all state changes
   - Who performed which actions
   - When changes occurred
   - Ability to replay workflows for debugging

4. **Market Role Complexity**:
   - Different workflows per market role (BRP, BSP, GU, etc.)
   - Dynamic step logic based on role
   - Custom validation per role
   - Extensible step types

5. **Operational Requirements**:
   - Compensation logic for rollback
   - Error handling and recovery
   - Concurrent workflow execution
   - Performance at scale (100s of active workflows)

## Decision

We will implement a **Hybrid Workflow Engine** combining:

- **State Machine** for explicit control flow
- **Event Sourcing** for audit trail and rollback
- **Saga Pattern** for compensation logic

### Architecture Overview

```typescript
┌─────────────────────────────────────────────────────────────┐
│                    Workflow Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   State      │  │    Event     │  │    Saga      │     │
│  │   Machine    │  │   Sourcing   │  │  Coordinator │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                           │                                  │
│                    ┌──────▼──────┐                          │
│                    │   Execution │                          │
│                    │   Context   │                          │
│                    └──────┬──────┘                          │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │               │
│    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐          │
│    │  Step   │      │  Step   │      │  Step   │          │
│    │ Handler │      │ Handler │      │ Handler │          │
│    │Registry │      │Executor │      │Validator│          │
│    └─────────┘      └─────────┘      └─────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. State Machine (Control Flow)

```typescript
// libs/workflow-engine/src/engine/StateMachine.ts

export interface WorkflowState {
  workflowId: string;
  tenantId: string;
  currentStepId: string;
  status: WorkflowStatus;
  stepStates: Map<string, StepState>;
  metadata: WorkflowMetadata;
}

export interface StepState {
  stepId: string;
  status: StepStatus;
  data: Record<string, any>;
  validationErrors?: ValidationError[];
  startedAt?: Date;
  completedAt?: Date;
  pausedAt?: Date;
}

export type WorkflowStatus =
  | 'draft'
  | 'in_progress'
  | 'paused'
  | 'awaiting_validation'
  | 'submitted'
  | 'completed'
  | 'failed'
  | 'rolled_back';

export type StepStatus = 'pending' | 'in_progress' | 'completed' | 'paused' | 'failed' | 'skipped';

export class StateMachine {
  private state: WorkflowState;
  private template: WorkflowTemplate;
  private transitions: TransitionMap;

  constructor(state: WorkflowState, template: WorkflowTemplate) {
    this.state = state;
    this.template = template;
    this.transitions = this.buildTransitionMap(template);
  }

  canTransition(toStepId: string): boolean {
    const allowedSteps = this.transitions.get(this.state.currentStepId);
    return allowedSteps?.includes(toStepId) ?? false;
  }

  async transition(toStepId: string, transitionData?: any): Promise<TransitionResult> {
    if (!this.canTransition(toStepId)) {
      throw new InvalidTransitionError(`Cannot transition from ${this.state.currentStepId} to ${toStepId}`);
    }

    const previousStepId = this.state.currentStepId;

    // Update state
    this.state.currentStepId = toStepId;
    this.state.stepStates.set(toStepId, {
      stepId: toStepId,
      status: 'in_progress',
      data: transitionData || {},
      startedAt: new Date(),
    });

    return {
      success: true,
      previousStepId,
      currentStepId: toStepId,
      state: this.state,
    };
  }

  getState(): WorkflowState {
    return this.state;
  }

  getCurrentStep(): WorkflowStep {
    return this.template.steps.find(s => s.id === this.state.currentStepId)!;
  }
}
```

#### 2. Event Sourcing (Audit Trail)

```typescript
// libs/workflow-engine/src/events/EventStore.ts

export interface WorkflowEvent {
  eventId: string;
  workflowId: string;
  tenantId: string;
  eventType: WorkflowEventType;
  stepId?: string;
  eventData: Record<string, any>;
  performedBy: string;
  occurredAt: Date;
}

export type WorkflowEventType =
  | 'WORKFLOW_CREATED'
  | 'WORKFLOW_STARTED'
  | 'STEP_STARTED'
  | 'STEP_COMPLETED'
  | 'STEP_FAILED'
  | 'STEP_VALIDATED'
  | 'STEP_PAUSED'
  | 'STEP_RESUMED'
  | 'WORKFLOW_PAUSED'
  | 'WORKFLOW_RESUMED'
  | 'WORKFLOW_SUBMITTED'
  | 'WORKFLOW_COMPLETED'
  | 'WORKFLOW_ROLLED_BACK'
  | 'STEP_COMPENSATED';

export class EventStore {
  constructor(private eventRepository: EventRepository) {}

  async append(event: Omit<WorkflowEvent, 'eventId' | 'occurredAt'>): Promise<WorkflowEvent> {
    const fullEvent: WorkflowEvent = {
      ...event,
      eventId: generateId(),
      occurredAt: new Date(),
    };

    await this.eventRepository.insert(fullEvent);

    return fullEvent;
  }

  async getEvents(workflowId: string, options?: EventQueryOptions): Promise<WorkflowEvent[]> {
    return this.eventRepository.findByWorkflowId(workflowId, options);
  }

  async getEventsSince(workflowId: string, timestamp: Date): Promise<WorkflowEvent[]> {
    return this.eventRepository.findByWorkflowId(workflowId, {
      since: timestamp,
    });
  }

  async rebuildState(workflowId: string, untilTimestamp?: Date): Promise<WorkflowState> {
    const events = await this.getEvents(workflowId, {
      until: untilTimestamp,
    });

    return this.replayEvents(events);
  }

  private replayEvents(events: WorkflowEvent[]): WorkflowState {
    let state = createInitialState();

    for (const event of events) {
      state = this.applyEvent(state, event);
    }

    return state;
  }

  private applyEvent(state: WorkflowState, event: WorkflowEvent): WorkflowState {
    switch (event.eventType) {
      case 'WORKFLOW_STARTED':
        return { ...state, status: 'in_progress' };

      case 'STEP_COMPLETED':
        const stepState = state.stepStates.get(event.stepId!);
        state.stepStates.set(event.stepId!, {
          ...stepState!,
          status: 'completed',
          data: event.eventData.stepData,
          completedAt: event.occurredAt,
        });
        return state;

      case 'WORKFLOW_PAUSED':
        return { ...state, status: 'paused' };

      // ... other event types

      default:
        return state;
    }
  }
}
```

#### 3. Saga Coordinator (Compensation)

```typescript
// libs/workflow-engine/src/engine/SagaCoordinator.ts

export interface CompensationAction {
  stepId: string;
  compensate: (context: CompensationContext) => Promise<void>;
}

export class SagaCoordinator {
  private compensations: Map<string, CompensationAction> = new Map();

  registerCompensation(stepId: string, action: CompensationAction): void {
    this.compensations.set(stepId, action);
  }

  async compensate(workflowId: string, fromStepId: string, toStepId: string, context: WorkflowContext): Promise<void> {
    // Get steps that need compensation
    const stepsToCompensate = await this.getStepsToCompensate(workflowId, fromStepId, toStepId);

    // Execute compensations in reverse order
    for (const stepId of stepsToCompensate.reverse()) {
      const compensation = this.compensations.get(stepId);

      if (compensation) {
        await compensation.compensate({
          workflowId,
          stepId,
          tenantId: context.tenantId,
          userId: context.userId,
        });

        await context.eventStore.append({
          workflowId,
          tenantId: context.tenantId,
          eventType: 'STEP_COMPENSATED',
          stepId,
          eventData: { compensatedAt: new Date() },
          performedBy: context.userId,
        });
      }
    }
  }

  private async getStepsToCompensate(workflowId: string, fromStepId: string, toStepId: string): Promise<string[]> {
    // Get workflow history and determine steps between from and to
    // Return list of step IDs that need compensation
    return []; // Implementation
  }
}
```

#### 4. Workflow Engine (Orchestrator)

```typescript
// libs/workflow-engine/src/engine/WorkflowEngine.ts

export class WorkflowEngine {
  constructor(
    private eventStore: EventStore,
    private sagaCoordinator: SagaCoordinator,
    private stepRegistry: StepRegistry,
    private workflowRepository: WorkflowRepository
  ) {}

  async executeStep(workflowId: string, stepId: string, input: any, context: WorkflowContext): Promise<StepResult> {
    // 1. Load workflow state from events
    const state = await this.loadWorkflowState(workflowId);

    // 2. Get template and build state machine
    const template = await this.getTemplate(state.templateId);
    const stateMachine = new StateMachine(state, template);

    // 3. Validate transition
    if (!stateMachine.canTransition(stepId)) {
      throw new InvalidTransitionError();
    }

    // 4. Get step handler
    const step = stateMachine.getCurrentStep();
    const handler = this.stepRegistry.get(step.type);

    // 5. Execute step
    try {
      await this.eventStore.append({
        workflowId,
        tenantId: context.tenantId,
        eventType: 'STEP_STARTED',
        stepId,
        eventData: { input },
        performedBy: context.userId,
      });

      const result = await handler.execute(step, input, context);

      if (result.success) {
        // Transition state machine
        await stateMachine.transition(step.next[result.outcome]);

        // Record event
        await this.eventStore.append({
          workflowId,
          tenantId: context.tenantId,
          eventType: 'STEP_COMPLETED',
          stepId,
          eventData: {
            output: result.data,
            nextStep: step.next[result.outcome],
          },
          performedBy: context.userId,
        });

        // Persist state
        await this.persistState(workflowId, stateMachine.getState());
      }

      return result;
    } catch (error) {
      await this.eventStore.append({
        workflowId,
        tenantId: context.tenantId,
        eventType: 'STEP_FAILED',
        stepId,
        eventData: { error: error.message },
        performedBy: context.userId,
      });

      throw error;
    }
  }

  async pause(workflowId: string, context: WorkflowContext): Promise<void> {
    const state = await this.loadWorkflowState(workflowId);

    state.status = 'paused';
    state.stepStates.get(state.currentStepId)!.pausedAt = new Date();

    await this.eventStore.append({
      workflowId,
      tenantId: context.tenantId,
      eventType: 'WORKFLOW_PAUSED',
      eventData: { pausedAt: new Date() },
      performedBy: context.userId,
    });

    await this.persistState(workflowId, state);
  }

  async resume(workflowId: string, context: WorkflowContext): Promise<void> {
    const state = await this.loadWorkflowState(workflowId);

    if (state.status !== 'paused') {
      throw new Error('Cannot resume workflow that is not paused');
    }

    state.status = 'in_progress';
    const currentStep = state.stepStates.get(state.currentStepId)!;
    delete currentStep.pausedAt;

    await this.eventStore.append({
      workflowId,
      tenantId: context.tenantId,
      eventType: 'WORKFLOW_RESUMED',
      eventData: { resumedAt: new Date() },
      performedBy: context.userId,
    });

    await this.persistState(workflowId, state);
  }

  async rollback(workflowId: string, toStepId: string, context: WorkflowContext): Promise<void> {
    const state = await this.loadWorkflowState(workflowId);

    // Validate rollback target
    if (!state.stepStates.has(toStepId)) {
      throw new Error('Cannot rollback to step not in history');
    }

    const targetStep = state.stepStates.get(toStepId)!;
    if (targetStep.status !== 'completed') {
      throw new Error('Can only rollback to completed steps');
    }

    // Execute compensations
    await this.sagaCoordinator.compensate(workflowId, state.currentStepId, toStepId, context);

    // Rebuild state to target point
    const targetTimestamp = targetStep.completedAt!;
    const rolledBackState = await this.eventStore.rebuildState(workflowId, targetTimestamp);

    rolledBackState.status = 'in_progress';
    rolledBackState.currentStepId = toStepId;

    await this.eventStore.append({
      workflowId,
      tenantId: context.tenantId,
      eventType: 'WORKFLOW_ROLLED_BACK',
      eventData: { toStepId, rolledBackAt: new Date() },
      performedBy: context.userId,
    });

    await this.persistState(workflowId, rolledBackState);
  }

  async validate(workflowId: string, context: WorkflowContext): Promise<ValidationResult> {
    const state = await this.loadWorkflowState(workflowId);
    const template = await this.getTemplate(state.templateId);

    const errors: ValidationError[] = [];

    for (const [stepId, stepState] of state.stepStates) {
      const step = template.steps.find(s => s.id === stepId);
      if (!step) continue;

      const handler = this.stepRegistry.get(step.type);
      const validationResult = await handler.validate(step, stepState.data);

      if (!validationResult.valid) {
        errors.push(...validationResult.errors);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  async submit(workflowId: string, context: WorkflowContext): Promise<SubmitResult> {
    // Validate before submit
    const validation = await this.validate(workflowId, context);
    if (!validation.valid) {
      throw new ValidationError('Workflow has validation errors', validation.errors);
    }

    const state = await this.loadWorkflowState(workflowId);
    state.status = 'submitted';

    await this.eventStore.append({
      workflowId,
      tenantId: context.tenantId,
      eventType: 'WORKFLOW_SUBMITTED',
      eventData: { submittedAt: new Date() },
      performedBy: context.userId,
    });

    await this.persistState(workflowId, state);

    return { success: true, workflowId };
  }

  private async loadWorkflowState(workflowId: string): Promise<WorkflowState> {
    // Try to load from MongoDB (fast)
    const cached = await this.workflowRepository.findById(workflowId);
    if (cached) return cached.state;

    // Fallback: rebuild from events
    return await this.eventStore.rebuildState(workflowId);
  }

  private async persistState(workflowId: string, state: WorkflowState): Promise<void> {
    // Update MongoDB (current state)
    await this.workflowRepository.updateState(workflowId, state);

    // Update PostgreSQL index (for queries)
    await this.workflowRepository.updateIndex(workflowId, {
      status: state.status,
      currentStepId: state.currentStepId,
      updatedAt: new Date(),
    });
  }
}
```

#### 5. Step Handler System

```typescript
// libs/workflow-engine/src/steps/StepHandler.ts

export interface StepHandler<TConfig = any, TInput = any, TOutput = any> {
  readonly type: string;

  validate(step: WorkflowStep<TConfig>, data: TInput): Promise<ValidationResult>;

  execute(step: WorkflowStep<TConfig>, input: TInput, context: WorkflowContext): Promise<StepResult<TOutput>>;

  compensate?(context: CompensationContext): Promise<void>;
}

export interface StepResult<T = any> {
  success: boolean;
  outcome: string; // 'default', 'approved', 'rejected', etc.
  data?: T;
  error?: Error;
}

// Built-in handler example
export class FormStepHandler implements StepHandler {
  readonly type = 'form';

  async validate(step: WorkflowStep, data: any): Promise<ValidationResult> {
    const schema = step.config.validation;
    try {
      await schema.parseAsync(data);
      return { valid: true, errors: [] };
    } catch (error) {
      return {
        valid: false,
        errors: error.errors,
      };
    }
  }

  async execute(step: WorkflowStep, input: any, context: WorkflowContext): Promise<StepResult> {
    // Validate
    const validation = await this.validate(step, input);
    if (!validation.valid) {
      return {
        success: false,
        outcome: 'validation_failed',
        error: new ValidationError('Form validation failed', validation.errors),
      };
    }

    // Save to database
    await context.database.saveStepData(context.workflowId, step.id, input);

    return {
      success: true,
      outcome: 'default',
      data: input,
    };
  }

  async compensate(context: CompensationContext): Promise<void> {
    // Delete saved form data
    await context.database.deleteStepData(context.workflowId, context.stepId);
  }
}
```

## State Persistence Strategy

### Dual Storage Pattern

**MongoDB (Source of Truth for State)**:

```typescript
workflow_instances {
  _id: ObjectId,
  tenantId: ObjectId,
  templateId: ObjectId,
  status: 'in_progress' | 'paused' | ...,
  currentStepId: string,
  state: {
    stepStates: {
      'step-1': { status: 'completed', data: {...}, completedAt: Date },
      'step-2': { status: 'in_progress', data: {...}, startedAt: Date }
    },
    metadata: { ... }
  },
  updatedAt: Date
}
```

**PostgreSQL (Index for Queries)**:

```sql
workflow_instances_index (
  id uuid PRIMARY KEY,
  tenant_id uuid,
  status text,
  current_step_id text,
  mongo_id text,
  created_at timestamptz,
  updated_at timestamptz
)
```

**MongoDB (Event Log)**:

```typescript
workflow_events {
  _id: ObjectId,
  workflowId: ObjectId,
  tenantId: ObjectId,
  eventType: 'STEP_COMPLETED',
  stepId: 'step-1',
  eventData: {...},
  performedBy: ObjectId,
  occurredAt: Date
}
```

## Consequences

### Positive

1. **Complete Audit Trail**
   - Every state change recorded as event
   - Can replay workflows for debugging
   - Compliance-ready audit logs

2. **Robust Rollback**
   - Compensation logic built-in
   - Replay events to any point in time
   - Safe rollback with validation

3. **Pause/Resume Support**
   - State persisted at every step
   - Can resume from exact point
   - Long-running workflow support

4. **Extensibility**
   - Plugin step handlers
   - Custom compensation logic
   - Market role-specific steps

5. **Failure Recovery**
   - Rebuild state from events
   - Recover from crashes
   - Idempotent operations

6. **Performance**
   - Cached state in MongoDB (fast reads)
   - Event append-only (fast writes)
   - PostgreSQL index for queries

### Negative

1. **Complexity**
   - Three patterns combined
   - More code to maintain
   - Steeper learning curve

2. **Storage Overhead**
   - Events stored permanently
   - State duplicated (Mongo + PG)
   - Growing event log

3. **Event Replay Performance**
   - Replaying long workflows slow
   - Need snapshot optimization
   - Memory consumption

4. **Compensation Logic**
   - Must implement for each step type
   - Complexity for complex operations
   - Testing compensation paths

### Mitigation Strategies

1. **Event Snapshots**
   - Create snapshots every N events
   - Replay from latest snapshot
   - Prune old events with snapshots

2. **Documentation**
   - Clear examples for each pattern
   - Step handler development guide
   - Compensation best practices

3. **Testing**
   - Test compensation paths
   - Event replay tests
   - State machine validation

4. **Monitoring**
   - Track event log size
   - Monitor replay performance
   - Alert on compensation failures

## Implementation Example

```typescript
// Usage in API
const engine = new WorkflowEngine(eventStore, sagaCoordinator, stepRegistry, workflowRepository);

// Create workflow
const workflowId = await engine.create({
  tenantId,
  templateId: 'brp-onboarding',
  createdBy: userId,
});

// Execute first step
await engine.executeStep(
  workflowId,
  'company-info',
  {
    companyName: 'Engie Belgium',
    vatNumber: 'BE0403170701',
  },
  context
);

// Pause
await engine.pause(workflowId, context);

// Resume later
await engine.resume(workflowId, context);

// Execute next step
await engine.executeStep(
  workflowId,
  'portfolio-definition',
  {
    accessPoints: ['EAN123'],
  },
  context
);

// Validate
const validation = await engine.validate(workflowId, context);

// Submit
if (validation.valid) {
  await engine.submit(workflowId, context);
}

// Rollback if needed
await engine.rollback(workflowId, 'company-info', context);
```

## Related ADRs

- ADR-001: Hybrid Database Architecture (PostgreSQL + MongoDB)
- ADR-002: Hybrid Modular Monorepo Structure
- ADR-004: GraphQL API Architecture [Pending]

## References

- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Saga Pattern](https://microservices.io/patterns/data/saga.html)
- [State Machine Pattern](https://refactoring.guru/design-patterns/state)
- [Command Query Responsibility Segregation (CQRS)](https://martinfowler.com/bliki/CQRS.html)
