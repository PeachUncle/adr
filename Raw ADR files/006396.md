# ADR-017: Caching Strategy for Spring Boot Application

## Status
Accepted

## Date
2025-03-01

## Context
Our application needs to handle significant read traffic efficiently while maintaining data consistency and system performance. We need a caching strategy that:

- Improves response times for frequently accessed data
- Reduces database load for read-heavy operations
- Maintains reasonable memory usage
- Ensures data consistency when underlying data changes
- Provides appropriate cache invalidation mechanisms
- Integrates well with our Spring Boot architecture
- Supports distributed caching for scalability
- Can be monitored and managed in production
- Allows for different caching policies based on data characteristics
- Balances performance improvements with operational complexity

Without an effective caching strategy, our application may experience performance bottlenecks, increased database load, higher latency, and scalability challenges as user traffic grows.

## Decision
We will implement a multi-level caching strategy using Spring Cache Abstraction as the foundation with the following components:

### 1. Caching Framework
- Use **Spring Cache Abstraction** as the primary caching API
- Implement **Caffeine** as the local in-memory cache provider
- Add **Redis** as a second-level distributed cache for clustered environments
- Configure a layered approach with local caches backed by distributed cache

### 2. Cache Regions and Policies
- Define distinct cache regions based on entity types and access patterns
- Implement different TTL (Time-To-Live) settings based on data volatility
- Configure size limits appropriate to the importance and access frequency of data
- Use write-through caching for critical data that must remain consistent

### 3. Cache Invalidation Strategy
- Use time-based expiration as the primary invalidation mechanism
- Implement event-based cache eviction for data modifications
- Use cache versioning for critical data to prevent stale reads
- Configure cache eviction policies (LRU, size-based) appropriate to each cache region

### 4. Integration Points
- Cache service layer responses for read operations
- Apply caching to expensive computations and aggregations
- Selectively cache repository results for frequently accessed entities
- Implement HTTP caching headers for API responses where appropriate

### 5. Operational Approach
- Expose cache statistics via Spring Boot Actuator
- Implement cache warmup procedures for critical data after deployment
- Provide administrative endpoints for cache management
- Monitor cache hit rates and adjust policies based on observed patterns

## Implementation Approach

1. **Cache Configuration**
   - Configure Spring Cache Abstraction with appropriate cache managers
   - Define cache regions with specific policies
   - Implement a composite cache manager for multi-level caching
   - Configure TTL, size limits, and eviction policies

2. **Application Integration**
   - Use declarative caching with `@Cacheable`, `@CachePut`, and `@CacheEvict` annotations
   - Implement cache keys that properly represent the cached data
   - Use SpEL expressions for dynamic cache key generation
   - Apply conditional caching based on context or data size

3. **Cache Consistency**
   - Implement cache synchronization mechanisms for distributed environments
   - Use cache versioning for critical data
   - Apply appropriate transaction boundaries for cache operations
   - Implement event-driven cache invalidation for data changes

4. **Monitoring and Management**
   - Expose cache statistics through Actuator endpoints
   - Implement cache health indicators
   - Create dashboards for cache performance monitoring
   - Configure alerts for cache-related issues

## Consequences

### Positive
- Significantly improved response times for cached data
- Reduced database load for frequently accessed data
- Better scalability for read-heavy operations
- Ability to handle traffic spikes more effectively
- Lower operational costs through reduced resource usage
- Improved user experience due to faster response times
- Protection of backend systems from excessive load
- Flexibility to adjust caching policies as needs evolve

### Negative
- Increased system complexity with cache management
- Potential for stale data if invalidation is not handled properly
- Additional memory consumption for cached data
- Risk of cache stampedes without proper protection
- Learning curve for developers to use caching effectively
- Debugging challenges when issues occur
- Additional operational overhead for monitoring and management
- Potential inconsistencies in distributed environments

## Alternatives Considered

1. **No Explicit Caching**
   - Rely solely on database query caching
   - Simpler implementation and maintenance
   - Limited performance benefits
   - No control over caching behavior
   - Missed opportunity for significant performance improvements

2. **Database-Only Optimizations**
   - Focus on query optimization and indexing
   - Use materialized views for aggregated data
   - Complementary to caching but not a replacement
   - Limited scalability benefits
   - Higher database resource usage

3. **Full-Page Caching**
   - Cache entire HTTP responses
   - Simpler implementation for some use cases
   - Less flexibility for dynamic content
   - Challenges with personalized content
   - Limited to web interfaces

4. **Custom Cache Implementation**
   - Tailored exactly to application needs
   - Higher development and maintenance effort
   - No community support
   - Risk of bugs in cache logic
   - Reinventing well-solved problems

## Implementation Notes

### Gradle Dependencies (Kotlin DSL)

