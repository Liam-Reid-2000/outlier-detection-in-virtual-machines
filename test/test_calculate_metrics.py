import unittest
from app_helper_scripts.app_exceptions import InvalidPercentageFloatValueError, InvalidValueForCalculationError

from app_helper_scripts.metric_calculations import metric_calculations

class metric_calculations_test(unittest.TestCase):

    ## TESTING ACCURACY CALCULATION
    def test_accuracy_valid_values(self):
        accuracy_calculated = metric_calculations.calculate_accuracy(tn=5,tp=5,n=20)
        self.assertEqual(0.5, accuracy_calculated)
    
    def test_accuracy_invalid_true_negative(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calculate_accuracy(tn=-5,tp=5,n=20)
    
    def test_accuracy_invalid_true_positive(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calculate_accuracy(tn=5,tp=-5,n=20)
    
    def test_accuracy_invalid_total(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calculate_accuracy(tn=5,tp=5,n=0)

    def test_accuracy_invalid_true_negative_plus_true_positive(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calculate_accuracy(tn=15,tp=5,n=17)


    ## TESTING PRECISION CALCULATION
    def test_precision_valid_values(self):
        precision_calculated = metric_calculations.calculate_precision(tp=5, fp=20)
        self.assertEqual(0.2, precision_calculated)

    def test_precision_invalid_true_positive(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calculate_precision(tp=-5, fp=20)

    def test_precision_invalid_false_positive(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calculate_precision(tp=5, fp=-20)


    ## TESTING RECALL CALCULATION
    def test_recall_valid_values(self):
        recall_calculated = metric_calculations.calulate_recall(tp=4, fn=1)
        self.assertEqual(0.8, recall_calculated)

    def test_recall_invalid_true_positive(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calulate_recall(tp=-4, fn=1)

    def test_recall_invalid_false_negative(self):
        with self.assertRaises(InvalidValueForCalculationError):
            metric_calculations.calulate_recall(tp=4, fn=-1)


    ## TESTING CALCULATE F1
    def test_f1_valid_values(self):
        f1_calculated = metric_calculations.calculate_f1(0.5, 0.5)
        self.assertEqual(0.5, f1_calculated)

    def test_f1_invalid_precision_negative(self):
        with self.assertRaises(InvalidPercentageFloatValueError):
            metric_calculations.calculate_f1(-0.7, 0.5)

    def test_f1_invalid_precicion_greater_than_one(self):
        with self.assertRaises(InvalidPercentageFloatValueError):
            metric_calculations.calculate_f1(1.5, 0.5)

    def test_f1_invalid_recall_negative(self):
        with self.assertRaises(InvalidPercentageFloatValueError):
            metric_calculations.calculate_f1(0.5, -0.7)

    def test_f1_invalid_recall_greater_than_one(self):
        with self.assertRaises(InvalidPercentageFloatValueError):
            metric_calculations.calculate_f1(0.5, 1.5)

if __name__ == '__main__':
    unittest.main()