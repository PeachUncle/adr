# ADR-022: Test Data Management Strategy

## Status
Accepted

## Date
2025-03-02

## Context
Our Aronim Bookstore application requires a consistent, maintainable, and efficient approach to managing test data across different testing layers (unit, integration, API, and end-to-end tests). We need a test data management strategy that:

- Provides predictable and consistent test data across test executions
- Supports different testing layers with appropriate test data approaches
- Enables test isolation to prevent interference between tests
- Maintains test data that is representative of production scenarios
- Scales with the growing application and test suite
- Supports parallel test execution
- Handles complex data relationships and constraints
- Balances between realism and simplicity
- Integrates well with our testing frameworks and tools
- Facilitates test setup and teardown processes

Without a well-defined test data management strategy, we risk inconsistent test behavior, slow test execution, test data pollution, and maintenance challenges as the test suite grows.

## Decision
We will implement a comprehensive test data management strategy with the following components:

### 1. Test Data Builders Pattern
- Implement builder pattern for test data creation
- Use fluent interfaces for readable test data setup
- Provide sensible defaults for all required fields
- Support customization of specific properties
- Include factory methods for common test scenarios

### 2. Layer-Specific Test Data Strategies
- **Unit Tests**: In-memory test data with mocks and stubs
- **Integration Tests**: Test-specific database with TestContainers
- **API Tests**: Combination of in-memory and database test data
- **End-to-End Tests**: Isolated test environment with controlled data setup

### 3. Database Initialization
- Use Flyway/Liquibase migrations for schema setup
- Implement specific test data SQL scripts for baseline data
- Leverage Spring Boot's `data.sql` for test-specific data
- Use programmatic data setup for complex scenarios
- Implement proper cleanup between test executions

### 4. Test Data Isolation
- Use transaction rollbacks for test isolation where appropriate
- Implement unique identifiers for test data to prevent collisions
- Use separate database schemas or databases for parallel test execution
- Implement test-specific data cleanup routines

### 5. Test Fixtures and Factories
- Create reusable test fixtures for common entities
- Implement factory methods for test data creation
- Support relationships between test entities
- Provide utility methods for test data verification

### 6. External Systems and APIs
- Mock external system responses for unit and integration tests
- Use WireMock for HTTP-based external service simulation
- Implement test doubles for external system integrations
- Configure test-specific credentials and endpoints

## Implementation Approach

1. **Test Data Builders**
   - Create builder classes for all domain entities
   - Implement fluent interfaces with sensible defaults
   - Add factory methods for common scenarios
   - Support relationship building between entities

2. **Database Test Data**
   - Configure TestContainers for database tests
   - Implement database initialization scripts
   - Create test-specific migration scripts
   - Set up proper test cleanup procedures

3. **Test Fixtures**
   - Create a test fixture library for common test scenarios
   - Implement factory methods for test data creation
   - Support customization of test data
   - Document available test fixtures

4. **External System Simulation**
   - Configure WireMock for external API simulation
   - Create mock responses for common scenarios
   - Implement test-specific configuration
   - Document available mock services

5. **Test Data Cleanup**
   - Implement automatic cleanup after tests
   - Use transaction management for test isolation
   - Create utility methods for manual cleanup
   - Configure proper test ordering when needed

## Consequences

### Positive
- Consistent and predictable test data across test executions
- Improved test readability through fluent builder interfaces
- Better test isolation preventing interference between tests
- Reduced maintenance effort for test data
- Support for complex test scenarios and relationships
- Easier setup of test preconditions
- Better representation of production-like data
- Improved test stability and reliability
- Easier debugging of test failures
- Support for parallel test execution

### Negative
- Initial development effort to create test data infrastructure
- Learning curve for developers to understand the test data patterns
- Potential for test data duplication across test classes
- Risk of complex test data setup code
- Maintenance overhead for test data builders and fixtures
- Potential performance impact for database-heavy tests
- Need for discipline to maintain test data isolation

## Alternatives Considered

1. **Ad-hoc Test Data Creation**
   - Simpler initial implementation
   - No standardized approach
   - Higher risk of test data inconsistency
   - More difficult maintenance as the test suite grows
   - Potential for test interference

2. **Shared Test Database**
   - Simpler setup with a single shared database
   - Higher risk of test interference
   - Challenges with parallel test execution
   - Potential for flaky tests due to shared state
   - Simpler initial configuration

