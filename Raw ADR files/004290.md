# ADR-2025-10-25: Morfogeneza Form Editor

## Status
Accepted - 2025-10-25

## Context
- Wprowadzamy tryb Morfogeneza", ktory pozwala uzytkownikowi tworzyc i aktywowac wlasne formy Cosia.
- Forma sklada sie z komorek; uzytkownik moze zarzadzac ich liczba (1..max posiadanych) oraz rozmiarem. Komorki nie moga zajmowac tej samej przestrzeni.
- Aktywna forma musi natychmiast odswiezac wizualizacje zarowno w aplikacji, jak i overlay bez dodatkowych cooldownow.
- Storywright zdefiniowal otwarte zagadnienia: plotno (siatka vs. wolna przestrzen), kolizje z organami wewnetrznymi, kontrakt komunikacji z overlay.

## Decision
1. **Model danych formy**
   - `MorphoForm` zawiera: `formId`, `name`, `createdAt`, `cells`, `metadata`.
   - `cells` to lista `MorphoCell` z polami `{id, position (x,y), radius, traits}`.
   - `position` jest zapisywane w lokalnym ukladzie wspolrzednych [0..1] x [0..1]; skalowanie do aktualnego levelu Cosia wykonuje warstwa prezentacji.
2. **Przechowywanie i aktywacja**
   - Formy zapisujemy w lokalnym repozytorium (Room/Datastore) z oznaczeniem `isActive`.
   - Forma 0 jest generowana on-the-fly na podstawie aktualnego stanu lifecycle (niezalezna od repozytorium).
   - Aktywacja formy publikuje event `ActivateMorphoForm(formId)` do core oraz overlay (Nodus implementuje kanal).
3. **Warstwa edytora**
   - Edytor operuje na `MorphoEditorState` (kopia robocza formy) i udostepnia operacje: dodawanie komorki, usuwanie, przesuwanie, zmiana promienia.
   - Limit komorek egzekwowany w ViewModelu edytora.
   - Suwak promienia dziala w zakresie `[minRadius(level), maxRadius(level)]`, gdzie wartosci wynikaja z obwodu organizmu.
4. **Walidacja i kolizje**
   - Guard rails: brak nachodzenia komorek (`distance >= r1 + r2`); komorki musza miescic sie w granicach organizmu (`position` i `radius` mieszcza sie w plotnie).
   - Przy naruszeniach UI natychmiast pokazuje czerwony outline, baner Komorki nachodza - przesun lub zmniejsz" i blokuje zapis/aktywacje; opcjonalny tryb autosort" rozsuwa komorki na najblizsze wolne heksy.
5. **Integracja z overlay**
   - Po aktywacji forma przekazywana jest do `CosLifecycleEngine` jako aktualny layout wizualizacji.
   - Overlay nasluchuje na `ActiveMorphoFormState` i renderuje komorki wedlug tego samego modelu (Nodus zapewnia serializacje przez ponizszy kanal).
6. **Kanal `forma_aktywna`**
   - Wprowadzamy `MorphoFormChannel` (Hilt singleton w `core/morpho`) z `MutableSharedFlow<ActiveMorphoForm>`; domyslnie `replay = 1`, `extraBufferCapacity = 1`, bez suspending emitow.
   - Aplikacja (UI/VM) emituje zdarzenie poprzez `MorphoFormChannel.emit(ActiveMorphoForm(...))` po zapisaniu formy.
   - `LifecycleOverlayService` subskrybuje `channel.updates` w `CoroutineScope(Dispatchers.Main.immediate)` i natychmiast aktualizuje wizualizacje.
   - Dla bezpieczenstwa procesowego utrzymujemy lekki `BroadcastReceiver` (`ACTION_MORPHO_FORM_ACTIVATED`) - overlay rejestruje go tylko gdy dziala poza procesem. Payload zdarzenia: `form_id`, `cells_hash`, `timestamp_epoch_ms`.
   - Event logowany jest do logcat z tagiem `MorphoFormChannel` (INFO) oraz do telemetry (TODO, po wdrozeniu analityki).

## UX Guard Rails (Echo)
Zrodlo: `docs/ux/morphogeneza-ux-research.md`

1. **Limity zasobow:** licznik komorek zmniejsza sie przy dodaniu elementu; cofniecie nie oddaje zasobu (liczone w historii undo).
2. **Nakladanie:** mapa kolizji na siatce heks; czerwony outline + baner bledu; opcjonalne autosort" rozsuwa kolidujace komorki.
3. **Granice organizmu:** outline + strefa ostrzegawcza 5%; suwak promienia odbija poza zakresem.
4. **Kontrola rozmiaru:** slider zalezny od levelu (`minRadius(level)`, `maxRadius(level)`), pokazuje procent zajetej powierzchni.
5. **Historia form:** lokalne undo/redo (min. 5 krokow) + mozliwosc zapisu szkicu (forma nieaktywna).
6. **Feedback aktywacji:** toast w aplikacji, log overlay Forma X aktywowana" oraz podswietlenie aktywnej formy na liscie.
7. **Bezpieczenstwo danych:** flagujemy szkic jako dirty"; przy powrocie proponujemy odzyskanie niedokonczonej formy.
8. **Autosort i cofanie:** autosort proponuje przesuniecie komorek (podglad + komunikat) i po potwierdzeniu przenosi je na najblizsze wolne heksy; undo natychmiast przywraca poprzedni stan.

## Consequences
- Model wspoldzielony przez aplikacje i overlay upraszcza synchronizacje oraz testy automatyczne.
- Uzycie wspolrzednych [0..1] oraz siatki heksagonalnej (snap-to-hex 5%) pozwala na niezalezne od poziomu skalowanie formy.
- Guard rails zostaly zdefiniowane; Echo i Kai musza zadbac o UX/testy zgodne z lista powyzej.
- Kanal `MorphoFormChannel` zapewnia spojny sposob emisji zdarzen; fallback receiver pozwala rozszerzyc rozwiazanie na osobny proces.
- Repozytorium form moze rosnac; potrzebne beda narzedzia do sprzatania/usuwania form (do rozwazenia pozniej).

## Open Questions / TODO
- [x] Orin: zatwierdz model plotna (siatka heksagonalna vs. wolna przestrzen z podpowiedziami).  
  **Decyzja:** uzywamy siatki heksagonalnej z mozliwoscia precyzyjnego dostrajania (snap-to-hex + mikro przesuniecia do 5% promienia).
- [x] Echo: dostarcz wytyczne UX (guard rails, zachowanie suwakow, komunikaty walidacyjne).  
  **Notatka:** `docs/ux/morphogeneza-ux-research.md`
- [x] Lumen: potwierdz, czy potrzebne sa presety form startowych oprocz formy 0.  
  **Decyzja:** Forma 0 pozostaje jedynym presetem; dodatkowe formy powstaja jako zapisy uzytkownika.
- [x] Nodus: wybierz kanal przesylu aktywnej formy (SharedFlow + fallback Broadcast) i zintegruj z eventem.

## Implementation Notes

- [ ] Echo/Lumen: odnotowac w dokumentacji, ze undo/redo i autosort sa w backlogu; przygotowac aktualizacje po wznowieniu prac.
- Pliki: `core/morpho/` (model + repozytorium), `feature/morphogenesis/` (UI + ViewModel).
- Wzorce DI: Hilt modul udostepniajacy `MorphoFormRepository` oraz `MorphoEditorInteractor`.
- Testy: jednostkowe (walidacja kolizji, limity), integracyjne (aktywny layout->overlay).
