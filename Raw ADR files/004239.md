# ADR 001: Modernizing ParticleLib with .NET 8 Features

## Status

Proposed

## Date

2025-04-12

## Context

ParticleLib is a proof of concept project originally created with .NET Framework 4.7.1 that implements a static octree with Morton codes for efficient O(1) sector lookups. The project demonstrates several advanced concepts including:

1. Spatial indexing using Morton codes (Z-order curves)
2. Parallel processing for particle simulation
3. Particle reflow across octree boundaries
4. Unsafe C# code for performance optimization
5. Dynamic spatial partitioning

With .NET 8 now available, we have an opportunity to modernize the codebase while potentially improving performance through modern language features and runtime optimizations.

## Decision

We will create a new prototype of ParticleLib using .NET 8 and modern C# features while maintaining or improving the performance characteristics of the original implementation. The new prototype will include a comprehensive test suite to validate and benchmark performance.

## Technical Details

### Language and Runtime Upgrades

1. **Target Framework**: Upgrade from .NET Framework 4.7.1 to .NET 8
2. **C# Language Version**: Upgrade to C# 12 to leverage modern language features

### Modern Language Features to Adopt

1. **Span<T> and Memory<T>**
   - Replace unsafe pointer code with safe, high-performance Span<T> and Memory<T>
   - Use System.Buffers for efficient memory pooling and reduced GC pressure

2. **SIMD Operations**
   - Utilize System.Numerics.Vector for SIMD-accelerated vector operations
   - Apply to Point3D operations and force calculations

3. **Records and Init-only Properties**
   - Use records for immutable data structures like Point3D
   - Apply init-only properties for improved safety

4. **Pattern Matching and Switch Expressions**
   - Replace lengthy switch statements with concise switch expressions
   - Use pattern matching for more expressive code in octree traversal

5. **Nullable Reference Types**
   - Enable nullable reference types for improved type safety
   - Eliminate potential null reference exceptions

6. **Improved Concurrency Models**
   - Replace Task-based parallelism with Parallel.ForEachAsync where appropriate
   - Utilize System.Threading.Channels for producer-consumer scenarios

7. **Generic Math**
   - Leverage .NET 8's generic math capabilities for more flexible numeric operations
   - Create generic implementations of vector operations

### Performance Optimizations

1. **Morton Code Calculation**
   - Optimize Morton code calculations using BitOperations.TrailingZeroCount and other bit manipulation intrinsics
   - Implement lookup tables for common operations

2. **Memory Management**
   - Replace GCHandle and unsafe pointers with ArrayPool<T> and ObjectPool<T>
   - Reduce GC pressure through efficient object reuse

3. **Struct Layout Optimization**
   - Apply StructLayout attributes for optimal memory alignment
   - Use readonly structs for improved performance

4. **AOT Compilation**
   - Utilize Native AOT compilation for reduced startup time and memory footprint
   - Apply trimming to reduce application size

5. **Hardware Intrinsics**
   - Leverage hardware-specific intrinsics for operations like vector math
   - Implement fallbacks for platforms without specific instruction sets

### Testing Framework

1. **Benchmarking Suite**
   - Implement BenchmarkDotNet for precise performance measurements
   - Create benchmarks for key operations (adding particles, traversing the octree, etc.)

2. **Performance Tests**
   - Test particle processing throughput (particles/second)
   - Measure memory usage and GC pressure
   - Compare lookup times against the original implementation

3. **Scalability Tests**
   - Test with varying numbers of particles (10^3, 10^6, 10^9)
   - Measure performance across different core counts
   - Evaluate memory efficiency with large datasets

4. **Correctness Tests**
   - Validate that the new implementation produces identical results to the original
   - Test edge cases like boundary conditions and particle reflow

## Test Scenarios

1. **Octree Construction Performance**
   - Measure time to build octrees of various sizes and depths
   - Compare memory usage between implementations

2. **Particle Processing Throughput**
   - Benchmark particles processed per second
   - Measure scaling with additional cores

3. **Lookup Performance**
   - Time to find a specific sector using Morton codes
   - Compare against traditional octree traversal

4. **Particle Reflow Efficiency**
   - Measure performance when particles move across boundaries
   - Test with different densities of particles

5. **Parallel Processing Scalability**
   - Test with 1, 2, 4, 8, 16, 32 cores
   - Measure efficiency and overhead

## Consequences

### Positive

1. Improved code readability and maintainability through modern language features
2. Potential performance improvements from .NET 8 runtime optimizations
3. Better type safety and reduced risk of memory-related bugs
4. Comprehensive performance metrics to guide future optimizations
5. Elimination of unsafe code while maintaining performance

### Negative

1. Initial development effort to rewrite and modernize the codebase
2. Risk of introducing new bugs during modernization
3. Potential learning curve for developers unfamiliar with modern C# features
4. Need to maintain compatibility with existing code that may depend on the library

### Neutral

1. Different debugging experience with modern language features
2. Changed memory allocation patterns may affect performance characteristics

## Alternatives Considered

1. **Incremental Modernization**
   - Gradually update the existing codebase rather than creating a new prototype
   - Rejected because a clean implementation allows for more fundamental architectural improvements

2. **C++/CUDA Implementation**
   - Rewrite in C++ with CUDA for GPU acceleration
   - Rejected due to increased complexity and reduced portability

3. **Maintain Status Quo**
   - Continue with the existing implementation
   - Rejected because we would miss opportunities for improvement

## Decision Outcome

Create a new prototype of ParticleLib using .NET 8 and modern C# features, with a comprehensive test suite to validate performance against the original implementation.
