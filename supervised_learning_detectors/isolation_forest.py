import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from app_helper_scripts.app_detection import collect_detection_data
from app_helper_scripts.app_helper import save_generated_data
from supervised_learning_detectors.data_splitter import *
from datetime import *


def train_model(X_train):
    rng = np.random.RandomState(42)
    clf = IsolationForest(max_samples=100, random_state=rng)
    return clf.fit(X_train)


def plot_iso_detection_data(isolation_forest_model, X_train, inliers_detected_x, inliers_detected_y, outliers_detected_x, outliers_detected_y):
    # plot the line, the samples, and the nearest vectors to the plane
    xx, yy = np.meshgrid(np.linspace(0,1440, 50), np.linspace(0, 100, 50))
    Z = isolation_forest_model.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.title("IsolationForest")
    plt.contourf(xx, yy, Z, cmap=plt.cm.Blues_r)

    b1 = plt.scatter(X_train[:, 0], X_train[:, 1], c="white", s=20, edgecolor="k")
    b2 = plt.scatter(inliers_detected_x, inliers_detected_y, c="green", s=20, edgecolor="k")
    c = plt.scatter(outliers_detected_x, outliers_detected_y, c="red", s=20, edgecolor="k")
    plt.axis("tight")
    plt.xlim((0, 1440))
    plt.ylim((0, 100))
    plt.legend(
        [b1, b2, c],
        ["training observations", "new regular observations", "new abnormal observations"],
        loc="upper left",
    )
    plt.show()


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
    

def do_isolation_forest_detection(split_ratio):

    # Load data and outliers
    split_data = load_data('resources/speed_7578.csv', split_ratio)
    outlier_data = split_outliers('resources/combined_labels.json',split_data[4][0])

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

    outlier_areas = get_outlier_areas(outlier_data[2],'realTraffic/speed_7578.csv')

    detection_data = collect_detection_data(outlier_inliers_split[1], 'realTraffic/speed_7578.csv',split_data[4],split_data[5], outlier_areas)

    # save the generated data  
    save_generated_data('supervised_histogram_' + str(split_ratio), detection_data)

    # Collect and return the detection data
    #detection_data = []
    #detection_data.append(split_data[4])
    #detection_data.append(split_data[5])
    #detection_data.append(outlier_inliers_split[1]['timestamp'])
    #detection_data.append(outlier_inliers_split[1]['data'])
    #detection_data.append(outlier_areas['first_x'])
    #detection_data.append(outlier_areas['second_x'])

    return detection_data


    #plot_iso_detection_data(isolation_forest_model, X_train, 
    #    convert_time_data_to_minutes_of_day(inliers_detected_x), 
    #    inliers_detected_y,
    #    convert_time_data_to_minutes_of_day(outliers_detected_x), 
    #    outliers_detected_y)

do_isolation_forest_detection(0.75)




#new_data_to_predict_x = []
    #new_data_to_predict_y = []
    #new_data_to_predict_x.append(700)
    #new_data_to_predict_y.append(0)
    #to_predict = np.r_['1,2,0', new_data_to_predict_x, new_data_to_predict_y]
    #print(isolation_forest_model.predict(to_predict))




    ### https://scikit-learn.org/stable/modules/outlier_detection.html ###