# ADR-002: Adoption of Java 21 as Primary Programming Language

## Status
Accepted

## Date
2025-03-01

## Context
Our project requires a robust, maintainable, and well-supported programming language for implementing the Aronim Bookstore application. We need a language that:

- Is well-suited for enterprise application development
- Has strong integration with Spring Boot and the Java ecosystem
- Provides good performance and stability
- Has a large talent pool and community support
- Offers long-term maintainability and support
- Has mature tooling and libraries
- Aligns with our team's skills and experience
- Provides type safety and compile-time checks
- Supports modern programming paradigms and features

The choice of programming language is fundamental and will impact all aspects of development, from code organization to team productivity and runtime performance. Additionally, selecting the specific version of the language is important to balance access to modern features with stability and ecosystem support.

## Decision
We will use **Java 21** (the latest LTS release) as the primary programming language for the Aronim Bookstore project.

### 1. Core Language Features in Java 21
- Strong static typing with generics
- Object-oriented programming with inheritance and interfaces
- Functional programming capabilities (lambdas, streams)
- Pattern matching for switch expressions (finalized in Java 21)
- Records for immutable data classes
- Sealed classes for defining class hierarchies
- Text blocks for cleaner multiline strings
- Virtual threads for high-throughput concurrent applications
- Structured concurrency for managing complex asynchronous operations
- Foreign Function & Memory API for interacting with code outside the JVM
- Module system for better encapsulation
- Rich standard library

### 2. Spring Boot Integration
- Native language for Spring framework
- First-class support in Spring Boot
- Spring 6 and Spring Boot 3 designed to leverage Java 21 features
- Comprehensive documentation and examples
- Mature annotation processing
- Excellent tooling support

### 3. Development Experience
- Rich IDE support (IntelliJ IDEA, Eclipse, VS Code)
- Strong refactoring capabilities
- Comprehensive static analysis tools
- Extensive debugging capabilities
- Well-established coding standards
- Preview features for early access to upcoming language improvements

### 4. Performance and Stability
- JIT compilation for runtime optimization
- Improved garbage collection algorithms
- GraalVM native image support for faster startup
- Virtual threads for improved scalability without increased memory usage
- Excellent profiling tools
- Predictable performance characteristics
- Strong backward compatibility guarantees

## Implementation Approach

1. **Language Version Configuration**
   - Standardize on Java 21 LTS
   - Configure toolchain in Gradle to ensure consistent JDK usage
   - Use preview features selectively with appropriate flags
   - Define coding standards for Java 21 features usage
   - Configure appropriate compiler settings

2. **Modern Java Features Adoption**
   - Use records for data transfer objects
   - Apply pattern matching for more readable conditional logic
   - Implement sealed classes for domain model hierarchies
   - Use text blocks for SQL queries and JSON templates
   - Leverage virtual threads for I/O-bound operations
   - Apply structured concurrency for complex asynchronous workflows

3. **Code Organization**
   - Follow standard Java package naming conventions
   - Implement clean separation of concerns
   - Use interfaces for defining contracts
   - Apply SOLID principles in class design
   - Leverage Java modules for larger applications

4. **Concurrency Approach**
   - Use virtual threads for I/O-bound operations
   - Apply structured concurrency for managing task groups
   - Implement non-blocking I/O where appropriate
   - Use modern concurrency utilities from java.util.concurrent

## Consequences

### Positive
- Access to the latest stable language features
- Virtual threads for dramatically improved scalability
- Pattern matching for more readable and safer code
- Records for concise data classes with less boilerplate
- Long-term support (LTS) for stability
- Improved performance with latest JVM optimizations
- Better developer experience with modern language features
- Future-proofing the codebase
- Compatibility with latest Spring framework versions
- Reduced verbosity compared to earlier Java versions

### Negative
- Requires JDK 21 runtime in production environments
- Some libraries may not yet be tested with Java 21
- Learning curve for developers familiar with older Java versions
- Limited experience with newest features in production settings
- Some build tools and CI environments may need updates
- Cloud platforms may have limited Java 21 support initially
- Preview features require special handling and may change

## Alternatives Considered

1. **Java 21 (LTS)**
   - Previous LTS release with good ecosystem support
   - Lacks virtual threads and other Java 21 improvements
   - Longer history of production use
   - More conservative choice
   - Still supported for many years

2. **Kotlin**
   - More concise syntax
   - Better null safety with nullable types
   - Extension functions
   - Coroutines for asynchronous programming
   - Data classes for immutable data
   - Interoperability with Java
   - Less mature ecosystem
   - Additional build complexity
   - Steeper learning curve for Java developers

