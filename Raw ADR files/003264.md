# ADR 005: Organizational Structure & Vacation Management System

**Status**: 📋 Planned (Implementation Pending)
**Date**: 2025-10-31
**Decision Makers**: Development Team

## Context

PortalForge's request approval system currently has limitations:
1. **No formal organizational structure** - Departments are stored as strings, not entities
2. **Limited hierarchy** - Only 3 roles (Employee, Manager, Director)
3. **Manual approver assignment** - No automatic routing based on organizational hierarchy
4. **No vacation coverage** - When approvers are on vacation, requests get stuck
5. **No visibility** - Managers can't see team vacation schedules

### Business Requirements

1. **Organizational Structure**:
   - Unlimited hierarchical depth (Board → VP → Director → Manager → Team Lead → Employee)
   - Department entity with parent-child relationships
   - Clear reporting lines (SupervisorId chain)
   - Visibility permissions (users see only their department by default)

2. **Vacation Management**:
   - Automatic substitute selection in vacation requests
   - Automatic routing to substitute when approver is on vacation
   - Team vacation calendar for managers (Timeline, Grid, List views)
   - Conflict detection (>30% team on vacation = alert)
   - Export to PDF/Excel

3. **Request Routing Intelligence**:
   - Multi-level hierarchy support (Employee → Manager → Director → VP → President)
   - Auto-approval when no higher supervisor exists
   - Support for specific department heads as approvers
   - Support for specific users or groups as approvers

4. **Notifications**:
   - In-app notifications when requests need approval
   - Email notifications (Phase 2)
   - Real-time updates (SignalR - optional)

## Decision

Implement a comprehensive organizational structure with intelligent vacation management:

### 1. Core Entities

#### Department Entity
```csharp
public class Department
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }

    // Unlimited hierarchy support
    public Guid? ParentDepartmentId { get; set; }
    public Department? ParentDepartment { get; set; }
    public ICollection<Department> ChildDepartments { get; set; }

    // Department head
    public Guid? HeadOfDepartmentId { get; set; }
    public User? HeadOfDepartment { get; set; }

    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }

    // Navigation
    public ICollection<User> Employees { get; set; }
}
```

#### VacationSchedule Entity
```csharp
public class VacationSchedule
{
    public Guid Id { get; set; }

    public Guid UserId { get; set; }
    public User User { get; set; }

    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }

    public Guid SubstituteUserId { get; set; }
    public User Substitute { get; set; }

    // Link to approved vacation request
    public Guid SourceRequestId { get; set; }
    public Request SourceRequest { get; set; }

    public VacationStatus Status { get; set; }
    public DateTime CreatedAt { get; set; }
}

public enum VacationStatus
{
    Scheduled,  // Future vacation
    Active,     // Currently on vacation
    Completed,  // Past vacation
    Cancelled   // Cancelled vacation
}
```

#### OrganizationalPermission Entity
```csharp
public class OrganizationalPermission
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public User User { get; set; }

    // Visibility permissions
    public bool CanViewAllDepartments { get; set; }
    public string VisibleDepartmentIds { get; set; } // JSON array of Guid[]

    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}
```

### 2. Enhanced Enums

#### Extended DepartmentRole
```csharp
public enum DepartmentRole
{
    Employee,       // Regular employee
    TeamLeader,     // Team lead (manages small team)
    Manager,        // Department manager
    Director,       // Department director
    VicePresident,  // Vice President
    President,      // President/CEO
    BoardMember     // Board member
}
```

#### Enhanced ApproverType
```csharp
public enum ApproverType
{
    Role,                  // Hierarchical role (Manager, Director)
    SpecificUser,          // Specific user by ID
    UserGroup,             // Any user from a RoleGroup
    SpecificDepartment,    // Head of specific department (NEW)
    DirectSupervisor       // Direct supervisor of submitter (NEW)
}
```

### 3. Request Routing Service

**Intelligent Approver Resolution:**

