# ADR-026: Adoption of Backend-for-Frontend (BFF) Pattern

## Status
Proposed

## Date
2025-03-02

## Context
The Aronim Bookstore application has a modular backend architecture (Modulith) and is adopting a micro-frontend approach for the client side. This creates challenges in efficiently connecting these frontend components with the backend services while maintaining:

- Optimal data delivery for specific frontend needs
- Security and authentication across multiple clients
- Consistent API design and user experience
- Performance optimization for different client types
- Simplified frontend development with backend integration
- Reduced network overhead and API chattiness
- Support for our micro-frontend architecture
- Clear separation of concerns between layers

Direct communication between micro-frontends and backend services could lead to increased complexity, redundant API calls, security vulnerabilities, and performance issues. Additionally, different client types (web, mobile, third-party integrations) may have varying data and interaction requirements.

## Decision
We will implement the **Backend-for-Frontend (BFF) pattern** with the following characteristics:

### 1. Architecture Approach
- Create dedicated BFF services tailored to specific frontend clients
- Implement a primary web BFF aligned with our micro-frontend architecture
- Design BFFs as API gateways that aggregate and transform data from backend services
- Align BFF boundaries with micro-frontend domain boundaries
- Implement proper authentication and authorization at the BFF layer

### 2. Technical Implementation
- Develop BFFs using **Spring Boot** to align with our backend technology stack
- Use **GraphQL** as the primary API interface for flexible data fetching
- Implement efficient caching strategies at the BFF layer
- Configure proper CORS policies for security
- Establish resilience patterns (circuit breakers, retries, fallbacks)
- Implement request/response compression for performance

### 3. Development Approach
- Create clear contracts between BFFs and micro-frontends
- Establish standards for API design and error handling
- Implement monitoring and observability at the BFF layer
- Use API documentation tools for clear interface specifications
- Create development tooling for BFF testing and simulation

### 4. Deployment Strategy
- Deploy BFFs independently from backend services
- Configure appropriate scaling based on frontend traffic patterns
- Implement blue/green deployment for zero-downtime updates
- Set up proper health checks and monitoring

## Implementation Approach

1. **BFF Service Development**
   - Create a core BFF framework with shared functionality
   - Implement domain-specific BFF modules aligned with micro-frontends
   - Set up authentication and authorization mechanisms
   - Establish logging, monitoring, and tracing infrastructure

2. **API Layer Implementation**
   - Develop GraphQL schema aligned with frontend data requirements
   - Implement efficient resolvers for backend service integration
   - Set up subscription support for real-time features
   - Create standardized error handling and response formatting

3. **Integration with Micro-Frontends**
   - Establish communication patterns between micro-frontends and BFFs
   - Implement client-side caching strategies
   - Create frontend API client libraries for consistent interaction
   - Set up development proxies for local testing

4. **Performance Optimization**
   - Implement response compression
   - Configure appropriate caching strategies
   - Optimize payload size through GraphQL field selection
   - Set up connection pooling for backend service communication

## Consequences

### Positive
- Tailored APIs optimized for specific frontend needs
- Reduced network traffic through aggregated API calls
- Improved frontend performance with optimized data delivery
- Enhanced security with centralized authentication and authorization
- Better separation of concerns between frontend and backend
- Simplified frontend development with backend abstraction
- Improved maintainability through focused BFF services
- More efficient handling of client-specific requirements
- Better support for our micro-frontend architecture
- Centralized point for monitoring frontend-facing APIs

### Negative
- Additional architectural complexity with new service layer
- Potential duplication of logic across different BFFs
- Need for careful governance to prevent BFF sprawl
- Additional operational overhead for deployment and maintenance
- Risk of creating a bottleneck if not properly designed
- Potential increased latency if not optimized
- Need for additional testing and quality assurance
- Requires strong API design discipline

## Alternatives Considered