3. **Java 22+ (non-LTS)**
   - Access to even newer features
   - Shorter support window
   - Less stable for long-term projects
   - Faster release cycles requiring more frequent updates
   - Less ecosystem testing and support

4. **GraalVM Native Image with Java 21**
   - Compiled ahead-of-time for faster startup
   - Smaller memory footprint
   - Trade-offs in dynamic features
   - More complex build process
   - Limited reflection capabilities
   - Could be considered as a deployment option rather than language alternative

## Implementation Notes

### Gradle Build Configuration (Kotlin DSL)

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
}

group = "com.aronim.bookstore"
version = "0.0.1-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_21
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-security")
    
    // Java-specific libraries
    implementation("com.google.guava:guava:32.1.2-jre")
    implementation("org.apache.commons:commons-lang3:3.13.0")
    implementation("org.apache.commons:commons-collections4:4.4")
    
    // Jackson for JSON processing
    implementation("com.fasterxml.jackson.core:jackson-databind")
    implementation("com.fasterxml.jackson.datatype:jackson-datatype-jsr310")
    
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.springframework.security:spring-security-test")
    testImplementation("org.junit.jupiter:junit-jupiter")
    testImplementation("org.mockito:mockito-junit-jupiter")
}

tasks.withType<Test> {
    useJUnitPlatform()
}

tasks.withType<JavaCompile> {
    options.compilerArgs.add("--enable-preview")
}
```

### Java Application Entry Point with Virtual Threads

```java
package com.aronim.bookstore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.embedded.tomcat.TomcatProtocolHandlerCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

import java.util.concurrent.Executors;

@SpringBootApplication
@EnableJpaAuditing
public class BookstoreApplication {

    public static void main(String[] args) {
        SpringApplication.run(BookstoreApplication.class, args);
    }
    
    @Bean
    public TomcatProtocolHandlerCustomizer<?> protocolHandlerVirtualThreadExecutorCustomizer() {
        return protocolHandler -> {
            protocolHandler.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        };
    }
}
```

### Domain Model Using Records and Sealed Classes

```java
package com.aronim.bookstore.domain.model;

import java.math.BigDecimal;
import java.util.UUID;

// Record for immutable value objects
public record BookDetails(
    String title,
    String isbn,
    BigDecimal price,
    Integer publicationYear,
    String description
) {
    // Compact constructor for validation
    public BookDetails {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("Title cannot be blank");
        }
        if (isbn == null || isbn.isBlank()) {
            throw new IllegalArgumentException("ISBN cannot be blank");
        }
        if (price == null || price.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Price must be positive");
        }
    }
}

// Sealed interface for book status hierarchy
public sealed interface BookStatus permits Available, Reserved, Sold, OutOfPrint {
    String getStatusName();
    boolean isAvailableForPurchase();
}

public record Available() implements BookStatus {
    @Override
    public String getStatusName() {
        return "AVAILABLE";
    }
    
    @Override
    public boolean isAvailableForPurchase() {
        return true;
    }
}

public record Reserved(UUID reservationId, String customerName) implements BookStatus {
    @Override
    public String getStatusName() {
        return "RESERVED";
    }
    
    @Override
    public boolean isAvailableForPurchase() {
        return false;
    }
}

public record Sold(UUID orderId) implements BookStatus {
    @Override
    public String getStatusName() {
        return "SOLD";
    }
    
    @Override
    public boolean isAvailableForPurchase() {
        return false;
    }
}

public record OutOfPrint() implements BookStatus {
    @Override
    public String getStatusName() {
        return "OUT_OF_PRINT";
    }
    
    @Override
    public boolean isAvailableForPurchase() {
        return false;
    }
}
```

### JPA Entity with Java 21 Features

```java
package com.aronim.bookstore.domain.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

