import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv('resources/speed_7578.csv')

boxplot_interval = 50

points_x = data['timestamp']
points_y = data['value']

outliers_x = []
outliers_y = []

boxplot_upper_range = []
boxplot_lower_range = []

outlier_count = 0

i = 0
while (i<len(points_x) - boxplot_interval):

    #get 50
    subset_x = []
    subset_y = []
    j = i
    while (j < i + boxplot_interval):
        subset_x.append(points_x[j])
        subset_y.append(points_y[j])
        j+=1

    #create new df
    subset_data = pd.DataFrame({'timestamp': subset_x, 'value': subset_y})



    #find quartile values and interquartile range

    #define array of data
    dataArr = np.array(subset_data['value'])
    #calculate interquartile range 
    q3, q1 = np.percentile(dataArr, [75 ,25])
    iqr = q3 - q1

    #print("subset\n")
    #print('q1 = ' + str(q1))
    #print('q3 = ' + str(q3))
    #print('iqr = ' + str(iqr))

    #calculate class boundaries
    lower_bound = q1 - iqr*1.5
    upper_bound = q3 + iqr*1.5

    #print('\n Boundaries')
    #print('Lower bound = ' + str(lower_bound))
    #print('Upper bound = ' + str(upper_bound))

    #is next data item an outlier?
    data_point = points_y[i + boxplot_interval]
    if ((data_point < lower_bound) or (data_point > upper_bound)):
        outlier_count +=1
        print('outlier')
        outliers_x.append(points_x[i + boxplot_interval])
        outliers_y.append(points_y[i + boxplot_interval])
    else:
        print('inlier')
    print(outlier_count)
    i = i + 1

    #Plotting Boxplot of value column
    #boxplot = subset_data.boxplot(column=['value'],grid = False)
    #plt.show()