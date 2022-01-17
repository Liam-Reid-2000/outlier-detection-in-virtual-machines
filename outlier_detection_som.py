from minisom import MiniSom

import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import make_blobs
from sklearn.preprocessing import scale

from sklearn.datasets import make_circles



outliers_percentage = 0.35
inliers = 300
outliers = int(inliers * outliers_percentage)


def detect_som_outliers():
    
    data = make_blobs(centers=[[2, 2], [-2, -2]], cluster_std=[.3, .3],
                    n_samples=inliers, random_state=0)[0]

    data = scale(data)
    data = np.concatenate([data, 
                        (np.random.rand(outliers, 2)-.5)*4.])




    som = MiniSom(2, 1, data.shape[1], sigma=1, learning_rate=0.5,
                neighborhood_function='triangle', random_seed=10)


    som.train(data, 100, random_order=False, verbose=True)  # random training

    quantization_errors = np.linalg.norm(som.quantization(data) - data, axis=1)
    error_treshold = np.percentile(quantization_errors, 
                                100*(1-outliers_percentage)+5)

    print('Error treshold:', error_treshold)

    is_outlier = quantization_errors > error_treshold

    outliers_x = data[is_outlier, 0]
    outliers_y = data[is_outlier, 1]

    inliers_x = data[~is_outlier, 0]
    inliers_y = data[~is_outlier, 1]

    som_detection_data = []
    som_detection_data.append(outliers_x)
    som_detection_data.append(outliers_y)
    som_detection_data.append(inliers_x)
    som_detection_data.append(inliers_y)

    return som_detection_data


def detect_som_outliers_circle():
    
    data = make_circles(noise=.1, n_samples=inliers, random_state=0)[0]
    data = scale(data)
    data = np.concatenate([data, 
                        (np.random.rand(outliers, 2)-.5)*4.])


    som = MiniSom(5, 5, data.shape[1], sigma=1, learning_rate=0.5,
                neighborhood_function='triangle', random_seed=10)


    som.train_batch(data, 100, verbose=True)  
    quantization_errors = np.linalg.norm(som.quantization(data) - data, axis=1)
    error_treshold = np.percentile(quantization_errors, 
                                100*(1-outliers_percentage)+5)
    is_outlier = quantization_errors > error_treshold


    outliers_x = data[is_outlier, 0]
    outliers_y = data[is_outlier, 1]

    inliers_x = data[~is_outlier, 0]
    inliers_y = data[~is_outlier, 1]

    som_detection_data_circle = []
    som_detection_data_circle.append(outliers_x)
    som_detection_data_circle.append(outliers_y)
    som_detection_data_circle.append(inliers_x)
    som_detection_data_circle.append(inliers_y)

    return som_detection_data_circle