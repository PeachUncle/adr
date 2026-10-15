# ADR-005: Alerting Metrics and Thresholds

## Date:
2024-04-03

## Status:
Accepted

## Context:
The context for this decision is to define the alerting metrics and thresholds for the Fishy Watch system. We need to determine the criteria for triggering alerts based on various parameters such as water quality, fish health, environmental conditions, and system anomalies.

## Decision:
After analyzing the requirements and considerations, we have defined the following alerting metrics and thresholds for Fishy Watch:

### Alerting Metrics:
1. **Water Quality Metrics**:
   - pH Level: Thresholds for acceptable pH levels in water.
   - Temperature: Thresholds for water temperature variations.
   - Salinity: Thresholds for salinity levels in water.
   - Oxygen Levels: Thresholds for oxygen levels critical to fish health.

2. **Fish Health Metrics**:
   - Parasite Detection: Alert when parasites are detected on fish.
   - Abnormal Behavior: Alert when fish exhibit abnormal behavior patterns.
   - Health Status: Alert when fish health parameters deviate from normal ranges.

3. **Environmental Conditions**:
   - Weather Events: Alerts for adverse weather conditions affecting fish farms.
   - Natural Disasters: Alerts for potential natural disasters impacting fish farms.

4. **System Anomalies**:
   - Data Outages: Alert when data acquisition systems experience outages.
   - Connectivity Issues: Alert when hardware-to-software communication is disrupted.
   - Performance Degradation: Alert when system performance falls below acceptable levels.

### Thresholds:
1. **Static Thresholds**:
   - Define static threshold values for water quality metrics, fish health parameters, and environmental conditions based on industry standards and best practices.
   - Example: pH level above 7.5 triggers an alert, oxygen levels below 5 ppm trigger an alert.

2. **Dynamic Thresholds**:
   - Implement dynamic thresholding based on historical data, machine learning models, or adaptive algorithms to adjust alerting thresholds dynamically.
   - Example: Use machine learning models to predict optimal pH ranges for specific fish species and adjust thresholds accordingly.

3. **User-Defined Thresholds**:
   - Allow users to set custom thresholds based on their specific farm requirements, fish species, and environmental factors.
   - Example: Farmers can set personalized thresholds for water temperature or parasite detection based on their expertise and farm conditions.

## Consequences:
### Pros:
- Early Detection: Defined alerting metrics and thresholds enable early detection of potential issues affecting fish health, water quality, and farm operations.
- Customization: User-defined thresholds and dynamic thresholding provide flexibility and adaptability to varying farm conditions and user preferences.
- Preventive Maintenance: Alerts help in proactive management and preventive maintenance, reducing risks and improving overall farm productivity.
- Decision Support: Alerting system assists farmers in making informed decisions and taking timely actions to mitigate risks and optimize farm performance.

### Cons:
- False Positives: Improperly set thresholds or noisy data may lead to false alerts, requiring fine-tuning and validation of alerting criteria.
- Complexity: Managing multiple alerting metrics, thresholds, and alert types adds complexity to system design and maintenance.
