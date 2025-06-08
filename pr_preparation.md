# Pull Request Preparation for Issue #2

## PR Title
Model Consolidation: Implement BaseItemModel and Standardize Field Names

## PR Description
This pull request addresses issue #2 by consolidating redundant models, implementing an abstract base class for item models, and standardizing field names across the codebase.

### Changes Made
- Created a `BaseItemModel` abstract class to reduce code duplication
- Removed redundant models (`Order`, `OrderItem`, `ShippingAddress`)
- Standardized field names (e.g., renamed `apartment_address` to `apartment_unit`)
- Implemented safe database migrations for schema changes
- Fixed testing infrastructure to accommodate model changes
- Updated documentation in `docs/models.md`

### Testing Done
- Unit tests updated to use the new model structure
- Migration scripts tested on development and test databases
- Manual testing of key application flows
- Verified that no data loss occurs during migration

### Related Issue
Closes #2

## Migration Instructions
When merging this PR, please run the following commands:

```bash
# 1. Create a database backup
cp db.sqlite3 db_backup_before_pr_merge.sqlite3

# 2. Apply migrations
python manage.py migrate

# 3. Run tests to verify changes
python manage.py test

# 4. Check admin interface to verify data integrity
```

## Documentation Updates
- Updated `docs/models.md` to document the new model structure and relationships
- No changes needed to README.md as it already references `docs/models.md` for model documentation