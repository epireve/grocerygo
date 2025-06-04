#!/usr/bin/env python
import sys
import subprocess
from pathlib import Path


def run_script(script_path):
    """Run a Python script and print its output"""
    print(f"\n{'='*80}")
    print(f"Running {script_path}")
    print(f"{'='*80}\n")

    result = subprocess.run(
        [sys.executable, script_path], capture_output=True, text=True
    )

    print(result.stdout)

    if result.stderr:
        print(f"Error running {script_path}:")
        print(result.stderr)
        return False

    return True


def main():
    """Run all product creation scripts"""

    # Get the directory where this script is located
    scripts_dir = Path(__file__).parent

    # List of product scripts to run in order
    product_scripts = [
        "add_bakery_products.py",
        "add_pantry_products.py",
        "add_dairy_products.py",
        "add_beverage_products.py",
        "add_produce_products.py",
    ]

    success_count = 0
    failed_scripts = []

    # Run each script
    for script in product_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            print(f"Script not found: {script_path}")
            failed_scripts.append(script)
            continue

        success = run_script(script_path)
        if success:
            success_count += 1
        else:
            failed_scripts.append(script)

    # Print summary
    print(f"\n{'='*80}")
    print(f"Product Import Summary")
    print(f"{'='*80}")
    print(f"Successfully ran {success_count} out of {len(product_scripts)} scripts.")

    if failed_scripts:
        print(f"\nFailed scripts:")
        for script in failed_scripts:
            print(f"- {script}")
    else:
        print("\nAll scripts completed successfully!")

    print("\nDone!")


if __name__ == "__main__":
    main()
