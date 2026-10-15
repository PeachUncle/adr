# ADR 002: Hybrid State Management (BLoC + Riverpod)

## Status
**Accepted** - November 2025

## Context
We need a state management solution that provides:
- Dependency injection for services
- Reactive state management for complex business logic
- Easy testing capabilities
- Type safety and compile-time errors

## Decision
We will use a **hybrid approach**:

### BLoC (Business Logic Component)
**Purpose**: Feature-specific state management

**Use Cases**:
- Todo feature state (loading, loaded, error)
- Auth feature state (authenticated, unauthenticated)
- Complex state transitions
- Event-driven business logic

**Benefits**:
- ✅ Clear separation of business logic and UI
- ✅ Excellent testing support (bloc_test)
- ✅ Event-driven architecture
- ✅ Immutable states with Freezed
- ✅ Time-travel debugging

### Riverpod
**Purpose**: Dependency injection and simple global state

**Use Cases**:
- Repository providers
- Service providers (DI)
- Configuration state
- Global app state (theme, locale)

**Benefits**:
- ✅ Type-safe providers
- ✅ Compile-time error detection
- ✅ Automatic disposal
- ✅ Easy to test with overrides
- ✅ No BuildContext required

## Implementation

### BLoC Structure
```dart
// Events
abstract class TodoEvent {}
class LoadTodos extends TodoEvent {}

// States
abstract class TodoState {}
class TodoLoading extends TodoState {}
class TodoLoaded extends TodoState {
  final List<Todo> todos;
}

// BLoC
class TodoBloc extends Bloc<TodoEvent, TodoState> {
  final TodoRepository repository;
  // Business logic here
}
```

### Riverpod Structure
```dart
// Providers
final todoRepositoryProvider = Provider<TodoRepository>((ref) {
  return getIt<TodoRepository>();
});

final todoBlocProvider = Provider<TodoBloc>((ref) {
  return TodoBloc(ref.watch(todoRepositoryProvider));
});
```

## Consequences

### Positive
✅ **Best of Both Worlds**: BLoC for complex state, Riverpod for DI  
✅ **Type Safety**: Compile-time errors for both  
✅ **Testability**: Excellent testing support for both  
✅ **Maintainability**: Clear patterns for different use cases  
✅ **Performance**: Efficient rebuilds with both solutions  

### Negative
⚠️ **Two Systems**: Team must learn both BLoC and Riverpod  
⚠️ **Dependency**: Two state management packages  
⚠️ **Consistency**: Need clear guidelines on when to use which  

### Mitigations
- Clear documentation on when to use each
- Code examples for common patterns
- Team training on both solutions
- Consistent folder structure

## Guidelines

### Use BLoC When:
- Complex state transitions
- Event-driven business logic
- Need time-travel debugging
- Multiple events affecting single state

### Use Riverpod When:
- Dependency injection
- Simple global state
- Configuration values
- Service access

## Alternatives Considered

### 1. Provider Only
- ❌ Rejected: Limited for complex state management
- ❌ No built-in event handling

### 2. BLoC Only
- ❌ Rejected: Overkill for dependency injection
- ❌ More boilerplate for simple use cases

### 3. GetX
- ❌ Rejected: Too much magic, hard to debug
- ❌ Tight coupling with framework

### 4. Redux
- ❌ Rejected: Too much boilerplate
- ❌ Single global store can become large

## References
- [BLoC Library Documentation](https://bloclibrary.dev/)
- [Riverpod Documentation](https://riverpod.dev/)
- [Flutter State Management Options](https://docs.flutter.dev/data-and-backend/state-mgmt/options)
