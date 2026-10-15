# ADR-004: Testing Strategy

## Status
Accepted

## Date
2024-07-29

## Context

We need a comprehensive testing strategy for our Angular application that covers:
- Unit testing for components, services, and pipes
- Integration testing for component interactions
- End-to-end testing for user workflows
- Code coverage requirements
- CI/CD integration
- Developer productivity and test maintenance

## Decision

We decided to implement a **multi-layered testing strategy** using:
- **Karma + Jasmine** for unit and integration testing
- **Angular Testing Utilities** for component testing
- **Test coverage** with minimum 90% threshold
- **CI/CD integration** with automated test execution
- **Testing best practices** and patterns

## Consequences

### Positive
- **Built-in Angular support**: Karma and Jasmine come preconfigured with Angular CLI
- **Mature ecosystem**: Well-established testing tools with extensive documentation
- **IDE integration**: Excellent support in VS Code and other IDEs
- **Debugging capabilities**: Easy to debug tests in browser
- **Community**: Large community and extensive resources
- **Coverage reporting**: Built-in code coverage with Istanbul

### Negative
- **Slower execution**: Karma runs tests in real browsers, which can be slower
- **Configuration complexity**: More complex setup compared to Jest
- **Memory usage**: Can consume more memory for large test suites
- **Flaky tests**: Browser-based tests can be more prone to timing issues

## Alternatives Considered

### Jest
- **Pros**: Faster execution, snapshot testing, better mocking
- **Cons**: Requires additional configuration for Angular, less Angular-specific tooling

### Cypress (E2E)
- **Pros**: Better developer experience, time-travel debugging
- **Cons**: Requires separate tool, additional learning curve

### Protractor (deprecated)
- **Pros**: Angular-specific E2E testing
- **Cons**: Deprecated by Angular team, being phased out

## Implementation Details

### Test Configuration
```javascript
// karma.conf.js
module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' },
        { type: 'lcov' }
      ],
      check: {
        global: {
          statements: 90,
          branches: 80,
          functions: 90,
          lines: 90
        }
      }
    },
    browsers: ['Chrome'],
    singleRun: false,
    restartOnFileChange: true
  });
};
```

## Testing Patterns

### Unit Testing Components
```typescript
describe('UserProfileComponent', () => {
  let component: UserProfileComponent;
  let fixture: ComponentFixture<UserProfileComponent>;
  let userService: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('UserService', ['getUser', 'updateUser']);

    await TestBed.configureTestingModule({
      imports: [UserProfileComponent, ReactiveFormsModule],
      providers: [
        { provide: UserService, useValue: spy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(UserProfileComponent);
    component = fixture.componentInstance;
    userService = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display user name when user is provided', () => {
    // Arrange
    const user: User = { id: '1', name: 'John Doe', email: 'john@example.com' };
    component.user = user;

    // Act
    fixture.detectChanges();

    // Assert
    const nameElement = fixture.debugElement.query(By.css('.user-name'));
    expect(nameElement.nativeElement.textContent).toContain('John Doe');
  });

  it('should emit userUpdated when form is submitted with valid data', () => {
    // Arrange
    spyOn(component.userUpdated, 'emit');
    const user: User = { id: '1', name: 'John Doe', email: 'john@example.com' };
    component.user = user;
    fixture.detectChanges();

    // Act
    component.userForm.patchValue({ name: 'Jane Doe', email: 'jane@example.com' });
    component.onSubmit();

    // Assert
    expect(component.userUpdated.emit).toHaveBeenCalledWith(
      jasmine.objectContaining({ name: 'Jane Doe', email: 'jane@example.com' })
    );
  });
});
```

### Unit Testing Services
```typescript
describe('UserService', () => {
  let service: UserService;
  let httpMock: jasmine.SpyObj<HttpClient>;

  beforeEach(() => {
    const spy = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);

    TestBed.configureTestingModule({
      providers: [
        UserService,
        { provide: HttpClient, useValue: spy }
      ]
    });

    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpClient) as jasmine.SpyObj<HttpClient>;
  });

  it('should fetch users successfully', () => {
    // Arrange
    const mockUsers: User[] = [
      { id: '1', name: 'John Doe', email: 'john@example.com' }
    ];
    httpMock.get.and.returnValue(of({ data: mockUsers }));

    // Act
    const result$ = service.getUsers();

    // Assert
    result$.subscribe(users => {
      expect(users).toEqual(mockUsers);
      expect(httpMock.get).toHaveBeenCalledWith('/api/users');
    });
  });

  it('should handle error when fetching users fails', () => {
    // Arrange
    const errorMessage = 'Network error';
    httpMock.get.and.returnValue(throwError(() => new Error(errorMessage)));

    // Act
    const result$ = service.getUsers();

    // Assert
    result$.subscribe({
      error: (error) => {
        expect(error.message).toContain('Failed to fetch users');
      }
    });
  });
});
```

