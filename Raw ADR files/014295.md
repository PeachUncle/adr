# ADR-004: Security Implementation and Authentication Strategy

## Status
**ACCEPTED** - 2025-09-11

## Context
We need to implement a comprehensive security strategy for the Pokedex API, including authentication, authorization, data protection, and security best practices. This is critical for protecting user data and ensuring system integrity.

## Decision
We will implement a multi-layered security approach using industry-standard practices:

### **Authentication Strategy**
- **JWT (JSON Web Tokens)**: Stateless authentication
- **Dual Token System**: Access tokens (short-lived) + Refresh tokens (long-lived)
- **Password Security**: bcrypt hashing with salt
- **Token Rotation**: Refresh token rotation on use

### **Authorization Strategy**
- **Role-Based Access Control (RBAC)**: Admin vs Regular users
- **Resource-Based Permissions**: Fine-grained access control
- **Protected Endpoints**: Authentication required for sensitive operations
- **Admin-Only Operations**: Elevated permissions for administrative tasks

### **Data Protection Strategy**
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: Parameterized queries only
- **XSS Prevention**: Input sanitization and output encoding
- **CSRF Protection**: CSRF tokens for state-changing operations

## Authentication Implementation

### **JWT Token System**
```python
# Token Configuration
ACCESS_TOKEN_EXPIRES = timedelta(hours=1)      # Short-lived
REFRESH_TOKEN_EXPIRES = timedelta(days=30)     # Long-lived
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_ALGORITHM = 'HS256'
```

### **Token Structure**
```json
{
  "sub": "user_id",           // Subject (user ID)
  "iat": 1640995200,          // Issued at
  "exp": 1640998800,          // Expires at
  "type": "access",           // Token type
  "role": "user"              // User role
}
```

### **Authentication Flow**
1. **User Registration**: Create account with hashed password
2. **User Login**: Validate credentials, issue tokens
3. **Token Usage**: Include access token in Authorization header
4. **Token Refresh**: Use refresh token to get new access token
5. **Token Logout**: Invalidate refresh token

### **Password Security**
```python
# Password Hashing with bcrypt
def set_password(self, password):
    salt = bcrypt.gensalt()
    self.password_hash = bcrypt.hashpw(
        password.encode('utf-8'), 
        salt
    ).decode('utf-8')

def check_password(self, password):
    return bcrypt.checkpw(
        password.encode('utf-8'),
        self.password_hash.encode('utf-8')
    )
```

## Authorization Implementation

### **Role-Based Access Control**
```python
# User Roles
class UserRole:
    REGULAR = "user"
    ADMIN = "admin"

# Permission Levels
class Permission:
    READ_POKEMON = "read:pokemon"
    WRITE_POKEMON = "write:pokemon"
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    ADMIN_ACCESS = "admin:access"
```

### **Protected Endpoints**
```python
# Public Endpoints (No Authentication)
GET  /api/v1/pokemon
GET  /api/v1/pokemon/{id}
POST /api/v1/auth/register
POST /api/v1/auth/login

# Protected Endpoints (Authentication Required)
GET    /api/v1/auth/profile
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/users/{id}/favorites
POST   /api/v1/users/{id}/favorites
DELETE /api/v1/users/{id}/favorites/{pokemon_id}

# Admin Endpoints (Admin Role Required)
POST   /api/v1/pokemon
PUT    /api/v1/pokemon/{id}
DELETE /api/v1/pokemon/{id}
GET    /api/v1/users
DELETE /api/v1/users/{id}
```

### **Authorization Decorators**
```python
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin access required'}, 403
        return f(*args, **kwargs)
    return decorated_function
```

## Input Validation and Sanitization

### **Request Validation**
```python
# Using Flask-RESTful reqparse
parser = reqparse.RequestParser()
parser.add_argument('username', required=True, type=str, help='Username is required')
parser.add_argument('email', required=True, type=email, help='Valid email is required')
parser.add_argument('password', required=True, type=str, min_length=8, help='Password must be at least 8 characters')

# Validation Rules
VALIDATION_RULES = {
    'username': {
        'type': str,
        'min_length': 3,
        'max_length': 80,
        'pattern': r'^[a-zA-Z0-9_]+$'
    },
    'email': {
        'type': str,
        'pattern': r'^[^@]+@[^@]+\.[^@]+$'
    },
    'password': {
        'type': str,
        'min_length': 8,
        'max_length': 128
    }
}
```

### **SQL Injection Prevention**
```python
# Use SQLAlchemy ORM (prevents SQL injection)
user = User.query.filter_by(username=username).first()

# Parameterized queries for raw SQL
db.session.execute(
    "SELECT * FROM users WHERE username = :username",
    {"username": username}
)
```

### **XSS Prevention**
```python
# Input sanitization
import bleach

def sanitize_input(text):
    return bleach.clean(text, tags=[], strip=True)

# Output encoding
from markupsafe import escape
safe_output = escape(user_input)
```

## Security Headers

### **HTTP Security Headers**
```python
# Security headers middleware
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

### **CORS Configuration**
```python
# CORS settings
CORS(app, origins=[
    'http://localhost:3000',  # React dev server
    'https://pokedex.example.com'  # Production domain
])
```

## Rate Limiting and DDoS Protection

### **Rate Limiting Strategy**
```python
# Rate limiting configuration
RATE_LIMITS = {
    'auth': '5 per minute',      # Authentication endpoints
    'api': '100 per minute',     # General API endpoints
    'admin': '1000 per minute'   # Admin endpoints
}

