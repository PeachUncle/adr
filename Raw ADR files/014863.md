# 3. Use Python 3 with pytest, lxml, signxml, and SQLAlchemy Stack

Date: 2025-10-15

## Status

**Partially Superseded** (2025-10-20)

The database-related sections (SQLAlchemy, Alembic, psycopg) were superseded by [ADR-0010](0010-remove-database-dependencies.md). Database functionality resides in the Jux API Server (separate project), not in pytest-jux.

The following sections **remain valid**:
- XML processing stack (lxml, signxml, cryptography)
- pytest integration
- REST API client (requests, pydantic)
- CLI tools and user experience
- Development tools

## Context

The pytest-jux project is a pytest plugin that signs JUnit XML reports and publishes them to a Jux REST API. The implementation requires:

1. **pytest Plugin Architecture**: Integration with pytest's hook system for automated report processing
2. **XML Processing**: JUnit XML parsing, canonicalization (C14N), and manipulation
3. **Cryptographic Operations**: XML digital signatures (XMLDSig) for chain-of-trust verification
4. **Data Modeling**: Consistent representation across SQLite and PostgreSQL
5. **REST API Integration**: HTTP client for report submission
6. **Python Ecosystem**: Compatibility with pytest ecosystem and system administrator workflows

The parent Jux project architecture requires:
- Support for both SQLite (local) and PostgreSQL (distributed) storage
- JUnit XML as the primary data format
- XML signatures for integrity and chain-of-trust
- Integration with pytest test suites used by system administrators

## Decision

We will use **Python 3** with the following core libraries:

### Core Stack

#### XML Processing & Cryptography
- **lxml** (5.x): XML parsing, XPath support, and C14N canonicalization
- **xmlschema** (2.x or 3.x): JUnit XML schema validation
- **signxml** (3.x): High-level XMLDSig signatures built on lxml and cryptography
- **cryptography** (41.x+): Modern cryptographic primitives (RSA, ECDSA key management)

#### Database Layer
- **SQLAlchemy** (2.x): ORM with PostgreSQL and SQLite dialect support
- **alembic** (1.x): Database migrations compatible with both databases
- **psycopg** (3.x): Modern PostgreSQL adapter with binary mode support

#### pytest Integration
- **pytest** (7.x or 8.x): Plugin host and test framework
- **pytest-cov**: Test coverage reporting
- **pytest-mock**: Mocking support for unit tests

#### CLI & User Experience
- **click** (8.x): Clean command-line interfaces
- **rich** (13.x): Beautiful terminal output (tables, progress bars, syntax highlighting)

#### REST API Client
- **requests** (2.x): Simple, reliable HTTP client for Jux API integration
- **pydantic** (2.x): Type-safe data validation for API payloads

#### Development Tools
- **ruff**: Fast Python linter and formatter (replaces black, isort, flake8)
- **mypy**: Static type checking
- **pytest-xdist**: Parallel test execution
- **coverage**: Code coverage measurement

### Technology Rationale

#### Python 3 Selection
**Strengths**:
- Native pytest plugin ecosystem (plugin *is* Python)
- Excellent XML processing libraries (lxml, signxml)
- Rich cryptographic library support
- Strong SQLAlchemy ecosystem for database abstraction
- Familiar to target users (system administrators often use Python for automation)

**Trade-offs**:
- Performance: Slower than Elixir/Rust for high-throughput scenarios
  - *Mitigation*: pytest plugin runs post-test, not performance-critical
- Concurrency: GIL limits parallelism
  - *Mitigation*: Plugin processing is I/O-bound (network, disk), not CPU-bound
- Type Safety: Dynamic typing vs. Elixir/Rust compile-time guarantees
  - *Mitigation*: Use mypy for static type checking, 100% type coverage for crypto code

#### lxml for XML Processing
**Rationale**:
- Fast C-based XML parsing (libxml2/libxslt bindings)
- Native C14N canonicalization support
- XPath 1.0 for JUnit XML querying
- Battle-tested in production environments
- Foundation for signxml

**Alternatives Considered**:
- xml.etree (stdlib): Limited C14N support, no XMLDSig integration
- xmltodict: No canonicalization support, lossy conversion

#### signxml for XML Signatures
**Rationale**:
- High-level XMLDSig API (easier than xmlsec bindings)
- Built on lxml and cryptography (consistent stack)
- Active maintenance and security updates
- Pythonic API suitable for pytest plugin context

**Alternatives Considered**:
- xmlsec (python-xmlsec): Complete XMLDSig/XMLEnc but harder installation, less Pythonic
- Custom implementation: High security risk, not recommended

