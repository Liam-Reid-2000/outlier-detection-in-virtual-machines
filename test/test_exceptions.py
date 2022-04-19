import unittest
from app_helper_scripts.app_exceptions import *

class app_exceptions_tests(unittest.TestCase):

    def test_throws_invalid_percentage_error(self):
        with self.assertRaises(InvalidPercentageFloatValueError):
            raise(InvalidPercentageFloatValueError(-3))
    
    def test_throws_invalid_calculation_input_value_error(self):
        with self.assertRaises(InvalidValueForCalculationError):
            raise(InvalidValueForCalculationError(8))

    def test_throws_invalid_star_of_index_error(self):
        with self.assertRaises(InvalidStartIndexError):
            raise(InvalidStartIndexError(-13))
            
if __name__ == '__main__':
    unittest.main()