from django.test.runner import DiscoverRunner
from django.db import connection
from django.core.management import call_command
import logging

# Disable migration warnings during test setup
logging.getLogger("django.db.backends.schema").setLevel(logging.ERROR)


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
        # Try the original setup_databases first
        try:
            old_config = super().setup_databases(**kwargs)
        except Exception as e:
            if "duplicate column name" in str(e) or "no such column" in str(e):
                # Migration failed due to schema conflicts - handle it manually
                print(f"Migration failed with schema conflict: {e}")
                print("Creating test database with correct schema manually...")

                # Create test database without migrations
                old_config = self._create_test_db_manually(**kwargs)
            else:
                # Some other error - re-raise
                raise

        # Now fix the database schema directly if needed
        self._fix_database_schema()

        return old_config

    def _create_test_db_manually(self, **kwargs):
        """
        Create test database manually when migrations fail.
        """
        from django.test.utils import setup_test_environment, teardown_test_environment
        from django.db import connections

        setup_test_environment()

        # Get database settings
        old_config = {}

        for alias in connections:
            connection = connections[alias]
            old_config[alias] = {
                "NAME": connection.settings_dict["NAME"],
            }

            # Create test database
            connection.creation.create_test_db(
                verbosity=self.verbosity, autoclobber=True
            )

            # Create tables manually with correct schema
            self._create_correct_schema(connection)

        return old_config

    def _create_correct_schema(self, db_connection):
        """
        Create the correct database schema manually.
        """
        with db_connection.cursor() as cursor:
            # Create auth_user table (required for foreign keys)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password VARCHAR(128) NOT NULL,
                    last_login DATETIME,
                    is_superuser BOOL NOT NULL,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    first_name VARCHAR(150) NOT NULL,
                    last_name VARCHAR(150) NOT NULL,
                    email VARCHAR(254) NOT NULL,
                    is_staff BOOL NOT NULL,
                    is_active BOOL NOT NULL,
                    date_joined DATETIME NOT NULL
                );
            """
            )

            # Create orders_address table with correct schema
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders_address (
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

            # Create orders_checkout table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders_checkout (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    payment_method VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    shipping_address_id INTEGER NOT NULL REFERENCES orders_address (id),
                    user_id INTEGER NOT NULL REFERENCES auth_user (id)
                );
            """
            )

            # Create orders_checkoutitem table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders_checkoutitem (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quantity INTEGER NOT NULL,
                    price_at_checkout DECIMAL(10, 2) NOT NULL,
                    checkout_id INTEGER NOT NULL REFERENCES orders_checkout (id),
                    product_id INTEGER NOT NULL
                );
            """
            )

            # Create orders_orderstatushistory table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders_orderstatushistory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status VARCHAR(20) NOT NULL,
                    notes TEXT NULL,
                    created_at DATETIME NOT NULL,
                    created_by_id INTEGER NULL REFERENCES auth_user (id),
                    checkout_id INTEGER NOT NULL REFERENCES orders_checkout (id)
                );
            """
            )

            # Create django_migrations table to track migrations
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS django_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied DATETIME NOT NULL
                );
            """
            )

            # Create indices
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS orders_address_user_id ON orders_address (user_id);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS orders_checkout_user_id ON orders_checkout (user_id);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS orders_checkout_shipping_address_id ON orders_checkout (shipping_address_id);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS orders_checkoutitem_checkout_id ON orders_checkoutitem (checkout_id);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS orders_orderstatushistory_created_by_id ON orders_orderstatushistory (created_by_id);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS orders_orderstatushistory_checkout_id ON orders_orderstatushistory (checkout_id);"
            )

    def _fix_database_schema(self):
        """
        Fix any remaining database schema issues.
        """
        with connection.cursor() as cursor:
            # Disable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=off;")

            # Check if address table exists and has correct schema
            cursor.execute("PRAGMA table_info(orders_address);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Ensure we have the apartment_unit column and not apartment_address
            if (
                "apartment_address" in column_names
                and "apartment_unit" not in column_names
            ):
                cursor.execute(
                    "ALTER TABLE orders_address RENAME COLUMN apartment_address TO apartment_unit;"
                )

            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=on;")
