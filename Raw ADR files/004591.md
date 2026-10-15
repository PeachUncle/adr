# ADR-0005: Dependency Injection for Testing

- **Date**: 2025-12-13
- **Status**: Accepted

## Context

Activity tests were using real database instances via `WeighToGoDBHelper.getInstance()` and creating real DAOs with `new UserDAO(dbHelper)`, causing:
- **Slow test execution**: Database I/O overhead resulted in 2-3 second test runs (vs 0.2 seconds with mocks)
- **Brittle tests**: Tests depended on database state, making them sensitive to data changes and harder to debug
- **Difficulty testing edge cases**: Hard to simulate error conditions, null returns, race conditions
- **Misclassified tests**: Integration tests masquerading as unit tests, reducing test isolation
-  **CI/CD impact**: Slow tests increase pipeline execution time and developer feedback loops

## Decision

Use **package-private setter injection** for Activity testing.

Activities expose package-private setter methods (e.g., `setUserDAO(UserDAO)`, `setWeightEntryDAO(WeightEntryDAO)`) that allow test code to inject Mockito mocks before `onCreate()` is called. The setters are documented as "for testing only" and use package-private visibility to prevent misuse from outside the package.

### Implementation Pattern

**Production Code** (Activity):
```java
public class MainActivity extends AppCompatActivity {
    private UserDAO userDAO;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize dependencies (default production behavior)
        initDataLayer();

        // Rest of onCreate...
    }

    private void initDataLayer() {
        WeighToGoDBHelper dbHelper = WeighToGoDBHelper.getInstance(this);
        userDAO = new UserDAO(dbHelper);
        sessionManager = SessionManager.getInstance(this);
    }

    // =============================================================================================
    // TESTING SETTERS (Package-Private)
    // =============================================================================================

    /**
     * Set UserDAO instance (for testing only).
     * Allows test code to inject mock DAOs.
     *
     * @param userDAO the UserDAO instance to use
     */
    void setUserDAO(UserDAO userDAO) {
        this.userDAO = userDAO;
    }

    /**
     * Set SessionManager instance (for testing only).
     * Allows test code to inject mock SessionManager.
     *
     * @param sessionManager the SessionManager instance to use
     */
    void setSessionManager(SessionManager sessionManager) {
        this.sessionManager = sessionManager;
    }
}
```

**Test Code**:
```java
@RunWith(RobolectricTestRunner.class)
public class MainActivityTest {

    @Mock private UserDAO mockUserDAO;
    @Mock private SessionManager mockSessionManager;

    private ActivityController<MainActivity> activityController;
    private MainActivity activity;

    @Before
    public void setUp() {
        MockitoAnnotations.openMocks(this);

        // Build activity BUT don't call create() yet
        activityController = Robolectric.buildActivity(MainActivity.class);
        activity = activityController.get();

        // Inject mocks BEFORE onCreate is called
        activity.setUserDAO(mockUserDAO);
        activity.setSessionManager(mockSessionManager);

        // Set default mock behaviors
        when(mockSessionManager.isLoggedIn()).thenReturn(false);

        // NOW call lifecycle methods (onCreate will use mocked dependencies)
        activityController.create().start().resume();
    }
}
```

## Rationale

### Why Setter Injection?

**Advantages:**
1. **Minimal production code impact**: One setter per dependency (~10-20 LOC per Activity)
2. **No external frameworks required**: Aligns with educational goals and project simplicity
3. **Activities remain simple and understandable**: No complex DI configuration or annotations
4. **Compatible with Android lifecycle**: Doesn't interfere with Activity creation or system callbacks
5. **Easy to migrate to Dagger/Hilt** in v3.0 when production-grade DI is warranted
6. **Follows SOLID Dependency Inversion Principle**: Activities depend on abstractions (DAO interfaces)

**Disadvantages mitigated:**
1. **Package-private setters could be misused** → Mitigated by clear Javadoc stating "for testing only" and package-private visibility limiting scope
2. **Adds LOC to production code** → Minimal (10-20 lines per Activity) and well-documented
3. **Test complexity increases** → Offset by improved test speed and isolation

### Alternatives Considered

#### 1. Constructor Injection
**Rejected**: Complicates Android lifecycle management. Activities are created by the system via Intent, making constructor injection difficult without custom Activity factories.

