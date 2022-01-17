import matplotlib.pyplot as plt
from moving_median_detection import *
from moving_average_detection import *
from plot import *
from display_results import display_results

from moving_average_median_ensemble import get_ensemble_result



def get_ideal_threshold(anomalies_csv, points_x, outlier_x, _data_coordinates, data_coordinates, x_name):
    i = 40
    best_score = 0
    ideal_threshold = 0
    while (i < 120):
        average_outliers = detect_median_outliers(i, _data_coordinates, data_coordinates)
        average_oulier_x = average_outliers[x_name]
        score = display_results(anomalies_csv, points_x, average_oulier_x)
        if (score > best_score):
            best_score = score
            ideal_threshold = i
        i += 1
    return ideal_threshold




def run_detection(data_csv, anomalies_csv, title):
    
    data_coordinates = get_data_coordinates(data_csv)
    points_x = data_coordinates['points_x']
    points_y = data_coordinates['points_y']
    plt.plot(points_x, points_y, color = 'b',label = "data",linewidth=0.5)
    
    plot_anomalies(anomalies_csv)
    
    
    ########## MEDIAN ##########

    median_data_coordinates = get_moving_median_coordinates(10, data_coordinates)
    median_points_x = median_data_coordinates['points_median_x']
    median_points_y = median_data_coordinates['points_median_y']
    plt.plot(median_points_x, median_points_y, color = 'g',label = "Median",linewidth=1)

    median_outliers = detect_median_outliers(34, median_data_coordinates, data_coordinates)
    median_oulier_x = median_outliers['timestamp']
    median_oulier_y = median_outliers['data']
    plt.scatter(median_oulier_x, median_oulier_y,color = 'g',label = "Median Detected",marker='o')

    #print('Ideal threshold = ' + str(get_ideal_threshold(anomalies_csv, points_x, median_oulier_x, median_data_coordinates, data_coordinates, 'median_outlier_x')))

    ########## MEDIAN ##########


    ########## AVERAGE ##########

    average_data_coordinates = get_moving_average_coordinates(10, data_coordinates)
    average_points_x = average_data_coordinates['points_average_x']
    average_points_y = average_data_coordinates['points_average_y']
    plt.plot(average_points_x, average_points_y, color = 'r',label = "Average",linewidth=1)

    average_outliers = detect_average_outliers(25, average_data_coordinates, data_coordinates)
    average_oulier_x = average_outliers['timestamp']
    average_oulier_y = average_outliers['data']
    plt.scatter(average_oulier_x, average_oulier_y,color = 'r',label = "Average Outliers",marker='o')

    #print('Ideal threshold = ' + str(get_ideal_threshold(anomalies_csv, points_x, average_oulier_x, average_data_coordinates, data_coordinates, 'average_outlier_x')))

    ########## AVERAGE ##########


    ####### ensemble

    ensemble_coordinates = get_ensemble_result(median_outliers, average_outliers)

    ensemble_x = ensemble_coordinates['ensemble_outlier_x']
    ensemble_y = ensemble_coordinates['ensemble_outlier_y']

    plt.scatter(ensemble_x, ensemble_y,color = 'b',label = "Ensemble Outliers",marker='o')

    ######


    plt.xticks(rotation = 25)
    plt.xlabel('Timestamp')
    plt.ylabel('Data')
    plt.title(title, fontsize = 20)
    plt.grid()
    plt.legend()

    display_results(anomalies_csv, points_x, average_oulier_x)

    return plt







def main():
    plt = run_detection('resources/speed_7578.csv', 'realTraffic/speed_7578.csv', 'Speed Data against Time (Using average based outlier detection with optimised threshold)')
    #run_detection('nyc_taxi.csv', 'realKnownCause/nyc_taxi.csv', 'NYC Taxi Data against Time (Using average based outlier detection with optimised threshold)')
    #run_detection('Twitter_volume_UPS.csv', 'realTweets/Twitter_volume_UPS.csv', 'Twitter Data against Time (Using average based outlier detection with optimised threshold)')
    #run_detection('machine_temperature_system_failure.csv', 'realKnownCause/machine_temperature_system_failure.csv', 'Machine Temperature Data against Time (Using average based outlier detection with optimised threshold)')
    #run_detection('ec2_cpu_utilization_fe7f93.csv', 'realAWSCloudwatch/ec2_cpu_utilization_fe7f93.csv', 'AWS Cloud Watch Data against Time (Using average based outlier detection with optimised threshold)')
    plt.show()


if __name__=="__main__":
    main()