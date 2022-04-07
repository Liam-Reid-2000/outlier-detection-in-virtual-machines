import unittest

from app_helper_scripts.app_detection import detection_runner

class app_detection_test(unittest.TestCase):

    def get_dummy_list(self, with_outlier):
        list_data_points =[]
        i = 0
        while i < 20:
            list_data_points.append(15)
            list_data_points.append(12)
            list_data_points.append(18)
            i += 1
        if (with_outlier):
            list_data_points.append(50)
        return list_data_points

    # TEST REAL TIME DETECTION
    def test_detect_real_time_moving_average(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_average', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)
    
    def test_detect_real_time_moving_median(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_median', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_moving_boxplot(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_boxplot', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_moving_histogram(self):
        confidence_outlier = detection_runner.detect_in_real_time('moving_histogram', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_full_ensemble(self):
        confidence_outlier = detection_runner.detect_in_real_time('full_ensemble', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)

    def test_detect_real_time_invalid_detector(self):
        confidence_outlier = detection_runner.detect_in_real_time('invalid_detector', self.get_dummy_list(True))
        self.assertTrue(confidence_outlier != 0)
        

    

if __name__ == '__main__':
    unittest.main()