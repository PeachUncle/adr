# ADR-021: Testing Pyramid Implementation

## Status
Accepted

## Date
2025-03-02

## Context
Our Aronim Bookstore application requires a comprehensive and efficient testing strategy to ensure reliability, maintainability, and quality. We need an approach that:

- Provides confidence in application functionality
- Enables fast feedback during development
- Supports refactoring and code changes with minimal test breakage
- Ensures good test coverage across all layers of the application
- Balances thoroughness with execution speed
- Integrates well with our CI/CD pipeline
- Aligns with our Spring Boot and Java technology stack
- Supports both developers and QA engineers
- Scales with the growing codebase
- Detects issues early in the development process

Without a well-defined testing strategy, we risk inconsistent test coverage, slow test execution, brittle tests, and ultimately, reduced software quality and development velocity.

## Decision
We will implement a **Testing Pyramid** approach with the following layers:

### 1. Unit Tests (Base Layer)
- Largest number of tests
- Tests individual components in isolation
- Uses mocking for dependencies
- Fast execution time
- JUnit 5 as the primary testing framework
- Mockito for mocking dependencies
- AssertJ for fluent assertions
- Focus on service and domain logic

### 2. Integration Tests (Middle Layer)
- Moderate number of tests
- Tests interactions between components
- Spring Boot Test for integration testing
- TestContainers for database testing
- Focus on repository implementations, service integrations, and external dependencies
- Tests against real databases and external systems
- Validates configuration and wiring

### 3. API Tests (Upper Middle Layer)
- Tests REST API endpoints
- Spring MVC Test for controller testing
- RestAssured for API testing
- Validates request/response handling, error responses, and status codes
- Tests API contracts and documentation

### 4. End-to-End Tests (Top Layer)
- Smallest number of tests
- Tests complete user journeys
- Cucumber for behavior-driven development
- Selenium/WebDriver for UI testing (if applicable)
- Focuses on critical user flows
- Validates system as a whole

### 5. Non-Functional Tests
- Performance tests using JMeter or Gatling
- Security tests using OWASP ZAP
- Resilience tests for failure scenarios
- Executed on a scheduled basis, not necessarily on every commit

## Implementation Approach

1. **Unit Testing Framework**
   - JUnit 5 as the base framework
   - Mockito for mocking
   - AssertJ for assertions
   - JaCoCo for code coverage analysis
   - Test naming convention: `should[ExpectedBehavior]When[StateUnderTest]`
   - Focus on behavior verification rather than implementation details

2. **Integration Testing**
   - Spring Boot Test for integration tests
   - TestContainers for database and external services
   - Separate test profile with appropriate configuration
   - Focused on repositories, service integrations, and external dependencies
   - Database initialization with appropriate test data

3. **API Testing**
   - Spring MVC Test for controller unit tests
   - RestAssured for external API testing
   - OpenAPI/Swagger contract validation
   - Testing of error scenarios and edge cases
   - Validation of security constraints

4. **End-to-End Testing**
   - Cucumber for BDD scenarios
   - Feature files written in Gherkin syntax
   - Step definitions implemented in Java
   - Focus on critical user journeys
   - Separate execution from the main build for faster feedback

5. **Test Data Management**
   - Test data builders for domain objects
   - Database fixtures for integration tests
   - Consistent approach to test data creation
   - Clear separation between test data and production data

6. **CI/CD Integration**
   - Unit and integration tests run on every commit
   - API tests run on pull requests
   - End-to-end tests run nightly or on demand
   - Performance tests run on a scheduled basis
   - Test reports published to CI/CD dashboard

## Consequences

### Positive
- Comprehensive test coverage across all layers
- Fast feedback from unit tests during development
- Confidence in system behavior through end-to-end tests
- Reduced risk of regression issues
- Better isolation of test failures
- Improved test maintainability
- Clearer documentation of expected behavior
- Support for refactoring with confidence
- Better collaboration between developers and QA
- Alignment with industry best practices

### Negative
- Initial investment to set up the testing infrastructure
- Learning curve for developers not familiar with all testing approaches
- Maintenance overhead for end-to-end tests
- Potential for test duplication across layers
- Risk of slow build times if not properly optimized
- Need for discipline to maintain the pyramid shape
- Complexity in managing test environments

## Alternatives Considered

1. **Ice Cream Cone Anti-Pattern**
   - More end-to-end tests than unit tests
   - Slower feedback cycle
   - More brittle tests
   - Higher maintenance cost
   - Easier for non-technical stakeholders to understand

