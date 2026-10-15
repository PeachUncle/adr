# ADR 0001: External Repository Markdown Structure for Operational Procedures

## Status

Accepted

## Context

OpsCore needs to read operational procedure documents (written in Markdown) from various external private GitLab/GitHub repositories. To ensure consistency, discoverability, and proper processing by OpsCore, a standardized structure and format for these documents are required.

## Decision

We decided to adopt the following rules for storing operational procedure Markdown files in external repositories that OpsCore will access:

1. **Directory:** Operational procedure Markdown files intended for OpsCore should be located within a specific directory in the external repository. The exact path of this directory **is configurable within OpsCore** (e.g., `/docs/opscore/`, `/runbooks/`, etc.).
2. **File Selection:** OpsCore will be configured to **select specific Markdown files** within the designated directory for processing, rather than automatically processing all files in the directory.
3. **File Naming:** While not strictly enforced by OpsCore for discovery (due to selective processing), using a consistent naming pattern like `[category]-[procedure-name].md` is still **highly recommended** for human readability and organization.
    * `[category]` should be a short identifier for the system or area the procedure relates to (e.g., `app`, `db`, `network`).
    * `[procedure-name]` should be a descriptive name using hyphens for spaces (e.g., `user-creation`, `patch-update`).
    * Example: `/docs/opscore/db-backup.md`
4. **Metadata (YAML Front Matter):** Each selected Markdown file must start with YAML front matter containing at least the following fields:

    ```yaml
    ---
    title: "Descriptive Title of the Procedure"
    owner: "Team Name or Email"
    version: "1.0" # Semantic versioning or date recommended
    type: "procedure" # Currently supported: procedure, knowledge
    tags:
      - tag1
      - tag2
    variables: # Optional: only for procedure documents
      - name: server_name
        label: "サーバー名"
        description: "バックアップ対象のサーバー名を入力してください"
        type: string
        required: true
        defaultValue: "prod-db-01"
      - name: backup_path
        label: "バックアップ保存パス"
        description: "バックアップファイルの保存先パス"
        type: string
        required: true
        defaultValue: "/backup/db"
    ---
    ```

    * `title`: Descriptive title of the procedure.
    * `owner`: Team name or email responsible for the procedure.
    * `version`: Version identifier (Semantic Versioning or date recommended).
    * `type`: Indicates the kind of document. **Currently supported values are `procedure` and `knowledge`.**
    * `tags`: A list of relevant tags for filtering/searching.
    * `variables` (optional): Array of variable definitions for parameterized procedures. See ADR 0013 for detailed specification.
      * `name`: Variable identifier (alphanumeric with underscores)
      * `label`: Human-readable label
      * `description`: Detailed explanation
      * `type`: Data type (`string`, `number`, `boolean`, `date`)
      * `required`: Whether the variable is required
      * `defaultValue`: Default value for the variable

5. **Content Structure:** While flexible, it is highly recommended to use consistent headings for clarity:
    * `## Prerequisites`: Any requirements before starting the procedure.
    * `## Steps`: Numbered or bulleted list of actions.
    * `## Verification`: How to confirm the procedure was successful.
    * `## Rollback Plan`: Steps to revert changes if necessary.
6. **Linking:** Use standard relative Markdown links for referencing other procedures within the same repository (e.g., `[Link Text](../category/other-procedure.md)`). Absolute links should be used for external resources.
7. **Permissions:** The OpsCore system requires read access (e.g., via a deploy key or service account) to the repositories containing these documents.

## Consequences

* **Pros:**
  * **Increased Flexibility:** OpsCore administrators can configure specific directories and files, adapting to various repository structures.
  * Standardization (via metadata and recommended structure) simplifies OpsCore's parsing logic for selected documents.
  * Consistent structure improves readability and maintainability for human operators.
  * Metadata enables richer features in OpsCore (filtering, search, ownership tracking).
* **Cons:**
  * Requires clear configuration within OpsCore to specify target directories and files.
  * Teams managing external repositories still need to ensure the selected files adhere to the metadata and content structure recommendations.
