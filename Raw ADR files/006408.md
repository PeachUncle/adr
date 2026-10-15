# ADR-029: GDPR Compliance Strategy

## Status
Proposed

## Date
2025-03-15

## Context
The Aronim Bookstore is expanding its operations to serve customers in the European Union, which requires compliance with the General Data Protection Regulation (GDPR). We need to implement a comprehensive GDPR compliance strategy that addresses:

- Lawful processing of personal data
- User rights management (access, rectification, erasure, etc.)
- Data protection by design and default
- Data breach notification procedures
- Data protection impact assessments
- Record keeping of processing activities
- Cross-border data transfer considerations
- Consent management
- Privacy policy and terms of service updates

Non-compliance with GDPR could result in significant financial penalties (up to 4% of global annual revenue or €20 million, whichever is higher), damage to reputation, and loss of customer trust. Additionally, the compliance approach must integrate with our existing architecture and technology decisions.

## Decision
We will implement a comprehensive GDPR compliance strategy with the following components:

### 1. Data Mapping and Management
- Create a complete data inventory documenting all personal data processed
- Implement data classification system (personal data, sensitive data, etc.)
- Establish data flow diagrams showing how data moves through our systems
- Define data retention periods and automated deletion processes
- Implement data minimization practices across all systems

### 2. Technical Implementation
- Create a centralized "Privacy Module" within our Modulith architecture
- Implement user consent management system with granular consent options
- Develop automated tools for handling data subject requests
- Implement pseudonymization and encryption for personal data
- Create audit logging for all data access and modifications
- Implement data portability exports in machine-readable formats

### 3. Organizational Measures
- Appoint a Data Protection Officer (DPO)
- Establish a privacy governance committee
- Create incident response procedures for data breaches
- Develop employee training program on GDPR and data protection
- Implement privacy impact assessment process for new features
- Create vendor assessment process for third-party data processors

### 4. User Interface and Experience
- Design transparent privacy notices at data collection points
- Implement user-friendly consent management interface
- Create self-service portal for data subject rights
- Develop clear communication for privacy policy updates
- Implement age verification for youth users where required

## Implementation Approach

1. **Foundation and Governance**
   - Appoint DPO and establish privacy governance structure
   - Conduct comprehensive data mapping exercise
   - Develop and document privacy policies and procedures
   - Create employee training materials and schedule

2. **Technical Infrastructure**
   - Design and implement Privacy Module within the Modulith architecture
   - Create data subject request handling system
   - Implement consent management database and API
   - Develop audit logging and monitoring capabilities
   - Implement encryption and pseudonymization measures

3. **User-Facing Components**
   - Design and implement consent management UI
   - Create self-service privacy portal for users
   - Update account management interfaces for GDPR compliance
   - Implement privacy-focused onboarding flows

4. **Validation and Compliance Verification**
   - Conduct internal privacy audit
   - Perform data protection impact assessments
   - Test data subject request handling processes
   - Validate security measures for personal data
   - Review and update third-party processor agreements

## Privacy Module Architecture

```
/privacy-module
  /api
    ConsentController.java
    DataSubjectRequestController.java
    PrivacySettingsController.java
  /service
    ConsentService.java
    DataSubjectRequestService.java
    DataRetentionService.java
    PrivacySettingsService.java
    DataExportService.java
  /repository
    ConsentRepository.java
    DataSubjectRequestRepository.java
    PrivacySettingsRepository.java
  /domain
    Consent.java
    ConsentPurpose.java
    DataSubjectRequest.java
    DataSubjectRequestType.java
    PrivacySettings.java
  /events
    ConsentChangedEvent.java
    DataSubjectRequestCreatedEvent.java
    DataSubjectRequestCompletedEvent.java
  /scheduled
    DataRetentionJob.java
    StaleRequestCleanupJob.java
```

## Consequences

### Positive
- Ensures legal compliance with GDPR, reducing regulatory risk
- Enhances user trust through transparent data practices
- Improves data security and governance across the organization
- Creates a structured approach to managing personal data
- Provides competitive advantage in privacy-conscious markets
- Establishes foundation for compliance with other privacy regulations
- Improves data quality through better management practices
- Reduces risk of data breaches through enhanced security measures

