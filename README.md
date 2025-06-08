# GroceryGo

A simple Django web application for online grocery shopping, allowing customers to browse products, add them to a cart, and place orders.

## Features

- **Product browsing and searching** with enhanced user experience
- **Product categorization** with detailed category pages and subcategory filtering
- **Interactive product variations selector** - modern UI for comparing product options without page navigation
- **Shopping cart management** with real-time updates and quantity controls
- **User account management** with profile and order history
- **Order placement and tracking** with comprehensive status updates
- **Enhanced Admin Dashboard** with business intelligence features:
  - Dark/Light theme toggle with persistent preferences
  - Sales trend analytics with interactive Chart.js visualizations
  - Order status distribution charts
  - Top products performance tracking
  - Low stock alerts and inventory monitoring
  - Real-time dashboard data via custom API endpoints
- **Consolidated Database Architecture** with improved data integrity:
  - Streamlined model structure with deprecated models fully removed
  - Enhanced Address management system replacing legacy ShippingAddress
  - Comprehensive OrderStatusHistory tracking
  - Advanced migration management with conflict resolution
- Admin interface for product, order, and user management

## Technology Stack

- Backend: Django
- Database: SQLite
- Frontend: Tailwind CSS with Shadcn/ui components
- Data Visualization: Chart.js
- Theme Management: CSS Custom Properties with LocalStorage persistence
- Testing: Custom Django test runner with migration-aware test infrastructure
- Database Management: Advanced migration tools and recovery utilities

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip
- Node.js and npm (for Tailwind CSS)

### Installation

1. Clone the repository:
```
git clone <repository-url>
cd grocerygo
```

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```
venv\Scripts\activate
```
- On macOS/Linux:
```
source venv/bin/activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Set up environment variables:
Create a `.env` file in the project root with:
```
DEBUG=true
SECRET_KEY=your-secret-key-here
```

6. Apply migrations and start the development environment:
```
./scripts/run-dev.sh --migrate
```

7. Create a superuser for admin access:
```
python manage.py createsuperuser
```

8. Access the application:
- Website: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

## Development Workflow

### Running the Application

We've created helpful scripts to streamline development:

```bash
# Start both Django and Tailwind CSS servers with one command
./scripts/run-dev.sh

# Apply migrations and start development environment
./scripts/run-dev.sh --migrate

# Use a custom port for the Django server
./scripts/run-dev.sh 8001

# Stop all development servers
./scripts/run-dev.sh stop
```

### Database Migrations

The project uses Django's migration system to manage database schema changes. Here's how migrations work in GroceryGo:

#### Applying Migrations

To apply all pending migrations:

```bash
# Option 1: Apply migrations using the run-dev.sh script
./scripts/run-dev.sh --migrate

# Option 2: Apply migrations directly with Django's manage.py
source venv/bin/activate && venv/bin/python manage.py migrate
```

#### Creating New Migrations

After modifying models (in `models.py` files), create migration files:

```bash
# Create migrations for a specific app
source venv/bin/activate && venv/bin/python manage.py makemigrations app_name

# Create migrations for all apps
source venv/bin/activate && venv/bin/python manage.py makemigrations
```

#### Migration Commands Reference

```bash
# Show migration status
python manage.py showmigrations

# Apply specific migration
python manage.py migrate app_name 0001_initial

# Roll back to a specific migration
python manage.py migrate app_name 0001_initial

# Apply migrations for a specific app
python manage.py migrate app_name
```

#### Migration Structure

The project maintains migrations in app-specific directories:
- `accounts/migrations/` - User account models
- `products/migrations/` - Product and category models
- `cart/migrations/` - Shopping cart models
- `orders/migrations/` - Order processing models

> **Important**: Always commit migration files to version control and apply migrations before running the application after pulling new changes from the repository.

### Admin Access

The application includes an enhanced Django admin interface with business intelligence features:

- **URL**: http://127.0.0.1:8000/admin/
- **Username**: grocerygoadmin
- **Password**: PassWord123!

#### Admin Dashboard Features

- **Business Intelligence Dashboard**: Interactive charts showing sales trends, order status distribution, and top-performing products
- **Dark/Light Theme Toggle**: Persistent theme switching across all admin pages
- **Low Stock Alerts**: Real-time monitoring of inventory levels with visual indicators
- **Enhanced UI**: Modern, responsive design using Tailwind CSS and Shadcn/ui components
- **API Endpoints**: Custom admin API for dashboard data (`/admin/api/sales-trend/`, `/admin/api/order-status/`, etc.)

> **Note**: If you need to create a new admin user, run:
> ```
> source venv/bin/activate && venv/bin/python manage.py createsuperuser
> ```

### Additional Scripts Documentation

For more details about the available scripts and their options, see [scripts/README.md](scripts/README.md).

## Project Structure

The project follows Django's MVT (Model-View-Template) architecture:

- `grocerygo/` - Main project directory
- `core/` - Core application with shared functionality
- `products/` - App for product and category management
- `accounts/` - App for user authentication and profiles
- `cart/` - App for shopping cart functionality
- `orders/` - App for order processing and management
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `theme/` - Tailwind CSS configuration
- `scripts/` - Development workflow scripts
- `docs/` - Project documentation
  - `models.md` - Complete database models documentation
  - `cart_debugging.md` - Solutions to common cart-related issues
  - `consolidation_plan.md` - Model consolidation implementation and lessons learned
  - `admin_management_guide.md` - Comprehensive admin interface documentation

For comprehensive documentation on all database models, see [docs/models.md](docs/models.md).
For information about cart implementation and troubleshooting, see [docs/cart_debugging.md](docs/cart_debugging.md).
For details on the model consolidation project and database architecture improvements, see [docs/consolidation_plan.md](docs/consolidation_plan.md).

## Available Pages and Routes

### Core Module
- `/` - Home page

### Authentication and User Account
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/register/` - New user registration
- `/accounts/profile/` - User profile (requires login)
- `/accounts/password-reset/` - Request password reset
- `/accounts/password-reset/done/` - Password reset email sent confirmation
- `/accounts/password-reset-confirm/<uidb64>/<token>/` - Set new password
- `/accounts/password-reset-complete/` - Password reset success confirmation
- `/accounts/password-change/` - Change password form (requires login)

