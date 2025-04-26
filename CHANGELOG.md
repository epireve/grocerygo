# Changelog

All notable changes to the GroceryGo project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.0.2] - 2025-04-27

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

## [0.0.3] - 2025-04-28

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