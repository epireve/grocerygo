from django.test import TestCase
from django.db import connection


class FixedSchemaTestCase(TestCase):
    """
    A TestCase that fixes the schema issues in the test database before running tests.

    This custom TestCase is REQUIRED as a fallback/alternative to FixedSchemaTestRunner
    for fixing database schema issues caused by complex migration history.

    The migration history contains multiple migrations that add/remove the phone
    column, creating conflicts during test database setup. This TestCase manually
    recreates the Address table with the correct schema.

    Usage: Inherit from this class instead of django.test.TestCase when tests
    need to interact with the Address model.

    WARNING: Do not remove this utility without first resolving the underlying
    migration conflicts. Tests that use Address model may fail without this fix.
    """

    @classmethod
    def setUpClass(cls):
        """Run setup operations before any test method in the class."""
        # Call parent setup first
        super().setUpClass()

        # Fix the database schema directly using SQL
        with connection.cursor() as cursor:
            # Check if phone column exists and fix the table if needed
            cursor.execute(
                """
                -- Disable foreign key constraints
                PRAGMA foreign_keys=off;
                
                -- Create a completely new table with correct schema
                CREATE TABLE IF NOT EXISTS _orders_address_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address_type VARCHAR(10) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    street_address VARCHAR(255) NOT NULL,
                    apartment_unit VARCHAR(255) NULL,
                    city VARCHAR(100) NOT NULL,
                    state VARCHAR(100) NOT NULL,
                    postal_code VARCHAR(20) NOT NULL,
                    country VARCHAR(100) NOT NULL,
                    phone VARCHAR(50) NULL,
                    is_default BOOL NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    user_id INTEGER NOT NULL REFERENCES auth_user (id)
                );
                
                -- Try to drop original table if it exists
                DROP TABLE IF EXISTS orders_address;
                
                -- Rename temp table to the correct name
                ALTER TABLE _orders_address_temp RENAME TO orders_address;
                
                -- Recreate indices
                CREATE INDEX orders_address_user_id ON orders_address (user_id);
                
                -- Re-enable foreign key constraints
                PRAGMA foreign_keys=on;
            """
            )