```csharp
public class RequestRoutingService
{
    public async Task<User?> ResolveApproverAsync(
        RequestApprovalStepTemplate stepTemplate,
        User submitter)
    {
        return stepTemplate.ApproverType switch
        {
            ApproverType.DirectSupervisor => submitter.Supervisor,

            ApproverType.Role => await ResolveByRoleAsync(
                stepTemplate.ApproverRole!.Value,
                submitter
            ),

            ApproverType.SpecificUser => await _unitOfWork.UserRepository
                .GetByIdAsync(stepTemplate.SpecificUserId!.Value),

            ApproverType.SpecificDepartment => await GetDepartmentHeadAsync(
                stepTemplate.SpecificDepartmentId!.Value
            ),

            ApproverType.UserGroup => await GetFirstAvailableFromGroupAsync(
                stepTemplate.ApproverGroupId!.Value
            ),

            _ => null
        };
    }

    private async Task<User?> ResolveByRoleAsync(
        DepartmentRole targetRole,
        User submitter)
    {
        var currentUser = submitter;

        // Walk up the supervisor chain
        while (currentUser.Supervisor != null)
        {
            if (currentUser.Supervisor.DepartmentRole >= targetRole)
            {
                return currentUser.Supervisor;
            }
            currentUser = currentUser.Supervisor;
        }

        // No higher supervisor - auto-approve scenario
        return null;
    }

    public async Task<bool> HasHigherSupervisor(User user)
    {
        return user.Supervisor != null;
    }
}
```

**Auto-Approval Logic:**

```csharp
// In SubmitRequestCommandHandler
var approver = await _routingService.ResolveApproverAsync(stepTemplate, submitter);

if (approver == null)
{
    // No higher supervisor exists - auto-approve
    var autoApprovedStep = new RequestApprovalStep
    {
        StepOrder = stepTemplate.StepOrder,
        ApproverId = submitter.Id, // Self-approved
        ApproverName = "Auto-approved (No higher supervisor)",
        Status = ApprovalStepStatus.Approved,
        Comment = "Automatically approved - submitter has no higher supervisor",
        StartedAt = DateTime.UtcNow,
        FinishedAt = DateTime.UtcNow
    };

    request.ApprovalSteps.Add(autoApprovedStep);
    _logger.LogInformation(
        "Auto-approved step {StepOrder} for request {RequestId} - no higher supervisor",
        stepTemplate.StepOrder,
        request.Id
    );
}
```

### 4. Vacation Schedule Service

**Core Functionality:**