```kotlin
dependencies {
    // Spring Cache abstraction
    implementation("org.springframework.boot:spring-boot-starter-cache")
    
    // Caffeine cache
    implementation("com.github.ben-manes.caffeine:caffeine:3.1.1")
    
    // Redis cache (for distributed caching)
    implementation("org.springframework.boot:spring-boot-starter-data-redis")
    
    // Optional: Redisson for advanced Redis features
    implementation("org.redisson:redisson-spring-boot-starter:3.17.4")
}
```

### Cache Configuration

```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CacheManager cacheManager(
            CaffeineCacheManager caffeineCacheManager,
            RedisCacheManager redisCacheManager) {
        
        // Create a composite cache manager that tries local cache first, then Redis
        CompositeCacheManager compositeCacheManager = new CompositeCacheManager();
        compositeCacheManager.setCacheManagers(List.of(caffeineCacheManager, redisCacheManager));
        compositeCacheManager.setFallbackToNoOpCache(false);
        
        return compositeCacheManager;
    }
    
    @Bean
    public CaffeineCacheManager caffeineCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        
        // Configure different caches with different policies
        cacheManager.setCacheSpecification("products=maximumSize=1000,expireAfterWrite=1h");
        cacheManager.setCacheSpecification("categories=maximumSize=100,expireAfterWrite=24h");
        cacheManager.setCacheSpecification("customerLookup=maximumSize=10000,expireAfterWrite=30m");
        cacheManager.setCacheSpecification("productRecommendations=maximumSize=500,expireAfterWrite=2h");
        
        // Enable statistics for monitoring
        cacheManager.setCaffeine(Caffeine.newBuilder()
                .recordStats());
        
        return cacheManager;
    }
    
    @Bean
    public RedisCacheManager redisCacheManager(RedisConnectionFactory connectionFactory) {
        // Default cache configuration
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofHours(1))
                .serializeKeysWith(RedisSerializationContext.SerializationPair.fromSerializer(new StringRedisSerializer()))
                .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()))
                .disableCachingNullValues();
        
        // Configure different caches with different TTL values
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        cacheConfigurations.put("products", defaultConfig.entryTtl(Duration.ofHours(2)));
        cacheConfigurations.put("categories", defaultConfig.entryTtl(Duration.ofHours(24)));
        cacheConfigurations.put("customerLookup", defaultConfig.entryTtl(Duration.ofMinutes(30)));
        cacheConfigurations.put("productRecommendations", defaultConfig.entryTtl(Duration.ofHours(3)));
        
        return RedisCacheManager.builder(connectionFactory)
                .cacheDefaults(defaultConfig)
                .withInitialCacheConfigurations(cacheConfigurations)
                .transactionAware()
                .build();
    }
    
    @Bean
    public CacheMetricsRegistrar cacheMetricsRegistrar(MeterRegistry registry, CacheManager cacheManager) {
        return new CacheMetricsRegistrar(registry, cacheManager);
    }
}
```

### Service Layer Caching

```java
@Service
public class ProductService {
    
    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;
    
    public ProductService(ProductRepository productRepository, CategoryRepository categoryRepository) {
        this.productRepository = productRepository;
        this.categoryRepository = categoryRepository;
    }
    
    @Cacheable(value = "products", key = "#id", unless = "#result == null")
    public Optional<ProductDTO> findProductById(UUID id) {
        return productRepository.findById(id)
                .map(this::convertToDto);
    }
    
    @Cacheable(value = "productsByCategory", key = "#categoryId")
    public List<ProductDTO> findProductsByCategory(UUID categoryId) {
        return productRepository.findByCategoryId(categoryId).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }
    
    @CachePut(value = "products", key = "#result.id")
    public ProductDTO createProduct(ProductDTO productDTO) {
        Product product = new Product();
        updateProductFromDto(product, productDTO);
        
        Product savedProduct = productRepository.save(product);
        
        // Evict related caches that might contain lists including this product
        evictRelatedCaches(savedProduct);
        
        return convertToDto(savedProduct);
    }
    
    @CachePut(value = "products", key = "#id")
    public Optional<ProductDTO> updateProduct(UUID id, ProductDTO productDTO) {
        return productRepository.findById(id)
                .map(product -> {
                    // Store old category for cache eviction
                    UUID oldCategoryId = product.getCategory() != null ? 
                        product.getCategory().getId() : null;
                    
                    updateProductFromDto(product, productDTO);
                    Product updatedProduct = productRepository.save(product);
                    
                    // Evict category caches if category changed
                    if (oldCategoryId != null && 
                        !oldCategoryId.equals(updatedProduct.getCategory().getId())) {
                        evictCategoryProductsCache(oldCategoryId);
                        evictCategoryProductsCache(updatedProduct.getCategory().getId());
                    } else {
                        evictRelatedCaches(updatedProduct);
                    }
                    
                    return convertToDto(updatedProduct);
                });
    }
    
    @CacheEvict(value = "products", key = "#id")
    public void deleteProduct(UUID id) {
        // Find product first to get related data for cache eviction
        productRepository.findById(id).ifPresent(product -> {
            productRepository.delete(product);
            evictRelatedCaches(product);
        });
    }
    
    @Cacheable(value = "productRecommendations", key = "#productId")
    public List<ProductDTO> getProductRecommendations(UUID productId) {
        // Expensive operation to calculate recommendations
        return calculateRecommendations(productId);
    }
    
    @CacheEvict(value = "categories", allEntries = true)
    @Scheduled(fixedRateString = "${cache.categories.refresh.rate:86400000}")
    public void evictAllCategoriesCache() {
        // Evict all entries from categories cache once per day
    }
    
    // Helper methods
    private void evictRelatedCaches(Product product) {
        if (product.getCategory() != null) {
            evictCategoryProductsCache(product.getCategory().getId());
        }
    }
    
    @CacheEvict(value = "productsByCategory", key = "#categoryId")
    public void evictCategoryProductsCache(UUID categoryId) {
        // Method is empty as the annotation handles the cache eviction
    }
    
    private List<ProductDTO> calculateRecommendations(UUID productId) {
        // Complex recommendation logic here
        return productRepository.findRelatedProducts(productId).stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }
    
    private ProductDTO convertToDto(Product product) {
        // Mapping logic
    }
    
    private void updateProductFromDto(Product product, ProductDTO dto) {
        // Update logic
    }
}
```

