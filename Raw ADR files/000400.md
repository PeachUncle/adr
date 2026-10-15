# ADR 005: MVP Budget Simplifications & Missing Features

**Date**: 2025-12-15  
**Status**: Accepted  
**Deciders**: Project Team  
**Context Tags**: #budget #mvp #technical-debt

---

## Context

During Phase 5.5 (Budget Creation), we implemented a simplified budget system to meet MVP timeline constraints (3 hours). The original design documented in `data-model.md` included:

- Custom budget periods (pay period support: 20th-19th)
- Month/year navigation
- Budget status workflow (draft → active → closed)
- Actual income/expense tracking
- Category management (add/edit/delete custom categories)
- Copy previous month functionality

**What we actually built**:
- Current calendar month ONLY (no navigation)
- Hardcoded DEFAULT_BUDGET_CATEGORIES (20+ categories)
- No custom categories
- No pay period support
- Simplified Budget entity (removed status, period_start/end, actual tracking)

---

## Decision

**We accept these simplifications for Phase 5.5 MVP**, but **MUST address before production**:

### **Critical** (Blocks real usage):
1. **Month/Year Selector** - Users need to view past months and plan future months
2. **Category Management** - Users must be able to add/edit/delete categories
3. **Actual Tracking** - Budget must show actual vs planned (requires transaction integration)

### **High Priority** (Poor UX without):
4. **Pay Period Support** - Many users paid mid-month (20th) need custom budget periods
5. **Copy Previous Month** - Re-entering budget every month is tedious
6. **Budget Status** - Draft/Active/Closed workflow for month-end closing

### **Medium Priority** (Nice to have):
7. **Category Groups Customization** - Allow users to create custom groups
8. **Budget Templates** - Save/reuse category sets

---

## Consequences

### **Positive**:
- ✅ Delivered working zero-based budget in 3 hours
- ✅ Core envelope logic validated
- ✅ Foundation for full budget system in place

### **Negative**:
- ❌ Users stuck on current month
- ❌ Cannot customize categories (everyone uses Dave Ramsey defaults)
- ❌ Calendar month only (doesn't match pay cycles)
- ❌ Cannot track actual spending (budget is "planned only")
- ❌ Tedious to recreate budget monthly

### **Technical Debt**:
- Budget entity needs refactoring to match original design
- Firestore schema change required (add period_start/end, status)
- UI needs month navigation component
- Category management screens needed (3-4 new screens)
- FirestoreBudgetRepository methods incomplete

---

## Implementation Plan

### **Phase 5.5.1: Month Navigation** (1 hour)
- Add month/year selector to budget screen
- Implement "Previous/Next Month" buttons
- Load budget for selected month (or create if doesn't exist)
- Update FirestoreBudgetRepository.getBudgetByMonth()

### **Phase 5.5.2: Category Management** (2 hours)
- Create "Manage Categories" screen
- Add/Edit/Delete custom categories
- Persist to Firestore `master_categories` collection
- Link to household for customization

### **Phase 5.5.3: Pay Period Support** (1.5 hours)
- Add `budget_period_start_day` to Household entity (default: 1)
- Calculate period_start/period_end based on start day
- Update Budget entity with period_start/period_end Timestamps
- UI: Allow household to set "Budget starts on day X of month"

### **Phase 5.5.4: Actual Tracking** (handled in Phase 5.6)
- Transaction entry updates BudgetCategory.actual_amount
- Budget screen shows Planned vs Actual
- Progress bars reflect actual spending

### **Phase 5.5.5: Copy Previous Month** (30 min)
- Implement copyBudgetToNextMonth() (already exists in repository)
- Add "Copy Last Month" button to budget screen
- Copy categories with planned amounts, reset actuals to 0

### **Phase 5.5.6: Budget Status Workflow** (1 hour)
- Add status: 'draft' | 'active' | 'closed' to Budget entity
- "Close Month" button (locks editing, useful for historical record)
- Only one active budget per period

---

## Alternatives Considered

### **Alternative 1: Build Full Budget System in Phase 5.5**
- **Pro**: No technical debt, complete from day 1
- **Con**: Would take 8-10 hours, not 3 hours
- **Rejected**: Breaks incremental development philosophy

### **Alternative 2: Skip Budgets Entirely in MVP**
- **Pro**: Focus on transactions only
- **Con**: Budgets are core to Dave Ramsey system - not optional
- **Rejected**: Budgets are "Must Have" feature

### **Alternative 3: Calendar Month Only (No Pay Period Support)**
- **Pro**: Simpler, matches most budgeting apps
- **Con**: Doesn't match how many people are paid (15th, 20th, etc.)
- **Status**: Open question - defer to user feedback?

---

## References

- Original design: `docs/architecture/data-model.md` lines 191-257
- User feedback: "I get paid on the 20th so my month runs from the 20th-19th"
- Dave Ramsey EveryDollar app supports custom budget periods
- Related: Phase 5.6 (Transactions) will need actual amount tracking

---

## Notes

**Critical User Feedback** (2025-12-15):
> "We cannot move to transactions. Budgets are monthly and we cannot select the month. Neither is budget linked to dates ie I get paid on the 20th so my month runs from the 20th - 19th of the next month. There is nowhere we can manage categories or category groups."

This confirms our simplifications went too far. User is correct.

**Next Steps**:
1. Document this ADR ✅
2. Update docs/project/project-status.md to break out Phase 5.5.1-5.5.6
3. Decide: Fix now or after Phase 5.6 (Transactions)?

**Recommendation**: Fix **Critical** items (5.5.1, 5.5.2) BEFORE Phase 5.6, defer rest.

