# ADR-0007: UI Component Architecture

## Status
Accepted

## Context
The Huda Al-Quran application requires a comprehensive UI component architecture to support:

- **Arabic RTL Interface**: Right-to-left layout for Arabic text
- **Responsive Design**: Multiple screen sizes and orientations
- **Theme System**: Dark/light theme support
- **Reusable Components**: Consistent UI across screens
- **Accessibility**: Screen reader and navigation support
- **Performance**: Smooth animations and scrolling

The UI architecture needed to address:

- Complex Arabic text rendering with proper fonts
- Audio player controls with real-time updates
- Quran reading interface with verse navigation
- Prayer times display with location awareness
- Settings and preference management
- Cross-platform consistency (iOS/Android)

## Decision
We implemented a component-based architecture using React Native components with custom styling, RTL support, and a theme system built on React Navigation theming.

### Architecture Overview

#### 1. Component Structure
```
components/
├── __tests__/              # Component tests
├── navigation/             # Navigation components
│   └── TabBarIcon.tsx
├── MiniPlayer.tsx          # Global audio controls
├── Collapsible.tsx         # Accordion component
├── ExternalLink.tsx        # Link handling
├── ThemedText.tsx          # Text with theme support
├── ThemedView.tsx          # View with theme support
├── QuranReader/            # Quran-specific components
│   ├── VerseCard.tsx
│   ├── SurahHeader.tsx
│   └── TranslationText.tsx
├── AudioControls/          # Audio player components
│   ├── PlayPauseButton.tsx
│   ├── ProgressBar.tsx
│   └── ReciterSelector.tsx
└── Common/                 # Reusable UI components
    ├── LoadingSpinner.tsx
    ├── ErrorBoundary.tsx
    └── SettingsItem.tsx
```

#### 2. Theme System
```typescript
// Colors.ts - Centralized color management
export const Colors = {
  light: {
    primary: '#1E88E5',
    secondary: '#4CAF50',
    background: '#FFFFFF',
    surface: '#F5F5F5',
    text: '#212121',
    textSecondary: '#757575',
    border: '#E0E0E0',
    error: '#F44336',
    arabicText: '#1A237E',
  },
  dark: {
    primary: '#90CAF9',
    secondary: '#81C784',
    background: '#121212',
    surface: '#1E1E1E',
    text: '#FFFFFF',
    textSecondary: '#B3B3B3',
    border: '#333333',
    error: '#EF5350',
    arabicText: '#C5CAE9',
  },
};

export const useThemeColor = (props: { light?: string; dark?: string }, colorName: keyof typeof Colors.light) => {
  const theme = useColorScheme() ?? 'light';
  const colorFromProps = props[theme];

  if (colorFromProps) {
    return colorFromProps;
  } else {
    return Colors[theme][colorName];
  }
};
```

#### 3. RTL Support Implementation
```typescript
// Force RTL layout in root layout
I18nManager.allowRTL(true);
I18nManager.forceRTL(true);

// RTL-aware components
const RTLView = ({ children, style, ...props }: ViewProps) => (
  <View style={[{ direction: 'rtl' }, style]} {...props}>
    {children}
  </View>
);

const RTLText = ({ children, style, ...props }: TextProps) => (
  <Text style={[{ textAlign: 'right', writingDirection: 'rtl' }, style]} {...props}>
    {children}
  </Text>
);
```

## Rationale

### Why Component-Based Architecture?

#### 1. **Reusability**
- Shared components across multiple screens
- Consistent UI patterns and behavior
- Reduced code duplication
- Easier maintenance and updates

#### 2. **Separation of Concerns**
- UI logic separated from business logic
- Clear component responsibilities
- Better testability
- Improved code organization

#### 3. **Theme Integration**
- Consistent theming across all components
- Dynamic theme switching
- Centralized color management
- Platform-specific adaptations

#### 4. **Performance Optimization**
- Component memoization for expensive renders
- Lazy loading of heavy components
- Optimized re-render patterns
- Memory-efficient component lifecycle

### Component Design Principles

#### 1. **Single Responsibility**
```typescript
// Example: VerseCard component focuses only on verse display
interface VerseCardProps {
  verse: Verse;
  surahId: number;
  verseNumber: number;
  isPlaying: boolean;
  onPlay: () => void;
  onBookmark: () => void;
}

const VerseCard: React.FC<VerseCardProps> = ({
  verse,
  surahId,
  verseNumber,
  isPlaying,
  onPlay,
  onBookmark,
}) => {
  // Component logic for verse display only
  return (
    <ThemedView style={styles.container}>
      <RTLText style={styles.arabicText}>{verse.text}</RTLText>
      <ThemedText style={styles.translationText}>{verse.translation}</ThemedText>
      <View style={styles.actions}>
        <PlayPauseButton isPlaying={isPlaying} onPress={onPlay} />
        <BookmarkButton onPress={onBookmark} />
      </View>
    </ThemedView>
  );
};
```

