import unittest
from calculator import FF13Calculator

class CalculatorTests(unittest.TestCase):
    def test_calculate_number_required(self):
        # Create a Calculator instance
        calculator = FF13Calculator()

        # Set the required values for testing
        calculator.exp_req_before_star = 10000
        calculator.multiplier_combo_box.currentText = lambda: "2"  # Mocking the currentText method
        component_exp = 500

        # Calculate the number required
        number_required = calculator.calculate_number_required(component_exp)

        # Assert the result
        self.assertEqual(number_required, 10.0)

    def test_calcul_exp_total(self):
        # Create a Calculator instance
        calculator = FF13Calculator()

        # Set the required values for testing
        level = 5
        exp = 100
        exp_initial = 50
        exp_increment = 10

        # Calculate the total experience
        exp_total = calculator.calcul_exp_total(level, exp, exp_initial, exp_increment)

        # Assert the result
        self.assertEqual(exp_total, 450)

if __name__ == "__main__":
    unittest.main()