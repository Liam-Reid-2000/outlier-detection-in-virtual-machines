import unittest
import pandas as pd

from ensemble_detectors.ensemble_voting import ensemble_voting

class ensemble_voting_test(unittest.TestCase):

    def get_test_outlier_voting_dataframe(self):
        points_x = []
        points_x.append(10)
        points_x.append(20)
        points_x.append(30)
        points_y = []
        points_y.append(13)
        points_y.append(12)
        points_y.append(15)
        return pd.DataFrame({'timestamp':points_x,'data':points_y})

    def get_test_outlier_voting_dataframe_two(self):
        points_x = []
        points_x.append(5)
        points_x.append(20)
        points_x.append(25)
        points_y = []
        points_y.append(23)
        points_y.append(12)
        points_y.append(4)
        return pd.DataFrame({'timestamp':points_x,'data':points_y})

    
    # TEST MAJORITY VOTE
    def test_get_ensemble_result_majority_all_same_classification(self):
        all_outliers = []
        # 3 detectors detect the same outliers
        all_outliers.append(self.get_test_outlier_voting_dataframe())
        all_outliers.append(self.get_test_outlier_voting_dataframe())
        all_outliers.append(self.get_test_outlier_voting_dataframe())
        outliers_after_vote = ensemble_voting.get_ensemble_result_majority(all_outliers)
        # should vote that all are outliers
        i = 0
        while i < len(outliers_after_vote['timestamp']):
            self.assertEqual(self.get_test_outlier_voting_dataframe()['timestamp'][i], outliers_after_vote['timestamp'][i])
            self.assertEqual(self.get_test_outlier_voting_dataframe()['data'][i], outliers_after_vote['data'][i])
            i += 1

    def test_get_ensemble_result_majority_some_different_classification(self):
        all_outliers = []
        # 2 detectors detect the same outliers, 1 detector detects different
        all_outliers.append(self.get_test_outlier_voting_dataframe())
        all_outliers.append(self.get_test_outlier_voting_dataframe())
        all_outliers.append(self.get_test_outlier_voting_dataframe_two())
        outliers_after_vote = ensemble_voting.get_ensemble_result_majority(all_outliers)
        # Should only predict one outlier after vote
        self.assertEqual(1, len(outliers_after_vote))
        self.assertEqual(self.get_test_outlier_voting_dataframe()['timestamp'][1], outliers_after_vote['timestamp'][0])
        self.assertEqual(self.get_test_outlier_voting_dataframe()['data'][1], outliers_after_vote['data'][0])

    
    def test_get_ensemble_result_majority_empty_outlier_list(self):
        all_outliers = []
        outliers_after_vote = ensemble_voting.get_ensemble_result_majority(all_outliers)
        self.assertEqual(0, len(outliers_after_vote))
        




    def get_test_outlier_dataframe_confidence(self):
        points_x = []
        points_x.append(5)
        points_x.append(10)
        points_x.append(15)
        points_x.append(20)
        points_x.append(25)
        points_x.append(30)
        points_y = []
        points_y.append(13)
        points_y.append(12)
        points_y.append(15)
        points_y.append(13)
        points_y.append(12)
        points_y.append(15)
        confidence = []
        confidence.append(1)
        confidence.append(0.8)
        confidence.append(0.6)
        confidence.append(0.5)
        confidence.append(-1)
        confidence.append(0.2)
        return pd.DataFrame({'timestamp':points_x,'data':points_y,'confidence':confidence})

    def get_test_outlier_dataframe_two_confidence(self):
        points_x = []
        points_x.append(5)
        points_x.append(10)
        points_x.append(15)
        points_x.append(20)
        points_x.append(25)
        points_x.append(30)
        points_y = []
        points_y.append(13)
        points_y.append(12)
        points_y.append(15)
        points_y.append(13)
        points_y.append(12)
        points_y.append(15)
        confidence = []
        confidence.append(1)
        confidence.append(-0.1)
        confidence.append(-0.6)
        confidence.append(0.2)
        confidence.append(-1)
        confidence.append(-1)
        return pd.DataFrame({'timestamp':points_x,'data':points_y,'confidence':confidence})


    # TEST CONFIDENCE VOTE
    def test_get_ensemble_result_confidence_all_same_classification(self):
        all_outliers = []
        # 3 detectors detect the same outliers
        all_outliers.append(self.get_test_outlier_dataframe_confidence())
        all_outliers.append(self.get_test_outlier_dataframe_confidence())
        all_outliers.append(self.get_test_outlier_dataframe_confidence())
        outliers_after_vote = ensemble_voting.get_ensemble_result_confidence(all_outliers)
        # should vote that all are outliers
        self.assertEqual(self.get_test_outlier_dataframe_confidence()['timestamp'][4], outliers_after_vote['timestamp'][0])
        self.assertEqual(self.get_test_outlier_dataframe_confidence()['data'][4], outliers_after_vote['data'][0])


    def test_get_ensemble_result_confidence_some_different_classification(self):
        all_outliers = []
        # 2 detectors detect the same outliers, 1 detector detects different
        all_outliers.append(self.get_test_outlier_dataframe_confidence())
        all_outliers.append(self.get_test_outlier_dataframe_confidence())
        all_outliers.append(self.get_test_outlier_dataframe_two_confidence())
        outliers_after_vote = ensemble_voting.get_ensemble_result_confidence(all_outliers)
        # Should only predict one outlier after vote
        self.assertEqual(2, len(outliers_after_vote))
        self.assertEqual(self.get_test_outlier_dataframe_confidence()['timestamp'][4], outliers_after_vote['timestamp'][0])
        self.assertEqual(self.get_test_outlier_dataframe_confidence()['data'][4], outliers_after_vote['data'][0])
        self.assertEqual(self.get_test_outlier_dataframe_confidence()['timestamp'][5], outliers_after_vote['timestamp'][1])
        self.assertEqual(self.get_test_outlier_dataframe_confidence()['data'][5], outliers_after_vote['data'][1])

    def test_get_ensemble_result_confidence_empty_outlier_list(self):
        all_outliers = []
        outliers_after_vote = ensemble_voting.get_ensemble_result_confidence(all_outliers)
        self.assertEqual(0, len(outliers_after_vote))


if __name__ == '__main__':
    unittest.main()