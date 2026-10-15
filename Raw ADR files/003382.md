# ADR-006: Unified Portal Design

**Status**: Accepted (Planned, Not Yet Implemented)  
**Date**: 2025  
**Decision Makers**: Development Team  
**Related Documents**: 
- `docs/active-development/UNIFIED_PORTAL_DESIGN.md`
- `docs/active-development/ADMIN_MIGRATION_STRATEGY.md`
- `docs/implementation-roadmap.md`

---

## Context

Protogen currently maintains two separate React applications serving different user roles:

### Current Architecture

```
┌─────────────────┐  ┌─────────────────┐
│     PORTAL      │  │      ADMIN      │
│  (User-Facing)  │  │  (Admin-Facing) │
├─────────────────┤  ├─────────────────┤
│ • Content View  │  │ • Content Mgmt  │
│ • Community     │  │ • Scene Author  │
│ • Navigation    │  │ • Deck Mgmt     │
│ • Feedback      │  │ • User Mgmt     │
└─────────────────┘  └─────────────────┘
        │                     │
        └─────────┬───────────┘
                  │
        ┌─────────────────┐
        │   SHARED LIB    │
        └─────────────────┘
```

### Problems with Dual Applications

1. **Code Duplication**: Similar components implemented twice
2. **Inconsistent UX**: Different navigation and interaction patterns
3. **Maintenance Overhead**: Changes must be applied to both apps
4. **User Confusion**: Switching between apps disrupts workflow
5. **Bundle Redundancy**: Two build pipelines, two deployments
6. **State Fragmentation**: Can't share state between apps
7. **Feature Gaps**: Features available in one but not the other

### Requirements

- Single application serving all user types
- Role-based access control for feature visibility
- Seamless mode switching without page reloads
- Maintain security boundaries between roles
- Consistent user experience across all features
- Unified navigation and interaction patterns
- Preserve all existing functionality
- Smooth migration path from current architecture

---

## Decision

**We will merge the admin and portal applications into a single Unified Portal with role-based feature access and modular system architecture.**

### Unified Portal Architecture

```
┌──────────────────────────────────────────────────┐
│              UNIFIED PORTAL                      │
├──────────────────────────────────────────────────┤
│  ┌────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ USER MODE  │ │ ADMIN MODE  │ │ TENANT MODE │ │
│  │ (Public)   │ │ (Authoring) │ │ (Mgmt)      │ │
│  ├────────────┤ ├─────────────┤ ├─────────────┤ │
│  │ Content    │ │ Scene Auth  │ │ User Mgmt   │ │
│  │ Community  │ │ Deck Mgmt   │ │ Analytics   │ │
│  │ Navigation │ │ Flow Author │ │ Settings    │ │
│  │ Engagement │ │ Context Mgmt│ │ Policies    │ │
│  └────────────┘ └─────────────┘ └─────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │         MODULAR SYSTEMS LAYER              │ │
│  │  Navigator • Scene • Flow • Dialog         │ │
│  │  Engagement • Context • Authoring          │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │         ROLE-BASED ACCESS CONTROL          │ │
│  │  Permission Checks • Feature Gating        │ │
│  │  Standing System • Dynamic UI              │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Single Codebase**: One application with role-based features
2. **Modular Systems**: Systems work across all modes
3. **Progressive Disclosure**: Features appear based on permissions
4. **Seamless Switching**: Mode changes without page reload
5. **Security First**: Server-side permission validation
6. **Consistent UX**: Unified navigation and interaction patterns
7. **Gradual Migration**: Incremental transition from current state

---

## Architectural Components

### 1. Mode System

Three primary modes based on user role:

```typescript
export enum PortalMode {
  USER = 'user',      // Public content consumption
  ADMIN = 'admin',    // Content authoring and management
  TENANT = 'tenant'   // Tenant administration
}

