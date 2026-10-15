# ADR-0001: Adopt Base UI as Component Library

**Status:** Accepted
**Date:** 2025-10-22
**Deciders:** Project maintainers

## Context

The super-claude project needs a standard component library for all UI-related skills and code generation. The library must provide:

- Unstyled, accessible component primitives
- WCAG AAA accessibility support
- Composability and customization
- Modern React patterns (hooks, Server Components)
- Strong TypeScript support

The component library choice affects:

- All component generation skills (component-generator, design-system-orchestrator)
- Developer workflows and patterns
- Migration paths for existing code
- Learning curve for skill users

## Decision

**Adopt Base UI (`@base-ui-components/react`) as the primary component library for all component-related work.**

All component generation skills will:

- Use Base UI primitives as the foundation
- Generate components following Base UI patterns
- Provide migration guides from other libraries to Base UI
- Target WCAG AAA accessibility standards

## Alternatives Considered

### Option 1: Radix UI

**Description:**
Popular headless UI component library with mature ecosystem.

**Pros:**

- Larger community and ecosystem
- More mature (longer history)
- Well-documented
- Individual component packages available
- Wide adoption in production apps

**Cons:**

- Requires installing multiple packages (`@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, etc.)
- Less composable architecture (more monolithic components)
- Accessibility is AA, not AAA
- Doesn't align with components.build philosophy

**Decision:** ❌ Rejected

**Rationale:** While mature, Radix UI's multi-package approach and less composable architecture don't align with our goal of simple, consistent patterns. The WCAG AA accessibility level is also below our AAA target.

### Option 2: Base UI

**Description:**
MUI's headless component library, designed for maximum composability and accessibility.

**Pros:**

- Single package installation (`@base-ui-components/react`)
- Highly composable (components.build philosophy)
- WCAG AAA accessibility built-in
- Modern architecture (designed for React 18+)
- Explicit exports (no barrel exports issues)
- Active development by MUI team
- Aligns with unstyled primitives → styled variants pattern

**Cons:**

- Smaller ecosystem than Radix UI (newer)
- Less community content and examples
- Requires more work to create fully-styled components

**Decision:** ✅ Selected

**Rationale:** Base UI's composability, single-package approach, and WCAG AAA accessibility align perfectly with our project goals. The components.build philosophy matches our preference for composable primitives over monolithic components. The smaller ecosystem is acceptable given our focus on code generation.

### Option 3: headless-ui

**Description:**
Tailwind Labs' headless UI component library.

**Pros:**

- Official Tailwind Labs support
- Good TypeScript support
- Clean API design
- Works well with Tailwind CSS

**Cons:**

- Coupled to Tailwind CSS ecosystem
- Limited component set
- Less focus on extreme composability
- Not specifically WCAG AAA focused

**Decision:** ❌ Rejected

**Rationale:** Too tightly coupled to Tailwind CSS (though we use Tailwind, we don't want library coupling). Limited component set and less focus on composability make it less suitable for our code generation goals.

## Consequences

### Positive

- **Consistent patterns**: All component skills generate Base UI-based components
- **Single import**: One package to install, simpler dependency management
- **Better composability**: Easier to create custom components from primitives
- **WCAG AAA**: Meets our accessibility standard out of the box
- **Future-proof**: Modern architecture aligned with React's direction
- **Simpler skills**: Component-generator can focus on one library's patterns

### Negative

- **Smaller ecosystem**: Fewer community examples and patterns to reference
- **Migration overhead**: Need to provide Radix → Base UI migration guides
- **Learning curve**: Users familiar with Radix need to learn Base UI patterns
- **Less mature**: Newer library means potential for breaking changes

### Neutral

- **Documentation burden**: Need to document Base UI patterns in skills
- **Plugin design**: radix-to-baseui-migrator skill needed for migration support
- **Skill maintenance**: Component skills need updating if Base UI changes

## Implementation Notes

**How will this be enforced?**

- component-generator skill generates only Base UI components
- design-system-orchestrator assumes Base UI primitives
- radix-to-baseui-migrator provides migration paths
- Code review guidelines to check for Base UI usage in generated code

**When does this take effect?**

- Immediately for all new component work
- Existing Radix examples should note migration path

**What needs to change to comply?**

- components-plugin skills use Base UI exclusively
- Component generation templates use `@base-ui-components/react`
- Documentation references Base UI patterns and API
- Migration guides document Radix → Base UI conversion

## References

**Related ADRs:**

- ADR-0004: WCAG AAA Accessibility Standard

**OpenSpec Proposals:**

- [components-plugin](../../../openspec/changes/components-plugin/) - Implementation of Base UI component generation

**External Resources:**

- [Base UI Documentation](https://base-ui.com/)
- [components.build Philosophy](https://basecn.dev/)
- [WCAG AAA Guidelines](https://www.w3.org/WAI/WCAG2AAA-Conformance)

## Notes

This decision was made based on:

1. **Project values**: Composability, accessibility, simplicity
2. **Code generation focus**: Easier to generate consistent patterns with one library
3. **Accessibility priority**: WCAG AAA is a hard requirement
4. **Developer experience**: Single package install is simpler than multi-package

If Base UI's development stalls or the library is deprecated, we should revisit this decision. The radix-to-baseui-migrator skill can be reversed to create a baseui-to-radix-migrator if needed.