2. **Testing Trophy**
   - Emphasis on integration tests
   - Fewer unit tests focused only on complex logic
   - More end-to-end tests than the pyramid
   - Potentially better balance for certain applications
   - Still maintains fast feedback for most changes

3. **Minimal Testing Approach**
   - Focus only on critical path testing
   - Lower initial development cost
   - Higher risk of regression issues
   - Reduced confidence in system behavior
   - Limited documentation of expected behavior

4. **Outsourced QA Testing**
   - Manual testing by dedicated QA team
   - Less developer involvement in testing
   - Slower feedback cycle
   - Higher long-term cost
   - Less automation

## Implementation Notes

### Unit Test Example (JUnit 5 + Mockito + AssertJ)

```java
@ExtendWith(MockitoExtension.class)
class BookServiceTest {

    @Mock
    private BookRepository bookRepository;

    @Mock
    private CategoryRepository categoryRepository;

    @InjectMocks
    private BookService bookService;

    @Test
    void shouldReturnBookWhenBookExists() {
        // Given
        UUID bookId = UUID.randomUUID();
        Book book = new Book("Clean Code", "9780132350884", BigDecimal.valueOf(39.99));
        when(bookRepository.findById(bookId)).thenReturn(Optional.of(book));

        // When
        Optional<Book> result = bookService.findById(bookId);

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getTitle()).isEqualTo("Clean Code");
        verify(bookRepository).findById(bookId);
    }

    @Test
    void shouldThrowExceptionWhenCreatingBookWithInvalidData() {
        // Given
        BookDTO bookDTO = new BookDTO();
        bookDTO.setTitle("");  // Invalid title

        // When/Then
        assertThatThrownBy(() -> bookService.createBook(bookDTO))
            .isInstanceOf(ValidationException.class)
            .hasMessageContaining("Title cannot be empty");
        
        verifyNoInteractions(bookRepository);
    }
}
```

### Integration Test Example (Spring Boot Test + TestContainers)

```java
@SpringBootTest
@Testcontainers
@ActiveProfiles("test")
class BookRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:14")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void registerProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private BookRepository bookRepository;

    @Autowired
    private CategoryRepository categoryRepository;

    @Test
    void shouldSaveAndRetrieveBook() {
        // Given
        Category category = new Category("Programming");
        categoryRepository.save(category);

        Book book = new Book("Clean Code", "9780132350884", BigDecimal.valueOf(39.99));
        book.setCategory(category);
        
        // When
        Book savedBook = bookRepository.save(book);
        Optional<Book> retrievedBook = bookRepository.findById(savedBook.getId());
        
        // Then
        assertThat(retrievedBook).isPresent();
        assertThat(retrievedBook.get().getTitle()).isEqualTo("Clean Code");
        assertThat(retrievedBook.get().getCategory().getName()).isEqualTo("Programming");
    }

    @Test
    void shouldFindBooksByCategory() {
        // Given
        Category programming = categoryRepository.save(new Category("Programming"));
        Category fiction = categoryRepository.save(new Category("Fiction"));
        
        bookRepository.save(new Book("Clean Code", "9780132350884", BigDecimal.valueOf(39.99)).setCategory(programming));
        bookRepository.save(new Book("Effective Java", "9780134685991", BigDecimal.valueOf(49.99)).setCategory(programming));
        bookRepository.save(new Book("The Hobbit", "9780547928227", BigDecimal.valueOf(14.99)).setCategory(fiction));
        
        // When
        List<Book> programmingBooks = bookRepository.findByCategory(programming);
        
        // Then
        assertThat(programmingBooks).hasSize(2);
        assertThat(programmingBooks).extracting(Book::getTitle).containsExactlyInAnyOrder("Clean Code", "Effective Java");
    }
}
```

### API Test Example (Spring MVC Test)

