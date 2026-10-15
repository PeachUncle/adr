# OSDOP-237: Case events data model

* Status: APPROVED
* Approved by: Dan Ashworth, Chris Tasker, Danny Betts

## Context and problem statement

We need a way to store (up to) the following information:

- Event type
- Event date
- Added by
- Nomination version
- Comment
- Files uploaded

The scope of this document will be to determine the data model for case events within WIOS, as well as deciding upon the
most suitable implementation pattern.

## Case events data model

### Option 1: Relational mapping

| CASE_EVENTS                  | CASE_EVENT_FILES   |
|------------------------------|--------------------|
| id: INT                      | id: INT            |
| type: TEXT                   | case_event_id: INT |
| nomination_id: INT           | file_id: INT       |
| nomination_version: INT      |                    |
| created_by: INT              |                    |
| created_timestamp: TIMESTAMP |                    |
| comment: TEXT                |                    |

Note: The `type` column will map to an enum representing the case event type.

This information would be created at the time of the event and stored using a method similar to:

```java
@Service
class CaseEventService {
  
  private UserDetailService userDetailService;
  private CaseEventRepository caseEventRepository;
  
  ...
  
  @Transactional
  public void createNominationSubmissionCaseEvent(NominationDetail nominationDetail, CaseEventComment comment) {
    var caseEvent = new CaseEvent();
    caseEvent.setNomination(nominationDetail.getNomination());
    caseEvent.setNominationVersion(nominationDetail.getVersion());
    caseEvent.setType(CaseEventType.NOMINATION_SUBMISSION);
    caseEvent.setCreatedBy(userDetailService.getUserDetail().wuaId());
    caseEvent.setCreatedInstant(Instant.now());
    caseEvent.setComment(comment.text());
    caseEventRepository.save(caseEvent);
  }
  
}
```

#### Positives

- Familiar structure to existing tables
- Referential integrity is kept for the nomination_detail_id
- JPA repository queries can be used to pull all case events for a nomination regardless of version
- We know the exact structure of each entry

#### Negatives

- New column needed if a case event is for something other than a nomination
    - Requires migration to add new column
    - Requires check constraint to ensure only one ID is set
    - Entity update
- Separate table for linking files resulting in an extra database call to fetch all downloading files

### Option 2: JSON store

| CASE_EVENTS |
|-------------|
| id: INT     |
| data: JSON  |

#### data JSON format example:

```json
{
  "eventType": String,
  "createdBy": ServiceUserDetailId,
  "createdDateTime": LocalDateTime,
  "comment": String,
  "nominationId": NominationId,
  "nominationVersion": Integer,
  "files": [
    {
      "fileId": Integer,
      "fileName": String
    }
  ]
}
```

#### Positives

- PostgreSQL JSON fields can be indexed
- Extensible for potential future case event data and formats (if any)
    - Easily modified to support different case event types that would require different data
    - If not relevant to nominationDetailId then no need to include in stored json
- Entity update wouldn't be required if new fields are added

#### Negatives

- Unable to enforce nominationDetailId references constraint
- Can be used in joins however syntax is different so may require brief upskilling if joins are expected in the future.
- Would potentially require flattening for data warehousing if querying were required
    - Could resolve with a view over the data
    - Syntax isn't too different: `SELECT ce->>"createdBy" FROM case_events ce`
- We wouldn't know if the JSON structure was correct
- Patches would be harder to do if required

## Decision

Option 1, relational mapping, appears to be the best solution due to the following reasons:

1. Use of JSON columns would be inconsistent with the rest of the application
2. There are no best practices currently defined within Digital for using JSON and so option 2 would be a riskier
   approach
3. There's no immediate requirement for extensibility other than visual prompt modifications
4. JPA queries would prevent the need for database integration testing for this functionality