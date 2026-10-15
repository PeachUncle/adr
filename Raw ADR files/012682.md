# ADR 005: OEM White-Labeling and Branding System

**Date**: 2025-10-03  
**Status**: ✅ Implemented  
**Decision Makers**: Development Team, Product Management  
**Related Documents**: `/docs/user-guide/`, OEM Customization Implementation

---

## Context

Network Optix partners and resellers need the ability to customize the Nx System Calculator with their own branding for customer-facing proposals and reports. This white-labeling capability is essential for:

- **OEM Partners**: Reselling under their own brand
- **System Integrators**: Professional proposals with their branding
- **Enterprise Customers**: Internal branding for corporate standards
- **Regional Distributors**: Localized branding

The system must support customization without code changes and maintain brand consistency across all customer touchpoints.

---

## Decision

We will implement a comprehensive OEM white-labeling system with the following capabilities:

### Customizable Elements

1. **Visual Branding**
   - Company logo upload (PNG, JPG, SVG)
   - Primary brand color (hex code)
   - Secondary color (optional)
   - Custom favicon

2. **Company Information**
   - Company name
   - Contact email
   - Phone number
   - Website URL
   - Physical address

3. **Document Customization**
   - Custom disclaimers
   - Terms and conditions
   - Footer text
   - Copyright notice

4. **Email Branding**
   - Logo in email header
   - Brand colors in email template
   - Custom signature
   - Contact information

---

## Architecture

### Storage Strategy

**Logo Files:**
- Upload to `/uploads/logos/` directory
- Filename format: `logo_[timestamp]_[hash].[ext]`
- Serve via static file endpoint: `/uploads/logos/[filename]`
- Maximum file size: 5 MB
- Supported formats: PNG, JPG, JPEG, SVG, GIF

**Branding Configuration:**
- Store in database (SQLite/PostgreSQL)
- Per-user or global configuration
- JSON schema for validation
- API endpoints for CRUD operations

### Database Schema

```sql
CREATE TABLE branding_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  -- NULL for global config
    company_name VARCHAR(255),
    logo_url VARCHAR(500),
    primary_color VARCHAR(7),  -- Hex color
    secondary_color VARCHAR(7),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    website_url VARCHAR(500),
    address TEXT,
    disclaimer TEXT,
    footer_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints

```python
# Upload logo
POST /api/v1/branding/upload-logo
Content-Type: multipart/form-data
Body: file (image file)

Response:
{
  "logo_url": "/uploads/logos/logo_1234567890_abc123.png",
  "filename": "company-logo.png",
  "size_bytes": 45678
}

# Save branding configuration
POST /api/v1/branding/config
Content-Type: application/json
Body:
{
  "company_name": "Acme Security Solutions",
  "logo_url": "/uploads/logos/logo_1234567890_abc123.png",
  "primary_color": "#0066CC",
  "contact_email": "info@acmesecurity.com",
  "website_url": "https://www.acmesecurity.com"
}

# Get branding configuration
GET /api/v1/branding/config

# Update branding configuration
PUT /api/v1/branding/config/{id}

# Delete branding configuration
DELETE /api/v1/branding/config/{id}
```

---

## Implementation Details

### Logo Upload Validation

```python
# app/api/branding.py

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".svg"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_logo(file: UploadFile) -> None:
    """Validate uploaded logo file."""
    
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    
    # Validate image format (optional)
    try:
        from PIL import Image
        image = Image.open(file.file)
        image.verify()
        file.file.seek(0)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )
```

### PDF Report Branding

```python
# app/services/pdf/report_generator.py

