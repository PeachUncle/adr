# ADR-0007: Git Hooks Strategy

## Status
Proposed

## Context
To maintain code quality and consistency, we need automated checks that run before commits and pushes. 
Currently, our conventional commit validation only happens in CI, which leads to delayed feedback and 
requires additional commits to fix issues.

We need a solution that:
- Validates commit messages locally before they're pushed
- Can be easily installed by all developers
- Works consistently across different development environments
- Can be version controlled
- Supports additional hooks for future needs

## Decision
We will implement Git hooks using:
1. Husky for Git hooks management
2. commitlint for commit message validation
3. npm scripts for hook installation

### Implementation Details
- Use husky for Git hooks management
- Configure commitlint with conventional commit rules
- Add pre-commit hook for commit message validation
- Add commit-msg hook for detailed message validation
- Include hook installation in project setup
- Document hook bypass procedures for exceptional cases

### Tool Selection
1. **Husky**
   - Industry standard for Git hooks
   - Easy to install and configure
   - Works cross-platform
   - Can be version controlled

2. **commitlint**
   - Supports conventional commit format
   - Configurable rules
   - Good error messages
   - Active maintenance

### Configuration
```js
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-max-line-length': [2, 'always', 100],
    'header-max-length': [2, 'always', 72],
  },
};
```

## Rationale

### Why Husky?
1. Reliable Git hooks management
2. Wide adoption in the community
3. Simple configuration
4. Cross-platform support
5. Version control friendly

### Why Local Validation?
1. Faster feedback loop
2. Reduces CI failures
3. Better developer experience
4. Consistent commit quality
5. Saves time fixing commits

## Consequences

### Positive
- Immediate feedback on commit messages
- Consistent commit history
- Reduced CI failures
- Better documentation through quality commits
- Easier release note generation

### Negative
- Additional setup step for developers
- Potential learning curve for commit conventions
- May slow down commit process initially
- Need to document hook bypass for emergencies

## Compliance
- All commits must follow conventional commit format
- Developers must install Git hooks during setup
- Hook bypass requires documentation
- CI still validates commits as backup
- Hook updates require team notification 