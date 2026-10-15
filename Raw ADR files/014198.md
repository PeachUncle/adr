# ADR 0002: Use Angular Standalone Components

**Status**: Accepted

**Date**: 2025-11-08 (Documented retroactively)

**Deciders**: AI Agent (following Angular best practices)

## Context

Angular 20.3 supports two component architectures:
1. NgModule-based (traditional)
2. Standalone components (modern)

Both applications needed a clear architectural pattern for component organization.

## Decision

Use **Angular Standalone Components** exclusively throughout the workspace.

## Rationale

### Chosen: Standalone Components

**Advantages**:
- ✅ **Simpler Mental Model**: No need to manage NgModules
- ✅ **Reduced Boilerplate**: Components declare their own dependencies
- ✅ **Better Tree-Shaking**: Unused components automatically excluded from bundle
- ✅ **Future-Proof**: Angular's recommended approach going forward
- ✅ **Easier Testing**: Components fully self-contained
- ✅ **Modern inject()**: Use `inject()` function instead of constructor DI

**Disadvantages**:
- ⚠️ Must explicitly import CommonModule and other dependencies
- ⚠️ Breaking change if migrating from NgModule apps

### Rejected: NgModule-Based Components

**Why Rejected**:
- Legacy pattern being phased out by Angular team
- More boilerplate with module declarations
- Harder to understand component dependencies
- Not the default in Angular 20.3

## Consequences

### Positive

**Cleaner Component Definitions**:
```typescript
@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  private service = inject(MyService); // Modern inject()
}
```

**No AppModule Management**:
- No need to maintain module import lists
- Components declare exactly what they need

**Better Code Organization**:
- Each component is truly independent
- Easier to move components between apps

### Negative

**Verbose Imports**: Must explicitly import even common modules
```typescript
imports: [CommonModule, FormsModule, RouterModule]
```

### Neutral

**Learning Curve**: Developers familiar with NgModules need to adjust

## Implementation

**All Components Follow Pattern**:
```typescript
@Component({
  standalone: true,
  imports: [/* explicit imports */],
  // ...
})
```

**Bootstrap in main.ts**:
```typescript
bootstrapApplication(AppComponent, appConfig);
```

**Examples in Codebase**:
- `apps/reward-chart/src/app/components/header/header.component.ts`
- `apps/family-calendar/src/app/components/calendar/calendar.component.ts`

## Follow-up

- ✅ All components use standalone pattern
- ✅ Nx generators configured to create standalone components by default
- 🔮 Future: Consider creating shared standalone component library

## References

- [Angular Standalone Components Guide](https://angular.dev/guide/components/importing)
- [Migration from NgModules](https://angular.dev/guide/ngmodules/migration)
- Configured in `nx.json`: `generators.@nx/angular:component.standalone: true`
