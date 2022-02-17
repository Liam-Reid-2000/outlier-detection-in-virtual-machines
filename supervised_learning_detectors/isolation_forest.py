import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.express as px
import plotly.graph_objects as go
from app_helper_scripts.app_detection import collect_detection_data
from app_helper_scripts.app_helper import save_generated_data
from supervised_learning_detectors.data_splitter import *
from datetime import *


def train_model(X_train):
    rng = np.random.RandomState(42)
    clf = IsolationForest(max_samples=20, random_state=rng)
    return clf.fit(X_train)


def get_max(arr1, arr2):
    max_arr_1 = np.max(arr1)
    max_arr_2 = np.max(arr2)
    return np.maximum(max_arr_1, max_arr_2)

def get_min(arr1, arr2):
    min_arr_1 = np.min(arr1)
    min_arr_2 = np.min(arr2)
    return np.minimum(min_arr_1, min_arr_2)



def plot_iso_detection_data(isolation_forest_model, X_train, inliers_detected_x, inliers_detected_y, outliers_detected_x, outliers_detected_y):
    # plot the line, the samples, and the nearest vectors to the plane

    #calc graph bounds
    min_x = get_min(inliers_detected_x,outliers_detected_x)
    max_x = get_max(inliers_detected_x,outliers_detected_x)
    min_y = get_min(inliers_detected_y,outliers_detected_y)
    max_y = get_max(inliers_detected_y,outliers_detected_y)


    xx, yy = np.meshgrid(np.linspace(min_x,max_x, 50), np.linspace(min_y, max_y, 50))
    Z = isolation_forest_model.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.title("Isolation Forest")
    plt.contourf(xx, yy, Z, cmap=plt.cm.Blues_r)

    b1 = plt.scatter(X_train[:, 0], X_train[:, 1], c="white", s=20, edgecolor="k")
    b2 = plt.scatter(inliers_detected_x, inliers_detected_y, c="green", s=20, edgecolor="k")
    c = plt.scatter(outliers_detected_x, outliers_detected_y, c="red", s=20, edgecolor="k")
    plt.axis("tight")
    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)
    plt.legend(
        [b1, b2, c],
        ["training observations", "new regular observations", "new abnormal observations"],
        loc="upper left",
    )

    train_data_df = pd.DataFrame({'minutes': X_train[:, 0],'data': X_train[:, 1]})
    inliers_data_df = pd.DataFrame({'minutes': inliers_detected_x,'data':inliers_detected_y})
    outliers_data_df = pd.DataFrame({'minutes': outliers_detected_x,'data':outliers_detected_y})

    fig = px.scatter(train_data_df, x='minutes', y='data',title= 'Data against Time (Using supervised isolation forest based outlier detection)')
    
  
    fig.add_trace(go.Scatter(x=inliers_data_df['minutes'], y=inliers_data_df['data'], mode='markers',name='Inliers Detected', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=outliers_data_df['minutes'], y=outliers_data_df['data'], mode='markers',name='Outliers Detected', line=dict(color='red')))

    #fig.show()

    #plt.show()

    return fig
    


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

    outlier_areas = get_outlier_areas(outlier_data[2],outlier_ref)

    detection_data = collect_detection_data(outlier_inliers_split[1], outlier_ref,split_data[4],split_data[5], outlier_areas)

    # save the generated data  
    save_generated_data('supervised_histogram_' + str(split_ratio), detection_data)

    if (plot):
        return plot_iso_detection_data(isolation_forest_model, X_train, 
            convert_time_data_to_minutes_of_day(outlier_inliers_split[0]['timestamp']), 
            outlier_inliers_split[0]['data'],
            convert_time_data_to_minutes_of_day(outlier_inliers_split[1]['timestamp']), 
            outlier_inliers_split[1]['data'])

    return detection_data

    

#do_isolation_forest_detection(0.75)




#new_data_to_predict_x = []
    #new_data_to_predict_y = []
    #new_data_to_predict_x.append(700)
    #new_data_to_predict_y.append(0)
    #to_predict = np.r_['1,2,0', new_data_to_predict_x, new_data_to_predict_y]
    #print(isolation_forest_model.predict(to_predict))




    ### https://scikit-learn.org/stable/modules/outlier_detection.html ###