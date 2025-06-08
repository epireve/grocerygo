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
   - Removed deprecated `Customer` model that was redundant with Django's User model

2. **Field Standardization**:
   - Renamed `apartment_address` to `apartment_unit` in the Address model for consistency
   - Standardized `phone_number` to `phone` across all models
   - Standardized `total_price` method name across item models

3. **Created Abstract Base Classes**:
   - Added `BaseItemModel` for shared fields and methods between `CartItem` and `CheckoutItem`

4. **Consolidated Logic**:
   - Moved common validation and calculation logic to base classes
   - Standardized save() methods across models

5. **Documentation**:
   - Added docstrings to models explaining relationships
   - Created this documentation file explaining the model structure

## Migration Management and Testing Infrastructure

The model consolidation required sophisticated migration management and testing infrastructure:

### Advanced Migration System

1. **Sequential Migration Fixes** (migrations 0010-0018):
   - `0010_fix_migration_errors.py` - Initial consolidation conflict resolution
   - `0011_merge_20250608_0017.py` - Merge conflicting migration branches
   - `0012_fix_duplicate_phone_column.py` - Handle field renaming conflicts
   - `0013_fix_migration_graph.py` - Resolve migration dependency issues
   - `0014_complete_database_cleanup.py` - Final cleanup of deprecated tables
   - `0015_merge_20250608_0024.py` - Secondary merge resolution
   - `0016_fix_orderstatushistory_migration.py` - OrderStatusHistory table fixes
   - `0017_fix_test_database_schema.py` - Test database schema alignment
   - `0018_fix_test_database_phone_column.py` - Final phone field standardization

2. **Squashed Migration** (migration 0007):
   - Combined multiple migration operations for cleaner history
   - Simplified deployment and migration replay scenarios

### Comprehensive Testing Infrastructure

1. **Custom Test Runner**: `FixedSchemaTestRunner`
   - Automatically handles database schema fixes during test execution
   - Ensures test database matches production schema
   - Configured in `settings.py` as the default test runner

2. **Migration-Aware Test Base Class**: `FixedSchemaTestCase`
   - Provides foundation for tests that require proper database schema
   - Handles schema verification before test execution
   - Used as base class for all model tests

3. **Comprehensive Test Suite**:
   - **Address Model Tests**: Validation, default address logic, field constraints
   - **Checkout Model Tests**: Order processing, status management, relationship integrity
   - **OrderStatusHistory Tests**: Audit trail functionality, status change tracking
   - **Deprecation Verification Tests**: Ensures removed models are completely gone

4. **Database Testing Utilities**:
   - `orders/test_utils.py` - Schema verification and data validation helpers
   - `orders/simple_test.py` - Basic connectivity and model access tests
   - `orders/test_deprecated.py` - Verification that deprecated models are removed

### Database Recovery and Management Tools

1. **Automated Recovery Scripts**:
   - `fix_test_database.py` - Fixes schema issues in test environments
   - `fix_test_db_during_tests.py` - Runtime schema fixing during test execution

2. **Manual SQL Scripts** (for emergency recovery):
   - `fix_database.sql` - Complete database schema restoration
   - `fix_address_table.sql` - Address table specific fixes
   - `create_orderstatushistory.sql` - OrderStatusHistory table creation
   - `insert_remaining_migrations.sql` - Manual migration record management

### Data Integrity and Recovery

1. **Address Data Recovery**:
   - Successfully recovered 2 address records lost during initial consolidation
   - Implemented field mapping for renamed columns (`apartment_address` → `apartment_unit`, `phone_number` → `phone`)
   - Ensured foreign key relationships remained intact

2. **Migration Conflict Resolution**:
   - Resolved circular dependencies between deprecated and new models
   - Handled foreign key constraint violations during model removal
   - Implemented proper cleanup order to prevent data loss

### Lessons Learned

1. **Migration Strategy**:
   - Always create backup before major model changes
   - Use squashed migrations for complex consolidation operations
   - Test migration rollback scenarios before applying to production

2. **Testing Best Practices**:
   - Custom test runners are essential for complex database operations
   - Schema verification should be automated in the test pipeline
   - Deprecation tests prevent regression to removed models

3. **Data Recovery Planning**:
   - Field mapping documentation is crucial for data migration
   - SQL scripts provide fallback when Django migrations fail
   - Incremental consolidation reduces risk compared to bulk changes

These comprehensive improvements establish a robust foundation for future database schema changes and ensure data integrity throughout the application lifecycle.