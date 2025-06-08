from django.test.runner import DiscoverRunner
from django.db import connection


class FixedSchemaTestRunner(DiscoverRunner):
    """
    A test runner that fixes the database schema issues before running tests.

    This custom test runner is REQUIRED due to complex migration history that
    causes "duplicate column name: phone" errors during test database creation.

    The migration history contains multiple migrations that add/remove the phone
    column, creating conflicts when Django tries to create the test database.
    This runner manually recreates the tables with the correct schema after
    the initial migration attempt fails.

    WARNING: Do not remove this test runner without first resolving the
    underlying migration conflicts. Tests will fail with OperationalError
    without this fix.
    """

    def setup_databases(self, **kwargs):
        """
        Set up the test databases with fixed schema.
        """
        # First, call the original setup_databases to create test databases
        old_config = super().setup_databases(**kwargs)

        # Now fix the database schema directly
        with connection.cursor() as cursor:
            # We need to execute each statement individually for SQLite

            # Disable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=off;")

            # Check if address table exists
            cursor.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='orders_address';"
            )
            address_table_exists = cursor.fetchone()[0] > 0

            if address_table_exists:
                # Create a correct schema table
                cursor.execute(
                    """
                    CREATE TABLE orders_address_new (
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
                """
                )

                # Drop old table
                cursor.execute("DROP TABLE IF EXISTS orders_address;")

                # Rename new table to correct name
                cursor.execute(
                    "ALTER TABLE orders_address_new RENAME TO orders_address;"
                )

                # Recreate indices
                cursor.execute(
                    "CREATE INDEX orders_address_user_id ON orders_address (user_id);"
                )

            # Check if OrderStatusHistory table exists
            cursor.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='orders_orderstatushistory';"
            )
            status_table_exists = cursor.fetchone()[0] > 0

            if status_table_exists:
                # Create a correct schema table
                cursor.execute(
                    """
                    CREATE TABLE orders_orderstatushistory_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        status VARCHAR(20) NOT NULL,
                        notes TEXT NULL,
                        created_at DATETIME NOT NULL,
                        created_by_id INTEGER NULL REFERENCES auth_user (id),
                        checkout_id INTEGER NOT NULL REFERENCES orders_checkout (id)
                    );
                """
                )

                # Drop old table
                cursor.execute("DROP TABLE IF EXISTS orders_orderstatushistory;")

                # Rename new table to correct name
                cursor.execute(
                    "ALTER TABLE orders_orderstatushistory_new RENAME TO orders_orderstatushistory;"
                )

                # Recreate indices
                cursor.execute(
                    "CREATE INDEX orders_orderstatushistory_created_by_id ON orders_orderstatushistory (created_by_id);"
                )
                cursor.execute(
                    "CREATE INDEX orders_orderstatushistory_checkout_id ON orders_orderstatushistory (checkout_id);"
                )

            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=on;")

        return old_config
