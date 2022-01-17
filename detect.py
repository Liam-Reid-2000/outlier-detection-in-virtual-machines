import matplotlib.pyplot as plt
from datetime import datetime
from pycaret.anomaly import *
import pandas as pd
import csv
import json


points_x = []
points_y = []

outliers_x = []


def get_no_outliers(target_data):
    f = open('combined_labels.json')
    data = json.load(f)
    f.close()
    return len(data[target_data])


def plot_data(csv_file_name):
    with open(csv_file_name,'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        for row in lines:
            try:
                points_y.append(float(row[1]))
                points_x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                print("error")


def plot_anomaly_areas(xF, xS):
    plt.axvspan(xF, xS, color = 'red',alpha=0.5)


def plot_anomalies(target_data):
    f = open('combined_windows.json')
    data = json.load(f)
    for i in data[target_data]:
        plot_anomaly_areas(datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f'),datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f'))
    f.close()


def detect_anomalies(model, outlierCount):
    data = pd.DataFrame({'timestamp': points_x,
                    'data': points_y})
    data.set_index('timestamp', drop=True, inplace=True)
    data['day'] = [i.day for i in data.index]
    data['day_name'] = [i.day_name() for i in data.index]
    data['day_of_year'] = [i.dayofyear for i in data.index]
    data['week_of_year'] = [i.weekofyear for i in data.index]
    data['hour'] = [i.hour for i in data.index] # only use this for speed data, commetn rest
    data['is_weekday'] = [i.isoweekday() for i in data.index]
    data.head()

    s = setup(data, session_id = 123)
    myModel = create_model(model, fraction = 0.05)#, fraction = outlierCount/len(points_x))

    myModel_results = assign_model(myModel)
    myModel_results.head()
    myModel_results[myModel_results['Anomaly'] == 1].head()
    outlier_dates = myModel_results[myModel_results['Anomaly'] == 1].index
    y_values = [myModel_results.loc[i]['data'] for i in outlier_dates]

    outliers_x.append(outlier_dates)

    outliers = pd.DataFrame({'timestamp': outlier_dates,
                    'data': y_values})

    return outliers




def get_true_positive(target_data):
    true_positive_count = 0
    f = open('combined_windows.json')
    data = json.load(f)
    for i in data[target_data]:
        minBound = datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')
        maxBound = datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f')
        for outlier in outliers_x[0]:
            if (outlier>=minBound and outlier<=maxBound):
                true_positive_count = true_positive_count + 1
    f.close()
    return true_positive_count


def get_false_positive(true_positive_count):
    return (len(outliers_x[0]) - true_positive_count)





def get_true_negative(target_data, false_positive_count):
    actual_negative_count = 0
    f = open('combined_windows.json')
    data = json.load(f)
    for point in points_x:
        is_actual_negative = True
        for i in data[target_data]:
            minBound = datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')
            maxBound = datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f')
            if (point>=minBound and point<=maxBound):
                is_actual_negative = False
        if (is_actual_negative):
            actual_negative_count = actual_negative_count + 1
    f.close()
    true_negative = actual_negative_count - false_positive_count
    return true_negative





def get_false_negative(target_data):
    hit_count = 0
    f = open('combined_labels.json')
    data = json.load(f)
    for i in data[target_data]:
        for outlier in outliers_x[0]:
            if (str(outlier) == str(i)):
                hit_count = hit_count + 1
    f.close()
    return (len(data[target_data]) - hit_count)



def display_results(anomalies_csv):
    
    n = len(points_x)

    tp = get_true_positive(anomalies_csv)
    fp = get_false_positive(tp)
    tn = get_true_negative(anomalies_csv, fp)
    fn = get_false_negative(anomalies_csv)

    tpRate = tp/n
    fpRate = fp/n
    tnRate = tn/n
    fnRate = fn/n

    accuracy = (tn+tp)/n
    recall = tp/(tp+fn)
    precision = tp/(tp+fp)

    try:
        f1 = (2*(recall*precision))/(precision+recall)
    except:
        print("error")
    
    print('\n\nDETECTION RESULTS \n')
    print('True Postives: ' + str(tp))
    print('False Postives: ' + str(fp))
    print('False Negatives: ' + str(fn))
    print('True Negatives: ' + str(tn))

#    print('\n')
#    print('True Postive Rate: ' + str(tpRate))
#    print('False Postive Rate: ' + str(fpRate))
#    print('False Negative Rate: ' + str(fnRate))
#    print('True Negative Rate: ' + str(tnRate))
    
    print('\n')
    print('Accuracy: ' + str(accuracy))
    print('Recall: ' + str(recall))
    print('Precision: ' + str(precision))
    try:
        print('f1 score: ' + str(f1))
    except:
        print('f1 score: 0')


    print('\n\nDETECTION RESULTS AS PERCENTAGES \n')

#    print('True Postive Rate: ' + str(round(tpRate*100,1)))
#    print('False Postive Rate: ' + str(round(fpRate*100,1)))
#    print('False Negative Rate: ' + str(round(fnRate*100,1)))
#    print('True Negative Rate: ' + str(round(tnRate*100,1)))
    
#    print('\n')
    print('Accuracy: ' + str(round(accuracy*100,1))+'%')
    print('Recall: ' + str(round(recall*100,1))+'%')
    print('Precision: ' + str(round(precision*100,1))+'%')
    try:
        print('f1 score: ' + str(round(f1*100,1))+'%')
    except:
        print('f1 score: 0.0%')




def run_detection(model, data_csv, anomalies_csv, title):
    plot_data(data_csv)
    plot_anomalies(anomalies_csv)
    plt.plot(points_x, points_y, color = 'b',label = "data",linewidth=0.5)
    outliers = detect_anomalies(model, get_no_outliers(anomalies_csv))
    plt.scatter(outliers['timestamp'], outliers['data'],color = 'r',label = "Anomalies Detected",marker='o')
    plt.xticks(rotation = 25)
    plt.xlabel('Timestamp')
    plt.ylabel('Data')
    plt.title(title, fontsize = 20)
    plt.grid()
    plt.legend()

    display_results(anomalies_csv)

    plt.show()






def main():
    run_detection('knn', 'speed_7578.csv', 'realTraffic/speed_7578.csv', 'Speed Data against Time (Using knn-based outlier detection)')
    #run_detection('knn', 'nyc_taxi.csv', 'realKnownCause/nyc_taxi.csv', 'NYC Taxi Data against Time (Using knn-based outlier detection)')
    #run_detection('knn', 'Twitter_volume_UPS.csv', 'realTweets/Twitter_volume_UPS.csv', 'Twitter Data against Time (Using knn-based outlier detection)')
    #run_detection('knn', 'machine_temperature_system_failure.csv', 'realKnownCause/machine_temperature_system_failure.csv', 'Machine Temperature Data against Time (Using knn-based outlier detection)')
    #run_detection('knn', 'ec2_cpu_utilization_fe7f93.csv', 'realAWSCloudwatch/ec2_cpu_utilization_fe7f93.csv', 'AWS Cloud Watch Data against Time (Using knn-based outlier detection)')



if __name__=="__main__":
    main()