1. **Direct API Communication**
   - Simpler architecture with fewer components
   - No additional service layer to maintain
   - Increased coupling between frontend and backend services
   - More network overhead with multiple API calls
   - Less optimized for specific frontend needs
   - Potential security concerns with direct backend access

2. **Shared API Gateway**
   - Single entry point for all API requests
   - Centralized authentication and routing
   - Less tailored to specific frontend requirements
   - Potential bottleneck for all API traffic
   - More complex configuration for varied client needs
   - Less alignment with micro-frontend architecture

3. **Client-Side API Composition**
   - Simplified backend architecture
   - More flexibility for frontend implementations
   - Increased network overhead
   - Security concerns with multiple service endpoints
   - Performance issues with multiple round-trips
   - Duplication of composition logic across clients

4. **GraphQL Federation**
   - Unified schema across multiple services
   - Strong typing and introspection capabilities
   - More complex implementation and maintenance
   - Requires GraphQL adoption across all services
   - Potential performance challenges with complex queries
   - Higher learning curve for development teams

## Implementation Notes

### BFF Service Structure

```java
// WebBffApplication.java
@SpringBootApplication
@EnableWebSecurity
public class WebBffApplication {
    public static void main(String[] args) {
        SpringApplication.run(WebBffApplication.class, args);
    }
}
```

### GraphQL Schema Definition

```graphql
# schema.graphqls
type Query {
    bookById(id: ID!): Book
    searchBooks(query: String!, page: Int, size: Int): BookConnection!
    featuredBooks(count: Int): [Book!]!
    userProfile: User
    cartItems: [CartItem!]!
}

type Mutation {
    addToCart(bookId: ID!, quantity: Int!): CartItem!
    removeFromCart(itemId: ID!): Boolean!
    updateQuantity(itemId: ID!, quantity: Int!): CartItem!
    checkout(paymentDetails: PaymentInput!): Order!
}

type Subscription {
    cartUpdates: CartUpdate!
}

type Book {
    id: ID!
    title: String!
    author: Author!
    price: Money!
    coverImage: String
    rating: Float
    description: String
    categories: [Category!]!
    relatedBooks: [Book!]!
    availability: StockStatus!
}

type Author {
    id: ID!
    name: String!
    biography: String
    photo: String
    books: [Book!]!
}

type Category {
    id: ID!
    name: String!
    books: [Book!]!
}

type BookConnection {
    items: [Book!]!
    totalCount: Int!
    hasNext: Boolean!
}

type User {
    id: ID!
    name: String!
    email: String!
    wishlist: [Book!]!
    orderHistory: [Order!]!
}

type CartItem {
    id: ID!
    book: Book!
    quantity: Int!
    price: Money!
}

type Order {
    id: ID!
    items: [CartItem!]!
    total: Money!
    status: OrderStatus!
    createdAt: String!
}

type Money {
    amount: Float!
    currency: String!
}

enum StockStatus {
    IN_STOCK
    LOW_STOCK
    OUT_OF_STOCK
    PRE_ORDER
}

enum OrderStatus {
    PENDING
    PAID
    SHIPPED
    DELIVERED
    CANCELLED
}

input PaymentInput {
    cardNumber: String!
    expiryMonth: Int!
    expiryYear: Int!
    cvv: String!
    nameOnCard: String!
}

type CartUpdate {
    type: CartUpdateType!
    item: CartItem
}

enum CartUpdateType {
    ADDED
    REMOVED
    UPDATED
    CLEARED
}
```

### GraphQL Resolver Implementation

