# ADR-028: Adoption of React Native for Cross-Platform Mobile Development

## Status
Proposed

## Date
2025-03-02

## Context
The Aronim Bookstore is expanding its digital presence beyond the web application to reach mobile users. We need to develop mobile applications that provide a consistent user experience across different platforms (iOS and Android) while:

- Maintaining brand consistency across platforms
- Efficiently utilizing development resources
- Achieving native-like performance and user experience
- Leveraging our existing JavaScript/React expertise
- Supporting our modular architecture approach
- Ensuring maintainability and long-term support
- Accelerating time-to-market for mobile applications
- Enabling code sharing between platforms

Developing separate native applications for iOS and Android would require maintaining multiple codebases, different technology stacks, and specialized development teams, potentially leading to inconsistent user experiences and increased development costs.

## Decision
We will adopt **React Native** as our framework for cross-platform mobile application development with the following characteristics:

### 1. Architecture Approach
- Implement a single React Native codebase that targets both iOS and Android
- Align mobile app architecture with our existing micro-frontend approach
- Integrate with our Backend-for-Frontend (BFF) services for data access
- Use native modules where platform-specific functionality is required
- Structure the application using a modular component architecture
- Implement proper state management aligned with our web application patterns

### 2. Technical Implementation
- Develop with **React Native** using TypeScript for type safety
- Use **React Navigation** for navigation management
- Implement **Redux** or **MobX** for state management (aligned with web approach)
- Utilize **React Native Paper** or custom component library for UI consistency
- Implement responsive designs that adapt to various device sizes
- Use **React Native Testing Library** for component testing

### 3. Development Approach
- Create shared component libraries between web and mobile platforms where possible
- Establish coding standards specific to React Native development
- Implement CI/CD pipelines for automated building and testing
- Use feature flags for progressive feature rollout
- Establish monitoring and analytics for mobile-specific metrics
- Create platform-specific adaptations only when necessary

### 4. Deployment Strategy
- Configure automated builds for both iOS and Android platforms
- Implement code signing and app store deployment processes
- Set up beta distribution channels for testing
- Establish over-the-air update mechanisms where appropriate
- Create release management processes for app store submissions

## Implementation Approach

1. **Project Setup and Configuration**
   - Initialize React Native project with TypeScript support
   - Configure ESLint and Prettier for code quality
   - Set up directory structure aligned with our architectural patterns
   - Configure module bundling and optimization

2. **Core Framework Implementation**
   - Implement navigation structure and routing
   - Create base UI component library
   - Set up state management infrastructure
   - Establish API client for BFF integration
   - Configure authentication and session management

3. **Feature Development**
   - Implement core bookstore features (browsing, search, cart, checkout)
   - Create user account management features
   - Develop offline capabilities for essential features
   - Implement push notification infrastructure

4. **Quality Assurance**
   - Set up unit and integration testing frameworks
   - Implement UI automation testing
   - Create performance testing benchmarks
   - Establish device testing matrix

## Consequences

### Positive
- Faster development cycles with a single codebase for multiple platforms
- Reduced development costs compared to maintaining separate native apps
- Ability to leverage existing React expertise and components
- Faster time-to-market for mobile applications
- Consistent user experience across platforms
- Easier maintenance with unified codebase
- Access to large ecosystem of React Native libraries and tools
- Ability to update certain app features without app store submissions
- Simplified recruitment with focus on one technology stack

### Negative
- Potential performance limitations compared to fully native applications
- Dependency on the React Native ecosystem and its update cycles
- Additional complexity when integrating with native device features
- Possible limitations for highly specialized UI/UX requirements
- Debugging challenges with cross-platform issues
- Potential version compatibility issues with native dependencies
- Learning curve for React developers to understand mobile-specific concerns
- Risk of "write once, debug everywhere" scenarios

## Alternatives Considered

1. **Native Development (Swift/Kotlin)**
   - Best possible performance and platform integration
   - Full access to platform-specific features and design patterns
   - Significantly higher development and maintenance costs
   - Requires specialized development teams for each platform
   - Slower feature delivery across platforms
   - Potential inconsistencies in feature implementation

2. **Flutter**
   - Good performance with custom rendering engine
   - Growing ecosystem and Google backing
   - Less alignment with our existing React expertise
   - Different programming language (Dart) requiring additional training
   - Less mature integration with certain native features
   - Potentially less web/mobile code sharing compared to React/React Native

