#!/bin/bash

# Script to import products into the GroceryGo database
# This script runs the add_all_products.py script

# Find the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate the virtual environment
echo "Activating virtual environment..."
source "$PROJECT_DIR/venv/bin/activate" || { echo "Failed to activate virtual environment. Make sure it exists."; exit 1; }

# Run the all products script
echo "Starting product import..."
python "$SCRIPT_DIR/add_all_products.py"

# Check if the script succeeded
if [ $? -eq 0 ]; then
    echo "Product import completed successfully!"
else
    echo "Product import encountered errors. Check the output above for details."
    exit 1
fi

echo "Done!"
exit 0 