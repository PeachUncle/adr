# ADR-0003: Overall Application Architecture

- **Date**: 2025-12-10
- **Status**: Accepted

## Context

The WeighToGo Android application requires a clear architectural foundation to support:
- User authentication and session management
- Local data persistence (SQLite database)
- Weight tracking with CRUD operations
- Goal management and progress tracking
- SMS notifications with runtime permissions
- Offline-first functionality (no server required for v1.0)

**Requirements:**
- Maintainable codebase following industry best practices
- Clear separation of concerns (UI, business logic, data access)
- Testable architecture supporting TDD methodology
- Android platform compatibility (API 28+ to API 36)
- Material Design 3 UI consistency
- Scalable for future features (trends, analytics, cloud sync)

**Constraints:**
- CS 360 course requirements (Java, SQLite, no Room initially)
- Single-user mobile app (no multi-user support in v1.0)
- Limited development time (academic project timeline)
- Must demonstrate professional coding standards

## Decision

We will implement a **Model-View-Controller (MVC)** architecture pattern with the following structure:

### 1. Architecture Pattern: MVC

**Model-View-Controller separation:**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    VIEW     │────▶│ CONTROLLER  │────▶│    MODEL    │
│  (Layouts)  │◀────│ (Activities)│◀────│  (Data +    │
│             │     │             │     │   Logic)    │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Model (Data & Business Logic):**
- `models/` - Plain Old Java Objects (POJOs): User, WeightEntry, GoalWeight, Achievement, UserPreference
- `database/` - Data Access Objects (DAOs): UserDAO, WeightEntryDAO, GoalWeightDAO
- `database/` - Database helper: WeighToGoDBHelper (Singleton pattern)
- `utils/` - Business logic: PasswordUtils, ValidationUtils, DateUtils, AchievementManager

**View (User Interface):**
- `res/layout/` - XML layout files (Material Design 3 components)
- `res/drawable/` - UI resources (backgrounds, icons, gradients)
- `res/values/` - UI configuration (colors, strings, dimensions, themes)

**Controller (User Input & Coordination):**
- `activities/` - Activity classes: LoginActivity, MainActivity, WeightEntryActivity, SMSSettingsActivity
- `adapters/` - RecyclerView adapters: WeightEntryAdapter
- Coordinates between View (layouts) and Model (data/logic)

### 2. Package Structure

```
weightogo/
├── activities/         # Controllers - UI event handling
│   ├── LoginActivity.java
│   ├── MainActivity.java
│   ├── WeightEntryActivity.java
│   └── SMSSettingsActivity.java
├── adapters/           # View helpers - RecyclerView binding
│   └── WeightEntryAdapter.java
├── database/           # Model - Data access layer
│   ├── WeighToGoDBHelper.java
│   ├── UserDAO.java
│   ├── WeightEntryDAO.java
│   └── GoalWeightDAO.java
├── models/             # Model - Domain objects
│   ├── User.java
│   ├── WeightEntry.java
│   ├── GoalWeight.java
│   ├── Achievement.java
│   └── UserPreference.java
├── utils/              # Model - Business logic & helpers
│   ├── PasswordUtils.java
│   ├── ValidationUtils.java
│   ├── SessionManager.java
│   ├── DateTimeConverter.java
│   ├── DateUtils.java
│   ├── BooleanConverter.java
│   ├── SMSNotificationManager.java
│   └── AchievementManager.java
└── constants/          # Shared constants
    └── AppConstants.java
```

