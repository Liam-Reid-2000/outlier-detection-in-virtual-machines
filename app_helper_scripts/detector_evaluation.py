import json

class detector_evaluation:

    def __init__(self, target_data, points_x, outliers_x):
        self.target_data = target_data
        self.outliers_x = outliers_x
        self.points_x = points_x   
        self.true_positives = []
        self.false_positives = []
        self.false_negatives = []
        self.true_negative_count = 0
    

    def get_detector_classification_evalutaion_data(self):
        outlier_labels_file = open('resources/combined_labels.json')
        outlier_labels = json.load(outlier_labels_file)

        for outlier_detected in self.outliers_x:
            is_true_outlier = False
            for true_outlier in outlier_labels[self.target_data]:
                if (str(outlier_detected) == str(true_outlier)):
                    is_true_outlier = True
                    self.true_positives.append(outlier_detected)
            if (is_true_outlier == False):
                self.false_positives.append(outlier_detected)

        for true_outlier in outlier_labels[self.target_data]:
            found = False
            for true_positive in self.true_positives:
                if (str(true_outlier) == str(true_positive)):
                    found = True
            if (found == False):
                self.false_negatives.append(true_outlier)

        self.true_negative_count = len(self.points_x) - len(self.false_positives) - len(self.true_positives)

        outlier_labels_file.close()

        true_neg = [self.true_negative_count]
        data_len = [len(self.points_x)]

        detector_classification_evalutaion_data = []
        detector_classification_evalutaion_data.append(self.true_positives)
        detector_classification_evalutaion_data.append(self.false_positives)
        detector_classification_evalutaion_data.append(self.false_negatives)
        detector_classification_evalutaion_data.append(true_neg)
        detector_classification_evalutaion_data.append(data_len)
        
        return detector_classification_evalutaion_data