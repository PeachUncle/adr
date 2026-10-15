# ADR: 004 - Excel File Handling for ProjectOneMil

## Context
The `ProjectOneMil` project requires the ability to read from and write to Excel files for data import and export functionalities. The team needs to decide on the library to be used for handling Excel files.

## Decision
We have decided to use the EPPlus library for handling Excel files in the `ProjectOneMil` project.

## Alternatives Considered
1. **NPOI**:
   - Pros:
     - Supports both .xls and .xlsx formats.
     - Open-source and widely used.
   - Cons:
     - More complex API compared to EPPlus.
     - Less documentation and community support.

2. **ClosedXML**:
   - Pros:
     - Simple and intuitive API.
     - Good documentation and community support.
   - Cons:
     - Primarily focused on .xlsx format.
     - Less performant for large datasets.

## Rationale
EPPlus was chosen for the following reasons:
- **Feature-Rich**: Provides comprehensive features for reading, writing, and manipulating Excel files.
- **Performance**: Efficiently handles large datasets, making it suitable for data-intensive operations.
- **Documentation**: Well-documented with a strong community, making it easier to find support and examples.
- **Compatibility**: Supports .xlsx format, which is widely used and compatible with modern Excel versions.

## Consequences
- **Positive**:
  - Simplified handling of Excel files with a rich set of features.
  - Efficient performance for large datasets.
  - Strong community support and documentation.
- **Negative**:
  - Licensing considerations for commercial use (EPPlus is licensed under Polyform Noncommercial).

## Implementation
The following steps will be taken to implement EPPlus in the `ProjectOneMil` project:
1. **Install EPPlus**: Add the EPPlus package to the project via NuGet.
2. **Read Excel Files**: Implement functionality to read data from Excel files using EPPlus.
3. **Write Excel Files**: Implement functionality to write data to Excel files using EPPlus.
4. **Handle Large Datasets**: Optimize reading and writing operations for large datasets to ensure performance.

## References
- [EPPlus Documentation](https://epplussoftware.com/docs)
- [EPPlus GitHub Repository](https://github.com/EPPlusSoftware/EPPlus)
- [NuGet Package](https://www.nuget.org/packages/EPPlus)
