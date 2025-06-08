#!/usr/bin/env python
"""
A script to run the tests with a fixed test database schema.
This script:
1. Creates a test database
2. Applies necessary fixes to the schema
3. Runs the tests
"""
import os
import sys
import sqlite3
import subprocess

# Set up environment for Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")


def fix_test_database():
    """Fix the test database schema."""
    print("Creating and preparing test database...")

    # Get the test database path - typically it's the default with _test suffix
    test_db_path = "db.sqlite3"

    # Connect to the test database
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    try:
        # Modify the database schema directly using SQL to avoid migration issues
        # Disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=off")

        # Fix the Address table
        print("Fixing orders_address table in the test database...")
        cursor.execute(
            """
        -- First, drop the table if it exists
        DROP TABLE IF EXISTS orders_address;
        
        -- Create the table with the correct schema
        CREATE TABLE orders_address (
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
        
        -- Create the index
        CREATE INDEX orders_address_user_id ON orders_address (user_id);
        """
        )

        # Fix the OrderStatusHistory table
        print("Fixing orders_orderstatushistory table in the test database...")
        cursor.execute(
            """
        -- First, drop the table if it exists
        DROP TABLE IF EXISTS orders_orderstatushistory;
        
        -- Create the table with the correct schema
        CREATE TABLE orders_orderstatushistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status VARCHAR(20) NOT NULL,
            notes TEXT NULL,
            created_at DATETIME NOT NULL,
            created_by_id INTEGER NULL REFERENCES auth_user (id),
            checkout_id INTEGER NOT NULL REFERENCES orders_checkout (id)
        );
        
        -- Create the indices
        CREATE INDEX orders_orderstatushistory_created_by_id ON orders_orderstatushistory (created_by_id);
        CREATE INDEX orders_orderstatushistory_checkout_id ON orders_orderstatushistory (checkout_id);
        """
        )

        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=on")

        # Commit changes
        conn.commit()
        print("Test database schema fixed successfully")

    except Exception as e:
        print(f"Error fixing test database schema: {e}")
        conn.rollback()
    finally:
        conn.close()


# Run tests for specific file/module
def run_tests(test_path):
    print(f"Running tests for {test_path}...")

    # Run the tests using the venv Python
    cmd = ["./venv/bin/python", "manage.py", "test", test_path]
    result = subprocess.run(cmd)

    # Return the exit code
    return result.returncode


# Main function
if __name__ == "__main__":
    # Get the test path from command line arguments
    if len(sys.argv) < 2:
        print("Usage: ./venv/bin/python fix_test_db_during_tests.py <test_path>")
        print(
            "Example: ./venv/bin/python fix_test_db_during_tests.py orders.tests.DeprecatedModelsTest"
        )
        sys.exit(1)

    test_path = sys.argv[1]

    # Apply migration changes (if possible) to create test tables
    migrate_cmd = ["./venv/bin/python", "manage.py", "migrate"]
    try:
        subprocess.run(migrate_cmd, check=True)
        print("Migrations applied successfully")
    except subprocess.CalledProcessError:
        print("Warning: Migration failed, proceeding with manual schema fixes")

    # Fix the test database
    fix_test_database()

    # Run the tests
    exit_code = run_tests(test_path)

    # Exit with the same code as the test run
    sys.exit(exit_code)
