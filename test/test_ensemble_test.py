import unittest

from ensemble_detectors.moving_median_detection import get_median
from ensemble_detectors.moving_average_detection import get_average

class outlier_detection_test(unittest.TestCase):

    def test_average(self):
        test_array = [1,2,3,4,5]
        self.assertEqual(3, get_average(test_array))
        test_array_2 = [1,2,2,3,3,4,4,4,4]
        self.assertEqual(3, get_average(test_array_2))

    def test_median(self):
        test_array = [1,2,3,4,5]
        self.assertEqual(3, get_median(test_array))
        test_array_2 = [1,2,2,3,3,4,4,4,4]
        self.assertEqual(3, get_median(test_array_2))


if __name__ == '__main__':
    unittest.main()