### User Order Management 
- `/accounts/order-history/` - List of user's past orders
- `/accounts/order-detail/<order_id>/` - Detailed view of a specific order

### Product Management
- `/products/` - Browse all products
- `/products/product/<slug>/` - View detailed product information
- `/products/categories/` - Browse all product categories
- `/products/category/<slug>/` - View products in a specific category

### Shopping Cart 
- `/cart/add/<slug>/` - Add a product to cart
- `/cart/view/` - View cart contents
- `/cart/remove/<item_id>/` - Remove a product from cart

### Admin Interface
- `/admin/` - Enhanced Django administration interface with business intelligence dashboard
- `/admin/login/` - Standalone admin login page with theme toggle
- `/admin/api/sales-trend/<days>/` - Sales trend data API endpoint
- `/admin/api/order-status/` - Order status distribution API endpoint
- `/admin/api/top-products/` - Top products performance API endpoint
- `/admin/api/low-stock/` - Low stock alerts API endpoint

## Testing

### Django Unit Testing
The project includes a comprehensive Django test suite with advanced testing infrastructure:

```bash
# Run all Django tests with the custom test runner
python manage.py test

# Run tests for a specific app
python manage.py test orders

# Run tests with more verbose output
python manage.py test --verbosity=2

# Run specific test cases
python manage.py test orders.tests.AddressModelTest
```

#### Advanced Testing Features
- **Custom Test Runner**: `FixedSchemaTestRunner` handles database schema fixes during testing
- **Migration-Aware Testing**: `FixedSchemaTestCase` base class for tests that need proper database schema
- **Comprehensive Model Testing**: Full test coverage for Address, Checkout, and OrderStatusHistory models
- **Deprecation Verification**: Tests to ensure deprecated models are completely removed
- **Database Recovery Testing**: Test utilities for schema verification and data recovery scenarios

### Browser Testing
The project includes Selenium-based browser testing for automated UI verification:

```bash
# Run the browser test script
./scripts/run_browser_test.py

# Run specific test cases (homepage, login, product, cart)
./scripts/run_browser_test.py --test homepage

# Run with screenshots enabled
./scripts/run_browser_test.py --screenshots
```

### Database Testing and Recovery
Development utilities for testing database operations:

```bash
# Test database schema fixes
python fix_test_database.py

# Run simple connectivity tests
python orders/simple_test.py

# Test deprecated model removal
python orders/test_deprecated.py
```

## Scripts

The project includes several utility scripts:

1. **Development Scripts**
   - `run-dev.sh` - Start development environment
   - `import-products.sh` - Import product data into database

2. **Product Data Scripts**
   - `add_bakery_products.py` - Add bakery products to database
   - `add_pantry_products.py` - Add pantry products to database
   - `add_dairy_products.py` - Add dairy products to database
   - `add_beverage_products.py` - Add beverage products to database
   - `add_produce_products.py` - Add produce products to database
   - `add_all_products.py` - Run all product scripts in sequence
   - `add_product_images.py` - Fetch and add product images

3. **Testing Scripts**
   - `run_browser_test.py` - Run browser-based UI tests
   - `orders/simple_test.py` - Simple database connectivity tests
   - `orders/test_deprecated.py` - Verify deprecated models are removed
   - `test_admin_fixes.py` - Test admin interface functionality

4. **Database Management Scripts**
   - `fix_test_database.py` - Fix database schema issues during development
   - `fix_test_db_during_tests.py` - Handle schema fixes during test execution
   - `orders/test_utils.py` - Database testing utilities and helpers
   - `orders/test_runner.py` - Custom Django test runner with schema fixing

5. **SQL Scripts for Manual Database Operations**
   - `fix_database.sql` - Manual database schema fixes
   - `fix_address_table.sql` - Address table specific fixes
   - `create_orderstatushistory.sql` - OrderStatusHistory table creation
   - `insert_remaining_migrations.sql` - Manual migration record insertion

## License

This project is licensed under the MIT License - see the LICENSE file for details. 