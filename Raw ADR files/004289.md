# ADR-2025-10-24: Cos v0.1 Architecture

## Status
Accepted - 2025-10-24

## Context
- Building Cos v0.1 from scratch requires shared lifecycle logic for in-app and overlay modes.
- Overlay must comply with Android 14 restrictions (SYSTEM_ALERT_WINDOW, foreground service type specialUse).
- We want modular structure to support future growth and testing.

## Decision
1. **Module Layout**
   - pp/: hosts Compose application, navigation, DI entry point.
   - eature/cos-lifecycle/: domain models, lifecycle engine, repository interfaces.
   - eature/cos-overlay/: overlay controller, foreground service, Compose overlay UI.
   - core/designsystem/: Material 3 theming and shared components.

2. **State Management**
   - CosLifecycleEngine exposes StateFlow<CosLifecycleState> with ordered list of CellSnapshot (etap + rodzic).
   - CosLifecycleViewModel udostepnia stan do aplikacji i overlay; przyciski steruja ostatnia komorka (Seed  Bud  Mature  Spawned  nowa komorka).
   - Broadcast receiver (LifecycleStageReceiver) mapuje komendy adb (SEED, NARODZINY, DOJRZEWANIE, NOWA_KOMORKA) na akcje silnika.

3. **Overlay Architecture**
    - OverlayController (Hilt singleton) checks permission, starts/stops service, persists position using DataStore.
    - LifecycleOverlayService runs as foreground service with WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, zapewnia Compose lifecycle + saved state owner.
    - Compose overlay UI uses same state as in-app view; gestures: drag + double tap.

4. **Dependency Injection**
   - @Module + @InstallIn(SingletonComponent::class) wiaze DefaultCosLifecycleEngine jako CosLifecycleEngine.
   - @HiltViewModel dla CosLifecycleViewModel wstrzykuje silnik.
   - Overlay service obtains dependencies via EntryPointAccessors.

5. **Rendering & Animations**
   - Canvas przelicza pozycje i promien bazowy tak, by caly organizm miescil sie w stalym kontenerze; wiecej komorek  mniejszy promien.
   - Animacje etapow (SeedBudMatureSpawned) realizowane sa przez plynne tweeny w Compose.
   - Brak wymogu styku komorek; pozycje ukladane sa rownomiernie po okregu.

## Consequences
- Manual commands i adb pozwalaja debugowac overlay bez czekania na uplyw czasu.
- Silnik zarzadza kolejnoscia komorek (tylko ostatnia moze przejsc do kolejnego etapu i wygenerowac potomka).
- Overlay i aplikacja dziela ten sam stan, wiec testy moga dzialac na emulatorze Pixel 5.

## Diagram
`
app/MainActivity          feature/cos-overlay
     |                            |
CosLifecycleViewModel --- StateFlow<CosLifecycleState> --- LifecycleOverlayService
     |                            |
   Compose UI             Compose overlay (drag/double tap)

CosLifecycleEngine <-> Broadcast Receiver / UI commands
`

## Follow-up
- Lumen moze eksperymentowac z dodatkowymi wzorcami rozmieszczenia (spirala, geste skupiska).
- Kai rozszerza testy o animacje i automatyczne sekwencje adb.
- Nyx aktualizuje pamiec dlugoterminowa o nowy proces manualnego cyklu.
