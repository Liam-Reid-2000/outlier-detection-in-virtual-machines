import csv
import datetime

all_points_x = []
all_points_y = []

train_points_x = []
train_points_y = []

test_points_x = []
test_points_y = []

def load_data(csv_file_name, split_ratio):
    with open(csv_file_name,'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        if (split_ratio <= 0 or split_ratio >= 1):
            print('Error: Split ration must be greater than 0 and less than 1')
        else:
            i = 0
            for row in lines:
                try:
                    all_points_y.append(float(row[1]))
                    all_points_x.append(datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
                except ValueError:
                    print("Error loading data")
                i += 1

            no_data_points = i
            train_test_point = split_ratio * no_data_points
            print(str(int(train_test_point)))

            i = 0
            while (i < int(train_test_point)):
                train_points_x.append(all_points_x[i])
                train_points_y.append(all_points_y[i])
                i+=1
            
            i = int(train_test_point)
            while (i < len(all_points_x)):
                test_points_x.append(all_points_x[i])
                test_points_y.append(all_points_y[i])
                i+=1

### SPLIT THE OUTLIER DATA AND LABEL ###

load_data('resources/speed_7578.csv', 0.5)

print('test length ' + str(len(test_points_x)))

print('train length ' + str(len(train_points_x)))