3. **Progressive Web App (PWA)**
   - Maximum code sharing with web application
   - Simplest deployment model with no app stores
   - Limited access to native device features
   - Reduced discoverability without app store presence
   - Performance limitations compared to native or hybrid apps
   - Limited offline capabilities
   - Inconsistent browser implementation of PWA features

4. **Hybrid Approaches (Ionic, Cordova)**
   - Web technologies wrapped in native container
   - Good for simple applications with minimal native requirements
   - Significant performance limitations
   - Less native look and feel
   - Outdated approach compared to newer frameworks

## Implementation Notes

### Project Structure

```
/src
  /app
    App.tsx
    AppNavigator.tsx
  /components
    /common
      Button.tsx
      Card.tsx
      Typography.tsx
    /book
      BookCard.tsx
      BookDetails.tsx
    /cart
      CartItem.tsx
      CartSummary.tsx
  /screens
    /home
      HomeScreen.tsx
    /catalog
      BookListScreen.tsx
      BookDetailScreen.tsx
    /cart
      CartScreen.tsx
      CheckoutScreen.tsx
    /account
      ProfileScreen.tsx
      OrderHistoryScreen.tsx
  /services
    /api
      apiClient.ts
      bookService.ts
      cartService.ts
      userService.ts
    /auth
      authService.ts
  /store
    /slices
      bookSlice.ts
      cartSlice.ts
      userSlice.ts
    store.ts
  /utils
    formatting.ts
    validation.ts
  /hooks
    useDebounce.ts
    useOnlineStatus.ts
  /constants
    colors.ts
    typography.ts
    spacing.ts
```

### React Native Component Example

```typescript
// src/components/book/BookCard.tsx
import React from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { Card, Text, Chip } from 'react-native-paper';
import { Book } from '../../types/Book';
import { formatCurrency } from '../../utils/formatting';
import { useNavigation } from '@react-navigation/native';
import { colors, spacing } from '../../constants';

interface BookCardProps {
  book: Book;
  horizontal?: boolean;
}

export const BookCard: React.FC<BookCardProps> = ({ book, horizontal = false }) => {
  const navigation = useNavigation();
  
  const handlePress = () => {
    navigation.navigate('BookDetail', { bookId: book.id });
  };
  
  return (
    <TouchableOpacity onPress={handlePress} style={horizontal ? styles.horizontalContainer : styles.container}>
      <Card style={horizontal ? styles.horizontalCard : styles.card}>
        <Card.Cover 
          source={{ uri: book.coverImage }} 
          style={horizontal ? styles.horizontalCover : styles.cover} 
        />
        <Card.Content style={styles.content}>
          <Text numberOfLines={2} style={styles.title}>{book.title}</Text>
          <Text numberOfLines={1} style={styles.author}>{book.author.name}</Text>
          <View style={styles.footer}>
            <Text style={styles.price}>{formatCurrency(book.price.amount, book.price.currency)}</Text>
            {book.availability === 'IN_STOCK' ? (
              <Chip icon="check" mode="outlined" style={styles.availabilityChip}>In Stock</Chip>
            ) : book.availability === 'LOW_STOCK' ? (
              <Chip icon="alert" mode="outlined" style={[styles.availabilityChip, styles.lowStockChip]}>Low Stock</Chip>
            ) : (
              <Chip icon="close" mode="outlined" style={[styles.availabilityChip, styles.outOfStockChip]}>Out of Stock</Chip>
            )}
          </View>
          {book.rating && (
            <View style={styles.ratingContainer}>
              <Text style={styles.rating}>{book.rating.toFixed(1)}</Text>
              {/* Star icons would go here */}
            </View>
          )}
        </Card.Content>
      </Card>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '48%',
    marginBottom: spacing.medium,
  },
  horizontalContainer: {
    width: '100%',
    marginBottom: spacing.small,
  },
  card: {
    height: 300,
  },
  horizontalCard: {
    flexDirection: 'row',
    height: 150,
  },
  cover: {
    height: 160,
  },
  horizontalCover: {
    width: 100,
    height: '100%',
  },
  content: {
    padding: spacing.small,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: spacing.xsmall,
  },
  author: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.small,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.small,
  },
  price: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.primary,
  },
  availabilityChip: {
    height: 24,
    fontSize: 10,
  },
  lowStockChip: {
    backgroundColor: colors.warning + '20',
  },
  outOfStockChip: {
    backgroundColor: colors.error + '20',
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.small,
  },
  rating: {
    marginRight: spacing.xsmall,
    fontWeight: 'bold',
  },
});
```

