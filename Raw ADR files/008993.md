# ADR-004: File Storage Strategy

**Status:** Accepted  
**Date:** 2025-10-07  
**Decision Makers:** Development Team, Infrastructure Team  
**Consulted:** Security Team, DevOps Team  

---

## Context

The EchoVerse Platform requires secure file upload and storage capabilities for:
- User profile pictures and avatars
- Product images for e-commerce
- Blog post media (images, videos)
- Document uploads (PDFs, Word docs)
- Marketing assets and media libraries
- Plugin files and resources

We needed a storage solution that provides:
- Secure file upload validation
- Malware and virus scanning
- Efficient file serving
- Scalability for growing storage needs
- CDN integration for performance
- Metadata tracking and search

---

## Decision

We have decided to implement a **local disk storage** solution with **Multer** for uploads, combined with **ClamAV virus scanning** and comprehensive file validation.

### Key Components:

1. **File Upload**
   - Multer for multipart/form-data handling
   - Disk storage with secure filename generation
   - Pre-validation of file size and type
   - Magic number (file signature) validation

2. **Security Layers**
   - File type whitelist (images, documents, videos)
   - MIME type validation
   - Magic number verification (prevent spoofing)
   - ClamAV virus scanning (production)
   - Path traversal protection
   - File size limits per type

3. **Storage Organization**
   - Local directory: `./uploads`
   - Secure random filenames (crypto.randomBytes)
   - Metadata stored in PostgreSQL
   - Static file serving with rate limiting

4. **File Types Supported**
   - **Images**: JPEG, PNG, GIF, WebP (max 5MB)
   - **Documents**: PDF, DOC, DOCX, TXT, CSV (max 10MB)
   - **Videos**: MP4, MPEG, WebM (max 50MB)

---

## Rationale

### Why Local Disk Storage?

**Pros:**
- ✅ Simple implementation and deployment
- ✅ No vendor lock-in
- ✅ Low cost (no storage fees)
- ✅ Full control over files
- ✅ Easy backup and migration
- ✅ Fast access on same server
- ✅ Docker volume compatibility

**Cons:**
- ❌ Not horizontally scalable (single server)
- ❌ No built-in CDN
- ❌ Manual backup required
- ❌ Disk space limits

**When to migrate to S3:**
- Storage exceeds 100GB
- Multi-region deployment needed
- CDN performance critical
- File sharing across servers required

### Why Multer?

**Pros:**
- ✅ Industry standard for Node.js
- ✅ Express middleware integration
- ✅ Flexible storage options (disk, memory, S3)
- ✅ File size limits
- ✅ Multipart form data handling
- ✅ Well-tested and maintained

**Cons:**
- ❌ Requires custom validation logic
- ❌ No built-in virus scanning

### Why ClamAV?

**Pros:**
- ✅ Open source antivirus
- ✅ Regular signature updates
- ✅ Docker image available
- ✅ Low resource usage
- ✅ REST API support

**Cons:**
- ❌ Additional infrastructure
- ❌ Scan latency (~100-500ms)
- ❌ False positives possible

---

## Implementation Details

### Upload Configuration

```typescript
// server/middleware/upload-enhanced.ts
const UPLOAD_DIR = process.env.UPLOAD_DIR || './uploads';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB default

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    const randomName = crypto.randomBytes(16).toString('hex');
    cb(null, `${randomName}${ext}`);
  }
});
```

### File Type Validation

```typescript
const ALLOWED_IMAGE_TYPES = [
  'image/jpeg', 'image/jpg', 'image/png', 
  'image/gif', 'image/webp'
];

const ALLOWED_DOCUMENT_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain', 'text/csv'
];

const ALLOWED_VIDEO_TYPES = [
  'video/mp4', 'video/mpeg', 'video/webm'
];
```

### Magic Number Validation

