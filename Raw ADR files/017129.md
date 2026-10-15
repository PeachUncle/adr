# ADR-0002: Role Folder Guidelines

**Status:** Accepted  
**Date:** 2025-05-15

## Context

This repository supports skill assessment scenarios for multiple roles (e.g., Product Owner, Enterprise Architect).  
As role-specific content increased, it became necessary to define a clear folder structure and file-naming convention to:

- Separate role-specific content from shared assets
- Improve maintainability and discoverability
- Support the addition of more roles in a consistent way

## Decision

Each role is assigned a dedicated folder under `roles/`:

```
roles/
├── po/
│   ├── README.md
│   ├── scenario.md
│   ├── evaluation_criteria.md
│   ├── collaborative_team.md
│   ├── prompt_intro.md
│   └── prompt_reflection.md
├── ea/
│   └── (To be added)
```

### Guidelines:

1. **Folder Name**  
   Use lowercase role identifiers (e.g., `po`, `ea`).

2. **README.md**  
   Contains an overview of the role and links to key files.

3. **Scenarios and Evaluation**  
   - `scenario.md`: Role-specific situations used in the roleplay  
   - `evaluation_criteria.md`: Assessment points and expectations

4. **Prompts (ChatGPT instruction)**  
   - All ChatGPT-targeted prompt files are named `prompt_{phase}.md`  
     Example: `prompt_intro.md`, `prompt_reflection.md`
   - These files guide how ChatGPT should behave in specific phases of the session

5. **Character & Team Context**  
   - `collaborative_team.md`: Provides character profiles or team dynamics for roleplay

## Consequences

- Easier to extend the repository with new roles (e.g., `roles/devlead/`, `roles/ba/`)
- ChatGPT can load role-specific prompts without confusion
- Developers can quickly identify whether a file is human-facing (`README.md`) or ChatGPT-facing (`prompt_*.md`)
- Promotes consistency between roles while allowing flexibility in content

## Future Considerations

- If prompts for a phase become mostly shared across roles, we may move them to `shared/` and override only if needed
- If we need complex team settings, consider a `teams/` shared directory
