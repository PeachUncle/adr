# ADR 0003: Model Registry and Routing

- Status: Accepted
- Date: 2025-09-06
- Authors: Aimless
- Deciders: Aimless
- Tags: routing, registry, providers, configuration, precedence

## Context

`llm-fiber` is providerless by default. The client should infer which provider to call based on the model name without forcing the user to specify `provider=...` on every call. We need a small, predictable “model registry” that maps model identifiers to providers and defines unambiguous precedence rules.

Requirements:

- Predictable and minimal: exact and prefix mappings only.
- Explicit precedence: per-call override > exact mapping > prefix mapping.
- Deterministic tie-breaking: most-specific (longest) prefix wins; otherwise preference order.
- No credentials: API keys/base URLs are configured on the client, not in the registry.
- Customizable: allow users to extend/override mappings and set preference order.
- Fail fast: unknown or ambiguous models should produce clear errors with actionable guidance.

Related docs: features/model-registry.md, features/providers.md, features/configuration.md.

## Decision

Introduce a `ModelRegistry` with:
- Two mapping tables:
  - Exact: `{model: provider}`
  - Prefix: `{prefix: provider}`
- A provider preference order: `("openai", "anthropic", "gemini")` by default.
- A resolution algorithm with strict, documented precedence.
- Clear error types/messages for unknown and ambiguous cases.
- A small, stable API for mapping, unmapping, and resolution.

### API Surface (conceptual)

- `map_exact(model: str, provider: str) -> None`
- `unmap_exact(model: str) -> None`
- `map_prefix(prefix: str, provider: str) -> None`
- `unmap_prefix(prefix: str) -> None`
- `set_preference_order(order: tuple[str, ...]) -> None`
- `provider_for_model(model: str) -> str`  (raises on error)
- `try_provider_for_model(model: str) -> str | None` (optional, returns None on unknown)
- `default() -> ModelRegistry` (pre-populated defaults)

Notes:
- All operations are case-sensitive.
- Providers are simple strings, e.g., `"openai" | "anthropic" | "gemini" | custom`.

### Default Mapping

Shipped defaults (subject to evolution as ecosystems change):
- openai: `gpt-*`, `o*`, `text-*`
- anthropic: `claude-*`
- gemini: `gemini-*`

The default preference order is:
- `("openai", "anthropic", "gemini")`

### Resolution Precedence and Algorithm

Given an input `model` and optionally a per-call `provider` override:

1) Per-call override
   - If the call specifies `provider=...`, return it (no registry lookup).

2) Exact match
   - If `model` is in the exact mapping table, return that provider.

3) Prefix match (deterministic)
   - Collect all prefixes P where `model.startswith(prefix)`.
   - If none, raise `ModelResolutionError(kind="unknown_model", model=...)` with guidance.
   - Reduce to the set with the longest prefix length (most specific).
     - If this yields a single provider, return it.
     - If multiple providers remain (equal-length prefixes mapping to different providers):
       - Use `preference_order` to pick the highest-ranked provider among them.
       - Providers absent from `preference_order` are considered after the listed ones, in lexicographic order (stable and explicit).
       - If a tie persists (e.g., empty preference order and equal ranks), raise `ModelResolutionError(kind="ambiguous_model", model=..., candidates=[...])` with guidance.

4) Fallback
   - No other fallbacks (e.g., fuzzy matching) are attempted. Fail fast to avoid surprises.

### Diagnostics and Errors

- Unknown model:
  - `ModelResolutionError(kind="unknown_model", model=..., message="No exact or prefix match. Add map_exact/map_prefix or specify provider explicitly.")`
- Ambiguous model:
  - `ModelResolutionError(kind="ambiguous_model", model=..., candidates=["openai","anthropic"], message="Conflicting equal-specificity prefixes. Adjust set_preference_order() or supply provider explicitly.")`

Implementations should ensure error messages suggest:
- Using `map_exact(...)` or `map_prefix(...)`,
- Adjusting `set_preference_order(...)`, or
- Passing `provider=...` per call.

### Mutability & Threading

- The registry is mutable to support configuration at startup (add/override mappings, set preference).
- Guidance: perform registry customization during application initialization, before high-concurrency call paths.
- Implementations should protect internal maps with a lock if concurrent mutation is needed, or document that runtime mutation is not thread-safe.

