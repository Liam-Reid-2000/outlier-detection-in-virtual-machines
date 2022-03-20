import unittest

from ensemble_detectors.moving_average_detection import is_data_outside_bounds

class outlier_detection_test(unittest.TestCase):


    def test_is_data_outside_bounds(self):
        test_result = is_data_outside_bounds(1,3,1)
        self.assertEqual(True, test_result)

        test_result = is_data_outside_bounds(2,2,5)
        self.assertEqual(False, test_result)

        test_result = is_data_outside_bounds(7,2,2)
        self.assertEqual(True, test_result)

if __name__ == '__main__':
    unittest.main()