3. **Production Data Sampling**
   - More realistic test data
   - Privacy and security concerns
   - Complex data anonymization requirements
   - Potential for unpredictable test behavior
   - Larger data volumes impacting test performance

4. **Fully Randomized Test Data**
   - Less maintenance of specific test cases
   - Potential for missing edge cases
   - Less predictable test behavior
   - Potential for flaky tests
   - Better coverage of unexpected scenarios

## Implementation Notes

### Test Data Builder Example

```java
public class BookBuilder {
    private UUID id = UUID.randomUUID();
    private String title = "Default Book Title";
    private String isbn = "9781234567897";
    private BigDecimal price = BigDecimal.valueOf(29.99);
    private String description = "Default book description";
    private Category category = CategoryBuilder.aCategory().build();
    private Set<Author> authors = new HashSet<>();
    private BookStatus status = BookStatus.AVAILABLE;
    
    private BookBuilder() {
    }
    
    public static BookBuilder aBook() {
        return new BookBuilder();
    }
    
    public static BookBuilder aFictionBook() {
        return aBook()
            .withTitle("Fiction Book")
            .withCategory(CategoryBuilder.aCategory().withName("Fiction").build());
    }
    
    public static BookBuilder aProgrammingBook() {
        return aBook()
            .withTitle("Programming Book")
            .withCategory(CategoryBuilder.aCategory().withName("Programming").build());
    }
    
    public BookBuilder withId(UUID id) {
        this.id = id;
        return this;
    }
    
    public BookBuilder withTitle(String title) {
        this.title = title;
        return this;
    }
    
    public BookBuilder withIsbn(String isbn) {
        this.isbn = isbn;
        return this;
    }
    
    public BookBuilder withPrice(BigDecimal price) {
        this.price = price;
        return this;
    }
    
    public BookBuilder withDescription(String description) {
        this.description = description;
        return this;
    }
    
    public BookBuilder withCategory(Category category) {
        this.category = category;
        return this;
    }
    
    public BookBuilder withAuthor(Author author) {
        this.authors.add(author);
        return this;
    }
    
    public BookBuilder withStatus(BookStatus status) {
        this.status = status;
        return this;
    }
    
    public Book build() {
        Book book = new Book();
        book.setId(id);
        book.setTitle(title);
        book.setIsbn(isbn);
        book.setPrice(price);
        book.setDescription(description);
        book.setCategory(category);
        book.setAuthors(authors);
        book.setStatus(status);
        return book;
    }
}
```

### Test Fixture Example

```java
public class TestFixtures {
    
    public static class Books {
        public static final Book CLEAN_CODE = BookBuilder.aBook()
            .withId(UUID.fromString("f295b54a-23a7-4f10-90d8-9b31f97e319b"))
            .withTitle("Clean Code")
            .withIsbn("9780132350884")
            .withPrice(BigDecimal.valueOf(39.99))
            .withDescription("A Handbook of Agile Software Craftsmanship")
            .withCategory(Categories.PROGRAMMING)
            .withAuthor(Authors.ROBERT_MARTIN)
            .build();
            
        public static final Book EFFECTIVE_JAVA = BookBuilder.aBook()
            .withId(UUID.fromString("c9b2b877-9179-4b71-bab5-4ce4c5d58e8f"))
            .withTitle("Effective Java")
            .withIsbn("9780134685991")
            .withPrice(BigDecimal.valueOf(49.99))
            .withDescription("Best practices for Java programmers")
            .withCategory(Categories.PROGRAMMING)
            .withAuthor(Authors.JOSHUA_BLOCH)
            .build();
            
        public static final Book THE_HOBBIT = BookBuilder.aBook()
            .withId(UUID.fromString("a1b2c3d4-e5f6-4a5b-8c7d-9e8f7a6b5c4d"))
            .withTitle("The Hobbit")
            .withIsbn("9780547928227")
            .withPrice(BigDecimal.valueOf(14.99))
            .withDescription("Fantasy novel by J.R.R. Tolkien")
            .withCategory(Categories.FICTION)
            .withAuthor(Authors.JRR_TOLKIEN)
            .build();
    }
    
    public static class Categories {
        public static final Category PROGRAMMING = CategoryBuilder.aCategory()
            .withId(UUID.fromString("d2e8352a-651a-4f58-bd8e-67c1e3b15dc3"))
            .withName("Programming")
            .build();
            
        public static final Category FICTION = CategoryBuilder.aCategory()
            .withId(UUID.fromString("b7c8d9e0-f1a2-3b4c-5d6e-7f8a9b0c1d2e"))
            .withName("Fiction")
            .build();
    }
    
    public static class Authors {
        public static final Author ROBERT_MARTIN = AuthorBuilder.anAuthor()
            .withId(UUID.fromString("e4f5a6b7-c8d9-4e5f-6a7b-8c9d0e1f2a3b"))
            .withName("Robert C. Martin")
            .build();
            
        public static final Author JOSHUA_BLOCH = AuthorBuilder.anAuthor()
            .withId(UUID.fromString("a1s2d3f4-g5h6-7j8k-9l0p-q1w2e3r4t5y6"))
            .withName("Joshua Bloch")
            .build();
            
        public static final Author JRR_TOLKIEN = AuthorBuilder.anAuthor()
            .withId(UUID.fromString("z1x2c3v4-b5n6-7m8k-9j0h-g1f2d3s4a5p6"))
            .withName("J.R.R. Tolkien")
            .build();
    }
    
    public static class Users {
        public static final User ADMIN_USER = UserBuilder.anAdmin()
            .withId(UUID.fromString("a9b8c7d6-e5f4-4g3h-2i1j-k0l9m8n7o6p5"))
            .withUsername("admin")
            .withEmail("admin@example.com")
            .build();
            
        public static final User REGULAR_USER = UserBuilder.aUser()
            .withId(UUID.fromString("p5o4i3u2-y1t7-8r9e0-w1q2-s3d4f5g6h7j8"))
            .withUsername("user")
            .withEmail("user@example.com")
            .build();
    }
}
```

