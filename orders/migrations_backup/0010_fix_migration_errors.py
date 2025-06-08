# Generated manually for fixing migration issues
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0007_fix_migration_issue"),
    ]

    operations = [
        # First, add the apartment_unit column
        migrations.AddField(
            model_name="address",
            name="apartment_unit",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        # Add checkout_id field to OrderStatusHistory
        migrations.AddField(
            model_name="orderstatushistory",
            name="checkout",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="status_history",
                to="orders.checkout",
            ),
        ),
    ]
