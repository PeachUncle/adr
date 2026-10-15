# TSDR-1004 Mobile UI Framework

## Status

Accepted, Proposed, Deprecated or Superseded (list DR)

## Context

We want iOS and Android mobile apps

Do not want desktop applications

## Decision



## Why / Notes



## Consequences



## Other Possible Options

### Native

https://www.reddit.com/r/iOSProgramming/comments/1gavd7s/as_of_2024_what_are_the_distinct_advantages_that/

Kotlin Multiplatform?
I thought there was some other library that was cross platform. Pretty much write
native on both but then share the same library?



### Flutter

from google

- https://www.reddit.com/r/FlutterDev/comments/1j2vmxj/develop_the_business_logic_first_approach/
- https://www.reddit.com/r/FlutterDev/comments/1jayrqx/the_final_word_on_flutter_architecture/
- https://www.reddit.com/r/FlutterDev/comments/1k9imhf/flutter_clean_architecture_implementation_guide/
- https://www.reddit.com/r/FlutterDev/comments/1kh9owe/whats_the_catch_with_flutter/
- https://www.reddit.com/r/FlutterDev/comments/1khrhrx/aside_from_being_cross_platform_why_do_some_devs/
- https://www.reddit.com/r/FlutterDev/comments/1kjnn2l/flutter_architecture_riverpod_bloc_or_vanilla/
- https://www.reddit.com/r/FlutterDev/comments/1klhp49/i_compiled_80_flutter_tips_into_a_web_page/
- https://www.reddit.com/r/FlutterDev/comments/1jtjliu/what_are_your_favorites_flutter_packages_that_you/
- https://www.reddit.com/r/FlutterDev/comments/1jwm4nn/i_made_a_hidden_inapp_debug_view_for_flutter_apps/
- https://www.reddit.com/r/FlutterDev/comments/1jxbf8q/whats_a_concept_you_understand_really_well_that/
- https://www.reddit.com/r/FlutterDev/comments/1k288c8/flutter_has_too_many_state_management_solutions/
- https://www.reddit.com/r/FlutterDev/comments/1k2s4zy/new_dart_formatting_is_hurting_productivity/
- https://www.reddit.com/r/FlutterDev/comments/1jv1iad/is_the_future_for_macpc_flutter_apps_bright_or_not/
- https://www.reddit.com/r/FlutterDev/comments/1k32q3g/gradle_sucks/
- https://www.reddit.com/r/FlutterDev/comments/1k883sp/what_are_your_favorite_underrated_flutter_packages/
- https://www.reddit.com/r/FlutterDev/comments/1klltpf/how_does_your_maindart_file_looks_like_any_good/
- https://www.reddit.com/r/FlutterDev/comments/1jspg4h/whats_flutter_like_for_a_ui_newbie/
- https://www.reddit.com/r/FlutterDev/comments/1jv1iad/is_the_future_for_macpc_flutter_apps_bright_or_not/
- https://www.reddit.com/r/FlutterDev/comments/1jv2efg/coming_back_after_a_few_years_how_much_has_changed/
- https://www.reddit.com/r/FlutterDev/comments/1jw2afz/sincere_question_why_would-you-use-flutter-for/


flutter vs react
- https://www.reddit.com/r/FlutterDev/comments/1jrvde8/performance_showdown_flutter_vs_react_native_vs/

### Svelt Native

### Others

- [Fyne](https://fyne.io/)
  - mobile and desktop. may be better at mobile than desktop
  - https://github.com/fyne-io/fyne
  - https://www.reddit.com/r/golang/comments/1jh60pr/we_are_developing_a_fyne_crud_gui_generator/
  - material design, movern ui look feel
- Gomobile
  - https://dev.to/nikl/using-golang-gomobile-to-build-android-application-with-code-18jo

## Not an Option

### React Native

we aren't using react for web.

### Others

- [Wails](https://wails.io/)
  - desktop apps using web technologies
  - https://www.reddit.com/r/golang/comments/1k0t8y6/wails_is_it_still_gaining_momentum_for_go_desktop/
- https://github.com/cogentcore/core
  - last release 2024-06
- [Gio](https://gioui.org/)
  - Linux, macOS, Windows, Android, iOS, FreeBSD, OpenBSD and WebAssembly
  - not focused on mobile. we don't need a desktop app.
- [Awesome Go: GUI](https://github.com/avelino/awesome-go?tab=readme-ov-file#gui)
  