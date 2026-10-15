# ADR-0002: Audio Architecture with EveryAyah API Integration

## Status
Accepted

## Context
The Quran application requires comprehensive audio recitation capabilities with the following requirements:

- Multiple reciters with different styles and qualities
- Verse-by-verse playback with navigation controls
- Offline caching for continuous listening without internet
- Background playback support
- Seamless switching between reciters
- Progress tracking and bookmark capabilities

## Decision
We implemented a layered audio architecture using the EveryAyah API for audio sources and Expo-AV for playback, with local caching for offline support.

### Architecture Components

#### 1. Audio Service Layer (`AudioService.ts`)
- **Single responsibility**: Manages audio playback operations
- **State management**: Tracks current verse, playback status, and settings
- **API integration**: Builds URLs and handles remote audio loading
- **Local file management**: Coordinates with storage service for caching

#### 2. Audio Player Context (`AudioPlayerContext.tsx`)
- **Global state**: Provides app-wide audio state using React Context
- **User preferences**: Manages reciter selection, speed, and repeat modes
- **Playback controls**: Exposes play, pause, next, previous operations
- **Position tracking**: Saves and restores last listening position

#### 3. Storage Integration
- **Local caching**: Downloads and stores audio files locally
- **Progressive loading**: Downloads on-demand with background queuing
- **Cache management**: Handles storage limits and cleanup
- **Offline fallback**: Uses local files when internet unavailable

### API Integration Strategy

#### EveryAyah API Usage
```typescript
// URL Pattern: https://everyayah.com/data/{reciterPath}/{surah}{verse}.mp3
const buildAudioUrl = (reciterPath: string, surahId: number, verseId: number) => {
  const surahPadded = (surahId + 1).toString().padStart(3, '0');
  const versePadded = verseId.toString().padStart(3, '0');
  return `https://everyayah.com/data/${reciterPath}/${surahPadded}${versePadded}.mp3`;
};
```

#### Reciter Management
- **Static configuration**: Reciter data stored in JSON file
- **Quality levels**: Multiple bitrate options (128kbps, 192kbps)
- **Style categorization**: Different recitation styles available
- **Fallback handling**: Graceful degradation when reciter unavailable

## Consequences

### Positive
- **Reliable audio source**: EveryAyah provides stable, high-quality recitations
- **Offline capability**: Users can download for offline listening
- **Smooth transitions**: Seamless switching between verses and reciters
- **Background support**: Continuous playback when app minimized
- **Memory efficient**: Streaming reduces initial app size

### Negative
- **Network dependency**: Initial playback requires internet connection
- **Storage usage**: Cached audio files consume device storage
- **API limitation**: Single point of failure for audio content
- **Download time**: Large surahs require significant download time

### Neutral
- **Complexity**: Multi-layer architecture adds implementation complexity
- **Maintenance**: Requires coordination between service, context, and storage layers
- **Performance**: Needs optimization for large file operations

## Implementation Details

### Audio Playback Flow
1. **User Action**: Select verse/surah for playback
2. **Cache Check**: Verify local file availability
3. **URL Resolution**: Build EveryAyah API URL if needed
4. **Audio Loading**: Load from local or remote source
5. **Playback Control**: Start/stop/pause based on user input
6. **Progress Tracking**: Update position and save state
7. **Next Verse**: Auto-advance based on repeat mode

### Caching Strategy
```typescript
// Progressive download with progress tracking
async preloadVerse(reciterPath: string, reciterId: string, surahId: number, verseId: number) {
  const url = this.buildAudioUrl(reciterPath, surahId, verseId);
  return await StorageService.downloadAudioFile(url, reciterId, surahId, verseId);
}
```

### Background Playback Configuration
```typescript
await Audio.setAudioModeAsync({
  allowsRecordingIOS: false,
  staysActiveInBackground: true,
  playsInSilentModeIOS: true,
  shouldDuckAndroid: true,
  playThroughEarpieceAndroid: false,
});
```

## Alternatives Considered

### 1. Self-hosted Audio Files
- **Pros**: Full control, no external dependencies
- **Cons**: Hosting costs, bandwidth management, scalability issues

### 2. YouTube API Integration
- **Pros**: Vast reciter library, established platform
- **Cons**: API restrictions, background playback limitations, ads

### 3. Spotify/Apple Music Integration
- **Pros**: Professional audio quality, existing user accounts
- **Cons**: API limitations, content restrictions, subscription requirements

### 4. No Offline Caching
- **Pros**: Simpler implementation, no storage concerns
- **Cons**: Poor user experience, high data usage, network dependency

## Performance Optimizations

### 1. Lazy Loading
- Download audio on-demand rather than bulk downloading
- Prioritize current verse and next verses

### 2. Progressive Caching
- Download next verses in background during playback
- Implement queue management for smooth transitions

### 3. Memory Management
- Proper cleanup of audio resources
- Limit concurrent downloads and active audio instances

### 4. Storage Optimization
- Compress audio files when possible
- Implement LRU eviction for cache management

## Future Enhancements

### 1. Multiple Audio Sources
- Add alternative audio providers for redundancy
- Implement fallback chain for unavailable reciters

### 2. Advanced Caching
- Predictive downloading based on user patterns
- Smart cache management with user preferences

### 3. Audio Quality Options
- Dynamic quality adjustment based on network speed
- User-selectable quality tiers

### 4. Streaming Optimization
- Adaptive bitrate streaming
- Buffer management for poor network conditions

---

*Decision Date: November 2025*  
*Status: Accepted*  
*Next Review: When new audio features or performance issues arise*
