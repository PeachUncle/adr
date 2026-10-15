# ADR-0006: API Integration Architecture

## Status
Accepted

## Context
The Huda Al-Quran application requires integration with multiple external APIs to provide comprehensive Islamic services:

- **Prayer Times**: Real-time calculation based on geographic location
- **Location Services**: GPS coordinates to city/country mapping
- **Audio Recitation**: Quran verse audio files from various reciters
- **Future APIs**: Quran translation, tafsir, Islamic calendar

The API integration needed to address:

- Multiple API endpoints with different data formats
- Rate limiting and error handling
- Offline fallback mechanisms
- Performance optimization for network requests
- Security considerations for API calls
- Caching strategies to reduce API calls

## Decision
We implemented a service-oriented API architecture with dedicated service classes, comprehensive error handling, and intelligent caching strategies.

### Architecture Overview

#### 1. Service Layer Structure
```
services/
├── AudioService.ts          # Audio file management and playback
├── PrayerTimesService.ts    # Prayer times calculation API
├── StorageService.ts        # Local storage and caching
├── LocationService.ts       # GPS and location APIs
└── APIService.ts           # Base HTTP client and utilities
```

#### 2. API Endpoints Integration
```typescript
// Prayer Times API
const PRAYER_TIMES_BASE_URL = 'https://api.aladhan.com/v1';

// Location Services API  
const LOCATION_BASE_URL = 'https://nominatim.openstreetmap.org';

// Audio Files API
const AUDIO_BASE_URL = 'https://everyayah.com/data';
```

#### 3. Service Pattern Implementation
```typescript
class PrayerTimesService {
  private readonly API_BASE_URL = 'https://api.aladhan.com/v1';
  private readonly CACHE_DURATION = 2 * 60 * 60 * 1000; // 2 hours

  async getPrayerTimes(coordinates: Coordinates, method: number = 5): Promise<PrayerTimesData> {
    // Check cache first
    const cachedData = await this.getCachedData(coordinates, method);
    if (cachedData) return cachedData;

    // Fetch from API
    const response = await fetch(
      `${this.API_BASE_URL}/timings/${this.getTodayDate()}?` +
      `latitude=${coordinates.latitude}&` +
      `longitude=${coordinates.longitude}&` +
      `method=${method}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    const prayerTimes = this.processApiResponse(data);
    await this.cacheData(coordinates, prayerTimes, method);
    
    return prayerTimes;
  }
}
```

## Rationale

### Why Service-Oriented Architecture?

#### 1. **Separation of Concerns**
- Each service handles specific domain logic
- Clear boundaries between different API integrations
- Easier testing and maintenance
- Single responsibility principle

#### 2. **Abstraction Layer**
- Hide API complexity from UI components
- Consistent interface across different APIs
- Easy to swap API implementations
- Centralized error handling

#### 3. **Reusability**
- Services can be used across multiple components
- Shared logic for common operations
- Consistent data transformation
- Centralized caching logic

#### 4. **Testability**
- Easy to mock services for unit tests
- Isolated business logic
- Clear interfaces for testing
- Dependency injection support

### API Integration Strategy

#### 1. Prayer Times API (Aladhan)
```typescript
// Features: Multiple calculation methods, timezone support, reliable data
interface PrayerTimesResponse {
  code: number;
  status: string;
  data: {
    timings: {
      Fajr: string;
      Dhuhr: string;
      Asr: string;
      Maghrib: string;
      Isha: string;
    };
    date: {
      readable: string;
      timestamp: string;
    };
    meta: {
      latitude: number;
      longitude: number;
      timezone: string;
    };
  };
}
```

#### 2. Location Services API (OpenStreetMap)
```typescript
// Features: Reverse geocoding, multi-language support, no API key required
interface LocationResponse {
  place_id: number;
  licence: string;
  osm_type: string;
  osm_id: number;
  lat: string;
  lon: string;
  display_name: string;
  address: {
    city: string;
    country: string;
    country_code: string;
  };
}
```

#### 3. Audio API (EveryAyah)
```typescript
// Features: Direct file access, multiple reciters, reliable CDN
const buildAudioUrl = (reciterPath: string, surahId: number, verseId: number) => {
  const surahPadded = (surahId + 1).toString().padStart(3, '0');
  const versePadded = verseId.toString().padStart(3, '0');
  return `https://everyayah.com/data/${reciterPath}/${surahPadded}${versePadded}.mp3`;
};
```

## Implementation Details

### 1. Base HTTP Client
```typescript
class APIService {
  private static readonly DEFAULT_TIMEOUT = 10000;
  private static readonly MAX_RETRIES = 3;