### API Service Integration

```typescript
// src/services/api/bookService.ts
import { apiClient } from './apiClient';
import { Book, BookConnection, SearchParams } from '../../types/Book';

export const bookService = {
  getBookById: async (id: string): Promise<Book> => {
    const query = `
      query GetBook($id: ID!) {
        bookById(id: $id) {
          id
          title
          description
          coverImage
          price {
            amount
            currency
          }
          author {
            id
            name
          }
          rating
          categories {
            id
            name
          }
          availability
        }
      }
    `;
    
    const response = await apiClient.query({
      query,
      variables: { id },
    });
    
    return response.data.bookById;
  },
  
  searchBooks: async (params: SearchParams): Promise<BookConnection> => {
    const { query, page = 0, size = 20 } = params;
    
    const gqlQuery = `
      query SearchBooks($query: String!, $page: Int, $size: Int) {
        searchBooks(query: $query, page: $page, size: $size) {
          items {
            id
            title
            coverImage
            price {
              amount
              currency
            }
            author {
              id
              name
            }
            rating
            availability
          }
          totalCount
          hasNext
        }
      }
    `;
    
    const response = await apiClient.query({
      query: gqlQuery,
      variables: { query, page, size },
    });
    
    return response.data.searchBooks;
  },
  
  getFeaturedBooks: async (count: number = 10): Promise<Book[]> => {
    const query = `
      query FeaturedBooks($count: Int) {
        featuredBooks(count: $count) {
          id
          title
          coverImage
          price {
            amount
            currency
          }
          author {
            id
            name
          }
          rating
          availability
        }
      }
    `;
    
    const response = await apiClient.query({
      query,
      variables: { count },
    });
    
    return response.data.featuredBooks;
  }
};
```

### Redux Store Configuration

```typescript
// src/store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import bookReducer from './slices/bookSlice';
import cartReducer from './slices/cartSlice';
import userReducer from './slices/userSlice';

export const store = configureStore({
  reducer: {
    books: bookReducer,
    cart: cartReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) => 
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Navigation Setup

```typescript
// src/app/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Screens
import HomeScreen from '../screens/home/HomeScreen';
import BookListScreen from '../screens/catalog/BookListScreen';
import BookDetailScreen from '../screens/catalog/BookDetailScreen';
import CartScreen from '../screens/cart/CartScreen';
import CheckoutScreen from '../screens/cart/CheckoutScreen';
import ProfileScreen from '../screens/account/ProfileScreen';
import OrderHistoryScreen from '../screens/account/OrderHistoryScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import SignupScreen from '../screens/auth/SignupScreen';

// Navigation types
import { RootStackParamList, MainTabParamList, AuthStackParamList } from '../types/navigation';

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();
const AuthStack = createStackNavigator<AuthStackParamList>();

// Auth navigator
const AuthNavigator = () => (
  <AuthStack.Navigator screenOptions={{ headerShown: false }}>
    <AuthStack.Screen name="Login" component={LoginScreen} />
    <AuthStack.Screen name="Signup" component={SignupScreen} />
  </AuthStack.Navigator>
);

// Home stack
const HomeStackNavigator = () => (
  <Stack.Navigator>
    <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
    <Stack.Screen name="BookDetail" component={BookDetailScreen} options={{ title: 'Book Details' }} />
  </Stack.Navigator>
);

// Catalog stack
const CatalogStackNavigator = () => (
  <Stack.Navigator>
    <Stack.Screen name="BookList" component={BookListScreen} options={{ title: 'Browse Books' }} />
    <Stack.Screen name="BookDetail" component={BookDetailScreen} options={{ title: 'Book Details' }} />
  </Stack.Navigator>
);

// Cart stack
const CartStackNavigator = () => (
  <Stack.Navigator>
    <Stack.Screen name="Cart" component={CartScreen} options={{ title: 'Your Cart' }} />
    <Stack.Screen name="Checkout" component={CheckoutScreen} options={{ title: 'Checkout' }} />
  </Stack.Navigator>
);

// Account stack
const AccountStackNavigator = () => (
  <Stack.Navigator>
    <Stack.Screen name="Profile" component={ProfileScreen} options={{ title: 'Your Profile' }} />
    <Stack.Screen name="OrderHistory" component={OrderHistoryScreen} options={{ title: 'Order History' }} />
  </Stack.Navigator>
);

