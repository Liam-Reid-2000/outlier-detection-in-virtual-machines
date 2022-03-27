import datetime
import json



class display_results:

    def __init__(self, target_data, points_x, outliers_x):
        self.target_data = target_data
        self.outliers_x = outliers_x
        self.points_x = points_x
        self.data_in_outlier_windows = 0
    
    

    def get_no_outliers(self):
        f = open('resources/combined_labels.json')
        data = json.load(f)
        f.close()
        return len(data[self.target_data])



    def get_true_positive(self):
        #outlier_windows_file = open('resources/combined_windows.json')
        #outlier_windows = json.load(outlier_windows_file)
        
        outlier_labels_file = open('resources/combined_labels.json')
        outlier_labels = json.load(outlier_labels_file)

        true_positive_count = 0

        for outlier in self.outliers_x[0]:
            for outlier2 in outlier_labels[self.target_data]:
                if (str(outlier) == str(outlier2)):
                    print('actual_outlier ' + str(outlier2))
                    true_positive_count += 1

        #for i in outlier_windows[self.target_data]:
            #minBound = datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')
            #maxBound = datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f')

            #no_outliers_in_this_boundary = 0
            #true_positive_count_for_this_boundary = 0

            #for outlier in outlier_labels[self.target_data]:
            #    outlier_date = datetime.datetime.strptime(outlier, '%Y-%m-%d %H:%M:%S')
            #    if (outlier_date>=minBound and outlier_date<=maxBound):
            #        no_outliers_in_this_boundary += 1


            
                #if (outlier>=minBound and outlier<=maxBound):
                #    self.data_in_outlier_windows += 1
                #    if (true_positive_count_for_this_boundary < no_outliers_in_this_boundary):
                #        true_positive_count_for_this_boundary += 1
            
            #true_positive_count += true_positive_count_for_this_boundary

        outlier_labels_file.close()
        #outlier_windows_file.close()
        return true_positive_count



    def get_false_positive(self):
        false_positive = len(self.outliers_x[0]) - self.get_true_positive()
        if (false_positive > 0):
            return false_positive
        else:
            return 0


    def get_true_negative(self):
        actual_negative_count = 0
        f = open('resources/combined_windows.json')
        data = json.load(f)

        # checks if data is in date format # Changes to date format if not
        try:
            self.points_x[0].hour
        except:
            arr_as_dates = []
            for i in self.points_x:
                arr_as_dates.append(datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S'))
            self.points_x = arr_as_dates

        for point in self.points_x:
            is_actual_negative = True
            for i in data[self.target_data]:
                minBound = datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')
                maxBound = datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f')
                if (point>=minBound and point<=maxBound):
                    is_actual_negative = False
            if (is_actual_negative):
                actual_negative_count = actual_negative_count + 1
        f.close()
        true_negative = actual_negative_count - self.get_false_positive()
        if (true_negative > 0):
            return true_negative
        else:
            return 0



    def get_false_negative(self):
        hit_count = 0
        f = open('resources/combined_labels.json')
        data = json.load(f)
        return len(data[self.target_data]) - self.get_true_positive()
        #for i in data[self.target_data]:
        #    for outlier in self.outliers_x[0]:
        #        if (str(outlier) == str(i)):
        #            hit_count = hit_count + 1
        #f.close()
        #false_negative = (len(data[self.target_data]) - hit_count)
        #if (false_negative > 0):
        #    return false_negative
        #else:
        #    return 0



    def display_results(self):
        
        n = len(self.points_x)

        tp = self.get_true_positive()
        fp = self.get_false_positive()
        tn = self.get_true_negative()
        fn = self.get_false_negative()

        ## Accuracy
        try:
            accuracy = (tn+tp)/n
        except:
            accuracy = 0

        ## Recall
        try:
            recall = tp/(tp+fn)
        except:
            recall = 0

        ## Precision
        try:
            precision = tp/(tp+fp)
        except:
            precision = 0

        ## F1
        try:
            f1 = (2*(recall*precision))/(precision+recall)
        except:
            f1 = 0

        results = []
        results.append(accuracy)
        results.append(recall)
        results.append(precision)
        results.append(f1)
        
        print('\n\nDETECTION RESULTS \n')
        print('True Postives: ' + str(tp))
        print('False Postives: ' + str(fp))
        print('False Negatives: ' + str(fn))
        print('True Negatives: ' + str(tn))
        
        #print('\n')
        #print('Accuracy: ' + str(accuracy))
        #print('Recall: ' + str(recall))
        #print('Precision: ' + str(precision))
        #print('f1 score: ' + str(f1))

        print('\n\nDETECTION RESULTS AS PERCENTAGES \n')
        
        print('Accuracy: ' + str(round(accuracy*100,1))+'%')
        print('Recall: ' + str(round(recall*100,1))+'%')
        print('Precision: ' + str(round(precision*100,1))+'%')
        print('f1 score: ' + str(round(f1*100,1))+'%')

        return results