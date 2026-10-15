# Architecture Decision Record (ADR)

**Title:** Anomaly Detection Algorithm Selection for IoT Devices Data

**Date:** [06/03/2024]

**Status:** Accepted

**Context:**

The Metrics Capturing System involves processing and analyzing data from a wide array of IoT medical devices. Given the nature of IoT data, which often includes large volumes of data from various sensors, it's crucial to implement an effective anomaly detection mechanism. This mechanism should be capable of identifying unusual patterns or behaviors that deviate significantly from the norm, which could indicate potential issues or significant events.

**Decision:**

After evaluating several anomaly detection algorithms, the following algorithms were identified as suitable for our IoT devices data:

1. **Isolation Forest**: For its effectiveness in high-dimensional datasets, which are common in IoT data.
2. **Local Outlier Factor (LOF)**: For detecting local anomalies, which might be more relevant in certain IoT applications.
3. **One-Class SVM**: For scenarios where the majority of data is normal, and only a small fraction is anomalous.
4. **Autoencoders**: For capturing complex patterns in the data, offering a powerful method for anomaly detection.
5. **DBSCAN**: For detecting clusters of anomalies in IoT data.

**Rationale:**

- **Isolation Forest** and **DBSCAN** are particularly effective for high-dimensional data, which is common in IoT scenarios.
- **Local Outlier Factor (LOF)** is useful for detecting local anomalies, which might be more relevant in certain applications.
- **One-Class SVM** is suitable for scenarios where the majority of data is normal, and only a small fraction is anomalous.
- **Autoencoders** offer a powerful method for anomaly detection, capable of capturing complex patterns in the data.
- **DBSCAN** is effective for detecting clusters of anomalies, which can be particularly useful in IoT data analysis.

**Consequences:**

- **Pros:** The selected algorithms are capable of handling the complexities and variability of IoT data, offering robust solutions for anomaly detection.
- **Cons:** The choice of algorithm depends on the specific characteristics of the IoT data and the types of anomalies to be detected. Experimentation and tuning of parameters may be required to achieve optimal results.

**Decision Maker:** [Rami Chalhoub]

**Decision Approver:** [Kishore Allwynraj]

**Implementation Plan:**

1. **Initial Selection:** Based on the above analysis, the team will initially focus on implementing **Isolation Forest** and **DBSCAN** for their effectiveness in handling high-dimensional data and detecting clusters of anomalies.
2. **Experimentation:** The team will experiment with these algorithms on a subset of the IoT data to evaluate their performance and suitability for the project's specific requirements.
3. **Parameter Tuning:** Based on the results of the initial experimentation, the team will fine-tune the parameters of the selected algorithms to optimize their performance.
4. **Integration:** Once the optimal configuration is identified, the selected anomaly detection algorithms will be integrated into the data processing pipeline for IoT devices data.

**Review Date:** [06/03/2024]
