# Design: Screenset-Owned API Services

## Context

HAI3 follows vertical slice architecture where screensets are self-contained domains. Currently, API services break this pattern by being centralized in `src/api/services/`. This creates implicit coupling between screensets that share API domains.

The current pattern assumes API services are reusable infrastructure, but in practice:
- Each screenset typically needs domain-specific API methods
- Shared API services create coordination overhead between teams
- Changes to shared services require careful impact analysis
- Testing becomes more complex with shared dependencies

## Goals / Non-Goals

**Goals:**
- Complete screenset isolation - each screenset owns all its code
- Enable independent development - no shared API service coordination
- Simplify reasoning - all screenset code lives in one directory
- Accept intentional duplication as a feature, not a bug

**Non-Goals:**
- Eliminate all duplication (duplication is intentional)
- Create abstraction layers to share API logic
- Maintain backward compatibility with centralized API pattern
- Preserve existing `src/api/` structure

## Decisions

### Decision 1: Screenset-Local API Services

**What:** Each screenset defines its API services in `src/screensets/<screenset>/api/`

**Why:**
- Enables true vertical slice architecture
- Developers can modify API services without coordinating with other teams
- Clear ownership boundaries
- Easier to understand screenset's full domain

**Structure:**
```
src/screensets/chat/
├── api/
│   ├── ChatApiService.ts    # Service class + self-registration
│   ├── api.ts                # TypeScript types/interfaces
│   └── mocks.ts              # Mock data for development
├── actions/
├── screens/
├── slices/
└── chatScreenset.tsx
```

**Alternatives considered:**
- Keep centralized API: Rejected - Creates coupling and coordination overhead
- Shared API packages: Rejected - Adds complexity without solving isolation problem
- Copy-on-write shared services: Rejected - Still requires coordination for "shared" baseline

### Decision 2: Accept Intentional Duplication

**What:** If two screensets need similar API functionality, they duplicate the implementation

**Why:**
- Independence > DRY principle in vertical slice architecture
- Each screenset can evolve its API needs independently
- Duplication makes dependencies explicit (copy-paste over abstraction)
- Easier to delete entire screensets without refactoring shared code

**Example:**
- `chat` screenset has `ChatApiService` with thread management
- `chat-copy` screenset copies `ChatApiService` and can modify independently
- Both screensets evolve separately without breaking each other

**Alternatives considered:**
- Extract shared logic to utilities: Rejected - Creates hidden coupling
- Use inheritance: Rejected - Tight coupling through class hierarchies
- Micro-frontends with shared SDKs: Rejected - Over-engineering for current scale

### Decision 3: Self-Registration Pattern Preserved

**What:** API services continue to self-register with `apiRegistry` at module import

**Why:**
- Preserves existing registry pattern used throughout HAI3
- No changes needed to `@hai3/uicore` API registry
- Screensets already use self-registration for other concerns

**How:**
```typescript
// src/screensets/chat/api/ChatApiService.ts
export const CHAT_DOMAIN = 'chat' as const;

export class ChatApiService extends BaseApiService {
  // ... implementation
}

// Self-register (happens at module import)
apiRegistry.register(CHAT_DOMAIN, ChatApiService);

// Type augmentation
declare module '@hai3/uicore' {
  interface ApiServicesMap {
    [CHAT_DOMAIN]: ChatApiService;
  }
}
```

**Alternatives considered:**
- Explicit registration in screenset config: Rejected - More boilerplate, less automatic
- Remove apiRegistry entirely: Rejected - Breaks consistent pattern with other registries

### Decision 4: Import API Services in Screenset Root

**What:** Screenset root file imports API service to trigger self-registration

**Why:**
- Ensures API services are registered when screenset loads
- Consistent with current pattern for screenset initialization
- Makes dependencies explicit

**Example:**
```typescript
// src/screensets/chat/chatScreenset.tsx
import './api/ChatApiService'; // Trigger self-registration
import './slices/chatSlice';   // Trigger slice registration

export const chatScreenset: ScreensetConfig = {
  // ... config
};

screensetRegistry.register(chatScreenset);
```

**Alternatives considered:**
- Lazy load API services: Rejected - Adds complexity and initialization race conditions
- Automatic discovery: Rejected - Implicit magic, harder to understand

### Decision 5: Framework Services vs Screenset Extensions

**What:** Framework services (e.g., AccountsApiService) remain in uicore package, but their mocks and module augmentations move to screensets

