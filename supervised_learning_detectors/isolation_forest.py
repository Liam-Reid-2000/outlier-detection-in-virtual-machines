import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from app_helper_scripts.app_exceptions import InvalidPercentageFloatValueError
from supervised_learning_detectors.data_splitter import *

def train_model(X_train):
    rng = np.random.RandomState(42)
    clf = IsolationForest(max_samples=20, random_state=rng)
    return clf.fit(X_train)


#def make_prediction(model, x, y):
#    new_data_to_predict_x = []
#    new_data_to_predict_y = []
#    new_data_to_predict_x.append(x)
#    new_data_to_predict_y.append(y)
#    to_predict = np.r_['1,2,0', new_data_to_predict_x, new_data_to_predict_y]
#    print(model.predict(to_predict))    


def split_outliers_inliers(labeled_test_data):
    
    outlier_inlier_split = []
    
    outliers_detected_x = []
    outliers_detected_y = []
    inliers_detected_x = []
    inliers_detected_y = []
    i = 0
    while (i < len(labeled_test_data['timestamp'])):
        if (labeled_test_data['label'][i] == 1):
            inliers_detected_x.append(labeled_test_data['timestamp'][i])
            inliers_detected_y.append(labeled_test_data['data'][i])
        else:
            outliers_detected_x.append(labeled_test_data['timestamp'][i])
            outliers_detected_y.append(labeled_test_data['data'][i])
        i += 1
    outlier_inlier_split.append(pd.DataFrame({'timestamp':inliers_detected_x,'data':inliers_detected_y}))
    outlier_inlier_split.append(pd.DataFrame({'timestamp':outliers_detected_x,'data':outliers_detected_y}))

    return outlier_inlier_split
    

def do_isolation_forest_detection(split_ratio, dataset, outlier_ref, plot=False):

    if (split_ratio >= 1 or split_ratio <=0):
        raise InvalidPercentageFloatValueError(split_ratio)

    # Load data and outliers
    split_data = load_data(dataset, split_ratio)
    outlier_data = split_outliers(outlier_ref,split_data[4][0])

    # Remove outliers from training data (Semi - Supervised training)
    clean_training_data = remove_outliers_from_training_data(outlier_data[1], split_data[2], split_data[3])
    
    # Train the model with training data
    X_train = get_data_as_matrix(convert_time_data_to_minutes_of_day(clean_training_data['timestamp']), clean_training_data['data'])
    isolation_forest_model = train_model(X_train)

    # Test the model with testing data
    X_test = get_data_as_matrix(convert_time_data_to_minutes_of_day(split_data[4]), split_data[5])
    y_pred_test = isolation_forest_model.predict(X_test)

    # Label the test data
    labeled_test_data = pd.DataFrame({'timestamp':split_data[4],'data':X_test[:, 1],'label':y_pred_test})

    # Separate outliers and inliers
    outlier_inliers_split = split_outliers_inliers(labeled_test_data)

    if (plot):
        plot_data = []
        plot_data.append(X_train) 
        plot_data.append(convert_time_data_to_minutes_of_day(outlier_inliers_split[0]['timestamp']))
        plot_data.append(outlier_inliers_split[0]['data'])
        plot_data.append(convert_time_data_to_minutes_of_day(outlier_inliers_split[1]['timestamp']))
        plot_data.append(outlier_inliers_split[1]['data'])
        return plot_data

    return outlier_inliers_split[1]

    ### https://scikit-learn.org/stable/modules/outlier_detection.html ###