// Main tab navigator
const TabNavigator = () => (
  <Tab.Navigator
    screenOptions={{
      tabBarActiveTintColor: '#1565C0',
      tabBarInactiveTintColor: '#757575',
      tabBarLabelStyle: { fontSize: 12 },
    }}
  >
    <Tab.Screen 
      name="HomeTab" 
      component={HomeStackNavigator} 
      options={{
        title: 'Home',
        tabBarIcon: ({ color, size }) => (
          <Icon name="home" color={color} size={size} />
        ),
        headerShown: false,
      }}
    />
    <Tab.Screen 
      name="CatalogTab" 
      component={CatalogStackNavigator}
      options={{
        title: 'Browse',
        tabBarIcon: ({ color, size }) => (
          <Icon name="book-open-variant" color={color} size={size} />
        ),
        headerShown: false,
      }}
    />
    <Tab.Screen 
      name="CartTab" 
      component={CartStackNavigator}
      options={{
        title: 'Cart',
        tabBarIcon: ({ color, size }) => (
          <Icon name="cart" color={color} size={size} />
        ),
        headerShown: false,
      }}
    />
    <Tab.Screen 
      name="AccountTab" 
      component={AccountStackNavigator}
      options={{
        title: 'Account',
        tabBarIcon: ({ color, size }) => (
          <Icon name="account" color={color} size={size} />
        ),
        headerShown: false,
      }}
    />
  </Tab.Navigator>
);

// Root navigator
export const AppNavigator = () => {
  const { isAuthenticated } = useSelector((state: RootState) => state.user);
  
  return (
    <NavigationContainer>
      {isAuthenticated ? <TabNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
};
```

### CI/CD Pipeline for React Native

```yaml
# .github/workflows/mobile-app.yml
name: Mobile App CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'mobile/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'mobile/**'

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'yarn'
          cache-dependency-path: mobile/yarn.lock
      
      - name: Install dependencies
        working-directory: mobile
        run: yarn install --frozen-lockfile
      
      - name: Run linting
        working-directory: mobile
        run: yarn lint
      
      - name: Run tests
        working-directory: mobile
        run: yarn test
  
  build-android:
    name: Build Android App
    needs: test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'yarn'
          cache-dependency-path: mobile/yarn.lock
      
      - name: Install dependencies
        working-directory: mobile
        run: yarn install --frozen-lockfile
      
      - name: Setup JDK
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '17'
      
      - name: Setup Android SDK
        uses: android-actions/setup-android@v2
      
      - name: Build Android App
        working-directory: mobile/android
        run: ./gradlew bundleRelease
      
      - name: Upload Android Bundle
        uses: actions/upload-artifact@v3
        with:
          name: android-release-bundle
          path: mobile/android/app/build/outputs/bundle/release/app-release.aab
  
  build-ios:
    name: Build iOS App
    needs: test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'yarn'
          cache-dependency-path: mobile/yarn.lock
      
      - name: Install dependencies
        working-directory: mobile
        run: yarn install --frozen-lockfile
      
      - name: Install CocoaPods
        working-directory: mobile/ios
        run: pod install
      
      - name: Build iOS App
        working-directory: mobile
        run: |
          xcodebuild -workspace ios/ArominBookstore.xcworkspace -scheme ArominBookstore \
          -configuration Release -destination generic/platform=iOS \
          -archivePath $PWD/build/ArominBookstore.xcarchive \
          archive
      
      - name: Upload iOS Archive
        uses: actions/upload-artifact@v3
        with:
          name: ios-archive
          path: mobile/build/ArominBookstore.xcarchive
```

## Compliance Verification
- Performance testing on target devices
- Accessibility compliance testing
- Security review of app permissions and data handling
- Cross-device compatibility testing
- UI/UX consistency review
- Offline functionality verification
- App store submission requirements validation
- Analytics and crash reporting verification

## References
- React Native Documentation: https://reactnative.dev/docs/getting-started
- React Navigation: https://reactnavigation.org/
- Redux Toolkit: https://redux-toolkit.js.org/
- React Native Paper: https://callstack.github.io/react-native-paper/
- React Native Testing Library: https://callstack.github.io/react-native-testing-library/
- Mobile App Security Best Practices: https://owasp.org/www-project-mobile-security/
- React Native Performance: https://reactnative.dev/docs/performance
- App Store Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Google Play Policies: https://play.google.com/about/developer-content-policy/
