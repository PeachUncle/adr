---
status: accepted
date: 2025-08-28
decision-makers:
  - voder-dev-team
consulted:
  - eslint-plugin-simple-import-sort maintainers
informed:
  - configuration consumers
---

# ADR-0008: Use simple-import-sort for import ordering

## Context and Problem Statement

Our ESLint configuration exports include conflicting import ordering rules that create circular fixes and break auto-fixing for consumers. Both `eslint-plugin-import`'s `import/order` rule and `eslint-plugin-simple-import-sort`'s import sorting rules attempt to control import statement ordering but use incompatible approaches, leading to unstable development workflows.

The simple-import-sort documentation explicitly states: "Make sure not to use other sorting rules at the same time: sort-imports, import/order."

## Decision Drivers

- Eliminate circular auto-fix conflicts that break ESLint workflows
- Provide reliable import sorting for all configuration consumers
- Follow plugin maintainer recommendations for rule compatibility
- Maintain zero-configuration developer experience
- Ensure consistent import ordering across all projects

## Considered Options

1. Keep `import/order` and remove `simple-import-sort/imports`
2. Keep `simple-import-sort/imports` and remove `import/order` (chosen)
3. Attempt to configure both rules to be compatible
4. Disable both rules and rely on Prettier for import formatting

## Decision Outcome

Chosen option: "Keep `simple-import-sort/imports` and remove `import/order`", because it follows the plugin maintainer's explicit compatibility guidance, provides zero-configuration automatic sorting, and eliminates circular fix conflicts while maintaining reliable auto-fix functionality.

### Consequences

- Good, because eliminates circular fixes warnings and enables reliable auto-fix workflows
- Good, because provides zero-configuration import sorting for all consumers
- Good, because follows official plugin compatibility recommendations
- Good, because better integration with modern TypeScript patterns and type-only imports
- Bad, because loss of manual grouping control (external vs internal imports)
- Bad, because different sorting algorithm may require re-formatting codebases

### Confirmation

Implementation compliance confirmed by:

- ✅ `import/order` rule removed from `eslint/base.ts`
- ✅ `simple-import-sort/imports` and `simple-import-sort/exports` active in `eslint/dx.ts`
- ✅ `npm run lint:check` passes without circular fixes warnings
- ✅ `npm run lint:fix` reliably auto-fixes import ordering without conflicts
- ✅ No ESLint disable comments needed for import ordering issues
- ✅ All test files can be auto-fixed consistently

## Pros and Cons of the Options

### Keep `import/order` and remove `simple-import-sort/imports`

Provides manual control over import grouping with explicit separation between dependency types.

- Good, because allows explicit grouping (external → internal → parent → sibling)
- Good, because more configurable for complex import organization needs
- Neutral, because widely adopted in JavaScript/TypeScript projects
- Bad, because requires manual configuration and maintenance
- Bad, because less automation-friendly for zero-config goals

### Keep `simple-import-sort/imports` and remove `import/order`

Provides automatic zero-configuration import sorting following a consistent algorithm.

- Good, because zero-configuration automatic sorting
- Good, because eliminates circular fix conflicts
- Good, because better TypeScript and modern ES module support
- Good, because follows plugin maintainer compatibility guidance
- Good, because integrates seamlessly with auto-fix workflows
- Neutral, because widely adopted for TypeScript projects
- Bad, because less control over import grouping

### Attempt to configure both rules to be compatible

Try to configure rules to avoid conflicts while keeping both active.

- Neutral, because could theoretically provide benefits of both approaches
- Bad, because explicitly discouraged by plugin maintainers
- Bad, because high complexity with uncertain outcomes
- Bad, because would require ongoing maintenance as plugins evolve

### Disable both rules and rely on Prettier for import formatting

Remove import ordering rules entirely and use Prettier for formatting.

- Good, because eliminates all rule conflicts
- Bad, because Prettier doesn't handle import ordering (only formatting)
- Bad, because loses import organization benefits entirely
- Bad, because doesn't meet developer experience goals for automatic organization

## More Information

Implementation completed by removing `import/order` rule from `eslint/base.ts` while keeping `simple-import-sort/imports` and `simple-import-sort/exports` in `eslint/dx.ts`. This follows the explicit guidance from simple-import-sort maintainers that these rules should not be used simultaneously.

The decision aligns with the package's developer experience goals by providing automatic, zero-configuration import sorting that integrates seamlessly with ESLint auto-fix workflows.
