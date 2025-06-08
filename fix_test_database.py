#!/usr/bin/env python
"""
Script to fix database schema issues before running tests.
"""
import os
import sys
import sqlite3
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grocerygo.settings")
django.setup()

from django.conf import settings

# Path to the test database - use the in-memory database to avoid file issues
TEST_DB_PATH = ":memory:"


def fix_database_schema():
    """Fix the database schema issues."""
    print("Fixing database schema...")

    # Connect to the database
    conn = sqlite3.connect(settings.DATABASES["default"]["NAME"])
    cursor = conn.cursor()

    try:
        # Check if the address table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orders_address'"
        )
        if cursor.fetchone():
            # Get table info to check for duplicate columns
            cursor.execute("PRAGMA table_info(orders_address)")
            columns = cursor.fetchall()

            # Check if phone column exists more than once
            phone_columns = [col for col in columns if col[1] == "phone"]

            if len(phone_columns) > 1:
                print("Fixing duplicate phone column in orders_address table...")

                # Disable foreign key constraints
                cursor.execute("PRAGMA foreign_keys=off")

                # Create a temporary table with the correct schema
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
                )
                """
                )

                # Copy data from the original table
                cursor.execute(
                    """
                INSERT INTO orders_address_new 
                SELECT id, address_type, full_name, street_address, 
                    COALESCE(apartment_unit, apartment_address), 
                    city, state, postal_code, country, phone, 
                    is_default, created_at, updated_at, user_id 
                FROM orders_address
                """
                )

                # Drop the original table
                cursor.execute("DROP TABLE orders_address")

                # Rename the new table
                cursor.execute(
                    "ALTER TABLE orders_address_new RENAME TO orders_address"
                )

                # Recreate indices
                cursor.execute(
                    "CREATE INDEX orders_address_user_id ON orders_address (user_id)"
                )

                # Re-enable foreign key constraints
                cursor.execute("PRAGMA foreign_keys=on")

                print("Fixed orders_address table")

        # Also fix OrderStatusHistory table if needed
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orders_orderstatushistory'"
        )
        if cursor.fetchone():
            print("Fixing orders_orderstatushistory table...")

            # Create a temporary table with the correct schema
            cursor.execute(
                """
            CREATE TABLE orders_orderstatushistory_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status VARCHAR(20) NOT NULL,
                notes TEXT NULL,
                created_at DATETIME NOT NULL,
                created_by_id INTEGER NULL REFERENCES auth_user (id),
                checkout_id INTEGER NOT NULL REFERENCES orders_checkout (id)
            )
            """
            )

            # Copy data from the original table, safely handling potential column differences
            try:
                cursor.execute(
                    """
                INSERT INTO orders_orderstatushistory_new 
                SELECT id, status, notes, created_at, created_by_id, checkout_id
                FROM orders_orderstatushistory
                """
                )
            except sqlite3.OperationalError:
                # Handle case where columns don't match
                print(
                    "Column mismatch in orders_orderstatushistory, skipping data copy"
                )

            # Drop the original table
            cursor.execute("DROP TABLE orders_orderstatushistory")

            # Rename the new table
            cursor.execute(
                "ALTER TABLE orders_orderstatushistory_new RENAME TO orders_orderstatushistory"
            )

            # Recreate indices
            cursor.execute(
                "CREATE INDEX orders_orderstatushistory_created_by_id ON orders_orderstatushistory (created_by_id)"
            )
            cursor.execute(
                "CREATE INDEX orders_orderstatushistory_checkout_id ON orders_orderstatushistory (checkout_id)"
            )

            print("Fixed orders_orderstatushistory table")

        # Commit changes
        conn.commit()
        print("Database schema fixed successfully")

    except Exception as e:
        print(f"Error fixing database schema: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    fix_database_schema()