```java
@WebMvcTest(BookController.class)
@Import(SecurityTestConfig.class)
class BookControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private BookService bookService;

    @Test
    @WithMockUser(roles = "USER")
    void shouldReturnBookWhenBookExists() throws Exception {
        // Given
        UUID bookId = UUID.randomUUID();
        BookDTO bookDTO = new BookDTO(
            bookId,
            "Clean Code",
            "9780132350884",
            BigDecimal.valueOf(39.99),
            "Programming principles",
            UUID.randomUUID(),
            "Programming"
        );
        
        when(bookService.findById(bookId)).thenReturn(Optional.of(bookDTO));

        // When/Then
        mockMvc.perform(get("/api/v1/books/{id}", bookId)
                .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(bookId.toString()))
            .andExpect(jsonPath("$.title").value("Clean Code"))
            .andExpect(jsonPath("$.isbn").value("9780132350884"))
            .andExpect(jsonPath("$.price").value(39.99))
            .andExpect(jsonPath("$.categoryName").value("Programming"));
        
        verify(bookService).findById(bookId);
    }

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldCreateBookWhenDataIsValid() throws Exception {
        // Given
        BookDTO requestDTO = new BookDTO();
        requestDTO.setTitle("Clean Code");
        requestDTO.setIsbn("9780132350884");
        requestDTO.setPrice(BigDecimal.valueOf(39.99));
        requestDTO.setCategoryId(UUID.randomUUID());
        
        BookDTO responseDTO = new BookDTO();
        BeanUtils.copyProperties(requestDTO, responseDTO);
        responseDTO.setId(UUID.randomUUID());
        
        when(bookService.createBook(any(BookDTO.class))).thenReturn(responseDTO);

        // When/Then
        mockMvc.perform(post("/api/v1/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(new ObjectMapper().writeValueAsString(requestDTO))
                .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists())
            .andExpect(jsonPath("$.title").value("Clean Code"))
            .andExpect(header().string("Location", containsString("/api/v1/books/")));
    }

    @Test
    @WithMockUser(roles = "USER")
    void shouldReturn403WhenUserTriesToCreateBook() throws Exception {
        // Given
        BookDTO requestDTO = new BookDTO();
        requestDTO.setTitle("Clean Code");
        
        // When/Then
        mockMvc.perform(post("/api/v1/books")
                .contentType(MediaType.APPLICATION_JSON)
                .content(new ObjectMapper().writeValueAsString(requestDTO)))
            .andExpect(status().isForbidden());
        
        verifyNoInteractions(bookService);
    }
}
```

### End-to-End Test Example (Cucumber)

```gherkin
# src/test/resources/features/book_management.feature
Feature: Book Management

  Background:
    Given the user is logged in as an admin

  Scenario: Admin creates a new book
    Given the following category exists:
      | name        |
      | Programming |
    When the admin adds a new book with the following details:
      | title      | isbn          | price | categoryName |
      | Clean Code | 9780132350884 | 39.99 | Programming  |
    Then the book should be created successfully
    And the book should appear in the list of available books

  Scenario: User searches for books by category
    Given the following books exist:
      | title         | isbn          | price | categoryName |
      | Clean Code    | 9780132350884 | 39.99 | Programming  |
      | Effective Java| 9780134685991 | 49.99 | Programming  |
      | The Hobbit    | 9780547928227 | 14.99 | Fiction      |
    When the user searches for books in category "Programming"
    Then the search results should contain 2 books
    And the search results should include the following books:
      | Clean Code    |
      | Effective Java|
```

```java
// Step definitions
@SpringBootTest
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class BookManagementSteps {

    @LocalServerPort
    private int port;

    @Autowired
    private CategoryRepository categoryRepository;

    @Autowired
    private BookRepository bookRepository;

    private RequestSpecification request;
    private Response response;

    @Before
    public void setUp() {
        RestAssured.baseURI = "http://localhost";
        RestAssured.port = port;
        request = RestAssured.given();
    }

    @Given("the user is logged in as an admin")
    public void userIsLoggedInAsAdmin() {
        // Setup authentication token for admin
        String token = getAdminAuthToken();
        request.header("Authorization", "Bearer " + token);
    }

    @Given("the following category exists:")
    public void theFollowingCategoryExists(DataTable dataTable) {
        List<Map<String, String>> rows = dataTable.asMaps(String.class, String.class);
        
        for (Map<String, String> row : rows) {
            Category category = new Category(row.get("name"));
            categoryRepository.save(category);
        }
    }

    @When("the admin adds a new book with the following details:")
    public void adminAddsNewBook(DataTable dataTable) {
        List<Map<String, String>> rows = dataTable.asMaps(String.class, String.class);
        Map<String, String> bookData = rows.get(0);
        
        Category category = categoryRepository.findByName(bookData.get("categoryName"))
            .orElseThrow(() -> new IllegalStateException("Category not found"));

        JSONObject requestBody = new JSONObject();
        requestBody.put("title", bookData.get("title"));
        requestBody.put("isbn", bookData.get("isbn"));
        requestBody.put("price", Double.parseDouble(bookData.get("price")));
        requestBody.put("categoryId", category.getId().toString());

        response = request
            .contentType(ContentType.JSON)
            .body(requestBody.toString())
            .when()
            .post("/api/v1/books");
    }

    @Then("the book should be created successfully")
    public void bookShouldBeCreatedSuccessfully() {
        response.then().statusCode(201);
    }

    // Additional step definitions...
}
```