**Package Responsibilities:**
- **activities/**: Handle user input, lifecycle events, navigate between screens, coordinate Model-View interaction
- **adapters/**: Bind data to RecyclerView items, handle item click events
- **database/**: Encapsulate all SQL operations, provide clean API for data access
- **models/**: Data structures with getters/setters, no business logic
- **utils/**: Reusable logic (validation, conversion, session management, notifications)
- **constants/**: App-wide constants (database version, shared preferences keys, regex patterns)

### 3. Design Patterns

**Singleton Pattern:**
- `WeighToGoDBHelper` - Single database connection throughout app lifecycle
- `SessionManager` - Single user session instance
- **Benefits**: Thread-safe, prevents multiple database connections, consistent state

**Data Access Object (DAO) Pattern:**
- `UserDAO`, `WeightEntryDAO`, `GoalWeightDAO`
- Abstracts database operations from business logic
- **Benefits**: Testable (can mock DAOs), swappable data sources, clear API

**Observer Pattern (Planned for Phase 2+):**
- `LiveData`-style callbacks for data change notifications
- UI updates when data changes (e.g., weight entry added/deleted)
- **Benefits**: Decoupled UI updates, reactive data flow

**Factory Pattern (Future):**
- Notification factory for different notification types
- Achievement factory for different achievement types

### 4. Technology Stack

**Programming Language:**
- Java 11 (course requirement, Android standard)
- **Chosen over Kotlin**: Course uses Java, team familiarity

**Build System:**
- Gradle 8.13+ with version catalog (`gradle/libs.versions.toml`)
- Centralized dependency management
- **Benefits**: Single source of truth for versions, easier updates

**Database:**
- SQLite (Android platform standard)
- Raw SQL with SQLiteOpenHelper (no Room in v1.0)
- See ADR-0001 for database architecture details
- See ADR-0002 for versioning strategy

**UI Framework:**
- Material Design 3 (Material Components for Android)
- ConstraintLayout for complex screens
- **Benefits**: Modern Android UI, accessibility support, consistent design

**Testing Framework:**
- JUnit 4 for unit tests
- Robolectric 4.13 for Android component testing (no emulator needed)
- Espresso for UI tests (device required)
- **Test-Driven Development (TDD)**: Red-Green-Refactor cycle

**Minimum/Target SDK:**
- Min SDK: 28 (Android 8.0 Oreo, 2017)
- Target SDK: 36 (Android 14+, 2025)
- **Rationale**: Balances modern features with device compatibility

### 5. Naming Conventions

**Classes:**
- PascalCase: `LoginActivity`, `WeightEntryDAO`, `PasswordUtils`
- Suffix patterns: `*Activity`, `*DAO`, `*Utils`, `*Manager`, `*Adapter`

**Methods:**
- camelCase (verbs): `getUserById()`, `validatePassword()`, `calculateBMI()`
- Boolean methods: `isValidUsername()`, `hasPermission()`, `isToday()`

**Variables:**
- camelCase (nouns): `userId`, `weightValue`, `currentDate`
- No single-letter names except loop counters

**Constants:**
- UPPER_SNAKE_CASE: `DATABASE_VERSION`, `MIN_PASSWORD_LENGTH`, `TAG`

**Layout IDs:**
- snake_case with type prefix: `btn_login`, `text_weight_display`, `input_username`

**Resource Files:**
- snake_case: `activity_login.xml`, `item_weight_entry.xml`, `bg_gradient_primary.xml`

**Database Columns:**
- snake_case: `user_id`, `weight_value`, `created_at`
- DAO layer maps to Java camelCase: `cursor.getLong("user_id")` → `user.setUserId(value)`

### 6. Code Organization Within Activities

**Standard Activity Structure (Order Matters):**

```java
public class LoginActivity extends AppCompatActivity {
    // 1. Constants and static fields
    private static final String TAG = "LoginActivity";
    private static final int MIN_USERNAME_LENGTH = 3;

    // 2. Instance fields - UI elements first, then data
    private EditText inputUsername;
    private EditText inputPassword;
    private Button btnLogin;
    private UserDAO userDAO;

    // 3. Lifecycle methods (in lifecycle order)
    @Override
    protected void onCreate(Bundle savedInstanceState) { }

    @Override
    protected void onResume() { }

    @Override
    protected void onPause() { }

    // 4. UI initialization
    private void initViews() { }

    private void setupListeners() { }

    // 5. Business logic methods
    private void handleLogin() { }

    private boolean validateInput() { }

    // 6. Helper/utility methods
    private void showError(String message) { }

    private void navigateToMain() { }
}
```

### 7. Dependency Management

**Version Catalog (`gradle/libs.versions.toml`):**
- Centralized dependency versions
- Type-safe accessors in build.gradle
- Example: `implementation libs.material`, `testImplementation libs.junit`

**Core Dependencies:**
- `androidx.appcompat` - Backward compatibility support
- `com.google.android.material` - Material Design components
- `androidx.constraintlayout` - Advanced layouts
- `junit` - Unit testing
- `org.robolectric` - Android unit testing without emulator

**No External Libraries for Core Features:**
- Password hashing: Java built-in MessageDigest (SHA-256)
- Date/time: Java 8 Time API (LocalDate, LocalDateTime)
- JSON parsing: Android built-in JSONObject (if needed)
- **Rationale**: Minimize dependencies, course requirements, learning experience

### 8. Testing Strategy

**Test-Driven Development (TDD):**
1. **Red**: Write failing test first
2. **Green**: Write minimal code to pass test
3. **Refactor**: Improve code while keeping tests green

**Test Coverage Requirements:**
- Utility classes: 100% coverage (PasswordUtils, ValidationUtils, DateUtils, etc.)
- DAO classes: 100% coverage (all CRUD operations)
- Business logic: 90%+ coverage (calculations, validations, workflows)
- Activities: Critical paths only (authentication, CRUD operations, permissions)
- Adapters: Basic functionality (data binding, click listeners)

**Test Organization:**
```
app/src/test/java/com/example/weighttogo/
├── models/         # POJO tests (getters/setters, toString)
├── database/       # DAO tests (CRUD, edge cases, constraints)
├── utils/          # Utility tests (validation, conversion, hashing)
└── activities/     # Activity tests (Robolectric, user flows)
```

**Testing Best Practices:**
- One test class per production class: `User.java` → `UserTest.java`
- Descriptive test names: `test_hashPassword_withValidInput_returnsNonNullHash()`
- AAA pattern: Arrange, Act, Assert
- Mock external dependencies (database, Android framework)
- Fast tests (<5 minutes for full suite)

### 9. Security Considerations

**Password Security:**
- SHA-256 hashing with random 16-byte salt
- Never store plain text passwords
- Never log passwords, hashes, or salts
- See `PasswordUtils` implementation

**SQL Injection Prevention:**
- Always use parameterized queries (ContentValues, prepared statements)
- Never concatenate user input into SQL strings
- DAO layer enforces this pattern

**Session Management:**
- Secure session storage (SharedPreferences or in-memory)
- Session timeout after inactivity (future enhancement)
- Clear session on logout

**Permissions:**
- Request SEND_SMS at runtime (Android 6.0+)
- Graceful degradation if permission denied
- Never require SMS for core functionality

### 10. Logging Strategy

**Log Levels:**
- `Log.d(TAG, ...)` - Method entry, parameter values (non-sensitive)
- `Log.i(TAG, ...)` - Successful operations (user logged in, entry saved)
- `Log.w(TAG, ...)` - Warnings (upgrade triggered, permission denied)
- `Log.e(TAG, ..., exception)` - Errors with stack traces

**What to Log:**
- Database creation/upgrade events
- Authentication attempts (success/failure, no passwords)
- Permission requests and results
- Data validation failures
- Exception stack traces

**What NOT to Log:**
- Passwords or password hashes
- Salts or encryption keys
- Personal identifiable information (PII)
- Full database query results (may contain sensitive data)

### 11. Error Handling

**Database Operations:**
```java
try {
    // Database operation
} catch (SQLiteException e) {
    Log.e(TAG, "Database error: " + e.getMessage(), e);
    // Show user-friendly message, don't expose SQL details
}
```

**User Input Validation:**
- Validate all input before processing
- Show clear error messages on validation failure
- Use `ValidationUtils` for consistent rules

**Graceful Degradation:**
- App works without SMS permission (no crashes)
- Handle missing data (empty states, default values)
- Network unavailable (not applicable for v1.0, but future-proof)

## Rationale

### Why MVC?

**Chosen over alternatives:**

| Pattern | Pros | Cons | Decision |
|---------|------|------|----------|
| **MVC** | ✅ Simple, well-understood<br>✅ Clear separation of concerns<br>✅ Easy to test<br>✅ Standard for Android | ❌ Activities can become large<br>❌ View-Controller coupling | **CHOSEN** - Best for course project, team familiarity |
| MVP | ✅ Better testability<br>✅ Presenter fully decoupled | ❌ More boilerplate<br>❌ Learning curve<br>❌ Overkill for simple app | Rejected - Too complex |
| MVVM | ✅ Modern Android standard<br>✅ LiveData/ViewModel support | ❌ Requires Jetpack libraries<br>❌ Learning curve<br>❌ Not covered in course | Deferred to v2.0+ |
| Clean Architecture | ✅ Maximum testability<br>✅ Highly decoupled | ❌ Significant boilerplate<br>❌ Overkill for small app<br>❌ Steep learning curve | Rejected - Too complex |

### Why Java 11 (Not Kotlin)?
- ✅ Course requirement (CS 360 uses Java)
- ✅ Team familiarity and existing knowledge
- ✅ Larger ecosystem for Android development
- ✅ Easier to find tutorials and examples
- ✅ Future migration to Kotlin possible (interoperable)

### Why SQLite (Not Room)?
- ✅ Android platform standard (zero configuration)
- ✅ Course requirement (demonstrate raw SQL knowledge)
- ✅ Full control over queries and migrations
- ✅ No external dependencies
- ❌ More boilerplate than Room
- **Future**: Migrate to Room in v2.0 (see ADR-0001)

### Why Material Design 3?
- ✅ Modern Android UI standard
- ✅ Built-in accessibility support (WCAG 2.1 AA)
- ✅ Consistent with Android ecosystem
- ✅ Theming and dark mode support
- ✅ Reduces custom UI code

### Why Test-Driven Development (TDD)?
- ✅ Catches bugs early (before implementation)
- ✅ Forces good design (testable code is well-designed code)
- ✅ Confidence in refactoring (tests verify behavior)
- ✅ Living documentation (tests show how code should work)
- ✅ Professional best practice

## Consequences

### Positive
- ✅ **Clear Structure**: Package organization makes it easy to find code
- ✅ **Testability**: MVC with DAOs is highly testable
- ✅ **Maintainability**: Separation of concerns makes changes easier
- ✅ **Scalability**: Can add features without major refactoring
- ✅ **Team Collaboration**: Clear conventions reduce confusion
- ✅ **Professional Standards**: Industry best practices demonstrated
- ✅ **Learning**: Demonstrates understanding of architecture patterns

### Negative
- ❌ **Activities Can Grow Large**: LoginActivity handles login + registration
- ❌ **No Compile-Time SQL Verification**: Room would catch SQL errors at compile time
- ❌ **More Boilerplate**: Raw SQL requires more code than Room
- ❌ **Manual Mapping**: DAO layer manually maps database columns to Java objects

### Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Activities become too complex | Extract business logic to utility classes |
| Test suite becomes slow | Use Robolectric for fast unit tests, minimize Espresso tests |
| Database migrations break data | Comprehensive migration tests (see ADR-0002) |
| Code duplication across DAOs | Share common code via base DAO class or utility methods |
| Inconsistent naming conventions | Code review checklist, lint rules |

## Implementation Guidelines

### When to Create a New Class

**Create a new Activity when:**
- New screen in the app (new layout file)
- Different user flow (login vs. main dashboard)

**Create a new Adapter when:**
- New RecyclerView with different item layout
- Different data type in list

**Create a new DAO when:**
- New database table
- Distinct set of CRUD operations

**Create a new Utility class when:**
- Reusable logic used by multiple activities
- Stateless helper methods (validation, conversion, calculation)

**Create a new Model when:**
- New database table (one model per table)
- Distinct data structure passed between layers

### When to Use Design Patterns

**Singleton:**
- Database helper (one connection per app)
- Session manager (one user session)
- **Never**: Models, DAOs, Activities

**Observer:**
- Data change notifications (future: LiveData)
- UI updates based on background operations

**Factory:**
- Creating different notification types
- Creating different achievement types
- **Never**: Simple object creation (use `new`)

## Future Enhancements

### v2.0: Room Persistence Library Migration
- Migrate from raw SQLite to Room
- Leverage compile-time SQL verification
- Use LiveData for reactive UI updates
- See ADR-0001 for database migration strategy

### v2.0: MVVM Architecture
- Introduce ViewModel layer (Jetpack)
- Use LiveData for data binding
- Reduce Activity complexity
- Better lifecycle management

### v3.0: Cloud Sync
- Add Repository pattern (local + remote data sources)
- Implement offline-first sync strategy
- Handle data conflicts

### v3.0: Dependency Injection
- Dagger/Hilt for dependency injection
- Improve testability (easier mocking)
- Reduce boilerplate in Activities

## Alternatives Considered

### Alternative 1: MVP (Model-View-Presenter)

**Pros:**
- Better testability (Presenter is POJO, easier to test)
- Complete separation of View and business logic
- Presenter can be reused across platforms

**Cons:**
- More boilerplate (one Presenter per Activity)
- More interfaces (View contract, Presenter contract)
- Learning curve for team
- Overkill for simple CRUD operations

**Decision:** Rejected - MVC is simpler and sufficient for project scope

### Alternative 2: Single-Package Structure

**Pros:**
- Simpler (all classes in one package)
- No package navigation

**Cons:**
- Hard to find classes as project grows
- No separation of concerns
- Mixes UI, data, and logic
- Not professional standard

**Decision:** Rejected - Package structure is essential for maintainability

### Alternative 3: Repository Pattern (Without Cloud)

**Pros:**
- Abstracts data source (easier to add cloud later)
- Clean API for data access
- Modern Android pattern

**Cons:**
- Additional layer of abstraction (DAO + Repository)
- Overkill for single data source (SQLite only)
- More boilerplate

**Decision:** Deferred to v3.0 when adding cloud sync

## References

- [Android Architecture Guide](https://developer.android.com/topic/architecture)
- [MVC Pattern in Android](https://www.geeksforgeeks.org/mvc-model-view-controller-architecture-pattern-in-android/)
- [Material Design 3](https://m3.material.io/)
- [Java Code Conventions](https://www.oracle.com/java/technologies/javase/codeconventions-contents.html)
- [Test-Driven Development by Example](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530) - Kent Beck

## Related ADRs

- ADR-0001: Initial Database Architecture (SQLite, schema, indexes, soft deletes)
- ADR-0002: Database Versioning Strategy (manual SQL migrations, future Room)
- ADR-0004: (Future) Room Persistence Library Migration Strategy
- ADR-0005: (Future) MVVM Architecture Migration Strategy

## Supersedes

None - this is the initial application architecture decision.

## Superseded By

None currently. Will be updated when migrating to MVVM (v2.0+) or adding cloud sync (v3.0+).