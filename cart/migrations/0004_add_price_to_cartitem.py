# Generated manually to fix missing price field in CartItem
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0003_cart_coupon"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitem",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
