# ADR-002: Cozi Integration

## Status
**Approved** — 2024-12-21

## Context

The family currently uses Cozi as their primary calendar and task management system. Cozi provides:
- Shared family calendar
- Shopping lists
- To-do lists
- Family journal

For the Reachy Home Assistant to be useful for daily briefings and schedule awareness, it needs access to this data.

### Key Requirements
1. Read calendar events for each family member
2. Access shared shopping and to-do lists
3. Sync regularly to stay current
4. Work offline with cached data
5. Avoid breaking existing family workflows

## Decision

**Use py-cozi library for one-way sync from Cozi to local PostgreSQL database.**

### Integration Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│    Cozi      │────▶│  Sync Service   │────▶│   PostgreSQL     │
│  (Cloud)     │     │  (py-cozi)      │     │   (Local)        │
└──────────────┘     └─────────────────┘     └──────────────────┘
                            │
                     Runs every 15 min
                     (or on-demand)
```

### Sync Strategy

| Data Type | Sync Frequency | Retention |
|-----------|----------------|-----------|
| Calendar events | Every 15 minutes | 30 days past, 90 days future |
| Shopping lists | Every 15 minutes | Current items only |
| To-do lists | Every 15 minutes | Active items + 7 days completed |
| Family members | On startup | Permanent |

### Data Mapping

```
Cozi Calendar Event → Local Event Table
├── event_id (Cozi ID)
├── title
├── start_time
├── end_time
├── location
├── notes
├── assigned_to (family member)
├── recurring_pattern
├── synced_at
└── source = 'cozi'
```

## Consequences

### Positive
- **Preserves existing workflow**: Family keeps using Cozi as they do now
- **No duplicate entry**: Events entered in Cozi appear in assistant automatically
- **Offline capability**: Local cache works when internet is down
- **Privacy**: Only reads data, doesn't push family data elsewhere

### Negative
- **One-way only**: Can't create events from assistant back to Cozi (API limitation)
- **Dependency on Cozi**: If Cozi changes/dies, need alternative
- **Credential storage**: Must store Cozi credentials locally
- **Sync delay**: Up to 15-minute lag for new events

### Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Cozi API changes | py-cozi library maintained; can fork if needed |
| Credential exposure | Store encrypted in .env, not in database |
| Cozi discontinuation | Data already in local DB; can migrate to Google Calendar sync |

## Implementation Notes

### Authentication
```python
from pycozi import Cozi

cozi = Cozi(
    email=os.getenv('COZI_EMAIL'),
    password=os.getenv('COZI_PASSWORD')
)
await cozi.login()
```

### Sync Logic
```python
async def sync_calendar():
    """Sync Cozi calendar to local database."""
    events = await cozi.get_calendar(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now() + timedelta(days=90)
    )

    for event in events:
        await upsert_event(
            cozi_id=event.id,
            title=event.title,
            start_time=event.start,
            end_time=event.end,
            # ... other fields
        )
```

### Scheduler
```python
# Run sync every 15 minutes
scheduler.add_job(sync_calendar, 'interval', minutes=15)
scheduler.add_job(sync_lists, 'interval', minutes=15)
```

## Future Considerations

1. **Two-way sync**: If Cozi adds write API, enable creating events via voice
2. **Google Calendar**: Add as alternative/supplement to Cozi
3. **iCloud Calendar**: For family members with Apple devices
4. **Push notifications**: If Cozi supports webhooks, use for instant sync

## Related Decisions
- ADR-001: Data storage (where synced data lives)
- ADR-003: Memory architecture (calendar data informs context)