// Mode switching
export function usePortalMode() {
  const [mode, setMode] = useState<PortalMode>(PortalMode.USER);
  const { user } = useAuth();
  
  const canAccessMode = (mode: PortalMode): boolean => {
    switch (mode) {
      case PortalMode.USER:
        return true; // Everyone
      case PortalMode.ADMIN:
        return user?.hasPermission('admin.access');
      case PortalMode.TENANT:
        return user?.hasPermission('tenant.manage');
    }
  };
  
  const switchMode = (newMode: PortalMode) => {
    if (canAccessMode(newMode)) {
      setMode(newMode);
      navigatorSystem.navigateTo(getModeHomePath(newMode));
    }
  };
  
  return { mode, switchMode, canAccessMode };
}
```

### 2. Role-Based UI Rendering

Components adapt based on user permissions:

```typescript
// Conditional feature rendering
export function SceneView({ scene }: SceneViewProps) {
  const { user } = useAuth();
  const canEdit = user?.hasPermission('scene.edit');
  const canManage = user?.hasPermission('scene.manage');
  
  return (
    <div className="scene-view">
      <SceneContent scene={scene} />
      
      {canEdit && (
        <EditControls scene={scene} />
      )}
      
      {canManage && (
        <ManagementPanel scene={scene} />
      )}
    </div>
  );
}
```

### 3. Unified Navigation

Single navigation system with mode-aware menus:

```typescript
export function NavigationMenu() {
  const { mode } = usePortalMode();
  const { user } = useAuth();
  
  const menuItems = useMemo(() => {
    const items: MenuItem[] = [
      { id: 'home', label: 'Home', path: '/' },
      { id: 'explore', label: 'Explore', path: '/explore' },
    ];
    
    if (user?.hasPermission('admin.access')) {
      items.push(
        { id: 'scenes', label: 'Scenes', path: '/admin/scenes' },
        { id: 'decks', label: 'Decks', path: '/admin/decks' }
      );
    }
    
    if (user?.hasPermission('tenant.manage')) {
      items.push(
        { id: 'users', label: 'Users', path: '/tenant/users' },
        { id: 'settings', label: 'Settings', path: '/tenant/settings' }
      );
    }
    
    return items;
  }, [mode, user]);
  
  return <Menu items={menuItems} />;
}
```

### 4. Enhanced Navigator System

Navigator coordinates cross-mode navigation:

```typescript
export class NavigatorSystem {
  // Mode-aware navigation
  navigateToAdminScene(sceneId: string) {
    this.checkPermission('admin.access');
    this.setMode(PortalMode.ADMIN);
    this.navigateToScene(sceneId);
  }
  
  // Seamless mode switching
  switchToUserMode() {
    this.setMode(PortalMode.USER);
    this.navigateTo('/');
  }
  
  // Permission-checked navigation
  private checkPermission(permission: string) {
    if (!currentUser.hasPermission(permission)) {
      throw new UnauthorizedError();
    }
  }
}
```

---

## Consequences

### Positive

✅ **Single Codebase**: One application to maintain  
✅ **Consistent UX**: Unified experience across all features  
✅ **Seamless Workflow**: No app switching for admin users  
✅ **Reduced Duplication**: Shared components and logic  
✅ **Better Performance**: Single bundle, shared state  
✅ **Simpler Deployment**: One build pipeline  
✅ **Feature Parity**: All features available where appropriate  
✅ **Progressive Enhancement**: Features unlock based on standing  
✅ **Flexible Permissions**: Fine-grained access control

### Negative

⚠️ **Migration Complexity**: Significant refactoring required  
⚠️ **Bundle Size**: Larger initial bundle (mitigated by code splitting)  
⚠️ **Security Risk**: Must ensure proper permission checks  
⚠️ **Testing Overhead**: More complex permission-based testing  
⚠️ **Development Time**: Substantial implementation effort

### Neutral

ℹ️ **Role System**: More sophisticated role/permission management  
ℹ️ **URL Structure**: Unified routing patterns  
ℹ️ **State Management**: Single state tree for all modes  
ℹ️ **Build Process**: Simplified to single application

---

## Migration Strategy

### Phase 1: Foundation (Weeks 1-2)

1. Set up unified portal repository
2. Implement mode system
3. Create role-based access control
4. Build unified navigation
5. Migrate shared components

### Phase 2: User Features (Weeks 3-4)

1. Migrate portal content viewing
2. Implement community features
3. Add engagement system
4. Test user-facing functionality
5. Ensure backward compatibility

### Phase 3: Admin Features (Weeks 5-7)

1. Migrate scene authoring tools
2. Move deck management
3. Transfer flow authoring
4. Migrate context management
5. Test admin workflows

### Phase 4: Tenant Features (Weeks 8-9)

1. Migrate user management
2. Transfer analytics
3. Move tenant settings
4. Implement policy management
5. Test tenant administration

### Phase 5: Integration & Testing (Week 10)

1. End-to-end testing
2. Permission verification
3. Performance optimization
4. Security audit
5. User acceptance testing

### Phase 6: Deployment (Week 11-12)

1. Gradual rollout
2. Monitor performance
3. Fix issues
4. Full production migration
5. Deprecate old applications

---

## Security Considerations

### Server-Side Validation

All permissions must be validated server-side:

```php
// API endpoint with permission check
Route::middleware(['auth', 'permission:scene.edit'])
    ->put('/scenes/{scene}', [SceneController::class, 'update']);
