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
- `grocery_go/` - Tailwind CSS configuration
- `scripts/` - Development workflow scripts

## License

This project is licensed under the MIT License - see the LICENSE file for details. 