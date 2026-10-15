# ADR-030: Internationalization and Localization Strategy

## Status
Proposed

## Context
The Aronim Bookstore application needs to support multiple languages and regional preferences to serve a global customer base. We need a consistent approach to internationalization (i18n) and localization (l10n) that works across our backend services, web frontend applications, and mobile applications while providing a seamless user experience.

Key considerations include:
- Support for multiple languages and locales
- Translation management workflow
- Date, time, number, and currency formatting
- Right-to-left (RTL) language support
- Performance impact of localization
- Developer experience and maintainability
- Consistency across web and mobile platforms

## Decision
We will implement a comprehensive internationalization and localization strategy with the following components:

### Backend (Java/Spring Boot)
1. Use Spring's built-in internationalization support with `MessageSource`
2. Store translations in resource bundles (properties files) organized by language
3. Implement locale detection based on:
   - User preferences stored in profile
   - Accept-Language HTTP header
   - URL path or query parameter (e.g., `?lang=fr`)
4. Use Java's `java.util.Locale` for formatting dates, numbers, and currencies

### Web Frontend (React)
1. Adopt React-i18next as our translation library
2. Implement lazy loading of translation files by language
3. Use the ICU message format for complex pluralization and formatting
4. Develop RTL layout support using CSS logical properties and directional utilities

### Mobile Frontend (React Native)
1. Use i18next with react-i18next for React Native
2. Implement react-native-localize for device locale detection
3. Support RTL layouts with React Native's built-in I18nManager
4. Use react-native-localization for device-native date and number formatting
5. Implement locale-specific assets (images, icons) where necessary

### Translation Management
1. Implement a translation management system to centralize translation efforts
2. Use JSON format for all frontend translations (web and mobile) and properties files for backend
3. Share translation keys and structures between web and mobile to maximize reuse
4. Establish a workflow for translation updates, including automated extraction of new strings

### Common Standards
1. Use ISO language codes for locale identification
2. Implement fallback mechanisms for missing translations
3. Create style guides for internationalized content
4. Establish a process for translation quality assurance
5. Define a common translation key structure to be used across platforms

## Consequences

### Positive
- The application will be accessible to users from different regions and language backgrounds
- Consistent localization approach across all application components (web, mobile, backend)
- Separation of code and content facilitates translation updates without code changes
- Lazy loading of translations improves performance for users
- Clear processes for managing translations will improve quality and consistency
- Shared translation resources between web and mobile reduce duplication

### Negative
- Increased development complexity and maintenance overhead
- Additional testing requirements for each supported locale
- Potential performance impact from loading translation resources
- Need for additional tools and processes for translation management
- UI design must accommodate text expansion/contraction in different languages
- Mobile-specific challenges with layout and formatting

### Risks
- Inconsistent user experience across different languages
- Incomplete or inaccurate translations
- Performance degradation from improper implementation of locale-specific resources
- Increased complexity in testing across multiple locales
- Divergence between web and mobile translations over time

## Implementation Details

### Backend Implementation
```java
@Configuration
public class LocalizationConfig {
    @Bean
    public MessageSource messageSource() {
        ReloadableResourceBundleMessageSource messageSource = new ReloadableResourceBundleMessageSource();
        messageSource.setBasename("classpath:i18n/messages");
        messageSource.setDefaultEncoding("UTF-8");
        return messageSource;
    }
    
    @Bean
    public LocaleResolver localeResolver() {
        SessionLocaleResolver resolver = new SessionLocaleResolver();
        resolver.setDefaultLocale(Locale.ENGLISH);
        return resolver;
    }
    
    @Bean
    public LocaleChangeInterceptor localeChangeInterceptor() {
        LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
        interceptor.setParamName("lang");
        return interceptor;
    }
}
```

### Web Frontend Implementation
```typescript
// i18n configuration for React web
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    ns: ['common', 'product', 'checkout'],
    defaultNS: 'common',
    interpolation: {
      escapeValue: false
    },
    react: {
      useSuspense: true
    }
  });

export default i18n;
```

### React Native Implementation
```typescript
// i18n configuration for React Native
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { getLocales } from 'react-native-localize';
import { I18nManager } from 'react-native';

// Import translation files
import en from './translations/en.json';
import fr from './translations/fr.json';
import ar from './translations/ar.json';

const resources = {
  en: { translation: en },
  fr: { translation: fr },
  ar: { translation: ar }
};

// Get device locale
const deviceLanguage = getLocales()[0].languageCode;

// Set up RTL if needed
const isRTL = getLocales()[0].isRTL;
I18nManager.forceRTL(isRTL);

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: deviceLanguage,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    react: {
      useSuspense: true
    }
  });

export default i18n;
```

### RTL Support for React Native
```typescript
// RTL helper component
import React, { ReactNode } from 'react';
import { View, StyleSheet, ViewStyle, I18nManager } from 'react-native';

interface RTLAwareViewProps {
  style?: ViewStyle;
  children: ReactNode;
}

export const RTLAwareView: React.FC<RTLAwareViewProps> = ({ style, children }) => {
  const rtlStyles = I18nManager.isRTL
    ? { flexDirection: 'row-reverse' }
    : { flexDirection: 'row' };

  return (
    <View style={[rtlStyles, style]}>
      {children}
    </View>
  );
};
```

### Example Usage in React Native
```tsx
import React from 'react';
import { Text, View } from 'react-native';
import { useTranslation } from 'react-i18next';
import { RTLAwareView } from './RTLAwareView';
import { format } from 'date-fns';
import { formatNumber, formatCurrency } from './formatters';

export const ProductDetail = ({ product }) => {
  const { t, i18n } = useTranslation();
  
  return (
    <View>
      <Text>{t('product.title', { title: product.title })}</Text>
      
      <RTLAwareView>
        <Text>{t('product.price')}:</Text>
        <Text>{formatCurrency(product.price, i18n.language)}</Text>
      </RTLAwareView>
      
      <Text>
        {t('product.releaseDate', {
          date: format(new Date(product.releaseDate), 'PP', {
            locale: getDateLocale(i18n.language)
          })
        })}
      </Text>
    </View>
  );
};
```

## Compliance
This approach aligns with our existing architectural decisions, particularly:
- ADR-004 (Spring Boot as Application Framework)
- ADR-007 (REST API Design Standards)
- ADR-025 (Micro-Frontend Architecture)
- ADR-027 (React as Default Frontend Framework)
- ADR-028 (React Native for Mobile Development)

The localization strategy complements our modular architecture (ADR-005) by implementing locale-specific behavior in a consistent way across all application modules, while ensuring a unified approach between web and mobile platforms.
