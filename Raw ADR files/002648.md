## Architecture Decision Record (ADR): Incorporating WASM Extensions in MidasFlow

### 1. Title

Support for Custom WASM Extensions in MidasFlow for Advanced Data Transformations and UDFs.

### 2. Status

Proposed

### 3. Context

To ensure MidasFlow's adaptability and future-proofing, there's a need to allow users to create more sophisticated data transformations and user-defined functions (UDFs) beyond what's feasible with plain SQL commands. WebAssembly (WASM) offers a promising solution for this, allowing extensibility without compromising performance.

### 4. Decision

#### 4.1. Transformation Using WASM

- **Goal**: To facilitate intricate transformations, such as calling external endpoints or altering table fields.

- **Implementation**:

- A WASM extension will be designed, providing a template and a straightforward interface.

- This interface would resemble a function that takes a record from an existing table and outputs a DataFrame.

- The record structure will be deduced from the input file (potentially containing column names) and a configuration file specifying the table name and necessary projections.

- Post transformation, the enriched record will be returned as a DataFrame, aiding in the generation of a new table.

- **Command-Line Tool**:

- To streamline the process, a command-line tool will be developed.

- This tool will generate the template WASM project and necessary structures for processing records.

- Users will primarily focus on completing specific transformation logic within this template.

#### 4.2. UDF (User-Defined Function) Integration

- **Goal**: To overcome the limitations of solely relying on SQL for data modification.

- **Implementation**:

- Enable the creation of new functions via WASM.

- These functions can be loaded into SQL commands, enriching the capabilities to modify records.

- **Storage & Configuration**:

- All custom WASM extensions (both transformations and UDFs) will reside in the application's folder containing MidasFlow's initial configurations.

- These extensions can be linked in the configuration file, ensuring seamless integration at runtime.

### 5. Consequences

- **Advantages**:

- Enhanced customizability and extensibility for users.

- Overcomes SQL's inherent limitations for certain data operations.

- Maintains high performance due to the efficient nature of WASM.

- **Challenges**:

- Requires rigorous testing to ensure user-generated WASM modules don't introduce vulnerabilities or instability.

- Users must be familiar with the WASM paradigm to make full use of this feature.
