# ADR-005: Technology Stack Selection

## Revision Log
| Date | Description |
|------|-------------|
| 2025-12-10 | Document created |
| 2025-12-11 | Added ADR-007 as spoke document |

## Context
Weight Stock Platform 2.0 requires a comprehensive technology stack for frontend user interface, backend API services, and data persistence. The stack must support privacy-preserving price calculations, session management, time-series analytics, and role-based access control.

## Decision
We use a modern web application stack with clear separation of concerns:

**Frontend Stack:**
- React 18+ for component-based UI development
- Vite for fast development and optimized production builds
- Material-UI (MUI) for consistent design components
- Coinbase Design System for financial UI patterns
- React i18n for internationalization support
- Axios for HTTP client with cookie-based authentication

**Backend Stack:**
- Flask 3+ as lightweight Python web framework
- Flask-Session for server-side session management
- SQLAlchemy as ORM for database abstraction
- pandas for time-series data analysis and moving averages
- Werkzeug for security utilities (password hashing)

**Database:**
- MySQL 8.0+ with InnoDB storage engine
- UTF8MB4 character set for full Unicode support
- Indexed timestamp columns for time-series queries

**Project Structure:**
- frontend/ directory for React application
- backend/ directory for Flask application
- Separate development servers with CORS configuration

## Consequences

### Benefits
- React ecosystem provides mature component libraries and tooling
- Vite offers significantly faster builds than webpack-based solutions
- Flask's simplicity suits medium-complexity API requirements
- pandas excels at time-series calculations for financial data
- MySQL provides ACID compliance for transactional integrity
- Clear frontend/backend separation enables independent scaling
- Coinbase Design System accelerates financial UI development

### Tradeoffs
- Python backend may have lower raw performance than Go/Rust alternatives
- SQLAlchemy ORM adds abstraction overhead vs raw SQL
- Separate frontend/backend requires CORS configuration
- pandas memory usage can be high for large datasets
- MySQL vertical scaling more complex than PostgreSQL
- Multiple technology stacks increase learning curve for new developers

## Implementation
1. Initialize frontend project using Vite React template
2. Install MUI, Coinbase Design System, i18n, and Axios dependencies
3. Initialize Flask backend with virtual environment
4. Configure Flask-Session with Redis or database backend
5. Set up SQLAlchemy models for User, PriceRecord, and related tables
6. Install pandas for data analysis capabilities
7. Provision MySQL 8.0+ database with UTF8MB4 charset
8. Configure development CORS settings for frontend-backend communication
9. Implement build and deployment pipelines for both frontend and backend

## Related Decisions
- **Hub document for**: ADR-001 (Client-Side Price Calculation), ADR-002 (Session-Based Authentication), ADR-003 (Server-Side Moving Average Calculation), ADR-004 (Immutable User Roles), ADR-007 (Trading Features Implementation)

## Future Considerations
Evaluate TypeScript adoption for frontend to improve type safety and developer experience. Consider PostgreSQL migration if advanced JSON query capabilities or superior scaling becomes critical.

## Appendix: Project Directory Structure

```
ClaudeCodeDemo/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WeightInput.jsx
│   │   │   ├── PriceChart.jsx
│   │   │   ├── RegistrationForm.jsx
│   │   │   └── LoginForm.jsx
│   │   ├── services/
│   │   │   └── authService.js
│   │   ├── i18n/
│   │   │   ├── en.json
│   │   │   └── zh.json
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── backend/
│   ├── api/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── chart.py
│   │   └── price.py
│   ├── models/
│   │   ├── user.py
│   │   └── price_record.py
│   ├── services/
│   │   └── chart_service.py
│   ├── app.py
│   ├── requirements.txt
│   └── config.py
└── docs/
    └── adr/
        ├── ADR-001-client-side-price-calculation.md
        ├── ADR-002-session-based-authentication.md
        ├── ADR-003-server-side-moving-average-calculation.md
        ├── ADR-004-immutable-user-roles.md
        └── ADR-005-technology-stack-selection.md
```

## Appendix: Frontend Dependencies

```json
// frontend/package.json
{
  "name": "weight-stock-platform-frontend",
  "version": "2.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@mui/material": "^5.14.20",
    "@mui/icons-material": "^5.14.19",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@coinbase/wallet-sdk": "^3.9.0",
    "react-i18next": "^13.5.0",
    "i18next": "^23.7.6",
    "axios": "^1.6.2",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
```

## Appendix: Backend Dependencies

```python
# backend/requirements.txt
Flask==3.0.0
Flask-Session==0.5.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
SQLAlchemy==2.0.23
pandas==2.1.4
numpy==1.26.2
Werkzeug==3.0.1
PyMySQL==1.1.0
redis==5.0.1
python-dotenv==1.0.0
```

## Appendix: Vite Configuration

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Proxy API requests to Flask backend during development
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

## Appendix: Flask Application Configuration

```python
# backend/config.py
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost:3306/weight_stock_platform?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'wsp:'
    SESSION_REDIS = os.environ.get('REDIS_URL') or 'redis://localhost:6379'

    # Cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

## Appendix: Database Schema

```sql
-- MySQL 8.0+ Schema for Weight Stock Platform 2.0

CREATE DATABASE IF NOT EXISTS weight_stock_platform
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE weight_stock_platform;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('buyer', 'seller', 'trader') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Price records table (weight never stored)
CREATE TABLE price_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Session storage (if using database backend instead of Redis)
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    session_data BLOB,
    expiration TIMESTAMP NOT NULL,
    INDEX idx_expiration (expiration)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