### Testing Observables
```typescript
describe('UserStateService', () => {
  let service: UserStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserStateService);
  });

  it('should emit users when setUsers is called', () => {
    // Arrange
    const users: User[] = [{ id: '1', name: 'John', email: 'john@example.com' }];
    let emittedUsers: User[] | undefined;

    // Act
    service.users$.subscribe(result => emittedUsers = result);
    service.setUsers(users);

    // Assert
    expect(emittedUsers).toEqual(users);
  });

  it('should combine loading and users state in viewModel$', () => {
    // Arrange
    const users: User[] = [{ id: '1', name: 'John', email: 'john@example.com' }];
    let viewModel: any;

    // Act
    service.viewModel$.subscribe(vm => viewModel = vm);
    service.setUsers(users);
    service.setLoading(true);

    // Assert
    expect(viewModel).toEqual({
      users: users,
      loading: true,
      error: null
    });
  });
});
```

## Testing Guidelines

### Test Structure (AAA Pattern)
```typescript
it('should do something when condition is met', () => {
  // Arrange - Set up test data and conditions
  const input = 'test input';
  const expectedOutput = 'expected result';
  
  // Act - Execute the functionality being tested
  const result = service.processInput(input);
  
  // Assert - Verify the expected outcome
  expect(result).toBe(expectedOutput);
});
```

### Test Naming Convention
- **Descriptive names**: "should return user when valid ID is provided"
- **Behavior focused**: Focus on what the code should do, not how
- **Consistent format**: "should [expected behavior] when [condition]"

### Mock Strategy
```typescript
// Service mocks
const mockUserService = jasmine.createSpyObj('UserService', {
  getUser: of(mockUser),
  updateUser: of(updatedUser)
});

// HTTP mocks
const mockHttpClient = jasmine.createSpyObj('HttpClient', ['get', 'post']);
mockHttpClient.get.and.returnValue(of(mockResponse));

// Component input mocks
const mockUser: User = {
  id: '1',
  name: 'Test User',
  email: 'test@example.com'
};
```

### Test Data Management
```typescript
// Create factory functions for test data
export function createMockUser(overrides: Partial<User> = {}): User {
  return {
    id: '1',
    name: 'Test User',
    email: 'test@example.com',
    isActive: true,
    createdAt: new Date(),
    ...overrides
  };
}

// Use in tests
const activeUser = createMockUser({ isActive: true });
const inactiveUser = createMockUser({ isActive: false });
```

## Coverage Requirements

### Coverage Thresholds
- **Statements**: 90% minimum
- **Branches**: 80% minimum  
- **Functions**: 90% minimum
- **Lines**: 90% minimum

### Coverage Exclusions
```typescript
// Exclude from coverage with comments
/* istanbul ignore next */
if (environment.production) {
  // Production-only code
}

// Exclude entire files in karma.conf.js
coverageReporter: {
  exclude: [
    'src/**/*.spec.ts',
    'src/**/test-data.ts',
    'src/**/mock-*.ts'
  ]
}
```

## CI/CD Integration

### GitHub Actions Configuration
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - run: npm ci
    - run: npm run test -- --watch=false --browsers=ChromeHeadless --code-coverage
    - name: Upload coverage reports
      uses: actions/upload-artifact@v4
      with:
        name: coverage-report
        path: coverage/
```

### Test Scripts
```json
{
  "scripts": {
    "test": "ng test",
    "test:ci": "ng test --watch=false --browsers=ChromeHeadless --code-coverage",
    "test:coverage": "ng test --code-coverage",
    "test:watch": "ng test --watch=true"
  }
}
```

## Best Practices

### Do's
- ✅ Write tests before or alongside implementation (TDD/BDD)
- ✅ Keep tests simple and focused on single behavior
- ✅ Use descriptive test names
- ✅ Mock external dependencies
- ✅ Test both happy path and error scenarios
- ✅ Maintain test code quality same as production code

### Don'ts
- ❌ Test implementation details
- ❌ Write tests that depend on other tests
- ❌ Use production data in tests
- ❌ Skip error case testing
- ❌ Write overly complex test setups
- ❌ Ignore failing tests

## Performance Optimization

### Test Execution Speed
```typescript
// Use TestBed.overrideComponent for faster component tests
beforeEach(() => {
  TestBed.overrideComponent(UserListComponent, {
    set: {
      providers: [
        { provide: UserService, useValue: mockUserService }
      ]
    }
  });
});

// Use async/await for cleaner async test code
it('should load users on init', async () => {
  await component.ngOnInit();
  expect(component.users.length).toBeGreaterThan(0);
});
```

## Related Decisions
- ADR-001: Frontend Framework Selection (Angular testing ecosystem)
- ADR-002: State Management Strategy (Testing observables and services)

## Review Date
This decision should be reviewed in 6 months (January 2025) or when:
- Test execution time becomes problematic
- Coverage requirements are consistently not met
- New testing tools provide significant advantages