```java
// BookResolver.java
@Component
public class BookResolver implements GraphQLQueryResolver {
    
    private final CatalogServiceClient catalogService;
    private final ReviewServiceClient reviewService;
    private final InventoryServiceClient inventoryService;
    
    public BookResolver(CatalogServiceClient catalogService, 
                        ReviewServiceClient reviewService,
                        InventoryServiceClient inventoryService) {
        this.catalogService = catalogService;
        this.reviewService = reviewService;
        this.inventoryService = inventoryService;
    }
    
    public BookDTO bookById(String id) {
        BookDTO book = catalogService.getBookById(id);
        if (book != null) {
            // Enrich with additional data
            book.setRating(reviewService.getAverageRating(id));
            book.setAvailability(inventoryService.getStockStatus(id));
        }
        return book;
    }
    
    public BookConnection searchBooks(String query, Integer page, Integer size) {
        page = page != null ? page : 0;
        size = size != null ? size : 20;
        
        SearchResult<BookDTO> result = catalogService.searchBooks(query, page, size);
        
        // Transform to GraphQL type
        BookConnection connection = new BookConnection();
        connection.setItems(result.getItems());
        connection.setTotalCount(result.getTotalCount());
        connection.setHasNext(result.isHasNext());
        
        return connection;
    }
    
    public List<BookDTO> featuredBooks(Integer count) {
        count = count != null ? count : 10;
        return catalogService.getFeaturedBooks(count);
    }
}
```

### Backend Service Client

```java
// CatalogServiceClient.java
@Service
public class CatalogServiceClient {
    
    private final WebClient webClient;
    private final CircuitBreaker circuitBreaker;
    
    public CatalogServiceClient(WebClient.Builder webClientBuilder,
                               CircuitBreakerFactory circuitBreakerFactory) {
        this.webClient = webClientBuilder
            .baseUrl("http://catalog-service")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
        
        this.circuitBreaker = circuitBreakerFactory.create("catalogService");
    }
    
    public BookDTO getBookById(String id) {
        return circuitBreaker.run(
            () -> webClient.get()
                .uri("/api/books/{id}", id)
                .retrieve()
                .bodyToMono(BookDTO.class)
                .block(),
            throwable -> getFallbackBook(id, throwable)
        );
    }
    
    public SearchResult<BookDTO> searchBooks(String query, int page, int size) {
        return circuitBreaker.run(
            () -> webClient.get()
                .uri(uriBuilder -> uriBuilder
                    .path("/api/books/search")
                    .queryParam("query", query)
                    .queryParam("page", page)
                    .queryParam("size", size)
                    .build())
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<SearchResult<BookDTO>>() {})
                .block(),
            throwable -> getFallbackSearchResult(throwable)
        );
    }
    
    public List<BookDTO> getFeaturedBooks(int count) {
        return circuitBreaker.run(
            () -> webClient.get()
                .uri(uriBuilder -> uriBuilder
                    .path("/api/books/featured")
                    .queryParam("count", count)
                    .build())
                .retrieve()
                .bodyToFlux(BookDTO.class)
                .collectList()
                .block(),
            throwable -> getFallbackFeaturedBooks(throwable)
        );
    }
    
    private BookDTO getFallbackBook(String id, Throwable throwable) {
        // Log error
        // Return empty or cached result
        return null;
    }
    
    private SearchResult<BookDTO> getFallbackSearchResult(Throwable throwable) {
        // Log error
        return new SearchResult<>(Collections.emptyList(), 0, false);
    }
    
    private List<BookDTO> getFallbackFeaturedBooks(Throwable throwable) {
        // Log error
        return Collections.emptyList();
    }
}
```

### Authentication Configuration

```java
// SecurityConfig.java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/graphql").permitAll()
                .requestMatchers("/graphiql").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(jwt -> {}))
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .build();
    }
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList(
            "https://bookstore.aronim.com", 
            "https://*.aronim.com"
        ));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("Authorization", "Content-Type"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

### Caching Configuration

```java
// CacheConfig.java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("books", "authors", "categories");
    }
    
    @Bean
    public CacheResolver bookCacheResolver(CacheManager cacheManager) {
        return new SimpleCacheResolver(cacheManager);
    }
}
```

### Resilience Configuration

```java
// ResilienceConfig.java
@Configuration
public class ResilienceConfig {