### Performance Test Example (JMeter/Gatling)

```scala
// Gatling performance test
class BookSearchSimulation extends Simulation {

  val httpProtocol = http
    .baseUrl("http://localhost:8080")
    .acceptHeader("application/json")
    .userAgentHeader("Gatling Performance Test")

  val scn = scenario("Book Search Scenario")
    .exec(http("Home Page")
      .get("/api/v1/books")
      .check(status.is(200)))
    .pause(1)
    .exec(http("Search Books by Category")
      .get("/api/v1/books/search?category=Programming")
      .check(status.is(200))
      .check(jsonPath("$.length()").gt(0)))
    .pause(1)
    .exec(http("Get Book Details")
      .get("/api/v1/books/${bookId}")
      .check(status.is(200))
      .check(jsonPath("$.title").exists()))

  setUp(
    scn.inject(
      rampUsers(50).during(10.seconds),
      constantUsersPerSec(20).during(1.minute)
    ).protocols(httpProtocol)
  ).assertions(
    global.responseTime.max.lt(1000),
    global.successfulRequests.percent.gt(95)
  )
}
```

## Gradle Configuration

```kotlin
plugins {
    id("java")
    alias(libs.plugins.spring.boot)
    alias(libs.plugins.spring.dependency.management)
    id("jacoco")  // For code coverage
}

dependencies {
    // Unit testing
    testImplementation(libs.junit.jupiter)
    testImplementation(libs.mockito.core)
    testImplementation(libs.mockito.junit.jupiter)
    testImplementation(libs.assertj.core)
    
    // Spring Boot testing
    testImplementation(libs.spring.boot.starter.test)
    testImplementation(libs.spring.security.test)
    
    // Integration testing
    testImplementation(libs.testcontainers.junit.jupiter)
    testImplementation(libs.testcontainers.postgresql)
    
    // API testing
    testImplementation(libs.rest.assured)
    
    // BDD testing
    testImplementation(libs.cucumber.java)
    testImplementation(libs.cucumber.junit)
    testImplementation(libs.cucumber.spring)
}

tasks.test {
    useJUnitPlatform()
    finalizedBy(tasks.jacocoTestReport)
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}

// Separate task for Cucumber tests
tasks.register<Test>("cucumberTests") {
    description = "Runs Cucumber BDD tests."
    group = "verification"
    
    testClassesDirs = sourceSets.test.get().output.classesDirs
    classpath = sourceSets.test.get().runtimeClasspath
    
    useJUnitPlatform {
        includeTags("cucumber")
    }
    
    // Ensure these tests run after unit and integration tests
    shouldRunAfter(tasks.test)
}
```

## GitHub Actions Integration

```yaml
name: Test Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK
      uses: actions/setup-java@v3
      with:
        java-version: '21'
        distribution: 'temurin'
        
    - name: Run unit and integration tests
      run: ./gradlew test
      
    - name: Run API tests
      run: ./gradlew apiTest
      
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports
        path: |
          build/reports/tests/
          build/reports/jacoco/
        
    - name: Run Cucumber tests
      run: ./gradlew cucumberTests
      
    - name: Upload Cucumber reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: cucumber-reports
        path: build/reports/cucumber/
```

## Compliance Verification
- Code coverage metrics for unit and integration tests
- Automated execution of all test levels in CI/CD pipeline
- Regular review of test coverage and quality
- Test-driven development practices encouraged
- Documentation of testing standards and best practices
- Training for developers on effective testing techniques
- Regular refactoring of tests to maintain quality

## References
- Test Pyramid: https://martinfowler.com/articles/practical-test-pyramid.html
- Spring Boot Testing Documentation: https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing
- JUnit 5 User Guide: https://junit.org/junit5/docs/current/user-guide/
- Mockito Documentation: https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html
- TestContainers Documentation: https://www.testcontainers.org/
- Cucumber Documentation: https://cucumber.io/docs/cucumber/
- REST Assured Documentation: https://rest-assured.io/
