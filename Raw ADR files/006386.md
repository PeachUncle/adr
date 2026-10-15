# ADR-003: Using Kotlin DSL for Gradle Build Configuration

## Status
Accepted

## Date
2025-03-01

## Context
Our project uses Gradle as its build tool, and we need to decide on the language to use for our build scripts. Gradle supports two Domain-Specific Languages (DSLs) for build configuration:

1. **Groovy DSL** (traditional build.gradle files)
2. **Kotlin DSL** (build.gradle.kts files)

We need to select the most appropriate DSL that:

- Provides good IDE support with code completion and navigation
- Offers type safety and compile-time error checking
- Aligns with our team's skills and preferences
- Supports all required Gradle functionality
- Maintains readability and maintainability
- Integrates well with our development workflow
- Scales appropriately with build complexity
- Has good documentation and community support

The choice of build script DSL affects developer productivity, build script maintainability, and the overall build system reliability.

## Decision
We will use **Kotlin DSL** for our Gradle build scripts. Our build files will use the `.gradle.kts` extension and leverage Kotlin's type-safe builders for Gradle configuration.

### 1. Core Benefits
- Strong type-safety with compile-time error checking
- Superior IDE support with reliable code completion
- Improved refactoring capabilities
- Better navigation to references and declarations
- Consistent syntax with our Kotlin-based application code
- Enhanced readability through more explicit syntax
- Improved discoverability of available properties and methods

### 2. Implementation Approach
- Use `.gradle.kts` extension for all Gradle build files
- Leverage `settings.gradle.kts` for multi-module project configuration
- Implement `buildSrc` directory for shared build logic
- Use Gradle version catalogs for dependency management
- Apply Kotlin idioms and best practices to build scripts
- Gradually migrate existing Groovy DSL scripts if applicable

### 3. Structure and Organization
- Organize build logic in buildSrc with proper package structure
- Use extension functions for common build configurations
- Extract complex build logic into separate Kotlin files
- Implement type-safe accessors for custom plugins and tasks
- Leverage Kotlin's string interpolation and multiline strings for cleaner configuration

## Implementation Approach

1. **Project Setup**
   - Configure root project's build.gradle.kts and settings.gradle.kts
   - Set up buildSrc directory with its own build.gradle.kts
   - Implement version catalogs in libs.versions.toml
   - Create shared build configurations for subprojects

2. **Migration Strategy** (if applicable)
   - Start with new modules using Kotlin DSL
   - Gradually convert existing Groovy scripts to Kotlin
   - Use the Groovy to Kotlin DSL converter tool when appropriate
   - Validate each conversion with build verification

3. **Knowledge Sharing**
   - Document common patterns and idioms
   - Provide examples of typical configurations
   - Create templates for new modules
   - Establish code review guidelines for build scripts

## Consequences

### Positive
- Enhanced IDE support with reliable code completion and navigation
- Compile-time error detection instead of runtime build failures
- Better refactoring support when changing build configuration
- More maintainable build scripts for complex projects
- Improved readability through static typing and explicit syntax
- Consistency with Kotlin application code (if using Kotlin)
- Better discoverability of APIs through IDE suggestions
- Access to Kotlin language features like extension functions and delegates
- Structured approach to organizing build logic

### Negative
- Steeper learning curve for developers not familiar with Kotlin
- More verbose syntax in some cases compared to Groovy
- Potentially slower script compilation, especially for initial builds
- Less flexibility than Groovy's dynamic nature
- Some third-party plugins may have less documentation for Kotlin DSL
- Migration effort required for existing Groovy DSL scripts
- Syntax differences between Groovy and Kotlin DSL may cause confusion

## Alternatives Considered

1. **Groovy DSL**
   - More concise syntax in some cases
   - Traditional approach with more examples available
   - Dynamic typing allows for more flexibility
   - Lower initial learning curve for Groovy-familiar developers
   - Faster script evaluation for simple builds
   - Less strict syntax requirements
   - More permissive with respect to API changes

