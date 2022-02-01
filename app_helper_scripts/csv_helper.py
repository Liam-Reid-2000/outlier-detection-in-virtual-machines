import csv

def write_to_csv(path, data, action):
    file = open(path,action,newline='')
    writer = csv.writer(file)
    writer.writerow(data)
    file.close()