# Changelog

All notable changes to the GroceryGo project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-04-26

### Fixed

1. Checkout Address Form Validation Error
   - Fixed the "on" value must be either True or False validation error that occurred when saving a shipping address during checkout
   - Added proper checkbox value conversion to boolean when processing the save_address field

2. Cart Count Update in Navbar
   - Fixed issue where changing quantities in the cart view wasn't updating the cart count in the navbar
   - Updated the updateCartIcon JavaScript function to target the correct element ID (cart-counter instead of cart-count)
   - Added proper visibility toggling for the cart counter badge based on item count

3. URL Namespace Resolution
   - Fixed NoReverseMatch errors related to URL namespace issues in templates
   - Updated product-related URLs in templates to use proper namespace 'products:product_list'
   - Improved URL structure consistency between namespaced and top-level URL patterns
   - Ensured home page and navigation elements correctly reference product list views

## [0.0.9] - 2025-04-26

### Added

1. Enhanced Admin Interface
   - Implemented custom admin actions for all models with permission checks
   - Added product discount management with percentage-based discounts
   - Created custom CSV export functionality for all major models
   - Added toggle active status for categories
   - Implemented payment status management for orders
   - Added order status history tracking for comprehensive order lifecycle management

2. Admin Documentation
   - Created comprehensive admin management guide in `docs/admin_management_guide.md`
   - Documented all custom admin actions and their usage
   - Added best practices for store management
   - Included CSV export functionality documentation
   - Provided detailed explanations of product, order, and user management capabilities

## [0.0.8] - 2025-04-26

### Added

1. Cart Quantity Management
   - Added quantity update feature in cart view using dropdown select
   - Implemented new endpoint to handle quantity updates
   - Improved user experience with real-time updates of cart quantities and subtotals

### Fixed

1. Cart Runtime Error Handling
   - Fixed RuntimeError in cart view when products no longer exist (dictionary changed size during iteration)
   - Added proper error handling for cart quantity updates
   - Implemented defensive programming patterns to prevent similar issues

## [0.0.7] - 2025-04-26

### Fixed

1. Cart View Runtime Error
   - Fixed a RuntimeError ("dictionary changed size during iteration") in the cart view
   - Implemented a safer approach for handling non-existent products in the cart
   - Added safety checks before removing items from session cart
   - Created detailed documentation in `docs/cart_debugging.md` explaining the issue and solution

### Added

1. Cart Debugging Documentation
   - Added comprehensive documentation on cart-related bugs and their solutions
   - Explained common runtime errors when manipulating cart session data
   - Provided best practices for cart implementation and session handling

## [0.0.6] - 2025-04-26

### Added

1. Model Documentation
   - Added comprehensive documentation for all database models in `docs/models.md`
   - Documented relationships between models
   - Included detailed field descriptions, methods, properties, and meta options

2. Database Migration Management
   - Created `migrations.sh` helper script for streamlined database migration workflow
   - Updated README.md with detailed migration documentation
   - Added documentation for migration commands in scripts/README.md

### Fixed

1. Cart Namespace Error
   - Fixed 'cart' namespace not registered error in URL configuration
   - Updated URL patterns to properly include the cart app URLs

## [0.0.5] - 2025-05-01

### Fixed

1. Navigation & UI Improvements
   - Fixed duplicate cart links in the site navigation
   - Ensured mobile menu cart link points to the correct URL
   - Improved overall UI consistency in navigation elements

## [0.0.4] - 2025-04-26

### Fixed

1. Cart URL Handling
   - Updated cart URLs to use product slugs instead of IDs for better SEO and more user-friendly URLs
   - Fixed `cart/urls.py` to use `<slug:slug>` pattern instead of `<int:product_id>` in URL routes
   - Modified `cart/views.py` to handle slug-based lookups instead of ID-based lookups
   - Updated templates to use the new URL pattern with slugs
   - Resolved "cart is not a registered namespace" error that occurred when accessing product details

### Added

1. Product Image Management
   - Added script for automated product image retrieval and processing
   - Implemented image resizing and optimization for better performance
   - Integrated with Serper.dev API for retrieving relevant product images

2. Selenium-based Browser Testing
   - Added `run_browser_test.py` for automated UI testing
   - Implemented test cases for homepage, login, product pages, and cart functionality
   - Configured screenshot capture for visual debugging

## [0.0.3] - 2025-04-26

### Added

1. Product Browsing Functionality
   - Created product list, detail, and category views
   - Implemented product browsing templates:
     - `product_list.html` - Browse all products with category filters
     - `product_detail.html` - Detailed product information with add to cart form
     - `category_detail.html` - Browse products by category with subcategory navigation

2. Order Management
   - Added proper order history and detail routes
   - Implemented order cancellation functionality
   - Connected order templates to views

3. Initial Data
   - Created script for populating product categories
   - Fixed script environment setup for database operations

4. Database Migrations
   - Created and applied migrations for user profiles
   - Applied initial database schema 

## [0.0.2] - 2025-04-26

### Added

1. Authentication Templates
   - Created `register.html` for user registration
   - Created/enhanced `login.html` for user login
   - Implemented password reset flow templates:
     - `password_reset.html` - Form to request password reset
     - `password_reset_done.html` - Confirmation page after request
     - `password_reset_confirm.html` - Form to set new password
     - `password_reset_complete.html` - Reset success page
     - `password_reset_email.html` - Email template for reset links
     - `password_reset_subject.txt` - Email subject line
   - Added `password_change.html` for authenticated users

2. User Account Templates
   - Implemented `profile.html` for user profile management
   - Added order management templates:
     - `order_history.html` - For viewing past orders
     - `order_detail.html` - For detailed order information

3. Documentation
   - Updated README with available pages and routes by module
   - Added comprehensive Tailwind CSS styling to all templates
   - Ensured consistent design language across authentication flows 

## [0.0.1] - 2025-04-26

### Added

1. Project initialization
   - Created virtual environment and installed dependencies
   - Initialized Django project structure
   - Set up directory structure for templates, static files, and media

2. Django configuration
   - Configured Django settings
   - Set up static and media files configuration
   - Added core app to INSTALLED_APPS

3. Database setup
   - Configured SQLite database
   - Applied initial migrations
   - Created superuser for admin access

4. Tailwind CSS integration
   - Set up Tailwind CSS for styling
   - Configured Tailwind CSS to work with Django

5. URL configuration
   - Set up URL routing in core/urls.py
   - Updated project URLconf to include core app URLs
   - Added media and static file URL configurations

6. Basic templates
   - Created base.html template with Tailwind CSS
   - Created home.html template that extends base.html

7. Development tools
   - Created run-dev.sh script to start both Django and Tailwind CSS servers
   - Created task-complete.sh script for task completion and GitHub push
   - Added documentation for development workflow 

## [Unreleased]

### Added

### Fixed