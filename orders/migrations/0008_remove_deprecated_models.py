# Generated manually for model consolidation
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0007_fix_migration_issue"),
    ]

    operations = [
        # First, update OrderStatusHistory to reference Checkout instead of Order
        migrations.RenameField(
            model_name="orderstatushistory",
            old_name="order",
            new_name="checkout",
        ),
        # Remove ShippingAddress model
        migrations.RemoveField(
            model_name="shippingaddress",
            name="user",
        ),
        migrations.DeleteModel(
            name="ShippingAddress",
        ),
        # Remove OrderItem model
        migrations.RemoveField(
            model_name="orderitem",
            name="order",
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="product",
        ),
        migrations.DeleteModel(
            name="OrderItem",
        ),
        # Remove Order model
        migrations.RemoveField(
            model_name="order",
            name="billing_address",
        ),
        migrations.RemoveField(
            model_name="order",
            name="shipping_address",
        ),
        migrations.RemoveField(
            model_name="order",
            name="user",
        ),
        migrations.DeleteModel(
            name="Order",
        ),
    ]
