from django.db import migrations


def rename_apartment_field_conditionally(apps, schema_editor):
    """
    Rename apartment_address to apartment_unit only if needed
    """
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        # Check if the table exists and get its schema
        cursor.execute("PRAGMA table_info(orders_address);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        has_apartment_address = "apartment_address" in column_names
        has_apartment_unit = "apartment_unit" in column_names

        if has_apartment_address and not has_apartment_unit:
            # Simple rename case
            cursor.execute("PRAGMA foreign_keys=off;")
            cursor.execute(
                """
                ALTER TABLE orders_address 
                RENAME COLUMN apartment_address TO apartment_unit;
            """
            )
            cursor.execute("PRAGMA foreign_keys=on;")
        elif has_apartment_address and has_apartment_unit:
            # Both exist - merge the data and drop apartment_address
            cursor.execute("PRAGMA foreign_keys=off;")
            # Update apartment_unit with data from apartment_address where apartment_unit is null/empty
            cursor.execute(
                """
                UPDATE orders_address 
                SET apartment_unit = apartment_address 
                WHERE apartment_unit IS NULL OR apartment_unit = '';
            """
            )
            # Drop the apartment_address column by recreating the table
            cursor.execute(
                """
                CREATE TABLE _orders_address_temp AS 
                SELECT id, address_type, full_name, street_address, apartment_unit,
                       city, state, postal_code, country, phone, is_default, 
                       created_at, updated_at, user_id
                FROM orders_address;
            """
            )
            cursor.execute("DROP TABLE orders_address;")
            cursor.execute("ALTER TABLE _orders_address_temp RENAME TO orders_address;")
            cursor.execute(
                "CREATE INDEX orders_address_user_id ON orders_address (user_id);"
            )
            cursor.execute("PRAGMA foreign_keys=on;")
        # If only apartment_unit exists, nothing to do


def reverse_func(apps, schema_editor):
    """No need to reverse"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0008_remove_deprecated_models"),
    ]

    operations = [
        migrations.RunPython(rename_apartment_field_conditionally, reverse_func),
    ]
