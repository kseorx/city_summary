import unittest
from processing.preprocessing import apply_rules

class TestPreprocessing(unittest.TestCase):
    def test_warm_clothes_true(self):
        summary = {"weather": {"temp_c": -5}, "rates": {"rate_to_rub": 50}}
        result = apply_rules(summary)
        self.assertTrue(result["weather"]["warm_clothes"])
        self.assertFalse(result["rates"]["expensive"])

    def test_expensive_true(self):
        summary = {"weather": {"temp_c": 15}, "rates": {"rate_to_rub": 105}}
        result = apply_rules(summary)
        self.assertFalse(result["weather"]["warm_clothes"])
        self.assertTrue(result["rates"]["expensive"])

if __name__ == "__main__":
    unittest.main()