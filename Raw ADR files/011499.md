## Context

MeldUI needs a date selection component that combines quick preset selections with full calendar functionality. This is a common pattern in analytics dashboards, reporting tools, and filtering interfaces. The existing `Calendar` and `RangeCalendar` components provide the base functionality but lack preset support and popover integration.

**Stakeholders:** Internal application developers using MeldUI for dashboards and data-heavy applications.

## Goals / Non-Goals

**Goals:**
- Provide a full-featured date picker with preset quick selections
- Support both single date and date range selection modes
- Allow customizable presets via props
- Provide sensible defaults that work out of the box
- Maintain consistency with existing MeldUI component patterns
- Support accessibility (keyboard navigation, ARIA)

**Non-Goals:**
- Time picker functionality (date only)
- Multi-calendar views (e.g., showing 3 months at once) - can use `numberOfMonths` prop
- Date/time zone conversion utilities

## Decisions

### Component Structure

**Decision:** Create a composite component that composes existing primitives.

The component will be structured as:
```
DateRangePicker (main entry)
├── DateRangePickerTrigger (button that opens popover)
├── DateRangePickerContent (popover content)
│   ├── DateRangePickerPresets (left panel with preset buttons)
│   └── DateRangePickerCalendar (right panel with calendar)
```

**Rationale:** This follows the existing composite pattern (e.g., MultiSelect) and allows flexibility for consumers who want to customize parts of the component.

### Preset Configuration

**Decision:** Presets use static functions that return date values.

```typescript
interface DatePreset {
  label: string
  value: () => DateValue  // for single mode
}

interface DateRangePreset {
  label: string
  value: () => { start: DateValue; end: DateValue }  // for range mode
}
```

**Rationale:** Static functions allow presets to calculate relative dates at selection time (e.g., "Today" always returns current date). This is more flexible than storing config like `{ days: -7 }` which requires interpretation logic.

**Alternatives considered:**
- Relative config objects: More declarative but less flexible for complex calculations
- String identifiers with built-in logic: Less customizable

### Built-in Default Presets

**Decision:** Provide separate defaults for single and range modes.

**Single mode defaults:**
- Today
- Yesterday
- 1 week ago
- 1 month ago

**Range mode defaults:**
- Today
- Yesterday
- Last 7 days
- Last 30 days
- This month
- Last month

**Rationale:** These cover common use cases in analytics and reporting. Users can override with custom presets.

### Selection Behavior

**Decision:** Provide `closeOnPresetSelect` prop (default: `true`).

**Rationale:** Auto-close is the expected behavior for quick selections, but some use cases may want the picker to stay open for comparison or verification.

### Calendar Visibility

**Decision:** Provide `showCalendar` prop (default: `true`).

When `false`, only the presets panel is shown. This is useful for simple use cases where users only need preset options.

### Mode Prop

**Decision:** Use a `mode` prop with values `'single'` | `'range'`.

```typescript
interface DateRangePickerProps {
  mode?: 'single' | 'range'  // default: 'range'
  // ... other props
}
```

**Rationale:** Explicit mode selection is clearer than inferring from v-model type.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Preset date calculations may differ from user expectations (timezone, locale) | Use `@internationalized/date` consistently, document timezone behavior |
| Large API surface with many props | Keep defaults sensible, provide good documentation |
| Performance with many presets | Presets are rendered once, not a concern |

## Component API

```typescript
interface DateRangePickerProps {
  // Core
  mode?: 'single' | 'range'
  modelValue?: DateValue | DateRange | undefined
  defaultValue?: DateValue | DateRange

  // Presets
  presets?: DatePreset[] | DateRangePreset[]
  showCalendar?: boolean
  closeOnPresetSelect?: boolean

  // Calendar props (passed to underlying Calendar/RangeCalendar)
  locale?: string
  minValue?: DateValue
  maxValue?: DateValue
  disabled?: boolean
  readonly?: boolean
  numberOfMonths?: number

  // Display
  placeholder?: string
  dateFormat?: string  // format for displaying selected date(s)
  class?: string
}

interface DateRangePickerEmits {
  'update:modelValue': [value: DateValue | DateRange | undefined]
  'preset-select': [preset: DatePreset | DateRangePreset]
}
```

## File Structure

```
packages/vue/src/composites/date-range-picker/
├── DateRangePicker.vue          # Main component
├── DateRangePickerTrigger.vue   # Trigger button
├── DateRangePickerContent.vue   # Popover content wrapper
├── DateRangePickerPresets.vue   # Presets panel
├── DateRangePickerCalendar.vue  # Calendar wrapper
├── presets.ts                   # Default presets and types
├── types.ts                     # TypeScript interfaces
└── index.ts                     # Exports
```

## Open Questions

- None currently - all major decisions resolved through clarification.