### Negative
- Increases development complexity and maintenance overhead
- Requires significant resources for implementation and ongoing compliance
- May impact some personalization features and marketing capabilities
- Could create performance overhead for certain operations
- Necessitates ongoing monitoring and updates as regulations evolve
- May require changes to existing data processing workflows
- Adds complexity to user onboarding and registration processes
- Creates additional operational procedures for staff

## Alternatives Considered

1. **Minimal Compliance Approach**
   - Implement only the bare minimum requirements for GDPR compliance
   - Lower initial implementation cost and complexity
   - Higher risk of non-compliance and potential penalties
   - Would not provide the trust benefits of a comprehensive approach
   - Rejected due to long-term risks and misalignment with company values

2. **Third-Party Compliance Solution**
   - Use off-the-shelf GDPR compliance tools and services
   - Faster implementation timeline
   - Less control over implementation details
   - Potential integration challenges with existing systems
   - Higher ongoing costs for subscription services
   - Rejected due to integration complexity and loss of control

3. **Separate Privacy Microservice**
   - Implement privacy features as a standalone microservice
   - Clear separation of concerns
   - Additional complexity in cross-service communication
   - Potential performance impact for frequent privacy-related operations
   - Rejected in favor of Privacy Module within Modulith architecture for better integration

4. **Regional Restriction Approach**
   - Block EU users entirely to avoid GDPR requirements
   - Simplest immediate solution
   - Severely limits business growth potential
   - Rejected as contrary to business expansion goals

## Implementation Examples

### Consent Management API

```java
// ConsentController.java
@RestController
@RequestMapping("/api/v1/privacy/consent")
public class ConsentController {

    private final ConsentService consentService;
    
    @Autowired
    public ConsentController(ConsentService consentService) {
        this.consentService = consentService;
    }
    
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<ConsentDTO>> getUserConsents(@PathVariable String userId) {
        return ResponseEntity.ok(consentService.getUserConsents(userId));
    }
    
    @PostMapping("/user/{userId}")
    public ResponseEntity<ConsentDTO> updateConsent(
            @PathVariable String userId,
            @Valid @RequestBody ConsentUpdateRequest request) {
        return ResponseEntity.ok(consentService.updateConsent(userId, request));
    }
    
    @GetMapping("/purposes")
    public ResponseEntity<List<ConsentPurposeDTO>> getConsentPurposes() {
        return ResponseEntity.ok(consentService.getAvailableConsentPurposes());
    }
}
```

### Data Subject Request Service

```java
// DataSubjectRequestService.java
@Service
public class DataSubjectRequestService {

    private final DataSubjectRequestRepository requestRepository;
    private final ApplicationEventPublisher eventPublisher;
    private final UserService userService;
    
    @Autowired
    public DataSubjectRequestService(
            DataSubjectRequestRepository requestRepository,
            ApplicationEventPublisher eventPublisher,
            UserService userService) {
        this.requestRepository = requestRepository;
        this.eventPublisher = eventPublisher;
        this.userService = userService;
    }
    
    @Transactional
    public DataSubjectRequestDTO createRequest(String userId, DataSubjectRequestCreateDTO request) {
        // Validate user exists
        userService.validateUserExists(userId);
        
        // Create request
        DataSubjectRequest dataRequest = new DataSubjectRequest();
        dataRequest.setUserId(userId);
        dataRequest.setRequestType(request.getRequestType());
        dataRequest.setStatus(RequestStatus.PENDING);
        dataRequest.setCreatedAt(LocalDateTime.now());
        dataRequest.setDetails(request.getDetails());
        
        DataSubjectRequest savedRequest = requestRepository.save(dataRequest);
        
        // Publish event for async processing
        eventPublisher.publishEvent(new DataSubjectRequestCreatedEvent(savedRequest));
        
        return mapToDTO(savedRequest);
    }
    
    @Transactional(readOnly = true)
    public List<DataSubjectRequestDTO> getUserRequests(String userId) {
        return requestRepository.findByUserId(userId).stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }
    
    @Transactional
    public void processAccessRequest(String requestId) {
        DataSubjectRequest request = getRequestById(requestId);
        
        if (request.getRequestType() != RequestType.ACCESS) {
            throw new IllegalStateException("Cannot process non-access request with this method");
        }
        
        // Process access request logic
        // ...
        
        // Update request status
        request.setStatus(RequestStatus.COMPLETED);
        request.setCompletedAt(LocalDateTime.now());
        requestRepository.save(request);
        
        eventPublisher.publishEvent(new DataSubjectRequestCompletedEvent(request));
    }
    
    // Additional methods for other request types...
    
    private DataSubjectRequest getRequestById(String requestId) {
        return requestRepository.findById(requestId)
                .orElseThrow(() -> new ResourceNotFoundException("Request not found: " + requestId));
    }
    
    private DataSubjectRequestDTO mapToDTO(DataSubjectRequest request) {
        // Mapping logic
        // ...
    }
}
```

