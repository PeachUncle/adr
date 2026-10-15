# ADR-003: Authentication & Security

## Status

Accepted

## Context

TodoList membutuhkan authentication yang secure, user-friendly, dan mendukung collaboration features.

## Decision

### Strategy: Session-Based Authentication

Menggunakan Spring Security dengan session management (bukan JWT).

**Alasan:**
- Traditional web app, bukan API-first
- Session lebih simple untuk server-rendered apps
- Built-in support di Spring Security
- Lebih secure by default (HttpOnly cookies)

## Implementation

### Security Configuration

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/", "/register", "/login").permitAll()
            .requestMatchers("/css/**", "/js/**").permitAll()
            .anyRequest().authenticated()
        )
        .formLogin(form -> form
            .loginPage("/login")
            .defaultSuccessUrl("/dashboard")
        )
        .logout(logout -> logout
            .logoutSuccessUrl("/")
            .invalidateHttpSession(true)
        )
        .csrf(csrf -> csrf.csrfTokenRepository(
            CookieCsrfTokenRepository.withHttpOnlyFalse()
        ));
    return http.build();
}
```

### Password Security

```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(10);  // 10 rounds
}
```

**Requirements:**
- Minimum 8 characters
- At least 1 uppercase
- At least 1 lowercase
- At least 1 number
- At least 1 special character

### Session Configuration

```yaml
server:
  servlet:
    session:
      timeout: 30m
      cookie:
        http-only: true
        secure: true      # HTTPS only (prod)
        same-site: strict # CSRF protection
```

### Account Lockout

```java
if (failedAttempts >= 5) {
    user.setLockTime(LocalDateTime.now().plusMinutes(15));
    throw new LockedException("Account locked. Try again in 15 minutes.");
}
```

### Method-Level Security

```java
@PreAuthorize("@taskSecurity.canAccessTask(#taskId, authentication)")
public TaskDto getTask(UUID taskId) { ... }
```

## Security Checklist

### Authentication
- [ ] BCrypt password hashing (strength 10)
- [ ] CSRF protection enabled
- [ ] Session timeout: 30 minutes
- [ ] Remember-me: 7 days
- [ ] Account lockout: 5 failed attempts
- [ ] Email verification before full access

### Authorization
- [ ] @PreAuthorize on service methods
- [ ] Owner check before modify/delete
- [ ] Team role check (OWNER, MEMBER, VIEWER)

### Headers
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] X-XSS-Protection: 1
- [ ] Content-Security-Policy configured

### Input
- [ ] Thymeleaf auto-escaping (XSS)
- [ ] JPA parameterized queries (SQL injection)
- [ ] Bean validation (@Valid)

## Security Tests

```java
@Test
void shouldRejectUnauthorizedAccess() {
    mockMvc.perform(get("/tasks"))
        .andExpect(status().is3xxRedirection())
        .andExpect(redirectedUrlPattern("**/login"));
}

@Test
void shouldEnforceCSRF() {
    mockMvc.perform(post("/tasks").param("title", "Test"))
        .andExpect(status().isForbidden());
}

@Test
void shouldLockAccountAfter5FailedAttempts() {
    for (int i = 0; i < 5; i++) {
        authService.loginFailed(email);
    }
    assertTrue(authService.isBlocked(email));
}
```

## What NOT to Log

- Passwords (plaintext or hashed)
- Password reset tokens
- Session IDs
- API keys

## What to Log

- Login attempts (success/failure)
- Unauthorized access attempts
- Password changes
- Admin actions

## Reference

- Architecture: [`../02-architecture.md`](../02-architecture.md)
- Implementation: [`../03-implementation-plan.md`](../03-implementation-plan.md)