#### 2. **Composition over Inheritance**
```typescript
// Complex components built from simpler ones
const QuranReader: React.FC<QuranReaderProps> = ({ surahId }) => {
  return (
    <ThemedView style={styles.container}>
      <SurahHeader surahId={surahId} />
      <FlatList
        data={verses}
        renderItem={({ item, index }) => (
          <VerseCard
            verse={item}
            surahId={surahId}
            verseNumber={index + 1}
            isPlaying={isCurrentVerse(surahId, index + 1)}
            onPlay={() => playVerse(surahId, index + 1)}
            onBookmark={() => toggleBookmark(surahId, index + 1)}
          />
        )}
        keyExtractor={(item, index) => `verse-${surahId}-${index}`}
      />
    </ThemedView>
  );
};
```

#### 3. **Props Interface Design**
```typescript
// Clear and type-safe component interfaces
interface AudioControlsProps {
  isPlaying: boolean;
  isLoading: boolean;
  currentPosition: number;
  duration: number;
  playbackSpeed: number;
  repeatMode: RepeatMode;
  currentReciter: Reciter;
  onPlayPause: () => void;
  onPrevious: () => void;
  onNext: () => void;
  onSeek: (position: number) => void;
  onSpeedChange: (speed: number) => void;
  onRepeatModeChange: (mode: RepeatMode) => void;
  onReciterChange: (reciter: Reciter) => void;
}
```

## Implementation Details

### 1. Themed Components
```typescript
// Base themed components for consistent styling
const ThemedText = React.forwardRef<Text, ThemedTextProps>(
  ({ style, lightColor, darkColor, type = 'body', ...rest }, ref) => {
    const color = useThemeColor({ light: lightColor, dark: darkColor }, 'text');
    const fontFamily = useFontFamily(type);

    return (
      <Text
        style={[
          { color, fontFamily },
          styles[type],
          style,
        ]}
        ref={ref}
        {...rest}
      />
    );
  }
);

const ThemedView = React.forwardRef<View, ThemedViewProps>(
  ({ style, lightColor, darkColor, ...rest }, ref) => {
    const backgroundColor = useThemeColor({ light: lightColor, dark: darkColor }, 'background');

    return (
      <View
        style={[
          { backgroundColor },
          style,
        ]}
        ref={ref}
        {...rest}
      />
    );
  }
);
```

### 2. Arabic Text Handling
```typescript
// Specialized component for Arabic text
const ArabicText: React.FC<ArabicTextProps> = ({
  children,
  fontSize,
  style,
  ...props
}) => {
  const { fontSize: userFontSize } = useUserPreferences();
  const actualFontSize = fontSize || userFontSize;

  return (
    <Text
      style={[
        {
          fontFamily: 'Othmani',
          fontSize: actualFontSize,
          textAlign: 'right',
          writingDirection: 'rtl',
          lineHeight: actualFontSize * 1.8,
        },
        styles.arabicText,
        style,
      ]}
      {...props}
    >
      {children}
    </Text>
  );
};
```

### 3. Audio Player Components
```typescript
// MiniPlayer - Global audio controls
const MiniPlayer: React.FC = () => {
  const { state, togglePlayPause, playNext, playPrevious } = useAudioPlayer();
  const navigation = useNavigation();

  if (!state.currentSurahId) return null;

  return (
    <ThemedView style={styles.container}>
      <View style={styles.content}>
        <TouchableOpacity onPress={() => navigation.navigate('player')}>
          <View style={styles.trackInfo}>
            <ArabicText style={styles.surahName}>
              {getSurahName(state.currentSurahId)}
            </ArabicText>
            <ThemedText style={styles.verseInfo}>
              الآية {state.currentVerseId}
            </ThemedText>
          </View>
        </TouchableOpacity>

        <View style={styles.controls}>
          <IconButton onPress={playPrevious} name="skip-previous" />
          <PlayPauseButton
            isPlaying={state.isPlaying}
            isLoading={state.isLoading}
            onPress={togglePlayPause}
          />
          <IconButton onPress={playNext} name="skip-next" />
        </View>
      </View>
    </ThemedView>
  );
};
```

### 4. Responsive Design
```typescript
// Responsive component utilities
const useResponsive = () => {
  const { width, height } = useWindowDimensions();
  const isTablet = width >= 768;
  const isLandscape = width > height;

  return {
    width,
    height,
    isTablet,
    isLandscape,
    breakpoint: {
      small: width < 375,
      medium: width >= 375 && width < 768,
      large: width >= 768,
    },
  };
};

const ResponsiveView: React.FC<ResponsiveViewProps> = ({
  children,
  smallStyle,
  mediumStyle,
  largeStyle,
  style,
}) => {
  const { breakpoint } = useResponsive();

  const responsiveStyle = [
    style,
    breakpoint.small && smallStyle,
    breakpoint.medium && mediumStyle,
    breakpoint.large && largeStyle,
  ].filter(Boolean);

  return <View style={responsiveStyle}>{children}</View>;
};
```

## Performance Optimizations