**Example complications:**
```java
// Would require custom factory or Instrumentation override
public MainActivity(UserDAO userDAO, SessionManager sessionManager) {
    this.userDAO = userDAO;
    this.sessionManager = sessionManager;
}
```

#### 2. Mockito.mockStatic()
**Rejected**: Requires `mockito-inline` dependency and increases test complexity. Static mocking can cause test pollution and is harder to debug.

**Example complexity:**
```java
@Test
public void testWithStaticMocks() {
    try (MockedStatic<WeighToGoDBHelper> dbHelperMock = mockStatic(WeighToGoDBHelper.class)) {
        dbHelperMock.when(() -> WeighToGoDBHelper.getInstance(any())).thenReturn(mockDbHelper);
        // ... test logic
    } // Auto-closes and cleans up static mock
}
```

#### 3. Dagger/Hilt Dependency Injection
**Deferred to v3.0**: Too much complexity for an educational project focused on Android fundamentals. Adds learning curve, build configuration, and annotation processing overhead.

**Tradeoffs:**
- **Pros**: Industry standard, compile-time safety, automatic injection
- **Cons**: High learning curve, build complexity, annotation processing, not necessary for project scope

## Consequences

### Positive
- **10-100x faster test execution**: Database I/O eliminated, tests run in milliseconds
- **True unit test isolation**: Tests verify business logic, not database operations
- **Easier to test edge cases**: Can simulate error conditions, null returns, exceptions
- **Forces better dependency management**: Explicit dependencies make architecture clearer
- **Improved CI/CD performance**: Faster tests reduce pipeline execution time

### Negative
- **Adds 2-5 setter methods per Activity** (~10-20 LOC per Activity)
- **Package-private setters could be misused**: Mitigated by Javadoc and visibility
- **Test setup becomes more verbose**: Must initialize mocks and stub responses
- **Mocks must match real DAO behavior**: Risk of mocks diverging from actual implementation

### Neutral
- **Integration tests still valuable**: Keep some integration tests to validate real DAO behavior
- **Test file size increases**: More setup code, but tests are more explicit and readable

## Migration Path

### v2.0 (Current): Manual Setter Injection
- Activities expose package-private setters for DAO dependencies
- Tests use Mockito to inject mocks via setters
- Simple, no external frameworks, educational value high

### v3.0 (Future): Migrate to Dagger/Hilt
- Replace manual setter injection with `@Inject` annotations
- Use Dagger/Hilt for production-grade dependency injection
- Retain test infrastructure (Mockito mocks), only change injection mechanism
- Benefit from compile-time safety and automatic dependency graph generation

**Migration effort**: Low to Medium. Setter injection prepares architecture for Dagger/Hilt by making dependencies explicit.

## Testing Strategy

For detailed testing guidelines including when to use mocks vs real database, dependency injection patterns, and mock stubbing best practices, see **CONTRIBUTING.md § Testing Strategy**.

## References

- [Mockito Documentation](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html)
- [Robolectric Testing](http://robolectric.org/)
- [Android Testing Best Practices](https://developer.android.com/training/testing)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Injection Patterns](https://martinfowler.com/articles/injection.html)
- **CONTRIBUTING.md** - Testing Strategy section

## Related ADRs

- **ADR-0001**: Initial Architecture Decision (Layered architecture with DAO pattern)
- **ADR-0003**: Version Planning (v3.0 includes Dagger/Hilt migration)

## Impacted Files

### Production Files (4 Activities with setters added):
1. `app/src/main/java/com/example/weighttogo/activities/LoginActivity.java` (2 setters)
2. `app/src/main/java/com/example/weighttogo/activities/MainActivity.java` (5 setters)
3. `app/src/main/java/com/example/weighttogo/activities/SettingsActivity.java` (3 setters)
4. `app/src/main/java/com/example/weighttogo/activities/WeightEntryActivity.java` (4 setters)

### Test Files (3 Activity tests refactored to use Mockito):
5. `app/src/test/java/com/example/weighttogo/activities/MainActivityTest.java`
6. `app/src/test/java/com/example/weighttogo/activities/SettingsActivityTest.java`
7. `app/src/test/java/com/example/weighttogo/activities/WeightEntryActivityTest.java`

**Note**: `LoginActivityIntegrationTest` was NOT refactored because it tests DAO/SessionManager integration directly without instantiating the Activity. These integration tests remain valuable for validating real database operations.
