# ADR 003: Advanced Requests System Architecture

**Status**: Implemented
**Date**: 2025-10-30
**Decision Makers**: Development Team

## Context

PortalForge requires an advanced requests/applications system that allows:
- Creation of custom request templates by authorized users
- Department-specific visibility and routing
- Multi-stage approval workflows (Manager → Director)
- Optional quiz requirements with passing scores
- Professional UI matching enterprise systems (ServiceNow, Jira Service Desk)

### Business Requirements

1. **Template Management**: Admins with `requests.manage_templates` permission can create templates for any department
2. **Approval Flow**: Configurable multi-step approval (Kierownik → Dyrektor) based on organizational hierarchy
3. **Quiz System**: Optional quiz at any approval step with configurable passing threshold (e.g., 80%)
4. **Department Visibility**: Templates can be department-specific or available to all
5. **Professional Icons**: Lucide icon library instead of emojis
6. **User Experience**: Modern, intuitive interface with visual timeline and real-time status

## Decision

Implement a comprehensive requests system with:

### Backend Architecture

**Domain Layer:**
- 7 new entities: `RequestTemplate`, `RequestTemplateField`, `RequestApprovalStepTemplate`, `Request`, `RequestApprovalStep`, `QuizQuestion`, `QuizAnswer`
- 5 enums: `DepartmentRole`, `RequestStatus`, `ApprovalStepStatus`, `RequestPriority`, `FieldType`
- Extended `User` entity with `DepartmentRole` (Employee, Manager, Director)

**Application Layer (CQRS):**
- **Template Commands**: CreateRequestTemplate, SeedRequestTemplates
- **Template Queries**: GetRequestTemplates, GetAvailableRequestTemplates, GetRequestTemplateById
- **Request Commands**: SubmitRequest, ApproveRequestStep
- **Request Queries**: GetMyRequests, GetRequestsToApprove

**Infrastructure Layer:**
- Complete EF Core configurations with JSONB columns for flexibility
- 2 repositories with comprehensive querying
- Migration: `20251030200000_AddRequestsSystem`

**Permissions:**
- `requests.view` - View requests
- `requests.create` - Create requests
- `requests.approve` - Approve requests
- `requests.manage_templates` - Manage templates (admin-only)

### Frontend Architecture

**Type System:**
- Complete TypeScript interfaces matching backend DTOs
- Type-safe enums

**API Integration:**
- `useRequestsApi` composable with all endpoints
- Error handling and loading states

**Components:**
- `IconPicker` - 80+ Lucide icons with search
- `RequestTimeline` - Visual approval progress
- `QuizModal` - Interactive quiz with scoring

**Pages:**
- Admin: Template list, Template creator (4-step wizard)
- User: Browse templates, Submit request, Track requests

**Features:**
- Drag & drop form builder
- Dynamic form rendering (6 field types)
- Visual approval timeline
- Search and filtering
- Mobile-responsive

## Technical Decisions

### 1. **DepartmentRole vs Separate Table**

**Decision**: Add `DepartmentRole` enum to User entity

**Rationale**:
- Simpler implementation
- Aligns with organizational hierarchy already defined by SupervisorId
- No additional joins required
- Easy to understand and maintain

**Alternative Considered**: Separate `DepartmentRoles` table with many-to-many relationship
- Rejected: Over-engineering for this use case

### 2. **JSON Storage for Form Data**

**Decision**: Store form responses as JSONB in PostgreSQL

**Rationale**:
- Templates are dynamic - field structure varies per template
- JSONB allows flexible querying if needed
- No need for EAV (Entity-Attribute-Value) pattern
- PostgreSQL JSONB is performant and supports indexing

**Alternative Considered**: EAV pattern with RequestFieldValues table
- Rejected: Adds complexity, harder to query, more joins

### 3. **Quiz Integration Approach**

**Decision**: Quiz questions attached to template, answers to approval step

**Rationale**:
- Quiz is part of template definition
- Answers are contextual to specific approval
- Allows quiz reuse across multiple requests
- Score calculation at submission time

### 4. **Approval Step Routing**

**Decision**: Automatic approver assignment based on DepartmentRole + supervisor hierarchy

**Rationale**:
- Template defines roles (Manager, Director)
- System finds actual person via user.Supervisor chain
- Flexible - works regardless of org structure changes
- No need to manually assign approvers

**Alternative Considered**: Manual approver selection per request
- Rejected: Too much friction for users

### 5. **Icon Library Choice**

**Decision**: Lucide Vue Next

**Rationale**:
- Professional, consistent design
- 1000+ icons available
- Vue 3 native components
- Tree-shakeable
- Better than emojis for enterprise UI

**Alternative Considered**: Heroicons, FontAwesome
- Heroicons: Limited set
- FontAwesome: Large bundle size

### 6. **Form Builder Implementation**

**Decision**: vuedraggable + custom field configurator

**Rationale**:
- Intuitive drag & drop UX
- Standard pattern (ServiceNow-like)
- Well-maintained library
- Works with Vue 3

## Database Schema

### New Tables

