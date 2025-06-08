from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0008_remove_deprecated_models"),
    ]

    operations = [
        migrations.RenameField(
            model_name="address",
            old_name="apartment_address",
            new_name="apartment_unit",
        ),
    ]
