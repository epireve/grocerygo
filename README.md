# GroceryGo

A simple Django web application for online grocery shopping, allowing customers to browse products, add them to a cart, and place orders.

## Features

- Product browsing and searching
- Product categorization
- Shopping cart management
- User account management
- Order placement and tracking
- Admin interface for product, order, and user management

## Technology Stack

- Backend: Django
- Database: SQLite
- Frontend: Tailwind CSS with Shadcn/ui components

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

The application includes a Django admin interface for managing content:

- **URL**: http://127.0.0.1:8000/admin/
- **Username**: grocerygoadmin
- **Password**: PassWord123!

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
- `/admin/` - Django administration interface for site management

## Testing

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

## License

This project is licensed under the MIT License - see the LICENSE file for details. 