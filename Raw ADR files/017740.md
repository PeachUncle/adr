# ADR 003: Ignore "found no layout file for reveal" Warning

## Status
Accepted (documented after multiple failed fix attempts)

## Context
Hugo emits this warning during builds:
```
WARN found no layout file for "reveal" for kind "page"
```

This warning appears because:
1. The site uses a dual-theme setup (hugo-theme-stack + reveal-hugo)
2. The `Reveal` output format is defined in `hugo.toml`
3. Hugo's layout resolution logs a warning even though the layout exists and works

## Decision
Accept this warning as a **false positive**. Do not attempt to "fix" it.

The functionality works correctly:
- `layouts/_default/single.reveal.html` handles the Reveal output format
- Posts with `outputs: ["Reveal"]` in front matter render as Reveal.js presentations
- Posts without this setting render as normal Stack-themed blog posts
- Search functionality works
- 404 page uses correct styling

## Failed Fix Attempts
Multiple attempts to suppress this warning broke other functionality:

| Commit | Attempt | Broke |
|--------|---------|-------|
| bee7699 | Add default Reveal template | Normal posts rendered as slides |
| 76db4ce | Remove problematic template | (partial fix) |
| b4bbb93 | Restore search + fix targeting | Final working state |

The current configuration (commit b4bbb93) achieves correct behavior for all page types despite the warning.

## Consequences
- **Positive:** All functionality works correctly
- **Negative:** Warning appears in build output (cosmetic only)

## DO NOT FIX
Every attempted fix has broken something else. The warning is harmless. If Hugo's logging changes in future versions to suppress this false positive, great. Otherwise, ignore it.

## Verification
To confirm the setup still works after any changes:
1. `hugo server -D`
2. Check `content/post/2024/slides-you-get/` renders as Reveal presentation
3. Check `content/post/2024/text-you-write/` renders as normal blog post
4. Check search functionality at `/search/`
5. Check 404 page styling at `/nonexistent-page/`
