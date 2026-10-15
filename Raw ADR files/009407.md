# ADR 004: Functional Error Handling with Either Pattern

## Status
**Accepted** - November 2025

## Context
Traditional try-catch error handling in Dart has several issues:
- Exceptions can be thrown anywhere, making it hard to track all possible errors
- No compile-time guarantee that errors are handled
- Error handling code scattered throughout the application
- Difficult to test error scenarios

We need a more robust, functional approach to error handling that:
- Makes errors explicit in function signatures
- Forces developers to handle errors
- Provides compile-time safety
- Is easy to test

## Decision
We will use the **Either pattern** from the `dartz` package for error handling throughout the application.

### Core Concept

```dart
// Either<Left, Right>
// Left = Failure (error case)
// Right = Success (happy path)

Future<Either<Failure, List<Todo>>> getTodos();
```

## Implementation

### Failure Hierarchy

```dart
// Domain Layer - Abstract failures
abstract class Failure {
  final String message;
  const Failure(this.message);
}

class CacheFailure extends Failure {
  const CacheFailure(String message) : super(message);
}

class ServerFailure extends Failure {
  const ServerFailure(String message) : super(message);
}

class NetworkFailure extends Failure {
  const NetworkFailure([String message = 'No internet connection']) 
      : super(message);
}
```

### Exception Hierarchy

```dart
// Data Layer - Concrete exceptions
class CacheException implements Exception {
  final String message;
  const CacheException(this.message);
}

class ServerException implements Exception {
  final String message;
  const ServerException(this.message);
}
```

### Usage Pattern

#### Repository Implementation (Data Layer)
```dart
@override
Future<Either<Failure, List<Todo>>> getTodos() async {
  try {
    final todos = await localDataSource.getAllTodos();
    return Right(todos);
  } on CacheException catch (e) {
    return Left(CacheFailure(e.message));
  } on ServerException catch (e) {
    return Left(ServerFailure(e.message));
  } catch (e) {
    return Left(GeneralFailure(e.toString()));
  }
}
```

#### Use Case (Domain Layer)
```dart
class GetTodos {
  final TodoRepository repository;
  
  Future<Either<Failure, List<Todo>>> call() async {
    return await repository.getTodos();
  }
}
```

#### BLoC (Presentation Layer)
```dart
Future<void> _onLoadTodos(LoadTodos event, Emitter<TodoState> emit) async {
  emit(const TodoState.loading());
  
  final result = await getTodos();
  
  result.fold(
    (failure) => emit(TodoState.error(message: failure.message)),
    (todos) => emit(TodoState.loaded(todos: todos)),
  );
}
```

## Benefits

### Type Safety
✅ **Compile-Time Checking**: Errors are part of the type signature  
✅ **No Uncaught Exceptions**: All errors must be handled explicitly  
✅ **IDE Support**: Auto-completion for both success and failure cases  

### Testability
✅ **Easy to Mock**: Simple to return Left(Failure) in tests  
✅ **Clear Expectations**: Test both success and failure paths  
✅ **No Exception Handling**: Just check Left or Right  

Example test:
```dart
test('should return CacheFailure when repository fails', () async {
  // arrange
  when(() => mockRepository.getTodos())
      .thenAnswer((_) async => const Left(CacheFailure('Cache error')));
  
  // act
  final result = await useCase();
  
  // assert
  expect(result, const Left(CacheFailure('Cache error')));
});
```

### Maintainability
✅ **Explicit Error Handling**: Can't forget to handle errors  
✅ **Consistent Pattern**: Same approach throughout the app  
✅ **Self-Documenting**: Function signature shows possible errors  

### Composability
✅ **Functional Composition**: Chain operations easily  
✅ **Transform Results**: Use map, flatMap, fold  
✅ **Combine Multiple Results**: Handle multiple Either values  

## Consequences

### Positive
✅ **No Runtime Crashes**: All errors caught and typed  
✅ **Better Testing**: Easy to test error scenarios  
✅ **Clear Contracts**: Function signatures show what can go wrong  
✅ **Functional Style**: Clean, composable code  
✅ **IDE Assistance**: Auto-completion for error handling  

### Negative
⚠️ **Learning Curve**: Team must understand Either pattern  
⚠️ **Verbosity**: More code than simple try-catch  
⚠️ **Dependency**: Requires dartz package  

### Mitigations
- Provide comprehensive documentation
- Code examples for common patterns
- Helper functions for common operations
- Team training on functional programming concepts

## Error Mapping Strategy

### Data Layer → Domain Layer
```dart
CacheException   → CacheFailure
ServerException  → ServerFailure
NetworkException → NetworkFailure
Exception        → GeneralFailure
```

### Logging Strategy
```dart
try {
  // operation
} on CacheException catch (e) {
  logger.e('Cache error: ${e.message}');
  return Left(CacheFailure(e.message));
}
```

## Alternatives Considered

### 1. Traditional Try-Catch
```dart
Future<List<Todo>> getTodos() async {
  try {
    return await localDataSource.getAllTodos();
  } catch (e) {
    throw CacheException(e.toString());
  }
}
```
- ❌ Rejected: No compile-time safety
- ❌ Easy to forget error handling
- ❌ Exceptions can propagate unexpectedly

### 2. Result Class
```dart
class Result<T> {
  final T? data;
  final String? error;
  bool get isSuccess => error == null;
}
```
- ❌ Rejected: Not type-safe
- ❌ Can have both data and error
- ❌ No functional composition

### 3. Callbacks
```dart
void getTodos({
  required Function(List<Todo>) onSuccess,
  required Function(String) onError,
});
```
- ❌ Rejected: Callback hell
- ❌ Hard to compose
- ❌ No return value

## Best Practices

### Do's
✅ Always use Either for operations that can fail  
✅ Create specific Failure types for different errors  
✅ Log errors before returning Left  
✅ Use fold() to handle both cases in presentation layer  
✅ Test both Left and Right paths  

### Don'ts
❌ Don't mix Either with try-catch in business logic  
❌ Don't throw exceptions from use cases  
❌ Don't ignore Left values  
❌ Don't create too many specific failure types  

## References
- [Dartz Package](https://pub.dev/packages/dartz)
- [Functional Programming in Dart](https://dart.dev/guides/language/language-tour#functions)
- [Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- [Either Type Explained](https://blog.logrocket.com/using-either-monad-handle-errors-typescript/)