### Database Test Configuration with TestContainers

```java
@TestConfiguration
@TestPropertySource(properties = {
    "spring.jpa.hibernate.ddl-auto=none",
    "spring.flyway.enabled=true",
    "spring.flyway.locations=classpath:db/migration,classpath:db/testdata"
})
public class TestDatabaseConfig {
    
    @Bean
    @Primary
    @ConditionalOnProperty(name = "test.database.type", havingValue = "testcontainers", matchIfMissing = true)
    public DataSource testContainersDataSource() {
        PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:14")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
        
        postgres.start();
        
        return DataSourceBuilder.create()
            .url(postgres.getJdbcUrl())
            .username(postgres.getUsername())
            .password(postgres.getPassword())
            .build();
    }
    
    @Bean
    @Primary
    @ConditionalOnProperty(name = "test.database.type", havingValue = "h2")
    public DataSource h2DataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }
}
```

### Base Test Class for Database Tests

```java
@SpringBootTest
@ActiveProfiles("test")
@Transactional
public abstract class BaseRepositoryTest {
    
    @Autowired
    protected TestEntityManager entityManager;
    
    @Autowired
    protected JdbcTemplate jdbcTemplate;
    
    @Autowired
    protected TestDataHelper testDataHelper;
    
    @BeforeEach
    void setUpTestData() {
        // Clear specific tables if needed
        // testDataHelper.clearTables("books", "authors");
        
        // Set up common test data
        testDataHelper.setupBasicTestData();
    }
    
    protected <T> T persistAndFlush(T entity) {
        entityManager.persist(entity);
        entityManager.flush();
        return entity;
    }
    
    protected <T> T save(T entity) {
        return entityManager.merge(entity);
    }
    
    protected void flushAndClear() {
        entityManager.flush();
        entityManager.clear();
    }
}
```

### Test Data Helper Service