```csharp
public class VacationScheduleService
{
    // Create vacation schedule from approved request
    public async Task CreateFromApprovedRequestAsync(Request vacationRequest)
    {
        var formData = JsonSerializer.Deserialize<Dictionary<string, object>>(
            vacationRequest.FormData
        );

        var schedule = new VacationSchedule
        {
            UserId = vacationRequest.SubmittedById,
            StartDate = DateTime.Parse(formData["startDate"].ToString()!),
            EndDate = DateTime.Parse(formData["endDate"].ToString()!),
            SubstituteUserId = Guid.Parse(formData["substitute"].ToString()!),
            SourceRequestId = vacationRequest.Id,
            Status = VacationStatus.Scheduled
        };

        await _context.VacationSchedules.AddAsync(schedule);
        await _context.SaveChangesAsync();

        _logger.LogInformation(
            "Created vacation schedule for {UserId} from {Start} to {End}, substitute: {SubstituteId}",
            schedule.UserId, schedule.StartDate, schedule.EndDate, schedule.SubstituteUserId
        );
    }

    // Get active substitute (if user is on vacation)
    public async Task<User?> GetActiveSubstituteAsync(Guid userId)
    {
        var now = DateTime.UtcNow;
        var schedule = await _context.VacationSchedules
            .Include(v => v.Substitute)
            .FirstOrDefaultAsync(v =>
                v.UserId == userId
                && v.StartDate <= now
                && v.EndDate >= now
                && v.Status == VacationStatus.Active
            );

        return schedule?.Substitute;
    }

    // Get team vacation calendar with conflict detection
    public async Task<VacationCalendar> GetTeamCalendarAsync(
        Guid departmentId,
        DateTime startDate,
        DateTime endDate)
    {
        var vacations = await _context.VacationSchedules
            .Include(v => v.User)
            .Include(v => v.Substitute)
            .Where(v =>
                v.User.DepartmentId == departmentId
                && v.EndDate >= startDate
                && v.StartDate <= endDate
            )
            .OrderBy(v => v.StartDate)
            .ToListAsync();

        var teamSize = await _context.Users
            .CountAsync(u => u.DepartmentId == departmentId && u.IsActive);

        return new VacationCalendar
        {
            Vacations = vacations,
            TeamSize = teamSize,
            Alerts = DetectConflicts(vacations, teamSize),
            Statistics = CalculateStatistics(vacations, teamSize)
        };
    }

    // Detect vacation conflicts (>30% team on vacation)
    private List<VacationAlert> DetectConflicts(
        List<VacationSchedule> vacations,
        int teamSize)
    {
        var alerts = new List<VacationAlert>();

        if (teamSize == 0) return alerts;

        var allDates = GetDateRange(vacations);

        foreach (var date in allDates)
        {
            var onVacationCount = vacations.Count(v =>
                v.StartDate <= date && v.EndDate >= date
            );

            var coveragePercent = (double)onVacationCount / teamSize * 100;

            if (coveragePercent >= 30)
            {
                alerts.Add(new VacationAlert
                {
                    Date = date,
                    Type = coveragePercent >= 50
                        ? AlertType.COVERAGE_CRITICAL
                        : AlertType.COVERAGE_LOW,
                    AffectedEmployees = vacations
                        .Where(v => v.StartDate <= date && v.EndDate >= date)
                        .Select(v => v.User)
                        .ToList(),
                    CoveragePercent = coveragePercent,
                    Message = $"⚠️ {onVacationCount}/{teamSize} pracowników na urlopie ({coveragePercent:F0}%)"
                });
            }
        }

        return alerts;
    }

    // Daily job to update vacation statuses
    public async Task UpdateVacationStatusesAsync()
    {
        var now = DateTime.UtcNow.Date;

        // Activate scheduled vacations
        var toActivate = await _context.VacationSchedules
            .Where(v => v.Status == VacationStatus.Scheduled && v.StartDate <= now)
            .ToListAsync();

        foreach (var vacation in toActivate)
        {
            vacation.Status = VacationStatus.Active;
            _logger.LogInformation(
                "Activated vacation for {UserId} - now on vacation until {EndDate}",
                vacation.UserId, vacation.EndDate
            );
        }

        // Complete active vacations
        var toComplete = await _context.VacationSchedules
            .Where(v => v.Status == VacationStatus.Active && v.EndDate < now)
            .ToListAsync();

        foreach (var vacation in toComplete)
        {
            vacation.Status = VacationStatus.Completed;
            _logger.LogInformation(
                "Completed vacation for {UserId}",
                vacation.UserId
            );
        }

        await _context.SaveChangesAsync();
    }
}
```

### 5. Frontend Components

#### Vacation Calendar Views

**Timeline View (Gantt Chart):**
- Visual bar chart showing vacations over time
- Color-coded by status (Scheduled=green, Active=blue, Completed=gray)
- Hover tooltips with details
- Click to view vacation details

**Calendar Grid View:**
- Traditional month calendar
- Multiple people per day shown as badges
- Click day to see who's on vacation

**List View:**
- Sortable table
- Columns: Employee, Start Date, End Date, Days Count, Substitute
- Export to Excel/PDF

