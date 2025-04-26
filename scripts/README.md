# GroceryGo Development Scripts

This directory contains helpful scripts for developing the GroceryGo application.

## Development Workflow

### Starting the Development Environment

Run the development environment (Django + Tailwind CSS) with one command:

```bash
./scripts/run-dev.sh
```

This will:
1. Start the Tailwind CSS watcher
2. Start the Django development server on port 8000
3. Allow you to stop both with a single Ctrl+C

### Options

- **Custom port**: `./scripts/run-dev.sh 8001` - Run Django on port 8001
- **Apply migrations**: `./scripts/run-dev.sh --migrate` - Apply migrations before starting
- **Stop servers**: `./scripts/run-dev.sh stop` - Stop all running servers

### Task Completion

When you complete a task, use:

```bash
./scripts/task-complete.sh <task-id> "Description of what was done"
```

For example:
```bash
./scripts/task-complete.sh 5 "Implemented Tailwind CSS setup"
```

This will:
1. Mark the task as "done" in your task management system
2. Add all changes to Git
3. Create a commit with a descriptive message
4. Push to your GitHub repository

## Product Data Scripts

The `scripts` directory includes several Python scripts to populate the database with product data. These scripts create categories and products with variants for different sections of the store.

### Available Product Scripts

- `add_bakery_products.py` - Adds bakery products (bread, pastries, cakes, etc.)
- `add_pantry_products.py` - Adds pantry items (rice, pasta, canned goods, oils, etc.)
- `add_dairy_products.py` - Adds dairy products (milk, cheese, yogurt, butter, etc.)
- `add_beverage_products.py` - Adds beverages (soft drinks, juices, coffee, tea, water, etc.)
- `add_produce_products.py` - Adds produce (fruits, vegetables, organic produce, etc.)
- `add_all_products.py` - Runs all the above scripts in sequence

### Running Product Scripts

The easiest way to import all products is to use the provided shell script:

```bash
./scripts/import-products.sh
```

This script will:
1. Activate the virtual environment
2. Run all product scripts in sequence
3. Provide a summary of the import process

Alternatively, you can run individual scripts:

```bash
# Make sure to activate your virtual environment first
source venv/bin/activate

# Run a specific product script
python scripts/add_bakery_products.py

# Or run all product scripts at once
python scripts/add_all_products.py
```

Each script will create appropriate categories if they don't exist, then add products with variants to those categories. Some products will be marked as "featured" to appear on the home page.

## Troubleshooting

If you're having issues with the development scripts:

1. Make sure the scripts are executable (`chmod +x scripts/*.sh`)
2. Check if there are any orphaned processes from previous runs
3. Make sure your virtual environment is properly set up 

For the product scripts, ensure:
1. Your database migrations have been applied
2. Your virtual environment has all dependencies installed
3. If you see import errors, make sure Django is configured correctly 