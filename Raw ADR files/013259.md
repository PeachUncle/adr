# ADR 0014: Execution Record and Evidence Management

## Status

Accepted

## Context

OpsCore needs to provide a comprehensive execution record system for operational procedures. This system should:

1. Record who executed which procedure, when, and with what parameter values
2. Allow users to attach screenshots and other evidence during execution
3. Support adding notes and comments for each step
4. Enable sharing execution records with team members and managers
5. Provide search and filtering capabilities for past executions
6. Support both local file storage and cloud object storage (S3, MinIO, etc.) for attachments

## Decision

We will implement an execution record system with the following specifications:

### 1. Execution Record Structure

Each execution record represents a single procedure execution session and contains:

- **Metadata**
  - Unique execution record ID
  - Document ID and version ID
  - Executor user ID
  - Execution title (user-defined or auto-generated)
  - Status: `in_progress`, `completed`, `failed`
  - Start timestamp
  - Completion timestamp
  - Variable values used during execution
  - Overall notes/comments

- **Access Control**
  - Access scope: `private`, `shared`
  - Shared with specific users or groups
  - Administrators can view all execution records

- **Execution Steps**
  - Step number
  - Step description
  - Step-specific notes
  - Attachments (screenshots, files)
  - Execution timestamp for each step

### 2. User Interface

#### Left Pane: Variable Input Form

- Display input fields for all variables defined in the procedure
- Pre-fill default values
- Validate required fields
- Show variable values in the rendered document

#### Center Pane: Procedure Document

- Display the procedure document with variable values substituted
- Highlight current step (optional)

#### Right Pane: Execution Evidence Panel

- **Execution Info Section**
  - Execution title (editable)
  - Status selector
  - Start time (auto-recorded)
  - Completion time (auto-updated on completion)
  - Overall notes textarea

- **Steps Section**
  - List of execution steps (can correspond to procedure steps)
  - For each step:
    - Step number and description
    - Notes textarea
    - File upload button for screenshots/attachments
    - Thumbnail preview of attached images
    - Timestamp when step was executed

- **Action Buttons**
  - Save Draft: Save current execution record in progress
  - Complete: Mark execution as completed
  - Mark as Failed: Mark execution as failed
  - Share: Configure sharing settings

### 3. Attachment Storage

#### Storage Strategy

- **Default: Local File System**
  - Store files in a configurable directory (e.g., `/data/attachments/{execution_record_id}/{attachment_id}`)
  - Organize by execution record ID for easy cleanup

- **Optional: Object Storage (S3/MinIO)**
  - Support S3-compatible object storage
  - Store files with key pattern: `attachments/{execution_record_id}/{attachment_id}`
  - Use pre-signed URLs for secure access

#### Storage Configuration

Storage type is configurable per deployment via environment variables:

```bash
ATTACHMENT_STORAGE_TYPE=local # or s3
ATTACHMENT_STORAGE_PATH=/data/attachments # for local
S3_BUCKET=opscore-attachments # for S3
S3_ENDPOINT=https://s3.amazonaws.com # for S3/MinIO
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
```

#### Attachment Metadata

Stored in database:

- Attachment ID
- Execution record ID
- Step number
- File name
- File size
- MIME type
- Storage type (`local` or `s3`)
- Storage path or key
- Uploaded by user ID
- Upload timestamp

### 4. Access Control and Sharing

#### Private Execution Records

- By default, execution records are private to the executor
- Only the executor and administrators can view

#### Shared Execution Records

- Executor can share with specific users or groups
- Shared users/groups can view but not edit
- Administrators can view all records regardless of sharing settings

#### Sharing UI

- "Share" button opens a modal
- Select users or groups to share with
- Option to make it accessible to all users in specific groups

### 5. Search and Filtering

Users can search and filter execution records by:

- Procedure document (title or ID)
- Executor (user name or ID)
- Execution date range
- Status (`in_progress`, `completed`, `failed`)
- Variables used (e.g., find all executions for a specific server)

#### Search UI

- Search bar for keyword search
- Filter dropdowns for document, executor, status
- Date range picker
- Results displayed in a table or card view with:
  - Execution title
  - Procedure name
  - Executor
  - Status
  - Start time
  - Actions (View, Edit, Delete)

### 6. Execution Record Lifecycle

1. **Start Execution**
   - User opens a procedure document
   - Fills in variable values
   - Clicks "Start Execution" button
   - System creates a new execution record with status `in_progress`

2. **During Execution**
   - User follows procedure steps
   - Adds notes and uploads screenshots for each step
   - Can save draft at any time

3. **Complete Execution**
   - User clicks "Complete" button
   - System updates status to `completed`
   - Records completion timestamp

4. **Failed Execution**
   - User clicks "Mark as Failed" button
   - System updates status to `failed`
   - Can add notes explaining the failure reason

5. **View Past Executions**
   - Users can browse their past execution records
   - View all details including variable values and attachments
   - Use as reference for future executions

### 7. Data Retention

- Execution records are retained indefinitely by default
- Administrators can configure retention policies
- When an execution record is deleted:
  - Soft delete the record (mark as deleted)
  - Optionally delete associated attachments after a grace period
  - Maintain deletion audit log

## Consequences

### Pros

- **Complete Traceability**: Full record of who did what, when, and how
- **Evidence Storage**: Screenshots and files provide proof of execution
- **Knowledge Sharing**: Team members can learn from past executions
- **Audit Compliance**: Detailed records for compliance and audit purposes
- **Flexible Storage**: Support for both local and cloud storage
- **Collaboration**: Sharing enables team collaboration and review

### Cons

- **Storage Requirements**: Attachments can consume significant storage space
- **Complexity**: Requires implementation of file upload, storage abstraction, and access control
- **Performance**: Large attachments may impact upload/download performance
- **Privacy Concerns**: Need to ensure proper access control for sensitive execution records

## Implementation Notes

1. Implement ExecutionRecord, ExecutionStep, and Attachment entities as per domain model
2. Create storage abstraction layer supporting both local filesystem and S3
3. Implement file upload API with multipart form support
4. Create frontend components for execution evidence panel
5. Implement access control middleware for execution record viewing
6. Add search and filtering API endpoints
7. Implement soft delete for execution records
8. Add configuration for storage type and S3 credentials
9. Consider implementing background job for thumbnail generation
10. Add API endpoints for sharing configuration
