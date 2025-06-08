-- Add the remaining migrations to django_migrations table
INSERT INTO django_migrations (app, name, applied)
VALUES 
    ('orders', '0013_fix_migration_graph', datetime('now')),
    ('orders', '0015_merge_20250608_0024', datetime('now')),
    ('orders', '0016_fix_orderstatushistory_migration', datetime('now'));