2. **Mixed Approach**
   - Using Kotlin DSL for new modules and complex configurations
   - Keeping Groovy DSL for simpler or existing modules
   - Potentially confusing with two different syntaxes
   - Inconsistent developer experience across the project
   - Difficulty in sharing build logic between different DSL types

3. **Maven**
   - XML-based configuration instead of a programming language
   - More declarative approach
   - Less flexibility for custom build logic
   - Would require complete build system replacement

## Implementation Notes

### Root Project Build Script (build.gradle.kts)

```kotlin
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    // Apply the Java plugin to add support for Java
    java
    
    // Apply the Kotlin JVM plugin to add support for Kotlin
    kotlin("jvm") version libs.versions.kotlin.get()
    
    // Apply the Spring Boot plugin
    id("org.springframework.boot") version libs.versions.springBoot.get() apply false
    id("io.spring.dependency-management") version libs.versions.springDependencyManagement.get() apply false
}

allprojects {
    group = "com.example"
    version = "0.0.1-SNAPSHOT"
    
    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "java")
    apply(plugin = "kotlin")
    apply(plugin = "io.spring.dependency-management")
    
    java {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
    }
    
    tasks.withType<KotlinCompile> {
        kotlinOptions {
            freeCompilerArgs = listOf("-Xjsr305=strict")
            jvmTarget = "21"
        }
    }
    
    tasks.withType<Test> {
        useJUnitPlatform()
    }
    
    dependencies {
        implementation(kotlin("stdlib-jdk8"))
        implementation(kotlin("reflect"))
        testImplementation(libs.junit.jupiter)
        testImplementation(libs.mockk)
    }
}

tasks.register("clean") {
    delete(rootProject.buildDir)
}
```

### Settings File (settings.gradle.kts)

```kotlin
rootProject.name = "my-application"

// Include all subprojects
include("app")
include("domain")
include("infrastructure")
include("api")

// Configure version catalog
enableFeaturePreview("VERSION_CATALOGS")

dependencyResolutionManagement {
    versionCatalogs {
        create("libs") {
            from(files("gradle/libs.versions.toml"))
        }
    }
}
```

### Version Catalog (gradle/libs.versions.toml)

```toml
[versions]
kotlin = "1.7.10"
springBoot = "2.7.0"
springDependencyManagement = "1.0.11.RELEASE"
junit = "5.8.2"
mockk = "1.12.4"
jackson = "2.13.3"

[libraries]
# Spring dependencies
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web" }
spring-boot-starter-data-jpa = { module = "org.springframework.boot:spring-boot-starter-data-jpa" }
spring-boot-starter-validation = { module = "org.springframework.boot:spring-boot-starter-validation" }
spring-boot-starter-security = { module = "org.springframework.boot:spring-boot-starter-security" }
spring-boot-starter-test = { module = "org.springframework.boot:spring-boot-starter-test" }

# Database
postgresql = { module = "org.postgresql:postgresql", version = "42.3.6" }
flyway-core = { module = "org.flywaydb:flyway-core", version = "8.5.13" }

# Testing
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }
mockk = { module = "io.mockk:mockk", version.ref = "mockk" }

# JSON
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }
jackson-kotlin = { module = "com.fasterxml.jackson.module:jackson-module-kotlin", version.ref = "jackson" }

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
kotlin-spring = { id = "org.jetbrains.kotlin.plugin.spring", version.ref = "kotlin" }
kotlin-jpa = { id = "org.jetbrains.kotlin.plugin.jpa", version.ref = "kotlin" }
spring-boot = { id = "org.springframework.boot", version.ref = "springBoot" }
spring-dependency-management = { id = "io.spring.dependency-management", version.ref = "springDependencyManagement" }
```

### BuildSrc for Custom Build Logic

```kotlin
// buildSrc/build.gradle.kts
plugins {
    `kotlin-dsl`
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-gradle-plugin:1.7.10")
}
```

