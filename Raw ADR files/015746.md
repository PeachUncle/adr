---
status: "accepted"
date: 2025-06-14
---

# 0002 – Environment‑Variable Naming & Scoping Convention

## Context and Problem Statement
Our build, test, and release scripts rely on environment variables populated
from `.env`.  Without a clear convention, variable sprawl quickly leads to
collisions (`OUTPUT`, `PATH`, …) or ambiguity between input and output
artefacts.

We therefore need a naming scheme that is **unambiguous, grep‑friendly, and
consistent across Bash, Docker, Just, and CI**.

## Decision Drivers
* **Instant recognisability** – a contributor should recognise a variable’s
  purpose from its name alone.
* **Collision avoidance** – especially with POSIX reserved names (`PATH`, `USER`).
* **Cross‑tool portability** – works in Bash, `just`, GitHub Actions.
* **Searchability** – easy to grep for all ROM‑related variables.

## Considered Options
* **Prefix‑based UPPER_SNAKE_CASE** (chosen): `ROM_INPUT_PATH`, `PATCH_PATH` …
* **Hierarchical dot notation**: `ROM.INPUT.PATH`, `PATCH.METADATA.SHA1` …
* **Mixed case descriptive**: `romInputPath`, `patchPath` …
* **No prefixes, rely on context**: `INPUT`, `OUTPUT`, `PATCH` …

## Decision Outcome
Chosen option: **Prefix‑based UPPER_SNAKE_CASE**, because it best meets all
decision drivers:

* Prefix groups (`ROM_`, `PATCH_`, `TOOLCHAIN_`) cluster related variables.
* Upper‑snake is idiomatic for shell / Docker envs.
* Grep‑friendly: `grep -R "^ROM_"` lists all ROM variables instantly.

### Consequences
* **Positive:** Zero namespace clashes with system vars; new prefixes are cheap.
* **Positive:** Editors & CI linters highlight unused vars reliably.
* **Negative:** Variable names are longer (verbosity).  Mitigated by copy‑paste
  and autocomplete.

### Confirmation
* Naming lint is enforced via code‑review checklist.
* CI greps for accidental lower‑case assignments (`grep -nE "^[a-z]+=.*"`).

## Pros and Cons of the Options
### Prefix‑based UPPER_SNAKE_CASE
* **Good:** POSIX‑friendly & conventional.
* **Good:** One‑line grep for a variable family.
* **Neutral:** Verbose.
* **Bad:** Cannot express nested structures (handled by expanding prefix set).

### Hierarchical dot notation
* **Good:** Expresses structure naturally.
* **Bad:** Breaks in Bash (`export ROM.INPUT.PATH=value` is invalid syntax).

### Mixed case descriptive
* **Good:** Shorter.
* **Bad:** Counter‑idiomatic in shell; easy to clash with shell keywords.

### Unprefixed generic names
* **Good:** Shortest.
* **Bad:** High collision risk; zero discoverability.

## More Information
If future tooling requires nested data, we can generate JSON blobs from the
flat env set (`env | jq -Rn '..."`).