```java
@Service
@Profile("test")
public class TestDataHelper {
    
    private final JdbcTemplate jdbcTemplate;
    private final EntityManager entityManager;
    private final CategoryRepository categoryRepository;
    private final AuthorRepository authorRepository;
    private final BookRepository bookRepository;
    private final UserRepository userRepository;
    
    @Autowired
    public TestDataHelper(
            JdbcTemplate jdbcTemplate,
            EntityManager entityManager,
            CategoryRepository categoryRepository,
            AuthorRepository authorRepository,
            BookRepository bookRepository,
            UserRepository userRepository) {
        this.jdbcTemplate = jdbcTemplate;
        this.entityManager = entityManager;
        this.categoryRepository = categoryRepository;
        this.authorRepository = authorRepository;
        this.bookRepository = bookRepository;
        this.userRepository = userRepository;
    }
    
    public void clearAllData() {
        executeInOrder(
            "DELETE FROM book_authors",
            "DELETE FROM orders_items",
            "DELETE FROM orders",
            "DELETE FROM books",
            "DELETE FROM authors",
            "DELETE FROM categories",
            "DELETE FROM users"
        );
    }
    
    public void clearTables(String... tableNames) {
        for (String tableName : tableNames) {
            jdbcTemplate.execute("DELETE FROM " + tableName);
        }
    }
    
    private void executeInOrder(String... sqlStatements) {
        for (String sql : sqlStatements) {
            try {
                jdbcTemplate.execute(sql);
            } catch (Exception e) {
                throw new RuntimeException("Failed to execute SQL: " + sql, e);
            }
        }
    }
    
    public void setupBasicTestData() {
        // Create and save categories
        Category programming = saveOrUpdate(TestFixtures.Categories.PROGRAMMING);
        Category fiction = saveOrUpdate(TestFixtures.Categories.FICTION);
        
        // Create and save authors
        Author robertMartin = saveOrUpdate(TestFixtures.Authors.ROBERT_MARTIN);
        Author joshuaBloch = saveOrUpdate(TestFixtures.Authors.JOSHUA_BLOCH);
        Author jrrTolkien = saveOrUpdate(TestFixtures.Authors.JRR_TOLKIEN);
        
        // Create and save books
        Book cleanCode = BookBuilder.aBook()
            .withId(TestFixtures.Books.CLEAN_CODE.getId())
            .withTitle("Clean Code")
            .withIsbn("9780132350884")
            .withPrice(BigDecimal.valueOf(39.99))
            .withCategory(programming)
            .build();
        cleanCode.getAuthors().add(robertMartin);
        saveOrUpdate(cleanCode);
        
        Book effectiveJava = BookBuilder.aBook()
            .withId(TestFixtures.Books.EFFECTIVE_JAVA.getId())
            .withTitle("Effective Java")
            .withIsbn("9780134685991")
            .withPrice(BigDecimal.valueOf(49.99))
            .withCategory(programming)
            .build();
        effectiveJava.getAuthors().add(joshuaBloch);
        saveOrUpdate(effectiveJava);
        
        Book theHobbit = BookBuilder.aBook()
            .withId(TestFixtures.Books.THE_HOBBIT.getId())
            .withTitle("The Hobbit")
            .withIsbn("9780547928227")
            .withPrice(BigDecimal.valueOf(14.99))
            .withCategory(fiction)
            .build();
        theHobbit.getAuthors().add(jrrTolkien);
        saveOrUpdate(theHobbit);
        
        // Create and save users
        saveOrUpdate(TestFixtures.Users.ADMIN_USER);
        saveOrUpdate(TestFixtures.Users.REGULAR_USER);
        
        // Flush to ensure all entities are persisted
        entityManager.flush();
    }
    
    private <T> T saveOrUpdate(T entity) {
        return entityManager.merge(entity);
    }
    
    public void generateTestBooks(int count, Category category, Author author) {
        for (int i = 0; i < count; i++) {
            Book book = BookBuilder.aBook()
                .withTitle("Generated Book " + i)
                .withIsbn("978000000" + String.format("%04d", i))
                .withPrice(BigDecimal.valueOf(10.0 + (i % 90)))
                .withCategory(category)
                .build();
            book.getAuthors().add(author);
            bookRepository.save(book);
        }
    }
}
```

### Integration Test Example with Test Data

```java
@SpringBootTest
@ActiveProfiles("test")
class BookRepositoryIntegrationTest extends BaseRepositoryTest {

    @Autowired
    private BookRepository bookRepository;
    
    @Test
    void shouldFindBooksByCategory() {
        // Given - Test data is already set up in BaseRepositoryTest
        Category programming = entityManager.find(Category.class, 
            TestFixtures.Categories.PROGRAMMING.getId());
        
        // When
        List<Book> books = bookRepository.findByCategory(programming);
        
        // Then
        assertThat(books).hasSize(2);
        assertThat(books).extracting(Book::getTitle)
            .containsExactlyInAnyOrder("Clean Code", "Effective Java");
    }
    
    @Test
    void shouldFindBooksByPriceRange() {
        // Given
        BigDecimal minPrice = BigDecimal.valueOf(30.00);
        BigDecimal maxPrice = BigDecimal.valueOf(45.00);
        
        // When
        List<Book> books = bookRepository.findByPriceBetween(minPrice, maxPrice);
        
        // Then
        assertThat(books).hasSize(1);
        assertThat(books.get(0).getTitle()).isEqualTo("Clean Code");
    }
    
    @Test
    void shouldSaveAndRetrieveNewBook() {
        // Given
        Category fiction = entityManager.find(Category.class, 
            TestFixtures.Categories.FICTION.getId());
        
        Book newBook = BookBuilder.aBook()
            .withTitle("New Test Book")
            .withIsbn("9781234567890")
            .withPrice(BigDecimal.valueOf(24.99))
            .withCategory(fiction)
            .build();
        
        // When
        Book savedBook = bookRepository.save(newBook);
        entityManager.flush();
        entityManager.clear(); // Clear persistence context to force a database read
        
        Optional<Book> retrievedBook = bookRepository.findById(savedBook.getId());
        
        // Then
        assertThat(retrievedBook).isPresent();
        assertThat(retrievedBook.get().getTitle()).isEqualTo("New Test Book");
        assertThat(retrievedBook.get().getCategory().getName()).isEqualTo("Fiction");
    }
}
```