```kotlin
// buildSrc/src/main/kotlin/com/example/build/SpringBootConventions.kt
package com.example.build

import org.gradle.api.Project
import org.gradle.kotlin.dsl.dependencies

/**
 * Applies Spring Boot conventions to a project
 */
fun Project.applySpringBootConventions() {
    plugins.apply("org.springframework.boot")
    plugins.apply("io.spring.dependency-management")
    plugins.apply("org.jetbrains.kotlin.plugin.spring")
    
    dependencies {
        "implementation"("org.springframework.boot:spring-boot-starter")
        "testImplementation"("org.springframework.boot:spring-boot-starter-test")
    }
}

/**
 * Applies Spring Boot Web conventions to a project
 */
fun Project.applySpringBootWebConventions() {
    applySpringBootConventions()
    
    dependencies {
        "implementation"("org.springframework.boot:spring-boot-starter-web")
        "implementation"("org.springframework.boot:spring-boot-starter-validation")
    }
}
```

### Application Module Build Script

```kotlin
// app/build.gradle.kts
import com.example.build.applySpringBootWebConventions

plugins {
    kotlin("jvm")
    kotlin("plugin.spring")
}

applySpringBootWebConventions()

dependencies {
    implementation(project(":domain"))
    implementation(project(":infrastructure"))
    implementation(project(":api"))
    
    implementation(libs.spring.boot.starter.web)
    implementation(libs.spring.boot.starter.data.jpa)
    implementation(libs.postgresql)
    implementation(libs.flyway.core)
    
    testImplementation(libs.spring.boot.starter.test)
    testImplementation(libs.junit.jupiter)
    testImplementation(libs.mockk)
}

// Configure the main class for the application
springBoot {
    mainClass.set("com.example.application.ApplicationKt")
}
```

### Custom Task Example

```kotlin
// Define a custom task type
abstract class GenerateVersionFileTask : DefaultTask() {
    @get:InputFile
    abstract val propertiesFile: RegularFileProperty
    
    @get:OutputFile
    abstract val outputFile: RegularFileProperty
    
    @TaskAction
    fun generate() {
        val properties = Properties()
        propertiesFile.get().asFile.inputStream().use { properties.load(it) }
        
        val version = properties.getProperty("version", "unknown")
        val buildTime = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ").format(Date())
        
        outputFile.get().asFile.writeText("""
            {
              "version": "$version",
              "buildTime": "$buildTime"
            }
        """.trimIndent())
    }
}

// Register an instance of the custom task
val generateVersionFile by tasks.registering(GenerateVersionFileTask::class) {
    propertiesFile.set(file("version.properties"))
    outputFile.set(file("${buildDir}/resources/main/version.json"))
}

// Make the processResources task depend on our custom task
tasks.processResources {
    dependsOn(generateVersionFile)
}
```

## Compliance Verification
- Ensure all build scripts compile successfully
- Verify IDE support with code completion and navigation
- Test build script performance, especially for clean builds
- Confirm compatibility with all required Gradle plugins
- Validate build script readability through peer review
- Check that common build tasks work as expected
- Verify integration with CI/CD pipeline

## References
- Gradle Kotlin DSL Primer: https://docs.gradle.org/current/userguide/kotlin_dsl.html
- Migrating Groovy to Kotlin DSL: https://guides.gradle.org/migrating-build-logic-from-groovy-to-kotlin/
- Gradle Version Catalog: https://docs.gradle.org/current/userguide/platforms.html
- Gradle buildSrc: https://docs.gradle.org/current/userguide/organizing_gradle_projects.html#sec:build_sources
- Kotlin DSL API Reference: https://gradle.github.io/kotlin-dsl-docs/api/
- Type-safe Project Accessors: https://docs.gradle.org/current/userguide/declaring_dependencies.html#sec:type-safe-project-accessors
- Gradle Kotlin DSL Samples: https://github.com/gradle/kotlin-dsl-samples