### Conditional Caching

```java
@Cacheable(value = "largeReports", key = "#reportId", 
    condition = "#result != null && #result.size() > 100",
    unless = "#reportId.startsWith('TEMP_')")
public List<ReportDataDTO> generateLargeReport(String reportId, ReportCriteria criteria) {
    // Expensive report generation logic
    return reportGenerator.createReport(reportId, criteria);
}
```

### Cache Key Generation

```java
@Cacheable(value = "searchResults", keyGenerator = "customKeyGenerator")
public Page<ProductDTO> searchProducts(ProductSearchCriteria criteria, Pageable pageable) {
    // Complex search logic
    return productSearchService.search(criteria, pageable);
}

@Component
public class CustomKeyGenerator implements KeyGenerator {
    
    @Override
    public Object generate(Object target, Method method, Object... params) {
        StringBuilder sb = new StringBuilder();
        sb.append(target.getClass().getSimpleName()).append(".");
        sb.append(method.getName());
        
        for (Object param : params) {
            if (param instanceof ProductSearchCriteria) {
                ProductSearchCriteria criteria = (ProductSearchCriteria) param;
                sb.append(":").append(criteria.getQuery())
                  .append(":").append(criteria.getMinPrice())
                  .append(":").append(criteria.getMaxPrice())
                  .append(":").append(criteria.getCategoryId());
            } else if (param instanceof Pageable) {
                Pageable pageable = (Pageable) param;
                sb.append(":p").append(pageable.getPageNumber())
                  .append(":s").append(pageable.getPageSize());
                
                if (pageable.getSort() != null) {
                    pageable.getSort().forEach(order -> 
                        sb.append(":").append(order.getProperty())
                          .append(":").append(order.getDirection()));
                }
            } else {
                sb.append(":").append(param.toString());
            }
        }
        
        return sb.toString();
    }
}
```

### Cache Synchronization with Events

```java
@Service
public class ProductEventHandler {
    
    private final CacheManager cacheManager;
    
    public ProductEventHandler(CacheManager cacheManager) {
        this.cacheManager = cacheManager;
    }
    
    @EventListener
    public void handleProductUpdatedEvent(ProductUpdatedEvent event) {
        // Evict specific product cache entry
        Cache productCache = cacheManager.getCache("products");
        if (productCache != null) {
            productCache.evict(event.getProductId());
        }
        
        // Evict category products cache if category changed
        if (event.isCategoryChanged()) {
            Cache categoryCache = cacheManager.getCache("productsByCategory");
            if (categoryCache != null) {
                categoryCache.evict(event.getOldCategoryId());
                categoryCache.evict(event.getNewCategoryId());
            }
        }
    }
    
    @EventListener
    public void handleCategoryUpdatedEvent(CategoryUpdatedEvent event) {
        // Evict category cache
        Cache categoryCache = cacheManager.getCache("categories");
        if (categoryCache != null) {
            categoryCache.evict(event.getCategoryId());
        }
        
        // Evict products by category cache
        Cache productsByCategoryCache = cacheManager.getCache("productsByCategory");
        if (productsByCategoryCache != null) {
            productsByCategoryCache.evict(event.getCategoryId());
        }
    }
}
```

