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
  ```
  
  Available test modules:
  - `homepage`: Tests that the homepage loads with categories and featured products
  - `login`: Tests the login functionality (requires username and password)
  - `product`: Tests that product detail pages load correctly
  - `cart`: Tests adding a product to the cart and viewing the cart

  The script will save screenshots in a `screenshots` directory as it runs.

### Data Management

- **add_bakery_products.py**: Add bakery products to the database
  ```bash
  python scripts/add_bakery_products.py
  ```

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