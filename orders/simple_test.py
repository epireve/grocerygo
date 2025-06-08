import os
import unittest
import re


class SimpleDeprecatedModelsTest(unittest.TestCase):
    """Tests to ensure deprecated models are truly removed by checking source files"""

    def test_deprecated_models_do_not_exist(self):
        """Test that the deprecated models are not defined in the models.py file"""
        # Path to the models.py file
        models_file = os.path.join(os.path.dirname(__file__), "models.py")

        # Read the content of the models.py file
        with open(models_file, "r") as f:
            content = f.read()

        # Define a regex pattern to find class definitions
        pattern = r"class\s+(Order|OrderItem|ShippingAddress)\s*\("

        # Search for the deprecated model class definitions
        matches = re.findall(pattern, content)

        # Print found class definitions if any
        if matches:
            print("\nFound deprecated model definitions:")
            for match in matches:
                print(f"- {match}")
        else:
            print("\nNo deprecated model definitions found.")

        # Check that no deprecated models are defined
        self.assertEqual(
            len(matches), 0, f"Found deprecated models: {', '.join(matches)}"
        )

        # Print the actual model classes defined (for reference)
        class_pattern = r"class\s+([A-Za-z0-9_]+)\s*\("
        all_classes = re.findall(class_pattern, content)
        print("\nActual model classes defined:")
        for cls in all_classes:
            print(f"- {cls}")


if __name__ == "__main__":
    unittest.main()
