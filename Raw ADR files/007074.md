# ADR 009: Feature Flags for Subscription Tiers

**Status:** Accepted

**Date:** 2024-11-12

---

## Context

BuildFlow has a freemium business model with three tiers (Starter, Pro, Business). We need to:
- Enable/disable features based on subscription
- Support self-hosted (all features enabled)
- Support SaaS (tier-based features)
- Avoid maintaining separate codebases

---

## Decision

**Use feature flags to control feature access based on organization subscription tier.**

### Implementation

```php
// config/buildflow.php
return [
    'features' => [
        'client_portal' => env('FEATURE_CLIENT_PORTAL', false),
        'white_label' => env('FEATURE_WHITE_LABEL', false),
        'api_access' => env('FEATURE_API_ACCESS', false),
        'advanced_analytics' => env('FEATURE_ADVANCED_ANALYTICS', false),
    ],
    
    'tiers' => [
        'starter' => [
            'price' => 0,
            'limits' => [
                'projects' => 3,
                'clients' => 10,
                'storage_mb' => 100,
            ],
            'features' => [], // No premium features
        ],
        'pro' => [
            'price' => 29,
            'limits' => [
                'projects' => 20,
                'clients' => 100,
                'storage_mb' => 10240,
            ],
            'features' => ['client_portal'],
        ],
        'business' => [
            'price' => 79,
            'limits' => [
                'projects' => -1, // unlimited
                'clients' => -1,
                'storage_mb' => 102400,
            ],
            'features' => ['client_portal', 'api_access', 'advanced_analytics'],
        ],
    ],
];
```

### Usage in Code

```php
// Check feature access
if (auth()->user()->organization->hasFeature('client_portal')) {
    // Show client portal UI
}

// Check limits
if (auth()->user()->organization->isAtLimit('projects')) {
    return response()->json(['error' => 'Project limit reached'], 403);
}

// Middleware
Route::middleware(['feature:client_portal'])->group(function () {
    // Protected routes
});
```

### Environment-Based

**Self-Hosted (.env):**
```
FEATURE_CLIENT_PORTAL=true
FEATURE_WHITE_LABEL=true
FEATURE_API_ACCESS=true
# All features enabled
```

**SaaS (.env):**
```
FEATURE_CLIENT_PORTAL=false  # Tier-based
FEATURE_WHITE_LABEL=false    # Tier-based
FEATURE_API_ACCESS=false     # Tier-based
# Features controlled by subscription
```

---

## Consequences

### Positive
- ✅ Single codebase for self-hosted and SaaS
- ✅ Easy to add new features
- ✅ Graceful feature rollout
- ✅ A/B testing possible
- ✅ Clear tier differentiation
- ✅ No code duplication

### Negative
- ⚠️ Code paths increase complexity
- ⚠️ Must test all combinations
- ⚠️ UI must handle disabled features
- ⚠️ Feature discovery complexity

---

## Tier Strategy

### Starter (Free)
- Core CRUD features
- Basic dashboard
- Limited capacity
- **Goal**: Get users started, prove value

### Pro ($29/mo)
- Client portal (KEY DIFFERENTIATOR)
- More capacity
- Branded exports
- **Goal**: Professional contractors, transparency

### Business ($79/mo)
- API access
- Advanced analytics
- Team features
- **Goal**: Growing businesses, integration needs

---

**Related:** ADR-006 (open source with tier-based SaaS)