### 1. Component Memoization
```typescript
// Memoize expensive components
const VerseCard = React.memo<VerseCardProps>(({ verse, surahId, verseNumber, isPlaying, onPlay, onBookmark }) => {
  return (
    // Component implementation
  );
}, (prevProps, nextProps) => {
  // Custom comparison for optimization
  return (
    prevProps.verse.id === nextProps.verse.id &&
    prevProps.isPlaying === nextProps.isPlaying &&
    prevProps.surahId === nextProps.surahId &&
    prevProps.verseNumber === nextProps.verseNumber
  );
});
```

### 2. Virtual Lists
```typescript
// FlatList optimization for long verse lists
const QuranReader: React.FC<QuranReaderProps> = ({ surahId }) => {
  const renderVerse = useCallback(({ item, index }) => (
    <VerseCard
      verse={item}
      surahId={surahId}
      verseNumber={index + 1}
      isPlaying={isCurrentVerse(surahId, index + 1)}
      onPlay={() => playVerse(surahId, index + 1)}
    />
  ), [surahId, playVerse]);

  return (
    <FlatList
      data={verses}
      renderItem={renderVerse}
      keyExtractor={(item, index) => `verse-${surahId}-${index}`}
      getItemLayout={(data, index) => ({
        length: VERSE_CARD_HEIGHT,
        offset: VERSE_CARD_HEIGHT * index,
        index,
      })}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={10}
      initialNumToRender={15}
    />
  );
};
```

### 3. Image Optimization
```typescript
// Optimized image loading
const OptimizedImage: React.FC<OptimizedImageProps> = ({
  source,
  style,
  placeholder,
  ...props
}) => {
  const [loaded, setLoaded] = useState(false);

  return (
    <View style={style}>
      {!loaded && placeholder && (
        <View style={styles.placeholder}>
          <ActivityIndicator />
        </View>
      )}
      <Image
        source={source}
        style={[style, { opacity: loaded ? 1 : 0 }]}
        onLoad={() => setLoaded(true)}
        {...props}
      />
    </View>
  );
};
```

## Accessibility Implementation

### 1. Screen Reader Support
```typescript
// Accessible components
const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  children,
  accessibilityLabel,
  accessibilityHint,
  onPress,
  ...props
}) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      accessibilityLabel={accessibilityLabel}
      accessibilityHint={accessibilityHint}
      accessibilityRole="button"
      {...props}
    >
      {children}
    </TouchableOpacity>
  );
};

// Usage in Quran reader
<VerseCard>
  <AccessibleButton
    accessibilityLabel={`تشغيل الآية ${verseNumber} من سورة ${surahName}`}
    accessibilityHint="اضغط لتشغيل صوت الآية"
    onPress={onPlay}
  >
    <PlayIcon />
  </AccessibleButton>
</VerseCard>
```

### 2. Navigation Accessibility
```typescript
// Accessible navigation
const AccessibleTabBar: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarAccessibilityLabel: 'القائمة السفلية',
        tabBarButton: (props) => (
          <TabBarButton
            {...props}
            accessibilityLabel={`${props.accessibilityLabel}، ${props.focused ? 'الصفحة الحالية' : ''}`}
          />
        ),
      }}
    >
      {/* Tab screens */}
    </Tab.Navigator>
  );
};
```

## Consequences

### Positive
- **Consistency**: Unified design system across all screens
- **Maintainability**: Easy to update and modify components
- **Reusability**: Shared components reduce code duplication
- **Accessibility**: Built-in support for screen readers and navigation
- **Performance**: Optimized rendering and memory usage
- **RTL Support**: Proper Arabic text rendering and layout

### Negative
- **Complexity**: Additional abstraction layer adds complexity
- **Learning Curve**: Team needs to understand component patterns
- **Bundle Size**: Component library adds to app size
- **Overhead**: Some performance overhead from abstraction

### Neutral
- **Development Time**: Initial setup takes longer but pays off later
- **Testing**: Requires comprehensive component testing
- **Documentation**: Need to maintain component documentation

## Future Enhancements

### 1. Design System Expansion
- Component library with Storybook
- Design tokens for spacing, typography, colors
- Animation library and guidelines
- Icon system with multiple variants

### 2. Advanced Components
- Gesture-based navigation
- Advanced audio visualizations
- Interactive Quran study tools
- Custom drawing components

### 3. Performance Improvements
- Component-level code splitting
- Advanced memoization strategies
- Native module integration for performance
- GPU-accelerated animations

### 4. Cross-Platform Consistency
- Web component adaptations
- Desktop layout optimizations
- Platform-specific interactions
- Unified design language

## Alternatives Considered

### 1. UI Component Library (NativeBase, UI Kitten)
- **Pros**: Pre-built components, faster development
- **Cons**: Less customization, bundle size, dependency risks

### 2. Styled Components or Emotion
- **Pros**: CSS-in-JS, dynamic styling
- **Cons**: Runtime overhead, learning curve

### 3. Pure React Native Components
- **Pros**: No dependencies, maximum control
- **Cons**: More boilerplate, inconsistent styling

### 4. Web-Based UI (React Native Web)
- **Pros**: Code sharing with web
- **Cons**: Performance limitations, platform differences

---

*Decision Date: November 2025*  
*Status: Accepted*  
*Next Review: When UI requirements significantly change or performance issues arise*
