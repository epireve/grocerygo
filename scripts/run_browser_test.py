from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import argparse
import sys
import os


def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode by default
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # Create a new Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def test_homepage(driver, base_url):
    """Test the homepage loads correctly with key elements."""
    print("\n🔍 Testing Homepage...")
    driver.get(base_url)

    # Wait for title to contain GroceryGo
    try:
        WebDriverWait(driver, 10).until(EC.title_contains("GroceryGo"))
        print("✅ Homepage title loaded correctly")
    except TimeoutException:
        print("❌ Homepage title not found or timeout")
        return False

    # Check for featured products section
    try:
        featured_products = driver.find_element(By.CSS_SELECTOR, ".featured-products")
        print(
            f"✅ Featured products section found with {len(featured_products.find_elements(By.CSS_SELECTOR, '.product-card'))} products"
        )
    except:
        print("❌ Featured products section not found")
        return False

    # Check for categories section
    try:
        categories = driver.find_element(By.CSS_SELECTOR, ".categories-section")
        print(
            f"✅ Categories section found with {len(categories.find_elements(By.CSS_SELECTOR, '.category-card'))} categories"
        )
    except:
        print("❌ Categories section not found")
        return False

    return True


def test_login(driver, base_url, username, password):
    """Test the login functionality."""
    if not username or not password:
        print("\n⚠️ Skipping login test - no credentials provided")
        return True

    print("\n🔍 Testing Login...")
    driver.get(f"{base_url}/accounts/login/")

    try:
        # Fill in login form
        driver.find_element(By.ID, "id_username").send_keys(username)
        driver.find_element(By.ID, "id_password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for login to complete - check for user menu or welcome element
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".user-menu, .welcome-user")
            )
        )
        print("✅ Login successful")
        return True
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return False


def test_product_page(driver, base_url):
    """Test a product detail page loads correctly."""
    print("\n🔍 Testing Product Detail Page...")

    try:
        # First navigate to categories to find a product
        driver.get(f"{base_url}/categories/")

        # Click on the first category
        categories = driver.find_elements(By.CSS_SELECTOR, ".category-card a")
        if not categories:
            print("❌ No categories found to test product pages")
            return False

        categories[0].click()

        # Now click on the first product
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, ".product-card a")
        if not products:
            print("❌ No products found in the category")
            return False

        products[0].click()

        # Check product detail page elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-detail"))
        )

        # Check for product title, price, and add to cart button
        assert driver.find_element(
            By.CSS_SELECTOR, ".product-title"
        ), "Product title not found"
        assert driver.find_element(
            By.CSS_SELECTOR, ".product-price"
        ), "Product price not found"
        assert driver.find_element(
            By.CSS_SELECTOR, "button.add-to-cart"
        ), "Add to cart button not found"

        print("✅ Product detail page loads correctly")
        return True
    except Exception as e:
        print(f"❌ Product page test failed: {str(e)}")
        return False


def test_cart(driver, base_url):
    """Test adding a product to cart and viewing the cart."""
    print("\n🔍 Testing Shopping Cart...")

    try:
        # Navigate to a product page first
        driver.get(f"{base_url}/categories/")
        categories = driver.find_elements(By.CSS_SELECTOR, ".category-card a")
        if not categories:
            print("❌ No categories found to test cart")
            return False

        categories[0].click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, ".product-card a")
        if not products:
            print("❌ No products found to test cart")
            return False

        products[0].click()

        # Add the product to cart
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.add-to-cart"))
        )
        add_to_cart_btn = driver.find_element(By.CSS_SELECTOR, "button.add-to-cart")
        product_name = driver.find_element(By.CSS_SELECTOR, ".product-title").text
        add_to_cart_btn.click()

        # Wait for cart confirmation or notification
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".cart-notification, .alert-success")
            )
        )

        # Go to cart page
        driver.get(f"{base_url}/cart/")

        # Check if product is in cart
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-items"))
        )
        cart_items = driver.find_elements(By.CSS_SELECTOR, ".cart-item")

        if not cart_items:
            print("❌ Cart is empty after adding product")
            return False

        print(f"✅ Product '{product_name}' successfully added to cart")
        return True
    except Exception as e:
        print(f"❌ Cart test failed: {str(e)}")
        return False


def take_screenshot(driver, name):
    """Take a screenshot and save it to the screenshots directory."""
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{screenshots_dir}/{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"📸 Screenshot saved to {filename}")


def run_tests(base_url, username=None, password=None, tests=None):
    """Run all tests and return True if all passed."""
    driver = setup_driver()

    try:
        print(f"\n🚀 Starting tests on {base_url}")

        all_tests = {
            "homepage": lambda: test_homepage(driver, base_url),
            "login": lambda: test_login(driver, base_url, username, password),
            "product": lambda: test_product_page(driver, base_url),
            "cart": lambda: test_cart(driver, base_url),
        }

        # Determine which tests to run
        if tests:
            tests_to_run = {
                name: func for name, func in all_tests.items() if name in tests
            }
        else:
            tests_to_run = all_tests

        if not tests_to_run:
            print("⚠️ No valid tests selected")
            return False

        results = {}
        for name, test_func in tests_to_run.items():
            try:
                results[name] = test_func()
                # Take a screenshot after each test
                take_screenshot(driver, name)
            except Exception as e:
                print(f"❌ Test '{name}' failed with error: {str(e)}")
                results[name] = False
                take_screenshot(driver, f"{name}_error")

        # Print summary
        print("\n📊 Test Results Summary:")
        for name, result in results.items():
            print(f"{'✅' if result else '❌'} {name.capitalize()}")

        return all(results.values())
    finally:
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run browser tests for GroceryGo website"
    )
    parser.add_argument(
        "--url", default="http://127.0.0.1:8000", help="Base URL of the website"
    )
    parser.add_argument("--username", help="Username for login test")
    parser.add_argument("--password", help="Password for login test")
    parser.add_argument(
        "--tests",
        help="Comma-separated list of tests to run (homepage,login,product,cart)",
    )

    args = parser.parse_args()

    # Parse specific tests if provided
    specific_tests = args.tests.split(",") if args.tests else None

    # Run the tests
    success = run_tests(
        base_url=args.url,
        username=args.username,
        password=args.password,
        tests=specific_tests,
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)
