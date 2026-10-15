# ADR-20251015-use-excel-like-navigation

## Status
Accepted

## Context
ExvoRed is used by academic researchers for data entry and cataloging workflows involving hundreds of exvotos, SEMs, and catalogs. User research revealed that the target audience consists primarily of humanities researchers familiar with spreadsheet applications like Microsoft Excel and Google Sheets, where they currently manage preliminary catalog data. The cataloging workflow involves repetitive data entry tasks: reviewing exvoto images, transcribing text, filling standardized fields, and cross-referencing with existing records.

Users expressed frustration with traditional CRUD interfaces that require multiple clicks to navigate between records, open edit modals, and save changes. The workflow requires frequent navigation between related records (e.g., viewing an exvoto, inspecting its offering SEM, checking the associated divinity, returning to the exvoto). Keyboard efficiency is critical for productivity; users want to minimize mouse usage during data entry sessions. The application must support both inline editing (quick field updates) and full-record editing (comprehensive data entry).

## Decision
Implement Excel-like keyboard navigation throughout all entity tables using custom React hooks: `useExcelMode` (state management for selected cell, visible columns, sorting) and `useExcelKeyboard` (arrow key navigation, Enter to edit, Escape to cancel). Arrow keys (↑ ↓ ← →) move selection between cells, Tab navigates fields within edit mode, Enter activates inline editing, and Escape cancels changes. Single-click selects a cell, double-click opens edit mode, and keyboard shortcuts (e for edit, i for inspect) provide additional navigation options.

## Consequences

### Positive
- Keyboard efficiency: Users can navigate entire tables, edit fields, and save changes without touching the mouse; reduces time per record from 2+ minutes to under 1 minute
- Familiar UX: Researchers already know Excel keybindings; no training required for basic navigation
- Reduced cognitive load: Consistent navigation model across all entity pages (exvotos, SEMs, catalogs, divinities)
- Inline editing speed: No modal open/close overhead for single-field edits; Tab to next field and Enter to save
- Column management: Users can hide irrelevant columns, reorder columns by workflow, and resize columns to fit their screen, improving focus and readability
- Horizontal scrolling: Tables can display 20+ columns without cramming; users scroll right to access additional fields

### Negative
- Custom implementation complexity: Building Excel-like navigation from scratch requires custom hooks (`useExcelMode`, `useExcelKeyboard`) and extensive state management; no off-the-shelf library
- Learning curve for non-Excel users: Users unfamiliar with spreadsheet navigation may struggle initially; requires documentation (KeybindsPage.tsx)
- Accessibility challenges: Arrow key navigation conflicts with screen reader navigation patterns; keyboard-only users without screen readers benefit, but screen reader users may struggle
- Modal interaction conflicts: Arrow keys should not navigate when modals are open; requires careful focus management and event handler guards
- Browser compatibility: Arrow key event handling differs slightly between browsers; requires cross-browser testing
- Mobile/touch unsupported: Excel-like navigation is keyboard-focused; mobile users must rely on touch interactions without keyboard shortcuts

### Neutral
- Hybrid approach required: Excel mode handles table navigation, but detail pages still use traditional forms for complex multi-field editing
- State management overhead: Tracking selected cell, editing cell, visible columns, and sort order adds complexity to React components

## Alternatives Considered

### Alternative 1: Standard CRUD Forms Only
**Rejected because:** Traditional CRUD forms require multiple clicks per operation: click Edit button, wait for modal to open, click field, edit, click Save, wait for modal to close. For bulk data entry (cataloging 50 exvotos in a session), this workflow is too slow. Users would spend 60+ seconds per record instead of the target 30-45 seconds with Excel mode. Standard forms also require switching between mouse and keyboard constantly, breaking flow state. User feedback explicitly requested "Excel-like" interaction for efficiency.

### Alternative 2: Editable Grid Library (ag-Grid, Handsontable)
**Rejected because:** ag-Grid Community Edition lacks features like column reordering and advanced filtering; ag-Grid Enterprise costs $999+/year, prohibitive for academic projects. Handsontable has similar licensing costs and a 100KB+ bundle size impact. Both libraries are over-engineered for ExvoRed's needs, including features like pivot tables, charting, and Excel export that are not required. Customizing these libraries to match ExvoRed's specific navigation patterns (e.g., "i" key for inspect) would require fighting against their built-in keybindings. Building custom hooks provides exactly the features needed with zero licensing costs and minimal bundle size impact.

### Alternative 3: Modal-Only Editing (No Inline Editing)
**Rejected because:** Modal-only editing forces users to open a full modal for every field change, even for single-character corrections. This adds 5-10 clicks per edit operation (click row, click Edit button, wait for modal, click field, edit, click Save, wait for modal close). For workflows involving many small edits (e.g., fixing typos in transcriptions), this is unacceptably slow. Users explicitly requested inline editing to match the Excel experience where cells are edited in place with a single Enter keypress.

## References
- useExcelMode hook: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/hooks/useExcelMode.ts`
- useExcelKeyboard hook: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/hooks/useExcelKeyboard.ts`
- DataTable component: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/components/DataTable.tsx`
- Keyboard shortcuts documentation: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/pages/KeybindsPage.tsx`