#### SQLAlchemy for Database Abstraction
**Rationale**:
- Single ORM for both SQLite and PostgreSQL
- Mature dialect system handles database differences
- Type mapping (JSON, LargeBinary/BYTEA, ARRAY handling)
- Alembic integration for migrations
- Industry standard for Python database abstraction

**Alternatives Considered**:
- Peewee: Simpler but less feature-complete for PostgreSQL
- Django ORM: Too heavyweight for plugin library
- Raw SQL: Loss of abstraction, manual dialect handling

### Library Version Constraints

```python
# Core dependencies (pyproject.toml or requirements.txt)
python = "^3.11"  # Target stable Debian/Fedora/openSUSE versions
lxml = "^5.0"
xmlschema = "^2.5"  # or "^3.0" when stable
signxml = "^3.2"
cryptography = "^41.0"
sqlalchemy = "^2.0"
alembic = "^1.12"
psycopg = {version = "^3.1", extras = ["binary"]}
pytest = "^7.4 || ^8.0"
click = "^8.1"
rich = "^13.0"
requests = "^2.31"
pydantic = "^2.5"

# Development dependencies
ruff = "^0.1"
mypy = "^1.7"
pytest-cov = "^4.1"
pytest-mock = "^3.12"
pytest-xdist = "^3.5"
coverage = {version = "^7.3", extras = ["toml"]}
```

### Supported Operating Systems
Per project requirements (Document #6):
- Debian 12 and 13
- Latest openSUSE and Fedora releases

Python 3.11+ available in all target distributions.

## Consequences

**Positive:**

- **pytest Integration**: Native plugin development in pytest's native language
- **XML Ecosystem**: Mature, battle-tested XML processing and signature libraries
- **Database Portability**: Single codebase for SQLite and PostgreSQL via SQLAlchemy
- **User Familiarity**: Python already used by target audience (system administrators)
- **Type Safety**: mypy provides static checking for critical crypto code
- **Rapid Development**: Rich library ecosystem accelerates implementation
- **Testing**: pytest tests pytest plugin (dogfooding)

**Negative:**

- **Performance**: Slower than compiled languages for high-volume processing
  - *Acceptable*: Post-test report processing is not performance-critical
- **GIL Limitations**: Parallelism constrained by Global Interpreter Lock
  - *Acceptable*: Plugin is I/O-bound, not CPU-bound
- **Deployment**: Requires Python runtime and dependencies
  - *Mitigated*: Python universally available on target OSes
- **Type Safety**: Runtime checks vs. compile-time guarantees
  - *Mitigated*: mypy static checking + comprehensive test suite

**Security Considerations**:

- **Cryptographic Libraries**: Use well-audited libraries (signxml, cryptography)
- **XML Processing**: lxml's libxml2 has good security track record
- **Dependency Management**: Pin versions, use Dependabot for security updates
- **Code Review**: 100% coverage for cryptographic code paths

## Implementation Notes

### Project Structure
```
pytest-jux/
├── pytest_jux/
│   ├── __init__.py
│   ├── plugin.py          # pytest hooks
│   ├── signer.py          # XML signing (signxml wrapper)
│   ├── canonicalizer.py   # C14N operations
│   ├── api_client.py      # REST API integration
│   ├── models.py          # SQLAlchemy models
│   └── cli.py            # Optional CLI commands
├── tests/
│   ├── test_plugin.py
│   ├── test_signer.py
│   ├── test_canonicalizer.py
│   ├── test_api_client.py
│   └── test_models.py
├── pyproject.toml
├── setup.py
└── README.md
```

### pytest Plugin Entry Point
```python
# pyproject.toml
[project.entry-points.pytest11]
jux_publisher = "pytest_jux.plugin"
```

### Type Checking Strategy
- Use mypy in strict mode for all modules
- 100% type coverage for cryptographic and security-critical code
- Type stubs for lxml, signxml (if needed)

### Testing Strategy
- TDD with pytest (dogfooding)
- Unit tests for all components (>85% coverage)
- Integration tests with real JUnit XML fixtures
- Property-based testing for canonicalization edge cases (hypothesis)
- Mock REST API for testing API client
- Test both SQLite and PostgreSQL dialects

## Related Decisions

- ADR-0001: Record architecture decisions
- ADR-0002: Adopt development best practices (establishes TDD approach)
- ADR-0004: [XML signature format and canonicalization strategy] (future)
- ADR-0005: [REST API protocol and authentication] (future)
- ADR-0006: [Key management and certificate handling] (future)

## References

- lxml documentation: https://lxml.de/
- signxml documentation: https://signxml.readthedocs.io/
- SQLAlchemy documentation: https://docs.sqlalchemy.org/
- pytest plugin documentation: https://docs.pytest.org/en/stable/how-to/writing_plugins.html
- JUnit XML schema: https://github.com/windyroad/JUnit-Schema/blob/master/JUnit.xsd
