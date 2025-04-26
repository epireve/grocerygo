# Development Scripts for GroceryGo

This directory contains useful scripts for development, deployment, and testing of the GroceryGo application.

## Available Scripts

### Development Workflow

- **run-dev.sh**: Start both the Django development server and Tailwind CSS watcher
  ```bash
  ./scripts/run-dev.sh [--no-tailwind] [--migrate] [--cleanup]
  ```
  Options:
  - `--no-tailwind`: Run only the Django server without Tailwind CSS
  - `--migrate`: Run migrations before starting servers
  - `--cleanup`: Kill any existing Django and Tailwind processes before starting

- **migrations.sh**: Helper script for database migration management
  ```bash
  # Apply all migrations
  ./scripts/migrations.sh apply
  
  # Create migrations for all apps
  ./scripts/migrations.sh make
  
  # Create migrations for specific app
  ./scripts/migrations.sh make app_name
  
  # Show migration status for all apps
  ./scripts/migrations.sh status
  
  # Revert migrations for an app to a specific version
  ./scripts/migrations.sh revert app_name 0001
  ```
  
  This script provides a convenient wrapper around Django's migration commands, making it easier to manage database schema changes across the project.

- **task-complete.sh**: Mark a task as done and push changes to GitHub
  ```bash
  ./scripts/task-complete.sh <task-id> "<commit-message>"
  ```
  Example:
  ```bash
  ./scripts/task-complete.sh 5 "Implement user registration"
  ```

### Testing

- **run_browser_test.py**: Run automated browser tests using Selenium
  ```bash
  # Ensure you have Selenium installed
  pip install selenium
  
  # Run all tests
  python scripts/run_browser_test.py
  
  # Run with custom URL
  python scripts/run_browser_test.py --url http://example.com
  
  # Run specific tests
  python scripts/run_browser_test.py --tests homepage,cart
  
  # Run login test with credentials
  python scripts/run_browser_test.py --tests login --username admin --password password
  
  # Run with screenshots enabled
  python scripts/run_browser_test.py --screenshots
  ```
  
  Available test modules:
  - `homepage`: Tests that the homepage loads with categories and featured products
  - `login`: Tests the login functionality (requires username and password)
  - `product`: Tests that product detail pages load correctly
  - `cart`: Tests adding a product to the cart and viewing the cart

  The script will save screenshots in a `screenshots` directory as it runs.

### Data Management

- **add_all_products.py**: Run all product scripts in sequence
  ```bash
  python scripts/add_all_products.py
  ```

- **import-products.sh**: Shell script to activate the environment and run all product scripts
  ```bash
  ./scripts/import-products.sh
  ```

- **Category-specific Product Scripts**:
  - **add_bakery_products.py**: Add bakery products to the database
  - **add_pantry_products.py**: Add pantry products to the database
  - **add_dairy_products.py**: Add dairy products to the database
  - **add_beverage_products.py**: Add beverage products to the database
  - **add_produce_products.py**: Add produce products to the database
  
  Each script can be run individually:
  ```bash
  python scripts/add_bakery_products.py
  ```

- **add_product_images.py**: Fetch and add product images using Serper.dev API
  ```bash
  # Ensure you have the Serper.dev API key in your .env file
  # SERPER_API_KEY=your_key_here
  
  python scripts/add_product_images.py
  
  # Options:
  # --limit N: Process only N products
  # --force: Replace existing images
  # --category SLUG: Process only products in a specific category
  ```
  
  This script:
  - Connects to Serper.dev API to search for product images
  - Downloads and optimizes images for products and categories
  - Respects rate limits and handles errors gracefully
  - Skips products that already have images (unless --force is used)
  - Resizes images to fit the website's layout requirements

## Usage Notes

- Scripts should be run from the project root directory
- Shell scripts may need executable permissions:
  ```bash
  chmod +x scripts/*.sh
  ```
- Python scripts should be run with the project's virtual environment activated:
  ```bash
  source venv/bin/activate
  python scripts/script_name.py
  ```

## Troubleshooting

If you encounter issues with the scripts:

1. Ensure your virtual environment is activated
2. Check that all dependencies are installed
3. Verify permissions on shell scripts
4. For Selenium tests, ensure Chrome is installed and the webdriver is compatible

For browser tests specifically:
- If tests fail, check the screenshots for visual clues on what went wrong
- Make sure your CSS selectors in the site match what the tests are looking for

For product image scripts:
- Check your Serper.dev API key is valid and has sufficient quota
- If images aren't downloaded properly, check your network connection
- Ensure your media directory is writable by the application 