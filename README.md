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
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEBUG=true
SECRET_KEY=your-secret-key-here
```

6. Apply migrations:
```
python manage.py migrate
```

7. Create a superuser for admin access:
```
python manage.py createsuperuser
```

8. Run the development server:
```
python manage.py runserver
```

9. Access the application:
- Website: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

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

## License

This project is licensed under the MIT License - see the LICENSE file for details. 