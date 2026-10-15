# ADR-004: Self-Contained Single-File Distribution

**Status**: Accepted

**Date**: 2025-10-29

## Context

We need to determine the best distribution strategy for our .NET MCP server. The server needs to be easily deployable across different platforms and environments without complex setup requirements.

Key considerations:
- Minimize deployment complexity for end users
- Support multiple platforms (Windows, macOS, Linux)
- Integrate well with IDE MCP configurations
- Ensure reliable execution across different environments
- Optimize for NuGet distribution model

## Decision

We will distribute the MCP server as **self-contained, single-file executables** for each target platform, packaged and distributed via NuGet as an MCP tool package.

### Options Considered

1. **Self-Contained Single-File Executables** ✅
   - Pros: No runtime dependencies, single file deployment, fast startup, platform-specific optimization
   - Cons: Larger file size, separate builds per platform

2. **Framework-Dependent Deployment**
   - Pros: Smaller file size, shared runtime benefits
   - Cons: Requires .NET runtime installation, version compatibility issues

3. **Container-Based Distribution**
   - Pros: Consistent environment, easy CI/CD, dependency isolation
   - Cons: Container runtime required, overhead for simple MCP tools, complexity

4. **Source-Only Distribution**
   - Pros: Minimal size, always up-to-date compilation
   - Cons: Requires .NET SDK, longer startup time, build dependencies

## Decision Rationale

- **Zero Dependencies**: No .NET runtime installation required on target machines
- **IDE Integration**: Works seamlessly with VS Code and Visual Studio MCP configurations
- **NuGet Compatibility**: Aligns with Microsoft's MCP distribution model via NuGet
- **Platform Optimization**: Each executable optimized for its target platform
- **Reliability**: Eliminates runtime version conflicts and dependency issues
- **User Experience**: Simple download and execute workflow

## Consequences

### Positive
- **Zero Setup**: Users can run the MCP server immediately after download
- **Platform Optimization**: Each build optimized for specific OS/architecture
- **Reliability**: No dependency on system-installed .NET runtime
- **IDE Ready**: Compatible with dnx command pattern used by VS Code/Visual Studio
- **Offline Capable**: No network dependencies after initial download
- **Version Isolation**: Each server version completely independent

### Negative
- **File Size**: Each executable ~30-50MB instead of ~1MB for framework-dependent
- **Build Complexity**: Must build separately for each target platform
- **Storage**: NuGet package contains multiple large executables
- **Update Size**: Full download required for updates (no delta updates)

### Neutral
- **Startup Performance**: Good performance, no runtime discovery overhead
- **Memory Usage**: Reasonable for MCP server workloads
- **Security**: Self-contained reduces attack surface but increases update responsibility

## Implementation Configuration

### Project Settings
```xml
<PropertyGroup>
  <SelfContained>true</SelfContained>
  <PublishSelfContained>true</PublishSelfContained>
  <PublishSingleFile>true</PublishSingleFile>
  <RuntimeIdentifiers>win-x64;win-arm64;osx-arm64;linux-x64;linux-arm64;linux-musl-x64</RuntimeIdentifiers>
</PropertyGroup>
```

### Target Platforms
- **Windows**: win-x64, win-arm64
- **macOS**: osx-arm64 (Apple Silicon)
- **Linux**: linux-x64, linux-arm64, linux-musl-x64

### NuGet Package Structure
```
package/
├── tools/
│   ├── win-x64/
│   │   └── SampleMcpServer.exe
│   ├── osx-arm64/
│   │   └── SampleMcpServer
│   └── linux-x64/
│       └── SampleMcpServer
└── .mcp/
    └── server.json
```

## Build Process

### Multi-Platform Build
```bash
dotnet pack -c Release
# Automatically builds for all RuntimeIdentifiers
```

### Platform-Specific Build
```bash
dotnet publish -c Release -r win-x64 --self-contained
dotnet publish -c Release -r osx-arm64 --self-contained
dotnet publish -c Release -r linux-x64 --self-contained
```

## Distribution Strategy

1. **NuGet Publication**: Package contains all platform executables
2. **Platform Detection**: dnx command automatically selects correct executable
3. **Version Management**: Standard NuGet versioning and update mechanisms
4. **IDE Integration**: Compatible with `.mcp.json` configuration files

## Performance Considerations

- **Cold Start**: ~100-200ms startup time (excellent for MCP scenarios)
- **Memory**: ~20-30MB baseline memory usage
- **File Size**: ~40MB per platform executable
- **Network**: One-time download, no runtime dependencies

## Security Implications

- **Attack Surface**: Reduced (no external runtime dependencies)
- **Updates**: Responsibility to update entire executable for security patches
- **Isolation**: Each server instance completely isolated
- **Trust**: Users execute pre-compiled binaries (standard for distributed tools)

## Future Considerations

If distribution size becomes problematic:
- Consider trimming features to reduce executable size
- Evaluate framework-dependent option for specific scenarios
- Implement delta update mechanisms for large deployments

## Related ADRs

- [ADR-001: Use .NET 9.0 for MCP Server Implementation](001-dotnet-9-mcp-server.md)
- [ADR-002: Choose stdio Transport for MCP Communication](002-stdio-transport.md)
- [ADR-003: Use Attribute-Based Tool Discovery](003-attribute-based-tools.md)

## References

- [.NET Self-Contained Deployment](https://docs.microsoft.com/en-us/dotnet/core/deploying/single-file)
- [NuGet MCP Guide](https://aka.ms/nuget/mcp/guide)
- [.NET Runtime Identifiers](https://docs.microsoft.com/en-us/dotnet/core/rid-catalog)