### Consent Domain Model

```java
// Consent.java
@Entity
@Table(name = "privacy_consents")
public class Consent {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;
    
    @Column(name = "user_id", nullable = false)
    private String userId;
    
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "purpose_id", nullable = false)
    private ConsentPurpose purpose;
    
    @Column(nullable = false)
    private boolean granted;
    
    @Column(name = "granted_at")
    private LocalDateTime grantedAt;
    
    @Column(name = "revoked_at")
    private LocalDateTime revokedAt;
    
    @Column(name = "ip_address")
    private String ipAddress;
    
    @Column(name = "user_agent")
    private String userAgent;
    
    // Getters, setters, etc.
}

// ConsentPurpose.java
@Entity
@Table(name = "privacy_consent_purposes")
public class ConsentPurpose {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;
    
    @Column(nullable = false, unique = true)
    private String code;
    
    @Column(nullable = false)
    private String name;
    
    @Column(length = 1000)
    private String description;
    
    @Column(name = "is_required")
    private boolean required;
    
    @Column(name = "retention_period_days")
    private Integer retentionPeriodDays;
    
    // Getters, setters, etc.
}
```

### Data Retention Job

```java
// DataRetentionJob.java
@Component
public class DataRetentionJob {

    private static final Logger logger = LoggerFactory.getLogger(DataRetentionJob.class);
    
    private final DataRetentionService retentionService;
    
    @Autowired
    public DataRetentionJob(DataRetentionService retentionService) {
        this.retentionService = retentionService;
    }
    
    @Scheduled(cron = "${privacy.data-retention.cron:0 0 2 * * ?}")
    public void executeRetentionPolicies() {
        logger.info("Starting scheduled data retention job");
        
        try {
            int deletedRecords = retentionService.applyRetentionPolicies();
            logger.info("Data retention job completed. Deleted {} records", deletedRecords);
        } catch (Exception e) {
            logger.error("Error executing data retention job", e);
        }
    }
}
```

### Privacy Settings UI Component (React)

