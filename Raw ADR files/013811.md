# ADR 0001 - MVVM Architecture with Provider Pattern

## Status
✅ Accepted (2025-02-01)

## Context
We need a maintainable architecture for our Flutter blog application that:
- Separates business logic from UI
- Provides testable components
- Supports multiple platforms (web/mobile)
- Handles state management efficiently

## Decision
Adopt a modified MVVM pattern using Provider for state management with the following structure:

```plaintext
lib/
├── src/
│   ├── core/
│   │   ├── app_router.dart    # Routing configuration
│   │   ├── base_view.dart     # Base widget for view binding
│   │   └── base_viewmodel.dart# Abstract ViewModel class
│   │
│   ├── features/
│   │   └── blog/
│   │       ├── data/
│   │       │   ├── models/
│   │       │   └── repositories/
│   │       └── presentation/
│   │           ├── view_models/
│   │           ├── views/
│   │           └── widgets/
│   │
│   └── shared/
│       ├── constants.dart     # Design system constants
│       └── utilities.dart     # Common utilities
```

### Key Components

1. **BaseViewModel**
```dart
abstract class BaseViewModel extends ChangeNotifier {
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  void setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
```

2. **BlogRepository Pattern**
```dart
abstract class BlogRepository {
  Future<List<BlogPost>> getPosts();
  Future<BlogPost> getPostById(String id);
}
```

3. **ViewModels**
```dart
class BlogListViewModel extends BaseViewModel {
  final BlogRepository repository;
  
  List<BlogPost> _posts = [];
  List<BlogPost> get posts => _posts;

  BlogListViewModel(this.repository);

  Future<void> loadPosts() async {
    setLoading(true);
    _posts = await repository.getPosts();
    setLoading(false);
  }
}
```

4. **Views**
```dart
class BlogListView extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ViewModelBuilder<BlogListViewModel>.reactive(
      viewModelBuilder: () => BlogListViewModel(getIt<BlogRepository>()),
      onModelReady: (model) => model.loadPosts(),
      builder: (context, model, child) {
        if (model.isLoading) return LoadingIndicator();
        return ListView.builder(
          itemCount: model.posts.length,
          itemBuilder: (context, index) => BlogPostItem(model.posts[index]),
        );
      },
    );
  }
}
```

5. **Routing**
```dart
class AppRouter {
  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case Routes.blogList:
        return MaterialPageRoute(builder: (_) => BlogListView());
      case Routes.blogPost:
        return MaterialPageRoute(builder: (_) => BlogPostView());
      default:
        return MaterialPageRoute(builder: (_) => NotFoundView());
    }
  }
}
```

## Consequences
- ✅ Clear separation of concerns between UI and business logic
- ✅ Easier testing through mocked ViewModels
- ✅ Scalable state management with Provider
- ➖ Slightly increased boilerplate for simple views
- ➖ Requires strict discipline in layer communication

## Implementation Steps
1. Create `core` directory structure with base classes
2. Implement Provider configuration in main app widget
3. Create blog feature structure with sample ViewModel/View pair
4. Add responsive layout handlers for web/mobile breakpoints
5. Set up dependency injection using get_it package

> **Note:** All ViewModels must extend `BaseViewModel` and Views should use `ViewModelBuilder` for proper Provider integration.