@Entity
@Table(name = "books")
@EntityListeners(AuditingEntityListener.class)
public class BookEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @NotBlank(message = "Book title is required")
    @Column(nullable = false)
    private String title;

    @NotBlank(message = "Book ISBN is required")
    @Column(nullable = false, unique = true)
    private String isbn;

    @NotNull(message = "Book price is required")
    @Positive(message = "Book price must be positive")
    @Column(nullable = false)
    private BigDecimal price;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private CategoryEntity category;

    @ManyToMany
    @JoinTable(
        name = "book_authors",
        joinColumns = @JoinColumn(name = "book_id"),
        inverseJoinColumns = @JoinColumn(name = "author_id")
    )
    private Set<AuthorEntity> authors = new HashSet<>();

    @Column(name = "publication_year")
    private Integer publicationYear;

    @Column(length = 2000)
    private String description;
    
    @Column(name = "status", nullable = false)
    @Enumerated(EnumType.STRING)
    private BookStatusEnum status = BookStatusEnum.AVAILABLE;

    @Column(name = "created_at", nullable = false, updatable = false)
    @CreatedDate
    private Instant createdAt;

    @Column(name = "updated_at")
    @LastModifiedDate
    private Instant updatedAt;

    // Constructors, getters, setters, equals, hashCode...
    
    // Using pattern matching in methods
    public boolean canBePurchased() {
        return switch (status) {
            case AVAILABLE -> true;
            case RESERVED, SOLD, OUT_OF_PRINT -> false;
        };
    }
    
    // Text block for complex query
    public static final String FIND_AVAILABLE_BOOKS_QUERY = """
        SELECT b FROM BookEntity b
        WHERE b.status = 'AVAILABLE'
        AND b.price <= :maxPrice
        ORDER BY b.title ASC
        """;
}
```

### Service Using Virtual Threads and Pattern Matching

```java
package com.aronim.bookstore.service;

import com.aronim.bookstore.catalog.domain.entity.BookEntity;
import com.aronim.bookstore.catalog.domain.model.BookStatus;
import com.aronim.bookstore.dto.BookDTO;
import com.aronim.bookstore.exception.ResourceNotFoundException;
import com.aronim.bookstore.repository.BookRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

@Service
@Transactional(readOnly = true)
public class BookService {

    private final BookRepository bookRepository;
    private final BookMapper bookMapper;
    private final ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

    public BookService(BookRepository bookRepository, BookMapper bookMapper) {
        this.bookRepository = bookRepository;
        this.bookMapper = bookMapper;
    }

    public BookDTO findBookById(UUID id) {
        return bookRepository.findById(id)
                .map(bookMapper::toDto)
                .orElseThrow(() -> new ResourceNotFoundException("Book", "id", id));
    }
    
    // Using virtual threads for concurrent processing
    public List<BookDTO> findAllBooksWithEnrichment() throws Exception {
        List<BookEntity> books = bookRepository.findAll();
        
        // Process books concurrently using virtual threads
        var futures = books.stream()
                .map(book -> executor.submit(() -> enrichBookData(book)))
                .toList();
        
        // Gather results
        var enrichedBooks = new java.util.ArrayList<BookEntity>(books.size());
        for (var future : futures) {
            enrichedBooks.add(future.get());
        }
        
        return enrichedBooks.stream()
                .map(bookMapper::toDto)
                .toList();
    }
    
    // Using pattern matching for switch
    public String getBookAvailabilityMessage(BookDTO book) {
        return switch (book.status()) {
            case Available a -> "Book is available for purchase";
            case Reserved r -> "Book is reserved by " + r.customerName();
            case Sold s -> "Book has been sold";
            case OutOfPrint o -> "Book is out of print";
            // Pattern variable binding makes the variable available in the case arm
        };
    }
    
    // Using structured concurrency (JEP 453, preview in Java 21)
    public void processBookWithDependencies(UUID bookId) throws Exception {
        try (var scope = new java.util.concurrent.StructuredTaskScope.ShutdownOnFailure()) {
            var bookFuture = scope.fork(() -> bookRepository.findById(bookId)
                    .orElseThrow(() -> new ResourceNotFoundException("Book", "id", bookId)));
            var authorsFuture = scope.fork(() -> bookRepository.findAuthorsForBook(bookId));
            var reviewsFuture = scope.fork(() -> bookRepository.findReviewsForBook(bookId));
            
            // Wait for all tasks to complete or any to fail
            scope.join();
            scope.throwIfFailed();
            
            // All tasks completed successfully
            var book = bookFuture.get();
            var authors = authorsFuture.get();
            var reviews = reviewsFuture.get();
            
            // Process the results...
        }
    }
    