```

### Client-Side Gating

UI elements hidden based on permissions (UX only):

```typescript
// Client-side feature gating
{user.hasPermission('scene.edit') && <EditButton />}
```

### Permission Levels

Hierarchical permission system:

- **User**: Basic content access
- **Contributor**: Can create content
- **Admin**: Can manage content
- **Tenant Admin**: Full tenant control

---

## Implementation Status

### Completed

- ✅ Architecture design documented
- ✅ Migration strategy defined
- ✅ Permission system designed
- ✅ Mode switching concept validated

### Pending

- ⏳ Unified portal implementation
- ⏳ Role-based access control system
- ⏳ Component migration
- ⏳ Navigation integration
- ⏳ Security implementation
- ⏳ Testing and validation
- ⏳ Production deployment

---

## Alternatives Considered

### Alternative 1: Keep Separate Applications

**Approach**: Maintain portal and admin as separate apps

**Rejected Because**:
- Doesn't solve code duplication problem
- User workflow remains fragmented
- Maintenance overhead continues
- Missed opportunity for unified experience

### Alternative 2: iframe Embedding

**Approach**: Embed admin app in portal via iframe

**Rejected Because**:
- Poor user experience
- State sharing extremely difficult
- Security complexities
- Performance overhead
- Feels like a hack

### Alternative 3: Micro-Frontends

**Approach**: Multiple independent frontends with runtime integration

**Rejected Because**:
- Excessive complexity for current scale
- State sharing challenges
- Routing complexity
- Bundle duplication
- Deployment overhead

### Alternative 4: Server-Side Rendering Split

**Approach**: Different SSR routes for different user types

**Rejected Because**:
- Still requires app switching
- Doesn't solve code duplication
- State fragmentation remains
- Complexity without clear benefit

---

## Success Metrics

### Technical Metrics

- Bundle size < current portal + admin combined
- Initial load time ≤ current portal
- Permission checks < 10ms overhead
- Zero security vulnerabilities
- Code coverage > 80%

### User Experience Metrics

- Seamless mode switching
- Consistent navigation patterns
- No feature regressions
- Positive user feedback
- Reduced support tickets

---

## References

- **Design Doc**: `docs/active-development/UNIFIED_PORTAL_DESIGN.md`
- **Migration Strategy**: `docs/active-development/ADMIN_MIGRATION_STRATEGY.md`
- **Roadmap**: `docs/implementation-roadmap.md` (Phase 7)

---

## Notes

The Unified Portal represents a significant evolution in Protogen's architecture, moving from role-separated applications to a single, comprehensive platform. This decision aligns with industry best practices and modern application design patterns.

The modular system architecture established in earlier phases (Navigator, Dialog, Scene, Flow) provides the foundation needed for successful unification. The standing-based permission system enables progressive feature unlocking as users grow within the community.

**Status**: Design complete and approved, awaiting implementation prioritization. Current focus is on completing Scene Management (Phase 2.5) and other foundational features before undertaking this major architectural transition.

**Timeline**: Estimated 11-12 weeks for full implementation when prioritized.

**Risk Assessment**: Medium-High. Requires careful migration and thorough testing, but the benefits justify the investment.

