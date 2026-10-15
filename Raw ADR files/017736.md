# Logger Module Description

- Status: Accepted
- Date: 2025-05-25
- Tags: logging, infrastructure, modularity, debugging, mysql, semantic analysis, user context, mvp-ready, extensible

## Context

SPLit is an analytical application composed of multiple interacting modules, each performing specific tasks — from data ingestion to advanced analysis. Logging is critical both for debugging and for stable system operation. The system requires a centralized, flexible, and extensible logging mechanism suitable for local development and future scaling.

## Decision

A logging module has been designed and approved to meet the following architectural requirements:

### 📄 Format and Output
- ✅ Colored log output in terminal
- ✅ All logs at level DEBUG+ are written to the file logs/split.log
- ✅ Log format: [YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] [user=USER] message
- ⛰️ Log file rotation by size (e.g., 5MB, 5 backup files)
- ❌ JSON logging is not required

### 🧱 Modularity and Initialization
- ✅ Usage of get_logger("module_name")
- ✅ Each module initializes its logger independently
- ✅ Logger settings (paths, levels, flags) are centralized in config.py
- ⛰️ Stub emit_semantic() included for future integration with semantic_log_analyzer

### 🔐 MySQL Logging
- ✅ Uses database split_logs, table logs
- ✅ Connection attempts up to 3 times; on failure, logs are written to file/terminal
- ✅ Reconnection attempts every 10 minutes
- ✅ All modules log to MySQL without source filtering
- ✅ Only logs with levels WARNING+ are written to the database

### 👤 User Context

- ✅ All logs include user_id (default: "user_zero")
- ⛰️ Globally set via set_user() during module startup
- ⛰️ Filtering by user_id is reserved for future implementation

### 🧠 Architectural Extensions
- ⛰️ Support for extra={...} for structured logging
- ⛰️ Support for session_id / run_id to link logs within a single analysis session
- ⛰️ Integration with semantic log analysis module via API or message queue

### Exclusions

- ❌ Integration with external logging services (Sentry, ELK)
- ❌ Web-based logging configuration interface
- ❌ Role-based logging permissions or subscriptions

## Conclusion

The logging module is designed as a universal component, scalable and suitable for both development and production. It supports future enhancements for semantic analysis, user context tracking, and session linkage, without overcomplicating the architecture. This decision ensures the logging subsystem remains transparent, reliable, and modular — independent of any external platforms.

Logger Module Description