```sql
RequestTemplates (8 columns + relations)
├── PK: Id (uuid)
├── Name, Description, Icon, Category
├── DepartmentId (nullable - null = all departments)
├── IsActive, RequiresApproval
├── EstimatedProcessingDays, PassingScore
├── CreatedById → Users
└── Relations: Fields[], ApprovalStepTemplates[], QuizQuestions[], Requests[]

RequestTemplateFields (10 columns)
├── PK: Id (uuid)
├── FK: RequestTemplateId
├── Label, FieldType, Placeholder
├── IsRequired, Options (JSONB)
├── MinValue, MaxValue, HelpText, Order

RequestApprovalStepTemplates (5 columns)
├── PK: Id (uuid)
├── FK: RequestTemplateId
├── StepOrder, ApproverRole, RequiresQuiz

QuizQuestions (4 columns)
├── PK: Id (uuid)
├── FK: RequestTemplateId
├── Question, Options (JSONB), Order

Requests (9 columns + relations)
├── PK: Id (uuid)
├── RequestNumber (unique), RequestTemplateId
├── SubmittedById, SubmittedAt, Priority
├── FormData (JSONB), Status, CompletedAt
└── Relations: ApprovalSteps[]

RequestApprovalSteps (11 columns)
├── PK: Id (uuid)
├── FK: RequestId, ApproverId
├── StepOrder, Status
├── StartedAt, FinishedAt, Comment
├── RequiresQuiz, QuizScore, QuizPassed

QuizAnswers (5 columns)
├── PK: Id (uuid)
├── FK: RequestApprovalStepId, QuizQuestionId
├── SelectedAnswer, IsCorrect, AnsweredAt
```

### Modified Tables

```sql
Users
└── Added: DepartmentRole (Employee/Manager/Director)
```

## API Endpoints

```
# Templates (Admin)
GET    /api/request-templates              [requests.manage_templates]
GET    /api/request-templates/available    [authenticated]
GET    /api/request-templates/{id}         [authenticated]
POST   /api/request-templates              [requests.manage_templates]
POST   /api/request-templates/seed         [requests.manage_templates]

# Requests (Users)
GET    /api/requests/my-requests            [requests.view]
GET    /api/requests/to-approve             [requests.approve]
POST   /api/requests                        [requests.create]
POST   /api/requests/{id}/steps/{stepId}/approve  [requests.approve]
```

## Approval Workflow Algorithm

```csharp
1. User submits request
2. Get template.ApprovalStepTemplates (ordered)
3. For each template step:
   - If ApproverRole = Manager → Find user.Supervisor
   - If ApproverRole = Director → Find user.Supervisor.Supervisor
   - Create RequestApprovalStep
   - First step: Status = InReview
   - Others: Status = Pending
4. Save request with all steps

On Approval:
1. Check: Is approver authorized?
2. Check: Is quiz required?
   - If yes and not passed → Status = RequiresSurvey, return
3. Approve current step (Status = Approved, FinishedAt = now)
4. Find next pending step
   - If exists → Status = InReview, StartedAt = now
   - If none → Request.Status = Approved, CompletedAt = now
```

## Quiz Scoring Algorithm

```typescript
1. User answers all questions
2. For each question:
   - Parse options JSON
   - Find option where isCorrect = true
   - Compare with user's selectedAnswer
   - Increment correctCount if match
3. Calculate: score = (correctCount / totalQuestions) * 100
4. Compare: passed = (score >= template.PassingScore)
5. Update step: QuizScore, QuizPassed
6. If passed → Allow approval
7. If failed → Status = SurveyFailed
```

## Consequences

### Positive

- ✅ **Flexibility**: Templates can be created without code changes
- ✅ **Scalability**: JSON storage handles varying form structures
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **User Experience**: Modern, intuitive interface
- ✅ **Type Safety**: Full TypeScript coverage
- ✅ **Testability**: Unit tests for critical paths
- ✅ **Performance**: Indexed queries, efficient data loading
- ✅ **Security**: Permission-based access control

### Challenges

- ⚠️ **Migration Required**: Users need DepartmentRole assignment
- ⚠️ **Supervisor Dependency**: Approval routing requires supervisors in org structure
- ⚠️ **JSON Querying**: Complex queries on FormData may be slow (can add specific indexes)

### Future Enhancements

- Email notifications on status changes
- File attachments support
- Request comments/discussion thread
- Template versioning
- SLA tracking and alerts
- Approval delegation
- Bulk approval actions
- Advanced reporting and analytics

## References

- [PRD](.ai/prd.md)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- ServiceNow Request Management
- Jira Service Desk best practices

## Implementation Files

**Backend:** 45 files (~3,500 LOC)
- 7 entities, 5 enums
- 7 EF configurations
- 1 migration
- 2 repositories
- 15 use cases
- 2 controllers
- 3 test files (11+ tests)

**Frontend:** 13 files (~2,000 LOC)
- 1 types file
- 1 composable
- 3 components
- 4 pages
- 1 middleware

**Dependencies Added:**
- `lucide-vue-next` - Icon library
- `vuedraggable` - Drag & drop

---

**Status**: ✅ All components implemented and tested
**Next Steps**: Apply migration, seed data, assign department roles