```typescript
const FILE_SIGNATURES: Record<string, number[][]> = {
  'image/jpeg': [[0xFF, 0xD8, 0xFF]],
  'image/png': [[0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]],
  'image/gif': [[0x47, 0x49, 0x46, 0x38, 0x37, 0x61], [0x47, 0x49, 0x46, 0x38, 0x39, 0x61]],
  'application/pdf': [[0x25, 0x50, 0x44, 0x46]], // %PDF
};

function validateMagicNumbers(buffer: Buffer, mimeType: string): boolean {
  const signatures = FILE_SIGNATURES[mimeType];
  if (!signatures) return true;
  
  return signatures.some(sig => 
    sig.every((byte, index) => buffer[index] === byte)
  );
}
```

### Multi-Layer Validation

1. **Pre-Upload Validation**
   - Content-Length header check
   - File size validation before upload

2. **Multer Validation**
   - MIME type whitelist
   - File filter callback
   - Size limits

3. **Post-Upload Validation**
   - Magic number verification
   - `file-type` library validation
   - MIME type spoofing detection

4. **Virus Scanning**
   - ClamAV scan (production only)
   - File quarantine on detection
   - Automatic cleanup

### Upload Endpoints

```typescript
// Image upload
router.post('/api/upload/image', 
  authenticateToken,
  mediaUploadRateLimiter,
  preValidateFileSize,
  uploadImage,
  verifyFileType,
  virusScanMiddleware,
  async (req, res) => {
    // Return file metadata
  }
);

// Document upload
router.post('/api/upload/document',
  authenticateToken,
  fileUploadRateLimiter,
  preValidateFileSize,
  uploadSingle,
  verifyFileType,
  virusScanMiddleware,
  async (req, res) => {
    // Return file metadata
  }
);
```

### File Metadata Storage

```typescript
// PostgreSQL table for file metadata
export const uploadedFiles = pgTable('uploaded_files', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => users.id).notNull(),
  filename: varchar('filename', { length: 255 }).notNull(),
  originalName: varchar('original_name', { length: 255 }).notNull(),
  mimetype: varchar('mimetype', { length: 100 }).notNull(),
  size: integer('size').notNull(),
  path: text('path').notNull(),
  uploadedAt: timestamp('uploaded_at').defaultNow().notNull(),
});
```

### Static File Serving

```typescript
// Serve uploaded files with rate limiting
app.use('/uploads', 
  staticAssetRateLimiter,
  express.static(UPLOAD_DIR, {
    maxAge: '1d',
    etag: true,
    lastModified: true,
  })
);
```

---

## Security Measures

### 1. Path Traversal Prevention
```typescript
function validateFilename(filename: string): void {
  if (filename.includes('..') || 
      filename.includes('/') || 
      filename.includes('\\')) {
    throw new Error('Invalid filename: path traversal detected');
  }
  
  if (filename.startsWith('.')) {
    throw new Error('Hidden files not allowed');
  }
}
```

### 2. File Size Limits
```typescript
const FILE_SIZE_LIMITS: Record<string, number> = {
  'image/jpeg': 5 * 1024 * 1024,   // 5MB
  'image/png': 5 * 1024 * 1024,    // 5MB
  'application/pdf': 10 * 1024 * 1024, // 10MB
  'video/mp4': 50 * 1024 * 1024,   // 50MB
};
```

### 3. Virus Scanning (Production)
```typescript
// server/middleware/virus-scan-production.ts
export async function scanFileWithClamAV(filePath: string): Promise<boolean> {
  const clamav = new NodeClam({
    clamdscan: {
      host: process.env.CLAMAV_HOST || 'localhost',
      port: parseInt(process.env.CLAMAV_PORT || '3310'),
    },
  });
  
  const { isInfected } = await clamav.scanFile(filePath);
  return isInfected;
}
```

### 4. Rate Limiting
```typescript
// Image uploads: 20 requests/minute
export const mediaUploadRateLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  message: 'Too many upload requests',
});

// Static files: 100 requests/minute
export const staticAssetRateLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 100,
});
```