  static async makeRequest<T>(
    url: string,
    options: RequestInit = {},
    retries: number = 0
  ): Promise<T> {
    try {
      const response = await fetch(url, {
        ...options,
        timeout: this.DEFAULT_TIMEOUT,
        headers: {
          'User-Agent': 'QuranApp/1.0 (contact@quranapp.local)',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (retries < this.MAX_RETRIES) {
        await this.delay(1000 * Math.pow(2, retries)); // Exponential backoff
        return this.makeRequest(url, options, retries + 1);
      }
      throw error;
    }
  }

  private static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### 2. Error Handling Strategy
```typescript
class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public endpoint?: string,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'APIError';
  }
}

const handleAPIError = (error: any, endpoint: string) => {
  if (error instanceof APIError) {
    return error;
  }

  if (error.name === 'TypeError' && error.message.includes('Network request failed')) {
    return new APIError('Network connection failed', undefined, endpoint, error);
  }

  if (error.message.includes('timeout')) {
    return new APIError('Request timeout', undefined, endpoint, error);
  }

  return new APIError('Unknown API error', undefined, endpoint, error);
};
```

### 3. Caching Implementation
```typescript
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

class CacheManager {
  private cache = new Map<string, CacheEntry<any>>();

  async get<T>(key: string): Promise<T | null> {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  async set<T>(key: string, data: T, ttl: number): Promise<void> {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + ttl,
    };
    this.cache.set(key, entry);
  }

  clear(): void {
    this.cache.clear();
  }

  // Cleanup expired entries
  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
      }
    }
  }
}
```

### 4. Rate Limiting
```typescript
class RateLimiter {
  private requests = new Map<string, number[]>();

  canMakeRequest(endpoint: string, limit: number, window: number): boolean {
    const now = Date.now();
    const requests = this.requests.get(endpoint) || [];
    
    // Remove old requests outside the window
    const validRequests = requests.filter(time => now - time < window);
    
    if (validRequests.length >= limit) {
      return false;
    }

    validRequests.push(now);
    this.requests.set(endpoint, validRequests);
    return true;
  }
}
```

## Performance Optimizations

### 1. Request Deduplication
```typescript
const pendingRequests = new Map<string, Promise<any>>();

const deduplicateRequest = async <T>(key: string, request: () => Promise<T>): Promise<T> => {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key);
  }

  const promise = request();
  pendingRequests.set(key, promise);

  try {
    const result = await promise;
    return result;
  } finally {
    pendingRequests.delete(key);
  }
};
```

### 2. Background Sync
```typescript
const syncCache = async () => {
  try {
    // Sync prayer times in background
    const coordinates = await getCurrentLocation();
    await PrayerTimesService.getPrayerTimes(coordinates);
    
    // Preload next day's prayer times
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    await PrayerTimesService.getPrayerTimes(coordinates, tomorrow);
  } catch (error) {
    console.error('Background sync failed:', error);
  }
};
```

### 3. Connection-Aware Requests
```typescript
const makeConnectionAwareRequest = async <T>(
  request: () => Promise<T>,
  fallbackData?: T
): Promise<T> => {
  const connectionType = await NetInfo.getConnectionType();
  
  if (connectionType === NetInfo.ConnectionType.None) {
    // Use cached data or fallback
    return fallbackData || getCachedData();
  }

  if (connectionType === NetInfo.ConnectionType.Cellular) {
    // Prefer cached data on cellular to save data
    const cached = getCachedData();
    if (cached && !isCacheExpired(cached)) {
      return cached;
    }
  }

  return request();
};
```

## Security Considerations

### 1. HTTPS Enforcement
```typescript
const validateURL = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:';
  } catch {
    return false;
  }
};
```

### 2. Input Validation
```typescript
const validateCoordinates = (coordinates: Coordinates): boolean => {
  return (
    coordinates.latitude >= -90 && 
    coordinates.latitude <= 90 &&
    coordinates.longitude >= -180 && 
    coordinates.longitude <= 180
  );
};
```

### 3. Data Sanitization
```typescript
const sanitizeAPIResponse = <T>(data: any): T => {
  // Remove potentially sensitive data
  const sanitized = { ...data };
  delete sanitized.internalFields;
  delete sanitized.debugInfo;
  return sanitized;
};
```

## Consequences

### Positive
- **Modularity**: Clear separation of API concerns
- **Reliability**: Comprehensive error handling and retries
- **Performance**: Intelligent caching and request optimization
- **Maintainability**: Easy to update or replace API implementations
- **Testability**: Services can be easily mocked and tested

### Negative
- **Complexity**: Additional abstraction layer adds complexity
- **Overhead**: Service layer adds minimal performance overhead
- **Dependencies**: External API dependencies create potential failure points
- **Maintenance**: Need to monitor API changes and updates

### Neutral
- **Learning Curve**: Team needs to understand service patterns
- **Code Volume**: Additional code for service layer
- **Debugging**: API errors may be harder to trace through service layer

## Future Enhancements

### 1. API Gateway Pattern
- Single entry point for all API calls
- Centralized authentication and rate limiting
- Request/response transformation
- API versioning support

### 2. GraphQL Integration
- Single endpoint for multiple data sources
- Reduced over-fetching and under-fetching
- Strong typing with schema
- Real-time subscriptions support

### 3. WebSocket Integration
- Real-time prayer time updates
- Live location tracking
- Push notifications for prayer times
- Real-time audio streaming

### 4. API Monitoring
- Request/response logging
- Performance metrics collection
- Error rate monitoring
- Usage analytics

## Alternatives Considered

### 1. Direct API Calls in Components
- **Pros**: Simple implementation, no abstraction
- **Cons**: Code duplication, hard to test, no caching strategy

### 2. Redux Middleware for API Calls
- **Pros**: Centralized API logic, time-travel debugging
- **Cons**: Tied to Redux, complex for simple API calls

### 3. Apollo Client (GraphQL)
- **Pros**: Advanced caching, real-time updates
- **Cons**: GraphQL required, overkill for REST APIs

### 4. No API Integration (Offline Only)
- **Pros**: No network dependencies, simple
- **Cons**: Limited functionality, poor user experience

---

*Decision Date: November 2025*  
*Status: Accepted*  
*Next Review: When new API integrations are needed or performance issues arise*