def generate_branded_report(
    calculation_data: CalculationRequest,
    results: CalculationResults,
    branding: Optional[BrandingConfig] = None
) -> bytes:
    """Generate PDF report with custom branding."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Header with logo
    if branding and branding.logo_url:
        logo_path = get_logo_path(branding.logo_url)
        logo = Image(logo_path, width=2*inch, height=0.67*inch)
        story.append(logo)
    else:
        # Default Network Optix logo
        story.append(default_logo())
    
    # Company name
    company_name = branding.company_name if branding else "Network Optix"
    story.append(Paragraph(
        company_name,
        ParagraphStyle(
            'CompanyName',
            fontSize=24,
            textColor=colors.HexColor(branding.primary_color if branding else '#0066CC')
        )
    ))
    
    # Report content...
    
    # Footer with custom text
    footer_text = branding.footer_text if branding else default_footer()
    story.append(Paragraph(footer_text, footer_style))
    
    doc.build(story)
    return buffer.getvalue()
```

### Email Template Branding

```html
<!-- app/services/email/templates/report_email.html -->

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff;">
                    <!-- Header with logo -->
                    <tr>
                        <td align="center" style="padding: 30px; background-color: {{ primary_color }};">
                            {% if logo_url %}
                            <img src="{{ logo_url }}" alt="{{ company_name }}" style="max-width: 200px; height: auto;">
                            {% else %}
                            <h1 style="color: #ffffff; margin: 0;">{{ company_name }}</h1>
                            {% endif %}
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="color: {{ primary_color }};">Your System Calculation Report</h2>
                            <p>Dear {{ recipient_name }},</p>
                            <p>Thank you for using the Nx System Calculator. Please find attached your detailed system calculation report for <strong>{{ project_name }}</strong>.</p>
                            <!-- More content... -->
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px; background-color: #f4f4f4; text-align: center;">
                            <p style="margin: 0; color: #666;">{{ company_name }}</p>
                            <p style="margin: 5px 0; color: #666;">{{ contact_email }} | {{ website_url }}</p>
                            <p style="margin: 5px 0; color: #999; font-size: 12px;">{{ footer_text }}</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
```

---

## Rationale

### Why file-based logo storage?

**Advantages:**
- ✅ Simple implementation
- ✅ Fast serving via static files
- ✅ Easy backup and migration
- ✅ No database bloat

**Alternatives considered:**
- Database BLOB storage (rejected: slower, database bloat)
- Cloud storage (S3, Azure Blob) (future enhancement)

### Why database for branding config?

**Advantages:**
- ✅ Structured data with validation
- ✅ Easy querying and updates
- ✅ Relational integrity
- ✅ Multi-user support

### Why hex colors instead of RGB?

**Advantages:**
- ✅ Web standard format
- ✅ Compact representation
- ✅ Easy validation
- ✅ Direct use in CSS/HTML

---

## Security Considerations

### File Upload Security

1. **File Type Validation**
   - Whitelist allowed extensions
   - Verify file content (magic bytes)
   - Reject executable files

2. **File Size Limits**
   - Maximum 5 MB per file
   - Prevent disk space exhaustion

3. **Filename Sanitization**
   - Generate unique filenames
   - Remove special characters
   - Prevent path traversal

4. **Storage Isolation**
   - Dedicated upload directory
   - No execute permissions
   - Separate from application code

### Access Control

- Logo files publicly accessible (needed for emails)
- Branding config requires authentication (future)
- Admin-only branding management (future)

---

## User Experience

### Frontend UI

**Branding Settings Page:**
```
┌─────────────────────────────────────┐
│  OEM Branding Configuration         │
├─────────────────────────────────────┤
│                                     │
│  Company Logo                       │
│  ┌─────────────────┐                │
│  │  [Upload Logo]  │                │
│  └─────────────────┘                │
│  Supported: PNG, JPG, SVG (max 5MB) │
│                                     │
│  Company Name                       │
│  [Acme Security Solutions        ]  │
│                                     │
│  Primary Brand Color                │
│  [#0066CC] ■                        │
│                                     │
│  Contact Email                      │
│  [info@acmesecurity.com         ]   │
│                                     │
│  Website URL                        │
│  [https://www.acmesecurity.com  ]   │
│                                     │
│  Custom Disclaimer (optional)       │
│  [                               ]  │
│  [                               ]  │
│                                     │
│  [Save Configuration]               │
│                                     │
└─────────────────────────────────────┘
```

---

## Testing Strategy

### Unit Tests

```python
def test_logo_upload_valid():
    """Test valid logo upload."""
    with open('test_logo.png', 'rb') as f:
        response = client.post(
            '/api/v1/branding/upload-logo',
            files={'file': ('logo.png', f, 'image/png')}
        )
    assert response.status_code == 200
    assert 'logo_url' in response.json()

def test_logo_upload_invalid_type():
    """Test invalid file type rejection."""
    with open('test.exe', 'rb') as f:
        response = client.post(
            '/api/v1/branding/upload-logo',
            files={'file': ('malware.exe', f, 'application/x-msdownload')}
        )
    assert response.status_code == 400

def test_branding_config_save():
    """Test saving branding configuration."""
    config = {
        'company_name': 'Test Company',
        'primary_color': '#FF0000',
        'contact_email': 'test@example.com'
    }
    response = client.post('/api/v1/branding/config', json=config)
    assert response.status_code == 200
```

---

## Future Enhancements

1. **Multi-tenant Support**
   - Per-user branding configurations
   - Role-based access control
   - Branding templates library

2. **Advanced Customization**
   - Custom CSS injection
   - Multiple logo variants (light/dark)
   - Font customization
   - Layout templates

3. **Cloud Storage Integration**
   - S3/Azure Blob for logos
   - CDN for faster delivery
   - Automatic image optimization

4. **Branding Preview**
   - Live preview of branded reports
   - Email template preview
   - Before/after comparison

---

## Success Metrics

- Logo upload success rate > 99%
- Average branding setup time < 5 minutes
- Partner satisfaction with customization options
- Reduction in custom deployment requests

---

## References

- [OWASP File Upload Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [Email Template Best Practices](https://www.campaignmonitor.com/dev-resources/)

---

## Approval

**Approved by**: Development Team, Product Management  
**Implementation Date**: 2025-10-03  
**Review Date**: 2026-01-03 (Quarterly review)