---

## Consequences

### Positive

1. **Security**: Multi-layer validation and virus scanning
2. **Simplicity**: Easy to implement and maintain
3. **Cost**: No storage fees or vendor costs
4. **Control**: Full control over file access and policies
5. **Performance**: Fast access on same server
6. **Privacy**: Files stay on our infrastructure

### Negative

1. **Scalability**: Limited to single server capacity
2. **CDN**: No built-in CDN for global distribution
3. **Backup**: Manual backup process required
4. **Storage**: Disk space limits
5. **Multi-Server**: Not suitable for horizontal scaling

### Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Disk full | Monitoring alerts at 80% capacity, cleanup old files |
| Malware upload | ClamAV scanning, file validation, quarantine |
| DDoS via uploads | Rate limiting, file size limits, authentication |
| Data loss | Daily backups to S3, disaster recovery plan |
| Path traversal | Filename validation, secure path handling |
| Type spoofing | Magic number validation, file-type library |

---

## Migration Path to S3

When scaling requirements demand, migration to S3:

### Phase 1: Dual Write (Transition)
```typescript
// Write to both local and S3
await Promise.all([
  writeToLocal(file),
  writeToS3(file)
]);
```

### Phase 2: Read from S3, Fallback to Local
```typescript
const fileUrl = await s3.getSignedUrl('getObject', {
  Bucket: 'uploads',
  Key: filename,
  Expires: 3600
});
```

### Phase 3: S3 Only
- Migrate all files to S3
- Update all URLs
- Remove local storage
- Configure CloudFront CDN

### S3 Configuration (Future)
```typescript
const s3Storage = multerS3({
  s3: s3Client,
  bucket: process.env.S3_BUCKET_NAME,
  acl: 'private',
  contentType: multerS3.AUTO_CONTENT_TYPE,
  key: (req, file, cb) => {
    const randomName = crypto.randomBytes(16).toString('hex');
    cb(null, `uploads/${randomName}${path.extname(file.originalname)}`);
  }
});
```

---

## Monitoring & Maintenance

### Disk Usage Monitoring
```typescript
// Check disk usage
const diskUsage = await checkDiskSpace('/');
if (diskUsage.percentUsed > 80) {
  alertAdmins('Disk usage critical');
}
```

### File Cleanup Policy
- Delete unattached files after 30 days
- Compress old files (>90 days)
- Archive deleted user files for 30 days
- Permanent deletion after retention period

### Backup Strategy
- **Daily**: Incremental backup to S3
- **Weekly**: Full backup to S3
- **Monthly**: Archive to Glacier
- **Retention**: 30-day point-in-time recovery

---

## Alternatives Considered

### 1. AWS S3
**Pros:** Scalable, CDN, global distribution  
**Cons:** Vendor lock-in, cost, complexity  
**Decision:** Deferred for future scaling

### 2. Cloudinary
**Pros:** Image optimization, transformations  
**Cons:** Cost, vendor lock-in  
**Decision:** Rejected for control

### 3. MinIO
**Pros:** S3-compatible, self-hosted  
**Cons:** Additional infrastructure  
**Decision:** Considered for future

### 4. Google Cloud Storage
**Pros:** Scalable, global  
**Cons:** Vendor lock-in, cost  
**Decision:** Rejected for AWS preference

---

## Related Decisions

- [ADR-001: Database Choice](./ADR-001-database-choice.md) - File metadata storage
- [ADR-002: Authentication Strategy](./ADR-002-authentication-strategy.md) - Upload authentication

---

## References

- [Multer Documentation](https://github.com/expressjs/multer)
- [ClamAV Documentation](https://docs.clamav.net/)
- [OWASP File Upload Security](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [File Type Validation](https://github.com/sindresorhus/file-type)

---

**Last Updated:** 2025-10-07  
**Next Review:** 2026-04-07