### API Test with WireMock for External Services

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class PaymentServiceIntegrationTest {

    @Autowired
    private PaymentService paymentService;
    
    @Autowired
    private WireMockServer wireMockServer;
    
    @BeforeEach
    void setUp() {
        wireMockServer.stubFor(
            post(urlPathEqualTo("/payment-api/v1/process"))
                .withHeader("Content-Type", equalTo("application/json"))
                .withRequestBody(matchingJsonPath("$.amount", greaterThan("0")))
                .willReturn(aResponse()
                    .withStatus(200)
                    .withHeader("Content-Type", "application/json")
                    .withBody("""
                        {
                            "transactionId": "tx-12345",
                            "status": "SUCCESS",
                            "timestamp": "2023-05-01T10:30:00Z"
                        }
                    """)
                )
        );
        
        wireMockServer.stubFor(
            post(urlPathEqualTo("/payment-api/v1/process"))
                .withHeader("Content-Type", equalTo("application/json"))
                .withRequestBody(matchingJsonPath("$.amount", equalTo("0")))
                .willReturn(aResponse()
                    .withStatus(400)
                    .withHeader("Content-Type", "application/json")
                    .withBody("""
                        {
                            "error": "INVALID_AMOUNT",
                            "message": "Payment amount must be greater than zero",
                            "timestamp": "2023-05-01T10:30:00Z"
                        }
                    """)
                )
        );
    }
    
    @Test
    void shouldProcessPaymentSuccessfully() {
        // Given
        PaymentRequest request = new PaymentRequest(
            "4111111111111111",
            "12/25",
            "123",
            BigDecimal.valueOf(99.99),
            "USD"
        );
        
        // When
        PaymentResponse response = paymentService.processPayment(request);
        
        // Then
        assertThat(response.isSuccessful()).isTrue();
        assertThat(response.getTransactionId()).isEqualTo("tx-12345");
    }
    
    @Test
    void shouldRejectPaymentWithZeroAmount() {
        // Given
        PaymentRequest request = new PaymentRequest(
            "4111111111111111",
            "12/25",
            "123",
            BigDecimal.ZERO,
            "USD"
        );
        
        // When/Then
        assertThatThrownBy(() -> paymentService.processPayment(request))
            .isInstanceOf(PaymentException.class)
            .hasMessageContaining("Payment amount must be greater than zero");
    }
}
```

### End-to-End Test with Cucumber

```gherkin
# src/test/resources/features/book_management.feature
Feature: Book Management

  Background:
    Given the system has the following categories
      | id                                   | name        |
      | d2e8352a-651a-4f58-bd8e-67c1e3b15dc3 | Programming |
      | b7c8d9e0-f1a2-3b4c-5d6e-7f8a9b0c1d2e | Fiction     |
    And the system has the following authors
      | id                                   | name             |
      | e4f5a6b7-c8d9-4e5f-6a7b-8c9d0e1f2a3b | Robert C. Martin |
      | z1x2c3v4-b5n6-7m8k-9j0h-g1f2d3s4a5p6 | J.R.R. Tolkien   |
    And the system has the following books
      | id                                   | title      | isbn          | price | category    | author           |
      | f295b54a-23a7-4f10-90d8-9b31f97e319b | Clean Code | 9780132350884 | 39.99 | Programming | Robert C. Martin |
      | a1b2c3d4-e5f6-4a5b-8c7d-9e8f7a6b5c4d | The Hobbit | 9780547928227 | 14.99 | Fiction     | J.R.R. Tolkien   |
    And I am logged in as an administrator

  Scenario: Add a new book to the catalog
    When I add a new book with the following details
      | title          | isbn          | price | category    | author           |
      | Effective Java | 9780134685991 | 49.99 | Programming | Joshua Bloch     |
    Then the book "Effective Java" should be added to the catalog
    And the book should have ISBN "9780134685991"
    And the book should be in category "Programming"
    And the book should cost $49.99

  Scenario: Search for books by category
    When I search for books in category "Programming"
    Then I should see the following books in the results
      | title      | isbn          | price |
      | Clean Code | 9780132350884 | 39.99 |
    And I should not see the following books in the results
      | title      | isbn          | price |
      | The Hobbit | 9780547928227 | 14.99 |