### Scope & Non-Goals

- The registry does not store credentials or base URLs.
  - Keys/URLs live on the `Fiber` client (constructor or `from_env()`).
- No fuzzy matching (e.g., edit distance). Exact or prefix only.
- No remote discovery of capabilities; see “Capabilities & Pricing” for a separate surface.

## Rationale

- Simplicity: Exact + prefix with deterministic precedence is easy to reason about and test.
- Safety: Longest-prefix and explicit preference order prevent accidental misrouting when multiple prefixes could match.
- Flexibility: Users can extend mappings for custom gateways or model namespaces (e.g., “acme-*”).
- Separation of concerns: Credentials and endpoints remain on the client; the registry only decides routing.

## Consequences

Positive:
- Predictable provider routing for common model families.
- Easy customization for private models and gateways.
- Clear operational behavior on unknown/ambiguous cases.

Negative:
- Requires initial customization for unusual model names.
- Case sensitivity may surprise some users; however, it avoids implicit normalization pitfalls.

Mitigations:
- Provide helpful errors and examples in docs.
- Offer `default()` with sensible initial mappings and preference.

## Alternatives Considered

1) Fuzzy matching (e.g., “closest prefix” by edit distance)
   - Rejected: surprising, hard to audit, and risky under evolving model catalogs.

2) Embedding credentials/base URLs in the registry
   - Rejected: mixes concerns and complicates secure handling of secrets.

3) Preference-only routing without longest-prefix tie-breaker
   - Rejected: loses specificity when overlapping prefixes exist (e.g., `gpt-4` vs `gpt-`).

4) Provider detection via provider APIs (remote introspection)
   - Rejected: adds network overhead, brittleness, and delays; model strings should be sufficient.

## Detailed Examples

- Map custom prefixes to providers:
  - `fiber.model_registry.map_prefix("acme-", "openai")`

- Exact mapping:
  - `fiber.model_registry.map_exact("my-claude", "anthropic")`

- Preference order (tie-breaking):
  - `fiber.model_registry.set_preference_order(("anthropic", "openai", "gemini"))`

- Per-call override (always wins):
  - `fiber.sync.ask("...", model="gpt-4o-mini", provider="openai")`

- Overlapping prefixes:
  - Prefix map: `"gpt-" -> openai`; `"gpt-4" -> openai`; `"gpt-4"` is more specific and wins.
  - If two different providers had equal-length matching prefixes (edge case), preference order applies.

- Unknown model:
  - Input: `"x-unknown-1"`
  - Error: unknown_model with guidance to add `map_prefix("x-", "...")` or pass `provider=...`.

## Appendix: Pseudocode

```
def provider_for_model(model: str, provider_override: str | None = None) -> str:
    if provider_override:
        return provider_override

    if model in exact_map:
        return exact_map[model]

    # collect all prefix matches
    matches = [(prefix, prov) for (prefix, prov) in prefix_map.items()
               if model.startswith(prefix)]
    if not matches:
        raise ModelResolutionError(kind="unknown_model", model=model)

    # keep only longest-prefix matches
    max_len = max(len(p) for (p, _) in matches)
    longest = [(p, prov) for (p, prov) in matches if len(p) == max_len]

    # reduce by preference order
    if len({prov for (_, prov) in longest}) == 1:
        return longest[0][1]

    candidates = list({prov for (_, prov) in longest})
    ordered = order_by_preference(candidates, preference_order)
    if not ordered:
        raise ModelResolutionError(kind="ambiguous_model",
                                   model=model,
                                   candidates=candidates)
    return ordered[0]
```

Where `order_by_preference()` returns candidates sorted so that providers present in `preference_order` are ordered by their index, followed by any unlisted providers in lexicographic order (stable, explicit).

## Migration

- Consolidate any existing ad-hoc routing into `ModelRegistry`.
- Use `map_exact/map_prefix` at startup to capture org-specific routes.
- If you previously relied on implicit or fuzzy behavior, introduce preference order or per-call overrides to remove ambiguity.

## Observability

- Optional debug logs when resolution occurs (model, decision path).
- Consider a metric for unknown/ambiguous resolution attempts to detect configuration drift.
