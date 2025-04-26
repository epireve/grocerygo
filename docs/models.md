# GroceryGo Database Models Documentation

This document provides a comprehensive overview of all database models used in the GroceryGo application. Understanding these models is essential for developing features, fixing bugs, and extending the application.

## Table of Contents

1. [Product Models](#product-models)
2. [User Account Models](#user-account-models)
3. [Cart Models](#cart-models)
4. [Order Models](#order-models)
5. [Relationships Overview](#relationships-overview)

## Product Models

The product-related models are defined in `products/models.py`.

### Category

The `Category` model represents product categories in the GroceryGo application.

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Unique name of the category |
| `slug` | SlugField | URL-friendly version of the name, automatically generated |
| `description` | TextField | Detailed description of the category |
| `image` | ImageField | Category image, stored in 'categories/' directory |
| `parent` | ForeignKey | Self-reference to parent category, enabling hierarchical structure |
| `active` | BooleanField | Whether the category is active and visible on the site |
| `created_at` | DateTimeField | When the category was created |
| `updated_at` | DateTimeField | When the category was last updated |

**Methods:**
- `__str__()`: Returns the category name
- `save()`: Automatically generates a slug if not provided
- `get_absolute_url()`: Returns the URL for viewing the category

**Meta:**
- `verbose_name`: "Category"
- `verbose_name_plural`: "Categories"
- `ordering`: Alphabetical by name

### Product

The `Product` model represents products available for purchase.

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Name of the product |
| `slug` | SlugField | URL-friendly version of the name |
| `description` | TextField | Detailed description of the product |
| `price` | DecimalField | Regular price of the product |
| `discount_price` | DecimalField | Optional discounted price |
| `category` | ForeignKey | Reference to the product's category |
| `image` | ImageField | Product image, stored in 'products/' directory |
| `stock` | IntegerField | Available quantity (default: 100) |
| `is_active` | BooleanField | Whether the product is active and available |
| `is_featured` | BooleanField | Whether the product should be featured on the homepage |
| `parent` | ForeignKey | Self-reference to parent product, enabling variants |
| `created_at` | DateTimeField | When the product was created |
| `updated_at` | DateTimeField | When the product was last updated |

**Properties:**
- `has_variants`: Returns True if the product has variant products
- `is_variant`: Returns True if the product is a variant of another product

**Methods:**
- `__str__()`: Returns the product name
- `save()`: Automatically generates a slug if not provided
- `get_absolute_url()`: Returns the URL for viewing the product detail

**Meta:**
- `verbose_name`: "Product"
- `verbose_name_plural`: "Products"
- `ordering`: Alphabetical by name

## User Account Models

The user account models are defined in `accounts/models.py`. Note that the application uses Django's built-in `User` model along with a custom profile.

### UserProfile

The `UserProfile` model extends Django's User model with additional information.

| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOneField | Link to Django's built-in User model |
| `full_name` | CharField | User's full name |
| `phone_number` | CharField | User's phone number |
| `address` | TextField | User's address |
| `terms_accepted` | BooleanField | Whether the user has accepted terms and conditions |

**Methods:**
- `__str__()`: Returns a string representation of the profile

**Signals:**
- `create_user_profile`: Creates a profile automatically when a user is created
- `save_user_profile`: Saves the profile when the user is saved

## Cart Models

The cart models are defined in `cart/models.py`.

### Cart

The `Cart` model represents a shopping cart, which can be associated with a logged-in user or a session.

| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOneField | Optional link to a user (for logged-in users) |
| `created_at` | DateTimeField | When the cart was created |
| `updated_at` | DateTimeField | When the cart was last updated |
| `session_id` | CharField | Session identifier for anonymous users |

**Properties:**
- `total_price`: Calculates the total price of all items in the cart
- `total_items`: Calculates the total number of items in the cart

**Methods:**
- `__str__()`: Returns a string representation of the cart

**Meta:**
- `verbose_name`: "Cart"
- `verbose_name_plural`: "Carts"

### CartItem

The `CartItem` model represents an item in a shopping cart.

| Field | Type | Description |
|-------|------|-------------|
| `cart` | ForeignKey | Reference to the cart this item belongs to |
| `product` | ForeignKey | Reference to the product being added to cart |
| `quantity` | PositiveIntegerField | Quantity of the product |
| `added_at` | DateTimeField | When the item was added to the cart |
| `updated_at` | DateTimeField | When the item was last updated |

**Properties:**
- `total_price`: Calculates the total price for this item (quantity × price)

**Methods:**
- `__str__()`: Returns a string representation of the cart item

**Meta:**
- `verbose_name`: "Cart Item"
- `verbose_name_plural`: "Cart Items"
- `unique_together`: ("cart", "product") - Prevents duplicate products in cart

## Order Models

The order models are defined in `orders/models.py`.

### Address

The `Address` model represents shipping and billing addresses.

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Reference to the user who owns this address |
| `address_type` | CharField | Type of address ("shipping" or "billing") |
| `full_name` | CharField | Full name of the recipient |
| `street_address` | CharField | Street address |
| `apartment_address` | CharField | Optional apartment or unit number |
| `city` | CharField | City |
| `state` | CharField | State/province |
| `postal_code` | CharField | Postal code/ZIP code |
| `country` | CharField | Country (default: "Malaysia") |
| `phone_number` | CharField | Contact phone number |
| `is_default` | BooleanField | Whether this is the default address for the user |
| `created_at` | DateTimeField | When the address was created |
| `updated_at` | DateTimeField | When the address was last updated |

**Methods:**
- `__str__()`: Returns a string representation of the address

**Meta:**
- `verbose_name`: "Address"
- `verbose_name_plural`: "Addresses"
- `ordering`: Default addresses first, then by creation date (descending)

### Order

The `Order` model represents a customer order.

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Reference to the user who placed the order |
| `order_number` | CharField | Unique order number |
| `shipping_address` | ForeignKey | Reference to the shipping address |
| `billing_address` | ForeignKey | Reference to the billing address |
| `order_status` | CharField | Status of the order ("pending", "processing", "shipped", "delivered", "cancelled") |
| `payment_method` | CharField | Method of payment ("credit_card", "bank_transfer", "cash_on_delivery", "e_wallet") |
| `payment_status` | BooleanField | Whether payment has been completed |
| `subtotal` | DecimalField | Subtotal of all items before tax and shipping |
| `shipping_cost` | DecimalField | Cost of shipping |
| `tax` | DecimalField | Tax amount |
| `total` | DecimalField | Total order cost |
| `notes` | TextField | Optional notes for the order |
| `created_at` | DateTimeField | When the order was created |
| `updated_at` | DateTimeField | When the order was last updated |

**Properties:**
- `order_items_count`: Returns the number of items in the order
- `get_status_display_class`: Returns CSS class based on order status

**Methods:**
- `__str__()`: Returns a string representation of the order
- `save()`: Automatically calculates the total if not provided

**Meta:**
- `verbose_name`: "Order"
- `verbose_name_plural`: "Orders"
- `ordering`: Latest orders first

### OrderItem

The `OrderItem` model represents an item within an order.

| Field | Type | Description |
|-------|------|-------------|
| `order` | ForeignKey | Reference to the order |
| `product` | ForeignKey | Reference to the product |
| `price` | DecimalField | Price of the product at time of purchase |
| `quantity` | PositiveIntegerField | Quantity ordered |

**Properties:**
- `total_price`: Calculates the total price for this item

**Methods:**
- `__str__()`: Returns a string representation of the order item

**Meta:**
- `verbose_name`: "Order Item"
- `verbose_name_plural`: "Order Items"

### OrderStatusHistory

The `OrderStatusHistory` model tracks changes in order status for audit purposes.

| Field | Type | Description |
|-------|------|-------------|
| `order` | ForeignKey | Reference to the order |
| `status` | CharField | New status value |
| `notes` | TextField | Optional notes about the status change |
| `created_by` | ForeignKey | User who made the status change |
| `created_at` | DateTimeField | When the status change occurred |

**Methods:**
- `__str__()`: Returns a string representation of the status change

**Meta:**
- `verbose_name`: "Order Status History"
- `verbose_name_plural`: "Order Status History"
- `ordering`: Latest changes first

## Relationships Overview

Here's a summary of the key relationships between models:

1. **User and UserProfile**: One-to-one relationship. Each Django User has one UserProfile.

2. **User and Orders**: One-to-many relationship. A User can have multiple Orders.

3. **User and Addresses**: One-to-many relationship. A User can have multiple Addresses.

4. **User and Cart**: One-to-one relationship. A User can have one active Cart.

5. **Category and Products**: One-to-many relationship. A Category can have multiple Products.

6. **Category Hierarchy**: Self-referential relationship. Categories can have parent categories and child categories.

7. **Product Variants**: Self-referential relationship. Products can have parent products and variant products.

8. **Cart and CartItems**: One-to-many relationship. A Cart can have multiple CartItems.

9. **Order and OrderItems**: One-to-many relationship. An Order can have multiple OrderItems.

10. **Order and Addresses**: Many-to-one relationships. An Order has one shipping Address and one billing Address.

11. **Order and OrderStatusHistory**: One-to-many relationship. An Order can have multiple status changes recorded. 