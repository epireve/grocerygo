# GroceryGo Models Documentation

## Database Model Relationships

This document describes the core models in the GroceryGo application and their relationships after the code consolidation.

## Abstract Base Models

### BaseItemModel

Located in `orders/models.py`, this abstract base class provides common fields and functionality for item models across the application:

- **Fields**:
  - `product`: ForeignKey to Product model
  - `quantity`: PositiveInteger representing number of items
  - `price`: DecimalField storing the price at time of item creation

- **Methods**:
  - `total_price`: Property method calculating price × quantity
  - `save()`: Overridden to ensure price is set if not provided

This base model is inherited by both CartItem and CheckoutItem, removing duplicate code and ensuring consistent behavior.

## Core Models

### User (Django's built-in)

The system uses Django's built-in User model with a related UserProfile model.

### Address

A flexible address model that can be used for both shipping and billing purposes.

- **Fields**:
  - `user`: ForeignKey to User
  - `address_type`: Choice field ("shipping" or "billing")
  - `full_name`: Customer's full name
  - `street_address`: Street address
  - `apartment_unit`: Apartment/unit number (optional)
  - `city`, `state`, `postal_code`, `country`: Geographic information
  - `phone`: Contact phone number (optional)
  - `is_default`: Boolean indicating if this is the default address for the user

- **Methods**:
  - Custom `save()` to ensure only one default address per type per user

### Cart

Represents a user's shopping cart, can be associated with authenticated users or session-based for guests.

- **Fields**:
  - `user`: OneToOneField to User (null=True for guest carts)
  - `session_id`: Session identifier for guest carts
  - `coupon`: Optional coupon applied to the cart

- **Methods**:
  - `total_price`: Property calculating total price of all items
  - `total_items`: Property calculating total number of items

### CartItem

Items within a cart, inherits from BaseItemModel.

- **Fields** (inherited from BaseItemModel):
  - `product`, `quantity`, `price`
- **Additional Fields**:
  - `cart`: ForeignKey to Cart
  - `added_at`, `updated_at`: Timestamps

### Checkout

Represents a completed order.

- **Fields**:
  - `user`: ForeignKey to User
  - `shipping_address`: ForeignKey to Address
  - `payment_method`: Choice field for payment options
  - `subtotal`, `shipping_cost`, `tax`, `total`: Price fields
  - `status`: Current order status
  - `notes`: Optional notes for the order
  - `created_at`, `updated_at`: Timestamps

### CheckoutItem

Items within a checkout/order, inherits from BaseItemModel.

- **Fields** (inherited from BaseItemModel):
  - `product`, `quantity`, `price`
- **Additional Fields**:
  - `checkout`: ForeignKey to Checkout

### OrderStatusHistory

Audit trail for order status changes.

- **Fields**:
  - `checkout`: ForeignKey to Checkout
  - `status`: New status value
  - `notes`: Optional notes about the status change
  - `created_by`: User who changed the status
  - `created_at`: Timestamp

## Coupon System

### Coupon

Represents discount coupons that can be applied to carts.

- **Fields**:
  - `code`: Unique coupon code
  - `discount_type`: Type of discount (percentage or fixed amount)
  - `value`: Amount of the discount
  - `min_purchase`: Minimum purchase amount to use the coupon
  - `valid_from`, `valid_to`: Validity period
  - `is_active`: Whether the coupon is currently active

## Code Consolidation Changes

As part of the code consolidation effort, the following changes were made:

1. **Removed Redundant Models**:
   - Removed unused `Order` and `OrderItem` models
   - Removed redundant `ShippingAddress` model in favor of the more flexible `Address` model

2. **Field Standardization**:
   - Renamed `apartment_address` to `apartment_unit` in the Address model for consistency
   - Standardized `total_price` method name across item models

3. **Created Abstract Base Classes**:
   - Added `BaseItemModel` for shared fields and methods between `CartItem` and `CheckoutItem`

4. **Consolidated Logic**:
   - Moved common validation and calculation logic to base classes
   - Standardized save() methods across models

5. **Documentation**:
   - Added docstrings to models explaining relationships
   - Created this documentation file explaining the model structure

These changes improve code maintainability, reduce duplication, and establish consistent naming conventions across the codebase.