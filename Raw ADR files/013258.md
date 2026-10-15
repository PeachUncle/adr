# ADR 0013: Document Variable Definition and Substitution

## Status

Accepted

## Context

OpsCore manages operational procedure documents that often require customization for specific execution contexts (e.g., server names, database names, backup paths). To support this, we need a mechanism to:

1. Define variables within procedure documents
2. Allow users to input values for these variables when executing procedures
3. Display the document with substituted variable values
4. Record the variable values used in each execution as part of the execution record

## Decision

We will implement a variable definition and substitution mechanism for procedure documents with the following specifications:

### 1. Variable Definition in Frontmatter

Variables are defined in the YAML frontmatter of Markdown files using a `variables` array:

```yaml
---
title: "Database Backup Procedure"
owner: "Database Team"
version: "1.0"
type: "procedure"
tags:
  - database
  - backup
variables:
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
  - name: retention_days
    label: "保持期間（日数）"
    description: "バックアップの保持期間"
    type: number
    required: false
    defaultValue: 30
  - name: enable_compression
    label: "圧縮を有効化"
    description: "バックアップファイルを圧縮するかどうか"
    type: boolean
    required: false
    defaultValue: true
---
```

#### Variable Properties

- **name** (string, required): Variable identifier used for substitution. Must be alphanumeric with underscores only.
- **label** (string, required): Human-readable label displayed in the UI.
- **description** (string, optional): Detailed explanation of the variable's purpose.
- **type** (string, required): Data type. Supported values: `string`, `number`, `boolean`, `date`.
- **required** (boolean, required): Whether the variable must be filled before execution.
- **defaultValue** (string/number/boolean, optional): Default value pre-filled in the input form.

### 2. Variable References in Document Body

Variables are referenced in the Markdown content using double curly braces:

```markdown
## Procedure Steps

1. Connect to the server: `{{server_name}}`
2. Create backup directory: `mkdir -p {{backup_path}}`
3. Execute backup command with retention of {{retention_days}} days
4. Compression enabled: {{enable_compression}}
```

### 3. Variable Input UI

When a user opens a procedure document, the system will:

1. Parse the `variables` array from the frontmatter
2. Display an input form in the left pane with:
   - Label for each variable
   - Input field appropriate for the variable type (text input, number input, checkbox, date picker)
   - Default value pre-filled if specified
   - Required field indicator
   - Description text as help text
3. Allow users to modify the values
4. Validate required fields before allowing execution
5. Substitute variable references in the document display with the user-provided values

### 4. Execution Record Storage

When a user executes a procedure, the system records:

- Document ID and version
- User ID
- Execution timestamp
- **Variable values used** (name-value pairs)
- Execution steps with notes and attachments

This allows for complete traceability of what values were used in each execution.

### 5. Variable Substitution Logic

- Backend: Parse frontmatter to extract variable definitions
- Frontend: Display input form based on variable definitions
- On value change: Re-render document with substituted values
- On execution: Store the final variable values in the execution record

### 6. Backward Compatibility

Documents without the `variables` field in frontmatter will work as before without any input form or variable substitution.

## Consequences

### Pros

- **Flexibility**: Procedures can be parameterized for different execution contexts
- **Traceability**: Execution records capture exactly what values were used
- **User-Friendly**: Clear input forms guide users through required parameters
- **Type Safety**: Variable types help prevent input errors
- **Reusability**: Same procedure can be reused with different parameters

### Cons

- **Increased Complexity**: Requires frontmatter parsing and variable substitution logic
- **UI Complexity**: Need to implement input forms with validation
- **Storage Requirements**: Execution records need to store variable values
- **Migration**: Existing procedures need to be updated to use variables if they want parameterization

## Implementation Notes

1. Update ADR 0001 to include the `variables` field specification
2. Extend the Document entity to include variable definitions
3. Implement frontmatter parser to extract variable definitions
4. Create frontend components for variable input forms
5. Implement variable substitution in the document renderer
6. Update ExecutionRecord entity to store variable values
7. Add validation logic for required variables
