# ADR-003: Secret Input Processing

## Status
Proposed

## Context
Following ADR-002's secret management model, we need to define how user input for secret creation and modification will be processed and validated. This includes validation rules, normalization processes, and error handling.

## Decision

### 1. Input Structure
The system accepts input in two formats:

#### 1.1 API/UI Input (JSON)
```json
{
    "path": "project/storage",
    "labels": {
        "env": "prod",
        "region": "us-west-2"
    },
    "name": "postgres",
    "tags": ["db", "pg"],
    "fields": {
        "username": "admin",
        "password": "secret"
    }
}
```

#### 1.2 Reference String Input (CLI)
```plaintext
project_storage:env=prod,region=us-west-2:postgres
```

### 2. Processing Flow

#### 2.1 Path Processing
1. **Format Detection**:
   - Detect input format (JSON or reference string)
   - Parse reference string if needed
   - Extract path components

2. **Path Normalization**:
   - Remove leading and trailing slashes
   - Example transformations:
     ```plaintext
     "/project/app/"  -> "project/app"
     "project/app/"   -> "project/app"
     "/project/app"   -> "project/app"
     "project/app"    -> "project/app"
     ```

3. **Format Conversion**:
   - Reference format to internal:
     ```plaintext
     "project_app" -> "project/app"
     ```

#### 2.2 Validation Stages
The system processes input in the following sequential stages:

1. **Structure Validation**
   * Validates presence of required fields:
     - path
     - name
   * Ensures correct data types
   * Validates array/object structures

2. **Character Validation**
   * Path segments: `[a-zA-Z0-9-_]+`
   * Label validation:
     - Keys:
       * Pattern: `[a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]` or `[a-zA-Z0-9]`
       * Maximum length: 63 characters
       * Examples:
         ```
         Valid:      'env', 'region-1', 'app123'
         Invalid:    '-env', 'env-', 'app.name'
         ```
     - Values:
       * Pattern: `[a-zA-Z0-9][a-zA-Z0-9-_.]*[a-zA-Z0-9]` or `[a-zA-Z0-9]`
       * Maximum length: 63 characters
       * Examples:
         ```
         Valid:      'prod', 'v1.2.3', 'us-west-2'
         Invalid:    '.prod', 'prod.', '-test'
         ```
   * Secret name: `[a-zA-Z0-9-_.]+`

3. **Label Processing**
   * Validates all label key-value pairs against patterns
   * Checks length constraints (63 chars)
   * Validates beginning and ending characters
   * Example validation:
     ```plaintext
     Input: {"env": "prod", "region": "us-west-2"}
     Checks:
     - Key 'env': starts with 'e' (alpha), ends with 'v' (alpha) ✓
     - Value 'prod': starts with 'p' (alpha), ends with 'd' (alpha) ✓
     - Key 'region': starts with 'r' (alpha), ends with 'n' (alpha) ✓
     - Value 'us-west-2': starts with 'u' (alpha), ends with '2' (num) ✓
     ```

4. **Tag Processing**
   * Validates tag format
   * Removes duplicate tags
   * Tags are stored in sorted order

5. **Uniqueness Check**
   * Validates combination of normalized path + all labels + name is unique
   * Label order does not affect uniqueness check

### 3. Error Handling

#### 3.1 Processing Rules
* Validation stops at first error encountered
* Each stage must pass completely before moving to next
* Single error returned from failing stage
* Error messages must be clear and actionable

#### 3.2 Error Categories
1. **Structure Errors**
   ```json
   {
     "code": "INVALID_STRUCTURE",
     "message": "Missing required field: path",
     "field": "path"
   }
   ```

2. **Label Validation Errors**
   ```json
   {
     "code": "INVALID_LABEL_KEY",
     "message": "Label key must begin and end with alphanumeric characters",
     "field": "labels",
     "key": "-env",
     "constraint": "Must match pattern: [a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]"
   }
   ```
   ```json
   {
     "code": "INVALID_LABEL_VALUE",
     "message": "Label value must be 63 characters or less",
     "field": "labels",
     "key": "region",
     "value": "<very long value>",
     "constraint": "Maximum length: 63 characters"
   }
   ```

3. **Uniqueness Errors**
   ```json
   {
     "code": "DUPLICATE_SECRET",
     "message": "Secret with this path, labels, and name already exists",
     "conflict": {
       "path": "project/app",
       "labels": {"env": "prod"},
       "name": "postgres"
     }
   }
   ```

## Consequences

### Positive
* Clear, predictable processing flow
* Early failure for invalid input
* Consistent path normalization
* Well-defined error responses
* Support for multiple input formats
* Order-independent label processing
* Kubernetes-compatible label constraints
* Detailed validation error messages

### Negative
* Single error response might require multiple request-response cycles
* Path normalization may cause initial user confusion
* Need to maintain format conversion logic
* Additional processing overhead for reference string parsing
* Stricter label validation may require updating existing labels

## Notes
* Consider implementing bulk validation mode for multiple secrets
* Monitor performance impact of uniqueness checks
* Document common error scenarios and resolutions
* Consider caching normalized paths
* Future: Consider relaxed validation mode for migration scenarios