#### Statistics Dashboard
```vue
<div class="grid grid-cols-3 gap-4">
  <StatCard
    icon="users"
    :value="currentlyOnVacation"
    label="Obecnie na urlopie"
    :subtitle="`z ${teamSize} pracowników`"
    color="blue"
  />

  <StatCard
    icon="calendar"
    :value="scheduledVacations"
    label="Zaplanowanych urlopów"
    subtitle="w tym miesiącu"
    color="green"
  />

  <StatCard
    v-if="alerts.length > 0"
    icon="alert-triangle"
    :value="alerts.length"
    label="Alerty kolizji"
    color="red"
  />
</div>
```

## Technical Decisions

### 1. **Department as Entity vs String**

**Decision**: Create Department entity with unlimited hierarchy

**Rationale**:
- Enables proper organizational structure
- Supports unlimited depth (Board → VP → Director → Manager → Team Lead → Employee)
- Allows department-level permissions and reporting
- Facilitates department-based filtering and routing
- Prepares for Active Directory/LDAP integration

**Migration Strategy**:
1. Create Department table
2. Migrate existing User.Department (string) → create Department records
3. Add User.DepartmentId (Guid) foreign key
4. Keep old User.Department field temporarily (deprecated)
5. After migration verified, drop old field

### 2. **Vacation Substitute in Form vs Separate Table**

**Decision**: Hybrid approach - field in request form + VacationSchedule table

**Rationale**:
- **Form Field**: User selects substitute when submitting vacation request
- **VacationSchedule Table**: Created automatically when request is approved
- **Benefits**:
  - User choice preserved in request history
  - Efficient querying for active vacations
  - Easy to check if someone is on vacation
  - Supports calendar views and conflict detection

**Alternative Considered**: Manual delegation table
- Rejected: Less user-friendly, requires manual setup before vacation

### 3. **Auto-Approval Logic**

**Decision**: Auto-approve requests when submitter has no higher supervisor

**Rationale**:
- **Scenario**: President/Board member submits vacation request
- **Problem**: No one above them to approve
- **Solution**: System auto-approves with audit trail
- **Safeguard**: Logged as "Auto-approved - no higher supervisor"
- **Alternative**: Could route to specific approval group (e.g., Board), but adds complexity

**Implementation**:
```csharp
if (approver == null)
{
    // Auto-approve with audit trail
    step.Status = Approved;
    step.Comment = "Auto-approved (no higher supervisor)";
    step.ApproverId = submitter.Id;
}
```

### 4. **Conflict Detection Threshold**

**Decision**: Alert when >30% of team on vacation, critical when >50%

**Rationale**:
- **30% threshold**: Yellow warning - coverage may be impacted
- **50% threshold**: Red critical - significant coverage risk
- **Customizable**: Can be configured per department
- **Based on**: Industry best practices for team coverage

### 5. **Vacation Calendar Export**

**Decision**: Server-side PDF/Excel generation using QuestPDF and EPPlus

**Rationale**:
- **QuestPDF**: Modern, fluent API for PDF generation
- **EPPlus**: Mature, reliable Excel generation
- **Server-side**: Consistent formatting, no browser compatibility issues
- **Alternative**: Client-side (jsPDF, ExcelJS) - rejected due to complexity

## Implementation Plan

### Sprint 1: Backend Foundation (Days 1-4)
- [x] Create Department entity + EF configuration
- [ ] Create VacationSchedule entity + EF configuration
- [ ] Create OrganizationalPermission entity
- [ ] Extend DepartmentRole enum (7 roles)
- [ ] Extend ApproverType enum (5 types)
- [ ] Migration: AddOrganizationalStructure
- [ ] Migration: MigrateUserDepartmentToEntity
- [ ] Migration: AddVacationScheduleSystem

### Sprint 2: Routing & Vacation Logic (Days 5-7)
- [ ] Implement RequestRoutingService
- [ ] Implement VacationScheduleService
- [ ] Auto-approval logic in SubmitRequestCommandHandler
- [ ] Substitute routing in ApproveRequestStepCommandHandler
- [ ] Daily job: UpdateVacationStatusesJob
- [ ] Unit tests for routing logic
- [ ] Unit tests for vacation logic

