# Decision: Soft Delete for Enrollments

## Context
When implementing the enrollment system in Phase 1.4, we needed to decide how to handle student unenrollment from course sections.

## Decision
We chose to implement **soft delete** (setting `is_active = False`) rather than hard delete (removing the record).

## Rationale

### 1. Preserve Historical Data
- Maintains record of who was enrolled and when
- Allows for enrollment analytics and reporting
- Supports audit trails for academic records

### 2. Support Re-enrollment
- Students can be re-enrolled without losing history
- Original enrollment date preserved
- Simpler logic for handling students dropping and re-adding courses

### 3. Future Features
- Can show enrollment history to teachers/admins
- Support for enrollment reports
- Track patterns (students who drop/re-enroll frequently)
- Academic transcript generation

### 4. Data Integrity
- Sessions reference enrollments
- Soft delete prevents orphaned references
- Maintains relational integrity

## Implementation

### Database Schema
```python
class SectionEnrollmentDB(Base):
    __tablename__ = "section_enrollments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    section_id = Column(String, ForeignKey("course_sections.id"))
    student_id = Column(String, nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Soft delete flag
    role = Column(String, default="student")
```

### Service Method
```python
def unenroll_student(self, db: Session, section_id: str, student_id: str) -> bool:
    enrollment = db.query(SectionEnrollmentDB).filter(
        SectionEnrollmentDB.section_id == section_id,
        SectionEnrollmentDB.student_id == student_id,
        SectionEnrollmentDB.is_active == True
    ).first()
    
    if enrollment:
        enrollment.is_active = False  # Soft delete
        db.commit()
        return True
    return False
```

### Queries Filter Active Records
```python
def get_section_roster(self, db: Session, section_id: str, include_inactive: bool = False):
    query = db.query(SectionEnrollmentDB).filter(
        SectionEnrollmentDB.section_id == section_id
    )
    
    if not include_inactive:
        query = query.filter(SectionEnrollmentDB.is_active == True)
    
    return query.all()
```

## Alternatives Considered

### Hard Delete
- **Pros**: Simpler queries, less data storage
- **Cons**: Loses history, complex re-enrollment, potential data integrity issues

### Separate History Table
- **Pros**: Clean separation of active/historical data
- **Cons**: More complex schema, requires triggers or application logic to maintain

### End Date Field
- **Pros**: Can track duration of enrollment
- **Cons**: More complex queries, nullable date field

## Consequences

### Positive
- Complete enrollment history maintained
- Easy re-enrollment process
- Better analytics capabilities
- No data loss

### Negative
- Slightly more complex queries (must filter by is_active)
- More data storage over time
- Need to consider inactive records in all queries

## Future Considerations
- May need periodic archival of very old inactive enrollments
- Could add indexes on (section_id, is_active) for performance
- Might add end_date field later for duration tracking