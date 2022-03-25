from app_helper_scripts.app_helper import *

model = 'moving_boxplot'
data_csv = 'resources/cloud_resource_data/ec2_cpu_utilization_ac20cd.csv'
outliers_csv = 'realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv'
threshold = 2.5
interval = 20

best_f1_score = 0
best_i = 0
best_t = 0

i = 10
while (i < 50):
    print('iteration = ' + str(i))

    t = 0.5
    while t < 10:
        detection_data = run_detection_hours_known_outliers(model, data_csv, outliers_csv, t, i)

        if (detection_data[6][3] > best_f1_score):
            best_f1_score = detection_data[6][3]
            best_i = i
            best_t = t

        print('t = ' + str(t) + ' : i = ' + str(i) + ' : F1 score = ' + str(detection_data[6][3]))
        t += 0.5
    i += 5

print('\nBest f1 = ' + str(best_f1_score))
print('\nBest threshold = ' + str(best_t))
print('\nBest interval = ' + str(best_i))