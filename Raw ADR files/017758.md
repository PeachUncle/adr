# ADR-002: Use Excel Files for Decision Tables

## Status

Accepted

## Context

The project needs a way to define business rules that can be easily understood and modified by business users, not just developers. We considered several approaches for rule definition:

- **Excel decision tables**: Business-friendly spreadsheet format
- **DRL files**: Native Drools Rule Language files
- **JSON/YAML configuration**: Structured text-based rule definition
- **Database-stored rules**: Rules stored in database tables
- **Web-based rule builder**: Custom UI for rule creation

Key requirements:
- Business users should be able to modify rules without developer intervention
- Rules should be version-controlled and auditable
- Format should be familiar to business stakeholders
- Support for complex rule logic with multiple conditions and actions
- Easy validation and testing of rule changes

## Decision

We chose to use **Excel files (.xlsx/.xls)** as the primary format for defining decision tables.

The decision table structure includes:
- **RuleSet**: Name of the rule collection
- **RuleId**: Unique identifier for each rule
- **Salience**: Rule priority (execution order)
- **Condition columns**: Input criteria for rule matching
- **Action columns**: Outputs when rule conditions are met

## Consequences

### Positive

- **Business-friendly**: Excel is familiar to most business users
- **Visual clarity**: Tabular format makes rule logic easy to understand
- **Version control**: Excel files can be stored in Git and tracked for changes
- **Validation**: Built-in Excel features for data validation and formatting
- **Documentation**: Can include documentation sheets within the same file
- **Flexibility**: Support for complex conditions and multiple actions per rule
- **Drools integration**: Native support in Drools for Excel decision tables
- **Offline editing**: Business users can work on rules without system access

### Negative

- **Binary format**: Excel files are binary, making diff/merge operations difficult
- **Concurrent editing**: Multiple users cannot easily edit the same file simultaneously
- **File corruption**: Excel files can become corrupted more easily than text files
- **Tool dependency**: Requires Excel or compatible software for editing
- **Size limitations**: Large rule sets may become unwieldy in spreadsheet format
- **Syntax errors**: Easy to introduce formatting errors that break rule compilation

### Neutral

- **Learning curve**: Business users need to understand decision table format and syntax
- **File management**: Need processes for uploading and deploying rule changes
- **Backup strategy**: Important to maintain backups of rule files

## References

- [Drools Decision Tables Documentation](https://docs.drools.org/7.73.0.Final/drools-docs/html_single/#decision-tables-con_decision-tables)
- [Excel Decision Table Examples](../src/main/resources/rules/decision-tables/)
- [Decision Table Guide](../DECISION_TABLES_GUIDE.md)