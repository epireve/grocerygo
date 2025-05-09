# Generated by Django 5.0.1 on 2025-04-26 15:01

from django.db import migrations, models


def copy_shipping_addresses_to_address(apps, schema_editor):
    """
    Copy data from ShippingAddress model to Address model
    """
    ShippingAddress = apps.get_model("orders", "ShippingAddress")
    Address = apps.get_model("orders", "Address")
    Checkout = apps.get_model("orders", "Checkout")

    # Create a mapping to store old ID to new ID
    address_mapping = {}

    # Get all shipping addresses
    shipping_addresses = ShippingAddress.objects.all()

    # Copy each shipping address to the Address model
    for shipping_address in shipping_addresses:
        # Create a new Address instance
        address = Address(
            user=shipping_address.user,
            address_type="shipping",
            full_name=shipping_address.full_name,
            street_address=shipping_address.street_address,
            apartment_address=shipping_address.apartment_unit,
            city=shipping_address.city,
            state=shipping_address.state,
            postal_code=shipping_address.postal_code,
            country=shipping_address.country,
            phone=shipping_address.phone,
            is_default=shipping_address.is_default,
            created_at=shipping_address.created_at,
            updated_at=shipping_address.updated_at,
        )
        address.save()

        # Store mapping of old ID to new ID
        address_mapping[shipping_address.id] = address.id

    # Update Checkout records to point to the new Address IDs
    for checkout in Checkout.objects.all():
        if (
            hasattr(checkout, "shipping_address_id")
            and checkout.shipping_address_id
            and checkout.shipping_address_id in address_mapping
        ):
            checkout.shipping_address_id = address_mapping[checkout.shipping_address_id]
            checkout.save()


def reverse_migration(apps, schema_editor):
    """
    No need to reverse this migration
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_alter_address_options_remove_address_phone_number_and_more"),
    ]

    operations = [
        migrations.RunPython(copy_shipping_addresses_to_address, reverse_migration),
        # Update the shipping_address field to make it required again
        migrations.AlterField(
            model_name="checkout",
            name="shipping_address",
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name="checkout_shipping_orders",
                to="orders.address",
            ),
        ),
    ]
