# ADR-002: Session-Based Authentication

## Revision Log
| Date | Description |
|------|-------------|
| 2025-12-10 | Document created |
| 2025-12-10 | Consolidated by ADR-005 |
| 2025-12-11 | Extended by ADR-006 |
| 2025-12-11 | Depended on by ADR-007 |

## Part of: ADR-005 (Technology Stack Selection)

## Context
The PRD requires persistent login state management for the Weight Stock Platform 2.0. The system needs secure authentication that allows server-side session control and protection against XSS attacks.

## Decision
We use Flask-Session with HttpOnly cookies for session-based authentication. Session data is stored server-side with secure cookie-based session identifiers.

## Consequences

### Benefits
- Sessions can be revoked immediately on the server side (logout, security breach)
- HttpOnly cookie flag prevents JavaScript access, mitigating XSS session theft
- Server maintains full control over session lifecycle and validation
- Stateful sessions simplify authorization checks without token parsing
- No cryptographic signature verification overhead on each request

### Tradeoffs
- Server must maintain session storage (memory, Redis, or database)
- Frontend cannot directly read user information from session token
- Horizontal scaling requires shared session store configuration
- Session data consumes server memory or storage resources
- CORS configuration more complex than stateless JWT approach

## Implementation
1. Install Flask-Session extension and configure session backend
2. Set session cookie with HttpOnly, Secure, and SameSite attributes
3. Implement login endpoint to create session after credential verification
4. Store user_id and role in server-side session object
5. Implement logout endpoint to destroy session
6. Configure session timeout and cleanup mechanism

## Related Decisions
- **Consolidated by**: ADR-005 - Technology Stack Selection
- **Depended on by**: ADR-004 - Immutable User Roles (role stored in session)
- **Depended on by**: ADR-007 - Trading Features Implementation (trading requires authenticated sessions)
- **Extended by**: ADR-006 - Production Bug Fixes (authentication reliability enhancements)

## Future Considerations
Evaluate Redis-backed session storage for production deployment to support horizontal scaling and session persistence across server restarts.

## Appendix: Flask-Session Configuration

```python
# backend/app.py
from flask import Flask, session
from flask_session import Session
import redis

app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Use environment variable in production
app.config['SESSION_TYPE'] = 'redis'  # Options: redis, memcached, filesystem, sqlalchemy
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # Sign session cookie for integrity
app.config['SESSION_KEY_PREFIX'] = 'wsp:'  # Weight Stock Platform prefix
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

# Cookie security settings
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SECURE'] = True    # HTTPS only (disable in dev)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # CSRF protection

# Initialize session
Session(app)
```

## Appendix: Authentication Endpoints

```python
# backend/api/auth.py
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Authenticate user and create server-side session.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        # Create server-side session
        session['user_id'] = user.id
        session['role'] = user.role
        session['username'] = user.username

        return jsonify({
            'status': 'success',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    Destroy server-side session.
    """
    session.clear()
    return jsonify({'status': 'logged out'}), 200

@auth_bp.route('/api/auth/session', methods=['GET'])
def get_session():
    """
    Retrieve current session information.
    """
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 401
```

## Appendix: Frontend Session Management

```javascript
// frontend/src/services/authService.js
import axios from 'axios';

const API_BASE = '/api/auth';

// Axios configuration for session cookies
axios.defaults.withCredentials = true; // Include cookies in requests

export const authService = {
  async login(username, password) {
    const response = await axios.post(`${API_BASE}/login`, {
      username,
      password
    });
    return response.data;
  },

  async logout() {
    const response = await axios.post(`${API_BASE}/logout`);
    return response.data;
  },

  async getSession() {
    // Frontend cannot read HttpOnly cookie directly
    // Must call backend to retrieve session data
    const response = await axios.get(`${API_BASE}/session`);
    return response.data;
  }
};
```