    @Bean
    public CircuitBreakerFactory circuitBreakerFactory() {
        SimpleCircuitBreakerFactory factory = new SimpleCircuitBreakerFactory();
        factory.configureDefault(id -> new SimpleCircuitBreakerConfig()
            .slidingWindowSize(10)
            .failureRateThreshold(50)
            .waitDurationInOpenState(Duration.ofSeconds(30))
            .permittedNumberOfCallsInHalfOpenState(5)
            .build());
        return factory;
    }
    
    @Bean
    public RetryFactory retryFactory() {
        SimpleRetryFactory factory = new SimpleRetryFactory();
        factory.configureDefault(id -> new SimpleRetryConfig()
            .maxAttempts(3)
            .waitDuration(Duration.ofMillis(100))
            .retryExceptions(IOException.class, TimeoutException.class)
            .build());
        return factory;
    }
}
```

### API Documentation

```java
// GraphQLConfig.java
@Configuration
public class GraphQLConfig {

    @Bean
    public SchemaGeneratorConfig schemaGeneratorConfig() {
        return SchemaGeneratorConfig.builder()
            .typeInfoGenerator(new TypeInfoGenerator())
            .build();
    }
    
    @Bean
    public GraphQLSchema graphQLSchema() {
        return SchemaGenerator.generateSchema(
            schemaGeneratorConfig(),
            SchemaParser.newParser()
                .file("schema.graphqls")
                .build()
                .parse()
        );
    }
    
    @Bean
    public GraphQL graphQL(GraphQLSchema graphQLSchema) {
        return GraphQL.newGraphQL(graphQLSchema)
            .instrumentation(new TracingInstrumentation())
            .build();
    }
}
```

### CI/CD Pipeline for BFF Service

```yaml
# .github/workflows/web-bff-service.yml
name: Web BFF Service CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'bff/web-bff/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'bff/web-bff/**'

jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
      
      - name: Build with Gradle
        working-directory: bff/web-bff
        run: ./gradlew build
      
      - name: Run tests
        working-directory: bff/web-bff
        run: ./gradlew test
      
      - name: Build Docker image
        working-directory: bff/web-bff
        run: ./gradlew bootBuildImage
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: web-bff-jar
          path: bff/web-bff/build/libs/*.jar
  
  deploy:
    name: Deploy
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: web-bff-jar
          path: app
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: aronim-bookstore/web-bff
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -t $ECR_REGISTRY/$ECR_REPOSITORY:latest .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service --cluster aronim-bookstore --service web-bff-service --force-new-deployment
```

## Performance Optimization

### Response Compression

```java
// CompressionConfig.java
@Configuration
public class CompressionConfig {
    
    @Bean
    public GzipWebFilterFactory gzipWebFilterFactory() {
        return new GzipWebFilterFactory();
    }
    
    @Bean
    public WebFilter gzipWebFilter() {
        return gzipWebFilterFactory().getWebFilter();
    }
}
```

## Compliance Verification
- Performance testing of API response times
- Load testing to verify BFF scalability
- Security audit of authentication and authorization mechanisms
- Verification of proper error handling and fallback mechanisms
- Testing of resilience patterns under failure conditions
- Documentation review for API contracts
- Validation of monitoring and observability setup

## References
- Backend-for-Frontend Pattern: https://samnewman.io/patterns/architectural/bff/
- GraphQL Documentation: https://graphql.org/learn/
- Spring Boot Documentation: https://spring.io/projects/spring-boot
- API Gateway Patterns: https://microservices.io/patterns/apigateway.html
- Resilience4j Documentation: https://resilience4j.readme.io/
- REST API Design Best Practices: https://restfulapi.net/
- Micro-Frontends with GraphQL: https://micro-frontends.org/
- API Security Best Practices: https://owasp.org/www-project-api-security/