    private BookEntity enrichBookData(BookEntity book) {
        // Simulate enrichment that might involve external API calls
        try {
            Thread.sleep(100); // Simulate work
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return book;
    }
}
```

### Testing with Java 21 Features

```java
package com.aronim.bookstore.service;

import com.aronim.bookstore.catalog.domain.entity.BookEntity;
import com.aronim.bookstore.catalog.domain.model.Available;
import com.aronim.bookstore.catalog.domain.model.BookStatus;
import com.aronim.bookstore.catalog.domain.model.OutOfPrint;
import com.aronim.bookstore.catalog.domain.model.Reserved;
import com.aronim.bookstore.dto.BookDTO;
import com.aronim.bookstore.exception.ResourceNotFoundException;
import com.aronim.bookstore.repository.BookRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BookServiceTest {

    @Mock
    private BookRepository bookRepository;

    @Mock
    private BookMapper bookMapper;

    @InjectMocks
    private BookService bookService;

    private UUID bookId;
    private BookEntity bookEntity;
    private BookDTO bookDTO;

    @BeforeEach
    void setUp() {
        bookId = UUID.randomUUID();
        
        bookEntity = new BookEntity();
        bookEntity.setId(bookId);
        bookEntity.setTitle("Test Book");
        bookEntity.setIsbn("1234567890");
        bookEntity.setPrice(BigDecimal.valueOf(29.99));
        
        // Using records
        var bookDetails = new BookDTO(
            bookId,
            "Test Book",
            "1234567890",
            BigDecimal.valueOf(29.99),
            null,
            null,
            new Available(),
            null
        );
        
        bookDTO = bookDetails;
    }

    @Test
    void findBookById_WhenBookExists_ShouldReturnBook() {
        // Given
        when(bookRepository.findById(bookId)).thenReturn(Optional.of(bookEntity));
        when(bookMapper.toDto(bookEntity)).thenReturn(bookDTO);

        // When
        var result = bookService.findBookById(bookId);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.title()).isEqualTo("Test Book");
        verify(bookRepository).findById(bookId);
        verify(bookMapper).toDto(bookEntity);
    }

    @Test
    void getBookAvailabilityMessage_WithDifferentStatuses_ShouldReturnCorrectMessage() {
        // Given
        var availableBook = new BookDTO(
            UUID.randomUUID(),
            "Available Book",
            "1111111111",
            BigDecimal.valueOf(19.99),
            null,
            null,
            new Available(),
            null
        );
        
        var reservedBook = new BookDTO(
            UUID.randomUUID(),
            "Reserved Book",
            "2222222222",
            BigDecimal.valueOf(29.99),
            null,
            null,
            new Reserved(UUID.randomUUID(), "John Doe"),
            null
        );
        
        var outOfPrintBook = new BookDTO(
            UUID.randomUUID(),
            "Out of Print Book",
            "3333333333",
            BigDecimal.valueOf(39.99),
            null,
            null,
            new OutOfPrint(),
            null
        );

        // When
        var availableMessage = bookService.getBookAvailabilityMessage(availableBook);
        var reservedMessage = bookService.getBookAvailabilityMessage(reservedBook);
        var outOfPrintMessage = bookService.getBookAvailabilityMessage(outOfPrintBook);

        // Then
        assertThat(availableMessage).isEqualTo("Book is available for purchase");
        assertThat(reservedMessage).contains("Book is reserved by John Doe");
        assertThat(outOfPrintMessage).isEqualTo("Book is out of print");
    }

    // More tests...
}
```

## Java 21 Feature Adoption Plan

1. **Immediate Adoption**
   - Records for DTOs and value objects
   - Pattern matching for switch
   - Text blocks for multiline strings
   - Sealed classes for domain model hierarchies

2. **Phased Adoption**
   - Virtual threads for I/O-bound operations
   - Structured concurrency for complex asynchronous flows
   - Foreign Function & Memory API for specific performance-critical sections

3. **Preview Features (with caution)**
   - String templates (preview in JDK 21)
   - Unnamed patterns and variables (preview in JDK 21)
   - Record patterns (preview in JDK 21)

## Compliance Verification
- Setup of Java-specific linting tools with Java 21 support
- Integration with static analysis tools (e.g., SonarQube with Java 21 rules)
- Code review guidelines for Java 21 features
- Unit testing requirements with focus on new language features
- Documentation standards for Java APIs
- Performance testing of virtual threads implementation

## References
- Java 21 Documentation: https://docs.oracle.com/en/java/javase/21/
- JDK 21 Release Notes: https://jdk.java.net/21/release-notes
- Spring Boot with Java 21: https://spring.io/blog/2023/05/25/spring-boot-3-1-0-available-now
- Inside Java Newscast (Virtual Threads): https://inside.java/2021/10/05/insidejava-newscast-16/
- Java 21 Features: https://openjdk.org/projects/jdk/21/
- Virtual Threads in Spring Boot: https://spring.io/blog/2022/10/11/embracing-virtual-threads
- Modern Java in Action (Book): https://www.manning.com/books/modern-java-in-action
