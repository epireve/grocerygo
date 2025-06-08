# Database Consolidation Plan

## Current Database State Analysis
*Timestamp: June 8, 2025*

### Record Counts

| Table | Count | Status |
|-------|-------|--------|
| Address | 2 | Active |
| ShippingAddress | 2 | Redundant |
| Order | 0 | Unused |
| OrderItem | 0 | Unused |
| Checkout | 21 | Active |
| CheckoutItem | 20 | Active |

### All Database Tables
```
auth_group_permissions
auth_user_groups
auth_user_user_permissions
auth_permission
auth_group
auth_user
products_category
accounts_userprofile
products_product
cart_cart
cart_cartitem
orders_address
orders_order
orders_orderitem
orders_orderstatushistory
orders_checkoutitem
orders_shippingaddress
orders_checkout
cart_coupon
```

### Foreign Key Relationships

#### Order Model
- Order -> shipping_address (Address): 0 records
- Order -> billing_address (Address): 0 records

#### Checkout Model
- Checkout -> shipping_address (Address): 21 records

#### Item Models
- OrderItem -> Order: 0 records
- CheckoutItem -> Checkout: 20 records

## Active vs. Dormant Models

### Active Models
- **Address**: Used by all Checkout instances (21 records pointing to it)
- **Checkout**: Contains 21 records
- **CheckoutItem**: Contains 20 records

### Dormant/Redundant Models
- **ShippingAddress**: Appears to be redundant as the system is using Address model instead (migration 0004 copied data from ShippingAddress to Address)
- **Order**: No records, not currently in use
- **OrderItem**: No records, not currently in use

## Migration History Analysis

Based on examining migration files:

1. **Migration 0002**: Added Checkout, CheckoutItem, and ShippingAddress models
2. **Migration 0003**: Renamed phone_number to phone in Address, set Checkout.shipping_address to allow NULL values temporarily
3. **Migration 0004**: Data migration to copy from ShippingAddress to Address model, maintaining relationships

## Consolidation Recommendations

### Models to Keep
1. **Address** over ShippingAddress
   - Rationale: All Checkout records (21) reference the Address model
   - Migration 0004 already migrated data from ShippingAddress to Address
   - Address model has a more flexible structure with address_type field

2. **Checkout/CheckoutItem** over Order/OrderItem
   - Rationale: Checkout/CheckoutItem models are actively used (21/20 records)
   - Order/OrderItem models have no data (0 records)

### Recommended Migration Strategy

1. **Address Consolidation**:
   - Keep the Address model
   - Remove the ShippingAddress model after confirming all data has been migrated
   - Verify no unexpected side effects for existing Checkout records

2. **Checkout/Order Consolidation**:
   - Option 1: Keep both models for now, but standardize on Checkout for new orders
   - Option 2: Rename Checkout to Order (requires complex migration)
   - Option 3: Remove Order/OrderItem models entirely as they're unused

3. **Field Standardization**:
   - Ensure consistent field naming across models (e.g., apartment_address vs apartment_unit)
   - Standardize on common choices for status fields, payment methods, etc.

## Implementation Plan

1. Create a database backup (COMPLETED: db_backup_20250608_before_consolidation.sqlite3)
2. Create data verification scripts to ensure integrity after migrations
3. Develop and test migrations in a staging environment
4. Update documentation to reflect the consolidated model structure
5. Schedule the migration during low-traffic periods

## Risks and Mitigations

1. **Data Loss Risk**: 
   - Mitigation: Full database backup created, plus verification scripts

2. **Application Errors**:
   - Mitigation: Thorough testing in staging environment before production deployment

3. **Inconsistent State**:
   - Mitigation: Transactions to ensure migrations complete fully or not at all

## Migration Fix Implementation (June 8, 2025)

### Issues Identified
1. Migration `0008_remove_deprecated_models.py` was not correctly applied - missing checkout_id column in OrderStatusHistory
2. Migration `0009_rename_apartment_address_to_apartment_unit.py` was failing because the apartment_unit column didn't exist

### Fix Strategy
1. Created migration `0010_fix_migration_errors.py` to:
   - Add apartment_unit column to Address model
   - Add checkout foreign key to OrderStatusHistory model
2. Encountered migration conflict due to parallel migration paths
3. Created merged migration `0011_merge_20250608_0017.py` to resolve conflicts
4. Squashed migrations 0007-0011 for cleaner migration history

### Implementation Results
1. Successfully applied squashed migration
2. Verified model structure and relationships in the database
3. Confirmed all admin interfaces work correctly:
   - Address admin with apartment_unit field
   - Checkout admin with related checkout items
   - OrderStatusHistory admin with checkout relationship
4. Created comprehensive unit tests for:
   - Address model functionality (including apartment_unit field)
   - OrderStatusHistory model and relationship to Checkout
   - Verification that deprecated models are truly removed

### Final Status
The code consolidation project is now complete with all acceptance criteria met:
1. ✅ Removed deprecated models (Order, OrderItem, ShippingAddress)
2. ✅ Renamed apartment_address to apartment_unit for consistency
3. ✅ Updated OrderStatusHistory to reference Checkout instead of Order
4. ✅ Added comprehensive unit tests
5. ✅ Updated documentation to reflect final model structure
6. ✅ All admin interfaces and functionality working correctly

### Lessons Learned
1. Complex migrations should be thoroughly tested on backup databases before production
2. When renaming fields that are already in use, ensure proper migration order
3. Squashing migrations can help resolve conflicts and create a cleaner history
4. Comprehensive tests are essential to verify migrations worked correctly