### Sprint 3: Frontend - Vacation Calendar (Days 8-11)
- [ ] VacationTimelineView component (Gantt chart)
- [ ] VacationCalendarGrid component (month view)
- [ ] VacationListView component (table)
- [ ] Page: /dashboard/team/vacation-calendar
- [ ] Statistics dashboard with alerts
- [ ] Export to PDF endpoint + frontend
- [ ] Export to Excel endpoint + frontend
- [ ] UserAutocomplete component (for substitute selection)

### Sprint 4: Frontend - Structure & Requests (Days 12-14)
- [ ] Page: /admin/structure (org chart tree)
- [ ] DepartmentTree component (recursive)
- [ ] Page: /admin/departments/[id] (department details)
- [ ] Fix clickable requests (NuxtLink instead of button)
- [ ] Page: /dashboard/requests/[id] (request details)
- [ ] Update request template form (substitute field, department dropdown)
- [ ] Panel: "Moje zastępstwa" (my substitutions)

### Sprint 5: Permissions & Notifications (Days 15-16)
- [ ] OrganizationalPermission CRUD endpoints
- [ ] Admin panel: Grant department visibility
- [ ] Notification system enhancements
- [ ] NotificationBell component improvements
- [ ] Email notifications (using SendGrid/SMTP)

### Sprint 6: Testing & Documentation (Days 17-18)
- [ ] Unit tests: RequestRoutingService (80%+ coverage)
- [ ] Unit tests: VacationScheduleService (80%+ coverage)
- [ ] Integration tests: Department CRUD
- [ ] Integration tests: Vacation calendar endpoints
- [ ] E2E tests: Create department, assign head
- [ ] E2E tests: Submit vacation request with substitute
- [ ] E2E tests: View vacation calendar, detect conflicts
- [ ] Documentation updates

## Database Migrations

### Migration 1: AddOrganizationalStructure

```sql
-- Create Departments table
CREATE TABLE "Departments" (
    "Id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "Name" VARCHAR(200) NOT NULL,
    "Description" TEXT NULL,
    "ParentDepartmentId" UUID NULL,
    "HeadOfDepartmentId" UUID NULL,
    "IsActive" BOOLEAN NOT NULL DEFAULT TRUE,
    "CreatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt" TIMESTAMP NULL,
    CONSTRAINT "FK_Departments_Departments_ParentDepartmentId"
        FOREIGN KEY ("ParentDepartmentId") REFERENCES "Departments"("Id") ON DELETE RESTRICT,
    CONSTRAINT "FK_Departments_Users_HeadOfDepartmentId"
        FOREIGN KEY ("HeadOfDepartmentId") REFERENCES "Users"("Id") ON DELETE SET NULL
);

CREATE INDEX "IX_Departments_ParentDepartmentId" ON "Departments"("ParentDepartmentId");
CREATE INDEX "IX_Departments_HeadOfDepartmentId" ON "Departments"("HeadOfDepartmentId");
CREATE INDEX "IX_Departments_IsActive" ON "Departments"("IsActive");

-- Add DepartmentId to Users (nullable initially)
ALTER TABLE "Users" ADD COLUMN "DepartmentId" UUID NULL;
ALTER TABLE "Users" ADD CONSTRAINT "FK_Users_Departments_DepartmentId"
    FOREIGN KEY ("DepartmentId") REFERENCES "Departments"("Id") ON DELETE RESTRICT;

CREATE INDEX "IX_Users_DepartmentId" ON "Users"("DepartmentId");

-- Extend DepartmentRole enum
-- (Handled in C# enum, PostgreSQL stores as string)
```

### Migration 2: MigrateUserDepartmentToEntity