```typescript
// PrivacySettingsPanel.tsx
import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Button, Divider, List, Switch, Text, Title } from 'react-native-paper';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { fetchPrivacySettings, updateConsent } from '../../store/slices/privacySlice';
import { ConsentPurpose, ConsentSetting } from '../../types/privacy';
import { LoadingIndicator } from '../common/LoadingIndicator';

export const PrivacySettingsPanel: React.FC = () => {
  const dispatch = useDispatch();
  const { consentPurposes, userConsents, loading, error } = useSelector(
    (state: RootState) => state.privacy
  );
  
  const [localConsents, setLocalConsents] = useState<Record<string, boolean>>({});
  const [hasChanges, setHasChanges] = useState(false);
  
  useEffect(() => {
    dispatch(fetchPrivacySettings());
  }, [dispatch]);
  
  useEffect(() => {
    if (userConsents) {
      const consentMap: Record<string, boolean> = {};
      userConsents.forEach(consent => {
        consentMap[consent.purposeCode] = consent.granted;
      });
      setLocalConsents(consentMap);
      setHasChanges(false);
    }
  }, [userConsents]);
  
  const handleToggleConsent = (purposeCode: string, required: boolean) => {
    if (required) {
      Alert.alert(
        'Required Consent',
        'This consent is required to use the application and cannot be disabled.',
        [{ text: 'OK' }]
      );
      return;
    }
    
    const newValue = !localConsents[purposeCode];
    setLocalConsents(prev => ({
      ...prev,
      [purposeCode]: newValue
    }));
    setHasChanges(true);
  };
  
  const handleSaveChanges = () => {
    Object.keys(localConsents).forEach(purposeCode => {
      const currentConsent = userConsents?.find(c => c.purposeCode === purposeCode);
      const newValue = localConsents[purposeCode];
      
      if (currentConsent?.granted !== newValue) {
        dispatch(updateConsent({
          purposeCode,
          granted: newValue
        }));
      }
    });
    
    setHasChanges(false);
  };
  
  if (loading) {
    return <LoadingIndicator />;
  }
  
  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>
          Failed to load privacy settings. Please try again later.
        </Text>
        <Button 
          mode="contained" 
          onPress={() => dispatch(fetchPrivacySettings())}
          style={styles.retryButton}
        >
          Retry
        </Button>
      </View>
    );
  }
  
  return (
    <ScrollView style={styles.container}>
      <Title style={styles.title}>Privacy Settings</Title>
      <Text style={styles.description}>
        Manage how your personal data is used within our application.
        Required consents are necessary for the application to function properly.
      </Text>
      
      <Divider style={styles.divider} />
      
      <List.Section>
        {consentPurposes.map((purpose: ConsentPurpose) => (
          <List.Item
            key={purpose.code}
            title={purpose.name}
            description={purpose.description}
            right={() => (
              <View style={styles.switchContainer}>
                {purpose.required && <Text style={styles.requiredText}>Required</Text>}
                <Switch
                  value={localConsents[purpose.code] ?? false}
                  onValueChange={() => handleToggleConsent(purpose.code, purpose.required)}
                  disabled={purpose.required}
                />
              </View>
            )}
          />
        ))}
      </List.Section>
      
      <View style={styles.buttonContainer}>
        <Button
          mode="contained"
          onPress={handleSaveChanges}
          disabled={!hasChanges}
          style={styles.saveButton}
        >
          Save Changes
        </Button>
        
        <Button
          mode="outlined"
          onPress={() => dispatch(fetchPrivacySettings())}
          style={styles.resetButton}
          disabled={!hasChanges}
        >
          Reset
        </Button>
      </View>
      
      <View style={styles.dataRequestContainer}>
        <Text style={styles.dataRequestTitle}>Data Subject Rights</Text>
        <Text style={styles.dataRequestDescription}>
          You can request access to your personal data, correction of inaccurate data,
          or deletion of your data under certain conditions.
        </Text>
        <Button
          mode="outlined"
          onPress={() => navigation.navigate('DataSubjectRequests')}
          style={styles.dataRequestButton}
        >
          Manage Data Requests
        </Button>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    marginBottom: 8,
  },
  description: {
    marginBottom: 16,
    color: '#666',
  },
  divider: {
    marginVertical: 16,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  requiredText: {
    fontSize: 12,
    color: '#666',
    marginRight: 8,
  },
  buttonContainer: {
    marginTop: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  saveButton: {
    flex: 1,
    marginRight: 8,
  },
  resetButton: {
    flex: 1,
    marginLeft: 8,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  errorText: {
    marginBottom: 16,
    textAlign: 'center',
    color: '#d32f2f',
  },
  retryButton: {
    marginTop: 16,
  },
  dataRequestContainer: {
    marginTop: 32,
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
  },
  dataRequestTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  dataRequestDescription: {
    marginBottom: 16,
    color: '#666',
  },
  dataRequestButton: {
    marginTop: 8,
  },
});
```

## Compliance Verification
- Regular privacy audits
- Data protection impact assessments for new features
- Periodic penetration testing of privacy-related systems
- Regular staff training and awareness testing
- Mock data breach exercises
- Third-party compliance certification
- User feedback on privacy controls
- Regulatory monitoring for GDPR updates

## References
- EU General Data Protection Regulation: https://gdpr-info.eu/
- European Data Protection Board Guidelines: https://edpb.europa.eu/edpb_en
- ICO GDPR Guidance: https://ico.org.uk/for-organisations/guide-to-data-protection/
- NIST Privacy Framework: https://www.nist.gov/privacy-framework
- OWASP Privacy Risks: https://owasp.org/www-project-top-10-privacy-risks/
- Spring Security Documentation: https://docs.spring.io/spring-security/reference/
- Consent Management Best Practices: https://iapp.org/resources/article/consent-guidance/
- Data Minimization Techniques: https://fpf.org/blog/data-minimization-strategies/
