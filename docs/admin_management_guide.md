# GroceryGo Admin & Management Guide

This document provides a comprehensive overview of the GroceryGo admin interface, including available models, custom actions, and management capabilities.

## Table of Contents

1. [Accessing the Admin Interface](#accessing-the-admin-interface)
2. [Admin Models Overview](#admin-models-overview)
3. [Product Management](#product-management)
4. [Category Management](#category-management)
5. [Order Management](#order-management)
6. [User & Profile Management](#user--profile-management)
7. [Address Management](#address-management)
8. [CSV Export Functionality](#csv-export-functionality)
9. [Best Practices](#best-practices)

## Accessing the Admin Interface

To access the admin interface:

1. Navigate to `/admin/` on your GroceryGo installation
2. Log in with administrator credentials (staff or superuser account)
3. You will be presented with the main admin dashboard showing all available models

## Admin Models Overview

The GroceryGo admin interface provides management for the following models:

| Model | Function | Key Actions |
|-------|----------|------------|
| Products | Manage product catalog | Discount management, feature products, inventory control |
| Categories | Organize product hierarchy | Toggle active status |
| Orders | Process customer orders | Status updates, payment tracking |
| Order Items | View order details | View details of items in orders |
| Users | Manage user accounts | User information export |
| User Profiles | Manage extended user data | Profile data management |
| Addresses | Manage user addresses | Address information export |
| Order Status History | Track order status changes | View order lifecycle |

## Product Management

The Product admin interface offers robust management capabilities for your product catalog.

### Key Features

- **Product List View**: Displays product name, price, discount price, category, active status, featured status, and creation date
- **Filtering**: Filter products by active status, featured status, and category
- **Search**: Search by name, slug, or description
- **Inline Editing**: Directly edit active and featured status from the list view
- **Variant Management**: Add and edit product variants through inline forms (for parent products)

### Custom Actions

1. **Mark as Featured**
   - Select products and choose "Mark selected products as featured"
   - Products will appear in featured sections throughout the site

2. **Mark as Not Featured**
   - Select products and choose "Mark selected products as not featured"
   - Removes products from featured sections

3. **Set Stock to Zero**
   - Select products and choose "Set stock to zero"
   - Quickly mark products as out of stock

4. **Apply Percentage Discount**
   - Select products and choose "Apply percentage discount"
   - Enter a percentage (1-99%)
   - Discount will be calculated and applied to selected products
   - Original and discounted prices will be displayed

5. **Clear Discount Prices**
   - Select products and choose "Clear discount prices"
   - Removes all discounts from selected products

6. **Export as CSV**
   - Select products and choose "Export selected products as CSV"
   - Download a CSV file containing all product data

## Category Management

Categories help organize your product catalog in a hierarchical structure.

### Key Features

- **Category List View**: Displays name, slug, parent category, active status, and creation date
- **Filtering**: Filter by active status and parent category
- **Search**: Search by name, slug, or description
- **Inline Editing**: Directly edit active status from the list view

### Custom Actions

1. **Toggle Active Status**
   - Select categories and choose "Toggle active status for selected categories"
   - Inactive categories become active and vice versa
   - Provides feedback on how many categories were activated/deactivated

## Order Management

The Order admin interface provides comprehensive tools for processing customer orders.

### Key Features

- **Order List View**: Displays order number, user, status, payment status, payment method, item count, total, and creation date
- **Filtering**: Filter by order status, payment status, payment method, and date
- **Search**: Search by order number, username, or email
- **Related Data**: View order items and status history through inline forms
- **Date Hierarchy**: Navigate orders by date hierarchy

### Custom Actions

1. **Order Status Management**
   - **Mark as Processing**: Updates selected orders to "processing" status
   - **Mark as Shipped**: Updates selected orders to "shipped" status
   - **Mark as Delivered**: Updates selected orders to "delivered" status
   - **Mark as Cancelled**: Updates selected orders to "cancelled" status
   - Each status change is logged in the OrderStatusHistory

2. **Payment Status Management**
   - **Mark as Paid**: Sets payment status to paid for selected orders
   - **Mark as Unpaid**: Sets payment status to unpaid for selected orders
   - Payment status changes are logged in the OrderStatusHistory

3. **Export Orders as CSV**
   - Select orders and choose "Export selected orders as CSV"
   - Downloads a CSV file with order data including order items as a formatted string

## User & Profile Management

GroceryGo provides enhanced user management capabilities by extending Django's built-in user model.

### Key Features

- **User List View**: Displays username, email, name, staff status, active status, and phone number
- **Filtering**: Standard user filters plus terms acceptance
- **Search**: Search by username, email, name, or phone number
- **Inline Editing**: Edit user profile data directly within user edit form

### Custom Actions

1. **Export Users as CSV**
   - Select users and choose "Export selected users as CSV"
   - Downloads a CSV file with user data including profile information

2. **Profile Management**
   - Stand-alone management of UserProfile model
   - Export profiles as CSV with user information

## Address Management

Manage customer shipping and billing addresses separately.

### Key Features

- **Address List View**: Displays user, full name, address type, city, and default status
- **Filtering**: Filter by address type, default status, city, state, and country
- **Search**: Search by username, full name, street address, or city
- **Date Hierarchy**: Navigate addresses by creation date

### Custom Actions

1. **Export Addresses as CSV**
   - Select addresses and choose "Export selected addresses as CSV"
   - Downloads a CSV file with all address data

## CSV Export Functionality

CSV export functionality is available for most admin models to facilitate data analysis and reporting.

### Available Exports

- **Products**: All product fields
- **Users**: User fields plus profile data
- **Profiles**: Profile fields plus username and email
- **Orders**: Order fields plus formatted list of items
- **Addresses**: All address fields

### Usage

1. Select the items you wish to export
2. Select the appropriate export action from the action dropdown
3. Click "Go" to generate and download the CSV file

## Best Practices

1. **Regular Order Processing**
   - Process orders daily using the status management actions
   - Keep customers informed by updating order status promptly

2. **Inventory Management**
   - Regularly review product stock levels
   - Use "Set stock to zero" for out-of-stock items

3. **Promotions Management**
   - Use the discount management feature for time-limited sales
   - Feature seasonal or promotional products using the "Mark as featured" action

4. **Data Analysis**
   - Export data to CSV for detailed analysis in spreadsheet software
   - Track order patterns and user behavior

5. **Security**
   - Only grant admin access to trusted staff members
   - All admin actions enforce staff permission checks

6. **Order History**
   - Review OrderStatusHistory to track the lifecycle of orders
   - Useful for resolving customer inquiries

---

This documentation covers the main administrative capabilities of GroceryGo. Contact the development team for additional assistance or custom administrative needs. 