```sql
-- Create department records from existing User.Department strings
INSERT INTO "Departments" ("Id", "Name", "Description", "IsActive", "CreatedAt")
SELECT
    gen_random_uuid(),
    DISTINCT "Department",
    '',
    TRUE,
    NOW()
FROM "Users"
WHERE "Department" IS NOT NULL AND "Department" != '';

-- Update Users.DepartmentId based on Department name
UPDATE "Users" u
SET "DepartmentId" = d."Id"
FROM "Departments" d
WHERE u."Department" = d."Name";
```

### Migration 3: AddVacationScheduleSystem

```sql
-- Create VacationSchedules table
CREATE TABLE "VacationSchedules" (
    "Id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "UserId" UUID NOT NULL,
    "StartDate" DATE NOT NULL,
    "EndDate" DATE NOT NULL,
    "SubstituteUserId" UUID NOT NULL,
    "SourceRequestId" UUID NOT NULL,
    "Status" VARCHAR(50) NOT NULL DEFAULT 'Scheduled',
    "CreatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT "FK_VacationSchedules_Users_UserId"
        FOREIGN KEY ("UserId") REFERENCES "Users"("Id") ON DELETE CASCADE,
    CONSTRAINT "FK_VacationSchedules_Users_SubstituteUserId"
        FOREIGN KEY ("SubstituteUserId") REFERENCES "Users"("Id") ON DELETE RESTRICT,
    CONSTRAINT "FK_VacationSchedules_Requests_SourceRequestId"
        FOREIGN KEY ("SourceRequestId") REFERENCES "Requests"("Id") ON DELETE RESTRICT
);

CREATE INDEX "IX_VacationSchedules_UserId" ON "VacationSchedules"("UserId");
CREATE INDEX "IX_VacationSchedules_Status_StartDate" ON "VacationSchedules"("Status", "StartDate");
CREATE INDEX "IX_VacationSchedules_StartDate_EndDate" ON "VacationSchedules"("StartDate", "EndDate");

-- Create OrganizationalPermissions table
CREATE TABLE "OrganizationalPermissions" (
    "Id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "UserId" UUID NOT NULL UNIQUE,
    "CanViewAllDepartments" BOOLEAN NOT NULL DEFAULT FALSE,
    "VisibleDepartmentIds" JSONB NOT NULL DEFAULT '[]',
    "CreatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt" TIMESTAMP NULL,
    CONSTRAINT "FK_OrganizationalPermissions_Users_UserId"
        FOREIGN KEY ("UserId") REFERENCES "Users"("Id") ON DELETE CASCADE
);

CREATE INDEX "IX_OrganizationalPermissions_UserId" ON "OrganizationalPermissions"("UserId");

-- Enhance RequestApprovalStepTemplates
ALTER TABLE "RequestApprovalStepTemplates"
ADD COLUMN "SpecificDepartmentId" UUID NULL,
ADD CONSTRAINT "FK_RequestApprovalStepTemplates_Departments_SpecificDepartmentId"
    FOREIGN KEY ("SpecificDepartmentId") REFERENCES "Departments"("Id") ON DELETE SET NULL;

-- Update RequestTemplate
ALTER TABLE "RequestTemplates"
ADD COLUMN "RequiresSubstituteSelection" BOOLEAN NOT NULL DEFAULT FALSE;
```

## API Endpoints

### Departments
- `GET /api/departments` - Get all departments (tree structure)
- `GET /api/departments/{id}` - Get department details
- `POST /api/departments` - Create department (Admin only)
- `PUT /api/departments/{id}` - Update department (Admin only)
- `DELETE /api/departments/{id}` - Delete department (Admin only)
- `GET /api/departments/{id}/employees` - Get department employees

### Vacation Schedules
- `GET /api/vacation-schedules/team` - Get team vacation calendar
- `GET /api/vacation-schedules/my-substitutions` - Get my active substitutions
- `GET /api/vacation-schedules/export/pdf` - Export calendar to PDF
- `GET /api/vacation-schedules/export/excel` - Export calendar to Excel