```

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
public class BookManagementSteps {

    @LocalServerPort
    private int port;
    
    @Autowired
    private TestDataHelper testDataHelper;
    
    @Autowired
    private CategoryRepository categoryRepository;
    
    @Autowired
    private AuthorRepository authorRepository;
    
    @Autowired
    private BookRepository bookRepository;
    
    private RequestSpecification request;
    private Response response;
    
    @Before
    public void setUp() {
        RestAssured.baseURI = "http://localhost";
        RestAssured.port = port;
        request = RestAssured.given();
        
        // Clear database before each scenario
        testDataHelper.clearAllData();
    }
    
    @Given("the system has the following categories")
    public void theSystemHasTheFollowingCategories(DataTable dataTable) {
        List<Map<String, String>> categories = dataTable.asMaps();
        
        for (Map<String, String> categoryData : categories) {
            Category category = CategoryBuilder.aCategory()
                .withId(UUID.fromString(categoryData.get("id")))
                .withName(categoryData.get("name"))
                .build();
            
            categoryRepository.save(category);
        }
    }
    
    @Given("the system has the following authors")
    public void theSystemHasTheFollowingAuthors(DataTable dataTable) {
        List<Map<String, String>> authors = dataTable.asMaps();
        
        for (Map<String, String> authorData : authors) {
            Author author = AuthorBuilder.anAuthor()
                .withId(UUID.fromString(authorData.get("id")))
                .withName(authorData.get("name"))
                .build();
            
            authorRepository.save(author);
        }
    }
    
    @Given("the system has the following books")
    public void theSystemHasTheFollowingBooks(DataTable dataTable) {
        List<Map<String, String>> books = dataTable.asMaps();
        
        for (Map<String, String> bookData : books) {
            Category category = categoryRepository.findByName(bookData.get("category"))
                .orElseThrow(() -> new IllegalStateException("Category not found: " + bookData.get("category")));
            
            Author author = authorRepository.findByName(bookData.get("author"))
                .orElseThrow(() -> new IllegalStateException("Author not found: " + bookData.get("author")));
            
            Book book = BookBuilder.aBook()
                .withId(UUID.fromString(bookData.get("id")))
                .withTitle(bookData.get("title"))
                .withIsbn(bookData.get("isbn"))
                .withPrice(new BigDecimal(bookData.get("price")))
                .withCategory(category)
                .build();
            
            book.getAuthors().add(author);
            bookRepository.save(book);
        }
    }
    
    @Given("I am logged in as an administrator")
    public void iAmLoggedInAsAnAdministrator() {
        // Setup authentication for admin user
        String token = obtainAdminToken();
        request.header("Authorization", "Bearer " + token);
    }
    
    // Additional step definitions...
    
    private String obtainAdminToken() {
        // Implementation to obtain admin token
        return "admin-token";
    }
}
```

## Compliance Verification
- Code reviews to ensure proper use of test data patterns
- Static analysis to detect test data anti-patterns
- Regular review of test data management practices
- Performance monitoring of test execution times
- Verification of test isolation through parallel execution
- Documentation of test data management approach
- Training for team members on test data best practices

## References
- Test Data Builder Pattern: http://www.natpryce.com/articles/000714.html
- Spring Boot Testing Documentation: https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing
- TestContainers Documentation: https://www.testcontainers.org/
- WireMock Documentation: http://wiremock.org/docs/
- Test Fixtures Best Practices: https://martinfowler.com/bliki/ObjectMother.html
- Spring Data JPA Testing: https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#jpa.sample-app.testing
- Cucumber Documentation: https://cucumber.io/docs/cucumber/