# Implementation with Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)
```

### **Endpoint-Specific Limits**
```python
@limiter.limit("5 per minute")
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    # Login endpoint with strict rate limiting
    pass

@limiter.limit("100 per minute")
@app.route('/api/v1/pokemon', methods=['GET'])
def get_pokemon():
    # Pokemon list with standard rate limiting
    pass
```

## Data Encryption and Storage

### **Sensitive Data Encryption**
```python
# Environment variables for secrets
import os
from cryptography.fernet import Fernet

# Encrypt sensitive data at rest
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
```

### **Database Security**
```python
# Database connection security
DATABASE_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'sslmode': 'require'  # Force SSL connection
}
```

## Logging and Monitoring

### **Security Event Logging**
```python
import logging
from datetime import datetime

# Security logger
security_logger = logging.getLogger('security')

def log_security_event(event_type, user_id, details):
    security_logger.warning({
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'details': details,
        'ip_address': request.remote_addr
    })

# Log security events
log_security_event('LOGIN_FAILED', None, {'username': username})
log_security_event('UNAUTHORIZED_ACCESS', user_id, {'endpoint': request.endpoint})
log_security_event('ADMIN_ACTION', user_id, {'action': 'user_deleted'})
```

### **Audit Trail**
```python
# Track sensitive operations
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    details = db.Column(db.JSON)
```

## Error Handling and Information Disclosure

### **Secure Error Responses**
```python
# Don't expose internal details
@app.errorhandler(500)
def internal_error(error):
    return {
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An internal error occurred'
        }
    }, 500

# Log detailed errors server-side
logger.error(f"Internal error: {str(error)}", exc_info=True)
```

### **Input Validation Errors**
```python
# Return validation errors without exposing system details
def handle_validation_error(errors):
    return {
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid input data',
            'details': [
                {'field': field, 'message': message}
                for field, message in errors.items()
            ]
        }
    }, 422
```

## Security Testing

### **Automated Security Tests**
```python
# Security test cases
def test_sql_injection_protection():
    response = client.post('/api/v1/auth/login', json={
        'username': "admin'; DROP TABLE users; --",
        'password': 'password'
    })
    assert response.status_code == 401

def test_xss_protection():
    response = client.post('/api/v1/auth/register', json={
        'username': '<script>alert("xss")</script>',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert '<script>' not in response.get_json()['user']['username']

def test_authentication_required():
    response = client.get('/api/v1/auth/profile')
    assert response.status_code == 401
```

## Implementation Status

### **✅ Implemented (Option B Complete)**
- **JWT Authentication**: Access and refresh tokens working
- **Password Hashing**: bcrypt with salt implemented
- **Role-Based Access**: Admin vs regular user permissions
- **Protected Endpoints**: Authentication required for sensitive operations
- **Input Validation**: Comprehensive request validation with rules
- **SQL Injection Prevention**: SQLAlchemy ORM usage
- **Error Handling**: Standardized error responses with HTTP status codes
- **Rate Limiting**: Flask-Limiter with per-endpoint limits (5/min auth, 100/min API, 1000/min admin)
- **Security Headers**: Complete implementation (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP, etc.)
- **CORS Configuration**: Properly configured for React dev and production
- **Audit Logging**: Full AuditLog model with comprehensive tracking
- **Security Monitoring**: Request logging, security event tracking
- **Input Sanitization**: XSS prevention and data validation

### **⏳ Pending (Future Enhancements)**
- **Two-Factor Authentication (2FA)**: TOTP or SMS-based 2FA
- **OAuth2 Integration**: Social login options
- **API Key Management**: For third-party integrations
- **Penetration Testing**: Security vulnerability assessment
- **SSL/TLS**: HTTPS configuration for production
- **Advanced Security Monitoring**: Automated security alerts

## Security Checklist

### **Authentication & Authorization**
- [x] JWT token implementation
- [x] Password hashing with bcrypt
- [x] Role-based access control
- [x] Protected endpoint enforcement
- [x] Token expiration handling
- [x] Refresh token rotation

### **Input Validation & Sanitization**
- [x] Request validation
- [x] SQL injection prevention
- [x] XSS prevention
- [x] Input sanitization
- [x] Output encoding

### **Security Headers & CORS**
- [x] CORS configuration
- [x] Security headers implementation
- [x] Content Security Policy
- [x] X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- [ ] HTTPS enforcement (production)

### **Monitoring & Logging**
- [x] Security event logging
- [x] Error handling
- [x] Audit trail implementation
- [x] Security monitoring
- [x] Request tracking with unique IDs

## Future Security Enhancements

### **Advanced Security Features**
- **Two-Factor Authentication (2FA)**: TOTP or SMS-based 2FA
- **OAuth2 Integration**: Social login options
- **API Key Management**: For third-party integrations
- **Webhook Security**: Signed webhook payloads
- **Security Scanning**: Automated vulnerability scanning

### **Compliance Considerations**
- **GDPR Compliance**: Data protection and privacy
- **SOC 2**: Security controls and monitoring
- **OWASP Top 10**: Address common vulnerabilities
- **Security Audits**: Regular security assessments

## Review
This ADR will be reviewed after security implementation to ensure all security measures are properly implemented and tested.

## Related ADRs
- **ADR-001**: Technology Stack Selection
- **ADR-002**: Database Design and Schema Decisions
- **ADR-003**: API Design Patterns and Versioning Strategy

---

**Last Updated**: 2025-09-11  
**Status**: ACCEPTED  
**Next Review**: After security testing completion