**Why:**
- Framework services are used by framework code (Layout, Header, etc.)
- But mocks and extensions are app-specific and should be owned by screensets
- Each screenset controls what mock data and extra fields it needs
- Maintains clean separation: framework infrastructure vs. app customization

**Structure:**
```typescript
// Framework service (stays in uicore)
packages/uicore/src/api/services/accounts/AccountsApiService.ts

// Screenset extensions (move to demo screenset)
src/screensets/demo/api/accounts/extra.ts    # Module augmentation
src/screensets/demo/api/accounts/mocks.ts    # Mock data
```

**Screenset registration:**
```typescript
// src/screensets/demo/demoScreenset.tsx
import './api/accounts/extra';
import { accountsMockMap } from './api/accounts/mocks';

apiRegistry.registerMocks(ACCOUNTS_DOMAIN, accountsMockMap);
```

**Alternatives considered:**
- Move framework services to screensets: Rejected - Framework needs these services
- Keep mocks centralized in `src/core/api/`: Rejected - Breaks vertical slice independence

### Decision 6: Remove All Centralized API Directories

**What:** Delete `src/api/apiRegistry.ts`, entire `src/api/` directory, and `src/core/api/` directory

**Why:**
- No longer needed with screenset-owned services and extensions
- Eliminates central coordination points
- Forces proper vertical slice organization

**Migration:**
- Move each service to its corresponding screenset
- Move framework service mocks/extras to screensets that use them
- Copy duplicates where multiple screensets use same domain
- Update imports in screenset action files

**Alternatives considered:**
- Keep for backward compatibility: Rejected - Maintains old pattern, confuses architecture
- Deprecate gradually: Rejected - Mixed patterns during transition period

## Risks / Trade-offs

### Risk: Code Duplication

**Mitigation:** Accept as intentional feature. Duplication enables independence, which is the primary goal. When duplication becomes excessive, it signals a need to extract a proper shared package, not centralize in `src/api/`.

### Risk: Inconsistent API Implementations

**Mitigation:** Each screenset owns its quality. If consistency is needed across screensets, extract to a workspace package (e.g., `@hai3/api-sdk`), not to `src/api/`.

### Risk: Breaking Changes During Migration

**Mitigation:** This is a breaking change. Complete migration in single PR:
1. Copy services to screensets
2. Update all imports
3. Delete `src/api/`
4. Validate with `npm run arch:check`

### Risk: Larger Bundle Size

**Impact:** Minimal - API services are small, and Vite tree-shaking will remove unused code. Duplication is at source level, not bundle level.

## Migration Plan

### Phase 1: Preparation (30 min)
1. Identify which screensets use which API services via `rg "apiRegistry.getService"`
2. Create migration mapping:
   - `CHAT_DOMAIN` → `chat` screenset
   - `CHAT_DOMAIN` → `chat-copy` screenset (duplicate)

### Phase 2: Copy Services (1 hour)
1. For each screenset:
   ```bash
   mkdir -p src/screensets/<screenset>/api
   cp -r src/api/services/<domain>/* src/screensets/<screenset>/api/
   ```
2. Update imports in copied files to use relative paths
3. Add import in screenset root: `import './api/<Service>ApiService'`

### Phase 3: Update Consumers (1 hour)
1. Update action files to import types from local `api/` directory
2. Verify `apiRegistry.getService(DOMAIN)` calls still work (registry is in uicore)
3. Run type-check: `npm run type-check`

### Phase 4: Delete Centralized API (15 min)
1. Delete `src/api/` directory
2. Remove import from `src/main.tsx`
3. Run `npm run arch:check` to validate

### Phase 5: Update Documentation (30 min)
1. Update `.ai/GUIDELINES.md` routing table
2. Update or remove `.ai/targets/API.md`
3. Update `.ai/targets/SCREENSETS.md` with API service rules
4. Update `CLAUDE.md` architecture section
5. Update `openspec/project.md`

### Rollback Plan
If issues arise:
1. Restore `src/api/` from git
2. Remove screenset `api/` directories
3. Restore original imports
4. Run `npm run build` to verify

## Open Questions

**Q: Should we create an `@hai3/api-sdk` package for truly shared API utilities?**
A: Not in this change. If shared utilities are needed later, address in separate proposal.

**Q: How do we handle API service changes that affect multiple screensets?**
A: Each screenset updates independently. This is intentional - forces explicit coordination rather than hidden coupling.

**Q: Should mock data also be duplicated?**
A: Yes, mock data is part of the API service domain and should be colocated with the service.
