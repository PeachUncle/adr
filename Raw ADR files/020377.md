# ADR-0004: Flask-React Integration Strategy

**Status:** Accepted  
**Date:** 2025-11-26  
**Supersedes:** None  
**Superseded By:** N/A

---

## Context

We needed to determine how Flask backend and React frontend would integrate and communicate in both development and production environments. Key considerations included:

- Development workflow efficiency (fast iteration, easy debugging)
- CORS handling for local development
- Production deployment simplicity
- Authentication strategy
- Hot module replacement for frontend
- API versioning approach
- Error handling patterns

Requirements:
- Excellent developer experience (fast reload, clear errors)
- Simple deployment for single-user local app
- Independent development of frontend and backend
- Prepare for future authentication needs

## Decision

We will use **separate servers in development** (Vite proxy) and **Flask serves React build in production**, with **JWT authentication deferred to post-MVP**.

### Core Integration Strategy:

1. **Development Environment: Separate Servers**
   ```
   Frontend: Vite dev server on localhost:5173
   Backend: Flask API on localhost:5000
   Communication: Vite proxy forwards /api/* to Flask
   ```

2. **Production Environment: Single Server**
   ```
   Flask serves:
   - Static files from React build (dist/)
   - API routes under /api/*
   - Catch-all route returns index.html (for React routing)
   ```

3. **CORS Handling**
   - **Development:** Vite proxy handles CORS (no Flask-CORS needed)
   - **Production:** Same-origin (no CORS issues)
   - **Fallback:** Flask-CORS configured for localhost:5173 if proxy insufficient

4. **API Communication: Axios with Interceptors**
   ```javascript
   // Frontend: Centralized API client
   const api = axios.create({
     baseURL: '/api',  // Works in both dev (proxy) and prod (same origin)
     timeout: 10000
   })
   
   // Request interceptor (for future auth)
   api.interceptors.request.use(config => {
     const token = localStorage.getItem('token')
     if (token) config.headers.Authorization = `Bearer ${token}`
     return config
   })
   ```

5. **Authentication: Deferred to Post-MVP**
   - MVP: Open API (no authentication)
   - Future: JWT tokens with Flask-JWT-Extended
   - Already architected in (interceptors ready)
   - Single-user local app reduces urgency

6. **Error Handling: Consistent Format**
   ```json
   {
     "error": "Error Type",
     "message": "Human-readable description"
   }
   ```

### Configuration:

**Vite Config (Development):**
```javascript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

**Flask Config (Production):**
```python
app = Flask(
    __name__,
    static_folder='../frontend/dist',
    static_url_path=''
)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
```

## Consequences

### Positive

- **Development Experience**: Separate servers enable fast HMR and independent debugging
- **Simplicity**: Vite proxy eliminates complex CORS configuration
- **Flexibility**: Can develop frontend or backend independently
- **Production Simplicity**: Single Flask server serves everything; easy to deploy
- **Clean Separation**: Frontend and backend are truly independent
- **Standard Practice**: Industry-standard approach for Flask + React
- **Future-Proof**: Authentication architecture ready when needed
- **Error Clarity**: Consistent error format aids debugging
- **Local-First**: Single server deployment perfect for desktop app

### Negative

- **Two Servers in Dev**: Must run both Flask and Vite during development
- **Port Management**: Need to manage two ports (5173, 5000)
- **Proxy Configuration**: Need to understand Vite proxy setup
- **Build Step Required**: Must build React before production deployment
- **CORS Complexity (if proxy fails)**: May need Flask-CORS as fallback

**Mitigation:**
- Simple start script can launch both servers
- Ports are standard conventions (well-documented)
- Vite proxy is straightforward configuration
- Build step is single command (`npm run build`)
- Flask-CORS is simple fallback if needed

## Alternatives Considered

### Alternative 1: Single Server with Flask Templates

**Description:** Flask renders HTML templates, React embedded in templates

**Pros:**
- Single server in development
- No CORS issues
- Traditional Flask approach

**Cons:**
- Terrible developer experience (no HMR)
- Mixing concerns (templates + React)
- Hard to maintain
- Can't leverage modern build tools
- Defeats purpose of SPA

**Why Not Chosen:** Completely undermines benefits of React. No hot reload makes development painful. Not a viable modern approach.

### Alternative 2: Nginx Reverse Proxy

**Description:** Nginx serves React files and proxies API requests to Flask

**Pros:**
- Production-grade setup
- Excellent performance
- Can scale easily
- Clear separation

**Cons:**
- Overkill for single-user local app
- Requires Nginx installation
- More complex deployment
- Harder for users to run
- Additional configuration management

**Why Not Chosen:** Too complex for local desktop app. Users would need to install and configure Nginx. Flask serving static files sufficient for our use case.

### Alternative 3: Flask-CORS in Development (No Proxy)

**Description:** Configure Flask-CORS, make direct requests from React dev server

**Pros:**
- No proxy configuration needed
- Clear separation of concerns
- Each server fully independent

**Cons:**
- Must configure CORS carefully
- Different URLs in dev vs. prod
- More environment-specific code
- CORS can be finicky to debug

**Why Not Chosen:** Vite proxy is simpler and more standard. Eliminates CORS complexity in development. Matches production URL structure (/api).

### Alternative 4: Authentication in MVP

**Description:** Implement JWT authentication from the start

**Pros:**
- Security from day one
- No need to add later
- Best practice

**Cons:**
- Slows MVP development
- Unnecessary for single-user local app
- Adds complexity to testing
- User doesn't need it yet

**Why Not Chosen:** Over-engineering for MVP. Single-user local app doesn't need authentication initially. Can add easily post-MVP (architecture supports it).

## Implementation Notes

1. **Development Workflow:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   flask run
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Start Script (Optional):**
   ```bash
   #!/bin/bash
   # scripts/dev.sh
   cd backend && flask run &
   cd frontend && npm run dev
   ```

3. **Environment Variables:**
   ```bash
   # frontend/.env.development
   VITE_API_URL=http://localhost:5000/api
   
   # frontend/.env.production
   VITE_API_URL=/api
   ```

4. **Production Build:**
   ```bash
   cd frontend
   npm run build
   # Creates frontend/dist/
   
   # Flask automatically serves from dist/ folder
   ```

5. **Future JWT Implementation:**
   ```python
   # Flask setup
   app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
   jwt = JWTManager(app)
   
   @auth_bp.route('/login', methods=['POST'])
   def login():
       access_token = create_access_token(identity={'id': user.id})
       return jsonify(access_token=access_token)
   
   @protected_route.route('/data')
   @jwt_required()
   def protected():
       current_user = get_jwt_identity()
       # ...
   ```

## References

- [Flask-React Integration Research](../research/tech-stack/flask-react-integration.md) - Comprehensive analysis (600+ lines)
- [Vite Proxy Documentation](https://vitejs.dev/config/server-options.html#server-proxy)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)
- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)

## Related ADRs

- **ADR-0001:** Flask Backend Architecture - Backend architecture using this integration strategy
- **ADR-0002:** React Frontend Architecture - Frontend architecture using this integration strategy
- **ADR-0003:** SQLite Database Design - Database layer accessed via this integration
- **ADR-0005:** Projects as Foundation Architecture - Feature architecture leveraging this integration approach

---

**Last Updated:** 2025-11-26  
**Status:** ✅ Accepted and Active