### Organizational Permissions
- `GET /api/permissions/organizational/{userId}` - Get user's org permissions
- `PUT /api/permissions/organizational/{userId}` - Update org permissions (Admin only)

## Success Metrics

1. **Organizational Structure**: Support unlimited hierarchy depth
2. **Vacation Coverage**: 100% of vacation requests specify substitute
3. **Conflict Detection**: Alert managers when >30% team on vacation
4. **Request Routing**: 95%+ accuracy in automatic approver assignment
5. **Auto-Approval**: Logged audit trail for all auto-approved requests
6. **User Satisfaction**: 90%+ satisfaction with vacation calendar UI

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data migration fails (Department string→entity) | High | Low | Thorough testing, rollback plan, keep old field temporarily |
| Performance issues with deep hierarchies | Medium | Medium | Add caching, optimize queries, limit practical depth to 10 levels |
| Conflict detection false positives | Low | Medium | Make threshold configurable, allow manual override |
| Substitute not available when needed | Medium | Low | Validate substitute is active user, not on vacation themselves |

## Future Enhancements (Post-MVP)

1. **Active Directory Integration**: Auto-sync org structure from AD/LDAP
2. **Delegation System**: Manual delegation of approvals (separate from vacation)
3. **Escalation**: Auto-escalate if approval overdue
4. **Parallel Approval**: Multiple people must approve simultaneously
5. **Conditional Routing**: Route based on form data (e.g., amount > $10k → CFO)
6. **Mobile App**: Native mobile app for approvals
7. **Analytics**: Dashboard showing approval metrics, bottlenecks

## References

- **Organizational Design**: Galbraith Star Model
- **Vacation Planning**: HR best practices (30% threshold)
- **Approval Workflows**: Jira Service Management, ServiceNow
- **Calendar UI**: Google Calendar, Outlook Calendar
- **Export Libraries**: QuestPDF, EPPlus

## Appendices

### Appendix A: Example Org Structure

```
PortalForge Inc.
├── Board of Directors (BoardMember)
│   └── Jan Kowalski (President)
│       ├── Anna Nowak (VicePresident - Operations)
│       │   ├── Piotr Wiśniewski (Director - IT)
│       │   │   ├── Maria Kowalczyk (Manager - Development)
│       │   │   │   ├── Tomasz Lewandowski (TeamLeader - Backend)
│       │   │   │   │   ├── Krzysztof Wójcik (Employee - Senior Dev)
│       │   │   │   │   └── Magdalena Kamińska (Employee - Junior Dev)
│       │   │   │   └── Ewa Zielińska (TeamLeader - Frontend)
│       │   │   │       └── ... employees
│       │   │   └── Jacek Szymański (Manager - Infrastructure)
│       │   │       └── ... teams
│       │   └── Katarzyna Dąbrowska (Director - HR)
│       │       └── ... departments
│       └── Michał Kozłowski (VicePresident - Finance)
│           └── ... departments
```

### Appendix B: Vacation Calendar Mockup

See: `.ai/diagrams/vacation-calendar-mockup.md`

### Appendix C: Request Routing Decision Tree

```
Request Submitted
├─ Step 1: Find Approver
│   ├─ ApproverType.DirectSupervisor → Use submitter.Supervisor
│   ├─ ApproverType.Role → Walk up supervisor chain to find role
│   ├─ ApproverType.SpecificUser → Use specified user
│   ├─ ApproverType.SpecificDepartment → Use department.HeadOfDepartment
│   └─ ApproverType.UserGroup → Pick first available from group
│
├─ Step 2: Check if approver found
│   ├─ Yes → Continue
│   └─ No → Auto-approve (no higher supervisor)
│
├─ Step 3: Check if approver on vacation
│   ├─ Yes → Use substitute from VacationSchedule
│   └─ No → Use original approver
│
└─ Step 4: Create approval step
    └─ Send notification to approver
```
