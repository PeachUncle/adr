# ADR-001: Choice of Tribuo for Machine Learning

## Status
Accepted

## Context
The XAI-Forge application requires a robust machine learning library for Java that can handle both classification and regression tasks, provide model serialization capabilities, and support explainable AI features. The application needs to train models, make predictions, and generate explanations for user transparency.

## Decision
We will use **Tribuo** (Oracle Labs) as the primary machine learning library for the XAI-Forge application.

## Consequences

### Positive Consequences
- **Enterprise-grade library**: Tribuo is developed by Oracle Labs and is production-ready
- **Comprehensive ML support**: Supports both classification and regression algorithms
- **Model serialization**: Built-in support for model persistence and loading
- **Explainable AI**: Native support for LIME and other explanation techniques
- **Performance**: Optimized for Java applications with good memory management
- **Active development**: Regular updates and community support
- **Integration**: Works well with Spring Boot and JPA
- **Documentation**: Comprehensive documentation and examples

### Negative Consequences
- **Learning curve**: Tribuo has a steeper learning curve compared to simpler libraries
- **Dependency size**: Adds significant size to the application JAR
- **Limited algorithms**: Fewer algorithm options compared to Python libraries
- **Community**: Smaller community compared to scikit-learn or TensorFlow

### Risks
- **Vendor lock-in**: Dependency on Oracle's continued support
- **Performance**: May not be as optimized as specialized ML libraries
- **Updates**: Breaking changes in major version updates

## Alternatives Considered

### 1. Weka
- **Pros**: Mature library, extensive algorithm support, good documentation
- **Cons**: Older API design, less active development, performance issues
- **Decision**: Rejected due to outdated architecture and performance concerns

### 2. DL4J (Deeplearning4j)
- **Pros**: Deep learning capabilities, good performance
- **Cons**: Overkill for traditional ML tasks, complex setup, large dependency
- **Decision**: Rejected as too complex for the application's needs

### 3. Custom Implementation
- **Pros**: Full control, minimal dependencies
- **Cons**: Significant development time, maintenance burden, potential bugs
- **Decision**: Rejected due to development complexity and time constraints

### 4. Python ML Services
- **Pros**: Access to scikit-learn, TensorFlow, PyTorch
- **Cons**: Additional service complexity, network latency, deployment complexity
- **Decision**: Rejected to keep the application monolithic and simple

## Implementation Notes
- Tribuo 4.3.1 is used as the specific version
- Models are serialized using Java's ObjectOutputStream
- LIME explanations are implemented using Tribuo's built-in explainability features
- Thread pools are configured for concurrent model training

## References
- [Tribuo Documentation](https://tribuo.org/)
- [Tribuo GitHub Repository](https://github.com/oracle/tribuo)
- [Machine Learning with Tribuo](https://tribuo.org/learn/4.3/tutorials/)