### HTTP Response Caching

```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {
    
    private final ProductService productService;
    
    public ProductController(ProductService productService) {
        this.productService = productService;
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<ProductDTO> getProduct(@PathVariable UUID id) {
        return productService.findProductById(id)
                .map(product -> ResponseEntity.ok()
                        .cacheControl(CacheControl.maxAge(30, TimeUnit.MINUTES)
                                .mustRevalidate())
                        .eTag(Integer.toString(product.hashCode()))
                        .body(product))
                .orElse(ResponseEntity.notFound().build());
    }
    
    @GetMapping("/category/{categoryId}")
    public ResponseEntity<List<ProductDTO>> getProductsByCategory(@PathVariable UUID categoryId) {
        List<ProductDTO> products = productService.findProductsByCategory(categoryId);
        
        return ResponseEntity.ok()
                .cacheControl(CacheControl.maxAge(10, TimeUnit.MINUTES))
                .body(products);
    }
    
    @GetMapping("/recommendations/{productId}")
    public ResponseEntity<List<ProductDTO>> getProductRecommendations(@PathVariable UUID productId) {
        List<ProductDTO> recommendations = productService.getProductRecommendations(productId);
        
        return ResponseEntity.ok()
                .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS))
                .body(recommendations);
    }
}
```

### Cache Monitoring and Management

```java
@RestController
@RequestMapping("/management/cache")
public class CacheManagementController {
    
    private final CacheManager cacheManager;
    
    public CacheManagementController(CacheManager cacheManager) {
        this.cacheManager = cacheManager;
    }
    
    @GetMapping
    public Map<String, Object> getCacheInfo() {
        Map<String, Object> result = new HashMap<>();
        
        cacheManager.getCacheNames().forEach(cacheName -> {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache instanceof CaffeineCache) {
                CaffeineCache caffeineCache = (CaffeineCache) cache;
                com.github.benmanes.caffeine.cache.Cache<Object, Object> nativeCache = 
                    caffeineCache.getNativeCache();
                
                Map<String, Object> cacheStats = new HashMap<>();
                cacheStats.put("size", nativeCache.estimatedSize());
                
                if (nativeCache.stats() != null) {
                    CacheStats stats = nativeCache.stats();
                    cacheStats.put("hitRate", stats.hitRate());
                    cacheStats.put("missRate", stats.missRate());
                    cacheStats.put("evictionCount", stats.evictionCount());
                }
                
                result.put(cacheName, cacheStats);
            }
        });
        
        return result;
    }
    
    @DeleteMapping("/{cacheName}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void clearCache(@PathVariable String cacheName) {
        Cache cache = cacheManager.getCache(cacheName);
        if (cache != null) {
            cache.clear();
        }
    }
    
    @DeleteMapping
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void clearAllCaches() {
        cacheManager.getCacheNames().forEach(cacheName -> {
            Cache cache = cacheManager.getCache(cacheName);
            if (cache != null) {
                cache.clear();
            }
        });
    }
}
```

## Configuration Properties

```yaml
spring:
  cache:
    type: caffeine
    cache-names: products,categories,customerLookup,productsByCategory,productRecommendations
    caffeine:
      spec: maximumSize=1000,expireAfterWrite=1h
  
  redis:
    host: ${REDIS_HOST:localhost}
    port: ${REDIS_PORT:6379}
    password: ${REDIS_PASSWORD:}
    timeout: 2000
    
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,caches
  metrics:
    cache:
      instrument: true

cache:
  ttl:
    products: 3600  # 1 hour in seconds
    categories: 86400  # 24 hours in seconds
    customerLookup: 1800  # 30 minutes in seconds
    productRecommendations: 7200  # 2 hours in seconds
  size:
    products: 1000
    categories: 100
    customerLookup: 10000
    productRecommendations: 500
```

## Compliance Verification
- Performance testing with and without caching enabled
- Monitoring of cache hit/miss rates in production
- Load testing to verify cache behavior under high traffic
- Verification of cache consistency mechanisms
- Testing of cache eviction policies
- Review of memory usage patterns
- Validation of cache TTL settings against data volatility
- Penetration testing to ensure cached data doesn't expose security vulnerabilities

## References
- Spring Cache Abstraction: https://docs.spring.io/spring-framework/docs/current/reference/html/integration.html#cache
- Caffeine Cache Documentation: https://github.com/ben-manes/caffeine/wiki
- Spring Data Redis Cache: https://docs.spring.io/spring-data/redis/docs/current/reference/html/#redis:support:cache
- Cache Design Patterns: https://caching.pspdfkit.com/cache-design-patterns/
- Cache-Aside Pattern: https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside
- Caching Best Practices: https://aws.amazon.com/caching/best-practices/
- HTTP Caching: https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
